#!/usr/bin/env python3
"""从 TrendRadar 成品报告 daily.html 渲染每日热点 Markdown。

复刻 TrendRadar 网页版「复制 Markdown」的逻辑,产出与推送飞书同源的内容:
  - ✨ AI 热点分析(DeepSeek 深度分析)
  - 📊 按话题分组的热榜(话题 → 各平台条目,含来源/排名/时间/可点击链接)
  - 📰 RSS 订阅更新

用法: python render_trendradar.py <date> <daily_html_path> [out_dir] [db_path]
  - daily_html_path: 必需,TrendRadar 的 output/html/latest/daily.html
  - db_path: 可选,daily.html 不可用时退化为按平台渲染热榜

纯标准库实现(re + html),无需 pip 依赖。
"""
import html
import os
import re
import sys


# ---------- 通用工具 ----------

def _text(fragment):
    """HTML 片段 → 纯文本(<br> 转换行,去标签,反转义)。"""
    if not fragment:
        return ""
    s = re.sub(r"<br\s*/?>", "\n", fragment, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).strip()


def _find_section(src, cls):
    """返回含 class=cls 的 section-divider 起始位置(找不到返回 -1)。"""
    m = re.search(r'<div class="[^"]*\b' + re.escape(cls) + r'\b[^"]*"', src)
    return m.start() if m else -1


def _parse_news_items(chunk):
    """从一段 HTML 里解析所有 news-item / new-item,返回 [{title,url,source,rank,time}]。"""
    items = []
    pieces = re.split(r'<div class="(?:news-item|new-item)\b', chunk)[1:]
    for p in pieces:
        m_title = re.search(r'class="(?:news-title|new-item-title)"[^>]*>\s*(?:<a href="([^"]*)"[^>]*>)?(.*?)(?:</a>)?\s*</div>', p, re.S)
        if not m_title:
            continue
        url = (m_title.group(1) or "").strip()
        title = _text(m_title.group(2))
        if not title:
            continue
        src_m = re.search(r'class="source-name">(.*?)</span>', p, re.S)
        rank_m = re.search(r'class="(?:rank-num|new-item-rank)[^"]*">(.*?)</span>', p, re.S)
        time_m = re.search(r'class="time-info">(.*?)</span>', p, re.S)
        items.append({
            "title": title,
            "url": url,
            "source": _text(src_m.group(1)) if src_m else "",
            "rank": _text(rank_m.group(1)) if rank_m else "",
            "time": _text(time_m.group(1)) if time_m else "",
        })
    return items


def _item_line(i, it):
    if it["url"]:
        line = f"{i}. [{it['title']}]({it['url']})"
    else:
        line = f"{i}. {it['title']}"
    meta = []
    if it["source"]:
        meta.append(it["source"])
    if it["rank"] and it["rank"] != "?":
        meta.append(f"#{it['rank']}")
    if it["time"]:
        meta.append(it["time"])
    if meta:
        line += "  `" + " · ".join(meta) + "`"
    return line


# ---------- 各区块渲染 ----------

def render_ai(src):
    start = _find_section(src, "ai-section")
    if start == -1:
        return "", 0
    seg = src[start:]
    m = re.search(r'ai-section-title">(.*?)</div>', seg, re.S)
    title = _text(m.group(1)) if m else "AI 热点分析"
    blocks = re.findall(
        r'<div class="ai-block-title">(.*?)</div>\s*<div class="ai-block-content">(.*?)</div>',
        seg, re.S,
    )
    if not blocks:
        return "", 0
    out = [f"## {title}", "", "> 🤖 由 DeepSeek 对当日全网热点自动分析生成(与推送飞书为同一份)", ""]
    for bt, bc in blocks:
        out.append(f"### {_text(bt)}")
        out.append("")
        # 折叠块内多余空行,避免"松散列表"被 Obsidian 自动整理成紧凑列表(否则本地会出现改动、卡住 pull)
        out.append(re.sub(r"\n{2,}", "\n", _text(bc)))
        out.append("")
    return "\n".join(out), len(blocks)


def render_hotlist(src):
    start = _find_section(src, "hotlist-section")
    if start == -1:
        return "", []
    end = src.find('<div class="section-divider', start + 10)
    seg = src[start: end if end != -1 else len(src)]
    groups = re.split(r'<div class="word-group"', seg)[1:]
    parsed = []
    for g in groups:
        name_m = re.search(r'class="word-name">(.*?)</div>', g, re.S)
        cnt_m = re.search(r'class="word-count[^"]*">(.*?)</div>', g, re.S)
        if not name_m:
            continue
        parsed.append({
            "name": _text(name_m.group(1)),
            "count": _text(cnt_m.group(1)) if cnt_m else "",
            "items": _parse_news_items(g),
        })
    if not parsed:
        return "", []
    out = ["## 📊 热点话题", ""]
    for grp in parsed:
        head = f"### 🔥 {grp['name']}"
        if grp["count"]:
            head += f"（{grp['count']}）"
        out.append(head)
        out.append("")
        for i, it in enumerate(grp["items"], 1):
            out.append(_item_line(i, it))
        out.append("")
    return "\n".join(out), parsed


def render_rss(src):
    start = _find_section(src, "rss-section")
    if start == -1:
        return ""
    end = src.find('<div class="section-divider', start + 10)
    seg = src[start: end if end != -1 else len(src)]
    feeds = re.split(r'<div class="feed-group"', seg)[1:]
    out = ["## 📰 RSS 订阅更新", ""]
    found = False
    for f in feeds:
        name_m = re.search(r'class="feed-name">(.*?)</div>', f, re.S)
        cnt_m = re.search(r'class="feed-count[^"]*">(.*?)</div>', f, re.S)
        if not name_m:
            continue
        head = f"### {_text(name_m.group(1))}"
        if cnt_m:
            head += f"（{_text(cnt_m.group(1))}）"
        out.append(head)
        out.append("")
        rss_items = re.split(r'<div class="rss-item\b', f)[1:]
        for i, p in enumerate(rss_items, 1):
            tm = re.search(r'class="rss-title"[^>]*>\s*(?:<a href="([^"]*)"[^>]*>)?(.*?)(?:</a>)?\s*</div>', p, re.S)
            if not tm:
                continue
            title = _text(tm.group(2))
            if not title:
                continue
            url = (tm.group(1) or "").strip()
            meta = []
            am = re.search(r'class="rss-author">(.*?)</span>', p, re.S)
            tim = re.search(r'class="rss-time">(.*?)</span>', p, re.S)
            if am:
                meta.append(_text(am.group(1)))
            if tim:
                meta.append(_text(tim.group(1)))
            line = f"{i}. [{title}]({url})" if url else f"{i}. {title}"
            if meta:
                line += "  `" + " · ".join(meta) + "`"
            out.append(line)
            found = True
        out.append("")
    return "\n".join(out) if found else ""


def render_from_db(db_path):
    """daily.html 不可用时的退化方案:按平台渲染热榜。"""
    import sqlite3
    from collections import OrderedDict
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        """SELECT p.name AS platform, ni.title AS title, ni.url AS url, MIN(rh.rank) AS best_rank
           FROM news_items ni JOIN platforms p ON p.id = ni.platform_id
           LEFT JOIN rank_history rh ON rh.news_item_id = ni.id
           GROUP BY ni.id ORDER BY p.name, best_rank""").fetchall()
    con.close()
    groups = OrderedDict()
    for r in rows:
        groups.setdefault(r["platform"], []).append(r)
    out = ["## 📋 热榜全览(按平台)", ""]
    for plat, items in groups.items():
        out.append(f"### {plat}")
        out.append("")
        for i, r in enumerate(items[:20], 1):
            t = (r["title"] or "").strip().replace("\n", " ")
            out.append(f"{i}. [{t}]({r['url']})" + (f"  `#{r['best_rank']}`" if r["best_rank"] else ""))
        out.append("")
    return "\n".join(out)


def main():
    if len(sys.argv) < 3:
        print("用法: python render_trendradar.py <date> <daily_html> [out_dir] [db_path]", file=sys.stderr)
        return 2
    date = sys.argv[1]
    html_path = sys.argv[2]
    out_dir = sys.argv[3] if len(sys.argv) > 3 else "TrendRadar"
    db_path = sys.argv[4] if len(sys.argv) > 4 else ""

    ai_md, n_ai = "", 0
    hot_md, groups = "", []
    src = ""
    if html_path and os.path.exists(html_path):
        try:
            src = open(html_path, encoding="utf-8").read()
        except OSError:
            src = ""
    if src:
        ai_md, n_ai = render_ai(src)
        hot_md, groups = render_hotlist(src)
        rss_md = render_rss(src)
    else:
        rss_md = ""

    if not hot_md and db_path and os.path.exists(db_path):
        hot_md = render_from_db(db_path)

    if not hot_md and not ai_md:
        print("ERROR: daily.html 与 db 均不可用,无法渲染", file=sys.stderr)
        return 1

    # 摘要行
    total_items = sum(len(g["items"]) for g in groups)
    top = sorted(groups, key=lambda g: len(g["items"]), reverse=True)[:3]
    hot_topics = " | ".join(f"{g['name']}({len(g['items'])})" for g in top)

    out = ["---", f"date: {date}", "source: TrendRadar", "type: daily-report",
           "tags: [热点, 日报, trendradar]", "---", "", f"# 📡 TrendRadar 每日热点 · {date}", ""]
    if groups:
        out.append(f"> 共 {total_items} 条热点 · {len(groups)} 个话题" + (f" · 最热:{hot_topics}" if hot_topics else ""))
        out.append("")
    if ai_md:
        out.append(ai_md)
        out.append("---")
        out.append("")
    if hot_md:
        out.append(hot_md)
    if rss_md:
        out.append("---")
        out.append("")
        out.append(rss_md)
    out.append("---")
    out.append("*数据来源:[TrendRadar](https://github.com/VerticalFall/TrendRadar) · AI 分析由 DeepSeek 生成*")
    out.append("")
    md = "\n".join(out)

    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{date}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"OK: 写入 {path}({len(md)} 字符,话题 {len(groups)}、AI块 {n_ai})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
