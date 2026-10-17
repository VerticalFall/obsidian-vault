#!/usr/bin/env python3
"""把 extract_report.py 的骨架渲染成 5 段速读摘要（研报速读 Skill 输出层）。

只做确定性拼装：数字来自抽取结果，判断（评级理由/投资逻辑）留给上层 LLM。

用法:
    python3 render_summary.py skeleton.json            # 打印 Markdown
    python3 render_summary.py skeleton.json -o out.md
    python3 render_summary.py skeleton.json --strict   # 缺项直接报错退出
"""
import argparse
import json
import sys
from pathlib import Path

SECTION_LABELS = {
    "summary": "投资要点", "earnings": "业绩", "business": "业务",
    "industry": "行业", "financial": "财务", "valuation": "估值",
    "risk": "风险", "catalyst": "催化剂", "target": "目标价", "rating": "评级",
}

MISS = "N/A"


def fmt_metric(m: dict) -> str:
    if not m:
        return MISS
    v, unit = m.get("value"), m.get("unit", "")
    s = f"{v:g}{unit}" if isinstance(v, (int, float)) else str(v)
    if "yoy" in m:
        s += f" ({m['yoy']:+.1f}% YoY)"
    return s


# 无显式单位的指标 -> 默认单位（原文以「%」或「x」出现，抽取时被剥掉了）
DEFAULT_UNIT = {
    "毛利率": "%", "ROE": "%", "负债率": "%",
    "PE": "x", "PB": "x", "EPS": "元", "目标价": "元",
}


def fmt_metric_typed(name: str, m: dict) -> str:
    """带默认单位兜底的格式化，避免出现「毛利率：25」这类歧义。"""
    if not m:
        return MISS
    m = dict(m)
    if not m.get("unit") and name in DEFAULT_UNIT:
        m["unit"] = DEFAULT_UNIT[name]
    return fmt_metric(m)


def smart_snippet(text: str, limit: int = 90) -> str:
    """去掉段标题行，抓第一句实质内容。"""
    if not text:
        return MISS
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) > 1 and len(lines[0]) <= 20:
        lines = lines[1:]
    body = "".join(lines)
    cut = body.find("。")
    s = body[: cut + 1] if 0 < cut < limit else body[:limit]
    return s.strip() or MISS


def build_markdown(d: dict) -> str:
    meta, m, risks = d.get("meta", {}), d.get("metrics", {}), d.get("risks", {})
    sec, ratings = d.get("sections", {}), d.get("ratings", {}).get("candidates", [])

    title = meta.get("title_guess") or meta.get("file", "研报")
    head = f"# 研报速读：{title}"
    sub = " · ".join(
        x for x in [
            meta.get("broker") and f"来源 {meta['broker']}",
            meta.get("date"),
            meta.get("pages_read") and f"{meta['pages_read']} 页",
        ] if x
    )

    # ---- 关键点 10 条（不足 10 条如实留 N/A，绝不编造）
    kp = [
        ("营收", fmt_metric(m.get("营收"))),
        ("净利", fmt_metric(m.get("净利"))),
        ("毛利率", fmt_metric_typed("毛利率", m.get("毛利率"))),
        ("ROE", fmt_metric_typed("ROE", m.get("ROE"))),
        ("估值", "PE " + fmt_metric_typed("PE", m.get("PE")) + " / PB " + fmt_metric_typed("PB", m.get("PB"))),
        ("业务", smart_snippet(sec.get("business", ""))),
        ("行业", smart_snippet(sec.get("industry", ""))),
        ("财务", smart_snippet(sec.get("financial", ""))),
        ("风险", " / ".join(k for k, v in risks.items() if v) or MISS),
        ("评级", " / ".join(ratings) or smart_snippet(sec.get("rating", ""), 40)),
    ]

    risk_lines = []
    for cat, hits in risks.items():
        if hits:
            risk_lines.append(f"- **{cat}**：{'；'.join(hits)}")
        else:
            risk_lines.append(f"- **{cat}**：⚠️ 原文未明确提及")

    val_parts = [
        f"当前 PE {fmt_metric_typed('PE', m.get('PE'))}",
        f"PB {fmt_metric_typed('PB', m.get('PB'))}",
        f"目标价 {fmt_metric_typed('目标价', m.get('目标价'))}",
        f"评级 {'/'.join(ratings) or MISS}",
    ]

    missing = d.get("sections_missing", [])

    md = [head]
    if sub:
        md.append(f"*{sub}*")
    md += ["", "## 【摘要】", smart_snippet(sec.get("summary", ""), 120)]
    md += ["", "## 【关键点】"]
    md += [f"{i}. **{k}**：{v}" for i, (k, v) in enumerate(kp, 1)]
    md += ["", "## 【估值】", " · ".join(val_parts)]
    md += ["", "## 【风险】"] + risk_lines
    md += ["", "## 【建议】"]
    md.append(
        " · ".join(x for x in [
            "/".join(ratings) or "评级原文未见",
            f"目标价 {fmt_metric_typed('目标价', m.get('目标价'))}",
            smart_snippet(sec.get("catalyst", ""), 60) if sec.get("catalyst") else "",
        ] if x and MISS not in x)
    )
    if missing:
        md += ["", f"> ⚠️ 原文未识别到段落：{', '.join(SECTION_LABELS[s] for s in missing)}"
                   "；对应项以 N/A 标注，未做任何编造填充。"]
    return "\n".join(md)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skeleton", help="extract_report.py 输出的 JSON")
    ap.add_argument("-o", "--output")
    ap.add_argument("--strict", action="store_true", help="有段缺失即退出非零")
    args = ap.parse_args()

    d = json.loads(Path(args.skeleton).read_text(encoding="utf-8"))
    if args.strict and d.get("sections_missing"):
        sys.exit(f"缺失段落: {d['sections_missing']}")

    md = build_markdown(d)
    if args.output:
        Path(args.output).write_text(md, encoding="utf-8")
        print(f"已写出 {args.output}（{len(md)} 字符）")
    else:
        print(md)


if __name__ == "__main__":
    main()
