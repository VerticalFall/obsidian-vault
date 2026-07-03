#!/usr/bin/env python3
"""从 AI HOT 公开 API 拉取当日日报,渲染成 Obsidian 友好的 Markdown。

API: https://aihot.virxact.com/api/public/daily
纯标准库实现(urllib + json),无需 pip 安装任何依赖。

输出目录可用环境变量 AIHOT_OUT_DIR 覆盖(默认 "AI-HOT")。
文件名用 API 返回的 date 字段,拿不到时回退到环境变量 RUN_DATE。
"""
import json
import os
import sys
import urllib.request

API_URL = "https://aihot.virxact.com/api/public/daily"
LANDING_URL = "https://aihot.virxact.com"
OUT_DIR = os.environ.get("AIHOT_OUT_DIR", "AI-HOT")

SECTION_EMOJI = {
    "模型发布/更新": "🧠",
    "产品发布/更新": "📦",
    "行业动态": "🏭",
    "论文研究": "📄",
    "技巧与观点": "💡",
}


def fetch_daily():
    req = urllib.request.Request(API_URL, headers={"User-Agent": "obsidian-vault-sync/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def render(daily):
    date = daily.get("date") or ""
    out = []
    out.append("---")
    out.append(f"date: {date}")
    out.append("source: AI HOT")
    out.append("type: daily-report")
    out.append("tags: [AI, 日报, ai-hot]")
    out.append("---")
    out.append("")
    out.append(f"# 🔥 AI HOT 日报 · {date}")
    out.append("")

    lead = daily.get("lead") or {}
    if lead.get("leadParagraph"):
        out.append(f"> {lead['leadParagraph']}")
        out.append("")

    idx = 0
    for section in daily.get("sections") or []:
        items = section.get("items") or []
        if not items:
            continue
        label = section.get("label") or ""
        emoji = SECTION_EMOJI.get(label, "🔖")
        out.append(f"## {emoji} {label}")
        out.append("")
        for item in items:
            idx += 1
            title = (item.get("title") or "(无标题)").strip()
            source = (item.get("sourceName") or "").strip()
            summary = (item.get("summary") or "").strip()
            url = (item.get("sourceUrl") or "").strip()
            head = f"{idx}. **{title}**"
            if source:
                head += f" — {source}"
            out.append(head)
            if summary:
                out.append(f"   {summary}")
            if url:
                out.append(f"   [查看原文]({url})")
            out.append("")

    out.append("---")
    out.append(f"*数据来源:[AI HOT]({LANDING_URL})*")
    out.append("")
    return date, "\n".join(out)


def main():
    try:
        daily = fetch_daily()
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: 拉取 AI HOT API 失败: {e}", file=sys.stderr)
        return 1

    date, md = render(daily)
    if not date:
        date = os.environ.get("RUN_DATE", "unknown")

    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{date}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"OK: 写入 {path}({len(md)} 字符)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
