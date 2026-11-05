# -*- coding: utf-8 -*-
"""宁德时代 300750.SZ · 巴菲特框架研究 PDF（A4 横向 8 页）"""
import sys, subprocess
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catl_data as D

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / "输出" / "A股" / f"300750.SZ-{D.DATE}"
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
"""


def table(headers, rows, widths=None, cls=""):
    out = [f'<table class="{cls}">']
    if widths:
        out.append("<colgroup>" + "".join(f'<col style="width:{w}">' for w in widths) + "</colgroup>")
    out.append("<thead><tr>" + "".join(f'<th class="{"num" if cls=="num" else ""}">{escape(str(h))}</th>' for h in headers) + "</tr></thead><tbody>")
    for row in rows:
        cells = []
        for v in row:
            c = ""
            if isinstance(v, str) and v.startswith("#"):
                c, v = v[1:].split("|", 1) if "|" in v else ("", v[1:])
            cells.append(f'<td class="{c}">{v}</td>')
        out.append("<tr>" + "".join(cells) + "</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def page(content, num, total=8):
    return (f'<div class="page">{content}<div class="footer"><span>巴菲特框架研究 · 宁德时代 300750.SZ · {D.DATE} · 仅供研究记录</span>'
            f'<span>不构成投资建议</span></div><div class="pnum">{num} / {total}</div></div>')


def score_bars(items):
    return "".join(
        f'<div class="score"><div class="lbl">{k}</div><div class="bar"><div class="fill" style="width:{v/5*100:.0f}%"></div></div><div class="v">{v}/5</div></div>'
        for k, v in items
    )


def np_chart(w=1080, h=118):
    vals = D.NP + [D.NP_2026E]
    labels = D.YEARS + ["2026E"]
    maxv = max(vals) * 1.14
    left, right, top, bottom = 44, 8, 16, 28
    plot_w, plot_h = w - left - right, h - top - bottom
    step = plot_w / len(vals)
    barw = min(58, step * 0.40)
    out = [f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}px" xmlns="http://www.w3.org/2000/svg">']
    for frac in [0, .25, .5, .75, 1]:
        y = top + plot_h * (1 - frac)
        out.append(f'<line x1="{left}" y1="{y:.1f}" x2="{w-right}" y2="{y:.1f}" stroke="#E5DFD3" stroke-width="1" stroke-dasharray="4 5"/>')
        out.append(f'<text x="{left-4}" y="{y+3:.1f}" font-size="7.0" fill="#5B6770" text-anchor="end">{maxv*frac:,.0f}</text>')
    for i, (lab, v) in enumerate(zip(labels, vals)):
        cx = left + step * (i + .5)
        bh = v / maxv * plot_h
        col = "#2F6B4F" if lab != "2026E" else "#7FA8D9"
        out.append(f'<rect x="{cx-barw/2:.1f}" y="{top+plot_h-bh:.1f}" width="{barw:.1f}" height="{bh:.1f}" rx="3" fill="{col}"/>')
        out.append(f'<text x="{cx:.1f}" y="{top+plot_h-bh-3:.1f}" font-size="7.6" font-weight="bold" fill="#2F6B4F" text-anchor="middle">{v:,.0f}</text>')
        out.append(f'<text x="{cx:.1f}" y="{h-6}" font-size="7.4" fill="#5B6770" text-anchor="middle">{lab}</text>')
    out.append("</svg>")
    return "".join(out)


def cover():
    scen = [
        ["悲观", f"¥{D.BLEND_BEAR:.2f}", f"#neg|{(D.BLEND_BEAR/D.PRICE-1)*100:+.1f}%", "价格战延续；2027 消费税 4% 无法转嫁；海外受阻"],
        ["基准", f"#pos|¥{D.BLEND_BASE:.2f}", f"#pos|{(D.BLEND_BASE/D.PRICE-1)*100:+.1f}%", "单位盈利企稳；税负部分转嫁；出货 +20%"],
        ["乐观", f"¥{D.BLEND_BULL:.2f}", f"#pos|{(D.BLEND_BULL/D.PRICE-1)*100:+.1f}%", "储能与海外高增；单位盈利修复；18x PE"],
    ]
    keys = [
        ["FCFF DCF", "EV 减少数股东、加净现金", f"¥{D.DCF_BASE:.2f}"],
        ["PE 法", "2027E EPS 22.50 × 15.3x", f"¥{D.PE_BASE_V:.2f}"],
        ["综合基准", "DCF 50% + PE 50%", f"¥{D.BLEND_BASE:.2f}"],
        ["评级 / 置信度", "有条件便宜", "中"],
    ]
    metrics = [
        ("现价", f"¥{D.PRICE:.2f}", "前收 ¥252.88；市值 12,306 亿"),
        ("2026E PE", f"{D.PRICE/D.EPS_2026E:.1f}x", f"EPS ¥{D.EPS_2026E:.2f}（净利 906 亿）"),
        ("2027E PE", f"{D.PRICE/D.EPS_2027E_BASE:.1f}x", f"EPS ¥{D.EPS_2027E_BASE:.2f}（低于一致 23.57）"),
        ("安全边际", f"+{D.MOS*100:.1f}%", f"基准 ¥{D.BLEND_BASE:.2f}"),
    ]
    metric_html = "".join(f'<div class="metric"><div class="k">{k}</div><div class="v">{v}</div><div class="n">{n}</div></div>' for k, v, n in metrics)
    return page(f"""
      <div class="kicker">巴菲特框架研究 · A股 · {D.DATE}</div>
      <h1>宁德时代<span>300750.SZ</span></h1>
      <div class="sub">动力电池 / 储能 · 价格日 {D.DATE} 午间 · 现价 ¥{D.PRICE:.2f} · 市值 {D.MARKET_CAP:,.0f} 亿元</div>
      <div class="conclusion">便宜，但有条件的便宜。现价较综合基准 ¥{D.BLEND_BASE:.2f} 低 {D.MOS*100:.1f}%；前提是 2027 年税负能部分转嫁、单位盈利不破 0.07 元/Wh。</div>
      <div class="metrics">{metric_html}</div>
      <div class="grid2" style="margin-top:1mm;">
        <div class="card">
          <h3>三情景每股价值</h3>
          {table(["情景","每股价值","相对现价","核心假设"], scen, ["13%","18%","14%","55%"])}
          <div class="small" style="margin-top:1.5mm;">综合 = DCF 50% + PE 50%；“相对现价”= 价值/现价 − 1，与安全边际分母不同。</div>
        </div>
        <div class="card">
          <h3>估值交叉与结论</h3>
          {table(["项目","方法","结果"], keys, ["24%","46%","30%"])}
          <div class="small" style="margin-top:1.5mm;">现价较基准低 {D.MOS*100:.1f}%；若要求 20% 安全边际，对应价格约 ¥{D.MOS20_PRICE:.2f}。现价已低于该价格。</div>
        </div>
      </div>
      <div class="note" style="margin-top:2.5mm;">
        <span class="tag fact">事实</span>财务数据来自公司公告与东方财富 F10；<span class="tag calc">计算</span>估值由本模型完成；
        <span class="tag assume">假设</span>2027E EPS、折现率与永续增长为研究假设；<span class="tag judge">判断</span>评级与置信度为主观判断。
        所有数字均可追溯到 Excel 模型与“来源”页。
      </div>
      <h3 style="margin-top:3mm;">投资论点拆解</h3>
      <div class="grid3">
        <div class="card bull"><h4>多头论据</h4><ul>
          <li>全球动力电池份额 39.2%、储能 30.4%；2025 年毛利率 26.3%、ROE 24.9%。</li>
          <li>净现金 2,427 亿；2025 年经营现金流 1,332 亿、FCF 909 亿。</li>
          <li>2026E PE 13.6x、2027E PE 11.8x；回购注销上限 400 亿。</li>
        </ul></div>
        <div class="card bear"><h4>空头论据</h4><ul>
          <li>2026Q3 毛利率 20.7%、单位盈利约 0.082 元/Wh，均为阶段低位。</li>
          <li>2027 年消费税升至 4%、出口退税取消，税负无法转嫁则净利下修。</li>
          <li>车企自研与二供、三供；份额提升放缓，价格战可能长期化。</li>
        </ul></div>
        <div class="card neutral"><h4>结论</h4><p>便宜来自市场对税负与价格战的担忧，不是生意变差；但“便宜”需要盈利不大幅下修作前提。</p><p class="small" style="margin-top:1mm;">评级：便宜；置信度：中。</p></div>
      </div>
    """, 1)


def page_boundary():
    boundary = [
        ["价格日", f"{D.DATE} 午间", "总市值", f"{D.MARKET_CAP:,.0f} 亿元"],
        ["最新财报", "2026 年三季报", "财务截止", "2026-09-30"],
        ["2026Q3", "营收 1,652 亿；净利 212.5 亿", "2026E", "净利 906 亿（一致预期）"],
        ["总股本", "46.2725 亿股", "净现金", "2,426.7 亿元"],
        ["少数股东", "363.4 亿元", "BPS", "¥83.61"],
    ]
    defs = [
        ["FCFF", "企业自由现金流；本文用净利+折旧摊销+利息−capex−营运资本增加估算"],
        ["WACC", "加权平均资本成本；Ke 8.7%、Kd 2.5%、D/(D+E) 13%"],
        ["EV → 股权", "EV − 少数股东权益 + 净现金；净现金=货币+交易性金融−有息负债"],
        ["单位盈利", "归母净利 / 电池销量，元/Wh；用于跟踪价格战与税负传导"],
        ["安全边际", "1 − 现价 / 基准价值；正=折价，负=溢价"],
    ]
    dq = [
        ["价格 / 股本", "¥265.94；46.2725 亿股", "与前收、市值核对一致"],
        ["财报口径", "2026 三季报；9M 累计", "ROE 17.64% 未年化"],
        ["一次性项目", "2025 特别股息 4.779 元/股", "分红率需区分普通/特别"],
        ["数据缺口", "2026Q4 销量、单位盈利", "2027 年税负传导是关键"],
    ]
    chain = [("01","数据边界","价格/财报/股本"),("02","生意与护城河","八问 + 分部"),("03","财务与分红","五年表"),
             ("04","两法估值","DCF + PE"),("05","情景与风险","安全边际")]
    chain_html = "".join(
        f'<div class="step"><div class="n">{n}</div><div class="s">{s}</div><div class="d">{d}</div></div>' +
        ('<div class="arrow">›</div>' if i < len(chain)-1 else '')
        for i, (n, s, d) in enumerate(chain))
    return page(f"""
      <h2>0. 数据边界、能力圈与定义</h2>
      <div class="grid2">
        <div>
          <h3>数据边界</h3>
          {table(["项目","内容","项目","内容"], boundary, ["18%","32%","18%","32%"])}
          <div class="note" style="margin-top:2.5mm;">
            <span class="tag fact">事实</span>价格、股本、财报为公开披露；<span class="tag assume">假设</span>2026E 净利为机构一致预期，2027E EPS 22.50 为本报告假设，不是公司指引。
            2025 年 DPS 7.964 元含特别股息 4.779 元，普通 DPS 约 3.185 元；用 7.964 元年化会高估可持续股息。
          </div>
        </div>
        <div>
          <h3>能力圈</h3>
          <ul>
            <li>能理解：收入=电池销量×单价；成本由材料、制造、折旧与税负决定；规模与良率是核心。</li>
            <li>能跟踪：销量、单价、单位盈利、毛利率、份额、海外收入、产能利用率、存货、经营现金流。</li>
            <li>不擅长：精确判断 2027 年税负转嫁比例与价格战底部；因此用 DCF + PE 区间，而不是单点。</li>
            <li>能力圈结论：这是周期成长股，不是稳定红利资产；适用 3 年以上资金。</li>
          </ul>
          <h3>关键定义</h3>
          {table(["术语","定义"], defs, ["16%","84%"])}
        </div>
      </div>
      <h3 style="margin-top:3mm;">研究链条</h3>
      <div class="chain">{chain_html}</div>
      <div class="grid2" style="margin-top:1mm;">
        <div class="card"><h3>数据质量检查</h3>{table(["项目","读数","说明"], dq, ["24%","34%","42%"])}</div>
        <div class="card"><h3>本报告不做什么</h3>
          <ul>
            <li>不把“低 PE”直接等同于便宜：2027 年盈利可能被税负下修。</li>
            <li>不把 2025 年特别股息当作可持续股息率。</li>
            <li>不预测短期股价，不给出个性化买卖指令。</li>
            <li>不把 2026Q3 单季低点线性外推到 2027 年。</li>
          </ul>
        </div>
      </div>
    """, 2)


def page_business():
    qs = [
        ("1. 生意能理解吗？", "能。收入=销量×单价；成本由正极/电解液等材料、制造折旧、人工与税负构成；规模、良率、产品结构决定毛利。"),
        ("2. 有护城河吗？", "有，但是成本曲线上的护城河。772GWh 产能、661GWh 销量、单位成本行业最低之一；客户认证 2–3 年；但没有提价权。"),
        ("3. 能长久吗？", "动力电池与储能需求长期增长；但技术路线（LFP/三元/固态）、车企自研与地缘政治会改变格局。"),
        ("4. 资本回报如何？", "2021–2025 ROE 21.5%→24.9%；2026 9M 17.6%（未年化）。高 ROE 来自周转与杠杆，不只是利润率。"),
        ("5. 增长来自哪里？", "储能（2026H1 占比 19.2%）、海外（2026H1 31.5%）、新产品（麒麟/神行/钠新）；国内动力份额提升放缓。"),
        ("6. 管理层是否可信？", "创始人控制，战略执行力强；分红率升至 50%、回购 200–400 亿全部注销。关注资本开支与海外扩张纪律。"),
        ("7. 最大风险是什么？", "2027 年消费税 4% + 出口退税取消；价格战使单位盈利从 0.082 跌向 0.06；海外市场被强制分割。"),
        ("8. 估值是否合理？", "2026E PE 13.6x、2027E PE 11.8x；DCF 349.94、PE 344.25，基准 347.10；现价 265.94，便宜但有条件。"),
    ]
    cards = "".join(f'<div class="q"><h4>{q}</h4><p>{a}</p></div>' for q, a in qs)
    canvas = [
        ["收入驱动", "电池销量 × 单价；动力 69%、储能 19%、材料 8%（2026H1）"],
        ["成本结构", "材料 60–70%、制造折旧、人工；规模与良率摊薄固定成本"],
        ["资本密度", "极高；2025 年 capex 423 亿、2026 9M 422 亿；在建 321GWh"],
        ["周期性", "锂价、车企库存、补贴/税率；储能平滑但同样竞价"],
        ["监管 / 竞争", "消费税、出口退税、IRA/EU 本地化；比亚迪/二线/车企自研"],
        ["关键指标", "销量、单价、单位盈利、毛利率、份额、海外收入、OCF"],
    ]
    moat = [("规模 / 成本", 5), ("客户认证", 4), ("技术与产品", 5), ("产业链整合", 4), ("海外本地化", 3)]
    return page(f"""
      <h2>1. 生意本质与八问</h2>
      <div class="small" style="margin-bottom:2.5mm;">用八个问题把“好生意”拆开：可理解、护城河、久期、资本回报、增长、管理层、风险、估值。</div>
      <div class="qgrid">{cards}</div>
      <div class="note" style="margin-top:2.5mm;">
        <b>一句话：</b>宁德时代是“成本曲线上的龙头”，不是“提价权上的垄断”；行业价格战激烈时，龙头只能用成本优势守住份额，无法阻止单价与单位盈利下行。
      </div>
      <div class="grid2" style="margin-top:3mm;">
        <div class="card"><h3>商业模式画布</h3>{table(["维度","内容"], canvas, ["22%","78%"])}</div>
        <div class="card"><h3>护城河评分（1–5）</h3>{score_bars(moat)}
          <div class="small" style="margin-top:2mm;">综合 4.3/5。评分是研究判断，不是精确度量；护城河强不等于当前价格便宜，也不等于单位盈利不会下行。</div>
        </div>
      </div>
    """, 3)


def page_financials():
    rows = [
        ["营业收入", "1,303.56","3,285.94","4,009.17","3,620.13","4,237.02","4,421.37","—"],
        ["归母净利", "159.31","307.29","441.21","507.45","722.01","645.30",f"{D.NP_2026E:.0f}"],
        ["EPS（元）", "6.88","7.18","10.06","11.58","16.14","14.13",f"{D.EPS_2026E:.2f}"],
        ["ROE（%）", "21.5","24.7","24.0","24.1","24.9","17.6*","—"],
        ["毛利率（%）", "26.3","20.3","19.2","24.4","26.3","22.7","—"],
        ["净利率（%）", "12.2","9.4","11.0","14.0","17.0","14.6","—"],
        ["经营现金流", "429.1","612.1","928.3","969.9","1,332.2","616.3","—"],
        ["资本开支", "437.7","482.2","336.3","311.8","423.5","421.7","—"],
        ["自由现金流", "-8.6","129.9","592.0","658.1","908.8","194.6","—"],
        ["DPS（元）", "—","2.52","2.011","4.553","7.964","—","9.79"],
        ["分红率（%）", "—","35.1","19.6","39.3","50.0","—","50.0"],
    ]
    seg25 = [
        ["动力电池", "3,165.1", "74.7%"],
        ["储能电池", "624.4", "14.7%"],
        ["材料及回收", "301.0", "7.1%"],
        ["其他", "146.5", "3.5%"],
        ["合计", "4,237.0", "100%"],
    ]
    seg26 = [
        ["动力电池", "1,921.2", "69.4%"],
        ["储能电池", "532.6", "19.2%"],
        ["材料及回收", "218.0", "7.9%"],
        ["其他", "97.4", "3.5%"],
        ["合计", "2,769.2", "100%"],
    ]
    return page(f"""
      <h2>2. 五年财务、分部与现金流</h2>
      <div class="grid2" style="align-items:start;">
        <div>
          <div class="small" style="margin-bottom:1.5mm;">单位：亿元、元/股、%；*2026 9M ROE 未年化；2026E 仅净利/EPS 为预测。</div>
          {table(["指标","2021","2022","2023","2024","2025","2026 9M","2026E"], rows, ["17%","11.5%","11.5%","11.5%","11.5%","11.5%","13%","12.5%"])}
        </div>
        <div>
          <h3>2025 年收入结构</h3>
          {table(["业务","收入（亿元）","占比"], seg25, ["40%","35%","25%"])}
          <h3 style="margin-top:2.5mm;">2026H1 收入结构</h3>
          {table(["业务","收入（亿元）","占比"], seg26, ["40%","35%","25%"])}
          <div class="small" style="margin-top:1.5mm;">储能占比 14.7%→19.2%；动力占比 74.7%→69.4%。2026 9M 综合毛利率 22.7%，Q3 降至 20.7%。</div>
        </div>
      </div>
      <div class="grid2" style="margin-top:2.5mm;">
        <div class="card"><h3>关键观察</h3><ul>
          <li>2026 9M 营收 +56.2%、净利 +31.6%，但 Q3 毛利率 20.7%、净利率 13.6%，增收不增利。</li>
          <li>Q3 单位盈利约 0.082 元/Wh，为阶段低位；消费税开征、出口退税率下调、低毛利产品占比上升、存货减值共同作用。</li>
          <li>2026 9M 经营现金流/净利降至 0.96（2025 年 1.84），capex 421.7 亿（+40%），FCF 仅 194.6 亿。</li>
        </ul></div>
        <div class="card"><h3>分红与资本配置</h3>
          <p><span class="tag fact">事实</span>2025 年 DPS 7.964 元，分红 361 亿、派息率 50%；其中特别股息 4.779 元/股、216.5 亿，一次性。</p>
          <p><span class="tag fact">事实</span>2026-07 公告 200–400 亿元回购、全部注销，上限 573 元/股；截至 10-31 已执行约 53.6 亿。</p>
          <p><span class="tag judge">判断</span>回购注销比特别股息更可持续；但 2026 年 capex 与营运资本占用上升，FCF 对股东回报的覆盖变薄。</p>
        </div>
      </div>
      <div class="note" style="margin-top:2.2mm;">
        <span class="tag calc">计算</span>2026 9M 自由现金流 194.6 亿，年化约 260 亿；对 50% 派息（约 453 亿）覆盖不足，差额需由账上净现金 2,427 亿补足。这是“高分红 + 高 capex”同时进行的代价，也是 2027 年税负上升后最需要跟踪的现金流缺口。
      </div>
    """, 4)


def page_management_dcf():
    mgmt = [
        "创始人曾毓群为实际控制人，通过控股股东与员工持股平台控制；管理层长期稳定，战略执行强。",
        "2025 年分红率提升至 50%（含特别股息）；2026 年推出 200–400 亿元回购并全部注销，是 A 股史上最大单次回购之一。",
        "资本开支仍高：2025 年 423 亿、2026 9M 422 亿；在建产能 321GWh，海外基地（德国/匈牙利/西班牙/印尼）进入投入期。",
        "判断：股东回报意愿明显改善，但资本配置的关键仍是“海外扩张的回报率”与“价格战下的 capex 纪律”。",
    ]
    dcf_rows = [
        ["2026E FCFF", "490 亿元", "净利 906 + 折旧摊销约 500 + 利息 30 − capex 700 − 营运资本 250 ≈ 486，取整 490"],
        ["增速起点", "12.0%", "2027 年；前五年反映储能/海外，后五年收敛"],
        ["折现年数", "10 年", "线性 fade 至终端 g"],
        ["终端 g", "2.5%", "略高于长期通胀，低于名义 GDP"],
        ["WACC", "7.8%", "Ke 8.7%、Kd 2.5%、D/(D+E) 13%"],
        ["净现金", "2,426.7 亿元", "货币 3,698.1 + 交易性金融 627.8 − 有息负债 1,899.2"],
        ["少数股东", "363.4 亿元", "从 EV 到股权价值扣除"],
        ["总股本", "46.2725 亿股", "当前股本，未考虑回购注销"],
        ["企业价值 EV", "14,129 亿元", "10 年 PV + 终值 PV"],
        ["股权价值", "16,193 亿元", "EV − 少数 + 净现金"],
        ["每股价值", "¥349.94", "/ 46.2725 亿股；较现价 +31.6%"],
    ]
    score = [
        ["分红纪律", "4", "派息率 50%；但含特别股息"],
        ["回购执行", "4", "上限 400 亿；已执行 53.6 亿"],
        ["再投资回报", "4", "ROE 24.9%；海外回报待验证"],
        ["杠杆管理", "5", "净现金 2,427 亿"],
        ["关联交易", "3", "产业链内部供应，需看定价"],
    ]
    return page(f"""
      <h2>3. 管理层与资本配置</h2>
      <ul>{''.join(f'<li>{x}</li>' for x in mgmt)}</ul>
      <h2 style="margin-top:3mm;">4. 估值方法一：FCFF DCF</h2>
      <div class="grid2">
        <div>
          {table(["假设 / 步骤","数值","说明"], dcf_rows, ["24%","18%","58%"])}
        </div>
        <div class="card">
          <h3>计算逻辑</h3>
          <div class="formula">FCFF(t) = FCFF(t−1) × (1 + g(t))
PV = Σ FCFF(t) / (1 + WACC)^t
TV = FCFF(10) × (1 + g) / (WACC − g)
EV = PV + TV / (1 + WACC)^10
股权价值 = EV − 少数股东 + 净现金</div>
          <p><span class="tag calc">计算</span>结果：<b>¥{D.DCF_BASE:.2f}</b>；现价 ¥{D.PRICE:.2f}，较 DCF 低 {(1-D.PRICE/D.DCF_BASE)*100:.1f}%。</p>
          <p><span class="tag assume">假设</span>FCFF 490 亿约为 2025 年 FCF 909 亿的 54%，已扣除 2026 年更高的 capex 与营运资本占用；不是把 2025 年峰值现金流直接外推。</p>
          <p><span class="tag judge">判断</span>DCF 对 WACC 与终端 g 敏感；单点价值只作锚，区间比点更重要。</p>
        </div>
      </div>
      <h3 style="margin-top:3mm;">资本配置记分卡（1–5）</h3>
      <div class="grid2">
        <div>{table(["维度","评分","依据"], score, ["24%","12%","64%"])}</div>
        <div class="card"><h3>治理红旗</h3>
          <ul>
            <li>海外基地资本开支大、回报周期长；若回报率低于 WACC，会稀释 ROE。</li>
            <li>特别股息与普通股息混用，容易让投资者高估可持续股息率。</li>
            <li>产业链内部供应（正极、回收）关联交易定价需持续跟踪。</li>
          </ul>
          <p class="small">记分卡是研究判断，不是公司评级；评分低不必然意味着股价下跌。</p>
        </div>
      </div>
    """, 5)


def page_pe_cross():
    pe_rows = [
        ["2027E EPS（基准）", "¥22.50", "低于一致预期 23.57，已反映部分税负"],
        ["目标 PE", "15.3x", "对应 2027E 15% 增长、24% ROE"],
        ["PE 每股价值", f"¥{D.PE_BASE_V:.2f}", "22.50 × 15.3"],
        ["2026E PE（现价）", f"{D.PRICE/D.EPS_2026E:.1f}x", "EPS 19.58"],
        ["2027E PE（现价）", f"{D.PRICE/D.EPS_2027E_BASE:.1f}x", "EPS 22.50"],
        ["PB（现价）", "3.18x", "BPS 83.61"],
    ]
    sens = [["WACC \\ g", "1.5%", "2.0%", "2.5%", "3.0%", "3.5%"]]
    for w, row in zip(D.WACC_GRID, D.SENS):
        sens.append([f"{w:.1%}"] + [f"{x:.1f}" for x in row])
    cross = [
        f"DCF ¥{D.DCF_BASE:.2f} vs PE ¥{D.PE_BASE_V:.2f}：两法相差仅 {abs(D.DCF_BASE/D.PE_BASE_V-1)*100:.1f}%，互相验证；各 50% 得 ¥{D.BLEND_BASE:.2f}。",
        f"现价 ¥{D.PRICE:.2f} 较基准低 {D.MOS*100:.1f}%；反向 DCF 隐含 2026E FCFF 约 {D.DCF_AT_PRICE_F0:.0f} 亿，比基准 490 亿低 {abs(D.DCF_AT_PRICE_F0/D.F0-1)*100:.1f}%。",
        "WACC ±40bp → 每股约 ¥328–376；g ±0.5pct → 约 ¥327–377。折现率与终端增长合计影响约 ±40 元，小于盈利下修的影响。",
    ]
    methods = [
        ["FCFF DCF", f"{D.DCF_BASE:.2f}", "50%", "周期成长；对 WACC/g 敏感，EV 扣少数加净现金"],
        ["PE", f"{D.PE_BASE_V:.2f}", "50%", "2027E EPS × 15.3x；对盈利假设敏感"],
        ["综合", f"{D.BLEND_BASE:.2f}", "100%", "两法各半，避免单边乐观"],
    ]
    checks = [
        "FCFF 490 亿 vs 2025 年 FCF 909 亿：约为 54%，已为 2026 年更高的 capex 与营运资本占用留出缓冲。",
        "WACC 7.8%：Rf 1.8% + 1.15×6.0% = 8.7% Ke；对周期成长股不算苛刻，也不是极度乐观。",
        "终端 g 2.5%：高于长期通胀，低于名义 GDP；若降至 2.0%，DCF 约 327 元。",
        "目标 PE 15.3x：低于 2021–2025 年平均，高于当前 11.8x；已给龙头与净现金溢价，但未给“永久成长”溢价。",
    ]
    return page(f"""
      <h2>5. 估值方法二：PE 与交叉检查</h2>
      <div class="grid2">
        <div>
          <h3>PE 法假设</h3>
          {table(["假设 / 步骤","数值","说明"], pe_rows, ["34%","18%","48%"])}
          <div class="note" style="margin-top:2mm;"><span class="tag calc">计算</span>结果：<b>¥{D.PE_BASE_V:.2f}</b>；现价较其折价 {D.PE_BASE_V/D.PRICE*100-100:.1f}%。</div>
        </div>
        <div>
          <h3>DCF 敏感性：每股价值（元）</h3>
          {table(sens[0], sens[1:], ["16%","16.8%","16.8%","16.8%","16.8%","16.8%"], cls="num")}
          <div class="small" style="margin-top:1.5mm;">基准格 WACC 7.8% / g 2.5% = ¥{D.DCF_BASE:.2f}；整张表均高于现价 ¥{D.PRICE:.2f}，说明“便宜”不依赖单一折现率假设。</div>
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


def page_scenarios():
    rows = [
        ["FCFF 基数（亿元）", "435", "490", "520"],
        ["增速起点", "5.0%", "12.0%", "15.5%"],
        ["WACC", "8.6%", "7.8%", "7.45%"],
        ["2027E EPS（元）", "17.50", "22.50", "25.00"],
        ["目标 PE", "12.5x", "15.3x", "18.0x"],
        ["DCF 每股（元）", f"{D.DCF_BEAR:.2f}", f"{D.DCF_BASE:.2f}", f"{D.DCF_BULL:.2f}"],
        ["PE 每股（元）", "218.75", f"{D.PE_BASE_V:.2f}", "450.00"],
        ["#pos|综合每股（元）", f"#pos|{D.BLEND_BEAR:.2f}", f"#pos|{D.BLEND_BASE:.2f}", f"#pos|{D.BLEND_BULL:.2f}"],
        ["#pos|相对现价", f"#pos|{(D.BLEND_BEAR/D.PRICE-1)*100:+.1f}%", f"#pos|{(D.BLEND_BASE/D.PRICE-1)*100:+.1f}%", f"#pos|{(D.BLEND_BULL/D.PRICE-1)*100:+.1f}%"],
    ]
    rev = [
        ["现价", f"¥{D.PRICE:.2f}", "对应 2026E PE 13.6x、2027E PE 11.8x"],
        ["隐含 2026E FCFF", f"{D.DCF_AT_PRICE_F0:.0f} 亿元", f"比基准 490 亿低 {abs(D.DCF_AT_PRICE_F0/D.F0-1)*100:.1f}%"],
        ["现价对应 2027E PE", "11.8x", "若 EPS 22.50 不变"],
        ["20% 安全边际价", f"¥{D.MOS20_PRICE:.2f}", f"基准 ¥{D.BLEND_BASE:.2f} × 0.8"],
    ]
    triggers = [
        ["单位盈利（元/Wh）", "0.082（2026Q3）", "< 0.06", "下调 2027E EPS 10–15%"],
        ["毛利率", "20.7%（2026Q3）", "< 18% 连续两季", "转向悲观情景"],
        ["全球动力份额", "39.2%（2025）", "< 35%", "护城河预警，下调目标 PE"],
        ["2027E 一致 EPS", "23.57", "下修 > 15%", "重估 PE 基准"],
    ]
    return page(f"""
      <h2>6. 三情景、反向估值与安全边际</h2>
      <div class="grid2">
        <div>
          <h3>情景假设与结果</h3>
          {table(["假设 / 结果","悲观","基准","乐观"], rows, ["34%","22%","22%","22%"])}
          <div class="small" style="margin-top:1.5mm;">悲观：价格战 + 税负无法转嫁 + 海外受阻；基准：单位盈利企稳、税负部分转嫁；乐观：储能/海外高增、估值修复。</div>
        </div>
        <div>
          <h3>反向估值：现价隐含了什么？</h3>
          {table(["项目","数值","说明"], rev, ["36%","22%","42%"])}
          <div class="card" style="margin-top:2.5mm;">
            <h3>安全边际</h3>
            <p style="font-size:9pt;">现价 <b>¥{D.PRICE:.2f}</b>；基准 <b>¥{D.BLEND_BASE:.2f}</b>；安全边际 <b class="pos">+{D.MOS*100:.1f}%</b>。</p>
            <p class="small">安全边际 = 1 − 现价/基准。正值为折价。20% 安全边际价格仅供计算参考，不是买卖指令。</p>
            <p class="small">“相对现价” = 每股价值/现价 − 1；与安全边际分母不同，数值接近但不相等。</p>
          </div>
          <div class="note" style="margin-top:2.5mm;">
            <span class="tag judge">判断</span>现价低于基准 23.4%，但高于悲观情景 219 元约 21%；市场定价的是“盈利下修”，不是“永久性衰退”。
          </div>
        </div>
      </div>
      <h3 style="margin-top:3mm;">情景触发条件</h3>
      {table(["指标","当前","触发阈值","动作"], triggers, ["26%","24%","24%","26%"])}
      <div class="small" style="margin-top:1.5mm;">触发表用于跟踪，不是预测；任一指标持续偏离基准，应重跑估值，而不是只改结论。</div>
      <div class="note" style="margin-top:2.2mm;">
        <b>税负时间轴：</b>2026-09 消费税 2% → 2027-01 出口退税取消（2026-04 已由 9% 降至 6%，2027-01 归零）→ 2027-09 消费税 4%。三个节点分别对应 2026Q3、2027Q1、2027Q4 的毛利率压力；若前两个节点未出现明显提价或成本对冲，第三个节点的 4% 更难转嫁。
      </div>
    """, 7)


def page_risks():
    risks = [
        ["价格战 / 单位盈利下滑", "车企压价 → 单价下降 → 单位盈利 0.082→0.06 元/Wh → 净利下修 20%+", "季度单位盈利、毛利率", "高"],
        ["税负无法转嫁", "消费税 2%→4%、出口退税 9%→0 → 毛利率 −2~3pct → 2027 净利下修", "消费税公告、毛利率", "中高"],
        ["海外地缘政治", "IRA/EU 关税/本地化要求 → 海外收入受限 → 失去 31% 高毛利", "海外收入占比、海外毛利率", "中高"],
        ["技术路线变化", "固态电池提前产业化 → 现有产能与 LFP 技术重估", "固态量产时间、研发投入", "低"],
        ["客户集中", "前五大 39%、第一大 13.7%；大客户转单 → 收入波动", "前五大占比、车企自研", "中"],
        ["存货 / 减值", "存货 945 亿（2025）+ 锂价下行 → 减值 → 利润波动", "存货/营收、减值计提", "中"],
    ]
    risk_rows = "".join(
        f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td class='center {'neg' if r[3]=='高' else ('warn' if r[3]=='中高' else '')}'>{r[3]}</td></tr>"
        for r in risks)
    calendar = [
        ["2026-10", "三季报", "Q3 单位盈利、毛利率、存货"],
        ["2027-03", "年报", "2026 分红、2027 税负指引"],
        ["2027-04", "一季报", "消费税 4% 前的抢装/提价"],
        ["季度", "份额 / 海外", "SNE 份额、海外收入与毛利率"],
        ["事件", "回购 / 税政", "回购执行、消费税与出口退税"],
    ]
    return page(f"""
      <h2>7. 风险、永久性损失与监控</h2>
      <table><colgroup><col style="width:16%"><col style="width:50%"><col style="width:24%"><col style="width:10%"></colgroup>
        <thead><tr><th>风险</th><th>事实 / 机制</th><th>监控指标</th><th class="center">等级</th></tr></thead>
        <tbody>{risk_rows}</tbody>
      </table>
      <h3 style="margin-top:3mm;">三个永久性损失风险</h3>
      <div class="grid3">
        <div class="card bear"><h4>技术被颠覆</h4><p class="small">固态电池/新体系由竞争对手率先量产，CATL 的产能与技术资产被重估。概率低，但一旦发生，估值不是跌 30%，而是商业逻辑重写。</p></div>
        <div class="card bear"><h4>海外市场被强制分割</h4><p class="small">美国/欧盟以安全或本地化理由限制中国电池，CATL 失去海外高毛利市场；国内价格战更激烈，ROE 长期跌破 WACC。</p></div>
        <div class="card bear"><h4>价格战长期化</h4><p class="small">产能过剩 + 车企自研，电池变成标准化大宗品，单位盈利永久性下台阶；CATL 仍是龙头，但赚不到超额利润。</p></div>
      </div>
      <div class="grid2" style="margin-top:2.5mm;">
        <div class="card"><h3>跟踪日历</h3>{table(["时间","事件","看什么"], calendar, ["14%","24%","62%"])}</div>
        <div class="card"><h3>什么会改变结论？</h3>
          <p><span class="tag fact">事实</span>若单位盈利连续两季回升至 0.09 元/Wh 以上、税负成功转嫁、储能出货超预期，2027E EPS 与目标 PE 会同步上修。</p>
          <p><span class="tag judge">判断</span>若 Q4 单位盈利跌破 0.07 元/Wh、2027 年消费税 4% 落地后毛利率跌破 18%，或份额跌破 35%，基准价值应下修至 250 元以下。</p>
        </div>
      </div>
      <h2 style="margin-top:3mm;">8. 来源与免责声明</h2>
      <div class="grid2">
        <div class="small">
          <b>主要来源：</b>公司 2025 年年报、2026 年三季报、2025 年度利润分配公告、2026-07-24 回购公告；财政部/海关总署/税务总局 2026 年第 20 号公告（消费税）、2026 年第 2 号公告（出口退税）；SNE Research 全球份额；东方财富 F10 与机构一致预期。
          <br><br>
          <b>价格日：</b>{D.DATE} 午间，¥{D.PRICE:.2f}；财务截止：2026-09-30。第三方数据仅用于交叉核对。
        </div>
        <div class="note">
          <b>免责声明：</b>本报告为研究记录，不构成任何投资建议、要约或承诺。估值依赖假设，假设变化会显著改变结果。作者可能不持有相关证券，也可能不了解报告发布后的最新变化。读者应独立判断，并咨询持牌专业人士。
        </div>
      </div>
    """, 8)


def build_html():
    pages = [cover(), page_boundary(), page_business(), page_financials(),
             page_management_dcf(), page_pe_cross(), page_scenarios(), page_risks()]
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{''.join(pages)}</body></html>"""


def build_pdf():
    OUT.mkdir(parents=True, exist_ok=True)
    html_path = OUT / f"300750.SZ-估值模型-{D.DATE}.html"
    pdf_path = OUT / f"300750.SZ-估值模型-{D.DATE}.pdf"
    html_path.write_text(build_html(), encoding="utf-8")
    cmd = [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
           f"--print-to-pdf={pdf_path}", html_path.as_uri()]
    subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=180)
    html_path.unlink(missing_ok=True)
    print("saved", pdf_path)


if __name__ == "__main__":
    build_pdf()
