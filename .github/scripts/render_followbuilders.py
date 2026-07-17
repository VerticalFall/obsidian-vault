#!/usr/bin/env python3
"""从 follow-builders 公共 feed 拉取 AI builder 动态，渲染成 Markdown。

数据源: https://github.com/zarazhangrui/follow-builders
理念: "Follow Builders, Not Influencers" — 追踪真正在造东西的 AI 研究者/创始人/PM/工程师

三个 feed 文件:
  - feed-x.json: 26 位 AI builder 的 X 推文
  - feed-blogs.json: Anthropic Engineering + Claude Blog 官方博客
  - feed-podcasts.json: 6 档 AI 播客转录

所有内容通过 GitHub raw URL 公开访问，无需 API Key。

环境变量:
  DEEPSEEK_API_KEY  — 用于播客转录摘要（可选，不设则跳过摘要）
  TODAY_OVERRIDE    — 手动指定日期 (YYYY-MM-DD，不设则用北京时间当天)
  FB_OUT_DIR        — 输出目录（默认 "FollowBuilders"）
"""

import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta

# ── 配置 ────────────────────────────────────────────────────────
FEED_BASE = "https://raw.githubusercontent.com/zarazhangrui/follow-builders/main"
FEEDS = {
    "x": f"{FEED_BASE}/feed-x.json",
    "blogs": f"{FEED_BASE}/feed-blogs.json",
    "podcasts": f"{FEED_BASE}/feed-podcasts.json",
}
OUT_DIR = os.environ.get("FB_OUT_DIR", "FollowBuilders")
BEIJING = timezone(timedelta(hours=8))

# DeepSeek 配置（复用现有 env）
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_API_BASE = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_FLASH_MODEL = "deepseek-v4-flash"


# ── helpers ────────────────────────────────────────────────────

def today_beijing() -> str:
    override = os.environ.get("TODAY_OVERRIDE", "").strip()
    if override:
        return override
    return datetime.now(BEIJING).strftime("%Y-%m-%d")


def fetch_json(url: str) -> dict | None:
    """拉取 JSON feed，失败返回 None。"""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "obsidian-vault-sync/1.0"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"WARNING: 拉取 {url} 失败: {e}", file=sys.stderr)
        return None


def format_time(iso_str: str) -> str:
    """ISO → 北京时间 HH:MM。"""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        dt_bj = dt.astimezone(BEIJING)
        return dt_bj.strftime("%H:%M")
    except Exception:
        return iso_str


def clean_html(text: str) -> str:
    """去掉 HTML 标签，保留纯文本。"""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&#x27;", "'", text)
    text = re.sub(r"&(?:amp|lt|gt|quot|nbsp);", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def truncate_text(text: str, max_chars: int = 500) -> str:
    """截断文本到 max_chars，尽量在句子边界截断。"""
    text = text.strip()
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    # 回退到最后一个句号/换行
    for sep in ["\n", ". ", "。", "! ", "? "]:
        idx = truncated.rfind(sep)
        if idx > max_chars * 0.5:
            truncated = truncated[:idx + len(sep.rstrip())]
            break
    return truncated.strip() + " ..."


# ── DeepSeek Flash 翻译 ────────────────────────────────────────

def contains_chinese(text: str) -> bool:
    """判断文本是否含中文。"""
    return bool(re.search(r'[一-鿿]', text))


def translate_to_chinese(text: str) -> str | None:
    """用 DeepSeek V4 Flash 将英文翻译为中文。失败返回 None。

    使用 flash 模型——更便宜更快，适合批量推文翻译（~38 条/天）。
    系统提示适配 AI 产业内容，保留技术术语。
    """
    if not DEEPSEEK_API_KEY:
        return None
    try:
        body = json.dumps({
            "model": DEEPSEEK_FLASH_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是AI行业翻译助手。将英文精确翻译为简体中文。"
                        "保留技术术语不翻译（如 API、GPU、prompt、fine-tune、RLHF、agent 等）。"
                        "只输出译文，不要任何解释或前缀。"
                    ),
                },
                {"role": "user", "content": text},
            ],
            "max_tokens": 2000,
            "temperature": 0.1,
        }).encode("utf-8")
        req = urllib.request.Request(
            DEEPSEEK_API_BASE,
            data=body,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))
        result = data["choices"][0]["message"]["content"]
        if not result or not result.strip():
            return None
        return result.strip()
    except Exception as e:
        print(f"      翻译失败: {e}", file=sys.stderr)
        return None


def translate_text(text: str) -> str | None:
    """翻译一条推文。只翻译不含中文、≥30 字的英文文本。"""
    text = text.strip()
    if not text:
        return None
    if contains_chinese(text):
        return None
    if len(text) < 30:
        return None
    # 超长截断
    if len(text) > 500:
        text = text[:500] + "..."
    return translate_to_chinese(text)


# ── DeepSeek 播客摘要 ──────────────────────────────────────────

def summarize_podcast(name: str, title: str, transcript: str) -> str | None:
    """用 DeepSeek 将播客转录总结为 ≤150 字中文摘要。失败返回 None。"""
    if not DEEPSEEK_API_KEY:
        return None
    if not transcript or len(transcript) < 200:
        return None

    # 截断转录到 ~4000 字符，节约 token
    truncated = transcript[:4000]
    try:
        body = json.dumps({
            "model": DEEPSEEK_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是AI行业观察者。用中文（≤150字）总结播客核心观点："
                        "讨论了什么问题？有哪些值得关注的观点或信号？"
                        "只输出摘要，不要解释或前缀。"
                    ),
                },
                {
                    "role": "user",
                    "content": f"播客: {name} — {title}\n\n转录片段:\n{truncated}",
                },
            ],
            "max_tokens": 300,
            "temperature": 0.1,
        }).encode("utf-8")

        req = urllib.request.Request(
            DEEPSEEK_API_BASE,
            data=body,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode("utf-8"))
        result = data["choices"][0]["message"]["content"]
        if result and result.strip():
            return result.strip()
    except Exception as e:
        print(f"      播客摘要失败: {e}", file=sys.stderr)
    return None


# ── 各区块渲染 ──────────────────────────────────────────────────

def render_x(data: dict) -> tuple[str, int, int, int, int]:
    """渲染 X 推文区块。返回 (markdown, builder_count, tweet_count, translated, failed)。"""
    builders = data.get("x") or []
    if not builders:
        return "", 0, 0, 0, 0

    out = ["## 🐦 X 动态", ""]
    total_tweets = 0
    builder_count = 0
    translated = 0
    failed = 0

    for b in builders:
        tweets = b.get("tweets") or []
        if not tweets:
            continue
        builder_count += 1
        name = b.get("name", "")
        handle = b.get("handle", "")
        bio = b.get("bio", "")

        out.append(f"### @{handle} — {name}")
        if bio:
            out.append(f"*{bio}*")
        out.append("")

        for tw in tweets:
            total_tweets += 1
            text = (tw.get("text") or "").strip()
            tw_id = tw.get("id", "")
            created = tw.get("createdAt", "")
            url = tw.get("url", "")
            likes = tw.get("likes", 0)
            retweets = tw.get("retweets", 0)
            replies = tw.get("replies", 0)
            is_quote = tw.get("isQuote", False)

            # 引用推文标记
            prefix = "💬 引用: " if is_quote else ""

            # 推文正文（引用块格式）
            for line in text.split("\n"):
                out.append(f"> {prefix}{line}")
                prefix = ""  # 仅第一行加前缀

            # 翻译（Flash 模型，≥30 字符英文推文）
            need_translation = not contains_chinese(text) and len(text) >= 30
            if need_translation:
                translation = translate_text(text)
                if translation:
                    out.append(f"> 🇨🇳 {translation}")
                    translated += 1
                else:
                    out.append("> 🇨🇳 [翻译失败]")
                    failed += 1
                time.sleep(0.2)  # Flash API 限流保护

            # 元数据行
            meta_parts = [f"🕐 {format_time(created)}"]
            if retweets:
                meta_parts.append(f"🔁 {retweets}")
            if likes:
                meta_parts.append(f"❤️ {likes}")
            if replies:
                meta_parts.append(f"💬 {replies}")
            meta_parts.append(f"[原文]({url})" if url else "无链接")
            out.append(" · ".join(meta_parts))
            out.append("")

    return "\n".join(out), builder_count, total_tweets, translated, failed


def render_blogs(data: dict) -> tuple[str, int]:
    """渲染官方博客区块。返回 (markdown, post_count)。"""
    posts = data.get("blogs") or []
    if not posts:
        return "", 0

    out = ["## 📝 官方博客", ""]
    for post in posts:
        title = (post.get("title") or "无标题").strip()
        url = (post.get("url") or "").strip()
        name = (post.get("name") or "").strip()
        content = (post.get("content") or "").strip()
        published = (post.get("publishedAt") or "").strip()

        title_line = f"### [{title}]({url})" if url else f"### {title}"
        out.append(title_line)
        meta = []
        if name:
            meta.append(name)
        if published:
            meta.append(published[:10])
        if meta:
            out.append(f"*{' · '.join(meta)}*")
        out.append("")

        if content:
            excerpt = truncate_text(clean_html(content), 500)
            if excerpt:
                out.append(f"> {excerpt}")
                out.append("")

    return "\n".join(out), len(posts)


def render_podcasts(data: dict) -> tuple[str, int, int]:
    """渲染播客区块。返回 (markdown, episode_count, summarized_count)。"""
    episodes = data.get("podcasts") or []
    errors = data.get("errors") or []
    if not episodes and not errors:
        return "", 0, 0

    out = ["## 🎙️ 播客", ""]

    summarized = 0
    for ep in episodes:
        name = (ep.get("name") or "").strip()
        title = (ep.get("title") or "无标题").strip()
        url = (ep.get("url") or "").strip()
        published = (ep.get("publishedAt") or "").strip()
        transcript = (ep.get("transcript") or "").strip()

        title_line = f"### [{title}]({url})" if url else f"### {title}"
        out.append(title_line)
        meta = []
        if name:
            meta.append(name)
        if published:
            meta.append(published[:10])
        if meta:
            out.append(f"*{' · '.join(meta)}*")
        out.append("")

        # 生成中文摘要
        if transcript:
            summary = summarize_podcast(name, title, transcript)
            if summary:
                out.append(f"> 📌 {summary}")
                out.append("")
                summarized += 1

        time.sleep(0.3)  # 避免 API 限流

    # 报错日志
    for err in errors:
        out.append(f"> ⚠️ 抓取异常: {err}")
        out.append("")

    return "\n".join(out), len(episodes), summarized


# ── 主渲染 ──────────────────────────────────────────────────────

def render(date_str: str,
           x_data: dict | None,
           blogs_data: dict | None,
           podcasts_data: dict | None) -> str:
    """组装完整 Markdown。"""
    out = []
    out.append("---")
    out.append(f"date: {date_str}")
    out.append("source: Follow Builders")
    out.append("type: daily-report")
    out.append("tags: [AI, builders, X, 播客, 博客]")
    out.append("---")
    out.append("")
    out.append(f"# 🤖 AI Builders 动态 · {date_str}")
    out.append("")

    # ── X 推文 ──
    x_md, n_builders, n_tweets, n_translated, n_failed = "", 0, 0, 0, 0
    if x_data:
        x_md, n_builders, n_tweets, n_translated, n_failed = render_x(x_data)

    # ── 博客 ──
    blogs_md, n_posts = "", 0
    if blogs_data:
        blogs_md, n_posts = render_blogs(blogs_data)

    # ── 播客 ──
    podcasts_md, n_eps, n_summarized = "", 0, 0
    if podcasts_data:
        podcasts_md, n_eps, n_summarized = render_podcasts(podcasts_data)

    # ── 摘要行 ──
    summary_parts = []
    if n_builders:
        summary_parts.append(f"{n_builders} 位 builder")
    if n_tweets:
        summary_parts.append(f"{n_tweets} 条推文")
    if n_posts:
        summary_parts.append(f"{n_posts} 篇博客")
    if n_eps:
        eps_str = f"{n_eps} 期播客"
        if n_summarized:
            eps_str += f"({n_summarized} 期已摘要)"
        summary_parts.append(eps_str)

    if summary_parts:
        out.append(f"> {' · '.join(summary_parts)}")
        out.append("")
    else:
        out.append("> 今日无内容")
        out.append("")

    # ── 组装区块 ──
    if x_md:
        out.append(x_md)
        out.append("")

    if blogs_md:
        if x_md:
            out.append("---")
            out.append("")
        out.append(blogs_md)
        out.append("")

    if podcasts_md:
        if x_md or blogs_md:
            out.append("---")
            out.append("")
        out.append(podcasts_md)
        out.append("")

    # ── 尾部 ──
    out.append("---")
    footer_parts = ["*数据来源: [follow-builders](https://github.com/zarazhangrui/follow-builders)"]
    if n_translated:
        footer_parts.append("翻译由 DeepSeek V4 Flash 提供")
    if n_summarized:
        footer_parts.append("播客摘要由 DeepSeek 提供")
    footer = " · ".join(footer_parts) + "*"
    out.append(footer)
    out.append("")

    return "\n".join(out)


# ── main ────────────────────────────────────────────────────────

def main():
    date_str = today_beijing()
    print(f"FollowBuilders 渲染 · {date_str}")

    # 并行拉取三个 feed
    print("拉取 feeds …")
    x_data = fetch_json(FEEDS["x"])
    blogs_data = fetch_json(FEEDS["blogs"])
    podcasts_data = fetch_json(FEEDS["podcasts"])

    if not x_data and not blogs_data and not podcasts_data:
        print("WARNING: 三个 feed 全部拉取失败，今日无 FollowBuilders 数据")
        return 0

    # 打印数据摘要
    for label, data in [("X", x_data), ("Blogs", blogs_data), ("Podcasts", podcasts_data)]:
        if not data:
            print(f"  {label}: 拉取失败或无数据")
            continue
        stats = data.get("stats", {})
        if stats:
            print(f"  {label}: {json.dumps(stats)}")
        else:
            # 手动统计
            items = data.get("x") or data.get("blogs") or data.get("podcasts") or []
            print(f"  {label}: {len(items)} 条")

    # 渲染
    md = render(date_str, x_data, blogs_data, podcasts_data)

    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{date_str}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"OK: 写入 {path} ({len(md)} 字符)")

    # 翻译统计
    x_stats = (x_data or {}).get("stats", {})
    total_tweets = x_stats.get("totalTweets", 0)
    if total_tweets:
        # render() 内部已统计，这里打一行汇总
        print(f"  翻译: DeepSeek V4 Flash")
    return 0


if __name__ == "__main__":
    sys.exit(main())
