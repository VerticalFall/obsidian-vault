#!/usr/bin/env python3
"""跨脚本集成测试 — 路由写出的选题池必须能被蒸馏正确消费。

为什么需要这个测试
    本仓库的选题池由 `run_daily_router.py`（每日）写入、由 `run_weekly_distill.py`
    （每周一）读取做冷却/归档。我改了前者的写入格式（表格行由 `extract_topic_pool`
    确定性生成、日期计数按实际行数重算），却从未验证后者是否还能读懂 —— 这正是
    **组件之间接缝处**最容易坏、而单元测试照不到的地方。

本测试把两个脚本串起来跑（全程离线，只用纯函数 + 临时文件）：
    真实路由日志 → parse_route_log → to_pool_row → update_topic_pool 写池
    → 蒸馏的 count_pool_stats / archive_topic_pool 读池并归档
并断言：行数一致、⭐/· 标记可读、归档能正确匹配、🌿 升入格式正确。

用法（在 每日日报/ 目录下）：
    python _test_pipeline_integration.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / ".github" / "scripts"))

import run_daily_router as R  # noqa: E402
import run_weekly_distill as W  # noqa: E402
from extract_topic_pool import dedupe_topics, parse_route_log, to_pool_row  # noqa: E402

FAILURES: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILURES.append(label)


TMP = HERE / "_test_tmp"


def cleanup() -> None:
    if not TMP.exists():
        return
    for child in sorted(TMP.rglob("*"), reverse=True):
        if child.is_file():
            child.unlink()
        elif child.is_dir():
            child.rmdir()
    TMP.rmdir()


EMPTY_POOL = (
    "# 选题池\n\n## 🔥 新进（最近 7 天）\n\n> 超过 7 天的选题 → 手动移入 🌿 或 💤\n\n"
    "## 🌿 持续发酵（有跨天信号累积）\n\n"
    "## 💤 等待更多信号\n\n"
    "## ✅ 已发布\n\n## 📦 归档\n\n| 周次 | 选题 | 去向 |\n|------|------|------|\n"
)


def main() -> int:
    cleanup()
    TMP.mkdir(exist_ok=True)
    pool = TMP / "_选题池.md"
    saved_topic_file = R.TOPIC_FILE
    # 蒸馏也读 TOPIC_FILE 模块常量 —— 不覆盖就会去改真实的 _选题池.md
    saved_distill_topic = W.TOPIC_FILE

    try:
        # ── 阶段 1：路由写池（用真实路由日志）──
        route_text = (HERE / "_路由" / "2026-09-23.md").read_text(encoding="utf-8")
        topics = parse_route_log(route_text)
        topics, _ = dedupe_topics(topics, "")
        check("阶段1：从真实路由日志提取到选题", len(topics) >= 2, f"{len(topics)} 条")

        pool.write_text(EMPTY_POOL, encoding="utf-8")
        R.TOPIC_FILE = str(pool)
        W.TOPIC_FILE = str(pool)
        R.update_topic_pool(topics, "无", "2026-09-23")
        written = pool.read_text(encoding="utf-8")

        # ── 阶段 2：蒸馏读池 —— 行数必须一致 ──
        stats_after_write = W.count_pool_stats(written)
        check("阶段2：蒸馏统计到的 🔥 行数与写入条数一致",
              stats_after_write["hot"] == len(topics),
              f"写入 {len(topics)} 条，蒸馏读到 🔥={stats_after_write['hot']}")

        # 每行都必须能被蒸馏的"数据行"判定识别（否则冷却/归档会漏掉）。
        # 注意：必须用与蒸馏**相同**的判定函数来筛选，不能自己写一套 —— 表头行
        # （`| 选题 | 钩子 |...`）也是 `|` 开头，自己写的朴素过滤会把它算进来。
        rows = [ln for ln in written.splitlines() if W.is_data_row(ln)]
        check("阶段2：每一行都被蒸馏视为数据行",
              len(rows) == len(topics), f"写入 {len(topics)} 条，蒸馏识别 {len(rows)} 行")

        # ⭐/· 标记必须保留（蒸馏的关键词匹配与人工扫读都依赖它）
        marks = [ln.split("|")[1].strip()[:1] for ln in rows]
        check("阶段2：⭐ 标记在写入后仍保留",
              any(m == "⭐" for m in marks), f"标记={marks}")

        # ── 阶段 3/4：用「上周」日期写池，才能走到冷却与升入逻辑 ──
        # （蒸馏只处理 ≤ last_sunday 的条目；用今天写池会被判定为"本周"而跳过，
        #   那样测的就不是冷却逻辑了 —— 这是本测试第一版的错误。）
        pool.write_text(EMPTY_POOL, encoding="utf-8")
        R.update_topic_pool(topics, "无", "2026-09-17")
        first_title = topics[0]["title"][:8]

        archived = W.archive_topic_pool(
            {"promote": [], "archive": [first_title], "keep_as_new": []},
            last_sunday="2026-09-20", today_str="2026-09-21")
        check("阶段3：按标题关键词能匹配并归档",
              any(first_title in e["title"] for e in archived),
              f"归档 {len(archived)} 条")

        # ── 阶段 4：周次标签与 🌿 升入格式 ──
        pool.write_text(EMPTY_POOL, encoding="utf-8")
        R.update_topic_pool(topics, "无", "2026-09-17")
        promoted = W.archive_topic_pool(
            {"promote": [first_title], "archive": [], "keep_as_new": []},
            last_sunday="2026-09-20", today_str="2026-09-21")
        pool_after = pool.read_text(encoding="utf-8")
        check("阶段4：promote 返回升入条目", len(promoted) >= 1, f"{len(promoted)} 条")
        check("阶段4：升入 🌿 区后带日期标注",
              "🔥区升入" in pool_after, "已写入 🌿 区")
        promoted_rows = [ln for ln in pool_after.splitlines() if "🔥区升入" in ln]
        check("阶段4：升入行格式为 4 列",
              bool(promoted_rows) and all(len(ln.split("|")) >= 5 for ln in promoted_rows),
              f"{len(promoted_rows)} 行")

        # ── 阶段 5：空池与脏行不应让蒸馏崩溃 ──
        dirty = EMPTY_POOL.replace(
            "## 🌿 持续发酵（有跨天信号累积）",
            "### 09-23（1 条）\n\n| 选题 | 钩子 | 角度 | 系列 |\n|------|------|------|------|\n"
            "| ⭐/· <选题标题> | <钩子> | <角度> | <系列> |\n\n## 🌿 持续发酵（有跨天信号累积）",
        )
        stats_dirty = W.count_pool_stats(dirty)
        check("阶段5：模板残留脏行不导致统计崩溃",
              isinstance(stats_dirty, dict) and "hot" in stats_dirty, str(stats_dirty))

        pool.write_text(EMPTY_POOL, encoding="utf-8")
        stats_empty = W.count_pool_stats(EMPTY_POOL)
        check("阶段5：空池统计为 0 且不报错", stats_empty["hot"] == 0, str(stats_empty))

    finally:
        R.TOPIC_FILE = saved_topic_file
        W.TOPIC_FILE = saved_distill_topic
        cleanup()

    print()
    if FAILURES:
        print(f"✗ {len(FAILURES)} 项未通过: {FAILURES}")
        return 1
    print("✓ 全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
