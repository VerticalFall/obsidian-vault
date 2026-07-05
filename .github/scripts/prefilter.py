#!/usr/bin/env python3
"""
每日信息第一层预筛选 —— 从 AI HOT + TrendRadar 报告中快速锚定候选条目。

三层漏斗中,本脚本只做第一层(内容锚定)。第二三层(框架适配 + 传播价值)
需要 LLM 判断,由 daily-router skill 完成。

纯标准库实现,在 GitHub Action 中零依赖运行。

输出:
  05_系统维护/_路由/YYYY-MM-DD-初筛.md  ← 通过第一层的候选条目
  05_系统维护/_路由/YYYY-MM-DD.md        ← 每日完整路由报告(由 daily-router 补充)
"""

import os
import re
import sys
from datetime import datetime, timezone, timedelta

# ── 配置 ──────────────────────────────────────────

AIHOT_DIR = os.environ.get("AIHOT_DIR", "AI-HOT")
TR_DIR = os.environ.get("TR_DIR", "TrendRadar")
OUT_DIR = os.environ.get("OUT_DIR", "_路由")  # 在同步仓库内,随 pull 到本地

TZ_SHANGHAI = timezone(timedelta(hours=8))

# ── 锚点关键词 ────────────────────────────────────

ANCHOR_AI = [
    # 大模型
    r'\b(大模型|LLM|GPT|Claude|Fable|Opus|Sonnet|Haiku|Gemini|DeepSeek|千问|Qwen|Kimi|天工)',
    r'\b(模型发布|模型更新|开源权重|微调|预训练|RLHF)',
    # Agent
    r'\b(Agent|智能体|agent|自主|自动化工作流|Harness)',
    # 算力
    r'\b(算力|GPU|芯片|数据中心|电力|H100|B200|昇腾|英伟达|AMD|NVIDIA)',
    # 政策
    r'\b(网信办|监管|护栏|军事用途|AI 安全|AI 伦理)',
    # 应用
    r'\b(AI 编程|AI 医疗|AI 金融|AI 助手|数字人|AI 视频|AI 生成)',
]

ANCHOR_FINANCE = [
    r'\b(利率|降息|加息|美联储|央行|货币政策|非农|CPI|通胀)',
    r'\b(暴跌|暴涨|大涨|重挫|崩盘|做空|爆仓|回调|反弹)',
    r'\b(IPO|上市|估值|融资|注资|增持|减持|回购|股息)',
    r'\b(银行|大额存单|国债|债券|收益率|杠杆|信贷)',
    r'\b(财报|利润|营收|亏损|ROI|资本开支)',
    r'\b(人民币|美元|汇率|外汇|黄金)',
]

ANCHOR_HISTORY = [
    r'\b(周期|泡沫|危机|恐慌|崩盘|衰退|萧条)',
    r'\b(制度|改革|变法|权力|监管|禁令)',
    r'\b(从众|恐慌性|情绪|非理性|误判)',
    r'\b(产业转移|出海|全球化|贸易战|关税|反倾销)',
    r'\b(郁金香|南海泡沫|1929|大萧条|次贷危机|互联网泡沫)',
]

ANCHOR_NARRATIVE = [
    # 中国制造 / 文化自信
    r'中国(制造|科技|空调|汽车|芯片|品牌|企业).*(出海|卖爆|火到|征服|优势)',
    r'(欧洲|美国|日本|全球).*(依赖|抢购|靠|离不开).*中国',
    r'(巴黎|法国|欧洲).*(空调|中国制造)',
    # 跨平台共振信号(≥3 平台)
    r'微博.*百度.*抖音|抖音.*B站.*知乎|贴吧.*B站.*微博',
    # 民族情绪
    r'中国(男篮|足球|体育).*(惨败|不敌|被.*击败)',
    r'(国产|自主).*(替代|崛起|突破)',
]

# ── 硬丢弃关键词 ──────────────────────────────────

HARD_DROP = [
    r'^[🎮⚽️🏀🏈⚾️🎾🏐🏉🥊🎱🏓🏸🏒🏑🥅🏋️‍♂️🤸‍♂️⛷️🏂🏄‍♂️🏊‍♂️🚴‍♂️].*(比赛|赛|决赛|晋级|淘汰|夺冠|冠军|联赛|杯|公开赛)',
    r'(无缘|晋级|夺冠|冠军|淘汰).*(八强|四强|决赛|半决赛|32 强)',
    r'(C罗|梅西|詹姆斯|库里|王楚钦|孙颖莎).*(比赛|决赛|晋级|得分)',
    r'^.*(纯.*论文|benchmark|基准测试|刷分)(?!.*产业|应用|产品)',
    r'(v\d+\.\d+\.\d+|版本发布|修.*bug|小版本|补丁).*发布',
]

# ── 利率史特殊通道(永远不过滤) ───────────────────

RATE_SPECIAL = [
    r'\b(利率|降息|加息|央行利率|联邦基金利率|基准利率|LPR|存款利率|贷款利率)',
    r'\b(大额存单|国债收益率|收益率曲线|期限利差|倒挂)',
]

# ── 解析函数 ──────────────────────────────────────

def extract_aihot_items(path):
    """从 AI HOT markdown 提取所有条目,返回 [{title,summary,section,idx}]"""
    if not os.path.exists(path):
        return []
    text = open(path, encoding='utf-8').read()
    items = []
    current_section = ""
    # AI HOT 条目格式: "N. **标题** — 来源\n   摘要..."
    for m in re.finditer(
        r'(?:^|\n)(\d+)\.\s+\*\*(.+?)\*\*\s*—\s*(.+?)(?:\n|$)'
        r'(.*?)(?=\n\d+\.\s+\*\*|\n##\s|\n---\s|\Z)',
        text, re.S
    ):
        idx = int(m.group(1))
        title = m.group(2).strip()
        source = m.group(3).strip()
        summary = m.group(4).strip()[:300]
        # 确定所属板块
        sec_m = re.search(r'##\s+[📦🧠🏭📄💡]\s+(.+)', text[:m.start()])
        if sec_m:
            current_section = sec_m.group(1).strip()
        items.append({
            "title": title,
            "source": f"AI HOT / {source}",
            "section": current_section,
            "idx": idx,
            "summary": summary,
        })
    return items


def extract_tr_items(path):
    """从 TrendRadar markdown 提取热榜条目,返回 [{title,source,section}]"""
    if not os.path.exists(path):
        return []
    text = open(path, encoding='utf-8').read()
    items = []
    # 话题组 + 条目: "### 🔥 话题名(N 条)" → "1. [标题](url) `平台 · #排名 · 时间`"
    current_topic = ""
    for line in text.splitlines():
        topic_m = re.match(r'###\s+[🔥📈📌].*\*\*(.+?)(?:（\d+\s*条）)?\*\*', line)
        if topic_m:
            current_topic = topic_m.group(1).strip()
            continue
        item_m = re.match(r'(\d+)\.\s+\[(.+?)\]\((.+?)\)\s+`(.+?)`', line)
        if item_m:
            meta = item_m.group(4)
            platform = meta.split('·')[0].strip() if '·' in meta else meta.strip()
            items.append({
                "title": item_m.group(2),
                "source": f"TrendRadar / {platform}",
                "section": current_topic,
                "idx": int(item_m.group(1)),
            })
    return items


def match_anchors(title, summary=""):
    """返回命中的锚点列表和是否有利率信号"""
    text = title + " " + summary
    anchors = []
    for pattern in ANCHOR_AI:
        if re.search(pattern, text):
            anchors.append("AI")
            break
    for pattern in ANCHOR_FINANCE:
        if re.search(pattern, text):
            anchors.append("金融")
            break
    for pattern in ANCHOR_HISTORY:
        if re.search(pattern, text):
            anchors.append("金融史")
            break
    for pattern in ANCHOR_NARRATIVE:
        if re.search(pattern, text):
            anchors.append("高传播叙事")
            break
    is_rate = any(re.search(p, text) for p in RATE_SPECIAL)
    is_hard_drop = any(re.search(p, text) for p in HARD_DROP)
    return anchors, is_rate, is_hard_drop


# ── 主流程 ────────────────────────────────────────

def main():
    today = os.environ.get("TODAY")
    if not today:
        today = datetime.now(TZ_SHANGHAI).strftime("%Y-%m-%d")

    aihot_path = os.path.join(AIHOT_DIR, f"{today}.md")
    tr_path = os.path.join(TR_DIR, f"{today}.md")

    aihot_items = extract_aihot_items(aihot_path)
    tr_items = extract_tr_items(tr_path)

    print(f"[初筛] AI HOT: {len(aihot_items)} 条, TrendRadar: {len(tr_items)} 条")

    # 逐条过第一层
    candidates = []
    rate_candidates = []
    dropped = []
    seen = set()

    for it in aihot_items + tr_items:
        key = it["title"][:80]
        if key in seen:
            continue
        seen.add(key)
        anchors, is_rate, is_hard = match_anchors(it.get("title", ""), it.get("summary", ""))
        if is_hard:
            dropped.append((it["title"][:60], "硬丢弃(体育/纯技术/版本更新)"))
        elif not anchors and not is_rate:
            dropped.append((it["title"][:60], "无锚点命中"))
        else:
            entry = {**it, "anchors": anchors}
            if is_rate:
                rate_candidates.append(entry)
            if anchors:
                candidates.append(entry)

    # 写入初筛结果
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f"{today}-初筛.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# 初筛结果 · {today}\n\n")
        f.write(f"**输入**: AI HOT {len(aihot_items)} 条 + TrendRadar {len(tr_items)} 条\n")
        f.write(f"**通过第一层**: {len(candidates)} 条候选 + {len(rate_candidates)} 条利率素材\n")
        f.write(f"**丢弃**: {len(dropped)} 条\n\n")
        f.write("> ⚠️ 本文件由 Layer 1 预筛选脚本自动生成。\n")
        f.write("> 第二三层(框架适配 + 传播价值)请运行 daily-router skill。\n\n")

        f.write("## 候选条目(通过第一层,待第二三层分析)\n\n")
        for it in candidates:
            f.write(f"- **{it['title'][:100]}**\n")
            f.write(f"  - 来源: {it.get('source','')}  |  锚点: {', '.join(it.get('anchors',[]))}\n")
            f.write(f"  - 板块: {it.get('section','')}\n\n")

        if rate_candidates:
            f.write("## 💰 利率史素材(特殊通道,永远保留)\n\n")
            for it in rate_candidates:
                f.write(f"- **{it['title'][:100]}**  ({it.get('source','')})\n")

        f.write(f"\n## 丢弃条目({len(dropped)}条)\n\n")
        f.write("| 条目 | 原因 |\n|------|------|\n")
        for title, reason in dropped:
            f.write(f"| {title} | {reason} |\n")

    print(f"OK: {out_path} ({len(candidates)} 候选, {len(rate_candidates)} 利率素材)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
