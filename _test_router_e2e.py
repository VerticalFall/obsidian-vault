#!/usr/bin/env python3
"""日报路由 — 端到端离线自测（mock DeepSeek，不联网、不改正式文件）。

这是最有价值的回归测试：把 main() 完整跑一遍，验证
    上下文 → 响应解析 → 截断体检 → 选题提取 → 去重 → 写入选题池
整条链路在**三种响应形态**下都正确：
    1. 完整响应（⭐ 区 + 普通选题区）→ 两个区的选题都进池
    2. 截断响应（只有 ⭐ 区）→ 能救回选题 + 产生告警注解
    3. API 失败 → 非零退出 + error 注解 + 不动选题池

用法（在 每日日报/ 目录下）：
    python _test_router_e2e.py
"""

from __future__ import annotations

import io
import os
import sys
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / ".github" / "scripts"))

import run_daily_router as R  # noqa: E402

FAILURES: list[str] = []

COMPLETE_RESPONSE = """===ROUTE_LOG===
# 日报路由 · 2026-09-23
输入: AI HOT(25条) + TrendRadar(54条) + X-Tweets(17条) + FollowBuilders(43条)
模式: 正常

## ⭐ 高优先级选题(→ 选题池)

### 01. 英伟达把网络业务拆出来单独定价
- 来源: AI HOT 2026-09-23
- 锚点: A、B
- 框架: 《叙事经济学》——叙事与事实的分裂
- 传播: 5/5(冲突/新鲜/情绪/解释/关联)
- 选题角度: 这是高优先级选题的角度说明。第二句话补充论证。
- merge_hint: 无
- 观点信号: 印证 V2

## 普通选题(→ 选题池)

### 01. 美国非农与出口数据打架
- 来源: TrendRadar 2026-09-23
- 锚点: C
- 框架: 《聪明的投资者》——安全边际
- 传播: 3/5(冲突/新鲜/情绪/解释/关联)
- 选题角度: 这是普通选题的角度说明。第二句话补充论证。
- merge_hint: 无
- 观点信号: 无关

## 🔄 更新现有选题
无

## 丢弃摘要
| 条目 | 原因 |
| 纯娱乐 | 无锚点 |
===END===
"""

TRUNCATED_RESPONSE = """===ROUTE_LOG===
# 日报路由 · 2026-09-23
输入: AI HOT(25条) + TrendRadar(54条)
模式: 正常

## ⭐ 高优先级选题(→ 选题池)

### 01. 磷化铟供应链的原子级瓶颈
- 来源: AI HOT 2026-09-23
- 锚点: A
- 框架: 《思考快与慢》——自动化偏见
- 传播: 5/5(冲突/新鲜/情绪/解释/关联)
- 选题角度: 这个选题的角度写到一半就断了，因为输出预算耗尽
"""


class FakePool:
    """给 main() 用的临时选题池。"""

    def __init__(self) -> None:
        self.root = HERE / "_test_tmp"
        self.root.mkdir(exist_ok=True)
        self.path = self.root / "_选题池.md"
        self.path.write_text(
            "# 选题池\n\n## 🔥 新进（最近 7 天）\n\n> 提示行\n\n"
            "### 08-09（10 条）\n\n| 选题 | 钩子 | 角度 | 系列 |\n|------|------|------|------|\n\n\n"
            "## 🌿 持续发酵\n\n## 💤 等待更多信号\n\n## 📦 归档\n",
            encoding="utf-8",
        )

    def rows(self) -> list[str]:
        text = self.path.read_text(encoding="utf-8")
        hot = text.split("## 🔥")[1].split("\n## ")[0]
        return [
            ln for ln in hot.splitlines()
            if ln.strip().startswith("|") and "---" not in ln and "选题 | 钩子" not in ln
        ]

    def cleanup(self) -> None:
        # main() 会在临时目录下建 _路由/，需递归清理
        if self.root.exists():
            for child in sorted(self.root.rglob("*"), reverse=True):
                if child.is_file():
                    child.unlink()
                elif child.is_dir():
                    child.rmdir()
            self.root.rmdir()


def run_main(response: str | Exception, pool: FakePool) -> tuple[int, str]:
    """跑一遍 main()，返回 (返回码, stdout)。"""
    def fake_call(system: str, user: str, max_tokens: int = 0) -> str:
        if isinstance(response, Exception):
            raise response
        return response

    saved_call, saved_file = R.call_deepseek, R.TOPIC_FILE
    saved_dir, saved_route = R.ROUTE_DIR, os.environ.get("TODAY_OVERRIDE")
    R.call_deepseek = fake_call           # type: ignore[assignment]
    R.TOPIC_FILE = str(pool.path)
    R.ROUTE_DIR = str(pool.root / "_路由")
    os.environ["TODAY_OVERRIDE"] = "2026-09-23"
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            code = R.main()
    finally:
        R.call_deepseek = saved_call     # type: ignore[assignment]
        R.TOPIC_FILE = saved_file
        R.ROUTE_DIR = saved_route
        if saved_route is None:
            os.environ.pop("TODAY_OVERRIDE", None)
        else:
            os.environ["TODAY_OVERRIDE"] = saved_route
    return code, buf.getvalue()


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILURES.append(label)


def main() -> int:
    # ── 场景 1：完整响应 → 两个区的选题都进池 ──
    pool = FakePool()
    try:
        code, out = run_main(COMPLETE_RESPONSE, pool)
        rows = pool.rows()
        check("完整响应：main 正常退出", code == 0, f"return={code}")
        check("完整响应：⭐ 区选题进池", any("英伟达把网络业务" in r for r in rows), f"{len(rows)} 行")
        check("完整响应：普通区选题也进池（旧解析器读不到表格格式）",
              any("美国非农与出口数据" in r for r in rows), f"{len(rows)} 行")
        check("完整响应：两区各一条，共 2 条", len(rows) == 2, f"{len(rows)} 行")
        check("完整响应：无截断告警", "WARNING: 路由日志疑似被截断" not in out)
        log = (pool.root / "_路由" / "2026-09-23.md")
        check("完整响应：路由日志已落盘", log.is_file(), str(log.name))
        if log.is_file():
            log.unlink()
    finally:
        pool.cleanup()

    # ── 场景 2：截断响应 → 救回选题 + 出告警注解 ──
    pool = FakePool()
    try:
        code, out = run_main(TRUNCATED_RESPONSE, pool)
        rows = pool.rows()
        check("截断响应：仍能救回选题", len(rows) == 1, f"{len(rows)} 行")
        check("截断响应：有截断告警", "疑似被截断" in out, out.strip().splitlines()[-3:])
        check("截断响应：产生 warning 注解", "::warning title=日报路由::" in out)
    finally:
        pool.cleanup()

    # ── 场景 3：API 失败 → 非零退出 + error 注解 + 不动池子 ──
    pool = FakePool()
    try:
        before = pool.path.read_text(encoding="utf-8")
        code, out = run_main(RuntimeError("HTTP 400 Bad Request — model not found"), pool)
        check("API 失败：返回非零", code == 1, f"return={code}")
        check("API 失败：产生 error 注解", "::error title=日报路由::" in out)
        check("API 失败：原因被带出（模型名可见）", "model not found" in out)
        check("API 失败：选题池未被改动", pool.path.read_text(encoding="utf-8") == before)
    finally:
        pool.cleanup()

    # ── 场景 4：响应缺 ROUTE_LOG 段 → 兜底 + 告警，且仍然提取 ──
    pool = FakePool()
    try:
        code, out = run_main(TRUNCATED_RESPONSE.replace("===ROUTE_LOG===", ""), pool)
        check("缺 ROUTE_LOG 段：有兜底告警", "::warning" in out, out.strip().splitlines()[-2:])
        check("缺 ROUTE_LOG 段：仍能提取选题", len(pool.rows()) >= 1, f"{len(pool.rows())} 行")
    finally:
        pool.cleanup()

    print()
    if FAILURES:
        print(f"✗ {len(FAILURES)} 项未通过: {FAILURES}")
        return 1
    print("✓ 全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
