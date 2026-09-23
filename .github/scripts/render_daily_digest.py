#!/usr/bin/env python3
"""每日精选 — 把当日四源 + 路由日志统合成一份可读、可写的当日精选。

解决的问题
    四源报告按源分文件（AI-HOT / TrendRadar / X-Tweets / FollowBuilders），
    路由日志又是给写作用的筛选结果 —— 每天要看 5 个文件才拼得出全貌。
    本脚本把它们合成**一份**：跨领域要闻 + 数字速览 + 可写选题。
    对应提案 P-20260811-02（每日专属新闻报告）。

产物
    _每日精选/YYYY-MM-DD.md

与 router 的分工（不重叠）
    router  → 筛选层：判断"今天什么值得写"，产出路由日志 + 选题池
    digest  → 消费层：把当天信息提纯成"一份读完就够"的东西

环境变量
    DEEPSEEK_API_KEY   — API Key（必需，除非设置 DIGEST_NO_LLM=1）
    DIGEST_MODEL       — 模型（默认 deepseek-flash）
    TODAY_OVERRIDE     — 指定日期（YYYY-MM-DD）
    DIGEST_DRY_RUN     — "1" 时只写预览文件，不写正式产物
    DIGEST_NO_LLM      — "1" 时跳过 LLM，直接产出降级精选（机械提取）
    DIGEST_MAX_TOKENS  — 输出预算（默认 4096；本产物短，不必试探 API 上限）

降级设计
    LLM 调用失败时**不再直接归零**，改为产出「降级版精选」：选题引自路由日志、
    数字从四源机械摘录，并明确标注"未经编辑加工"。理由：LLM 一坏整条产出层就
    没了，而本机 LLM 恰恰已经坏了几周 —— 产出层不能建立在单点上。
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

# 选题提取复用路由脚本的解析器（同一份路由日志，同一套解析规则）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_topic_pool import parse_route_log  # noqa: E402

BEIJING = timezone(timedelta(hours=8))
# 模型名。初版写成 "deepseek-chat" —— 该别名**已于 2026-07-24 停用**，等于一上线
# 就是坏的（详见 render_xtweets.py 的同一处教训）。现用当前模型 deepseek-flash。
MODEL = os.environ.get("DIGEST_MODEL", "deepseek-flash")
API_BASE = "https://api.deepseek.com/v1/chat/completions"
OUT_DIR = os.environ.get("DIGEST_OUT_DIR", "_每日精选")
MAX_TOKENS = int(os.environ.get("DIGEST_MAX_TOKENS", "4096"))
DRY_RUN = os.environ.get("DIGEST_DRY_RUN", "") == "1"
# 强制走降级路径：本地验证降级产物、或 API 故障期间临时止血
NO_LLM = os.environ.get("DIGEST_NO_LLM", "") == "1"

# 单源最多喂入多少字符，避免上下文被某一源吃光
PER_SOURCE_LIMIT = 12000

DIGEST_SYSTEM_PROMPT = """你是「AI × 经济」知识库的当日精选编辑。读者是一个人，他要的是**读完这一份就知道今天发生了什么、什么最重要**，而不是信息堆砌。

## 你的输入
当日四个信息源（AI HOT / TrendRadar / X-Tweets / FollowBuilders）和当天的路由日志（已筛选出的写作选题）。

## 输出（严格按下面结构，不要加别的区）

===DIGEST===
# 每日精选 · YYYY-MM-DD

> 一句话：今天最值得知道的是什么（30 字内，要具体，不要"AI 持续发展"这种空话）

## 📌 今天最重要的 5 条

按重要性排序（不是按领域平均分配），每条格式固定：

1. **<标题：具体的人/公司/数字，不要抽象概括>**
   - 事实：<2-3 句，必须有具体数字或具体动作>
   - 为什么重要：<1-2 句，串到产业逻辑或周期上，不要复述事实>
   - 来源：<源名 + 具体条目>

## 🔢 数字速览

今天出现的、值得记住的硬数字（5-8 条）。每条一行：`<数字> — <它意味着什么>`
只收有信息量的数字（增速、价格、产能、估值、成本变化），不收"XX 公司发布了 XX"这类无数字条目。

## 🌐 领域速览

- **AI/科技**：<2-3 句，覆盖当天该领域最有信号量的事>
- **财经/市场**：<2-3 句>
- **国际/政治**：<2-3 句>
- **其他值得知道**：<1-2 句；确实没有就写"今日无">

## ✍️ 今天可写（从路由日志提取）

1-3 条。每条格式：

- **<选题标题>**（传播分 X/5）
  - 钩子：<一句让人想看下去的话>
  - 怎么切：<切入角度，1-2 句>
  - 素材够不够：<够开写 / 需要补调研：补什么>

===END===

## 硬性要求
- **只要事实与数字，不要评论腔**。禁止"值得我们深思""引发了广泛关注"这类填充句。
- 每条"为什么重要"必须给出**因果或对照**（和什么比、违背了什么预期），不要同义反复。
- 数字必须来自输入材料，**不许推算、不许编造**。材料里没有就少写一条。
- 读不出来/材料缺失的领域，直接写"今日无"，不要硬凑。
- 全文控制在 900-1300 字。宁可少写一条，不要注水。
"""


def bao_date() -> str:
    override = os.environ.get("TODAY_OVERRIDE", "").strip()
    if override:
        return override
    return datetime.now(BEIJING).strftime("%Y-%m-%d")


def read_file(path: str, limit: int = PER_SOURCE_LIMIT) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except (FileNotFoundError, OSError):
        return ""
    if len(text) > limit:
        text = text[:limit] + f"\n…（已截断，原文 {len(text)} 字符）"
    return text


def build_context(date_str: str) -> tuple[str, dict]:
    """拼装上下文，返回 (上下文, 各源统计)。"""
    sources = {
        "AI HOT": f"AI-HOT/{date_str}.md",
        "TrendRadar": f"TrendRadar/{date_str}.md",
        "X-Tweets": f"X-Tweets/{date_str}.md",
        "FollowBuilders": f"FollowBuilders/{date_str}.md",
    }
    parts = [f"=== 当日日期: {date_str} ===", ""]
    stats: dict[str, int] = {}
    for name, path in sources.items():
        text = read_file(path)
        stats[name] = len(text)
        if text:
            parts.append(f"=== {name} ===")
            parts.append(text)
            parts.append("")
        else:
            parts.append(f"=== {name} ===（当日无产出）")
            parts.append("")

    route = read_file(f"_路由/{date_str}.md")
    stats["路由日志"] = len(route)
    if route:
        parts.append("=== 当日路由日志（已筛选的写作选题） ===")
        parts.append(route)
    else:
        parts.append("=== 当日路由日志 ===（当日缺失）")
    return "\n".join(parts), stats


def gh_annotate(level: str, message: str) -> None:
    """在 GitHub Actions 运行页产生注解。

    本步骤是 `continue-on-error: true`，失败会显示为成功 —— 注解是让
    "今天没生成精选"、以及失败原因一眼可见的手段。
    """
    message = message.replace("\n", " ").replace("%", "%25").replace("\r", "%0D")
    print(f"::{level} title=每日精选::{message}", flush=True)


def call_deepseek(system: str, user: str, max_tokens: int = MAX_TOKENS) -> str:
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY 环境变量未设置")
    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
        # 关闭思考模式：官方文档「思考模式默认打开，effort 默认 high」，思维链会先
        # 占用 max_tokens 预算。精选是**格式固定的结构化产出**，思维链无增益却会
        # 挤掉正文预算（本产物 900-1300 字，预算 4096，被思维链吃掉就写不完）。
        # 另：思考模式下 temperature 不生效，关闭后 0.4 才真正起作用。
        "thinking": {"type": "disabled"},
        "temperature": 0.4,
    }).encode("utf-8")
    req = urllib.request.Request(
        API_BASE,
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8", "replace")[:400]
        except Exception:  # noqa: BLE001
            detail = "(响应体读取失败)"
        raise RuntimeError(f"HTTP {e.code} {e.reason} — {detail}") from e
    content = data["choices"][0]["message"]["content"]
    if not content or not content.strip():
        raise RuntimeError("DeepSeek 返回空内容 — 可能 Key 失效、额度耗尽或限流")
    return content


def extract_digest(raw: str) -> str:
    """取出 ===DIGEST=== 与 ===END=== 之间的正文。"""
    m = re.search(r"===DIGEST===\s*(.+?)\s*===END===", raw, re.S)
    body = m.group(1) if m else raw
    body = re.sub(r"^```\w*\n?", "", body.strip())
    body = re.sub(r"\n?```\s*$", "", body)
    return body.strip()


def validate_digest(body: str) -> list[str]:
    """体检：缺区 / 数字段为空都算问题（不静默通过）。"""
    problems: list[str] = []
    for section in ("今天最重要的", "数字速览", "领域速览", "今天可写"):
        if section not in body:
            problems.append(f"缺「{section}」区")
    # 数字速览是否真有数字
    m = re.search(r"##\s*🔢\s*数字速览\s*(.+?)(?=\n##|\Z)", body, re.S)
    if m and not re.search(r"\d", m.group(1)):
        problems.append("数字速览区没有任何数字")
    if len(body) < 400:
        problems.append(f"正文过短（{len(body)} 字符）")
    last = ""
    for line in reversed(body.splitlines()):
        if line.strip():
            last = line.strip()
            break
    if last.endswith(("，", "、", "：", "——", "-")):
        problems.append("末尾疑似被截断")
    return problems


def extract_numbers(date_str: str, limit: int = 8) -> list[tuple[str, str]]:
    """从当日四源里抽取硬数字，返回 [(数字, 上下文)]。

    这是兜底精选的核心价值：即使 LLM 完全不可用，「今天的硬数字」也能被
    机械地捞出来。抽取规则刻意保守：
      - 只认带明确量纲的形态（%/倍/亿/万/个百分点…），避免把日期、序号当信号；
      - **跳过含 URL 的行**（TrendRadar 的条目带百度/知乎链接，链接里的编码数字
        会产出 "81500%" 这种垃圾）；
      - 同一行只取一个数字，避免一句话里 81.0%/84.4%/3.3 三个数重复三遍。
    """
    NOISE = re.compile(r"^\d{4}$|^\d{1,2}$|^\d{1,2}月$|^20\d\d-\d\d")
    pattern = re.compile(
        r"(\d+(?:\.\d+)?\s*(?:%|％|倍|亿美元|万元|亿元|亿|万|美元|个百分点|bp|个基点))"
    )
    TIME_NOISE = ("年", "月", "日", "点", "时", "分")
    URL = re.compile(r"https?://|www\.|%[0-9A-Fa-f]{2}")

    seen: set[str] = set()
    seen_ctx: list[str] = []
    out: list[tuple[str, str]] = []

    def _dup_context(ctx: str) -> bool:
        """上下文是否与已收录的重复（同一事件在多源里出现 → 只留一条）。"""
        norm = re.sub(r"\s+", "", ctx)[:40]
        for prev in seen_ctx:
            if norm and (norm in prev or prev in norm):
                return True
        return False

    files = [
        f"AI-HOT/{date_str}.md",
        f"TrendRadar/{date_str}.md",
        f"X-Tweets/{date_str}.md",
        f"FollowBuilders/{date_str}.md",
        f"_路由/{date_str}.md",
    ]
    for path in files:
        text = read_file(path, limit=20000)
        if not text:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or set(line) <= set("|-: "):
                continue
            if URL.search(line):
                continue
            if re.search(r"(发布|更新于|时间|UTC|GMT)\s*[:：]?\s*\d", line):
                continue
            # 路由日志的元数据行不是内容，数字（如"#7"）没有信息量
            if re.match(r"^[-*]\s*(来源|框架|锚点|传播|观点信号|merge_hint|选题角度)\s*[:：]", line):
                continue
            if line.startswith(">"):
                continue
            m = pattern.search(line)  # 每行最多取一个，防止同句数字刷屏
            if not m:
                continue
            raw = m.group(1).strip()
            num = re.split(r"[%％倍亿万美元个]|bp", raw)[0].strip()
            if NOISE.match(num) or raw in seen:
                continue
            tail = raw[len(num):].strip()
            if tail in TIME_NOISE:
                continue
            seen.add(raw)
            ctx = line[:160]
            if _dup_context(ctx):
                continue
            seen_ctx.append(re.sub(r"\s+", "", ctx)[:40])
            out.append((raw, ctx))
            if len(out) >= limit:
                return out
    return out


def _route_section(date_str: str) -> str:
    """从路由日志提取选题，生成「今天可写」区。"""
    route_text = read_file(f"_路由/{date_str}.md")
    if not route_text:
        return "## ✍️ 今天可写\n\n（当日无路由日志 —— 路由未成功，无筛选结果）\n"
    topics = parse_route_log(route_text)
    if not topics:
        return "## ✍️ 今天可写\n\n（路由日志里未解析出选题 —— 可能被截断）\n"
    lines = ["## ✍️ 今天可写", ""]
    for t in topics:
        lines.append(f"- **{t['title']}**（{t['spread'] or '传播分未标注'}）")
        if t["hook"]:
            lines.append(f"  - 钩子：{t['hook']}")
        if t["angle"]:
            lines.append(f"  - 怎么切：{t['angle']}")
        if t["merge_hint"] and t["merge_hint"] != "无":
            lines.append(f"  - 合并建议：{t['merge_hint']}")
    lines.append("")
    return "\n".join(lines)


def _content_titles(path: str, limit: int = 3) -> list[str]:
    """从一份日报里取真正的内容标题。

    各源条目形态不同，实测：
      - AI-HOT      `1. **标题** — 来源`   （编号 + 粗体）
      - TrendRadar  `1. 纯文本标题`        （编号，无粗体）
      - X-Tweets    `#### @某人`           （小节标题）
    所以按"编号条目优先、其次粗体条目、最后小节标题"的顺序取；关键是**不能**
    取 `## 🧠 模型发布/更新` 这类分类标题 —— 那是目录名，对读者毫无信息量。
    """
    text = read_file(path, limit=20000)
    if not text:
        return []
    numbered: list[str] = []
    bolded: list[str] = []
    headings: list[str] = []
    quotes: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        # 过滤目录型行：只有序号没有内容、或明显是导航
        m = re.match(r"^(?:\d+[.、]|[-*])\s*\*\*(.{6,100}?)\*\*", s)
        if m:
            numbered.append(m.group(1))
            continue
        m = re.match(r"^\d+[.、]\s*([^|>#*\s].{5,100})$", s)
        if m:
            numbered.append(m.group(1))
            continue
        m = re.match(r"^[-*]\s*\*\*(.{6,100}?)\*\*", s)
        if m:
            bolded.append(m.group(1))
            continue
        m = re.match(r"^#{3,4}\s+(.{4,100})$", s)
        if m:
            headings.append(m.group(1))
            continue
        # X-Tweets 用 `> 推文摘要` 承载内容，没有编号/粗体条目
        if s.startswith(">"):
            m = re.match(r"^>\s*(.{10,140})$", s)
            if m:
                quotes.append(m.group(1))
            continue

    titles: list[str] = []
    for group in (numbered, bolded, headings, quotes):
        for raw in group:
            title = re.sub(r"\s*—.*$", "", raw).strip(" *#：:。>")
            title = re.sub(r"^[（(]\d+[）)]\s*", "", title)
            # 去掉链接：FollowBuilders 的推文标题常带 t.co 短链
            title = re.sub(r"\s*https?://\S+.*$", "", title).strip()
            if not title or title.startswith("http") or len(title) < 6:
                continue
            # 分类标签而非内容：「📝 原创（5 条）」「↩ 回复（4 条）」
            if re.search(r"[（(]\d+\s*条[）)]\s*$", title):
                continue
            # 统计行而非内容：「2 位博主 · 17 条推文」「17 位 builder · 43 条推文」
            if "·" in title and re.search(r"\d+\s*(位|条)", title):
                continue
            # 纯 @句柄（X-Tweets 的小节标题就是博主名，无内容信息）
            if re.fullmatch(r"[@#][\w.]+", title):
                continue
            if title in titles:
                continue
            titles.append(title)
            if len(titles) >= limit:
                return titles
    return titles


def _domain_section(date_str: str, out: list[str]) -> None:
    """领域速览：把各源的内容标题按源聚合，不做 LLM 判断。"""
    out.append("## 🌐 领域速览")
    out.append("")
    for label, path in (
        ("AI/科技（AI HOT）", f"AI-HOT/{date_str}.md"),
        ("热点/市场（TrendRadar）", f"TrendRadar/{date_str}.md"),
        ("博主信号（X-Tweets）", f"X-Tweets/{date_str}.md"),
        ("AI builder（FollowBuilders）", f"FollowBuilders/{date_str}.md"),
    ):
        titles = _content_titles(path)
        if titles:
            out.append(f"- **{label}**：" + "；".join(titles))
        else:
            out.append(f"- **{label}**：当日无可提取标题")
    out.append("")


def build_fallback_digest(date_str: str, reason: str = "") -> str:
    """不用 LLM 也能产出的降级精选。

    为什么需要：LLM 一坏，整条产出层就归零——而这台机器上 LLM 恰恰已经
    坏了几周。降级版只做**机械提取**（不编造、不推断），保证每天至少有一份
    可读、可写的东西，并明确标注"未经编辑加工"。
    """
    route_text = read_file(f"_路由/{date_str}.md")
    topics = parse_route_log(route_text) if route_text else []

    out: list[str] = [
        f"# 每日精选（降级版）· {date_str}",
        "",
        "> ⚠️ **本份由脚本机械生成，未经 LLM 编辑加工。**"
        + (f"原因：{reason}" if reason else ""),
        "> 数字为原文自动摘录（未核对语义），选题直接引自路由日志。",
        "",
    ]

    # 今天最重要的：用路由日志的 ⭐ 选题当骨架（没有就明说）
    out.append("## 📌 今天最重要的")
    out.append("")
    star = [t for t in topics if t["mark"] == "⭐"]
    if star:
        for i, t in enumerate(star, 1):
            out.append(f"{i}. **{t['title']}**")
            if t["angle"]:
                out.append(f"   - 角度：{t['angle']}")
            if t["sources"]:
                out.append(f"   - 来源：{t['sources'][:200]}")
    else:
        out.append("（当日无路由日志或未筛出高优先级选题 —— 请直接看下方领域速览）")
    out.append("")

    # 数字速览
    out.append("## 🔢 数字速览")
    out.append("")
    nums = extract_numbers(date_str)
    if nums:
        for raw, ctx in nums:
            out.append(f"- {raw} — {ctx}")
    else:
        out.append("（当日未自动摘录到带量纲的数字）")
    out.append("")

    _domain_section(date_str, out)
    out.append(_route_section(date_str))
    return "\n".join(out).rstrip() + "\n"


def _write_output(body: str, date_str: str) -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{date_str}.md")
    if DRY_RUN:
        preview = f"_{OUT_DIR.strip('_')}_dryrun.md"
        with open(preview, "w", encoding="utf-8") as f:
            f.write(body + "\n")
        print(f"DRY_RUN: 已写 {preview}（未写正式产物）")
        return 0
    with open(path, "w", encoding="utf-8") as f:
        f.write(body + "\n")
    print(f"OK: {path}")
    return 0


def main() -> int:
    date_str = bao_date()
    print(f"=== 每日精选 · {date_str} ===")
    print(f"模型: {MODEL}")

    context, stats = build_context(date_str)
    print("输入: " + "  ".join(f"{k}={v}" for k, v in stats.items()))
    missing = [k for k, v in stats.items() if v == 0]
    if missing:
        print(f"WARNING: 以下输入当日缺失 —— {'、'.join(missing)}")
        gh_annotate("warning", f"当日输入缺失：{'、'.join(missing)}（精选覆盖面会打折）")
    if stats["AI HOT"] == 0 and stats["TrendRadar"] == 0:
        print("ERROR: 当日主源全部缺失，不生成精选")
        gh_annotate("error", "AI HOT 与 TrendRadar 当日都缺失 —— 不生成精选")
        return 1
    print(f"上下文约 {len(context)} 字符")

    # 强制降级（本地验证 / 临时绕开 API 故障）
    if NO_LLM:
        print("NO_LLM=1：跳过 LLM，直接产出降级精选")
        gh_annotate("notice", "按 DIGEST_NO_LLM 设置产出降级精选（未经 LLM 加工）")
        return _write_output(build_fallback_digest(date_str, "已设置 DIGEST_NO_LLM"), date_str)

    print("调用 DeepSeek API …")
    try:
        raw = call_deepseek(DIGEST_SYSTEM_PROMPT, context)
    except Exception as exc:  # noqa: BLE001 — 要原样上报原因
        reason = f"{type(exc).__name__}: {exc}"
        print(f"ERROR: DeepSeek 调用失败 —— {reason}")
        # 降级而不是归零：LLM 坏了也要有一份可读产物
        gh_annotate("error", f"DeepSeek 调用失败（模型 {MODEL}）：{reason} —— 改产出降级精选")
        print("→ 改产出降级精选（机械提取，未编辑加工）")
        return _write_output(build_fallback_digest(date_str, reason), date_str)
    print(f"响应 {len(raw)} 字符")

    body = extract_digest(raw)
    problems = validate_digest(body)
    if problems:
        # 明确报错，不静默落盘半成品
        print("WARNING: 精选体检未通过 —— " + "；".join(problems))
        gh_annotate("warning", "精选体检未通过：" + "；".join(problems))
    else:
        print("体检通过")

    return _write_output(body, date_str)


if __name__ == "__main__":
    sys.exit(main())
