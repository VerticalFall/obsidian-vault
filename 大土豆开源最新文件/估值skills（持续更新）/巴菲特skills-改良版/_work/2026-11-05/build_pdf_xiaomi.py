# -*- coding: utf-8 -*-
"""Build Xiaomi 1810.HK typeset PDF report (8 pages, A4 landscape)."""
import sys, subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import xiaomi_data as D

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / "输出" / "港股" / f"1810.HK-{D.DATE}"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

CSS = """
@page { size: A4 landscape; margin: 9mm; }
* { box-sizing: border-box; }
body { margin:0; font-family:"Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif;
       color:#1F2933; font-size:8pt; line-height:1.35; }
.page { width:279mm; height:192mm; page-break-after:always; position:relative;
        padding:0 0 7mm 0; overflow:hidden; }
.page:last-child { page-break-after:auto; }
.kicker { font-size:6.8pt; color:#8C6D5A; letter-spacing:1.2px; }
h1 { font-size:22pt; margin:1mm 0 0; color:#1F2933; letter-spacing:0.5px; }
h2 { font-size:12pt; color:#2F6B4F; margin:0 0 2mm; border-bottom:0.6pt solid #D9D2C5;
     padding-bottom:1mm; }
h3 { font-size:9pt; color:#2F6B4F; margin:0 0 1.4mm; }
.sub { font-size:8.2pt; color:#5B6770; margin-top:1mm; }
.rule { height:0.6pt; background:#D9D2C5; margin:2.4mm 0; }
.banner { background:#2F6B4F; color:#fff; padding:2.6mm 4mm; font-size:9.4pt;
          font-weight:bold; border-radius:1.2mm; }
.metrics { display:flex; gap:2.4mm; margin-top:2.4mm; }
.metric { flex:1; border:0.4pt solid #E8E2D5; border-radius:1.2mm; padding:2.1mm 2.5mm;
          background:#FCFBF7; }
.metric .k { font-size:6.8pt; color:#5B6770; }
.metric .v { font-size:14.5pt; font-weight:bold; color:#2F6B4F; margin-top:0.4mm; }
.metric .n { font-size:6.5pt; color:#5B6770; margin-top:0.3mm; }
.grid2 { display:grid; grid-template-columns:1fr 1fr; gap:3mm; margin-top:2.4mm; }
.grid3 { display:grid; grid-template-columns:1fr 1fr 1fr; gap:3mm; margin-top:2.4mm; }
.card { border:0.4pt solid #E8E2D5; border-radius:1.2mm; padding:2.1mm 2.7mm;
        background:#fff; }
.card.green { background:#F3F8F4; border-color:#C9DDD1; }
.card.gold { background:#FBF7EA; border-color:#E6D9B8; }
.card.red { background:#FBF0EE; border-color:#E8C9C3; }
table { width:100%; border-collapse:collapse; font-size:7.05pt; }
th { background:#EFE8D8; color:#5B4A3A; font-weight:bold; padding:1.05mm 0.9mm;
     border:0.35pt solid #D9D2C5; text-align:center; }
td { padding:0.85mm 0.9mm; border:0.35pt solid #D9D2C5; vertical-align:middle; }
td.l { text-align:left; } td.r { text-align:right; } td.c { text-align:center; }
tr.total td { background:#F7EFD2; font-weight:bold; }
.small { font-size:6.9pt; color:#5B6770; }
.note { background:#FBF7EA; border-left:0.9mm solid #C9A227; padding:1.7mm 2.5mm;
        font-size:6.7pt; color:#5B6770; margin-top:2mm; }
.tag { display:inline-block; font-size:6.1pt; padding:0.15mm 0.9mm; border-radius:0.7mm;
       margin-right:0.8mm; font-weight:bold; }
.fact { background:#E3EFE7; color:#2F6B4F; } .calc { background:#E8F0FB; color:#1A73E8; }
.assume { background:#F7EFD2; color:#8C6D5A; } .judge { background:#F8E5E1; color:#B23A2E; }
ul { margin:0.5mm 0 0 3.5mm; padding:0; }
li { margin:0.35mm 0; font-size:7.4pt; }
.footer { position:absolute; left:0; right:0; bottom:0; display:flex;
          justify-content:space-between; font-size:6.1pt; color:#8C6D5A;
          border-top:0.35pt solid #E8E2D5; padding-top:0.9mm; }
.bar { height:3.2mm; background:#E8EFE9; border-radius:1mm; overflow:hidden; }
.bar > div { height:3.2mm; background:#2F6B4F; }
.big { font-size:16pt; font-weight:bold; color:#2F6B4F; }
.mid { font-size:10pt; font-weight:bold; }
.kv { display:flex; justify-content:space-between; border-bottom:0.3pt dotted #D9D2C5;
      padding:0.7mm 0; font-size:7.3pt; }
.kv b { color:#1F2933; }
"""


def table(headers, rows, widths=None, aligns=None, total_rows=()):
    colg = ""
    if widths:
        colg = "<colgroup>" + "".join(f'<col style="width:{w}">' for w in widths) + "</colgroup>"
    thead = "<tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr>"
    body = []
    for i, row in enumerate(rows):
        cls = ' class="total"' if i in total_rows else ""
        cells = "".join(
            f'<td class="{aligns[j] if aligns else "l"}">{v}</td>' for j, v in enumerate(row)
        )
        body.append(f"<tr{cls}>{cells}</tr>")
    return f"<table>{colg}<thead>{thead}</thead><tbody>{''.join(body)}</tbody></table>"


def page(content, n):
    return f'<div class="page">{content}<div class="footer"><span>巴菲特框架研究 · 小米集团 1810.HK · 2026-11-05 · 仅供研究记录</span><span>{n} / 8</span></div></div>'


def hk(v):
    return f"HK${v / D.FX:,.2f}"


def pct(x, d=1):
    return f"{x*100:+.{d}f}%"


def num(x, d=1):
    return f"{x:,.{d}f}"


# ---------------------------------------------------------------- page 1
def p1():
    metrics = f"""
    <div class="metrics">
      <div class="metric"><div class="k">现价（2026-11-05 收盘）</div><div class="v">HK${D.PRICE_HKD:.2f}</div><div class="n">¥{D.PRICE:.2f}；前收 HK$28.76</div></div>
      <div class="metric"><div class="k">2026E PE</div><div class="v">{D.MARKET_CAP/D.NP_ADJ_2026E:.1f}x</div><div class="n">经调整净利 250 亿元（-36%）</div></div>
      <div class="metric"><div class="k">2027E PE</div><div class="v">{D.MARKET_CAP/D.NP_ADJ_2027E_BASE:.1f}x</div><div class="n">经调整净利 350 亿元（+40%）</div></div>
      <div class="metric"><div class="k">安全边际</div><div class="v">+{D.MOS*100:.1f}%</div><div class="n">综合基准 HK${D.BLEND_BASE/D.FX:.2f}</div></div>
    </div>"""

    scen = table(
        ["情景", "DCF", "PE", "综合", "相对现价", "核心假设"],
        [
            ["悲观", hk(D.DCF_BEAR), hk(D.PE_BEAR_V), hk(D.BLEND_BEAR), pct(D.BLEND_BEAR/D.PRICE-1), "存储涨价延续；汽车价格战；2027 净利 280 亿"],
            ["基准", hk(D.DCF_BASE), hk(D.PE_BASE_V), hk(D.BLEND_BASE), pct(D.BLEND_BASE/D.PRICE-1), "2027 净利 350 亿；汽车亏损收窄；手机毛利修复"],
            ["乐观", hk(D.DCF_BULL), hk(D.PE_BULL_V), hk(D.BLEND_BULL), pct(D.BLEND_BULL/D.PRICE-1), "2027 净利 420 亿；汽车扭亏；AI 变现超预期"],
        ],
        ["12%", "12%", "12%", "12%", "13%", "39%"],
        ["c", "r", "r", "r", "r", "l"],
        total_rows=(1,),
    )

    cross = table(
        ["项目", "结果", "说明"],
        [
            ["FCFF DCF", hk(D.DCF_BASE), "F0 200 亿、g 13%→3%、WACC 9.6%"],
            ["PE 法", hk(D.PE_BASE_V), "2027E EPS 1.354 元 × 22x"],
            ["综合基准", hk(D.BLEND_BASE), "DCF 50% + PE 50%"],
            ["现价", hk(D.PRICE_HKD), f"市值 HK${D.MARKET_CAP_HKD:,.0f} 亿"],
            ["安全边际", f"+{D.MOS*100:.1f}%", "1 − 现价 / 基准"],
            ["评级 / 置信度", "合理 / 中", "观察，等更好价格或盈利拐点"],
        ],
        ["27%", "23%", "50%"],
        ["l", "r", "l"],
        total_rows=(2,),
    )

    return page(f"""
      <div class="kicker">巴菲特框架研究 · 港股 · 2026-11-05</div>
      <h1>小米集团 <span style="font-size:13pt;color:#5B6770;">1810.HK</span></h1>
      <div class="sub">手机 × AIoT / 智能电动汽车 / 互联网服务｜价格日 2026-11-05 收盘｜现价 HK${D.PRICE_HKD:.2f}｜市值 HK${D.MARKET_CAP_HKD:,.0f} 亿</div>
      <div class="rule"></div>
      <div class="banner">好生意，合理价格，但没有安全边际。现价较综合基准 HK${D.BLEND_BASE/D.FX:.2f} 低 {D.MOS*100:.1f}%；20% 安全边际价 HK${D.MOS20_PRICE/D.FX:.2f}，现价仍高 {(D.PRICE/D.MOS20_PRICE-1)*100:.0f}%。</div>
      {metrics}
      <div class="grid2">
        <div class="card"><h3>三情景每股价值（港元）</h3>{scen}</div>
        <div class="card"><h3>估值交叉与结论</h3>{cross}</div>
      </div>
      <div class="grid3">
        <div class="card green"><h3>多头论点</h3>
          <ul><li>全球手机份额 13.3%、位列第三；IoT 与互联网服务提供高毛利现金流。</li>
          <li>2025 年经调整净利 392 亿元、经营现金流 341 亿元；净现金 1,800 亿元。</li>
          <li>2026 年回购上限 200 亿港元、全部注销；汽车 2027 年有望减亏。</li></ul></div>
        <div class="card red"><h3>空头论点</h3>
          <ul><li>2026Q2 经调整净利 62.2 亿元、同比 -42.6%；手机毛利率仅 8.5%。</li>
          <li>汽车分部亏损 26 亿元；澎程放量仍需验证，价格战未止。</li>
          <li>2026E 净利 -36%，2026E PE 27.3x；不分红，回购被股权激励部分抵消。</li></ul></div>
        <div class="card gold"><h3>结论</h3>
          <ul><li><b>合理，不是便宜。</b>基准 HK${D.BLEND_BASE/D.FX:.2f}，现价仅低 {D.MOS*100:.1f}%。</li>
          <li>安全边际不足：20% 边际价 HK${D.MOS20_PRICE/D.FX:.2f}，现价仍高 {(D.PRICE/D.MOS20_PRICE-1)*100:.0f}%。</li>
          <li>等 26 港元以下，或 2027 年盈利拐点确认。</li></ul></div>
      </div>
      <div class="note">事实：财报与价格；计算：市值、PE、DCF、敏感性；假设：2026E/2027E 净利、F0、WACC、g；判断：护城河、评级。数据截至 2026-06-30 中报，Q3 官方业绩 2026-11-24 发布，本文用券商前瞻。不构成投资建议。</div>
    """, 1)


# ---------------------------------------------------------------- page 2
def p2():
    boundary = table(
        ["项目", "内容"],
        [
            ["价格日", "2026-11-05 收盘 HK$30.90；前收 HK$28.76"],
            ["财务截止", "2026-06-30 中报"],
            ["Q3 状态", "官方业绩 2026-11-24 发布；本文用券商前瞻"],
            ["股本 / 市值", f"{D.SHARES:.1f} 亿股；HK${D.MARKET_CAP_HKD:,.0f} 亿 / ¥{D.MARKET_CAP:,.0f} 亿"],
            ["汇率", "HKD/CNY 0.85601（中国货币网 2026-11-05）"],
            ["2026E", "经调整净利 250 亿元（本文估计，非公司指引）"],
            ["2027E", "经调整净利 350 亿元（本文假设）"],
            ["净现金", "2,193 − 393 = 1,800 亿元（2026H1）"],
        ],
        ["26%", "74%"], ["l", "l"],
    )
    definitions = f"""
      <div class="card">
        <h3>口径说明</h3>
        <div class="kv"><span>经调整净利</span><b>非 IFRS，剔除 SBC、投资公允价值变动</b></div>
        <div class="kv"><span>市值</span><b>{D.SHARES:.1f} 亿股 × HK${D.PRICE_HKD:.2f}</b></div>
        <div class="kv"><span>净现金</span><b>现金储备 2,193 − 借款 393</b></div>
        <div class="kv"><span>DCF</span><b>FCFF = 净利 + D&A + SBC − capex − WC</b></div>
        <div class="kv"><span>每股价值</span><b>股权价值 ÷ 258.4 亿股</b></div>
        <div class="kv"><span>汇率</span><b>港元价值 = 人民币价值 ÷ 0.85601</b></div>
      </div>"""
    chain = table(
        ["步骤", "内容", "用途"],
        [
            ["1", "FY2025 年报（2026-03-24）", "历史基线：收入、利润、分部、交付"],
            ["2", "2026Q1 业绩（2026-05-26）", "手机毛利率、汽车交付、经调整净利"],
            ["3", "2026 中报（2026-08-18）", "Q2 分部、现金储备、借款、研发"],
            ["4", "Q3 券商前瞻（2026-11）", "Q3 净利 41–50 亿、交付 10.1–10.3 万"],
            ["5", "DCF + PE + 情景", "得到基准 HK$32.08、区间 HK$19.89–44.86"],
        ],
        ["8%", "47%", "45%"], ["c", "l", "l"],
    )
    return page(f"""
      <h2>1. 数据边界、口径与能力圈</h2>
      <div class="grid2">
        <div class="card"><h3>数据边界</h3>{boundary}</div>
        {definitions}
      </div>
      <div class="grid2">
        <div class="card"><h3>能力圈</h3>
          <p><span class="tag fact">能看懂</span>手机/IoT 是硬件生意，看份额、ASP、毛利率；互联网是变现层，看 MAU 与 ARPU；汽车看交付、ASP、单车亏损。</p>
          <p><span class="tag assume">看不清</span>汽车执行力与价格战底部、AI 投入回报、存储周期持续时间、印度/欧洲监管。</p>
          <p><span class="tag judge">结论</span>适合“正常化盈利 + 情景估值”，不适合用单季利润线性外推；汽车业务应用期权思维，而非确定性现金流。</p>
        </div>
        <div class="card"><h3>研究链</h3>{chain}</div>
      </div>
      <div class="note"><b>数据质量提示：</b>① 2026Q3 官方数据未发布，Q3 净利与交付为券商预测，误差可能较大；② 2026E/2027E 为本文估计，中金 247/403 亿、华泰 254/336 亿，分歧显著；③ 经调整净利为非 IFRS；④ 分部毛利率受“其他”与内部抵销影响；⑤ 股权激励持续发行新股，股本可能高于 258.4 亿股。</div>
    """, 2)


# ---------------------------------------------------------------- page 3
def p3():
    qa = [
        ["1. 我能看懂吗？", "能。手机/IoT 看份额、ASP、毛利率；互联网看 MAU/ARPU；汽车看交付、ASP、单车亏损。"],
        ["2. 护城河是什么？", "品牌 + 生态（手机/家居/汽车互联）+ 成本效率 + 渠道；手机全球第三、份额 13.3%；但硬件没有提价权。"],
        ["3. 能长久吗？", "手机与 IoT 大概率长期存在；汽车是十年维度新业务，胜率未定；AI 可能重构入口。"],
        ["4. 资本回报如何？", "2025 年 ROE 约 18%；手机轻资产高回报，汽车重资产拉低整体回报。"],
        ["5. 增长来自哪里？", "汽车（2025 年收入 1,033 亿、+222%）、IoT 出海、互联网服务、AI；手机进入成熟期。"],
        ["6. 管理层可信吗？", "雷军创始人控制，执行力强；回购注销、不分红；但汽车/AI 投入大，资本配置纪律待验证。"],
        ["7. 最大风险是什么？", "存储涨价压制手机毛利；汽车价格战与放量不及预期；AI 投入回报低；股权激励稀释。"],
        ["8. 估值合理吗？", "2026E PE 27.3x、2027E PE 19.5x；基准 HK$32.08，现价 HK$30.90，仅高 3.7%；合理，无安全边际。"],
    ]
    qa_t = table(["问题", "回答"], qa, ["18%", "82%"], ["l", "l"])
    seg25 = table(
        ["业务", "收入", "同比", "占比", "毛利率"],
        [
            ["智能手机", "1,864.0", "-2.8%", "40.8%", "10.9%"],
            ["IoT 与生活消费", "1,232.0", "+18.3%", "26.9%", "21.0%"],
            ["互联网服务", "374.0", "+9.7%", "8.2%", "76.5%"],
            ["智能电动汽车及 AI", "1,060.7", "+223.8%", "23.2%", "24.3%"],
            ["其他", "41.2", "-12.0%", "0.9%", "30.0%"],
            ["合计", "4,572.9", "+25.0%", "100%", "22.3%"],
        ],
        ["30%", "18%", "16%", "16%", "20%"],
        ["l", "r", "r", "r", "r"],
        total_rows=(5,),
    )
    seg26 = table(
        ["业务", "收入", "同比", "毛利率"],
        [
            ["智能手机", "421.0", "-7.5%", "8.5%"],
            ["IoT 与生活消费", "313.0", "-19.2%", "20.1%"],
            ["互联网服务", "90.0", "-0.6%", "76.8%"],
            ["智能电动汽车及 AI", "249.0", "+17.1%", "19.2%"],
        ],
        ["38%", "22%", "20%", "20%"],
        ["l", "r", "r", "r"],
    )
    moat = [("品牌与用户心智", 4), ("生态与切换成本", 4), ("成本与渠道效率", 4), ("技术壁垒", 3), ("定价权", 2)]
    bars = "".join(
        f'<div class="kv"><span>{name}</span><b>{score} / 5</b></div>'
        f'<div class="bar" style="margin-bottom:1.3mm;"><div style="width:{score*20}%"></div></div>'
        for name, score in moat
    )
    return page(f"""
      <h2>2. 生意：八个问题</h2>
      {qa_t}
      <div class="grid2" style="margin-top:2mm;">
        <div class="card"><h3>2025 年收入结构（亿元）</h3>{seg25}
          <div class="small" style="margin-top:1mm;">汽车收入首破千亿、同比 +222%；手机收入 -2.8%，但 ASP 提升。</div></div>
        <div class="card"><h3>2026Q2 分部（最新实际）</h3>{seg26}
          <div class="small" style="margin-top:1mm;">集团毛利率 19.8%（-2.7pct）；互联网服务 76.8% 是毛利最大来源；汽车亏损 26 亿元。</div></div>
      </div>
      <div class="grid2" style="margin-top:2mm;">
        <div class="card"><h3>护城河评分：3.4 / 5</h3>{bars}
          <div class="small">品牌与生态强、定价权弱；属于“好生意”，不是“伟大生意”。</div></div>
        <div class="card"><h3>商业本质</h3>
          <p><span class="tag fact">硬件</span>手机/IoT 毛利率低，靠规模、周转与渠道效率赚钱；硬件是入口，不是利润中心。</p>
          <p><span class="tag fact">互联网</span>广告、游戏、金融科技毛利率 76%+，是利润的“放大器”；但收入占比仅 8%。</p>
          <p><span class="tag judge">汽车</span>第二增长曲线，也是资本黑洞：2025 年首年经营盈利 9 亿，2026 年因新车与价格战重新转亏。</p>
        </div>
      </div>
    """, 3)


# ---------------------------------------------------------------- page 4
def p4():
    fin = table(
        ["指标", "2021", "2022", "2023", "2024", "2025", "2026E"],
        [
            ["营业收入", "3,283.1", "2,800.4", "2,709.7", "3,659.1", "4,572.9", "4,400.0"],
            ["归母净利", "193.4", "24.7", "174.8", "235.8", "415.7", "250.0"],
            ["经调整净利", "220.4", "85.0", "192.7", "272.4", "391.7", "250.0"],
            ["经营现金流", "428.0", "-43.9", "413.0", "393.0", "341.4", "120.0"],
            ["资本开支", "50.0", "58.0", "62.7", "73.0", "127.7", "180.0"],
            ["自由现金流", "378.0", "-101.9", "350.3", "320.0", "213.7", "-60.0"],
            ["EPS（元）", "0.76", "0.10", "0.70", "0.94", "1.62", "0.97"],
            ["ROE（%）", "12.0", "1.5", "10.0", "12.0", "18.0", "9.0"],
        ],
        ["24%", "12.7%", "12.7%", "12.7%", "12.7%", "12.7%", "12.7%"],
        ["l", "r", "r", "r", "r", "r", "r"],
        total_rows=(2,),
    )
    ratios = table(
        ["比率", "2021", "2022", "2023", "2024", "2025", "2026E"],
        [
            ["收入增速", "—", "-14.7%", "-3.2%", "+35.0%", "+25.0%", "-3.8%"],
            ["经调整净利率", "6.7%", "3.0%", "7.1%", "7.4%", "8.6%", "5.7%"],
            ["毛利率", "17.7%", "17.0%", "21.2%", "20.9%", "22.3%", "20.0%"],
            ["经营现金流/净利", "2.21x", "-1.78x", "2.36x", "1.67x", "0.82x", "0.48x"],
            ["资本开支/收入", "1.5%", "2.1%", "2.3%", "2.0%", "2.8%", "4.1%"],
        ],
        ["27%", "12%", "12%", "12%", "12%", "12%", "13%"],
        ["l", "r", "r", "r", "r", "r", "r"],
    )
    bs = table(
        ["项目", "金额", "说明"],
        [
            ["现金储备", "2,193", "含现金、定期存款与理财"],
            ["借款总额", "393", "短期 97.1 + 长期 295.7"],
            ["净现金", "1,800", "现金储备 − 借款"],
            ["2026H1 经营现金流", "20.5", "营运资本与汽车投入占用"],
            ["2026H1 资本开支", "60.0", "Q2 36.21 亿，汽车/AI 23.83 亿"],
            ["2026H1 自由现金流", "-39.5", "经营现金流 − 资本开支"],
            ["2026H1 研发投入", "182", "占收入 8.7%"],
        ],
        ["38%", "18%", "44%"], ["l", "r", "l"],
    )
    return page(f"""
      <h2>3. 财务：增长、现金流与股东回报</h2>
      <div class="grid2">
        <div class="card"><h3>2021–2026E 损益（亿元）</h3>{fin}</div>
        <div class="card"><h3>关键比率</h3>{ratios}
          <div class="small" style="margin-top:1mm;">2026E 为本文估计；2025 年经调整净利 392 亿元、同比 +43.8%。</div></div>
      </div>
      <div class="grid2" style="margin-top:2mm;">
        <div class="card"><h3>2026H1 现金流与资产负债表（亿元）</h3>{bs}</div>
        <div class="card"><h3>关键读数</h3>
          <ul><li>2025 年自由现金流 214 亿元，覆盖回购与投资；2026H1 转负 -39.5 亿元，主因汽车产能、AI 投入与营运资本。</li>
          <li>账上现金储备 2,193 亿元、净现金 1,800 亿元，占总市值 {D.NET_CASH/D.MARKET_CAP*100:.1f}%；短期不存在流动性风险。</li>
          <li>2026 年回购上限 200 亿港元、全部注销；但 2025 年总股本从 251 亿增至 260 亿，股权激励稀释抵消部分回购。</li>
          <li>2025 年研发 331 亿元（+37.8%），2026H1 182 亿元（8.7%）；投入强度上升压制短期利润。</li></ul></div>
      </div>
      <div class="note">自由现金流 = 经营现金流 − 资本开支。2026H1 经营现金流仅 20.5 亿元，是“利润低谷 + 营运资本占用”的组合，不是现金流断裂；但若汽车业务持续亏损，2027 年 FCF 可能继续为负。</div>
    """, 4)


# ---------------------------------------------------------------- page 5
def p5():
    mgmt = """
      <div class="card"><h3>管理层与资本配置</h3>
        <ul>
          <li><b>创始人控制：</b>雷军任董事长兼 CEO，A/B 双重股权；战略执行力强，汽车业务亲自带队。</li>
          <li><b>股东回报：</b>上市以来零现金分红；回购全部注销。2025 年回购约 63 亿港元，旧计划累计 146 亿港元；2026 年新计划上限 200 亿港元，至 9 月已执行约 123 亿。</li>
          <li><b>再投资：</b>2025 年研发 331 亿元、资本开支 128 亿元；汽车与 AI 是主要投向，回报周期 3–5 年。</li>
          <li><b>治理关注：</b>双重股权、股权激励稀释（2026 年 7 月回购 7,980 万股、同期发行 5,419 万股）、印度/欧洲监管。</li>
        </ul>
      </div>"""
    score = table(
        ["维度", "评分", "依据"],
        [
            ["分红纪律", "1", "零股息；以回购替代"],
            ["回购执行", "5", "200 亿港元上限、全部注销"],
            ["再投资回报", "3", "汽车/AI 投入大，回报待验证"],
            ["杠杆管理", "4", "净现金 1,800 亿元"],
            ["稀释控制", "2", "股权激励持续发行新股"],
        ],
        ["28%", "12%", "60%"], ["l", "c", "l"],
    )
    dcf = table(
        ["假设 / 步骤", "数值", "说明"],
        [
            ["2026E FCFF", "200 亿元", "净利 250 + D&A 130 + SBC 40 − capex 180 − WC 40"],
            ["增速起点", "13.0%", "2027 年；前五年反映汽车放量"],
            ["折现年数", "10 年", "线性 fade 至终端 g"],
            ["终端 g", "3.0%", "略高于长期通胀"],
            ["WACC", "9.6%", "Ke 11.0%、Kd 3.0%、D/(D+E) 6%"],
            ["净现金", "1,800 亿元", "2026H1"],
            ["总股本", "258.4 亿股", "当前股本"],
            ["企业价值 EV", "4,690.5 亿元", "10 年 PV + 终值 PV"],
            ["股权价值", "6,490.5 亿元", "EV + 净现金 − 少数股东"],
            ["每股价值", "¥25.12 / HK$29.34", "÷ 258.4 亿股"],
        ],
        ["26%", "24%", "50%"], ["l", "r", "l"],
        total_rows=(9,),
    )
    formula = """
      <div class="card" style="background:#F7F4EC;">
        <h3>计算逻辑</h3>
        <div style="font-family:Consolas,monospace;font-size:7.2pt;line-height:1.7;">
          FCFF(t) = FCFF(t−1) × (1 + g(t))<br>
          PV = Σ FCFF(t) / (1 + WACC)^t<br>
          TV = FCFF(10) × (1 + g) / (WACC − g)<br>
          EV = PV + TV / (1 + WACC)^10<br>
          Equity = EV + net cash − minority
        </div>
        <p style="margin-top:1.5mm;"><span class="tag calc">计算</span>DCF HK$29.34；现价 HK$30.90，较 DCF 高 5.3%。</p>
        <p><span class="tag assume">假设</span>F0 200 亿元低于 2025 年 FCF 214 亿元，已为 2026 年更高的 capex 与营运资本留出缓冲。</p>
      </div>"""
    return page(f"""
      <h2>3. 管理层、资本配置与估值方法一：DCF</h2>
      <div class="grid2">
        {mgmt}
        <div class="card"><h3>资本配置记分卡（1–5）</h3>{score}
          <div class="small" style="margin-top:1mm;">记分卡是研究判断，不是公司评级。</div></div>
      </div>
      <div class="grid2" style="margin-top:2mm;">
        <div class="card"><h3>FCFF DCF（基准）</h3>{dcf}</div>
        {formula}
      </div>
      <div class="note"><b>DCF 的局限：</b>汽车业务仍处投入期，F0 对 capex 与营运资本假设敏感；WACC 每变动 0.3pct，价值变动约 5–6%。DCF 给出 HK$29.34，低于现价，说明当前现金流并不支持 30.90 港元——估值依赖 2027 年盈利修复。</div>
    """, 5)


# ---------------------------------------------------------------- page 6
def p6():
    pe = table(
        ["项目", "数值", "说明"],
        [
            ["2027E 经调整净利", "350 亿元", "中金 403、华泰 336；取中值偏保守"],
            ["2027E EPS", "¥1.354", "350 ÷ 258.4 亿股"],
            ["目标 PE", "22x", "对应 2027E 增速 +40%、ROE 修复"],
            ["PE 每股价值", "¥29.80 / HK$34.81", "1.354 × 22"],
            ["现价对应 2027E PE", "19.5x", "HK$30.90 / HK$1.58"],
        ],
        ["34%", "26%", "40%"], ["l", "r", "l"],
        total_rows=(3,),
    )
    sens_rows = []
    for i, w in enumerate(D.SENS_WACC):
        row = [f"{w*100:.1f}%"]
        for v in D.SENS[i]:
            row.append(f"{v/D.FX:.1f}")
        sens_rows.append(row)
    sens = table(
        ["WACC \\ g", "2.50%", "2.75%", "3.00%", "3.25%", "3.50%"],
        sens_rows,
        ["18%", "16.4%", "16.4%", "16.4%", "16.4%", "16.4%"],
        ["c", "r", "r", "r", "r", "r"],
        total_rows=(2,),
    )
    cross = table(
        ["检查项", "数值", "读数"],
        [
            ["DCF", "HK$29.34", "低于现价 5.3%"],
            ["PE", "HK$34.81", "高于现价 12.7%"],
            ["综合基准", "HK$32.08", "高于现价 3.8%"],
            ["TTM PE", "22.9x", "经调整净利 299 亿元"],
            ["EV/2026E 经调整净利", "20.1x", "扣除净现金 1,800 亿元"],
            ["券商目标价", "HK$32–35", "中金 34、华泰 32、花旗 33.2、大和 35"],
        ],
        ["34%", "24%", "42%"], ["l", "r", "l"],
    )
    return page(f"""
      <h2>4. 估值方法二：PE 与交叉检查</h2>
      <div class="grid2">
        <div class="card"><h3>PE 法（2027E）</h3>{pe}
          <div class="small" style="margin-top:1mm;">2026E PE 27.3x 是“利润低谷”的读数；2027E PE 19.5x 才是正常化后的估值。</div></div>
        <div class="card"><h3>交叉检查</h3>{cross}
          <div class="small" style="margin-top:1mm;">DCF 与 PE 相差 18.6%，分歧来自“2027 年盈利修复”假设；券商目标价集中在 32–35 港元。</div></div>
      </div>
      <div class="grid2" style="margin-top:2mm;">
        <div class="card"><h3>敏感性：DCF 每股价值（港元），WACC × g</h3>{sens}
          <div class="small" style="margin-top:1mm;">整张表 HK$26.4–33.4；现价 HK$30.90 位于中枢附近，说明“合理”不依赖单点假设。</div></div>
        <div class="card"><h3>方法比较</h3>
          <table><thead><tr><th>方法</th><th>优点</th><th>局限</th></tr></thead><tbody>
            <tr><td class="l">DCF</td><td class="l">反映现金流与资本开支</td><td class="l">对 F0、WACC 敏感；汽车投入期难预测</td></tr>
            <tr><td class="l">PE</td><td class="l">反映盈利修复与市场定价</td><td class="l">2027E 净利分歧大（336–403 亿）</td></tr>
            <tr><td class="l">综合</td><td class="l">两法各 50%，避免单边乐观</td><td class="l">仍依赖 2027 年修复假设</td></tr>
          </tbody></table>
          <p class="small" style="margin-top:1.5mm;"><span class="tag judge">判断</span>合理价格的核心不是“现在便宜”，而是“2027 年净利能否回到 350 亿以上”。</p>
        </div>
      </div>
    """, 6)


# ---------------------------------------------------------------- page 7
def p7():
    scen = table(
        ["情景", "F0", "g 起点", "WACC", "2027E EPS", "目标 PE", "DCF", "PE", "综合", "相对现价"],
        [
            ["悲观", "160", "5.0%", "10.6%", "¥1.084", "17x", "15.63", "18.42", "17.03", "-35.6%"],
            ["基准", "200", "13.0%", "9.6%", "¥1.354", "22x", "25.12", "29.80", "27.46", "+3.8%"],
            ["乐观", "230", "17.0%", "9.0%", "¥1.625", "25x", "36.17", "40.63", "38.40", "+45.2%"],
        ],
        ["10%", "8%", "9%", "9%", "12%", "10%", "10%", "10%", "10%", "12%"],
        ["c", "r", "r", "r", "r", "r", "r", "r", "r", "r"],
        total_rows=(1,),
    )
    reverse = table(
        ["项目", "数值", "说明"],
        [
            ["现价", "HK$30.90", "2026-11-05 收盘"],
            ["综合基准", "HK$32.08", "DCF 50% + PE 50%"],
            ["安全边际", "+3.7%", "1 − 现价 / 基准"],
            ["20% 安全边际价", "HK$25.66", "基准 × 0.8"],
            ["现价隐含 2026E FCFF", "214.7 亿元", "比基准 200 亿高 7.3%"],
        ],
        ["38%", "26%", "36%"], ["l", "r", "l"],
    )
    triggers = table(
        ["指标", "当前", "触发阈值", "动作"],
        [
            ["2026Q4 汽车交付", "10 月 >5 万", "< 4.5 万/月", "下调 2027 年汽车收入"],
            ["汽车分部亏损", "Q2 -26 亿", "连续两季 >35 亿", "转向悲观情景"],
            ["手机毛利率", "8.5%（Q2）", "<8% 连续两季", "下调 2027E 净利 10%"],
            ["IoT 毛利率", "20.1%（Q2）", "<18%", "检查存储成本"],
            ["2027E 经调整净利", "350 亿（本文）", "下修 >15%", "重估 PE 基准"],
            ["回购执行", "约 123 亿港元", "<100 亿（12 个月）", "股东回报低于预期"],
        ],
        ["30%", "22%", "24%", "24%"], ["l", "r", "l", "l"],
    )
    return page(f"""
      <h2>5. 三情景、反向估值与触发条件</h2>
      <div class="card"><h3>情景假设与结果（人民币元）</h3>{scen}
        <div class="small" style="margin-top:1mm;">悲观 = 存储涨价延续 + 汽车价格战；基准 = 2027 年净利 350 亿；乐观 = 汽车扭亏 + AI 变现。</div></div>
      <div class="grid2" style="margin-top:2mm;">
        <div class="card"><h3>反向估值：现价隐含了什么？</h3>{reverse}
          <p class="small" style="margin-top:1mm;"><span class="tag judge">判断</span>现价隐含 F0 214.7 亿元，比本文基准 200 亿高 7.3%，但低于 2025 年 FCF 214 亿元——市场定价“温和修复”，不是“强复苏”。</p></div>
        <div class="card"><h3>安全边际</h3>
          <div class="big">+{D.MOS*100:.1f}%</div>
          <p class="small">现价 HK$30.90，基准 HK$32.08；正安全边际但不足 20%。20% 安全边际价 HK$25.66，现价仍高 {(D.PRICE/D.MOS20_PRICE-1)*100:.0f}%。</p>
          <p class="small">“相对现价” = 每股价值 / 现价 − 1；与安全边际分母不同，数值接近但不相等。</p></div>
      </div>
      <div class="card" style="margin-top:2mm;"><h3>监控触发条件</h3>{triggers}
        <div class="small" style="margin-top:1mm;">存储周期：2025H2 涨价 → 2026Q1 手机毛利率 10.1% → Q2 8.5% → Q3 仍承压；若 2027 年存储价格回落，手机毛利率有望修复至 10% 以上。</div></div>
    """, 7)


# ---------------------------------------------------------------- page 8
def p8():
    risks = table(
        ["风险", "机制", "监控指标", "等级"],
        [
            ["存储涨价", "内存/闪存涨价 → 手机毛利率 8.5% → 净利下修", "手机毛利率、存储现货价", "高"],
            ["汽车价格战", "车企降价 → ASP 下降 → 汽车亏损扩大", "交付量、ASP、分部亏损", "高"],
            ["澎程不及预期", "新车订单/产能爬坡慢 → 2026 年目标落空", "月交付、订单 backlog", "中高"],
            ["AI 投入回报低", "capex/研发上升 → 费用率上升 → FCF 承压", "研发费用率、AI 收入", "中"],
            ["股权激励稀释", "每年发行新股 → 抵消回购注销", "总股本、回购注销数", "中"],
            ["地缘政治", "印度/欧洲贸易与数据监管", "海外收入占比、政策", "中"],
        ],
        ["18%", "46%", "26%", "10%"], ["l", "l", "l", "c"],
    )
    cal = table(
        ["时间", "事件", "看什么"],
        [
            ["2026-11-24", "Q3 业绩", "经调整净利 41–50 亿？汽车亏损 31–36 亿？手机毛利率？"],
            ["2026-12", "11 月交付", "澎程月销能否稳定 2 万辆以上"],
            ["2027-03", "2026 年报", "全年交付、汽车分部亏损、2027 指引、回购进度"],
            ["2027-05", "Q1 业绩", "存储价格是否回落；手机毛利率修复"],
            ["季度", "交付 / 份额", "月交付、全球手机份额、IoT 增速"],
        ],
        ["14%", "18%", "68%"], ["c", "l", "l"],
    )
    return page(f"""
      <h2>6. 风险、永久性损失与跟踪</h2>
      <div class="card"><h3>主要风险矩阵</h3>{risks}</div>
      <div class="grid3" style="margin-top:2mm;">
        <div class="card red"><h3>永久性损失 ①</h3><p><b>汽车业务失败。</b>投入数百亿、年销未达规模，长期亏损吞噬手机现金流；概率中低，但一旦发生，估值逻辑重写。</p></div>
        <div class="card red"><h3>永久性损失 ②</h3><p><b>手机结构性萎缩。</b>存储涨价 + 竞争加剧 + 换机周期延长，份额跌破 10%，现金流与生态入口同时受损。</p></div>
        <div class="card red"><h3>永久性损失 ③</h3><p><b>品牌/安全事件。</b>汽车或手机出现重大安全/质量危机，信任受损，生态协同反噬；概率低，但不可逆。</p></div>
      </div>
      <div class="grid2" style="margin-top:2mm;">
        <div class="card"><h3>跟踪日历</h3>{cal}</div>
        <div class="card"><h3>来源与免责声明</h3>
          <p class="small"><b>来源：</b>小米集团 2025 年报（2026-03-24）、2026Q1 业绩（2026-05-26）、2026 中报（2026-08-18）、2026Q3 券商前瞻（中金/华泰/花旗/中信建投）、回购公告、中国货币网汇率。</p>
          <p class="small"><b>数据日期：</b>财务截至 2026-06-30；价格 2026-11-05 收盘；Q3 官方业绩 2026-11-24 发布。</p>
          <p class="small"><b>免责声明：</b>本报告为研究记录，不构成任何投资建议、要约或承诺。估值依赖假设，假设变化会显著改变结果。读者应独立判断，并咨询持牌专业人士。</p>
        </div>
      </div>
    """, 8)


def build_html():
    pages = [p1(), p2(), p3(), p4(), p5(), p6(), p7(), p8()]
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{''.join(pages)}</body></html>"""


def build_pdf():
    OUT.mkdir(parents=True, exist_ok=True)
    html_path = OUT / f"1810.HK-估值模型-{D.DATE}.html"
    pdf_path = OUT / f"1810.HK-估值模型-{D.DATE}.pdf"
    html_path.write_text(build_html(), encoding="utf-8")
    cmd = [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
           f"--print-to-pdf={pdf_path}", html_path.as_uri()]
    subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=180)
    html_path.unlink(missing_ok=True)
    print("saved", pdf_path.name)


if __name__ == "__main__":
    build_pdf()
