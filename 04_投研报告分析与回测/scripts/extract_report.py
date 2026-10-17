#!/usr/bin/env python3
"""券商研报文本抽取 + 骨架识别。

用途：把券商研报 PDF（或纯文本）转成结构化骨架，供上层 LLM 按
skill 的 5 类规则 / 10 段结构填充。本脚本只做确定性工作
（读文件、分页、关键词定位、数值正则抽取），不做判断。

用法:
    python3 extract_report.py report.pdf                 # 打印骨架（JSON）
    python3 extract_report.py report.pdf -o out.json     # 写文件
    python3 extract_report.py report.txt --text          # 纯文本输入
    python3 extract_report.py report.pdf --pages 1-20    # 只读部分页
"""
import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- 10 段结构
# 段名 -> 定位关键词（命中任一即认为是该段的起始行）
SECTION_KEYWORDS = {
    "summary":    ["投资要点", "核心观点", "投资逻辑", "报告摘要", "摘要"],
    "earnings":   ["业绩", "经营情况", "财务表现", "业绩回顾", "业绩点评"],
    "business":   ["业务", "主营业务", "分业务", "产品结构", "业务拆分"],
    "industry":   ["行业", "市场空间", "行业格局", "景气度", "赛道"],
    "financial":  ["财务", "盈利能力", "毛利率", "费用率", "现金流"],
    "valuation":  ["估值", "估值水平", "PE", "PB", "DCF", "目标价"],
    "risk":       ["风险", "风险提示", "风险因素"],
    "catalyst":   ["催化剂", "催化", "增长驱动", "看点"],
    "target":     ["目标价", "合理价值", "合理区间", "市值空间"],
    "rating":     ["评级", "投资建议", "首次覆盖", "维持", "上调", "下调"],
}

# ---------------------------------------------------------------- 数据规则
# 每个指标: (正则, 归一化函数名)
NUM = r"([\-\d,]+\.?\d*)"
YOY = r"(?:[（(]\s*([+\-]?\d+\.?\d*)\s*%\s*(?:YoY|同比)?\s*[)）])?"

DATA_PATTERNS = {
    "营收": [
        rf"营业(?:总)?收入[^\d\-\n]{{0,12}}{NUM}\s*(亿元|万元|百万元|万)",
        rf"营收[^\d\-\n]{{0,12}}{NUM}\s*(亿元|万元|百万元|万)",
        rf"收入[^\d\-\n]{{0,10}}{NUM}\s*(亿元|万元)元?{YOY}",
    ],
    "净利": [
        rf"(?:归母)?净利润[^\d\-\n]{{0,12}}{NUM}\s*(亿元|万元|百万元|万)",
        rf"净利[^\d\-\n]{{0,12}}{NUM}\s*(亿元|万元)元?",
    ],
    "毛利率": [rf"毛利率[^\d\-\n]{{0,8}}{NUM}\s*%"],
    "ROE": [rf"(?:ROE|净资产收益率)[^\d\-\n]{{0,8}}{NUM}\s*%"],
    "PE": [rf"\bPE\b[^\d\-\n]{{0,10}}{NUM}\s*[xX倍]"],
    "PB": [rf"\bP[B]\b[^\d\-\n]{{0,10}}{NUM}\s*[xX倍]"],
    "EPS": [rf"\bEPS\b[^\d\-\n]{{0,10}}{NUM}\s*元"],
    "负债率": [rf"(?:资产负债率|负债率)[^\d\-\n]{{0,8}}{NUM}\s*%"],
    "目标价": [rf"目标(?:价|价格)[^\d\-\n]{{0,10}}{NUM}\s*元"],
}

RATING_WORDS = ["买入", "增持", "持有", "中性", "减持", "卖出", "强烈推荐", "推荐"]
RISK_CATEGORIES = {
    "行业风险": ["行业", "竞争", "景气", "需求", "价格战", "渗透率"],
    "政策风险": ["政策", "补贴", "监管", "关税", "标准", "审批"],
    "公司风险": ["管理层", "客户", "产能", "供应链", "技术", "债务", "股权"],
    "估值风险": ["估值", "PE", "PB", "泡沫", "回调", "流动性"],
}


# ---------------------------------------------------------------- PDF 读取
def read_pdf(path: Path, pages: str | None = None) -> tuple[str, int]:
    try:
        import pdfplumber
    except ImportError:
        sys.exit(
            "缺少 pdfplumber。请安装：pip install --user pdfplumber\n"
            "或改用 --text 传入已抽取的 txt 文件。"
        )

    lo, hi = 1, 10**9
    if pages:
        m = re.match(r"(\d+)\s*-\s*(\d+)", pages)
        if m:
            lo, hi = int(m.group(1)), int(m.group(2))
        elif pages.isdigit():
            lo = hi = int(pages)

    chunks, total = [], 0
    with pdfplumber.open(str(path)) as pdf:
        total = len(pdf.pages)
        for i, page in enumerate(pdf.pages, start=1):
            if i < lo or i > hi:
                continue
            # 页码标记保留，便于引用回原文
            chunks.append(f"\n<<<PAGE {i}>>>\n" + (page.extract_text() or ""))
    return "\n".join(chunks), total


def read_file(path: Path, is_text: bool, pages: str | None) -> tuple[str, int]:
    if is_text or path.suffix.lower() in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore"), 0
    return read_pdf(path, pages)


# ---------------------------------------------------------------- 分段
def split_sections(text: str, window: int = 1600) -> dict:
    """按关键词定位 10 段的起始位置，截取到下一个段起始或 window 字符。"""
    lines = text.splitlines()
    hits = []  # (line_idx, section)
    seen = set()
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or len(stripped) > 40:   # 太长的行不是标题
            continue
        for sec, kws in SECTION_KEYWORDS.items():
            if sec in seen:
                continue
            if any(kw in stripped for kw in kws):
                hits.append((idx, sec))
                seen.add(sec)
                break

    hits.sort()
    sections = {}
    for n, (idx, sec) in enumerate(hits):
        end = hits[n + 1][0] if n + 1 < len(hits) else len(lines)
        body = "\n".join(lines[idx:end]).strip()
        sections[sec] = body[:window]
    return sections


# ---------------------------------------------------------------- 抽数据
def _clean_num(s: str) -> float:
    return float(s.replace(",", ""))


def extract_metrics(text: str) -> dict:
    out = {}
    for name, pats in DATA_PATTERNS.items():
        for pat in pats:
            m = re.search(pat, text)
            if not m:
                continue
            val = _clean_num(m.group(1))
            unit = ""
            for g in m.groups()[1:]:
                if g and not re.fullmatch(r"[+\-]?\d+\.?\d*", g):
                    unit = g
                    break
            out[name] = {"value": val, "unit": unit}
            # 邻近找同比
            tail = text[m.end(): m.end() + 60]
            yoy = re.search(r"([+\-]?\d+\.?\d*)\s*%.{0,6}(?:YoY|同比)", tail)
            if yoy:
                out[name]["yoy"] = float(yoy.group(1))
            break
    return out


def extract_ratings(text: str) -> dict:
    found = [w for w in RATING_WORDS if w in text]
    return {"candidates": found}


def extract_risks(text: str) -> dict:
    """按 4 类风险归类，返回每类命中的句子。"""
    risk_block = ""
    m = re.search(
        r"(?:风险提示|风险因素|风险提示及免责声明|投资风险)[^\n]{0,20}\n(.{0,1500})",
        text, re.S,
    )
    if m:
        risk_block = m.group(1)
    else:
        m = re.search(r"\n风险[^\n]{0,10}\n(.{0,1500})", text, re.S)
        risk_block = m.group(1) if m else text

    # 风险段常被后面章节污染，遇到下一个已知段标题就截断
    stop = re.search(
        r"\n(?:催化剂|催化\b|评级|投资建议|目标价|免责声明|分析师|附录|图表目录)",
        risk_block,
    )
    if stop:
        risk_block = risk_block[: stop.start()]

    result = {}
    for cat, kws in RISK_CATEGORIES.items():
        sent = re.findall(r"[^。；\n]{6,80}[。；]", risk_block)
        hit = [s.strip() for s in sent if any(kw in s for kw in kws)][:2]
        result[cat] = hit
    return result


def guess_meta(text: str, path: Path) -> dict:
    """探测标题/券商/日期等元信息（启发式，不求准确）。"""
    head = "\n".join(text.splitlines()[:40])
    date = re.search(r"(20\d{2})[年\-/\.]\s*(\d{1,2})[月\-/\.]", head)
    brokers = ["中金", "中信", "华泰", "国泰君安", "招商", "广发", "海通", "申万",
               "兴业", "东方", "天风", "长江", "光大", "民生", "国信", "东吴",
               "Morgan", "Goldman", "CICC", "UBS"]
    return {
        "file": path.name,
        "date": f"{date.group(1)}-{int(date.group(2)):02d}" if date else None,
        "broker": next((b for b in brokers if b in head), None),
        "title_guess": next(
            (l.strip() for l in text.splitlines() if 6 <= len(l.strip()) <= 40),
            None,
        ),
    }


# ---------------------------------------------------------------- 主流程
def build(text: str, path: Path, total_pages: int) -> dict:
    sections = split_sections(text)
    return {
        "meta": {**guess_meta(text, path), "pages_read": total_pages},
        "chars": len(text),
        "sections_found": sorted(sections.keys()),
        "sections_missing": [s for s in SECTION_KEYWORDS if s not in sections],
        "sections": sections,
        "metrics": extract_metrics(text),
        "ratings": extract_ratings(text),
        "risks": extract_risks(text),
        "_raw_chars": len(text),
    }


def main():
    ap = argparse.ArgumentParser(description="券商研报骨架抽取")
    ap.add_argument("path", help="PDF 或 txt 文件")
    ap.add_argument("-o", "--output", help="输出 JSON 路径（默认打印到 stdout）")
    ap.add_argument("--text", action="store_true", help="按纯文本读取")
    ap.add_argument("--pages", help="页范围，如 1-20 或 5")
    ap.add_argument("--full-text", action="store_true",
                    help="额外输出全文（默认不输出，省 token）")
    args = ap.parse_args()

    p = Path(args.path)
    if not p.exists():
        sys.exit(f"文件不存在: {p}")

    text, total = read_file(p, args.text, args.pages)
    data = build(text, p, total)
    if args.full_text:
        data["full_text"] = text

    blob = json.dumps(data, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(blob, encoding="utf-8")
        print(f"已写出 {args.output}")
        print(f"识别段落 {len(data['sections_found'])}/10，缺失: {data['sections_missing']}")
        print(f"抽到指标 {len(data['metrics'])} 个: {list(data['metrics'])}")
    else:
        print(blob)


if __name__ == "__main__":
    main()
