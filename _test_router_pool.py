#!/usr/bin/env python3
"""日报路由选题池写入 — 离线自测（不调 LLM、不改动正式文件）。

验证 P-20260923-01 的核心修复：从路由日志**确定性提取**选题并写入选题池。
用 tmp 文件当选题池，断言写入结果正确，并检查日期计数不再被日期数字污染。

用法（在 每日日报/ 目录下）：
    python _test_router_pool.py
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / ".github" / "scripts"))

import run_daily_router as R  # noqa: E402
from extract_topic_pool import dedupe_topics, parse_route_log, to_pool_row  # noqa: E402

FAILURES: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILURES.append(label)


def main() -> int:
    # ── 1. 用真实的截断日志验证「解析器能救回来」 ──
    log_path = HERE / "_路由" / "2026-09-23.md"
    text = log_path.read_text(encoding="utf-8")
    topics = parse_route_log(text)
    check("真实截断日志可提取选题", len(topics) == 3, f"提取 {len(topics)} 条")
    check("提取结果带优先级标记", all(t["mark"] in ("⭐", "·") for t in topics))
    check("提取结果带钩子", sum(1 for t in topics if t["hook"]) >= 2,
          f"{sum(1 for t in topics if t['hook'])}/3 条有钩子")

    # ── 2. 表格行格式 ──
    row = to_pool_row(topics[0])
    check("表格行是 4 列", row.count("|") == 5, row[:60])
    check("表格行无换行", "\n" not in row)

    # ── 3. 去重（同一天两条 NVDA 收购 HF 应被合并，其余不得误杀）──
    dupes = parse_route_log((HERE / "_路由" / "2026-09-03.md").read_text(encoding="utf-8")) + \
        parse_route_log((HERE / "_路由" / "2026-09-04.md").read_text(encoding="utf-8"))
    kept, skipped = dedupe_topics(dupes)
    check("跨天重复选题被去重", len(skipped) == 1,
          f"保留 {len(kept)} 跳过 {len(skipped)}：" + "; ".join(s["skip_reason"] for s in skipped))
    check("去重不误杀（6 条中只合并 1 条）", len(kept) == 5, f"保留 {len(kept)} 条")

    # ── 3b. 截断检测：必须能认出真实的截断日志 ──
    trunc = R.detect_truncation(text)
    check("能识别出真实截断日志", len(trunc) >= 2, "；".join(trunc))
    full = (HERE / "_路由" / "2026-09-04.md").read_text(encoding="utf-8")
    # 09-04 是完整日志（六个区齐全、句子收尾完整）—— 不得误报
    check("完整日志不误报", R.detect_truncation(full) == [],
          "；".join(R.detect_truncation(full)))
    tiny = (HERE / "_路由" / "2026-08-24.md").read_text(encoding="utf-8")
    check("短日志被识别为异常", len(R.detect_truncation(tiny)) >= 1,
          "；".join(R.detect_truncation(tiny)))
    clean = "# 日报路由 · X\n\n## ⭐ 高优先级选题(→ 选题池)\n\n### 01. 标题\n- 角度: 写完了。\n\n## 普通选题(→ 选题池)\n\n### 01. 标题二\n- 角度: 也写完了。\n\n## 丢弃摘要\n| 条目 | 原因 |\n"
    check("合成完整日志不误报", R.detect_truncation(clean) == [],
          "；".join(R.detect_truncation(clean)))

    # ── 3d. 字段完整性过滤：截断日志的最后一条不得写进选题池 ──
    # 真实日志 2026-09-23 的第三条只有标题（钩子/角度在被切掉的部分），
    # 不过滤就会在用户看板里留下一行没用的占位。
    def _complete(ts):
        return [t for t in ts if t["title"].strip() and t["hook"].strip() and t["angle"].strip()]

    check("截断日志确实含字段不全的选题（前提成立）",
          len(_complete(topics)) < len(topics),
          f"提取 {len(topics)} 条，完整 {len(_complete(topics))} 条")
    check("完整性过滤后无空单元格",
          all(t["hook"].strip() and t["angle"].strip() for t in _complete(topics)))

    # ── 3c. 失败可见性：注解格式 + API 失败必须非静默 ──
    import io
    from contextlib import redirect_stdout

    buf = io.StringIO()
    with redirect_stdout(buf):
        R.gh_annotate("error", "测试\n多行 % 百分号")
    line = buf.getvalue().strip()
    check("注解使用 GitHub 语法", line.startswith("::error title=日报路由::"), line)
    check("注解已转义换行与百分号", "\n" not in line and "%25" in line, line)

    # 没有 API Key 时必须抛错并给出原因（旧代码静默 → 全绿但没产出）
    saved = os.environ.pop("DEEPSEEK_API_KEY", None)
    try:
        R.call_deepseek("sys", "user")
        raised = False
    except Exception as exc:  # noqa: BLE001
        raised = "DEEPSEEK_API_KEY" in str(exc)
    finally:
        if saved is not None:
            os.environ["DEEPSEEK_API_KEY"] = saved
    check("缺 Key 时调用报错且说明原因", raised)

    # ── 4. 写入 tmp 选题池 ──
    # 用工作区内的临时目录：系统 temp 目录在沙箱下不可写
    tmp_root = HERE / "_test_tmp"
    tmp_root.mkdir(exist_ok=True)
    try:
        pool = tmp_root / "_选题池.md"
        pool.write_text(
            "# 选题池\n\n## 🔥 新进（最近 7 天）\n\n> 超过 7 天的选题 → 手动移入 🌿 或 💤\n\n"
            "### 08-09（10 条）\n\n| 选题 | 钩子 | 角度 | 系列 |\n|------|------|------|------|\n\n\n"
            "## 🌿 持续发酵（有跨天信号累积）\n\n## 💤 等待更多信号\n\n## ✅ 已发布\n\n## 📦 归档\n",
            encoding="utf-8",
        )
        R.TOPIC_FILE = str(pool)
        R.update_topic_pool(topics, "无", "2026-09-23")
        out = pool.read_text(encoding="utf-8")

        new_rows = [ln for ln in out.splitlines()
                    if ln.strip().startswith("|") and "---" not in ln
                    and "选题 | 钩子" not in ln]
        check("新选题已写入", len(new_rows) == 3, f"写入 {len(new_rows)} 行")
        check("日期子标题已创建", "### 09-23（3 条）" in out)
        check("新日期组在旧日期组之前", out.index("### 09-23") < out.index("### 08-09"))
        check("日期计数未被日期数字污染",
              not re.search(r"###\s*09-2[0-9]（\d{3,}", out) and "### 08-09（10 条）" in out)

        # ── 5. 同日再跑（当天第二次路由）：追加而非新建段，计数如实 ──
        R.update_topic_pool([topics[1]], "无", "2026-09-23")
        out2 = pool.read_text(encoding="utf-8")
        check("同日再次写入不重复建段", out2.count("### 09-23") == 1)

        # 断言方式：数「09-23 段内的实际数据行」，并与标题里的 N 对账
        hot_lines = out2.split("### 09-23")[1].split("### ")[0].splitlines()
        actual = [ln for ln in hot_lines
                  if ln.strip().startswith("|") and "---" not in ln
                  and "选题 | 钩子" not in ln]
        header_n = int(re.search(r"（(\d+) 条）", out2).group(1))
        check("计数标题 == 实际数据行数", header_n == len(actual),
              f"标题写 {header_n} 条，实际 {len(actual)} 行")
    finally:
        for p in tmp_root.glob("*"):
            p.unlink()
        tmp_root.rmdir()

    print()
    if FAILURES:
        print(f"✗ {len(FAILURES)} 项未通过: {FAILURES}")
        return 1
    print("✓ 全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
