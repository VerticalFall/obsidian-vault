#!/usr/bin/env python3
"""L1 系统健康监控 — 每天 Action 采集+路由后自动运行。
纯标准库，零 LLM 调用，零成本。

检查项:
  1. 信息源产出（三源文件存在 + 大小 > 200B）
  2. X-Tweets 有效推文计数
  3. 路由日志产出（文件存在 + > 500 字符）
  4. 选题池存量（🌱待定 + 💤等待 条目数）
  5. 翻译成功率（翻译失败比例）

输出:
  _系统健康/YYYY-MM-DD.md     — 每日健康报告
  _系统健康/_告警摘要.md       — 滚动告警摘要（🔴 和 🟡）
"""

import os
import re
import sys
from datetime import datetime, timezone, timedelta

BEIJING = timezone(timedelta(hours=8))

# ── 配置 ──
AIHOT_DIR = "AI-HOT"
XTWEETS_DIR = "X-Tweets"
TR_DIR = "TrendRadar"
ROUTE_DIR = "_路由"
TOPIC_FILE = "_选题池.md"
HEALTH_DIR = "_系统健康"
ALERT_FILE = os.path.join(HEALTH_DIR, "_告警摘要.md")
TO_VERIFY_FILE = os.path.join(HEALTH_DIR, "_待追加_待验证问题.md")


def bao_date():
    ov = os.environ.get("TODAY_OVERRIDE", "").strip()
    return ov if ov else datetime.now(BEIJING).strftime("%Y-%m-%d")


def file_size(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return 0


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except (FileNotFoundError, OSError):
        return ""


def list_recent_files(directory, pattern="*.md", days=7):
    """列出 directory 下匹配 pattern 的文件路径，按日期倒序。"""
    import glob as g
    files = sorted(g.glob(f"{directory}/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md"), reverse=True)
    return files[:days]


# ═══════════════════════════════════════════════════════════════
# 检查项
# ═══════════════════════════════════════════════════════════════

def check_sources(date_str):
    """检查 1: 三源文件存在 + 大小 > 200B。"""
    sources = {
        "AI HOT": os.path.join(AIHOT_DIR, f"{date_str}.md"),
        "X-Tweets": os.path.join(XTWEETS_DIR, f"{date_str}.md"),
        "TrendRadar": os.path.join(TR_DIR, f"{date_str}.md"),
    }
    details = {}
    for name, path in sources.items():
        sz = file_size(path)
        ok = sz > 200
        details[name] = {"size": sz, "ok": ok}

    ok_count = sum(1 for d in details.values() if d["ok"])
    missing = [n for n, d in details.items() if not d["ok"]]

    if ok_count == 3:
        return "🟢", "三源都在", details
    elif ok_count >= 2:
        return "🟡", f"缺: {', '.join(missing)}", details
    else:
        return "🔴", f"仅 {ok_count}/3 源在线，缺: {', '.join(missing)}", details


def check_xtweets(date_str):
    """检查 2: X-Tweets 有效推文计数。

    X-Tweets 文件格式:
      > <推文正文>          ← 一条推文
      > 🇨🇳 <翻译>          ← 翻译（不算新推文）
      > ↩ <回复>            ← 回复（算推文内容但非独立）
      🕐 HH:MM · ...        ← 元数据行
    """
    path = os.path.join(XTWEETS_DIR, f"{date_str}.md")
    if not os.path.exists(path):
        return "🟡", "今日无 X-Tweets 文件", 0

    text = read_file(path)
    if not text:
        return "🟡", "X-Tweets 文件为空", 0

    # 统计推文条数：开头行的 "> N 位博主 · M 条推文"
    header_match = re.search(r'>\s*\d+\s*位博主\s*·\s*(\d+)\s*条推文', text)
    declared_count = int(header_match.group(1)) if header_match else None

    # 实际计数：找到所有包含🕐时间戳的独立推文
    # 每条推文以 "> 内容" 开始，以含 "🕐" 的元数据行结束
    tweet_starts = 0
    lines = text.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        # 推文元数据行（带有时间戳🕐）标志着一条推文的结束
        if re.search(r'🕐', stripped):
            tweet_starts += 1

    if declared_count is not None and declared_count > 0:
        level = "🟢"
        detail = f"{declared_count} 条推文"
    elif tweet_starts > 0:
        level = "🟢"
        detail = f"~{tweet_starts} 条推文(计数)"
    else:
        level = "🔴"
        detail = "0 条推文"

    return level, detail, declared_count or tweet_starts


def check_route_log(date_str):
    """检查 3: _路由/当天.md 存在 + 字符数 > 500。"""
    path = os.path.join(ROUTE_DIR, f"{date_str}.md")
    text = read_file(path)

    if not text:
        return "🔴", "路由日志缺失", 0

    char_count = len(text)
    if char_count >= 500:
        return "🟢", f"{char_count} 字符", char_count
    else:
        return "🔴", f"仅 {char_count} 字符(不足 500)", char_count


def check_topic_pool():
    """检查 4: 选题池中 🌱待定 + 💤等待 条目数。"""
    text = read_file(TOPIC_FILE)
    if not text:
        return "🔴", "选题池文件不存在", 0

    # 只匹配表格行(以 | 🌱待定 或 | 💤等待 开头),排除图例行中出现的 emoji
    pending = len(re.findall(r'^\|\s*🌱待定', text, re.MULTILINE))
    waiting = len(re.findall(r'^\|\s*💤等待', text, re.MULTILINE))
    total = pending + waiting

    if total >= 5:
        return "🟢", f"{total} 条(🌱{pending} 💤{waiting})", total
    elif total >= 3:
        return "🟡", f"{total} 条(🌱{pending} 💤{waiting})", total
    else:
        return "🔴", f"仅 {total} 条(🌱{pending} 💤{waiting})", total


def check_translation(date_str):
    """检查 5: X-Tweets 翻译成功率。

    统计 X-Tweets 文件中 `> 🇨🇳` 翻译行数量 与 `翻译失败` 标记。
    """
    path = os.path.join(XTWEETS_DIR, f"{date_str}.md")
    text = read_file(path)
    if not text:
        return "🟢", "无数据", 0, 0

    succeeded = len(re.findall(r'> 🇨🇳', text))
    failed = len(re.findall(r'翻译失败', text))
    total = succeeded + failed

    if total == 0:
        return "🟢", "无需翻译(全中文)", 0, 0

    fail_rate = failed / total
    if fail_rate < 0.2:
        return "🟢", f"成功率 {succeeded}/{total} ({1-fail_rate:.0%})", succeeded, failed
    elif fail_rate < 0.5:
        return "🟡", f"成功率 {succeeded}/{total} ({1-fail_rate:.0%})", succeeded, failed
    else:
        return "🔴", f"成功率仅 {succeeded}/{total} ({1-fail_rate:.0%})", succeeded, failed


# ═══════════════════════════════════════════════════════════════
# 告警联动
# ═══════════════════════════════════════════════════════════════

def load_alert_history():
    """读取告警摘要，返回 {检查项: [(日期, 级别), ...]} 用于判断连续告警。"""
    text = read_file(ALERT_FILE)
    if not text:
        return {}
    history = {}
    for line in text.split("\n"):
        m = re.match(r'\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([^|]+?)\s*\|\s*([🟡🔴])\s*\|', line)
        if m:
            d, item, lv = m.group(1), m.group(2).strip(), m.group(3)
            history.setdefault(item, []).append((d, lv))
    return history


def check_consecutive(item, level, history, date_str, threshold=3):
    """检查某项是否为连续 N 天 🟡（或任一天 🔴）。"""
    if level == "🔴":
        return True, f"🔴 告警触发"
    if level == "🟡":
        past = history.get(item, [])
        # 统计最近连续 🟡 天数(含今天)
        consecutive = 1
        for d, lv in reversed(past):
            if lv in ("🟡", "🔴"):
                consecutive += 1
            else:
                break
        if consecutive >= threshold:
            return True, f"🟡 连续 {consecutive} 天"
    return False, ""


def update_alert_summary(date_str, results):
    """更新告警摘要，追加今日 🔴/🟡。返回需联动追加到待验证问题的列表。"""
    os.makedirs(HEALTH_DIR, exist_ok=True)
    history = load_alert_history()

    alerts = []
    to_verify = []

    for item_name, (level, detail) in results:
        if level not in ("🔴", "🟡"):
            continue

        should_notify, reason = check_consecutive(item_name, level, history, date_str)
        alerts.append(f"| {date_str} | {item_name} | {level} | {detail} |")

        if should_notify:
            to_verify.append(f"- [ ] [{date_str}] L1 告警: {item_name} — {reason}（{detail}）")

    # 写告警行
    existing = read_file(ALERT_FILE)
    if not existing:
        header = (
            "# 告警摘要\n\n"
            "> 仅记录 🔴 和 🟡。🟢 恢复时追加一条恢复记录。\n\n"
            "| 日期 | 检查项 | 级别 | 详情 |\n"
            "|------|--------|:---:|------|\n"
        )
        new_content = header + "\n".join(alerts) + "\n"
    else:
        new_content = existing.rstrip() + "\n" + "\n".join(alerts) + "\n"

    with open(ALERT_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    # 写待验证追加
    if to_verify:
        with open(TO_VERIFY_FILE, "w", encoding="utf-8") as f:
            f.write("# 待追加到 待验证问题.md\n\n")
            f.write("以下条目需由 PM/DevOps 手动追加到 vault 的 `05_系统维护/待验证问题.md`:\n\n")
            f.write("\n".join(to_verify) + "\n")

    return to_verify


# ═══════════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════════

def main():
    date_str = bao_date()
    print(f"=== L1 系统健康检查 · {date_str} ===")

    # 1. 信息源
    src_level, src_detail, src_info = check_sources(date_str)
    print(f"  [信息源] {src_level} {src_detail}")

    # 2. X-Tweets 推文
    xt_level, xt_detail, xt_count = check_xtweets(date_str)
    print(f"  [X-Tweets] {xt_level} {xt_detail}")

    # 3. 路由日志
    rl_level, rl_detail, rl_chars = check_route_log(date_str)
    print(f"  [路由日志] {rl_level} {rl_detail}")

    # 4. 选题池
    tp_level, tp_detail, tp_count = check_topic_pool()
    print(f"  [选题池] {tp_level} {tp_detail}")

    # 5. 翻译
    tr_level, tr_detail, tr_ok, tr_fail = check_translation(date_str)
    print(f"  [翻译] {tr_level} {tr_detail}")

    # ── 写健康报告 ──
    os.makedirs(HEALTH_DIR, exist_ok=True)
    report_path = os.path.join(HEALTH_DIR, f"{date_str}.md")

    lines = [
        f"# 系统健康 · {date_str}",
        "",
        "| # | 检查项 | 状态 | 详情 |",
        "|---|--------|:---:|------|",
        f"| 1 | 信息源产出 | {src_level} | {src_detail} |",
        f"| 2 | X-Tweets 推文 | {xt_level} | {xt_detail} |",
        f"| 3 | 路由日志 | {rl_level} | {rl_detail} |",
        f"| 4 | 选题池存量 | {tp_level} | {tp_detail} |",
        f"| 5 | 翻译成功率 | {tr_level} | {tr_detail} |",
        "",
    ]

    # 汇总
    reds = sum(1 for lv in [src_level, xt_level, rl_level, tp_level, tr_level] if lv == "🔴")
    yellows = sum(1 for lv in [src_level, xt_level, rl_level, tp_level, tr_level] if lv == "🟡")
    if reds:
        lines.append(f"> 🔴 {reds} 项异常  🟡 {yellows} 项警告")
    elif yellows:
        lines.append(f"> 🟡 {yellows} 项警告")
    else:
        lines.append("> 🟢 全绿，系统运行正常")

    report = "\n".join(lines) + "\n"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"OK: {report_path}")

    # ── 告警联动 ──
    results = [
        ("1.信息源", (src_level, src_detail)),
        ("2.X-Tweets", (xt_level, xt_detail)),
        ("3.路由日志", (rl_level, rl_detail)),
        ("4.选题池", (tp_level, tp_detail)),
        ("5.翻译", (tr_level, tr_detail)),
    ]
    to_verify = update_alert_summary(date_str, results)
    if to_verify:
        print(f"⚠ 待追加到待验证问题: {len(to_verify)} 条")
        for tv in to_verify:
            print(f"  {tv}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
