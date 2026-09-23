#!/usr/bin/env python3
"""L1 系统健康监控 — 每天 Action 采集+路由后自动运行。
纯标准库，零 LLM 调用，零成本。

检查项:
  1. 信息源产出（四源文件存在 + 大小 > 200B）
  2. X-Tweets 有效推文计数
  3. 路由日志产出（文件存在 + > 500 字符 + ⭐/普通两区完整未截断）
  4. 选题池存量（🔥/🌿/💤 条目数 + 表格质量：模板残留/重复行）
  5. 翻译成功率（翻译失败比例）
  6. 待验证问题（未处理条目数，非空 → 🟡）
  7. 每日精选产出（_每日精选/当天.md 存在且四区完整）
  8. 路由覆盖率（近 7 天「上游有输入却无路由产出」的天数——查趋势性失效）
  9. 写作产出（选题池 ✅ 已发布 最近日期距今天数——查目的侧停滞）

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
DIGEST_DIR = os.environ.get("DIGEST_OUT_DIR", "_每日精选")
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
    """检查 3: _路由/当天.md 存在 + 字符数 > 500 + **结构完整未被截断**。

    只查字符数会漏掉"日志落盘了但被输出预算砍半"这种情况——那正是选题池
    断供 6 周却只报 🟡 的原因。所以这里同时查两个区是否都在。
    """
    path = os.path.join(ROUTE_DIR, f"{date_str}.md")
    text = read_file(path)

    if not text:
        return "🔴", "路由日志缺失", 0

    char_count = len(text)
    if char_count < 500:
        return "🔴", f"仅 {char_count} 字符(不足 500)", char_count

    # 结构完整性：⭐ 区与普通选题区都必须在，否则是输出被截断
    missing = []
    if "高优先级选题" not in text:
        missing.append("高优先级区")
    if "普通选题" not in text:
        missing.append("普通选题区")
    if missing:
        return "🟡", f"{char_count} 字符，但缺 {'/'.join(missing)}（疑被截断）", char_count
    return "🟢", f"{char_count} 字符", char_count


def check_router_coverage(days=7):
    """检查 8: 近 N 天里「上游有输入、路由却无产出」的天数。

    为什么需要这一项：检查 1 只看当天四源是否在线，检查 3 只看当天路由日志；
    两者都发现不了**长期趋势性失效**——实测路由日志 39 份 / 83 天，也就是说
    一半以上的日子上游明明有内容、路由却没产出，而旧健康检查全程只报 🟡/🔴
    的「路由日志缺失」，没有任何一项把它归因为"路由步骤反复失败"。

    判定口径（保守）：某天算"本应有路由"需要当日四源里**至少两份**文件有实质内容
    （>200B）。只有一份源的边角日子不算，避免误报。
    """
    def _has_content(path):
        return file_size(path) > 200

    should_have, produced, missing = 0, 0, []
    for i in range(days):
        d = (datetime.now(BEIJING) - timedelta(days=i)).strftime("%Y-%m-%d")
        present = sum(
            1 for p in (
                os.path.join(AIHOT_DIR, f"{d}.md"),
                os.path.join(XTWEETS_DIR, f"{d}.md"),
                os.path.join(TR_DIR, f"{d}.md"),
                os.path.join(FB_DIR, f"{d}.md"),
            ) if _has_content(p)
        )
        if present < 2:
            continue
        should_have += 1
        if _has_content(os.path.join(ROUTE_DIR, f"{d}.md")):
            produced += 1
        else:
            missing.append(d)

    if should_have == 0:
        return "🟢", f"近 {days} 天无可判定日期", 0
    lost = should_have - produced
    detail = f"{produced}/{should_have} 天有产出"
    if lost == 0:
        return "🟢", detail, 0
    if lost >= should_have / 2:
        return "🔴", f"{detail}，缺 {lost} 天（路由步骤反复失败）", lost
    return "🟡", f"{detail}，缺 {'、'.join(missing[-3:])}", lost


def check_writing_output(date_str, stale_days=14):
    """检查 9: 写作产出是否停滞（选题池 ✅ 已发布 的最近日期距今天数）。

    为什么需要这一项：本系统最靠近"目的"的一环是**写成公众号文章**，但此前 8 项
    检查里没有任何一项能发现"整条线在跑、却两个月没产出"。实测：✅ 已发布 区最近
    日期为 07-22，至 09-23 已停滞约 63 天，而健康报告长期只显示 🟡「选题池存量」
    —— 那是**输入侧**指标，与产出侧无关。

    判定：以选题池 ✅ 已发布 区的最大 MM-DD 为最近发布日。
    """
    text = read_file(TOPIC_FILE)
    if not text:
        return "🟡", "选题池不存在，无法判断写作产出", 0

    if "## ✅" not in text:
        return "🟡", "选题池缺「✅ 已发布」区，无法判断写作产出", 0
    section = text.split("## ✅", 1)[1].split("\n## ", 1)[0]

    dates = []
    for line in section.splitlines():
        s = line.strip()
        if not s.startswith("|") or set(s) <= set("|-: ") or "---" in s:
            continue
        cols = [c.strip() for c in s.split("|")]
        if len(cols) < 2:
            continue
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$|^(\d{2})-(\d{2})$", cols[1])
        if not m:
            continue
        if m.group(1):  # YYYY-MM-DD
            dates.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))
        else:           # MM-DD → 补年份
            dates.append((int(date_str[:4]), int(m.group(4)), int(m.group(5))))

    if not dates:
        return "🟡", "「✅ 已发布」区无有效日期条目", 0

    try:
        today = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        today = datetime.now(BEIJING).replace(tzinfo=None)
    latest = max(dates)
    try:
        latest_dt = datetime(latest[0], latest[1], latest[2])
    except ValueError:
        return "🟡", f"「✅ 已发布」区日期不合法: {latest}", 0

    gap = (today - latest_dt).days
    latest_str = f"{latest[0]:04d}-{latest[1]:02d}-{latest[2]:02d}"

    # 日期在未来：多为跨年（池里只写 MM-DD，补的是今天年份）。不误报为停滞。
    if gap < 0:
        return "🟢", f"最近发布 {latest_str}", 0
    if gap >= 30:
        return "🔴", f"写作产出已停滞 {gap} 天（最近发布 {latest_str}）", gap
    if gap >= stale_days:
        return "🟡", f"{gap} 天无新发布（最近 {latest_str}）", gap
    return "🟢", f"最近发布 {latest_str}（{gap} 天前）", 0


def check_digest(date_str):
    """检查 7: _每日精选/当天.md 存在且不是空壳。

    这是**产出层**体检：旧健康检查只盯着采集/筛选，没有任何一项能发现
    "系统在跑但两个月没产出过东西"。
    """
    path = os.path.join(DIGEST_DIR, f"{date_str}.md")
    text = read_file(path)
    if not text:
        return "🟡", "当日精选缺失", 0

    char_count = len(text)
    if char_count < 300:
        return "🟡", f"仅 {char_count} 字符（疑似空壳）", char_count

    missing = [s for s in ("今天最重要的", "数字速览", "今天可写") if s not in text]
    if missing:
        return "🟡", f"{char_count} 字符，但缺 {'/'.join(missing)}", char_count
    return "🟢", f"{char_count} 字符", char_count


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

    # 7. 每日精选（产出层）
    dg_level, dg_detail, dg_count = check_digest(date_str)
    print(f"  [每日精选] {dg_level} {dg_detail}")

    # 8. 路由覆盖率（趋势性失效）
    rc_level, rc_detail, rc_lost = check_router_coverage()
    print(f"  [路由覆盖率] {rc_level} {rc_detail}")

    # 9. 写作产出（目的侧：有没有文章出来）
    wo_level, wo_detail, wo_gap = check_writing_output(date_str)
    print(f"  [写作产出] {wo_level} {wo_detail}")

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
        f"| 7 | 每日精选产出 | {dg_level} | {dg_detail} |",
        f"| 8 | 路由覆盖率(7天) | {rc_level} | {rc_detail} |",
        f"| 9 | 写作产出 | {wo_level} | {wo_detail} |",
        "",
    ]

    # 汇总
    levels = [src_level, xt_level, rl_level, tp_level, tr_level, pv_level, dg_level, rc_level, wo_level]
    reds = sum(1 for lv in levels if lv == "🔴")
    yellows = sum(1 for lv in levels if lv == "🟡")
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
        ("7.每日精选", (dg_level, dg_detail)),
        ("8.路由覆盖率", (rc_level, rc_detail)),
        ("9.写作产出", (wo_level, wo_detail)),
    ]
    to_verify = update_alert_summary(date_str, results)
    if to_verify:
        print(f"⚠ 待验证问题追加: {len(to_verify)} 条")
        for tv in to_verify:
            print(f"  {tv}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
