#!/usr/bin/env python3
"""从 TrendRadar 渲染每日热点 Markdown(含 AI 分析)。

内容两部分:
  1. AI 热点分析 —— 从 TrendRadar 成品报告 daily.html 的 .ai-section 提取
     (即 DeepSeek 对当日全网热点的深度分析,与推送到飞书的是同一份)
  2. 热榜全览 —— 从当日 SQLite 数据库渲染各平台榜单

用法: python render_trendradar.py <db_path> <date> [out_dir] [daily_html_path]
纯标准库实现(sqlite3 + re),无需 pip 依赖。
"""
import html
import os
import re
import sqlite3
import sys
from collections import OrderedDict

TOP_PER_PLATFORM = int(os.environ.get("TR_TOP_PER_PLATFORM", "20"))


def _strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def extract_ai_analysis(html_path):
    """从 daily.html 提取 AI 分析区,渲染为 markdown。取不到返回空串。"""
    if not html_path or not os.path.exists(html_path):
        return ""
    try:
        src = open(html_path, encoding="utf-8").read()
    except OSError:
        return ""
    if "ai-section-title" not in src:
        return ""

    m = re.search(r'ai-section-title">(.*?)</div>', src, re.S)
    sec_title = _strip_tags(m.group(1)) if m else "AI 热点分析"

    blocks = re.findall(
        r'<div class="ai-block-title">(.*?)</div>\s*'
        r'<div class="ai-block-content">(.*?)</div>',
        src, re.S,
    )
    if not blocks:
        return ""

    out = [f"## {sec_title}", "", "> 🤖 由 DeepSeek 对当日全网热点自动分析生成(与推送到飞书的为同一份)", ""]
    for title, content in blocks:
        t = _strip_tags(title)
        c = re.sub(r"<br\s*/?>", "\n", content, flags=re.I)
        c = _strip_tags(c)
        c = re.sub(r"\n{3,}", "\n\n", c)
        out.append(f"### {t}")
        out.append("")
        out.append(c)
        out.append("")
    return "\n".join(out)


def render_hotlist(db_path):
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    rows = cur.execute(
        """
        SELECT p.name         AS platform,
               ni.title       AS title,
               ni.url         AS url,
               MIN(rh.rank)   AS best_rank,
               ni.crawl_count AS crawl_count
        FROM news_items ni
        JOIN platforms p        ON p.id = ni.platform_id
        LEFT JOIN rank_history rh ON rh.news_item_id = ni.id
        GROUP BY ni.id
        ORDER BY p.name ASC, ni.crawl_count DESC, best_rank ASC
        """
    ).fetchall()
    con.close()

    groups = OrderedDict()
    for r in rows:
        groups.setdefault(r["platform"], []).append(r)

    out = [
        "## 📋 热榜全览",
        "",
        f"> 覆盖 {len(groups)} 个平台,共 {len(rows)} 条热点(每平台按最高排名展示前 {TOP_PER_PLATFORM} 条)。",
        "",
    ]
    for platform, items in groups.items():
        out.append(f"### {platform}")
        out.append("")
        for i, r in enumerate(items[:TOP_PER_PLATFORM], 1):
            title = (r["title"] or "").strip().replace("\n", " ")
            url = (r["url"] or "").strip()
            best = r["best_rank"]
            meta = []
            if r["crawl_count"] and r["crawl_count"] > 1:
                meta.append(f"在榜 {r['crawl_count']} 次")
            if best:
                meta.append(f"最高第 {best} 位")
            suffix = (" · " + " · ".join(meta)) if meta else ""
            if url:
                out.append(f"{i}. [{title}]({url}){suffix}")
            else:
                out.append(f"{i}. {title}{suffix}")
        out.append("")
    return "\n".join(out)


def main():
    if len(sys.argv) < 3:
        print("用法: python render_trendradar.py <db_path> <date> [out_dir] [daily_html]", file=sys.stderr)
        return 2
    db_path = sys.argv[1]
    date = sys.argv[2]
    out_dir = sys.argv[3] if len(sys.argv) > 3 else "TrendRadar"
    html_path = sys.argv[4] if len(sys.argv) > 4 else ""

    if not os.path.exists(db_path):
        print(f"ERROR: 数据库不存在: {db_path}", file=sys.stderr)
        return 1

    ai_md = extract_ai_analysis(html_path)
    hot_md = render_hotlist(db_path)

    out = ["---", f"date: {date}", "source: TrendRadar", "type: daily-report",
           "tags: [热点, 日报, trendradar]", "---", "", f"# 📡 TrendRadar 每日热点 · {date}", ""]
    if ai_md:
        out.append(ai_md)
        out.append("---")
        out.append("")
    out.append(hot_md)
    out.append("---")
    out.append("*数据来源:[TrendRadar](https://github.com/VerticalFall/TrendRadar) · AI 分析由 DeepSeek 生成*")
    out.append("")
    md = "\n".join(out)

    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{date}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    status = "含 AI 分析" if ai_md else "无 AI 分析(未取到 daily.html)"
    print(f"OK: 写入 {path}({len(md)} 字符,{status})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
