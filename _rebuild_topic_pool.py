#!/usr/bin/env python3
"""重建选题池 — 从路由日志恢复断供 6 周的选题（先出提案文件，不动正式文件）。

背景
    🔥 区自 2026-08-10 起被清空后连续 6 周断供，路由日志里可恢复的选题
    从未落池。本脚本把 `_路由/` 日志里能提取到的选题按原日期归位，
    同时清掉「表头下无数据行」的历史空壳节。

安全设计
    默认只写提案文件 `_选题池_提案.md`，**不碰 `_选题池.md`**。
    加 `--apply` 才写正式文件（内容红线：需用户确认后执行）。

用法
    python _rebuild_topic_pool.py              # 出提案文件
    python _rebuild_topic_pool.py --apply      # 确认后落盘
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / ".github" / "scripts"))

from extract_topic_pool import dedupe_topics, parse_route_log, to_pool_row  # noqa: E402

POOL = HERE / "_选题池.md"
PROPOSAL = HERE / "_选题池_提案.md"
ROUTE_DIR = HERE / "_路由"

# 提案文件顶部必须写明的下游行为（蒸馏会在下周一整批归档这批恢复的选题）
POOL_REBUILD_NOTE = """> ⚠️ **恢复说明（务必先读）**
>
> 本文件由 `_rebuild_topic_pool.py` 从 `_路由/` 历史日志恢复，**未改动 `_选题池.md`**。
>
> - 恢复选题：%d 条，按原路由日期归位（08-21 ~ 09-23）。
> - **下一次周一蒸馏会把这一整批归档**：蒸馏的归档判据是「条目日期 ≤ last_sunday
>   且未被 `TOPIC_OPS` 显式保留」，未匹配的条目**默认 archive**，与日期新旧无关。
>   （曾尝试"把日期改挂到今天"来规避，实测无效 —— 今天同样 ≤ last_sunday。）
> - 也就是说：**这是个 5 天窗口**。想真正用上它们，请在下一个周一前挑出要写的，
>   或让蒸馏显式 `keep_as_new`。
> - 只想看不想动池子 → 保持现状即可，无需执行任何命令。
"""

HOT_HEADER = "## 🔥 新进（最近 7 天）"
HOT_NOTE = "> 超过 7 天的选题 → 手动移入 🌿 或 💤"


def _is_data_row(line: str) -> bool:
    s = line.strip()
    if not s.startswith("|"):
        return False
    if set(s) <= set("|-: "):
        return False
    if "---" in s:
        return False
    cols = [c.strip() for c in s.split("|")]
    # 表头行：第二列是「选题」
    if len(cols) >= 2 and cols[1] == "选题":
        return False
    return True


def is_complete(topic: dict) -> bool:
    """选题必须有标题 + 钩子 + 角度才算可用 —— 截断日志会产出空字段的脏行。"""
    return bool(topic["title"].strip() and topic["hook"].strip() and topic["angle"].strip())


def extract_all(since: str = "2026-08-15") -> dict[str, list[dict]]:
    """按日期提取路由日志里的选题（跨天去重 + 完整性过滤）。

    `since` 起点：路由日志是**累积式**的（同一事件在后续日期的日志里会重复出现），
    越早的日志越可能把已归档的老选题再捞一遍。选题池 🔥 区只关心近期，
    所以默认只回看 `since` 之后的日志。
    """
    by_date: dict[str, list[dict]] = {}
    seen: list[dict] = []
    for path in sorted(ROUTE_DIR.glob("*.md")):
        if path.stem < since:
            continue
        text = path.read_text(encoding="utf-8")
        topics = [t for t in parse_route_log(text) if is_complete(t)]
        dropped = len(parse_route_log(text)) - len(topics)
        if dropped:
            print(f"  跳过节内不完整选题 {dropped} 条 [{path.stem}]（日志被截断）")
        if not topics:
            continue
        # 跨天去重：拿"已收录选题"生成的表格行当既有池文本传入
        pool_text = "\n".join(to_pool_row(t) for t in seen)
        final, skipped = dedupe_topics(topics, pool_text)
        for s in skipped:
            print(f"  去重跳过 [{path.stem}] {s['title'][:40]} — {s['skip_reason']}")
        if final:
            by_date[path.stem] = final
            seen.extend(final)
    return by_date


def rebuild(existing: str, by_date: dict[str, list[dict]]) -> tuple[str, dict]:
    """重建选题池文本。返回 (新文本, 统计)。

    恢复的选题一律**按原路由日期归位**（忠于历史，便于核对来源）。

    ⚠️ 必须知道的下游行为（实测，非推测）：
        蒸馏的归档判据是「条目日期 ≤ last_sunday **且** 未被 TOPIC_OPS 显式保留」。
        未匹配 TOPIC_OPS 的条目**默认 archive**，与日期新旧无关 —— 也就是说
        **下一次周一蒸馏会把这一整批恢复的选题归档掉**。

        我一度想用「把日期改挂到今天」来规避，实测**无效**：今天仍 ≤ last_sunday，
        依然落入默认归档分支。所以本脚本不提供该选项 —— 提供它只会造成
        "这样就能留住"的错觉。

        要让恢复的选题活下来，正确做法是让蒸馏显式保留它们（见 POOL_REBUILD_NOTE）。
    """
    lines = existing.split("\n")

    # ── 定位 🔥 区 ──
    hot_start = next(i for i, l in enumerate(lines) if l.strip().startswith("## 🔥"))
    hot_end = next(
        (i for i in range(hot_start + 1, len(lines))
         if lines[i].strip().startswith("## ")),
        len(lines),
    )

    # 🔥 区之前 + 区头 + 提示行
    head = lines[: hot_start + 1]
    # 保留提示行（以 > 开头）
    note_lines = [l for l in lines[hot_start + 1 : hot_end] if l.strip().startswith(">")]
    after = lines[hot_end:]

    # ── 新 🔥 区：按日期倒序（最新在前）──
    hot: list[str] = [""]
    hot.extend(note_lines or [HOT_NOTE])
    hot.append("")
    # 日期子标题必须是 `### MM-DD` —— 蒸馏用 `^###\s+(\d{2}-\d{2})` 取月日再拼年份。
    for date in sorted(by_date, reverse=True):
        topics = by_date[date]
        hot.append(f"### {date[5:]}（{len(topics)} 条）")
        hot.append("")
        hot.append("| 选题 | 钩子 | 角度 | 系列 |")
        hot.append("|------|------|------|------|")
        for t in topics:
            hot.append(to_pool_row(t))
        hot.append("")

    new_text = "\n".join(head + hot + after)
    new_text = re.sub(r"\n{4,}", "\n\n\n", new_text)

    stats = {
        "dates": len(by_date),
        "topics": sum(len(v) for v in by_date.values()),
        "old_shells": sum(
            1 for l in lines[hot_start:hot_end] if l.strip().startswith("### ")
        ),
    }
    return new_text, stats


def insert_note_after_frontmatter(text: str, note: str) -> str:
    """把说明插到 YAML frontmatter **之后**。

    frontmatter 必须在文件最开头，否则 Obsidian 无法解析（title/aliases 失效）。
    第一版把说明直接拼在最前面，正好踩了这个坑。
    """
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            fm_end = text.find("\n", end + 1)
            if fm_end != -1:
                return text[: fm_end + 1] + "\n" + note + "\n---\n\n" + text[fm_end + 1 :]
    return note + "\n---\n\n" + text


def main() -> int:
    apply = "--apply" in sys.argv
    existing = POOL.read_text(encoding="utf-8")

    print("从路由日志提取选题 …")
    by_date = extract_all()
    total = sum(len(v) for v in by_date.values())
    print(f"共 {len(by_date)} 个日期、{total} 条选题")
    for d in sorted(by_date, reverse=True):
        print(f"  {d}: {len(by_date[d])} 条")

    new_text, stats = rebuild(existing, by_date)
    print(f"\n清除旧空壳节 {stats['old_shells']} 个 → 新 🔥 区 {stats['topics']} 条")
    print("⚠️ 下一次周一蒸馏会把这一整批归档（默认 archive 策略，与日期新旧无关）")

    if apply:
        backup = POOL.with_suffix(".md.bak")
        backup.write_text(existing, encoding="utf-8")
        POOL.write_text(new_text, encoding="utf-8")
        print(f"已落盘: {POOL}（原文件备份 {backup.name}）")
    else:
        PROPOSAL.write_text(
            insert_note_after_frontmatter(new_text, POOL_REBUILD_NOTE % stats["topics"]),
            encoding="utf-8",
        )
        print(f"提案已写出: {PROPOSAL}（未改动 {POOL.name}）")
        print("确认后执行: python _rebuild_topic_pool.py --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
