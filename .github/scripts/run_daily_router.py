#!/usr/bin/env python3
"""自动日报路由 — 用 DeepSeek V4 Flash 跑 daily-router 三层漏斗。

纯标准库(urllib + json + re),运行时读取 AI-HOT / X-Tweets / TrendRadar,
调用 DeepSeek API,产出 _路由/YYYY-MM-DD.md 并更新 _选题池.md。

环境变量:
  DEEPSEEK_API_KEY   — API Key(必需)
  ROUTER_MODEL        — 模型(默认 deepseek-flash = V4.1 Flash)
  TODAY_OVERRIDE      — 指定日期(YYYY-MM-DD,不设则用北京时间今天)
  ROUTER_DRY_RUN      — 若设为 "1" 则只预览不写文件
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta

# 选题池行从路由日志确定性提取（相对导入，脚本与提取器同目录）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_topic_pool import dedupe_topics, parse_route_log as extract_topics, to_pool_row  # noqa: E402

BEIJING = timezone(timedelta(hours=8))
MODEL = os.environ.get("ROUTER_MODEL", "deepseek-flash")
API_BASE = "https://api.deepseek.com/v1/chat/completions"
ROUTE_DIR = os.environ.get("ROUTE_OUT_DIR", "_路由")
TOPIC_FILE = os.environ.get("TOPIC_FILE", "_选题池.md")
VIEWPOINT_FILE = os.environ.get("VIEWPOINT_FILE", "_观点.md")
DRY_RUN = os.environ.get("ROUTER_DRY_RUN", "") == "1"
# 输出预算。模型输出上限受 API 侧限制（设过头会整个请求 400），所以不靠"加大
# max_tokens"解决截断，而是靠**结构上省预算**：选题池表格行改由脚本从路由日志
# 确定性提取，模型不再重复生成一份 POOL_UPDATES（那正是被截断掉的部分）。
MAX_TOKENS = int(os.environ.get("ROUTER_MAX_TOKENS", "8192"))

# ── 路由规则(从 daily-router SKILL.md 精简) ──────────────────────────

ROUTER_SYSTEM_PROMPT = """你是一个财经×AI 内容路由助手。你的任务是对每天的四大信息源做三层漏斗筛选，把值得写公众号文章的选题输出到路由日志，并更新选题池。

## 第一层筛选：内容锚定（四个锚点，命中一个即通过）

| 锚点 A: AI | 大模型/ChatGPT/Claude/Agent/智能体/算力/芯片/数据中心/GPU/AI 政策/监管/伦理/有产业影响的 AI 应用 |
| 锚点 B: 金融 | 利率/央行/货币政策/资产价格/做空/暴跌/企业财报/估值/IPO/融资/利润/银行/杠杆/信贷/泡沫/崩盘 |
| 锚点 C: 金融史视角 | 周期/泡沫/危机/制度变迁/群体非理性/叙事传播/产业转移/技术扩散/中国特殊性 |
| 锚点 D: 高传播叙事 | 民族情绪/跨平台共振(3+)/破圈传播力/可接金融史接口。需命中至少两条才保留 |
硬丢弃: 纯体育/纯娱乐/纯技术工具/纯App更新/纯论文benchmark/纯学术无应用故事

## 第二层筛选：框架适配（八本标尺书，至少一本能讲出 ≥500 字独特分析）
《叙事经济学》(希勒)、《穷查理宝典》(芒格)、《思考快与慢》(卡尼曼)、《明朝那些事儿》、《聪明的投资者》(格雷厄姆)、《巴菲特致股东的信》、《文明现代化价值投资与中国》(李录)、《全球视野下的投资机会》(时寒冰)

## 第三层筛选：传播价值（五标尺各0/1分）
认知冲突(反直觉) / 叙事新鲜度(刚萌芽) / 情绪张力(恐惧/愤怒/惊讶) / 解释空间(需翻译成普通人能懂) / 关联广度(能串到知识库里的节点)
≥4分 → ⭐高优先级  |  2-3分 → 普通  |  ≤1分 → 丢弃

## 交叉检查
- 跟选题池现有选题对比，同一叙事线 → 输出 "更新现有选题"
- 两条⭐选题属同一主题线 → 标注 merge_hint
- 3条以上跨天独立信号 → 标注跨天信号

## X-Tweets 特殊处理
X 博主的推文不是经过编辑的新闻摘要。英文推文（含翻译）中可能有隐晦的市场信号——投资人说"散户觉得暴跌是飞刀但我觉得是长期持有机会"这种，需要你解读成可路由的信号。不是每条推文都值得路由，只提取跟 AI/金融/产业明确相关的。

## FollowBuilders 特殊处理
FollowBuilders 追踪 26 位 AI builder（Karpathy、Sam Altman、Swyx 等）的 X 推文、Anthropic/Claude 官方博客、以及 6 档 AI 播客。内容全部是英文，聚焦 AI 产业前沿（模型发布、产品思路、技术趋势、行业判断）。处理规则：
- 推文信号：关注行业级判断（"we're seeing X trend"）而非个人动态。多位 builder 同时讨论同一话题 → 标注跨源共振。
- 博客信号：官方博客文章通常是重大发布或技术深度文，天然属于锚点 A（AI）。只要有具体产品或架构决策 → 默认进入路由。
- 播客信号：已有 DeepSeek 中文摘要（标注 📌），把摘要当「精炼后的信号」来路由。摘要中提到跟锚点 B/C（金融/金融史）交叉的内容，优先提取。
- 注意：FollowBuilders 的 AI 浓度天然很高，需要你比 AI HOT 更严格地执行第二层（框架适配）和第三层（传播价值）——纯技术讨论、benchmark 对比、无产业影响的小工具更新，即使来自 Karpathy 也应该丢弃。

## 利率史素材
利率/央行/货币政策条目永远保留。标注 "💰 利率史素材"。

## 观点信号（仅当上下文提供「我的既有判断」段落时执行）
对每条进入路由日志的选题（⭐ 和普通都要），对照「我的既有判断」表逐条判断：
- 印证 V几：支持某条既有判断 → 备注"可作为 V几 的追踪证据"
- 挑战 V几：与某条判断冲突 → 单独高亮。挑战不降权反而提权——要么是"我错了"类绝佳选题，要么应触发观点修正
- 无关：不涉及任何既有判断
如果上下文中没有「我的既有判断」段落，省略所有观点信号字段，其余照常。

---

## 输出格式

请严格按以下格式输出，用 `===SECTION===` 分隔三个部分：

===ROUTE_LOG===
完整的路由日志 Markdown，格式如下：
```markdown
# 日报路由 · YYYY-MM-DD
输入: AI HOT(XX条) + TrendRadar(XX条) + X-Tweets(XX条) + FollowBuilders(XX条)
模式: {正常 / 周一模式 / 仅X源}

## ⭐ 高优先级选题(→ 选题池)

每条一个 `### NN.` 小节，字段固定如下（字段名不要改写）：

### 01. <选题标题>
- 来源: <具体来源和日期>
- 锚点: <命中的锚点>
- 框架: <标尺书 + 一句怎么用，50 字内>
- 传播: X/5(冲突/新鲜/情绪/解释/关联)
- 选题角度: <80-150字。为省输出预算，不要重复「钩子」里已经写过的话>
- merge_hint: {无 / 建议与"XX"合并为XX系列}
- 观点信号:{印证 V几,一句依据 / 挑战 V几,一句依据 / 无关}

(最多3条)

## 普通选题(→ 选题池)

**格式与高优先级完全一致**（`### NN.` 小节 + 同样 7 个字段，序号从 01 重新开始），
只是传播分 2-4 分、不占当日 ⭐ 名额。不要用表格。

## 🔄 更新现有选题
### 更新: <选题池里的选题名>
- 新信号: <新信息>
- 更新方式: <加到哪篇文章的哪个位置 / 等更多信号 / 具体操作>

## 💰 利率史素材

## 丢弃摘要
| 条目 | 原因 |

## 📊 本周跨天信号(仅在周一模式或有累积信号时)
```

**写完 `## ⭐ 高优先级选题` 与 `## 普通选题` 两个区是硬性要求**——选题池靠这两个区的
`### NN.` 小节确定性提取，缺一个区就等于当天不产出选题。宁可每条角度写短一点，
也要把两个区都写完。

**不要再输出 `===TOPIC_POOL_UPDATES===` 或 `===TOPIC_UPDATES===` 段**：选题池表格行
由脚本从上面的路由日志自动提取，你不需要（也不应该）重复生成一遍。所有信息写进
路由日志正文即可。

---

## 约束
- 高优先级 ≤3 条/天，普通选题 ≤5 条/天
- 丢弃条目列出理由,不要静默丢弃
- 利率史永远不丢
- 同一日期不重复路由
- merge_hint 要落到具体操作,不用模糊语言

现在开始对以下日报内容执行路由。"""


# ── helpers ────────────────────────────────────────────────────

def bao_date() -> str:
    ov = os.environ.get("TODAY_OVERRIDE", "").strip()
    return ov if ov else datetime.now(BEIJING).strftime("%Y-%m-%d")


def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def is_table_sep(line: str) -> bool:
    """判断是否为 Markdown 表格分隔行。
    兼容无 padding(|---|---|) 与有 padding(| --- | --- |) 两种写法——
    只要整行由 | - : 空格 组成且含至少一个 -，即视为分隔行。
    """
    s = line.strip()
    return s.startswith("|") and "-" in s and set(s) <= set("|-: ")


def load_viewpoints(path: str = "") -> str:
    """读取 _观点.md 第二层「当前核心判断」表格的数据行。

    任何失败(文件缺失/无该小节/表格无数据行/异常)返回 "" —
    router 降级为无观点模式,不阻塞路由。
    """
    try:
        text = read_file(path or VIEWPOINT_FILE)
        if not text:
            return ""
        m = re.search(r'^## 二、当前核心判断.*?\n(.*?)(?=^## |\Z)',
                      text, re.M | re.S)
        if not m:
            return ""
        rows = []
        for line in m.group(1).split("\n"):
            s = line.strip()
            if not s.startswith("|") or is_table_sep(s):
                continue
            if re.match(r'^\|\s*#\s*\|', s):  # 表头行
                continue
            rows.append(s)
        return "\n".join(rows)
    except Exception as e:
        print(f"WARNING: _观点.md 解析失败,降级为无观点模式: {e}")
        return ""


def list_routes(route_dir: str, days: int = 3) -> list[str]:
    """返回最近 N 天的路由日志路径列表。"""
    import glob as g
    files = sorted(g.glob(f"{route_dir}/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md"), reverse=True)
    return files[:days]


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
        # 关闭思考模式。官方文档：「思考模式默认打开，且 effort 默认为 high」——
        # 也就是说思维链会先占用输出预算，而 max_tokens 同时覆盖思维链与正文。
        # 本任务是**结构化提取**（输出格式已在 system prompt 里固定死），
        # 思维链没有增益，却会挤掉本该写进路由日志的预算（截断的另一成因）。
        # 注意：思考模式下 temperature 不生效（文档明示），关闭后它才真正起作用。
        "thinking": {"type": "disabled"},
        "temperature": 0.3,
    }).encode("utf-8")

    req = urllib.request.Request(
        API_BASE,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        # 把 API 的响应体带出来 —— "模型名不存在"和"额度耗尽"都是 4xx，
        # 但只有响应体说得清是哪一种（旧代码只抛裸 HTTPError，看不出原因）。
        try:
            detail = e.read().decode("utf-8", "replace")[:400]
        except Exception:  # noqa: BLE001
            detail = "(响应体读取失败)"
        raise RuntimeError(f"HTTP {e.code} {e.reason} — {detail}") from e
    content = data["choices"][0]["message"]["content"]
    if not content or not content.strip():
        raise RuntimeError("DeepSeek 返回了空内容 — 可能是模型不可用、Key 额度耗尽或服务端限流")
    return content


def parse_sections(output: str) -> dict[str, str]:
    """解析 ===SECTION=== 分隔的输出。"""
    sections = {}
    current = ""
    for line in output.split("\n"):
        m = re.match(r'^===(\w+)===$', line)
        if m:
            current = m.group(1)
            sections[current] = ""
        elif current:
            sections[current] += line + "\n"
    return {k: v.strip() for k, v in sections.items()}


def build_context(date_str: str) -> str:
    """构建传给 LLM 的上下文。"""
    parts = []

    # 当日报告
    aihot = read_file(f"AI-HOT/{date_str}.md")
    xtweets = read_file(f"X-Tweets/{date_str}.md")
    trendradar = read_file(f"TrendRadar/{date_str}.md")

    parts.append(f"=== 当日日期: {date_str} ===")
    parts.append("")

    if aihot:
        # 只传内容(去frontmatter),节省token
        lines = aihot.split("\n")
        body_start = next((i for i, l in enumerate(lines) if l.startswith("# ")), 0)
        parts.append("## AI HOT 日报\n" + "\n".join(lines[body_start:]))
    else:
        parts.append("## AI HOT: 今日无更新")

    if xtweets:
        lines = xtweets.split("\n")
        body_start = next((i for i, l in enumerate(lines) if l.startswith("# ")), 0)
        parts.append("## X 博主动态\n" + "\n".join(lines[body_start:]))
    else:
        parts.append("## X-Tweets: 今日无更新")

    if trendradar:
        lines = trendradar.split("\n")
        body_start = next((i for i, l in enumerate(lines) if l.startswith("# ")), 0)
        parts.append("## TrendRadar 热点\n" + "\n".join(lines[body_start:]))
    else:
        parts.append("## TrendRadar: 今日无更新")

    # FollowBuilders — AI builder 动态（推文+博客+播客）
    followbuilders = read_file(f"FollowBuilders/{date_str}.md")
    if followbuilders:
        lines = followbuilders.split("\n")
        body_start = next((i for i, l in enumerate(lines) if l.startswith("# ")), 0)
        parts.append("## FollowBuilders (AI Builders 动态)\n" + "\n".join(lines[body_start:]))
    else:
        parts.append("## FollowBuilders: 今日无更新")

    # 选题池
    topic_pool = read_file(TOPIC_FILE)
    if topic_pool:
        parts.append("\n=== 当前选题池 ===\n")
        parts.append(topic_pool)

    # 我的既有判断(观点信号参考) — 缺失时静默省略,降级为无观点模式
    viewpoints = load_viewpoints()
    if viewpoints:
        parts.append("\n=== 我的既有判断(观点信号参考) ===\n")
        parts.append("| # | 判断 | 形成日期 | 置信度 | 来源文章 |")
        parts.append("|---|------|---------|:---:|------|")
        parts.append(viewpoints)

    # 最近路由日志(去重用,只传日期行)
    recent = list_routes(ROUTE_DIR, days=3)
    if recent:
        parts.append("\n=== 最近 3 天路由日志(去重参考) ===\n")
        for f in recent:
            date_tag = os.path.basename(f).replace(".md", "")
            parts.append(f"- 已有路由: {date_tag}")

    return "\n".join(parts)


# ── main ────────────────────────────────────────────────────────

def detect_truncation(route_log: str) -> list[str]:
    """检测路由日志是否被输出预算截断。

    截断是选题池断供 6 周的根因，但旧代码对它**完全静默** —— 所以加了这层
    体检：缺区、末尾悬空都算异常，交由调用方打印并计入告警。
    """
    problems: list[str] = []
    if "高优先级选题" not in route_log:
        problems.append("缺「高优先级选题」区")
    if "普通选题" not in route_log:
        problems.append("缺「普通选题」区")
    # 末尾悬空：最后一行以这些结尾，说明句子没写完就被切了
    last = ""
    for line in reversed(route_log.splitlines()):
        if line.strip():
            last = line.strip()
            break
    if last.endswith(("，", "、", "：", ":", "——", "-", "（", "(", "和", "与", "的")):
        problems.append(f"末尾句子未写完（…{last[-24:]}）")
    return problems


def gh_annotate(level: str, message: str) -> None:
    """在 GitHub Actions 运行页顶部产生注解。

    本步骤是 `continue-on-error: true`，退出码再大也显示为成功 —— 路由连续
    多日失败而流水线全绿，就是这个原因。注解是唯一能让"每天都没跑成"被
    一眼看到的手段（`::warning::` / `::error::` 由 Actions 解析为注解）。
    非 Actions 环境（本地跑）会原样打印，不影响使用。
    """
    message = message.replace("\n", " ").replace("%", "%25").replace("\r", "%0D")
    print(f"::{level} title=日报路由::{message}", flush=True)


def main():
    date_str = bao_date()
    print(f"=== 日报路由 · {date_str} ===")
    print(f"模型: {MODEL}")

    # 构建上下文
    context = build_context(date_str)
    print(f"上下文约 {len(context)} 字符")

    # 调 DeepSeek —— 失败必须说清是 Key、模型名还是限流
    print("调用 DeepSeek API …")
    try:
        raw = call_deepseek(ROUTER_SYSTEM_PROMPT, context)
    except Exception as exc:  # noqa: BLE001 — 要原样上报原因
        reason = f"{type(exc).__name__}: {exc}"
        print(f"ERROR: DeepSeek 调用失败 —— {reason}")
        gh_annotate("error", f"DeepSeek 调用失败（模型 {MODEL}）：{reason} —— 当日无路由日志、选题池不更新")
        return 1
    print(f"响应 {len(raw)} 字符")

    # 解析
    sections = parse_sections(raw)
    route_log = sections.get("ROUTE_LOG", "").strip()
    topic_updates = sections.get("TOPIC_UPDATES", "").strip()

    # 清理 markdown 围栏
    if route_log.startswith("```"):
        route_log = re.sub(r'^```\w*\n?', '', route_log, count=1)
        route_log = re.sub(r'\n?```\s*$', '', route_log)
        route_log = route_log.strip()

    if not route_log:
        print("ERROR: 未解析出 ROUTE_LOG")
        gh_annotate("warning", "响应里没有 ===ROUTE_LOG=== 段，已把整个响应当作路由日志兜底")
        # 兜底：整个响应当作路由日志（选题池仍可从其中提取）
        route_log = raw

    # ── 截断体检（截断曾是静默的，这是 6 周无人发现的原因）──
    problems = detect_truncation(route_log)
    if problems:
        print("WARNING: 路由日志疑似被截断 —— " + "；".join(problems))
        gh_annotate("warning", "路由日志疑似被截断：" + "；".join(problems))

    # ── 从路由日志确定性提取选题池行 ──
    # 不再依赖模型的 ===TOPIC_POOL_UPDATES=== 段：路由日志正文会吃掉大部分
    # 输出预算，那段经常生成不出来（选题池断供 6 周的根因）。
    topics = extract_topics(route_log)
    pool_text = read_file(TOPIC_FILE)
    kept, skipped = dedupe_topics(topics, pool_text)
    print(f"从路由日志提取选题 {len(topics)} 条，去重后 {len(kept)} 条")
    for s in skipped:
        print(f"  跳过: {s['title'][:40]} — {s['skip_reason']}")
    if not topics:
        # 明确失败，不静默跳过
        print("ERROR: 路由日志中未提取到任何选题（两区都缺失或被截断）——选题池本次不更新")
        gh_annotate("error", "路由日志里提取不到任何选题（两区缺失或被截断）—— 当日选题池不会更新")

    if DRY_RUN:
        # 写文件避免 Windows GBK 终端编码问题
        with open("_router_dryrun_route.md", "w", encoding="utf-8") as f:
            f.write(route_log)
        with open("_router_dryrun_topics.md", "w", encoding="utf-8") as f:
            f.write("=== 提取到的选题池行 ===\n")
            f.write("\n".join(to_pool_row(t) for t in kept) or "(无)")
            f.write(f"\n\n=== TOPIC_UPDATES ===\n{topic_updates}")
        print("DRY_RUN: wrote _router_dryrun_route.md and _router_dryrun_topics.md")
        return 0

    # 写路由日志
    os.makedirs(ROUTE_DIR, exist_ok=True)
    route_path = os.path.join(ROUTE_DIR, f"{date_str}.md")
    with open(route_path, "w", encoding="utf-8") as f:
        f.write(route_log + "\n")
    print(f"OK: {route_path}")

    # 更新选题池
    update_topic_pool(kept, topic_updates, date_str)

    return 0


def update_topic_pool(topics: list[dict], updates: str, date_str: str):
    """把提取出的选题写入选题池（表格格式）。

    格式：
      ## 🔥 新进
      ### MM-DD（N 条）
      | 选题 | 钩子 | 角度 | 系列 |
      |------|------|------|------|
      | ⭐ 标题 | ... | ... | ... |

    插入逻辑：
      1. 找 `## 🔥` 标题
      2. 在 🔥 区内找或建 `### MM-DD` 子标题
      3. 在日期子标题下的表格分隔行后插入新行

    `topics` 为 extract_topic_pool.parse_route_log 解析出的结构化选题；
    表格行由 to_pool_row 生成，不再依赖模型的第二段输出。
    """
    existing = read_file(TOPIC_FILE)
    if not existing:
        print("WARNING: _选题池.md 不存在,跳过")
        return

    # ── 空操作提前返回 ──
    has_new = bool(topics)
    has_upd = bool(updates.strip()) and updates.strip() != "无"
    if not has_new and not has_upd:
        print("OK: 无新选题/更新项，选题池未修改")
        return

    new_rows = [to_pool_row(t) for t in topics] if has_new else []

    lines = existing.split("\n")

    # ── 取 MM-DD ──
    mmdd = date_str[-5:] if len(date_str) >= 10 else date_str

    # ── 定位 🔥 区 ──
    hot_start = -1
    next_section = -1
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("## 🔥"):
            hot_start = i
        elif hot_start >= 0 and s.startswith("## ") and not s.startswith("## 🔥"):
            next_section = i
            break

    if hot_start < 0:
        print("WARNING: 找不到 ## 🔥 区,跳过")
        return

    hot_end = next_section if next_section >= 0 else len(lines)

    # ── 解析表格行的辅助函数 ──
    def is_data_row(line: str) -> bool:
        s = line.strip()
        return s.startswith("|") and not set(s) <= set("|-: ") and "---" not in s

    # ── 插入新条目（表格格式）──
    if new_rows:
        date_marker = f"### {mmdd}"
        date_sub_idx = -1
        for i in range(hot_start, hot_end):
            if lines[i].strip().startswith(date_marker):
                date_sub_idx = i
                break

        if date_sub_idx >= 0:
            # 日期子标题已存在 → 在表格分隔行后插入，并把「（N 条）」改成实际行数
            sep_idx = -1
            in_date_table = False
            for j in range(date_sub_idx, hot_end):
                s = lines[j].strip()
                if s.startswith("### ") and j != date_sub_idx:
                    break  # 到了下一个日期组
                if s.startswith("|"):
                    in_date_table = True
                if in_date_table and set(s) <= set("|-: "):
                    sep_idx = j
                    break
            if sep_idx >= 0:
                insert_at = sep_idx + 1
                for i, row in enumerate(new_rows):
                    lines.insert(insert_at + i, row)
                # 计数只数本日期组的数据行：必须先排除表头行
                # （`| 选题 | 钩子 | 角度 | 系列 |` 会被朴素判定当成数据行），
                # 并在遇到下一个 `###` / `##` 时停止，避免把后续日期组也算进来。
                total = 0
                for j in range(date_sub_idx + 1, len(lines)):
                    s = lines[j].strip()
                    if s.startswith("### ") or s.startswith("## "):
                        break
                    if is_data_row(s) and "选题" not in s.split("|")[1]:
                        total += 1
                lines[date_sub_idx] = re.sub(
                    r"（\d+\s*条）", f"（{total} 条）", lines[date_sub_idx]
                )
            else:
                print(f"WARNING: {date_marker} 下找不到表格分隔行，选题池未插入新行")
        else:
            # 日期子标题不存在 → 建日期组（### MM-DD + 表头 + 分隔行 + 数据行）
            date_line = f"### {mmdd}（{len(new_rows)} 条）"
            header = "| 选题 | 钩子 | 角度 | 系列 |"
            sep = "|------|------|------|------|"

            # 找到插入位置：🔥 区内第一个已有日期子标题之前，否则 🔥 区末尾
            insert_at = -1
            for j in range(hot_start + 1, hot_end):
                if lines[j].strip().startswith("### "):
                    insert_at = j
                    break
            if insert_at < 0:
                # 🔥 区没有日期子标题 → 插在 🔥 区提示行之后
                for j in range(hot_start + 1, hot_end):
                    if lines[j].strip().startswith(">"):
                        insert_at = j + 1
                        break
                if insert_at < 0:
                    insert_at = hot_start + 2

            # 插入：空行 → ### 日期 → 空行 → 表头 → 分隔 → 数据行 → 空行
            lines.insert(insert_at, "")
            lines.insert(insert_at, date_line)
            lines.insert(insert_at + 1, "")
            lines.insert(insert_at + 2, header)
            lines.insert(insert_at + 3, sep)
            for i, row in enumerate(new_rows):
                lines.insert(insert_at + 4 + i, row)
            lines.insert(insert_at + 4 + len(new_rows), "")

        print(f"OK: 选题池 🔥 新区 ({mmdd}) 新增 {len(new_rows)} 条")

    # ── 更新已有条目（跨区搜索表格行的选题列关键词）──
    if has_upd:
        updated_count = 0
        for ul in updates.strip().split("\n"):
            ul = ul.strip()
            if not ul.startswith("|"):
                continue
            parts = [p.strip() for p in ul.split("|")]
            if len(parts) < 3:
                continue
            keyword = parts[1].strip()
            new_signal = parts[2].strip()
            for i, line in enumerate(lines):
                s = line.strip()
                if not is_data_row(s):
                    continue
                # 检查选题列（第一列）是否包含关键词
                cols = [c.strip() for c in s.split("|")]
                if len(cols) < 3:
                    continue
                title_cell = cols[1]  # 去掉前后 | 后第一列
                if keyword in title_cell:
                    # 更新"最新信号"列（🌿 区第 2 列）
                    # 🔥 区没有"最新信号"列，只更新 🌿 区
                    section = ""
                    for j in range(i - 1, -1, -1):
                        sj = lines[j].strip()
                        if sj.startswith("## "):
                            section = sj
                            break
                    if "🌿" in section:
                        # 表格行格式: | ⭐ 标题 | 最新信号 | 角度 | 系列 |
                        # 替换第 2 列（最新信号）
                        if len(cols) >= 4:
                            cols[2] = f" {new_signal} "
                            new_line = "|" + "|".join(cols) + "|"
                            lines[i] = new_line
                            updated_count += 1
                    break
        if updated_count:
            print(f"OK: 已有选题更新 {updated_count} 条（🌿 区最新信号）")

    # ── 写回 ──
    with open(TOPIC_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    sys.exit(main())
