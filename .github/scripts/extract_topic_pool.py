#!/usr/bin/env python3
"""从路由日志确定性提取选题池行 — 修复「模型输出截断导致选题池断供」。

背景（为什么需要这个脚本）
    旧流程让模型在一次生成里同时输出：路由日志正文 + `===TOPIC_POOL_UPDATES===`
    选题池表格行 + `===TOPIC_UPDATES===`。路由日志正文本身就写掉数千字，
    max_tokens 预算耗尽后模型在「高优先级选题」段之后就停了 —— 实测
    `_路由/2026-08-21/09-03/09-04/09-23` 全部只有 ⭐ 区，`普通选题`、`更新`、
    `POOL_UPDATES` 段全部缺失。结果：路由日志落盘（内容被砍半），选题池连续 6 周断供。

修复思路
    路由日志改为**唯一事实来源**：模型只负责产出结构化 markdown（它已经做得很稳），
    选题池表格行由本脚本从路由日志里**确定性解析**出来，不再依赖模型的第二段输出。
    解析失败时明确报错，不静默跳过（旧逻辑静默 = 6 周没人发现）。

用法
    python .github/scripts/extract_topic_pool.py _路由/2026-09-23.md
    python .github/scripts/extract_topic_pool.py _路由/2026-09-23.md --format preview
    python .github/scripts/extract_topic_pool.py _路由/2026-09-23.md --format rows
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# 选题池表格列：| 选题 | 钩子 | 角度 | 系列 |
MAX_CELL = 120  # 单元格过长会让表格没法扫读


def _strip_md(text: str) -> str:
    """去掉 markdown 强调符，保留正文。"""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    return text.strip()


def _cell(text: str, limit: int = MAX_CELL) -> str:
    """把任意文本压成单行表格单元格。"""
    text = _strip_md(text)
    text = text.replace("|", "／").replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text


def _field(block: str, *names: str) -> str:
    """取 `- 名称: 值` 形式的字段值（值可跨行直到下一个 `- ` 字段）。"""
    for name in names:
        pattern = rf"(?m)^-\s*{re.escape(name)}\s*[:：]\s*(.+?)(?=\n-\s*\S+\s*[:：]|\n#|\n##|\Z)"
        m = re.search(pattern, block, re.S)
        if m:
            value = " ".join(line.strip() for line in m.group(1).splitlines()).strip()
            if value:
                return value
    return ""


def _hook_from_angle(angle: str) -> str:
    """没有独立 `钩子` 字段时，从选题角度里取第一句当钩子。

    顺带剥掉模型爱写的元话语前缀（"核心钩子是…"、"典型XX案例——"、
    "从…切入"），这些不是钩子本身，留着只会占宽度。
    """
    angle = _strip_md(angle)
    if not angle:
        return ""
    first = re.split(r"[。；;]", angle)[0].strip()
    # 元话语前缀
    first = re.sub(r"^(核心钩子是|核心冲突是|钩子是|切入角度[:：]?)\s*", "", first)
    first = re.sub(r"^典型[「\"']?[^」\"'——]{0,20}[」\"']?案例\s*——\s*", "", first)
    # "从…切入" 只留切入的内容，不留"从/切入"壳
    m = re.match(r"^从[「\"']?(.+?)[」\"']?切入[:：]?(.*)$", first)
    if m:
        rest = m.group(2).strip(" ：:——")
        first = rest or m.group(1)
    return first.strip() or angle


def _series_from_title(title: str) -> str:
    """标题里的 `——` 后半句常是系列线索；默认「独立」。"""
    return "独立"


def dedupe_topics(topics: list[dict], pool_text: str = "") -> tuple[list[dict], list[dict]]:
    """当日去重 + 与选题池已存在条目去重（按标题字符重合度）。

    返回 (保留列表, 跳过列表)；跳过项带 skip_reason，供日志说明。

    阈值刻意保守（宁留重复，不误杀）：同一事件不同措辞（如
    「Nvidia 129 亿美元收购 Hugging Face」vs「NVDA 129 亿美元买 HF」）
    归一化后相似度约 0.6，而不同选题普遍 <0.2 —— 两者之间有很宽的分离带。
    只做轻量实体别名归一，不做激进改写。
    """
    # 轻量实体别名归一：只处理高频同义写法
    ALIASES = {
        "nvidia": "nvda", "英伟达": "nvda",
        "huggingface": "hf", "hugging face": "hf",
        "微软": "msft", "microsoft": "msft",
        "谷歌": "goog", "google": "goog",
        "meta": "meta", "脸书": "meta",
        "openai": "openai", "奥特曼": "altman", "奥尔特曼": "altman",
        "anthropic": "anthropic", "claude": "claude",
        "amazon": "amzn", "亚马逊": "amzn",
        "buy": "buy", "收购": "buy", "买": "buy", "并购": "buy",
        "美元": "$", "亿美元": "$", "亿": "$",
    }

    def norm(s: str) -> str:
        s = s.lower()
        for k, v in ALIASES.items():
            s = s.replace(k, v)
        return re.sub(r"[^\w\u4e00-\u9fff$]", "", s)

    # 泛用词不进实体集：这些词在 AI 选题里天天出现，重合不代表同一事件
    STOPWORDS = {
        "ai", "buy", "the", "and", "for", "not", "new", "inc", "llc",
        "gpt", "llm", "ceo", "ipo", "meta", "claude", "anthropic", "openai",
        "msft", "goog", "amzn", "altman", "agent", "agents", "model", "models",
    }

    def entities(s: str) -> set[str]:
        """抽取高信号实体：拉丁词（≥2 字符，去停用词）+ 数字串。"""
        s = s.lower()
        for k, v in ALIASES.items():
            s = s.replace(k, v)
        ents = {w for w in re.findall(r"[a-z]{2,}", s) if w not in STOPWORDS}
        ents |= {f"num:{n}" for n in re.findall(r"\d{2,}", s)}
        return ents

    def similar(a: str, b: str) -> float:
        """实体重叠优先，回退到汉字集合重合度。

        注意：单个实体重叠**绝不**判定为重复 —— AI 选题里 OpenAI / Anthropic /
        英伟达 这类词几乎天天出现，单实体重合是噪声而非信号。只有共享 ≥2 个
        高信号实体（如 nvda + hf）才认定为同一选题。
        """
        ea, eb = entities(a), entities(b)
        if len(ea & eb) >= 2:
            return 1.0
        sa, sb = set(norm(a)), set(norm(b))
        if not sa or not sb:
            return 0.0
        return len(sa & sb) / len(sa | sb)

    THRESHOLD = 0.5

    kept: list[dict] = []
    skipped: list[dict] = []
    existing_titles = []
    for row in pool_text.splitlines():
        row = row.strip()
        if row.startswith("|") and "---" not in row:
            cols = [c.strip() for c in row.split("|")]
            if len(cols) >= 3 and cols[1] and not cols[1].startswith("选题"):
                existing_titles.append(re.sub(r"^[⭐·/◈\s]+", "", cols[1]))

    for t in topics:
        dup_of = ""
        best = 0.0
        for prev in kept:
            score = similar(t["title"], prev["title"])
            if score >= THRESHOLD and score > best:
                dup_of, best = prev["title"], score
        if not dup_of:
            for prev_title in existing_titles:
                score = similar(t["title"], prev_title)
                if score >= THRESHOLD and score > best:
                    dup_of, best = prev_title, score
        if dup_of:
            skipped.append({**t, "skip_reason": f"与「{dup_of[:30]}」重复（相似度 {best:.2f}）"})
        else:
            kept.append(t)
    return kept, skipped


def parse_route_log(text: str) -> list[dict]:
    """解析路由日志，返回选题列表。

    识别 `### <序号>. <标题>` 分块，按所在的 `## ` 区判定优先级：
      - `## ⭐ 高优先级选题` → ⭐
      - `## 普通选题`        → ·
    """
    topics: list[dict] = []
    # 先按 `## ` 大区切分，记录每个区间的优先级标记
    sections = list(re.finditer(r"(?m)^##\s+(.+)$", text))
    region_marks: list[tuple[int, int, str]] = []
    for idx, sec in enumerate(sections):
        start = sec.end()
        end = sections[idx + 1].start() if idx + 1 < len(sections) else len(text)
        heading = sec.group(1)
        if "高优先级" in heading:
            mark = "⭐"
        elif "普通" in heading:
            mark = "·"
        else:
            mark = ""  # 更新 / 观点信号 等区不产选题行
        region_marks.append((start, end, mark))

    for start, end, mark in region_marks:
        if not mark:
            continue
        chunk = text[start:end]
        # `### 01. 标题`
        for m in re.finditer(r"(?m)^###\s+(\d+)[.、]\s*(.+)$", chunk):
            body_start = m.end()
            nxt = re.search(r"(?m)^###\s+\d+[.、]", chunk[body_start:])
            body = chunk[body_start : body_start + nxt.start()] if nxt else chunk[body_start:]
            title = _strip_md(m.group(2)).strip()
            if not title:
                continue
            angle = _field(body, "选题角度", "角度")
            hook = _field(body, "钩子") or _hook_from_angle(angle)
            topics.append(
                {
                    "mark": mark,
                    "seq": m.group(1),
                    "title": title,
                    "hook": _cell(hook),
                    "angle": _cell(angle, 200),
                    "sources": _field(body, "来源"),
                    "anchor": _field(body, "锚点"),
                    "framework": _cell(_field(body, "框架"), 200),
                    "spread": _field(body, "传播"),
                    "merge_hint": _field(body, "merge_hint"),
                    "viewpoint": _field(body, "观点信号"),
                    "series": _series_from_title(title),
                }
            )
    return topics


def to_pool_row(topic: dict) -> str:
    """转成选题池表格行（| 选题 | 钩子 | 角度 | 系列 |）。

    钩子列刻意压短（表格要能一眼扫完）；路由日志里没有独立「钩子」字段，
    钩子是取「选题角度」的首句，所以不压缩就等于把角度抄一遍。
    """
    return (
        f"| {topic['mark']} {_cell(topic['title'], 90)} "
        f"| {_cell(topic['hook'], 60)} "
        f"| {topic['angle']} "
        f"| {topic['series']} |"
    )


def to_preview(topics: list[dict], date_str: str) -> str:
    """人读预览。"""
    out = [f"# 选题池提取预览 · {date_str}", f"共 {len(topics)} 条", ""]
    for t in topics:
        out.append(f"## {t['mark']} {t['seq']}. {t['title']}")
        out.append(f"- 钩子: {t['hook']}")
        out.append(f"- 角度: {t['angle']}")
        if t["sources"]:
            out.append(f"- 来源: {_cell(t['sources'], 300)}")
        if t["anchor"]:
            out.append(f"- 锚点: {t['anchor']}")
        if t["spread"]:
            out.append(f"- 传播: {t['spread']}")
        if t["merge_hint"]:
            out.append(f"- merge: {_cell(t['merge_hint'], 300)}")
        if t["viewpoint"]:
            out.append(f"- 观点信号: {_cell(t['viewpoint'], 300)}")
        out.append("")
    return "\n".join(out)


def to_digest_section(topics: list[dict]) -> str:
    """给「每日精选」用的选题段。"""
    out = ["## ✍️ 今天可写（按传播分排序）", ""]
    for t in topics:
        out.append(f"### {t['mark']} {t['title']}")
        out.append(f"- 钩子：{t['hook']}")
        out.append(f"- 怎么切：{t['angle']}")
        if t["framework"]:
            out.append(f"- 可用框架：{t['framework']}")
        if t["sources"]:
            out.append(f"- 信号来源：{_cell(t['sources'], 300)}")
        out.append("")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="从路由日志确定性提取选题池行")
    ap.add_argument("route_log", help="路由日志路径，如 _路由/2026-09-23.md")
    ap.add_argument(
        "--format",
        choices=["rows", "preview", "digest", "json"],
        default="rows",
        help="输出格式（默认 rows，直接可粘进选题池表格）",
    )
    args = ap.parse_args(argv)

    path = Path(args.route_log)
    if not path.is_file():
        print(f"ERROR: 路由日志不存在: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    date_str = path.stem
    topics = parse_route_log(text)

    if not topics:
        # 明确失败，不静默跳过（旧逻辑的静默 = 6 周无人发现）
        print(f"ERROR: 未能从 {path} 解析出任何选题 —— 路由日志可能被截断", file=sys.stderr)
        return 2

    if args.format == "rows":
        print("\n".join(to_pool_row(t) for t in topics))
    elif args.format == "preview":
        print(to_preview(topics, date_str))
    elif args.format == "digest":
        print(to_digest_section(topics))
    else:
        print(json.dumps(topics, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
