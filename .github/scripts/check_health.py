#!/usr/bin/env python3
"""L1 系统健康监控 — 每天 Action 采集+路由后自动运行。
纯标准库，零 LLM 调用，零成本。

检查项:
  1. 信息源产出（四源文件存在 + 大小 > 200B）
  2. X-Tweets 有效推文计数
  3. 路由日志产出（文件存在 + > 500 字符）
  4. 选题池存量（🔥/🌿/💤 条目数 + 表格质量：模板残留/重复行）
  5. 翻译成功率（翻译失败比例）
  6. 待验证问题（未处理条目数，非空 → 🟡）

输出:
  _系统健康/YYYY-MM-DD.md     — 每日健康报告
  _系统健康/_告警摘要.md       — 滚动告警摘要（🔴 和 🟡）
  _系统健康/待验证问题.md     — 待人工核实的条目（追加式，处理完删除对应行）
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
FB_DIR = "FollowBuilders"
ROUTE_DIR = "_路由"
TOPIC_FILE = "_选题池.md"
HEALTH_DIR = "_系统健康"
ALERT_FILE = os.path.join(HEALTH_DIR, "_告警摘要.md")
TO_VERIFY_FILE = os.path.join(HEALTH_DIR, "待验证问题.md")


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
    """检查 1: 四源文件存在 + 大小 > 200B。"""
    sources = {
        "AI HOT": os.path.join(AIHOT_DIR, f"{date_str}.md"),
        "X-Tweets": os.path.join(XTWEETS_DIR, f"{date_str}.md"),
        "TrendRadar": os.path.join(TR_DIR, f"{date_str}.md"),
        "FollowBuilders": os.path.join(FB_DIR, f"{date_str}.md"),
    }
    details = {}
    for name, path in sources.items():
        sz = file_size(path)
        ok = sz > 200
        details[name] = {"size": sz, "ok": ok}

    ok_count = sum(1 for d in details.values() if d["ok"])
    missing = [n for n, d in details.items() if not d["ok"]]

    if ok_count == 4:
        return "🟢", "四源都在", details
    elif ok_count >= 3:
        return "🟡", f"缺: {', '.join(missing)}", details
    else:
        return "🔴", f"仅 {ok_count}/4 源在线，缺: {', '.join(missing)}", details


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

    # 检测抓取异常标记
    fetch_errors = len(re.findall(r'⚠️ \[抓取异常', text))
    if fetch_errors > 0:
        if level == "🟢":
            level = "🟡"
        detail += f" · ⚠️ {fetch_errors} 处抓取异常"

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
    """检查 4: 选题池「可写库存」= 🔥 + 🌿 + 💤 三区的条目数。

    三区均为 Markdown 表格，按分区统计表格数据行。
    ✅ 已发布不计入库存。
    """
    text = read_file(TOPIC_FILE)
    if not text:
        return "🔴", "选题池文件不存在", 0

    counts = {"🔥": 0, "🌿": 0, "💤": 0}
    current = None
    in_table = False
    seen_rows = []
    for line in text.split("\n"):
        s = line.strip()
        m = re.match(r'^##\s*(🔥|🌿|💤|✅)', s)
        if m:
            sec = m.group(1)
            current = sec if sec in counts else None
            in_table = False
            continue
        if current is None:
            continue
        # 检测表格开始
        if s.startswith("|"):
            in_table = True
        elif not s.startswith("|") and s != "":
            in_table = False
            continue
        if not in_table or not s.startswith("|"):
            continue
        # 跳过分隔行和表头
        if set(s) <= set("|-: "):
            continue
        first_cell = s.strip("|").split("|")[0].strip()
        if first_cell in ("选题", "文章", "标题"):
            continue
        # ⸺ 占位符行（阿里 Claude 那条）不计
        if first_cell == "⸺":
            continue
        counts[current] += 1
        seen_rows.append(s)

    total = counts["🔥"] + counts["🌿"] + counts["💤"]
    detail = f"{total} 条(🔥{counts['🔥']} 🌿{counts['🌿']} 💤{counts['💤']})"

    # 表格质量（P-20260808-04）：模板残留行（含 < 占位符）+ 完全重复行
    issues = []
    template_rows = [r for r in seen_rows if "<" in r]
    if template_rows:
        issues.append(f"{len(template_rows)} 行模板残留")
    dup_rows = len(seen_rows) - len(set(seen_rows))
    if dup_rows:
        issues.append(f"{dup_rows} 行重复")

    if issues:
        return "🟡", detail + " · 表格质量: " + "、".join(issues), total
    if total >= 5:
        return "🟢", detail, total
    elif total >= 3:
        return "🟡", detail, total
    else:
        return "🔴", detail, total


def check_translation(date_str):
    """检查 5: X-Tweets 翻译成功率。

    统计 X-Tweets 文件中 `> 🇨🇳` 翻译行数量 与 `[翻译失败]` 标记。
    注: `> 🇨🇳 [翻译失败]` 表示翻译尝试失败（API 不可用/超时等），
    与"无需翻译(全中文)"不同——后者意味着没有英文推文需要翻译。
    """
    path = os.path.join(XTWEETS_DIR, f"{date_str}.md")
    text = read_file(path)
    if not text:
        return "🟢", "无数据", 0, 0

    succeeded = len(re.findall(r'> 🇨🇳 (?!\[翻译失败\])', text))
    failed = len(re.findall(r'> 🇨🇳 \[翻译失败\]', text))
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

def check_pending_verification():
    """检查 6: 待验证问题文件中未处理条目的数量。非空 → 🟡（提醒闭环，不进告警摘要）。"""
    text = read_file(TO_VERIFY_FILE)
    if not text:
        return "🟢", "无待处理", 0
    pending = len(re.findall(r'^\s*-\s*\[\s*\]', text, re.M))
    if pending == 0:
        return "🟢", "无待处理", 0
    return "🟡", f"{pending} 条待处理", pending


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
    """更新告警摘要，追加今日 🔴/🟡。返回本次实际写入待验证问题的列表。"""
    os.makedirs(HEALTH_DIR, exist_ok=True)
    history = load_alert_history()

    existing = read_file(ALERT_FILE)
    if not existing:
        existing = (
            "# 告警摘要\n\n"
            "> 仅记录 🔴 和 🟡。🟢 恢复时追加一条恢复记录。\n\n"
            "| 日期 | 检查项 | 级别 | 详情 |\n"
            "|------|--------|:---:|------|\n"
        )

    # 已记录行键（日期|检查项）：同日同项不重复追加，防手动重跑污染连续天数统计
    recorded = set()
    for line in existing.split("\n"):
        m = re.match(r'\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([^|]+?)\s*\|', line)
        if m:
            recorded.add((m.group(1), m.group(2).strip()))

    alerts = []
    to_verify = []

    for item_name, (level, detail) in results:
        if level not in ("🔴", "🟡"):
            continue
        if (date_str, item_name) in recorded:
            continue
        should_notify, reason = check_consecutive(item_name, level, history, date_str)
        alerts.append(f"| {date_str} | {item_name} | {level} | {detail} |")
        if should_notify:
            to_verify.append(f"- [ ] [{date_str}] L1 告警: {item_name} — {reason}（{detail}）")

    if alerts:
        new_content = existing.rstrip() + "\n" + "\n".join(alerts) + "\n"
        with open(ALERT_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)

    # 待验证问题（P-20260808-03）：追加式写入，同日同检查项不重复追加；
    # 人工核实处理后由人删除对应行（或改为 ✅ 并注明结论）
    fresh = []
    if to_verify:
        verify_existing = read_file(TO_VERIFY_FILE)
        if not verify_existing:
            verify_existing = (
                "# 待验证问题\n\n"
                "> 健康检查自动追加（🔴 或连续 🟡 时）。人工核实处理后**删除对应行**"
                "（或改为 ✅ 并注明结论）。随每日日报仓库同步到远程。\n\n"
            )
        else:
            verify_existing = verify_existing.rstrip() + "\n"
        for tv in to_verify:
            marker = tv.split(" — ")[0]
            if marker not in verify_existing:
                fresh.append(tv)
        if fresh:
            with open(TO_VERIFY_FILE, "w", encoding="utf-8") as f:
                f.write(verify_existing + "\n".join(fresh) + "\n")

    return fresh


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

    # 6. 待验证问题
    pv_level, pv_detail, pv_count = check_pending_verification()
    print(f"  [待验证问题] {pv_level} {pv_detail}")

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
        f"| 6 | 待验证问题 | {pv_level} | {pv_detail} |",
        "",
    ]

    # 汇总
    reds = sum(1 for lv in [src_level, xt_level, rl_level, tp_level, tr_level, pv_level] if lv == "🔴")
    yellows = sum(1 for lv in [src_level, xt_level, rl_level, tp_level, tr_level, pv_level] if lv == "🟡")
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
        print(f"⚠ 待验证问题追加: {len(to_verify)} 条")
        for tv in to_verify:
            print(f"  {tv}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
