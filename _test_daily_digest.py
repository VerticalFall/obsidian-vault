#!/usr/bin/env python3
"""每日精选渲染 — 离线自测（不调 LLM）。

验证 render_daily_digest.py 的上下文拼装、解析与体检逻辑。
真实 LLM 输出质量靠 _每日精选/ 产物人工抽查，不在本测试范围。

用法（在 每日日报/ 目录下）：
    python _test_daily_digest.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / ".github" / "scripts"))

import render_daily_digest as D  # noqa: E402

FAILURES: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILURES.append(label)


def main() -> int:
    # ── 1. 上下文拼装（用真实的 2026-09-23 四源 + 路由日志）──
    ctx, stats = D.build_context("2026-09-23")
    check("四源全部读入", all(stats[k] > 0 for k in ("AI HOT", "TrendRadar", "X-Tweets", "FollowBuilders")),
          "  ".join(f"{k}={v}" for k, v in stats.items()))
    check("路由日志读入", stats["路由日志"] > 0, f"{stats['路由日志']} 字符")
    check("上下文含全部区块", all(s in ctx for s in ("AI HOT", "TrendRadar", "X-Tweets", "FollowBuilders", "路由日志")))

    # ── 2. 源缺失时优雅降级 ──
    ctx2, stats2 = D.build_context("1999-01-01")
    check("缺失日期不报错且标记无产出", stats2["AI HOT"] == 0 and "当日无产出" in ctx2)

    # ── 3. 单源字符上限 ──
    big = HERE / "_test_tmp_big.md"
    big.write_text("x" * (D.PER_SOURCE_LIMIT + 500), encoding="utf-8")
    truncated = D.read_file(str(big), D.PER_SOURCE_LIMIT)
    big.unlink()
    check("超长源被截断", "已截断" in truncated, f"{len(truncated)} 字符")

    # ── 4. ===DIGEST=== 包裹解析 ──
    raw = "前言\n===DIGEST===\n# 标题\n正文内容\n===END===\n后记"
    check("能剥掉包裹只取正文", D.extract_digest(raw) == "# 标题\n正文内容",
          repr(D.extract_digest(raw)))
    fenced = "```markdown\n# 标题\n正文\n```"
    check("能剥掉 markdown 围栏", D.extract_digest(fenced) == "# 标题\n正文",
          repr(D.extract_digest(fenced)))

    # ── 5. 体检器 ──
    good = (
        "# 每日精选 · 2026-09-23\n\n> 一句话结论\n\n"
        "## 📌 今天最重要的 5 条\n\n1. **某公司降价 50%**\n   - 事实：降了一半。\n\n"
        "## 🔢 数字速览\n\n- 47% — 每季度成本降幅\n\n"
        "## 🌐 领域速览\n\n- **AI/科技**：某事发生。\n\n"
        "## ✍️ 今天可写\n\n- **选题标题**（5/5）\n  - 钩子：一句钩子\n"
    ) + "补充正文。" * 60
    check("完整样例无问题", D.validate_digest(good) == [], "；".join(D.validate_digest(good)))

    missing = D.validate_digest("## 📌 今天最重要的 5 条\n\n内容很短")
    check("缺区被报出", sum(1 for p in missing if "缺「" in p) >= 3, "；".join(missing))
    check("正文过短被报出", any("过短" in p for p in missing), "；".join(missing))

    nodigit = D.validate_digest(good.replace("- 47% — 每季度成本降幅", "- 成本在下降"))
    check("数字速览无数字被报出", any("没有任何数字" in p for p in nodigit), "；".join(nodigit))

    chopped = D.validate_digest(good + "\n最后一句没写完，")
    check("末尾截断被报出", any("截断" in p for p in chopped), "；".join(chopped))

    # ── 6. 失败可见性：注解格式 + 缺 Key 必须报错 ──
    import io
    import os
    from contextlib import redirect_stdout

    buf = io.StringIO()
    with redirect_stdout(buf):
        D.gh_annotate("error", "测试\n多行 % 百分号")
    line = buf.getvalue().strip()
    check("注解使用 GitHub 语法", line.startswith("::error title=每日精选::"), line)
    check("注解已转义换行与百分号", "\n" not in line and "%25" in line, line)

    saved = os.environ.pop("DEEPSEEK_API_KEY", None)
    try:
        D.call_deepseek("sys", "user")
        raised = False
    except Exception as exc:  # noqa: BLE001
        raised = "DEEPSEEK_API_KEY" in str(exc)
    finally:
        if saved is not None:
            os.environ["DEEPSEEK_API_KEY"] = saved
    check("缺 Key 时调用报错且说明原因", raised)

    # ── 8. 降级路径（LLM 不可用时的产出保障）──
    fb = D.build_fallback_digest("2026-09-23", "测试原因")
    check("降级产物含四个区标题",
          all(s in fb for s in ("今天最重要的", "数字速览", "领域速览", "今天可写")),
          "缺失: " + ", ".join(s for s in ("今天最重要的", "数字速览", "领域速览", "今天可写") if s not in fb))
    check("降级产物标注未经加工", "未经 LLM 编辑加工" in fb and "测试原因" in fb)
    check("降级产物含真实选题", "杰文斯" in fb or "放缓AI" in fb)

    # 数字抽取的质量回归（下列噪声都是实测踩出来的）
    nums = D.extract_numbers("2026-09-23")
    raw_values = [n for n, _ in nums]
    check("数字抽取有结果", len(nums) >= 3, f"{len(nums)} 条: {raw_values}")
    check("不带 URL 编码数字（曾产出 81500% 垃圾）",
          not any(re.match(r"^\d{5,}%", v) for v in raw_values), str(raw_values))
    ctxs = [c for _, c in nums]
    check("同一行不重复产出多个数字",
          len(ctxs) == len(set(ctxs)), f"{len(ctxs)} 条 / {len(set(ctxs))} 个不同上下文")
    check("不含路由日志元数据行",
          not any(re.match(r"^[-*]\s*(来源|框架|锚点)\s*[:：]", c) for c in ctxs))
    check("不含引用行（回复/引用噪声）", not any(c.startswith(">") for c in ctxs))

    # 内容标题抽取：各源都要能出内容标题，且不能是目录/统计行
    for src in ("AI-HOT", "TrendRadar", "FollowBuilders"):
        ts = D._content_titles(f"{src}/2026-09-23.md")
        check(f"{src} 可提取内容标题", len(ts) >= 1, str(ts[:1]))
        check(f"{src} 未把分类标签当标题",
              not any(re.search(r"[（(]\d+\s*条[）)]\s*$", t) for t in ts), str(ts))
    check("统计行不被当标题",
          not any("位 builder" in t or "条推文" in t
                  for t in D._content_titles("FollowBuilders/2026-09-23.md")))

    # ── 7. 端到端（mock LLM）：产物落盘 / 失败不动产物 ──
    GOOD_OUTPUT = (
        "===DIGEST===\n# 每日精选 · 2026-09-23\n\n> 一句话结论\n\n"
        "## 📌 今天最重要的 5 条\n\n1. **某公司降价 50%**\n   - 事实：降了一半。\n\n"
        "## 🔢 数字速览\n\n- 47% — 每季度成本降幅\n\n"
        "## 🌐 领域速览\n\n- **AI/科技**：某事发生。\n\n"
        "## ✍️ 今天可写\n\n- **选题标题**（5/5）\n  - 钩子：一句钩子\n"
        "===END==="
    )
    tmp_root = HERE / "_test_tmp"
    tmp_root.mkdir(exist_ok=True)
    out_root = tmp_root / "_每日精选"
    saved_call, saved_dir = D.call_deepseek, D.OUT_DIR
    saved_date = os.environ.get("TODAY_OVERRIDE")
    os.environ["TODAY_OVERRIDE"] = "2026-09-23"

    def fake_ok(system: str, user: str, max_tokens: int = 0) -> str:
        return GOOD_OUTPUT

    def fake_fail(system: str, user: str, max_tokens: int = 0) -> str:
        raise RuntimeError("HTTP 401 Unauthorized — invalid api key")

    try:
        D.OUT_DIR = str(out_root)
        D.call_deepseek = fake_ok  # type: ignore[assignment]
        buf = io.StringIO()
        with redirect_stdout(buf):
            code_ok = D.main()
        artifact = out_root / "2026-09-23.md"
        check("端到端：成功时返回 0", code_ok == 0, f"return={code_ok}")
        check("端到端：产物落在 _每日精选/YYYY-MM-DD.md", artifact.is_file(), str(artifact.name))
        if artifact.is_file():
            body = artifact.read_text(encoding="utf-8")
            check("端到端：产物无 ===DIGEST=== 包裹残留", "===DIGEST===" not in body)
            check("端到端：产物含四个区", all(s in body for s in ("今天最重要的", "数字速览", "领域速览", "今天可写")))

        before = artifact.read_text(encoding="utf-8") if artifact.is_file() else ""
        D.call_deepseek = fake_fail  # type: ignore[assignment]
        buf2 = io.StringIO()
        with redirect_stdout(buf2):
            code_fail = D.main()
        out2 = buf2.getvalue()
        # 设计变更：LLM 失败不再归零，改为产出「降级版精选」。
        # 理由：LLM 一坏整条产出层就没了，而这台机器上 LLM 恰恰已经坏了几周。
        check("端到端：LLM 失败仍返回 0（产出降级版而非归零）", code_fail == 0, f"return={code_fail}")
        check("端到端：失败时有 error 注解", "::error title=每日精选::" in out2)
        check("端到端：失败时明确说明改产出降级版", "降级精选" in out2, out2.strip().splitlines()[-1:])
        after = artifact.read_text(encoding="utf-8") if artifact.is_file() else ""
        check("端到端：降级版覆盖了正常版产物", after != before and after != "")
        check("端到端：降级版带明确标注", "降级版" in after and "未经 LLM 编辑加工" in after)
        check("端到端：降级版仍含四个区",
              all(s in after for s in ("今天最重要的", "数字速览", "领域速览", "今天可写")))
        check("端到端：降级版记录了失败原因", "invalid api key" in after, "")
    finally:
        D.call_deepseek = saved_call  # type: ignore[assignment]
        D.OUT_DIR = saved_dir
        if saved_date is None:
            os.environ.pop("TODAY_OVERRIDE", None)
        else:
            os.environ["TODAY_OVERRIDE"] = saved_date
        if tmp_root.exists():
            for child in sorted(tmp_root.rglob("*"), reverse=True):
                if child.is_file():
                    child.unlink()
                elif child.is_dir():
                    child.rmdir()
            tmp_root.rmdir()

    print()
    if FAILURES:
        print(f"✗ {len(FAILURES)} 项未通过: {FAILURES}")
        return 1
    print("✓ 全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
