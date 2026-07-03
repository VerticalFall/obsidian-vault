#!/usr/bin/env python3
"""从 TrendRadar 的当日 SQLite 数据库渲染每日热点 Markdown。

用法: python render_trendradar.py <db_path> <date> [out_dir]
纯标准库实现(sqlite3)。

数据库结构(TrendRadar output/news/<date>.db):
  platforms(id, name, ...)                    -- 11 个热榜平台(今日头条/百度热搜…)
  news_items(id, title, platform_id, rank, url, crawl_count, ...)
  rank_history(news_item_id, rank, ...)       -- 每条热点当天的排名变化

渲染逻辑:按平台分组,取每条热点当天的"最高排名"(peak rank)排序,
每个平台展示前 N 条(环境变量 TR_TOP_PER_PLATFORM,默认 20)。
"""
import os
import sqlite3
import sys
from collections import OrderedDict

TOP_PER_PLATFORM = int(os.environ.get("TR_TOP_PER_PLATFORM", "20"))


def render(db_path, date):
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

    out = []
    out.append("---")
    out.append(f"date: {date}")
    out.append("source: TrendRadar")
    out.append("type: daily-report")
    out.append("tags: [热点, 日报, trendradar]")
    out.append("---")
    out.append("")
    out.append(f"# 📡 TrendRadar 每日热点 · {date}")
    out.append("")
    out.append(
        f"> 覆盖 {len(groups)} 个平台,共 {len(rows)} 条热点"
        f"(每平台按最高排名展示前 {TOP_PER_PLATFORM} 条)。"
    )
    out.append("")

    for platform, items in groups.items():
        out.append(f"## {platform}")
        out.append("")
        for i, r in enumerate(items[:TOP_PER_PLATFORM], 1):
            title = (r["title"] or "").strip().replace("\n", " ")
            url = (r["url"] or "").strip()
            best = r["best_rank"]
            meta = []
            if r["crawl_count"]:
                meta.append(f"在榜 {r['crawl_count']} 次")
            if best:
                meta.append(f"最高第 {best} 位")
            suffix = (" · " + " · ".join(meta)) if meta else ""
            if url:
                out.append(f"{i}. [{title}]({url}){suffix}")
            else:
                out.append(f"{i}. {title}{suffix}")
        out.append("")

    out.append("---")
    out.append("*数据来源:[TrendRadar](https://github.com/VerticalFall/TrendRadar)*")
    out.append("")
    return "\n".join(out)


def main():
    if len(sys.argv) < 3:
        print("用法: python render_trendradar.py <db_path> <date> [out_dir]", file=sys.stderr)
        return 2
    db_path = sys.argv[1]
    date = sys.argv[2]
    out_dir = sys.argv[3] if len(sys.argv) > 3 else "TrendRadar"

    if not os.path.exists(db_path):
        print(f"ERROR: 数据库不存在: {db_path}", file=sys.stderr)
        return 1

    md = render(db_path, date)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{date}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"OK: 写入 {path}({len(md)} 字符)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
