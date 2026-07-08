#!/usr/bin/env python3
"""从 SocialData.tools API 拉取指定 X 博主的当日推文,渲染成 Markdown。

API: https://api.socialdata.tools
纯标准库实现(urllib + json),无需 pip 安装。
博主列表从 X-Tweets/following.json 读取。
输出: X-Tweets/YYYY-MM-DD.md

环境变量:
  SOCIALDATA_API_KEY — API Key(必需)
  XTWEETS_OUT_DIR    — 输出目录(默认 "X-Tweets")
  TODAY_OVERRIDE     — 手动指定日期(YYYY-MM-DD,用于补抓历史,不设则用北京时间当天)
"""

import json
import os
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
    """返回北京时间今天的 YYYY-MM-DD,或环境变量 TODAY_OVERRIDE 指定的日期。"""
    override = os.environ.get("TODAY_OVERRIDE", "").strip()
    if override:
        return override
    return datetime.now(BEIJING).strftime("%Y-%m-%d")


def today_start_utc(date_str: str) -> str:
    """给定北京时间 YYYY-MM-DD,返回当天 00:00 对应的 UTC ISO 8601。
    例如 date_str="2026-07-08" → "2026-07-07T16:00:00Z"
    """
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    dt_beijing = dt.replace(tzinfo=BEIJING)
    return dt_beijing.isoformat()


def api_get(path: str) -> dict:
    """调 SocialData.tools API,返回 JSON。"""
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
    """读取 following.json,返回 screen_name 列表。"""
    if not os.path.exists(FOLLOWING_FILE):
        print(f"WARNING: {FOLLOWING_FILE} 不存在,返回空列表")
        return []
    with open(FOLLOWING_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("users", [])


def resolve_user(screen_name: str) -> dict | None:
    """通过 screen_name 查用户信息,返回 {id_str, screen_name, name}。"""
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
    """拉取用户推文,翻页直到推文时间早于 since_utc。"""
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

        # 筛选北京时间今天的推文
        for tw in tweets:
            created = tw.get("tweet_created_at", "")
            if created >= since_utc:
                all_tweets.append(tw)
            else:
                # 已进入昨天,停止收集
                return all_tweets

        cursor = data.get("next_cursor")
        if not cursor:
            break

        time.sleep(0.3)  # 友好间隔

    return all_tweets


def tweet_url(screen_name: str, tweet_id: str) -> str:
    return f"https://x.com/{screen_name}/status/{tweet_id}"


def format_time(iso_str: str) -> str:
    """UTC ISO 8601 → 北京时间 HH:MM。"""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        dt_bj = dt.astimezone(BEIJING)
        return dt_bj.strftime("%H:%M")
    except Exception:
        return iso_str


# ── render ──────────────────────────────────────────────────────

def render(date_str: str, tweets_by_user: list[tuple[dict, list[dict]]]) -> str:
    """渲染为 Obsidian 友好的 Markdown。"""
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
            # 跳过纯转推(无自己文字)
            text = (tw.get("full_text") or tw.get("text") or "").strip()
            tw_id = tw.get("id_str", "")
            created = tw.get("tweet_created_at", "")
            reply_to = tw.get("in_reply_to_screen_name", "")

            # 前缀标记
            prefix = ""
            if reply_to:
                prefix = f"↩ 回复 @{reply_to}: "

            out.append(f"{prefix}{text}")
            out.append(
                f"🕐 {format_time(created)} · "
                f"🔁 {tw.get('retweet_count', 0)} · "
                f"❤️ {tw.get('favorite_count', 0)} · "
                f"👁 {tw.get('views_count', 0)} · "
                f"[查看原文]({tweet_url(screen_name, tw_id)})"
            )
            out.append("")

    out.append("---")
    out.append("*数据来源:[SocialData.tools](https://socialdata.tools)*")
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
        print(f"{len(tweets)} 条今日推文")
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
