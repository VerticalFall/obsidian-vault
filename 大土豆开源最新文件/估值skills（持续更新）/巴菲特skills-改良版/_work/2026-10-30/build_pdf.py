# -*- coding: utf-8 -*-
import sys, subprocess, re
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model_config import COMPANIES

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / "输出" / "A股"
DATE = "2026-10-30"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

CSS = """
@page { size: A4 landscape; margin: 9mm; }
* { box-sizing: border-box; }
body { margin:0; font-family:"Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif; color:#1F2933; font-size:8.6pt; line-height:1.42; }
.page { width:279mm; height:192mm; position:relative; page-break-after:always; overflow:hidden; padding:0 1mm; }
.page:last-child { page-break-after:auto; }
.kicker { font-size:7.5pt; color:#5B6770; letter-spacing:1.2px; text-transform:uppercase; }
h1 { font-size:23pt; margin:2mm 0 1mm; color:#1F2933; letter-spacing:-.4px; }
h1 span { color:#2F6B4F; font-size:15pt; font-weight:600; margin-left:2mm; }
.sub { color:#5B6770; font-size:10pt; margin-bottom:3mm; }
h2 { font-size:13pt; color:#2F6B4F; margin:0 0 2.5mm; padding-bottom:1.4mm; border-bottom:1.5px solid #E8E2D5; }
h3 { font-size:9.5pt; color:#8C6D5A; margin:0 0 1.5mm; }
h4 { font-size:8.8pt; color:#2F6B4F; margin:0 0 1mm; }
p { margin:0 0 1.8mm; }
ul { margin:0 0 2mm 4mm; padding:0; }
li { margin:0 0 1.2mm; }
.small { font-size:7.6pt; color:#5B6770; }
.tiny { font-size:6.8pt; color:#5B6770; }
.card { background:#FBF8F1; border:1px solid #E8E2D5; border-radius:2mm; padding:3.2mm 3.6mm; }
.conclusion { background:#2F6B4F; color:#fff; border-radius:2mm; padding:3.6mm 4.2mm; font-size:11pt; font-weight:600; margin:2mm 0 3mm; }
.metrics { display:grid; grid-template-columns:repeat(4,1fr); gap:2.5mm; margin-bottom:3mm; }
.metric { background:#fff; border:1px solid #E8E2D5; border-radius:2mm; padding:2.8mm 3mm; }
.metric .k { font-size:7.4pt; color:#5B6770; }
.metric .v { font-size:14pt; font-weight:700; color:#1F2933; margin-top:.8mm; }
.metric .n { font-size:6.9pt; color:#5B6770; margin-top:.8mm; }
.grid2 { display:grid; grid-template-columns:1fr 1fr; gap:4mm; }
.grid3 { display:grid; grid-template-columns:1fr 1fr 1fr; gap:3.5mm; }
table { width:100%; border-collapse:collapse; font-size:7.9pt; }
th { background:#EFE8D8; color:#5B4A3A; text-align:left; padding:1.3mm 1.5mm; border:1px solid #D9D2C5; font-weight:600; }
td { padding:1.2mm 1.5mm; border:1px solid #D9D2C5; vertical-align:top; }
tr:nth-child(even) td { background:#FAF8F2; }
.num { text-align:right; white-space:nowrap; }
.center { text-align:center; }
.pos { color:#2F6B4F; font-weight:600; }
.neg { color:#B23A2E; font-weight:600; }
.warn { color:#C9A227; font-weight:600; }
.tag { display:inline-block; font-size:6.4pt; padding:.2mm 1.2mm; border-radius:1mm; margin-right:1mm; font-weight:600; }
.fact { background:#E8EFE9; color:#2F6B4F; }
.calc { background:#EAF1F8; color:#1A5C9E; }
.assume { background:#FBF3D9; color:#8A6A12; }
.judge { background:#F3E8E5; color:#8C3B2E; }
.qgrid { display:grid; grid-template-columns:1fr 1fr; gap:2.8mm; }
.q { border:1px solid #E8E2D5; border-radius:2mm; padding:2.4mm 3mm; background:#fff; }
.q p { font-size:7.9pt; margin:0; color:#2A333B; }
.q h4 { font-size:8.2pt; }
.formula { background:#F2F7FB; border-left:2.5mm solid #1A73E8; padding:2.6mm 3mm; font-family:Consolas,"Microsoft YaHei",monospace; font-size:7.8pt; color:#1F2933; margin:2mm 0; white-space:pre-line; }
.bull { border-top:2.5mm solid #2F6B4F; }
.bear { border-top:2.5mm solid #B23A2E; }
.neutral { border-top:2.5mm solid #C9A227; }
.chain { display:flex; align-items:center; gap:1.8mm; margin:1mm 0 3mm; }
.step { flex:1; background:#fff; border:1px solid #E8E2D5; border-radius:1.5mm; padding:2.2mm 2mm; text-align:center; }
.step .n { display:inline-block; width:5.2mm; height:5.2mm; line-height:5.2mm; border-radius:50%; background:#2F6B4F; color:#fff; font-size:7pt; font-weight:700; }
.step .s { font-size:7.6pt; font-weight:600; margin-top:.8mm; }
.step .d { font-size:6.6pt; color:#5B6770; margin-top:.5mm; }
.arrow { color:#C9A227; font-size:10pt; font-weight:700; }
.score { display:flex; align-items:center; gap:2mm; margin:1.6mm 0; }
.score .lbl { width:24mm; font-size:7.8pt; color:#1F2933; }
.score .bar { flex:1; height:3.2mm; background:#EDE8DC; border-radius:1.6mm; overflow:hidden; }
.score .fill { height:100%; background:#2F6B4F; }
.score .v { width:6mm; text-align:right; font-size:7.4pt; color:#5B6770; }
.footer { position:absolute; left:0; right:0; bottom:0; border-top:1px solid #E8E2D5; padding-top:1.2mm; display:flex; justify-content:space-between; font-size:6.6pt; color:#5B6770; }
.pnum { position:absolute; right:0; bottom:0; font-size:6.6pt; color:#5B6770; }
.note { background:#FBF7EA; border:1px solid #E8E2D5; padding:2.2mm 2.8mm; font-size:7.2pt; color:#5B6770; border-radius:1.5mm; }
.center-title { text-align:center; margin:0 0 2mm; }
.center-title h2 { border:none; margin:0; }
"""


def fmt(v, n=2, pct=False):
    if v is None:
        return "—"
    if pct:
        return f"{v:.{n}f}%"
    return f"{v:,.{n}f}"


def table(headers, rows, widths=None, cls="", header_cls=""):
    out = [f'<table class="{cls}">']
    if widths:
        out.append("<colgroup>" + "".join(f'<col style="width:{w}">' for w in widths) + "</colgroup>")
    out.append("<thead><tr>" + "".join(f'<th class="{header_cls}">{escape(str(h))}</th>' for h in headers) + "</tr></thead><tbody>")
    for row in rows:
        cells = []
        for i, v in enumerate(row):
            c = ""
            if isinstance(v, str) and v.startswith("#"):
                m = re.match(r"#(pos|neg|warn|center)(.*)", v)
                if m:
                    c, v = m.group(1), m.group(2)
            cells.append(f'<td class="{c}">{v}</td>')
        out.append("<tr>" + "".join(cells) + "</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def np_chart(c, w=1100, h=112):
    vals = c.net_profit + [c.net_profit_2026e]
    labels = c.years + ["2026E"]
    dps = c.dps + [c.dps_2026e]
    maxv = max(vals) * 1.12
    left, right, top, bottom = 42, 10, 14, 30
    plot_w = w - left - right
    plot_h = h - top - bottom
    step = plot_w / len(vals)
    barw = min(70, step * 0.42)
    out = [f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}px" xmlns="http://www.w3.org/2000/svg">']
    for frac in [0, .25, .5, .75, 1]:
        y = top + plot_h * (1 - frac)
        out.append(f'<line x1="{left}" y1="{y:.1f}" x2="{w-right}" y2="{y:.1f}" stroke="#E5DFD3" stroke-width="1" stroke-dasharray="4 5"/>')
        out.append(f'<text x="{left-4}" y="{y+3:.1f}" font-size="7.2" fill="#5B6770" text-anchor="end">{maxv*frac:,.0f}</text>')
    for i, (lab, v) in enumerate(zip(labels, vals)):
        cx = left + step * (i + .5)
        bh = v / maxv * plot_h
        col = "#2F6B4F" if lab != "2026E" else "#7FA8D9"
        out.append(f'<rect x="{cx-barw/2:.1f}" y="{top+plot_h-bh:.1f}" width="{barw:.1f}" height="{bh:.1f}" rx="3" fill="{col}"/>')
        out.append(f'<text x="{cx:.1f}" y="{top+plot_h-bh-3:.1f}" font-size="7.8" font-weight="bold" fill="#2F6B4F" text-anchor="middle">{v:,.0f}</text>')
        out.append(f'<text x="{cx:.1f}" y="{h-12}" font-size="7.6" fill="#5B6770" text-anchor="middle">{lab}</text>')
        out.append(f'<text x="{cx:.1f}" y="{h-2}" font-size="6.6" fill="#8C6D5A" text-anchor="middle">DPS {dps[i]:.2f}</text>')
    out.append("</svg>")
    return "".join(out)


def score_bars(items):
    return "".join(
        f'<div class="score"><div class="lbl">{k}</div><div class="bar"><div class="fill" style="width:{v/5*100:.0f}%"></div></div><div class="v">{v}/5</div></div>'
        for k, v in items
    )


def page(content, num, total=8):
    return f'<div class="page">{content}<div class="footer"><span>巴菲特框架研究 · {DATE} · 仅供研究记录</span><span>不构成投资建议</span></div><div class="pnum">{num} / {total}</div></div>'


def cover(c):
    scen = c.scenario_values
    metrics = [
        ("收盘价", f"¥{c.price:.2f}", f"市值 {c.market_cap:,.0f} 亿"),
        ("2026E PE", f"{c.pe_2026e:.1f}x", f"EPS ¥{c.eps_2026e:.2f}"),
        ("2026E 股息率", f"{c.dividend_yield_2026e*100:.1f}%", f"DPS ¥{c.dps_2026e:.2f}"),
        ("安全边际", f"{c.margin_of_safety*100:+.1f}%", f"基准 ¥{c.blended_value:.2f}"),
    ]
    metric_html = "".join(f'<div class="metric"><div class="k">{k}</div><div class="v">{v}</div><div class="n">{n}</div></div>' for k,v,n in metrics)
    scenario_rows = [
        ["悲观", f"¥{scen['悲观']:.2f}", f"{(scen['悲观']/c.price-1)*100:+.1f}%", {"600900.SH":"来水偏枯、利率上行","000001.SZ":"ROE 6.5%、资产质量恶化","601088.SH":"煤价回落、需求走弱"}[c.code]],
        ["#pos基准", f"#pos¥{c.blended_value:.2f}", f"#pos{(c.blended_value/c.price-1)*100:+.1f}%", {"600900.SH":"正常来水、利率稳定","000001.SZ":"ROE 7.5%、零售企稳","601088.SH":"中周期煤价、收购协同"}[c.code]],
        ["乐观", f"¥{scen['乐观']:.2f}", f"{(scen['乐观']/c.price-1)*100:+.1f}%", {"600900.SH":"来水偏丰、电价改革","000001.SZ":"ROE 8.5%、分红提升","601088.SH":"煤价高位、整合超预期"}[c.code]],
    ]
    key_rows = [
        ["估值方法 1", c.method1_name, f"¥{c.method1_value:.2f}"],
        ["估值方法 2", c.method2_name, f"¥{c.method2_value:.2f}"],
    ]
    if c.method3_value:
        key_rows.append(["估值方法 3", c.method3_name, f"¥{c.method3_value:.2f}"])
    key_rows += [
        ["综合基准", "加权", f"¥{c.blended_value:.2f}"],
        ["评级 / 置信度", c.rating, c.confidence],
    ]
    thesis = {
        "600900.SH": (
            ["六库联调、边际成本近零，现金流可预测性极高。",
             "2026–2030 分红承诺 ≥70%，2026E 股息率 3.1%。",
             "折旧到期与财务费用下降，利润有韧性。"],
            ["2026Q3 发电量 -14.9%，全年盈利有下修风险。",
             "净债务 2,735 亿，利率上行对估值杀伤大。",
             "电价受管制，电量增长有限，难以支撑高成长估值。"],
            "好资产，但 29.74 元已高于基准 27.59 元；等回调或利率下行，不追高。",
        ),
        "000001.SZ": (
            ["0.47 倍 PB 处历史低位，悲观预期已大部分定价。",
             "2026E 股息率 5.6%，分红率有提升空间。",
             "零售 AUM 4.39 万亿、CET1 11.26%，资产负债表不弱。"],
            ["ROE 8.8% 低于 COE 11.5%，价值创造为负。",
             "关注类 2.07%、逾期 1.59% 上升，拨备降至 214.75%。",
             "NIM 1.80% 仍在下行通道，规模难以完全对冲。"],
            "低估值已反映大部分悲观预期，但重估需要 ROE 企稳；现价偏高，等更低价或催化剂。",
        ),
        "601088.SH": (
            ["煤电路港航一体化，成本曲线左侧，抗周期能力强。",
             "1,335.98 亿收购 11 家并表，资源量与装机提升。",
             "2025 年分红率 79.1%，2026E 股息率 3.8%。"],
            ["煤价 448 元/吨处周期高位，盈利正常化空间大。",
             "电力毛利率 13.4%（-4.9pct），成本 +8.1%。",
             "负债率 40.8%、少数股东 969 亿，收购推高杠杆。"],
            "好资产，但现价接近乐观情景；周期高位不追，等煤价或估值回落。",
        ),
    }[c.code]
    bull, bear, verdict = thesis
    return page(f"""
      <div class="kicker">巴菲特框架研究 · A股 · 2026-10-30</div>
      <h1>{c.name}<span>{c.code}</span></h1>
      <div class="sub">{c.industry} · 价格日 2026-10-30 · 收盘 ¥{c.price:.2f} · 市值 {c.market_cap:,.0f} 亿元</div>
      <div class="conclusion">{c.conclusion}</div>
      <div class="metrics">{metric_html}</div>
      <div class="grid2" style="margin-top:1mm;">
        <div class="card">
          <h3>三情景每股价值</h3>
          {table(["情景","每股价值","相对现价","核心假设"], scenario_rows, ["13%","18%","14%","55%"])}
          <div class="small" style="margin-top:1.5mm;">基准价值为 {"三法" if c.method3_value else c.method1_name + " 与 " + c.method2_name} 的加权结果；“相对现价”= 价值/现价 − 1，与安全边际分母不同。</div>
        </div>
        <div class="card">
          <h3>估值交叉与结论</h3>
          {table(["项目","方法","结果"], key_rows, ["24%","28%","48%"])}
          <div class="small" style="margin-top:1.5mm;">安全边际：{c.margin_of_safety*100:+.1f}%；现价较基准{'高' if c.price>c.blended_value else '低'} {abs(c.price/c.blended_value-1)*100:.1f}%。若要求 20% 安全边际，对应价格约 ¥{c.blended_value*0.8:.2f}。</div>
        </div>
      </div>
      <div class="note" style="margin-top:2.5mm;">
        <span class="tag fact">事实</span>财务数据来自公司公告与东方财富 F10；<span class="tag calc">计算</span>估值由本模型完成；
        <span class="tag assume">假设</span>折现率、永续增长与正常化盈利为研究假设；<span class="tag judge">判断</span>评级与置信度为主观判断。
        所有数字均可追溯到 Excel 模型与“来源”页。
      </div>
      <h3 style="margin-top:3mm;">投资论点拆解</h3>
      <div class="grid3">
        <div class="card bull"><h4>多头论据</h4><ul>{''.join(f'<li>{x}</li>' for x in bull)}</ul></div>
        <div class="card bear"><h4>空头论据</h4><ul>{''.join(f'<li>{x}</li>' for x in bear)}</ul></div>
        <div class="card neutral"><h4>结论</h4><p>{verdict}</p><p class="small" style="margin-top:1mm;">评级：{c.rating}；置信度：{c.confidence}。</p></div>
      </div>
    """, 1)


def page_boundary(c):
    if c.code == "600900.SH":
        boundary = [
            ["价格日", "2026-10-30 收盘", "总市值", f"{c.market_cap:,.0f} 亿元"],
            ["最新财报", "2026 年半年报", "财务截止", "2026-06-30"],
            ["2026Q3", "仅发电量公告；财报未披露", "2026E", "模型估计"],
            ["总股本", f"{c.shares:,.2f} 亿股", "净债务", f"{c.net_debt:,.1f} 亿元"],
        ]
        circle = [
            "能理解：收入=发电量×电价；成本以折旧、财务费用为主，六库联调改变来水在梯级间的分配。",
            "能跟踪：月度/季度发电量、来水、电价、财务费用、资本开支、分红率。",
            "不擅长：精确预测来水与利率；因此用正常化 FCFF 与 DDM 区间，而不是单点预测。",
        ]
    elif c.code == "000001.SZ":
        boundary = [
            ["价格日", "2026-10-30 收盘", "总市值", f"{c.market_cap:,.0f} 亿元"],
            ["最新财报", "2026 年三季报", "财务截止", "2026-09-30"],
            ["2026Q3", "营收 1,031 亿；净利 391.86 亿", "2026E", "模型估计"],
            ["总股本", f"{c.shares:,.2f} 亿股", "BPS", f"¥{c.bps:.2f}"],
        ]
        circle = [
            "能理解：净利息收入=生息资产×NIM；加手续费，减信用成本与费用。",
            "能跟踪：NIM、不良率、关注类、逾期率、拨备覆盖率、CET1、零售 AUM。",
            "不擅长：精确判断零售信贷周期底部；因此用 RI/PB-ROE 区间，并给资产质量情景。",
        ]
    else:
        boundary = [
            ["价格日", "2026-10-30 收盘", "总市值", f"{c.market_cap:,.0f} 亿元"],
            ["最新财报", "2026 年三季报", "财务截止", "2026-09-30"],
            ["2026Q3", "营收 2,960.31 亿；净利 444.03 亿", "2026E", "模型估计"],
            ["总股本", f"{c.shares:,.2f} 亿股", "净债务", f"{c.net_debt:,.1f} 亿元"],
        ]
        circle = [
            "能理解：煤电路港航化一体化；煤炭是利润核心，电力/化工/运输是延伸与对冲。",
            "能跟踪：煤价、长协比例、产量/销量、单位成本、电价、电力毛利率、收购整合。",
            "不擅长：精确判断煤价周期顶部；因此用中周期 FCFF、DDM 与 PE 三法交叉。",
        ]
    defs = [
        ["FCFF", "企业自由现金流；EBIT×(1−t)+D&A−capex−ΔWC"],
        ["COE", "股权成本；无风险利率 + 股权风险溢价"],
        ["RI", "剩余收益；BPS+(ROE−COE)×BPS/(COE−g)"],
        ["安全边际", "1 − 现价 / 基准价值；正=折价，负=溢价"],
        ["正常化", "用中周期盈利/现金流替代单一年份，避免峰值或谷值失真"],
    ]
    dq = {
        "600900.SH": [
            ["价格 / 股本", "29.74 元；244.68 亿股", "行情与公告一致"],
            ["财报口径", "2026H1；2026Q3 未披露", "2026E 为模型估计"],
            ["一次性项目", "无明显异常", "来水与电价是主变量"],
            ["数据缺口", "Q3 财报、全年电量", "10 月三季报补全"],
        ],
        "000001.SZ": [
            ["价格 / 股本", "11.64 元；194.06 亿股", "行情与公告一致"],
            ["财报口径", "2026Q3；EPS 扣永续债利息", "不可用净利润/股本"],
            ["一次性项目", "无重大", "信用成本是主变量"],
            ["数据缺口", "零售不良生成率", "关注类/逾期可跟踪"],
        ],
        "601088.SH": [
            ["价格 / 股本", "51.99 元；216.89 亿股", "总市值含少数股东"],
            ["财报口径", "2026Q3；收购追溯调整", "2025 每股数据不可比"],
            ["一次性项目", "同一控制下合并", "比较期已重述"],
            ["数据缺口", "收购标的月度利润", "并表利润可跟踪"],
        ],
    }[c.code]
    chain = [("01","数据边界","价格/财报/股本"),("02","生意与护城河","八问"),("03","财务与分红","五年表"),
             ("04","两法估值","DCF/RI + DDM"),("05","情景与风险","安全边际")]
    chain_html = "".join(f'<div class="step"><div class="n">{n}</div><div class="s">{s}</div><div class="d">{d}</div></div>' + ('<div class="arrow">›</div>' if i < len(chain)-1 else '') for i,(n,s,d) in enumerate(chain))
    return page(f"""
      <h2>0. 数据边界、能力圈与定义</h2>
      <div class="grid2">
        <div>
          <h3>数据边界</h3>
          {table(["项目","内容","项目","内容"], boundary, ["20%","30%","20%","30%"])}
          <div class="note" style="margin-top:2.5mm;">
            <span class="tag fact">事实</span>价格、股本、财报数据为公开披露；<span class="tag assume">假设</span>2026E 为模型估计，不是公司指引。
            {"长江电力 2026Q3 财报尚未披露，2026E 依据 H1 财报 + Q3 发电量推算，误差可能较大。" if c.code=="600900.SH" else ""}
            {"平安银行 EPS 为扣除永续债利息后的归母口径；不要用净利润/总股本替代。" if c.code=="000001.SZ" else ""}
            {"中国神华 2026 年收购为同一控制下合并，比较期已追溯调整；2025 年每股数据与 2026 年不可直接比较。" if c.code=="601088.SH" else ""}
          </div>
        </div>
        <div>
          <h3>能力圈</h3>
          <ul>{''.join(f'<li>{x}</li>' for x in circle)}</ul>
          <h3>关键定义</h3>
          {table(["术语","定义"], defs, ["18%","82%"])}
        </div>
      </div>
      <h3 style="margin-top:3.5mm;">研究链条</h3>
      <div class="chain">{chain_html}</div>
      <div class="grid2" style="margin-top:1mm;">
        <div class="card"><h3>数据质量检查</h3>{table(["项目","读数","说明"], dq, ["24%","34%","42%"])}</div>
        <div class="card"><h3>本报告不做什么</h3>
          <ul>
            <li>不预测短期股价，不判断明天涨跌。</li>
            <li>不给出个性化买卖指令，不替代持牌顾问。</li>
            <li>不把单一年份的峰值或谷值当作正常化盈利。</li>
            <li>不把“低 PE / 低 PB”直接等同于便宜。</li>
          </ul>
        </div>
      </div>
    """, 2)


def page_business(c):
    qs = {
        "600900.SH": [
            ("1. 生意能理解吗？", "是。收入=发电量×上网电价；成本以折旧、财务费用为主。六库联调把来水在梯级间再分配，边际成本近零。"),
            ("2. 有护城河吗？", "有，但不是定价权。稀缺坝址、流域梯级权、输电消纳优先、近零边际成本；电价受管制。"),
            ("3. 能长久吗？", "大坝经济寿命 50–100 年，需求稳定；来水、利率、电价政策是外生变量。"),
            ("4. 资本回报如何？", "2024/2025 ROE 15.7%/15.9%，高杠杆放大。折旧到期与财务费用下降是近年利润增量。"),
            ("5. 增长来自哪里？", "乌白注入完成后，电量增长有限；看电价改革、辅助服务、抽蓄、绿电交易。"),
            ("6. 管理层是否可信？", "三峡集团控股；2026–2030 分红承诺 ≥70%。关注关联交易、资本开支是否稀释回报。"),
            ("7. 最大风险是什么？", "来水偏枯（2026Q3 发电量 -14.9%）、利率上行、电价下行、资本开支超预期。"),
            ("8. 估值是否合理？", "2026E PE 22.6x、股息率 3.1%；DCF 30.17、DDM 25.00，基准 27.59；现价 29.74，偏贵。"),
        ],
        "000001.SZ": [
            ("1. 生意能理解吗？", "是。净利息收入=生息资产×NIM，加手续费，减信用成本与费用；零售与对公两翼。"),
            ("2. 有护城河吗？", "弱护城河。平安集团渠道、零售品牌、科技投入；但产品同质化，定价权有限。"),
            ("3. 能长久吗？", "银行业长期存在；但息差下行、脱媒、零售风险周期会压制盈利能力。"),
            ("4. 资本回报如何？", "ROE 从 2022 年 12.36% 降至 2025 年 9.15%，2026E 8.8%，低于 COE 11.5%。"),
            ("5. 增长来自哪里？", "零售 AUM 4.39 万亿、私行 2.10 万亿；主动压降高风险个人贷款，对公补位。"),
            ("6. 管理层是否可信？", "平安集团控制，零售转型进入深水区；关注风险偏好、分红率、资本充足。"),
            ("7. 最大风险是什么？", "关注类 2.07%（+24bp）、逾期 1.59%（+10bp）、信用卡不良 2.15%、房地产敞口。"),
            ("8. 估值是否合理？", "0.47 PB、5.6% 前瞻股息率；RI 12.28、DDM 8.13，基准 11.03；现价 11.64，合理偏贵。"),
        ],
        "601088.SH": [
            ("1. 生意能理解吗？", "是。煤电路港航化一体化；煤炭是利润核心，电力/化工/运输是延伸与对冲。"),
            ("2. 有护城河吗？", "有。长协煤占比高、资源禀赋、自有铁路港口、一体化对冲；成本曲线左侧。"),
            ("3. 能长久吗？", "煤炭仍是中国基础能源，但长期需求见顶；资源寿命与一体化资产支持久期。"),
            ("4. 资本回报如何？", "2022 年高煤价 ROE 18.1%，2025 年 12.8%；周期波动大，分红率 79%。"),
            ("5. 增长来自哪里？", "1,335.98 亿收购集团 12 家资产、11 家并表；煤化工扭亏、电力装机 7,208 万千瓦。"),
            ("6. 管理层是否可信？", "国家能源集团控股；关联收购定价与整合是关键，分红承诺 2025–2027 ≥65%。"),
            ("7. 最大风险是什么？", "煤价回落、电力毛利率 13.4%（-4.9pct）、收购推高负债率至 40.8%、少数股东 969 亿。"),
            ("8. 估值是否合理？", "20x PE、3.8% 股息率；DCF 38.19、DDM 32.50、PE 39.00，基准 36.64；现价 51.99，昂贵。"),
        ],
    }[c.code]
    cards = "".join(f'<div class="q"><h4>{q}</h4><p>{a}</p></div>' for q,a in qs)
    canvas = {
        "600900.SH": [
            ["收入驱动", "发电量 × 上网电价；六库联调在梯级间再分配来水"],
            ["成本结构", "折旧约 45%、财务费用、运维；边际成本近零"],
            ["资本密度", "极高；大坝/机组，资本开支高峰已过"],
            ["周期性", "来水周期；电价与利率政策周期"],
            ["监管 / 竞争", "电价受管制；流域垄断，无直接竞争"],
            ["关键指标", "发电量、电价、财务费用、DPS"],
        ],
        "000001.SZ": [
            ["收入驱动", "生息资产 × NIM；加手续费与投资收益"],
            ["成本结构", "存款成本、信用成本、业务及管理费"],
            ["资本密度", "高；RWA 约束，CET1 11.26%"],
            ["周期性", "信用周期；零售不良滞后于宏观"],
            ["监管 / 竞争", "强监管；产品同质化，价格竞争激烈"],
            ["关键指标", "NIM、不良/关注/逾期、AUM、CET1"],
        ],
        "601088.SH": [
            ["收入驱动", "煤炭销量 × 价格；电力/运输/化工延伸"],
            ["成本结构", "自产煤成本、外购煤、运输、电力燃料"],
            ["资本密度", "高；矿井、铁路、港口、电厂"],
            ["周期性", "煤价与电价周期；电力部分对冲"],
            ["监管 / 竞争", "资源审批、长协、安全监管；寡头格局"],
            ["关键指标", "煤价、产量、单位成本、电力毛利"],
        ],
    }[c.code]
    moat = {
        "600900.SH": [("资源 / 牌照",5),("成本优势",5),("网络 / 渠道",3),("品牌 / 定价",2),("转换成本",4)],
        "000001.SZ": [("资源 / 牌照",4),("成本优势",2),("网络 / 渠道",4),("品牌 / 定价",3),("转换成本",3)],
        "601088.SH": [("资源 / 牌照",5),("成本优势",5),("网络 / 渠道",4),("品牌 / 定价",3),("转换成本",4)],
    }[c.code]
    return page(f"""
      <h2>1. 生意本质与八问</h2>
      <div class="small" style="margin-bottom:2.5mm;">用八个问题把“好生意”拆开：可理解、护城河、久期、资本回报、增长、管理层、风险、估值。</div>
      <div class="qgrid">{cards}</div>
      <div class="note" style="margin-top:2.5mm;">
        <b>一句话：</b>{"长江电力是“好资产 + 合理偏贵的价格”；护城河来自坝址与调度，不来自提价权。" if c.code=="600900.SH" else
        "平安银行是“低估值 + 低 ROE”的组合；0.47 倍 PB 不是错杀，而是对 ROE 下行的定价。" if c.code=="000001.SZ" else
        "中国神华是“好资产 + 周期高位 + 乐观价格”；一体化降低波动，但不能消除周期。"}
      </div>
      <div class="grid2" style="margin-top:3mm;">
        <div class="card"><h3>商业模式画布</h3>{table(["维度","内容"], canvas, ["22%","78%"])}</div>
        <div class="card"><h3>护城河评分（1–5）</h3>{score_bars(moat)}
          <div class="small" style="margin-top:2mm;">评分是研究判断，不是精确度量；5=极强，1=很弱。护城河强不等于当前价格便宜。</div>
        </div>
      </div>
    """, 3)


def page_financials(c):
    if c.code == "600900.SH":
        rows = [
            ["营业收入", "556.46","688.63","781.44","844.92","862.42","820.0","379.29"],
            ["归母净利", "262.73","237.26","272.45","324.96","345.03","322.0","147.56"],
            ["EPS（元）", "1.155","0.970","1.114","1.328","1.410","1.316","0.603"],
            ["ROE（%）", "14.9","11.6","12.7","15.8","16.0","14.6","6.55"],
            ["毛利率（%）", "62.1","57.1","57.8","59.1","61.7","58.0","57.9"],
            ["净利率（%）", "47.2","34.5","34.9","38.5","40.0","39.3","39.6"],
            ["资产负债率（%）", "42.1","55.7","62.9","60.8","58.3","58.0","59.4"],
            ["DPS（元）", "0.815","0.853","0.820","0.943","1.000","0.920","—"],
            ["分红率（%）", "70.6","88.0","73.6","71.0","70.9","70.0","—"],
            ["经营现金流", "—","—","—","—","605.63","—","241.28"],
            ["资本开支", "—","—","—","—","184.88","—","44.35"],
            ["FCF（经营− capex）", "—","—","—","—","420.75","—","196.93"],
        ]
        notes = [
            "2026H1 净利 +13.0%，主要来自来水偏丰、财务费用 -13.6%、折旧到期；但 Q3 发电量 -14.9%，全年大概率回落。",
            "2026E 净利 322 亿、EPS 1.316、DPS 0.92；对应 PE 22.6x、股息率 3.1%。",
            "经营现金流远高于净利，折旧是主要非现金项；FCF 约 420 亿，足以覆盖 70% 分红。",
            "净债务约 2,735 亿（含一年内到期非流动负债），是 EV 估值的关键扣减项。",
        ]
    elif c.code == "000001.SZ":
        rows = [
            ["营业收入", "1,693.83","1,798.95","1,646.99","1,466.95","1,314.42","1,350.0","1,031.0"],
            ["归母净利", "363.36","455.16","464.55","445.08","426.33","435.0","391.86"],
            ["EPS（元）", "1.73","2.20","2.25","2.15","2.07","2.24","1.94"],
            ["ROE（%）", "10.85","12.36","11.38","10.08","9.15","8.8","8.07"],
            ["净息差（%）", "2.74","2.75","2.38","1.87","1.78","1.80","1.80"],
            ["不良率（%）", "1.02","1.05","1.06","1.06","1.05","1.05","1.05"],
            ["拨备覆盖率（%）", "288.4","290.3","261.1","250.7","220.9","214.8","214.75"],
            ["核心一级资本（%）", "8.60","8.64","9.22","10.69","11.49","11.26","11.26"],
            ["DPS（元）", "0.228","0.285","0.719","0.608","0.596","0.650","0.249"],
            ["分红率（%）", "13.2","13.0","32.0","28.3","28.8","29.0","—"],
        ]
        notes = [
            "营收从 2022 年 1,799 亿降至 2025 年 1,314 亿，净利从 464.6 亿降至 426.3 亿；2026 年恢复正增长。",
            "NIM 1.80% 同比 +1bp，环比企稳；但 ROE 8.8% 仍低于 COE 11.5%。",
            "拨备覆盖率从 2024 年 250.7% 降至 214.75%，缓冲变薄；关注类 2.07%、逾期 1.59% 上升。",
            "CET1 11.26% 充足；分红率仅 29%，理论上有提升空间，但受资本与监管约束。",
        ]
    else:
        rows = [
            ["营业收入", "3,356.40","3,445.33","3,430.74","3,397.88","2,949.16","3,960.0","2,960.31"],
            ["归母净利", "500.84","696.48","596.94","558.05","528.49","565.0","444.03"],
            ["EPS（元）", "2.520","3.505","3.004","2.809","2.660","2.600","2.062"],
            ["ROE（%）", "13.6","18.1","14.9","13.5","12.8","12.0","8.81"],
            ["毛利率（%）", "32.9","39.0","35.9","34.1","35.1","35.0","35.0"],
            ["净利率（%）", "14.9","20.2","17.4","16.4","21.3","19.1","18.4"],
            ["资产负债率（%）", "26.6","26.1","24.1","25.7","33.2","40.8","40.8"],
            ["DPS（元）", "2.54","2.55","2.26","2.26","2.01","1.95","0.98"],
            ["分红率（%）", "100.8","72.8","75.2","80.5","79.1","75.0","—"],
            ["经营现金流", "—","—","—","—","750.59","—","927.0"],
            ["资本开支", "—","—","—","—","483.98","—","471.81"],
            ["FCF（经营− capex）", "—","—","—","—","266.61","—","455.19"],
        ]
        notes = [
            "2026Q3 净利 444.03 亿（+3.8%），扣非 +10.6%；煤炭稳健、电力承压、煤化工扭亏。",
            "2026E 净利 565 亿、EPS 2.60、DPS 1.95；对应 PE 20.0x、股息率 3.8%。",
            "2026 年收购 12 家标的、11 家并表，作价 1,335.98 亿；负债率从 33.2% 升至 40.8%，少数股东 969 亿。",
            "2026 9M 经营现金流 927 亿、capex 471.81 亿，FCF 455 亿；全年正常化 FCF 约 620 亿。",
        ]
    return page(f"""
      <h2>2. 五年财务与分红</h2>
      <div class="small" style="margin-bottom:2mm;">单位：亿元、元/股、%；2026E 为模型估计；最新列为 {"2026H1" if c.code=="600900.SH" else "2026Q3"}。</div>
      {table(["指标","2021","2022","2023","2024","2025","2026E","最新"], rows, ["22%","10.5%","10.5%","10.5%","10.5%","10.5%","10.5%","11%"])}
      <div class="grid2" style="margin-top:2.5mm;">
        <div class="card"><h3>关键观察</h3><ul>{''.join(f'<li>{x}</li>' for x in notes)}</ul></div>
        <div class="card"><h3>分红与资本配置</h3>
          <p><span class="tag fact">事实</span>{"2025 年 DPS 1.00 元，分红总额 244.68 亿，分红率 70.9%；2026–2030 承诺 ≥70%。" if c.code=="600900.SH" else
          "2025 年 DPS 0.596 元，分红率 28.8%；2026 中期 DPS 0.249 元。" if c.code=="000001.SZ" else
          "2025 年 DPS 2.01 元，分红总额 418.11 亿，分红率 79.1%；2025–2027 承诺 ≥65%。"}</p>
          <p><span class="tag judge">判断</span>{"分红是主要回报来源；70% 派息可持续，但增长有限。" if c.code=="600900.SH" else
          "分红率有提升空间，但 ROE 低于 COE，保留利润的边际价值为负。" if c.code=="000001.SZ" else
          "高分红对估值有支撑，但周期高点的高分红不可外推。"}</p>
        </div>
      </div>
      <div class="card" style="margin-top:2.2mm;padding:1.5mm 3mm 0;">
        <h3>归母净利与每股分红</h3>
        {np_chart(c, h=112)}
      </div>
    """, 4)


def page_management_method1(c):
    if c.code == "600900.SH":
        mgmt = [
            "控股股东三峡集团；2026–2030 年分红承诺 ≥70%，2025 年分红 244.68 亿、分红率 70.9%。",
            "乌东德/白鹤滩注入后，资本开支高峰已过；2026H1 capex 44.35 亿、财务费用 -13.6%。",
            "需要跟踪关联交易、电价机制、抽蓄/新能源投资是否稀释回报。",
            "判断：资本配置总体友好，但增长空间有限，分红是主要回报来源。",
        ]
        method_rows = [
            ["归一化 FCFF", "430 亿元", "2025 CFO 605.6 − capex 184.9 + 利息/营运资金调整"],
            ["WACC", "6.0%", "Rf 1.62% + 风险溢价；水电类低杠杆"],
            ["永续 g", "1.8%", "电量与电价长期温和增长"],
            ["企业价值 EV", "10,238 亿元", "FCFF/(WACC−g)"],
            ["减：净债务", "2,735 亿元", "含一年内到期非流动负债"],
            ["减：少数股东", "120 亿元", "2026H1"],
            ["股权价值", "7,383 亿元", "EV − 净债务 − 少数"],
            ["每股价值", "¥30.17", "/ 244.68 亿股"],
        ]
    elif c.code == "000001.SZ":
        mgmt = [
            "平安集团控股，零售转型进入深水区；2025 年分红率 28.8%，2026 中期 DPS 0.249 元。",
            "CET1 11.26% 充足；但 ROE 低于 COE，保留利润的边际价值为负，理论上应提高分红。",
            "关注管理层风险偏好、零售不良生成、对公房地产敞口。",
            "判断：资本配置中性，分红率有提升空间，但受资本与监管约束。",
        ]
        method_rows = [
            ["BPS", "¥24.56", "2026Q3 归母净资产 / 194.06 亿股"],
            ["可持续 ROE", "7.5%", "2026E 8.8%，考虑 NIM 与信用成本后下调"],
            ["COE", "11.5%", "Rf 1.62% + 银行股权风险溢价"],
            ["永续 g", "3.5%", "与资本补充、分红率相匹配"],
            ["RI 每股价值", "¥12.28", "BPS+(ROE−COE)×BPS/(COE−g)"],
            ["Justified PB", "0.50x", "(ROE−g)/(COE−g)"],
            ["PB 估值", "¥12.28", "BPS × Justified PB"],
        ]
    else:
        mgmt = [
            "国家能源集团控股；1,335.98 亿关联收购，12 家标的、11 家并表，200 亿配套募资。",
            "2026Q3 负债率 40.8%、少数股东 969 亿；财务费用 +49.8%，收购推高杠杆。",
            "分红承诺 2025–2027 ≥65%，2025 年分红率 79.1%。",
            "判断：外延扩张提升规模，但收购定价、整合与杠杆是资本配置的关键变量。",
        ]
        method_rows = [
            ["归一化 FCFF", "620 亿元", "2026E CFO − capex，按中周期煤价调整"],
            ["WACC", "8.0%", "周期资源股要求回报"],
            ["永续 g", "1.5%", "煤价长期通胀，低于名义 GDP"],
            ["企业价值 EV", "9,538 亿元", "FCFF/(WACC−g)"],
            ["减：净债务", "286 亿元", "2026Q3"],
            ["减：少数股东", "969 亿元", "2026Q3"],
            ["股权价值", "8,283 亿元", "EV − 净债务 − 少数"],
            ["每股价值", "¥38.19", "/ 216.89 亿股"],
        ]
    score = {
        "600900.SH": [
            ["分红纪律", "5", "70% 承诺；2025 年 70.9%"],
            ["再投资回报", "3", "乌白注入后稳定，新增投资待验证"],
            ["杠杆管理", "3", "净债务 2,735 亿；负债率 58%"],
            ["关联交易", "3", "集团资产注入，需看定价"],
            ["股东沟通", "4", "分红政策清晰、可预期"],
        ],
        "000001.SZ": [
            ["分红纪律", "3", "分红率 29%，低于同业"],
            ["再投资回报", "2", "ROE 8.8% < COE 11.5%"],
            ["杠杆 / 资本", "4", "CET1 11.26%，资本充足"],
            ["关联交易", "4", "平安集团协同，透明度尚可"],
            ["股东沟通", "3", "战略透明，执行待验证"],
        ],
        "601088.SH": [
            ["分红纪律", "4", "分红率 79%；承诺 ≥65%"],
            ["再投资回报", "3", "收购资产回报待验证"],
            ["杠杆管理", "2", "负债率 40.8%；财务费用 +49.8%"],
            ["关联交易", "2", "1,335.98 亿关联收购"],
            ["股东沟通", "3", "承诺明确，整合待观察"],
        ],
    }[c.code]
    return page(f"""
      <h2>3. 管理层与资本配置</h2>
      <ul>{''.join(f'<li>{x}</li>' for x in mgmt)}</ul>
      <h2 style="margin-top:3mm;">4. 估值方法一：{c.method1_name}</h2>
      <div class="grid2">
        <div>
          {table(["假设 / 步骤","数值","说明"], method_rows, ["26%","18%","56%"])}
        </div>
        <div class="card">
          <h3>计算逻辑</h3>
          <div class="formula">{"EV = FCFF / (WACC − g)\n股权价值 = EV − 净债务 − 少数股东权益\n每股价值 = 股权价值 / 总股本" if c.code!="000001.SZ" else "RI = BPS + (ROE − COE) × BPS / (COE − g)\nJustified PB = (ROE − g) / (COE − g)\nPB 估值 = BPS × Justified PB"}</div>
          <p><span class="tag calc">计算</span>结果：<b>¥{c.method1_value:.2f}</b>；现价 ¥{c.price:.2f}，相对{'溢价' if c.price>c.method1_value else '折价'} {abs(c.price/c.method1_value-1)*100:.1f}%。</p>
          <p><span class="tag assume">假设</span>{"FCFF 430 亿接近 2025 年 420.75 亿的自由现金流；未假设大规模新坝建设。" if c.code=="600900.SH" else
          "可持续 ROE 7.5% 低于 2026E 8.8%，已反映 NIM 与信用成本压力。" if c.code=="000001.SZ" else
          "FCFF 620 亿高于 2025 年 266.61 亿，反映 2026 年收购并表与煤价回升；与 2026 9M 年化 607 亿基本相当。"}</p>
          <p><span class="tag judge">判断</span>{"DCF 对 WACC/g 敏感，单点价值只作锚。" if c.code!="000001.SZ" else "RI 对 ROE/COE 极敏感；单点价值只作锚。"}</p>
        </div>
      </div>
      <h3 style="margin-top:3mm;">资本配置记分卡（1–5）</h3>
      <div class="grid2">
        <div>{table(["维度","评分","依据"], score, ["24%","12%","64%"])}</div>
        <div class="card"><h3>治理红旗</h3>
          <ul>
            {"<li>集团关联交易与资产注入定价是否公允。</li><li>抽蓄/新能源投资是否稀释 ROE。</li><li>电价管制下的资本开支纪律。</li>" if c.code=="600900.SH" else
             "<li>零售风险偏好是否再次放松。</li><li>分红率是否长期低于同业。</li><li>管理层稳定性与战略连续性。</li>" if c.code=="000001.SZ" else
             "<li>1,335.98 亿关联收购的定价与减值风险。</li><li>负债率与少数股东权益快速上升。</li><li>收购标的整合与协同兑现。</li>"}
          </ul>
          <p class="small">记分卡是研究判断，不是公司评级；评分低不必然意味着股价下跌。</p>
        </div>
      </div>
    """, 5)


def page_method2(c):
    if c.code == "600900.SH":
        method2 = [
            ["归一化 DPS", "¥1.00", "2025 年分红 1.00 元；2026–2030 承诺 ≥70%"],
            ["COE", "6.0%", "与 WACC 一致"],
            ["DDM g", "2.0%", "股息长期增长"],
            ["DDM 每股价值", "¥25.00", "DPS/(COE−g)"],
        ]
        sens = [["WACC \\ g", "1.2%", "1.5%", "1.8%", "2.1%", "2.4%"]]
        for w in [0.054, 0.058, 0.060, 0.062, 0.066]:
            row = [f"{w:.1%}"]
            for g in [0.012, 0.015, 0.018, 0.021, 0.024]:
                ev = 430 / (w - g)
                row.append(f"{(ev - c.net_debt - c.minority) / c.shares:.1f}")
            sens.append(row)
        cross = [
            "DCF ¥30.17 vs DDM ¥25.00：差距来自留存现金与再投资假设；两者各 50% 得基准 ¥27.59。",
            "现价 ¥29.74 较基准高 7.8%；现价隐含永续 g 1.76%（WACC 6.0%）或 WACC 6.04%（g 1.8%）。",
            "WACC ±50bp → 每股约 ¥25.7–35.8；g ±0.3pct → 约 ¥27.4–33.4。利率是最大估值变量。",
        ]
    elif c.code == "000001.SZ":
        method2 = [
            ["归一化 DPS", "¥0.65", "2026E 分红率约 29%"],
            ["COE", "11.5%", "与 RI 一致"],
            ["DDM g", "3.5%", "与 RI 一致"],
            ["DDM 每股价值", "¥8.13", "DPS/(COE−g)"],
        ]
        sens = [["COE \\ ROE", "6.5%", "7.0%", "7.5%", "8.0%", "8.5%"]]
        for coe in [0.105, 0.110, 0.115, 0.120, 0.125]:
            row = [f"{coe:.1%}"]
            for roe in [0.065, 0.070, 0.075, 0.080, 0.085]:
                row.append(f"{c.bps + (roe - coe) * c.bps / (coe - 0.035):.1f}")
            sens.append(row)
        cross = [
            "RI ¥12.28 vs DDM ¥8.13：差距来自 29% 的低分红率；若分红率提升，DDM 会靠近 RI。",
            "现价 ¥11.64 较基准 ¥11.03 高 5.5%，合理偏贵；现价隐含 ROE 7.29%（COE 11.5%、g 3.5%）。",
            "ROE ±50bp → 每股约 ±¥1.54；COE ±50bp → 约 ¥11.6–13.1。ROE 与信用成本是核心。",
        ]
    else:
        method2 = [
            ["2026E DPS", "¥1.95", "分红率约 75%"],
            ["COE", "8.0%", "与 WACC 一致"],
            ["DDM g", "2.0%", "股息长期增长"],
            ["DDM 每股价值", "¥32.50", "DPS/(COE−g)"],
            ["2026E EPS", "¥2.60", "归母净利/股本"],
            ["中周期 PE", "15.0x", "周期股合理中枢"],
            ["PE 每股价值", "¥39.00", "EPS×PE"],
        ]
        sens = [["WACC \\ FCF", "520", "560", "600", "620", "660", "700", "720"]]
        for w in [0.070, 0.075, 0.080, 0.085, 0.090]:
            row = [f"{w:.1%}"]
            for fcff in [520, 560, 600, 620, 660, 700, 720]:
                ev = fcff / (w - 0.015)
                row.append(f"{(ev - c.net_debt - c.minority) / c.shares:.1f}")
            sens.append(row)
        cross = [
            "DCF ¥38.19、DDM ¥32.50、PE ¥39.00；三法均低于现价 ¥51.99，综合基准 ¥36.64。",
            "现价较基准高 41.9%；现价隐含永续 g 3.05%（WACC 8.0%）或 WACC 6.45%（g 1.5%）。",
            "WACC ±50bp → 约 ¥35.0–41.9；FCF ±60 亿 → 约 ±¥2.8。即使乐观假设，仍难支撑现价。",
        ]
    methods = {
        "600900.SH": [
            ["FCFF DCF", "30.17", "50%", "稳定现金流；对 WACC/g 敏感"],
            ["DDM", "25.00", "50%", "高分红；忽略留存现金"],
            ["综合", "27.59", "100%", "两法各半，取区间中值"],
        ],
        "000001.SZ": [
            ["剩余收益 RI", "12.28", "70%", "银行主方法；对 ROE/COE 敏感"],
            ["DDM", "8.13", "30%", "低分红率下偏低，作交叉"],
            ["综合", "11.03", "100%", "RI 为主，DDM 为辅"],
        ],
        "601088.SH": [
            ["FCFF DCF", "38.19", "50%", "中周期现金流；对煤价敏感"],
            ["DDM", "32.50", "30%", "高分红；周期高点不可外推"],
            ["PE", "39.00", "20%", "中周期 15x；避免峰值低 PE"],
            ["综合", "36.64", "100%", "三法加权"],
        ],
    }[c.code]
    checks = {
        "600900.SH": [
            "FCFF 430 亿 vs 2025 年 420.75 亿：+2.2%，接近实际，未假设新坝。",
            "g 1.8% vs 10Y 国债 1.62%：永续增长略高于无风险利率，合理但偏乐观。",
            "WACC 6.0%：对水电类低杠杆资产偏低，若利率上行 50bp，价值降至约 25.7 元。",
            "DDM 25.00 元低于 DCF：留存现金未分配，DDM 天然保守。",
        ],
        "000001.SZ": [
            "可持续 ROE 7.5% vs 2026E 8.8%：已下调，反映 NIM 与信用成本压力。",
            "COE 11.5%：Rf 1.62% + 股权风险溢价；对银行不算苛刻。",
            "g 3.5%：与资本补充、分红率匹配；若 g 降至 3.0%，价值约 9.6 元。",
            "DDM 8.13 元低于 RI：29% 分红率下，DDM 低估留存价值。",
        ],
        "601088.SH": [
            "FCFF 620 亿 vs 2025 年 266.6 亿：2026 年收购并表 + 煤价回升，与 9M 年化 607 亿基本相当。",
            "g 1.5%：低于长期通胀，考虑煤炭需求见顶，合理。",
            "WACC 8.0%：周期资源股要求回报；若降至 7.5%，价值约 43.9 元。",
            "PE 15x：高于煤炭行业历史中枢，已给一体化与长协溢价。",
        ],
    }[c.code]
    return page(f"""
      <h2>5. 估值方法二与交叉检查</h2>
      <div class="grid2">
        <div>
          {table(["假设 / 步骤","数值","说明"], method2, ["26%","18%","56%"])}
          <div class="note" style="margin-top:2mm;"><span class="tag calc">计算</span>结果：<b>¥{c.method2_value:.2f}</b>；与现价相比 {'溢价' if c.price>c.method2_value else '折价'} {abs(c.price/c.method2_value-1)*100:.1f}%。</div>
        </div>
        <div>
          <h3>敏感性：每股价值（元）</h3>
          {table(sens[0], sens[1:], ["16%","16.8%","16.8%","16.8%","16.8%","16.8%"], cls="num")}
        </div>
      </div>
      <div class="card" style="margin-top:2.5mm;">
        <h3>交叉检查</h3>
        <ul>{''.join(f'<li>{x}</li>' for x in cross)}</ul>
      </div>
      <div class="grid2" style="margin-top:2.5mm;">
        <div class="card"><h3>估值方法比较</h3>{table(["方法","结果","权重","适用性 / 局限"], methods, ["22%","16%","14%","48%"])}</div>
        <div class="card"><h3>关键假设检验</h3><ul>{''.join(f'<li>{x}</li>' for x in checks)}</ul></div>
      </div>
    """, 6)


def page_scenarios(c):
    scen = c.scenario_values
    if c.code == "600900.SH":
        rows = [
            ["归一化 FCFF（亿元）","400","430","470"],
            ["WACC","6.5%","6.0%","5.7%"],
            ["永续 g","1.5%","1.8%","2.0%"],
            ["DCF 每股（元）","21.85","30.17","40.48"],
            ["DPS（元）","0.88","1.00","1.08"],
            ["COE","6.5%","6.0%","5.7%"],
            ["DDM g","1.5%","2.0%","2.2%"],
            ["DDM 每股（元）","17.60","25.00","30.86"],
            ["#pos综合每股（元）", f"#pos{scen['悲观']:.2f}", f"#pos{c.blended_value:.2f}", f"#pos{scen['乐观']:.2f}"],
            ["#pos相对现价", f"#pos{(scen['悲观']/c.price-1)*100:+.1f}%", f"#pos{(c.blended_value/c.price-1)*100:+.1f}%", f"#pos{(scen['乐观']/c.price-1)*100:+.1f}%"],
        ]
        rev = [
            ["现价隐含 EV","10,132 亿元","市值+净债务+少数股东"],
            ["隐含永续 g（WACC 6.0%）","1.76%","WACC − FCF/EV"],
            ["隐含 WACC（g 1.8%）","6.04%","g + FCF/EV"],
            ["20% 安全边际价格","¥22.07","基准 ¥27.59 × 0.8"],
        ]
    elif c.code == "000001.SZ":
        rows = [
            ["可持续 ROE","6.5%","7.5%","8.5%"],
            ["COE","12.0%","11.5%","11.0%"],
            ["永续 g","3.0%","3.5%","4.0%"],
            ["RI 每股（元）","9.55","12.28","15.79"],
            ["DPS（元）","0.55","0.65","1.00"],
            ["DDM g","3.0%","3.5%","4.0%"],
            ["DDM 每股（元）","6.11","8.13","14.29"],
            ["#pos综合每股（元）", f"#pos{scen['悲观']:.2f}", f"#pos{c.blended_value:.2f}", f"#pos{scen['乐观']:.2f}"],
            ["#pos相对现价", f"#pos{(scen['悲观']/c.price-1)*100:+.1f}%", f"#pos{(c.blended_value/c.price-1)*100:+.1f}%", f"#pos{(scen['乐观']/c.price-1)*100:+.1f}%"],
        ]
        rev = [
            ["现价 PB","0.47x","价格 / BPS 24.56"],
            ["隐含 ROE（COE 11.5%、g 3.5%）","7.29%","PB×(COE−g)+g"],
            ["隐含 COE（ROE 7.5%、g 3.5%）","11.94%","g+(ROE−g)/PB"],
            ["20% 安全边际价格","¥8.83","基准 ¥11.03 × 0.8"],
        ]
    else:
        rows = [
            ["归一化 FCFF（亿元）","520","620","720"],
            ["WACC","8.5%","8.0%","7.5%"],
            ["永续 g","1.0%","1.5%","2.0%"],
            ["DCF 每股（元）","26.18","38.19","54.57"],
            ["DPS（元）","1.70","1.95","2.20"],
            ["COE","8.5%","8.0%","7.5%"],
            ["DDM g","1.5%","2.0%","2.0%"],
            ["DDM 每股（元）","24.29","32.50","40.00"],
            ["PE（倍）","11.0","15.0","18.0"],
            ["PE 每股（元）","25.85","39.00","54.00"],
            ["#pos综合每股（元）", f"#pos{scen['悲观']:.2f}", f"#pos{c.blended_value:.2f}", f"#pos{scen['乐观']:.2f}"],
            ["#pos相对现价", f"#pos{(scen['悲观']/c.price-1)*100:+.1f}%", f"#pos{(c.blended_value/c.price-1)*100:+.1f}%", f"#pos{(scen['乐观']/c.price-1)*100:+.1f}%"],
        ]
        rev = [
            ["现价隐含 EV","12,531 亿元","市值+净债务+少数股东"],
            ["隐含永续 g（WACC 8.0%）","3.05%","WACC − FCF/EV"],
            ["隐含 WACC（g 1.5%）","6.45%","g + FCF/EV"],
            ["20% 安全边际价格","¥29.32","基准 ¥36.64 × 0.8"],
        ]
    triggers = {
        "600900.SH": [
            ["发电量 / 来水", "-8% 以上", "±3%", "+5% 以上"],
            ["10Y 国债", "2.2%", "1.6–1.8%", "1.4%"],
            ["上网电价", "-3%", "持平", "+2%"],
            ["DPS（元）", "0.88", "1.00", "1.08"],
        ],
        "000001.SZ": [
            ["ROE", "6.5%", "7.5%", "8.5%"],
            ["不良率", "1.30%", "1.05%", "0.95%"],
            ["关注类", "2.50%", "2.07%", "1.80%"],
            ["分红率", "25%", "30%", "45%"],
        ],
        "601088.SH": [
            ["煤价（元/吨）", "380", "448", "520"],
            ["电力毛利率", "8%", "13.4%", "18%"],
            ["并表利润（亿）", "50", "68.8", "85"],
            ["资产负债率", "45%", "40.8%", "38%"],
        ],
    }[c.code]
    return page(f"""
      <h2>6. 三情景、反向估值与安全边际</h2>
      <div class="grid2">
        <div>
          <h3>情景假设与结果</h3>
          {table(["假设 / 结果","悲观","基准","乐观"], rows, ["34%","22%","22%","22%"])}
        </div>
        <div>
          <h3>反向估值：现价隐含了什么？</h3>
          {table(["项目","数值","说明"], rev, ["38%","20%","42%"])}
          <div class="card" style="margin-top:2.5mm;">
            <h3>安全边际</h3>
            <p style="font-size:9pt;">现价 <b>¥{c.price:.2f}</b>；基准 <b>¥{c.blended_value:.2f}</b>；安全边际 <b class="{'neg' if c.margin_of_safety<0 else 'pos'}">{c.margin_of_safety*100:+.1f}%</b>。</p>
            <p class="small">安全边际 = 1 − 现价/基准。负值表示现价高于基准；正值为折价。20% 安全边际价格仅供计算参考，不是买卖指令。</p>
            <p class="small">“相对现价” = 每股价值/现价 − 1；与安全边际分母不同，数值接近但不相等。</p>
          </div>
          <div class="note" style="margin-top:2.5mm;">
            <span class="tag judge">判断</span>{"现价接近基准，但 2026E 盈利下修与利率上行会压缩安全垫；不是“便宜的好资产”。" if c.code=="600900.SH" else
            "现价高于基准约 5.5%；低 PB 已定价 ROE 下行，向上重估需要 ROE 企稳或分红率提升。" if c.code=="000001.SZ" else
            "现价高于基准 42%，且接近乐观情景；市场在为煤价高位与收购增长付费。"}
          </div>
        </div>
      </div>
      <h3 style="margin-top:3mm;">情景触发条件</h3>
      {table(["指标","悲观","基准","乐观"], triggers, ["34%","22%","22%","22%"])}
      <div class="small" style="margin-top:1.5mm;">触发表用于跟踪，不是预测；任一指标持续偏离基准，应重跑估值，而不是只改结论。</div>
    """, 7)


def page_risks(c):
    if c.code == "600900.SH":
        risks = [
            ["来水偏枯", "2026Q3 发电量 -14.9%；乌东德来水偏枯 9.29%", "月度发电量、主要水库来水", "高"],
            ["利率上行", "净债务 2,735 亿；WACC +50bp → 价值约 -15%", "10Y 国债、公司债利差", "高"],
            ["电价下行", "市场化交易比例提升，电价受管制", "上网电价、市场化电量", "中"],
            ["资本开支", "抽蓄/新能源投资可能稀释回报", "capex、在建工程", "中"],
            ["关联交易", "集团资产注入/关联采购", "公告、关联交易比例", "低中"],
        ]
        monitor = ["季度发电量与来水", "财务费用与债务成本", "分红率与派息公告", "电价政策与市场化交易", "资本开支与在建项目"]
    elif c.code == "000001.SZ":
        risks = [
            ["零售不良", "信用卡不良 2.15%、消费贷 1.16%", "不良生成率、核销", "高"],
            ["关注/逾期", "关注类 2.07%（+24bp）、逾期 1.59%（+10bp）", "关注类、逾期率", "高"],
            ["NIM 下行", "NIM 1.80%，资产收益率下行", "NIM、贷款定价", "中高"],
            ["资本约束", "CET1 11.26%，分红率仅 29%", "CET1、RWA 增速", "中"],
            ["房地产/对公", "对公房地产敞口与城投风险", "房地产不良、集中度", "中"],
        ]
        monitor = ["NIM 与生息资产收益率", "不良/关注/逾期/拨备", "零售 AUM 与私行", "CET1 与分红率", "房地产与对公集中度"]
    else:
        risks = [
            ["煤价回落", "2026 煤价 448 元/吨（+7.4%），周期高位", "秦皇岛现货、长协价", "高"],
            ["电力毛利", "电力毛利率 13.4%（-4.9pct），成本 +8.1%", "电价、度电成本", "中高"],
            ["收购整合", "1,335.98 亿收购、11 家并表、少数股东 969 亿", "并表利润、协同、减值", "高"],
            ["杠杆上升", "负债率 40.8%（2025 年 33.2%）", "有息负债、财务费用", "中高"],
            ["A/H 溢价", "A 股 51.99 元；H 股股息率约 6.7%", "AH 溢价、南向资金", "中"],
        ]
        monitor = ["煤价与长协比例", "自产煤单位成本", "电力毛利率", "收购标的并表利润", "负债率与财务费用", "A/H 溢价"]
    risk_rows = "".join(f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td class='center {'neg' if r[3]=='高' else ('warn' if r[3]=='中高' else '')}'>{r[3]}</td></tr>" for r in risks)
    calendar = {
        "600900.SH": [
            ["2026-10", "三季报", "发电量、财务费用、Q3 净利"],
            ["2027-04", "年报", "DPS、分红率、电价"],
            ["月度", "来水 / 发电量", "主要水库来水、发电量"],
            ["季度", "利率", "10Y 国债、信用利差"],
            ["事件", "资本开支", "抽蓄/新能源、关联交易"],
        ],
        "000001.SZ": [
            ["2026-10", "三季报", "NIM、不良、关注类"],
            ["2027-03", "年报", "分红率、CET1"],
            ["季度", "零售", "AUM、私行、信用卡"],
            ["月度", "社融", "零售信贷需求"],
            ["事件", "管理层 / 监管", "战略连续性、资本规则"],
        ],
        "601088.SH": [
            ["2026-10", "三季报", "煤价、电力毛利、并表利润"],
            ["2027-03", "年报", "分红率、负债率"],
            ["月度", "煤价", "秦皇岛现货、长协"],
            ["季度", "产量 / 成本", "自产煤、单位成本"],
            ["事件", "收购整合", "协同、减值、少数股东"],
        ],
    }[c.code]
    return page(f"""
      <h2>7. 风险与监控</h2>
      <table><colgroup><col style="width:16%"><col style="width:48%"><col style="width:26%"><col style="width:10%"></colgroup>
        <thead><tr><th>风险</th><th>事实 / 机制</th><th>监控指标</th><th class="center">等级</th></tr></thead>
        <tbody>{risk_rows}</tbody>
      </table>
      <div class="grid2" style="margin-top:2.5mm;">
        <div class="card"><h3>监控清单</h3><ul>{''.join(f'<li>{x}</li>' for x in monitor)}</ul></div>
        <div class="card"><h3>什么会改变结论？</h3>
          <p><span class="tag fact">事实</span>{"若来水恢复正常、电价上行、利率下行，DCF/DDM 会同步上修；若 Q3 弱势延续到 Q4，2026E 仍有下修风险。" if c.code=="600900.SH" else
          "若 ROE 稳定在 8.5% 以上、关注/逾期回落、分红率提升，RI 与 DDM 会同步上修；若零售不良继续生成，PB 可能继续下探。" if c.code=="000001.SZ" else
          "若煤价维持高位、收购协同超预期、负债率回落，2026E 盈利可能上修；若煤价回落或电力毛利继续压缩，当前估值缺乏支撑。"}</p>
          <p><span class="tag judge">判断</span>{"估值对利率的敏感度高于对来水的敏感度。" if c.code=="600900.SH" else
          "估值对 ROE 与信用成本的敏感度高于对规模增长。" if c.code=="000001.SZ" else
          "估值对煤价与收购整合的敏感度最高；A/H 溢价是额外的安全垫/风险源。"}</p>
        </div>
      </div>
      <h3 style="margin-top:3mm;">跟踪日历</h3>
      {table(["时间","事件","看什么"], calendar, ["14%","22%","64%"])}
      <h2 style="margin-top:3mm;">8. 来源与免责声明</h2>
      <div class="grid2">
        <div class="small">
          <b>主要来源：</b>公司 2026 年半年报/三季报、2025 年年报、分红公告、收购公告；东方财富 F10；腾讯证券行情；中国 10 年期国债收益率（2026-10-29，1.6233%）。
          <br><br>
          <b>价格日：</b>2026-10-30 收盘。财务数据以公司公告为准；第三方数据仅用于交叉核对。
        </div>
        <div class="note">
          <b>免责声明：</b>本报告为研究记录，不构成任何投资建议、要约或承诺。估值依赖假设，假设变化会显著改变结果。作者可能不持有或不了解报告发布后的最新变化。读者应独立判断，并咨询持牌专业人士。
        </div>
      </div>
    """, 8)


def build_html(c):
    pages = [cover(c), page_boundary(c), page_business(c), page_financials(c),
             page_management_method1(c), page_method2(c), page_scenarios(c), page_risks(c)]
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{''.join(pages)}</body></html>"""


def build_pdf(c):
    outdir = OUT / f"{c.code}-{DATE}"
    outdir.mkdir(parents=True, exist_ok=True)
    html_path = outdir / f"{c.code}-估值模型-{DATE}.html"
    pdf_path = outdir / f"{c.code}-估值模型-{DATE}.pdf"
    html_path.write_text(build_html(c), encoding="utf-8")
    cmd = [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
           f"--print-to-pdf={pdf_path}", html_path.as_uri()]
    subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=180)
    html_path.unlink(missing_ok=True)
    print("saved", pdf_path)


if __name__ == "__main__":
    for c in COMPANIES:
        build_pdf(c)
