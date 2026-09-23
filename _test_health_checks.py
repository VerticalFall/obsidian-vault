#!/usr/bin/env python3
"""健康检查 7/8/9 的契约测试 — 防止"狼来了"式误报。

为什么需要
    检查 7「每日精选产出」、8「路由覆盖率」、9「写作产出」是本次新增的监控项。
    检查 9 会直接对用户报 🔴（当前：写作产出已停滞 63 天）——如果它的阈值或日期解析
    有误报，用户会逐渐忽略所有告警，监控体系整体失信。因此必须把它的判定契约钉死：
    分档边界、两种日期写法、跨年不误报、空区不崩。

全部离线，只用临时选题池文件，不改动真实数据。

用法（在 每日日报/ 目录下）：
    python _test_health_checks.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / ".github" / "scripts"))

import check_health as H  # noqa: E402

FAILURES: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILURES.append(label)


TMP = HERE / "_test_tmp"


def pool_with_published(date_cell: str) -> str:
    """造一份带指定「已发布」日期的选题池文本。"""
    return (
        "# 选题池\n\n## 🔥 新进（最近 7 天）\n\n## 🌿 持续发酵\n\n## 💤 等待更多信号\n\n"
        "## ✅ 已发布\n\n| 日期 | 选题 | 文章 |\n|------|------|------|\n"
        f"| {date_cell} | 某选题 | [[某文]] |\n\n## 📦 归档\n"
    )


def with_pool(pool_text: str, fn):
    """把真实 TOPIC_FILE 换成临时文件后调用 fn，保证不碰正式数据。"""
    TMP.mkdir(exist_ok=True)
    p = TMP / "_选题池.md"
    p.write_text(pool_text, encoding="utf-8")
    saved = H.TOPIC_FILE
    H.TOPIC_FILE = str(p)
    try:
        return fn()
    finally:
        H.TOPIC_FILE = saved
        p.unlink()
        TMP.rmdir()


def main() -> int:
    # ── 检查 9：写作产出 ──
    check("停滞 63 天判 🔴",
          with_pool(pool_with_published("07-22"),
                    lambda: H.check_writing_output("2026-09-23"))[0] == "🔴")
    check("停滞 63 天给出具体天数",
          "63" in with_pool(pool_with_published("07-22"),
                            lambda: H.check_writing_output("2026-09-23"))[1])

    # 分档边界：>=30 🔴 / >=14 🟡 / <14 🟢
    cases = [("2026-08-01", "2026-09-23", "🔴", 53),   # 53 天
             ("2026-08-25", "2026-09-23", "🟡", 29),   # 29 天
             ("2026-09-15", "2026-09-23", "🟢", 8)]    # 8 天
    for pub, today, want, gap in cases:
        lvl, detail, _ = with_pool(pool_with_published(pub[5:]),
                                   lambda t=today: H.check_writing_output(t))
        check(f"{gap} 天判 {want}", lvl == want, f"{lvl} {detail}")

    # 恰好 30 天 → 🔴；恰好 14 天 → 🟡（边界含等号）
    m = with_pool(pool_with_published("2026-08-24"), lambda: H.check_writing_output("2026-09-23"))
    check("恰好 30 天判 🔴（边界）", m[0] == "🔴", f"{m[0]} {m[1]}")
    m = with_pool(pool_with_published("2026-09-09"), lambda: H.check_writing_output("2026-09-23"))
    check("恰好 14 天判 🟡（边界）", m[0] == "🟡", f"{m[0]} {m[1]}")

    # 未来日期（跨年补年份所致）不得误报为停滞
    m = with_pool(pool_with_published("12-31"), lambda: H.check_writing_output("2026-09-23"))
    check("未来日期不误报", m[0] == "🟢", f"{m[0]} {m[1]}")

    # 支持 YYYY-MM-DD 写法
    m = with_pool(pool_with_published("2026-07-22"), lambda: H.check_writing_output("2026-09-23"))
    check("支持 YYYY-MM-DD 写法", m[0] == "🔴" and "2026-07-22" in m[1], f"{m[0]} {m[1]}")

    # 异常输入不崩、且不误判为 🟢
    m = with_pool("# 选题池\n\n## 🔥 新进\n", lambda: H.check_writing_output("2026-09-23"))
    check("缺「✅ 已发布」区 → 🟡 而非 🟢/崩溃", m[0] == "🟡", f"{m[0]} {m[1]}")
    m = with_pool(pool_with_published("不是日期"), lambda: H.check_writing_output("2026-09-23"))
    check("无效日期 → 🟡 而非 🟢/崩溃", m[0] == "🟡", f"{m[0]} {m[1]}")

    # ── 检查 8：路由覆盖率 ──
    lvl, detail, lost = H.check_router_coverage(days=7)
    check("路由覆盖率返回三要素", lvl in ("🟢", "🟡", "🔴") and isinstance(lost, int),
          f"{lvl} {detail} lost={lost}")
    check("路由覆盖率分级与缺失天数一致",
          (lost == 0 and lvl == "🟢") or (lost > 0 and lvl in ("🟡", "🔴")),
          f"lost={lost} level={lvl}")

    # ── 检查 7：每日精选产出 ──
    lvl, detail, _ = H.check_digest("2026-09-23")
    check("精选缺失时报 🟡（非 🔴，属可降级项）", lvl == "🟡", f"{lvl} {detail}")

    print()
    if FAILURES:
        print(f"✗ {len(FAILURES)} 项未通过: {FAILURES}")
        return 1
    print("✓ 全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
