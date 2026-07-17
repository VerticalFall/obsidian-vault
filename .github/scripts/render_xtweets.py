#!/usr/bin/env python3
"""从 SocialData.tools API 拉取指定 X 博主的当日推文,翻译+渲染成 Markdown。

API: https://api.socialdata.tools
翻译: translate 库(Google Translate 免费后端)
博主列表从 X-Tweets/following.json 读取。
输出: X-Tweets/YYYY-MM-DD.md

环境变量:
  SOCIALDATA_API_KEY — API Key(必需)
  XTWEETS_OUT_DIR    — 输出目录(默认 "X-Tweets")
  TODAY_OVERRIDE     — 手动指定日期(YYYY-MM-DD,用于补抓历史,不设则用北京时间当天)
"""

import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta

API_BASE = "https://api.socialdata.tools/twitter"
OUT_DIR = os.environ.get("XTWEETS_OUT_DIR", "X-Tweets")
FOLLOWING_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "X-Tweets", "following.json"
)

# ── helpers ────────────────────────────────────────────────────

BEIJING = timezone(timedelta(hours=8))


def today_beijing() -> str:
    override = os.environ.get("TODAY_OVERRIDE", "").strip()
    if override:
        return override
    return datetime.now(BEIJING).strftime("%Y-%m-%d")


def today_start_utc(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    dt_beijing = dt.replace(tzinfo=BEIJING)
    return dt_beijing.isoformat()


def api_get(path: str) -> dict:
    api_key = os.environ.get("SOCIALDATA_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("SOCIALDATA_API_KEY 环境变量未设置")
    url = f"{API_BASE}/{path.lstrip('/')}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def load_following() -> list[str]:
    if not os.path.exists(FOLLOWING_FILE):
        print(f"WARNING: {FOLLOWING_FILE} 不存在,返回空列表")
        return []
    with open(FOLLOWING_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("users", [])


def resolve_user(screen_name: str) -> dict | None:
    try:
        profile = api_get(f"user/{screen_name}")
        return {
            "id_str": profile.get("id_str", ""),
            "screen_name": profile.get("screen_name", screen_name),
            "name": profile.get("name", screen_name),
        }
    except Exception as e:
        print(f"WARNING: 查用户 {screen_name} 失败: {e}", file=sys.stderr)
        return None


def fetch_tweets(user_id: str, since_utc: str) -> list[dict]:
    """拉取用户推文，翻页直到推文时间早于 since_utc。
    注意：API 可能返回乱序推文（如置顶推文在最前），所以不能看到一条旧的就提前 return，
    而是遍历整页后再判断是否继续翻页。
    """
    all_tweets = []
    cursor = None
    page = 0

    while True:
        page += 1
        path = f"user/{user_id}/tweets"
        if cursor:
            path += f"?cursor={urllib.request.quote(cursor)}"

        try:
            data = api_get(path)
        except Exception as e:
            print(f"WARNING: 拉取推文第{page}页失败: {e}", file=sys.stderr)
            break

        tweets = data.get("tweets") or []
        if not tweets:
            break

        # 遍历整页：收集今天的，记录最早时间
        saw_old = False
        oldest_in_page = None
        for tw in tweets:
            created = tw.get("tweet_created_at", "")
            if not oldest_in_page or created < oldest_in_page:
                oldest_in_page = created
            if created >= since_utc:
                all_tweets.append(tw)
            else:
                saw_old = True

        # 当前页最早推文 < since，后面的页也不会有今天的了
        if saw_old and oldest_in_page and oldest_in_page < since_utc:
            break

        cursor = data.get("next_cursor")
        if not cursor:
            break

        time.sleep(0.3)

    return all_tweets


def tweet_url(screen_name: str, tweet_id: str) -> str:
    return f"https://x.com/{screen_name}/status/{tweet_id}"


def format_time(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        dt_bj = dt.astimezone(BEIJING)
        return dt_bj.strftime("%H:%M")
    except Exception:
        return iso_str


# ── 翻译 ────────────────────────────────────────────────────────

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_API_BASE = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_TRANSLATE_MODEL = "deepseek-chat"

def contains_chinese(text: str) -> bool:
    """判断文本是否含中文。"""
    return bool(re.search(r'[一-鿿]', text))


def translate_to_chinese(text: str) -> str | None:
    """用 DeepSeek API 将英文翻译为中文。失败返回 None。

    换用 DeepSeek 替代 translate 库(Google Translate 免费后端)，
    因为 GitHub Actions 出口 IP 被 Google 频繁限流导致翻译静默失效。
    DeepSeek 翻译质量更好(对金融术语理解更深)，增量成本 ~$0.0002/千字符。
    """
    if not DEEPSEEK_API_KEY:
        print("      DEEPSEEK_API_KEY 未设置，跳过翻译", file=sys.stderr)
        return None
    try:
        body = json.dumps({
            "model": DEEPSEEK_TRANSLATE_MODEL,
            "messages": [
                {"role": "system", "content": "你是一个专业金融翻译。将英文精确翻译为简体中文。保持专业术语准确(如 DRAM→DRAM、HBM→HBM 不翻译)。只输出译文，不要加任何解释或括号说明。"},
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
            print("      翻译返回空内容", file=sys.stderr)
            return None
        return result.strip()
    except Exception as e:
        print(f"      翻译失败: {e}", file=sys.stderr)
        return None


def translate_text(text: str) -> str | None:
    """翻译一条推文。只翻译不含中文的文本。字数 < 30 跳过（太短没价值）。"""
    text = text.strip()
    if not text:
        return None
    if contains_chinese(text):
        return None
    if len(text) < 30:
        return None
    # 超长文本截断翻译（> 500 字符先截）
    if len(text) > 500:
        text = text[:500] + "..."
    return translate_to_chinese(text)


def clean_tweet_text(tw: dict) -> str:
    """提取纯文本,去掉 t.co 短链接。"""
    text = (tw.get("full_text") or tw.get("text") or "").strip()
    # 去掉末尾所有 t.co 短链接
    text = re.sub(r'https://t\.co/\S+', '', text).strip()
    return text


# ── render ──────────────────────────────────────────────────────

def render(date_str: str, tweets_by_user: list[tuple[dict, list[dict]]]) -> str:
    out = []
    out.append("---")
    out.append(f"date: {date_str}")
    out.append("source: X Tweets (SocialData.tools)")
    out.append("type: daily-report")
    out.append("tags: [X, 推特, 博主动态]")
    out.append("---")
    out.append("")
    out.append(f"# 🐦 X 博主动态 · {date_str}")
    out.append("")

    total = sum(len(tweets) for _, tweets in tweets_by_user)
    out.append(f"> {len(tweets_by_user)} 位博主 · {total} 条推文")
    out.append("")

    for user, tweets in tweets_by_user:
        name = user.get("name", "")
        screen_name = user.get("screen_name", "")
        out.append(f"## @{screen_name}")
        if name and name != screen_name:
            out.append(f"*{name}*")
        out.append("")

        for tw in tweets:
            text = clean_tweet_text(tw)
            tw_id = tw.get("id_str", "")
            created = tw.get("tweet_created_at", "")
            reply_to = tw.get("in_reply_to_screen_name", "")

            prefix = ""
            if reply_to:
                prefix = f"↩ 回复 @{reply_to}: "

            # 是否需要翻译
            need_translation = not contains_chinese(text) and len(text) >= 30

            # 原文
            out.append(f"> {prefix}{text}")

            # 翻译
            if need_translation:
                translation = translate_text(text)
                if translation:
                    out.append(f"> 🇨🇳 {translation}")
                else:
                    out.append(f"> 🇨🇳 [翻译失败]")

            # 数据行
            out.append(
                f"🕐 {format_time(created)} · "
                f"🔁 {tw.get('retweet_count', 0)} · "
                f"❤️ {tw.get('favorite_count', 0)} · "
                f"👁 {tw.get('views_count', 0)} · "
                f"[原文]({tweet_url(screen_name, tw_id)})"
            )
            out.append("")

    out.append("---")
    out.append("*数据来源:[SocialData.tools](https://socialdata.tools) · 翻译由 Google Translate 提供*")
    out.append("")
    return "\n".join(out)


# ── main ────────────────────────────────────────────────────────

def main():
    date_str = today_beijing()
    since_utc = today_start_utc(date_str)
    print(f"目标日期(北京): {date_str}  →  UTC since: {since_utc}")

    screen_names = load_following()
    if not screen_names:
        print("WARNING: 无待追踪博主,退出")
        return 1

    print(f"追踪 {len(screen_names)} 位博主: {', '.join(screen_names)}")

    tweets_by_user = []
    for sn in screen_names:
        user = resolve_user(sn)
        if not user:
            continue
        uid = user["id_str"]
        print(f"  @{sn} (id={uid}) …", end=" ")
        tweets = fetch_tweets(uid, since_utc)
        to_translate = sum(1 for t in tweets if not contains_chinese(clean_tweet_text(t)) and len(clean_tweet_text(t)) >= 30)
        print(f"{len(tweets)} 条今天 (需翻译 {to_translate} 条)")

        tweets_by_user.append((user, tweets))

    if not tweets_by_user:
        print("今日无推文,不生成文件")
        return 0

    md = render(date_str, tweets_by_user)

    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{date_str}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"OK: 写入 {path} ({len(md)} 字符)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
