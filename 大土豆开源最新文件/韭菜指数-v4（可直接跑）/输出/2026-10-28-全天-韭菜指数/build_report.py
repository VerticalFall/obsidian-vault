# -*- coding: utf-8 -*-
"""生成 2026-10-28 韭菜指数 v4.0 全天版 HTML"""
import os, re, html

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
TEMPLATE = os.path.join(ROOT, "references", "template-全天.html")
OUT_HTML = os.path.join(BASE, "10月28号-全天-韭菜指数.html")

src = open(TEMPLATE, encoding="utf-8").read()
prefix = src[:src.find('<div class="wrap">')]
prefix = re.sub(r"<title>.*?</title>", "<title>韭菜指数 · 2026.10.28 全天 · 国家队没上班，成长股自己嗨</title>", prefix, flags=re.S)

CUSTOM_CSS = """
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei","Segoe UI Emoji","Apple Color Emoji",sans-serif}
.fund-col.in{background:var(--bull-bg);border-color:#eccac4}
.fund-col.in .fh,.fund-col.in .fv{color:var(--bull)}
.fund-col.out{background:var(--bear-bg);border-color:#bfe0cd}
.fund-col.out .fh,.fund-col.out .fv{color:var(--bear)}
.verify-t{width:100%;border-collapse:collapse;background:#fff;border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:10px 0;font-size:12.5px}
.verify-t th{background:var(--paper2);color:var(--accent);font-size:11.5px;font-weight:800;padding:7px 8px;border-bottom:1px solid var(--line);text-align:center}
.verify-t td{padding:7px 8px;border-bottom:1px dashed rgba(0,0,0,.07);text-align:center;line-height:1.55}
.verify-t td:first-child{text-align:left;font-weight:700}
.verify-t tr:last-child td{border-bottom:none}
.l5-t{width:100%;border-collapse:collapse;font-size:12.5px;min-width:660px;margin:10px 0 2px}
.l5-t th{padding:7px 6px;text-align:center;font-weight:700;font-size:11.5px;border-bottom:2px solid var(--ink);white-space:nowrap}
.l5-t th:first-child{text-align:left}
.l5-t td{padding:7px 6px;text-align:center;font-weight:700;font-size:13px;border-top:1px solid var(--line);white-space:nowrap}
.l5-t td.name{text-align:left;font-size:12.5px;font-weight:700;white-space:nowrap}
.l5-t td.c-l1{color:#c0392b}.l5-t td.c-l2{color:#b85c00}.l5-t td.c-l3{color:#1f4e79}.l5-t td.c-l4{color:#0a6e44}.l5-t td.c-l5{color:#5a5246}
.l5-bar{height:10px;border-radius:5px;overflow:hidden;display:flex;min-width:180px}
.l5-bar i{display:block;height:100%}
.l5-bar .b1{background:#e74c3c}.l5-bar .b2{background:#ff7a00}.l5-bar .b3{background:#4a90d9}.l5-bar .b4{background:#0a8f5b}.l5-bar .b5{background:#8a8272}
.l5-legend{display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:10px;font-size:11.5px;color:var(--soft);line-height:1.6}
.l5-legend span b{font-weight:800}
.l5-legend .d1{color:#c0392b}.l5-legend .d2{color:#b85c00}.l5-legend .d3{color:#1f4e79}.l5-legend .d4{color:#0a6e44}.l5-legend .d5{color:#5a5246}
"""
prefix = prefix.replace("</style>", CUSTOM_CSS + "</style>")

def thermo(name, score, prev, desc, color, up=True):
    h = round(score * 1.28)
    y = 150 - h
    arrow = "↑" if up else "↓"
    cls = "t-cmp" if up else "t-cmp dn"
    return f'''  <div class="thermo">
    <svg viewBox="0 0 70 200" aria-label="{name}{score}度">
      <line x1="46" y1="26" x2="52" y2="26" stroke="#b5ab96" stroke-width="1.5"/>
      <line x1="46" y1="89" x2="52" y2="89" stroke="#b5ab96" stroke-width="1.5"/>
      <line x1="46" y1="152" x2="52" y2="152" stroke="#b5ab96" stroke-width="1.5"/>
      <text x="56" y="30" font-size="9" fill="#8a8272">100</text>
      <text x="56" y="93" font-size="9" fill="#8a8272">50</text>
      <text x="56" y="156" font-size="9" fill="#8a8272">0</text>
      <rect x="26" y="22" width="14" height="128" rx="7" fill="#f5f0e6" stroke="#9a9180" stroke-width="2"/>
      <rect x="28" y="{y}" width="10" height="{h}" rx="5" fill="{color}"/>
      <circle cx="33" cy="{y}" r="5" fill="{color}"/>
    </svg>
    <div class="t-name">{name}</div>
    <div class="t-val" style="color:{color}">{score}°</div>
    <div class="{cls}">{arrow}{abs(score-prev)} <span class="prev">昨全天{prev}°</span></div>
    <div class="t-desc">{desc}</div>
  </div>'''

thermos = [
    thermo("市场热度", 73, 42, "76.7%上涨·量能100.6%", "#ff7a00"),
    thermo("赚钱效应", 83, 30, "72涨停·5板·普涨", "#ff7a00"),
    thermo("讨论热度", 71, 46, "成交额环比+11.5%", "#ff7a00"),
    thermo("恐贪情绪", 64, 71, "封板率51%·炸板69家", "#c8a415", up=False),
    thermo("风险偏好", 90, 14, "进攻+2.7% vs 防御-0.2%", "#c0392b"),
]

TOPS = [
    ("🤖 人形机器人 → 物理AI涨停潮", "上海文件+宇树大会", "上海文件+宇树生态大会双催化，板块+4.76%；但午后炸板率49%，先手在出货。", 98, "#e74c3c"),
    ("💾 AI硬件·CPO/PCB", "超跌修复", "CPO+3.80%、PCB+3.98%、存储+3.84%，全线修复；没有新订单，只有旧逻辑。", 95, "#e74c3c"),
    ("🔬 半导体·先进封装", "涨幅第一", "半导体+4.88%全场第一；长鑫科技纳入上证综指，被动资金预期点燃设备/封装。", 90, "#e74c3c"),
    ("🔧 汽车零部件涨停潮", "机器人卖铲人", "执行器/丝杠/减速器同源，凯众股份2板；汽零成了机器人行情的“卖铲人”。", 87, "#e74c3c"),
    ("💥 午后机器人批量炸板", "情绪拐点", "上午封板率近80%，收盘只剩51%；69家炸板，机器人链午后集体开板。", 85, "#e74c3c"),
    ("📱 消费电子·苹果折叠屏", "果链催化", "苹果折叠屏出货目标上调，果链+3.31%；发布会前的老剧本，节奏比方向重要。", 80, "#ff7a00"),
    ("💊 AI制药/CRO", "超跌+降息预期", "CRO+4.77%、AI制药+2.64%，超跌+海外降息预期；药明系修复，持续性存疑。", 78, "#ff7a00"),
    ("🛒 低位消费/零售补涨", "小票游击", "茂业商业2板、青岛食品3板，低位小票补涨；防御资金退潮后的游击战。", 74, "#ff7a00"),
    ("🍶 白酒/银行防御端失血", "风格切换", "白酒-0.92%、银行-0.35%，中证红利仅+0.03%；风险偏好回来了，防御端被抽血。", 72, "#ff7a00"),
    ("📉 证券/船舶/酒店领跌", "进攻不彻底", "证券、船舶、酒店跌幅居前；进攻日券商不涨，说明这不是全面牛市，只是超跌反弹。", 68, "#c8a415"),
]

def rank_card(i, item):
    name, tag, desc, score, color = item
    if i == 1:
        cls, numcls = "rank-card top1", "rank-num r1"
    elif i == 2:
        cls, numcls = "rank-card top2", "rank-num r2"
    elif i == 3:
        cls, numcls = "rank-card top3", "rank-num r3"
    else:
        cls, numcls = "rank-card", "rank-num"
    return f'''<div class="{cls}">
  <div class="{numcls}">{i}</div>
  <div class="rank-info">
    <div class="name">{name} <span class="tag">{tag}</span></div>
    <div class="desc">{desc}</div>
  </div>
  <div class="rank-score"><div class="big" style="color:{color}">{score}</div><div class="unit">讨论度</div></div>
</div>'''

ranks = "\n".join(rank_card(i + 1, x) for i, x in enumerate(TOPS))

DEEPS = [
    ("c1", "🤖 人形机器人·物理AI", "🔥 今日主线·涨停潮核心", "+4.76%", "板块涨幅·L1+L2 58%", "#c0392b",
     [("催化", "上海行动方案提出2028年8000台人形机器人进工厂"),
      ("盘面", "机器人+3.67%、通用设备+3.65%，午后批量炸板")],
     (28, 30, 26, 12, 4),
     "断症：上海文件把“物理AI”写进工厂KPI，L1+L2 58%全场最高——故事新、空间大、人人懂。但午后炸板说明：先手在用涨停板出货，接棒的人还在讲2028年的故事。"),
    ("c2", "🔧 汽车零部件", "🔧 机器人映射·涨停居前", "+3.47%", "板块涨幅·L1+L2 53%", "#0a8f5b",
     [("逻辑", "执行器/丝杠/减速器与机器人同源，汽零是“卖铲人”"),
      ("盘面", "凯众股份2板，多家首板，午后跟随机器人回落")],
     (25, 28, 28, 14, 5),
     "断症：汽零是机器人行情的影子板块：L2 28%+L3 28%，半懂不懂的人最多。订单没见到，先按2028年机器人产量炒2026年估值——产业链映射，不是业绩兑现。"),
    ("c3", "📱 消费电子", "📱 苹果链·折叠屏", "+3.31%", "板块涨幅·L1+L2 46%", "#b8860b",
     [("催化", "苹果折叠屏出货目标上调，果链设备跟涨"),
      ("盘面", "消费电子+3.31%，成交温和放大，机构参与24%")],
     (20, 26, 30, 18, 6),
     "断症：苹果折叠屏是“旧故事新数字”，L1+L2 46%，比机器人低一档。L4+L5 24%说明机构愿意给仓位——但消费电子向来“发布会前涨、发布后跌”，节奏比方向重要。"),
    ("c4", "💾 AI硬件·CPO/PCB", "💾 超跌修复·无新催化", "+3.98%", "PCB涨幅·L1+L2 42%", "#d9a500",
     [("盘面", "CPO+3.80%、PCB+3.98%、存储+3.84%，全线修复"),
      ("逻辑", "英伟达产业链情绪修复，但没有新订单落地")],
     (18, 24, 32, 20, 6),
     "断症：AI硬件是“昨天被砸、今天被抢”的典型：L3路人32%最高，围观的多、真信的少。没有新订单，只有超跌——反弹可以，反转要等业绩。"),
    ("c5", "🔬 半导体", "🔬 涨幅第一·长鑫入指", "+4.88%", "板块涨幅·L1+L2 35%", "#1f4e79",
     [("盘面", "半导体+4.88%领涨，先进封装/存储/设备全线走强"),
      ("催化", "长鑫科技纳入上证综指/科创综指，被动资金预期")],
     (15, 20, 33, 24, 8),
     "断症：半导体涨得最猛，L5机构却只占8%——涨幅第一、筹码最散。长鑫入指是“被动资金要买”的明牌：确定，但所有人都知道。"),
    ("c6", "🍶 白酒/银行", "🍶 防御端·失血", "-0.92%", "白酒跌幅·L1+L2 22%", "#7a3fa0",
     [("盘面", "白酒-0.92%、银行-0.35%，中证红利仅+0.03%"),
      ("资金", "防御端失血，钱流向创业板/中证1000")],
     (8, 14, 28, 36, 14),
     "断症：昨天还是避风港，今天成了提款机：L4+L5 50%全场最高，照样跌。机构浓度高只说明“人少且专业”，不保证上涨——防御端下跌，恰是风险偏好修复的证据。"),
]

def deep_card(d):
    cls, name, tag, big, unit, color, rows, lv, ding = d
    total = sum(lv)
    strip = "\n".join(
        f'      <div class="dc-l1 l{k}"><span class="pct">{v}%</span>{lab}</div>'
        for k, v, lab in zip(range(1, 6), lv, ["L1 🥬", "L2 🐣", "L3 🧭", "L4 📈", "L5 🏛"]))
    data = "\n".join(f'      <div class="row"><b>{a}：</b>{b}</div>' for a, b in rows)
    return f'''  <div class="deep-card {cls}">
    <div class="dc-top"><span class="dc-name">{name}</span><span class="dc-tag">{tag}</span></div>
    <div class="dc-bignum" style="color:{color}">{big}<span class="unit">{unit}</span></div>
    <div class="dc-data">
{data}
    </div>
    <div class="dc-l1strip">
{strip}
    </div>
    <div class="dc-ding">{ding}</div>
  </div>'''

deeps = "\n".join(deep_card(d) for d in DEEPS)

CENSUS = [
    ("🤖 人形机器人", (28, 30, 26, 12, 4), "58%"),
    ("🔧 汽车零部件", (25, 28, 28, 14, 5), "53%"),
    ("📱 消费电子", (20, 26, 30, 18, 6), "46%"),
    ("💾 AI硬件", (18, 24, 32, 20, 6), "42%"),
    ("🔬 半导体", (15, 20, 33, 24, 8), "35%"),
    ("🍶 白酒/银行", (8, 14, 28, 36, 14), "22%"),
]

def census_row(name, lv, total):
    cells = "".join(f'<td class="c-l{k}">{v}%</td>' for k, v in zip(range(1, 6), lv))
    bars = "".join(f'<i class="b{k}" style="width:{v}%"></i>' for k, v in zip(range(1, 6), lv))
    color = "#c0392b" if total in ("58%", "53%") else ("#0a6e44" if total == "22%" else "#1f4e79")
    return f'''      <tr>
        <td class="name">{name}</td>
        {cells}
        <td style="color:{color};font-size:14px">{total}</td>
        <td><div class="l5-bar">{bars}</div></td>
      </tr>'''

census_rows = "\n".join(census_row(*c) for c in CENSUS)

ETFS = [
    ("159915 创业板ETF易方达", "116.1亿", "1.21x", "1.20x", "🔥 成长领涨·创业板放量", True),
    ("588000 科创50ETF华夏", "93.0亿", "1.04x", "0.95x", "科创50温和跟涨", False),
    ("512100 中证1000ETF南方", "48.2亿", "1.26x", "1.21x", "🔥 小盘放量·游资回流", True),
    ("510300 沪深300ETF华泰", "45.6亿", "0.78x", "0.62x", "❄️ 国家队缺席·权重缩量", False),
    ("510500 中证500ETF南方", "40.4亿", "0.96x", "0.98x", "中盘持平", True),
    ("510050 上证50ETF华夏", "24.8亿", "1.31x", "0.82x", "⚠️ 低位反抽·仍低于均量", False),
    ("518880 黄金ETF华安", "22.1亿", "0.88x", "0.70x", "黄金缩量·避险降温", True),
    ("588080 科创板50ETF易方达", "20.5亿", "1.04x", "1.03x", "科创50持平", False),
    ("512480 半导体ETF国联安", "12.3亿", "1.25x", "1.06x", "半导体放量跟涨", True),
    ("512880 证券ETF国泰", "11.8亿", "0.71x", "0.79x", "券商缩量·进攻不彻底", False),
    ("159919 沪深300ETF嘉实", "11.2亿", "1.19x", "0.57x", "⚠️ 低基数反弹", True),
    ("510310 沪深300ETF易方达", "8.2亿", "0.67x", "0.23x", "❄️ 连续隐身", False),
    ("510330 沪深300ETF华夏", "7.9亿", "0.71x", "0.41x", "❄️ 权重无人问", True),
    ("512890 红利低波ETF华泰", "5.8亿", "0.46x", "0.66x", "红利缩量·防御退潮", False),
    ("512690 酒ETF鹏华", "4.6亿", "1.07x", "1.12x", "酒ETF放量下跌·分歧", True),
    ("512200 房地产ETF南方", "0.9亿", "0.92x", "0.50x", "地产躺平", False),
]

def etf_row(e, i):
    name, amt, d1, d14, note, shade = e
    bg = ' style="background:#fdf3f1"' if shade else ""
    return f'''      <tr{bg}><td style="padding:5px 9px;border:1px solid var(--line)">{name}</td><td style="padding:5px 9px;border:1px solid var(--line);text-align:right;font-weight:700">{amt}</td><td style="padding:5px 9px;border:1px solid var(--line);text-align:right">{d1}</td><td style="padding:5px 9px;border:1px solid var(--line);text-align:right;color:var(--soft)">{d14}</td><td style="padding:5px 9px;border:1px solid var(--line)">{note}</td></tr>'''

etf_rows = "\n".join(etf_row(e, i) for i, e in enumerate(ETFS))

CHART = sorted(ETFS, key=lambda x: float(x[3].replace("x", "")), reverse=True)

def chart_rows():
    out = []
    for i, (name, amt, d1, d14, note, _) in enumerate(CHART):
        ratio = float(d14.replace("x", ""))
        y = 44 + i * 26
        w = round(ratio * 330)
        if ratio >= 1.1:
            c = "#e74c3c"
        elif ratio >= 0.9:
            c = "#ff7a00"
        elif ratio >= 0.7:
            c = "#8a8272"
        else:
            c = "#0a8f5b"
        label = name.split(" ", 1)[0] + " " + name.split(" ", 1)[1][:8]
        out.append(f'''  <text x="218" y="{y+12}" font-size="11.5" text-anchor="end" fill="#0d1117">{label}</text>
  <rect x="230" y="{y+1}" width="{w}" height="14" rx="3" fill="{c}"/>
  <text x="{230+w+7}" y="{y+12}" font-size="11.5" font-weight="800" fill="{c}">{d14}</text>''')
    return "\n".join(out)

chart = chart_rows()

body = f'''<div class="wrap">

<header class="hero">
  <div class="kicker"><span class="type-tag">韭菜指数</span> 散户吃瓜指数 · Retail Watcher · 2026.10.28 全天收盘（周三）</div>
  <h1>国家队没上班，成长股自己嗨：<em>创业板+3.40%</em>——人形机器人+物理AI涨停潮，<br>但午后炸板率49%、封板率只剩51%。这是超跌反弹，不是全面进攻</h1>
  <div class="meta">
    版本：韭菜指数 TOP10 · 全天收盘 15:00 · 环比参考：10/27 全天（上一期）；温度计环比基准：10/27 全天读数<br>
    数据来源：东方财富日K/涨停池收盘口径（16只ETF逐一对账） + 财联社/中国证券报/上海证券报 + 公开讨论（v4.0 精简版）
  </div>
  <div class="badge-row">
    <span class="badge w">📈 沪指 +0.91% 报 3681.47 · 深成 +2.02% · 创业板 +3.40% · 科创50 +2.45%</span>
    <span class="badge w">📊 量能 1.63 万亿 · 较昨放量 1675 亿 · 为20日均量的100.6%</span>
    <span class="badge w">🌱 4156 涨 / 1239 跌（77%）· 涨停 72 · 炸板 69 · 封板率 51.1% · 最高5板（襄阳轴承）</span>
    <span class="badge hl-badge">🤖 人形机器人 +4.76% · 半导体 +4.88% · CPO +3.80% · PCB +3.98%</span>
    <span class="badge fun-badge">🏛 国家队缺席：510300 仅0.62x、510050 0.82x（14日均量）</span>
    <span class="badge g">🍶 防御端失血：白酒 -0.92% · 银行 -0.35% · 中证红利 +0.03%</span>
  </div>
  <div class="lead">
    <b>一句话看懂：</b>昨天还在ICU，今天直接进KTV——<b>但买单的人不是国家队</b>。上午机器人+物理AI涨停潮、半导体+4.88%领涨，下午机器人链批量炸板，封板率从近80%掉到51%。<b>这是超跌反弹，不是全面进攻</b>：300/50宽基全线缩量，钱是从防御端撤出来、冲进成长赛道的存量资金。
  </div>
</header>

<!-- ① 温度计 -->
<div class="eyebrow"><span class="num">🌡</span><span class="label">市场体温计 · 2026.10.28 全天收盘 · 环比 10/27 全天</span></div>

<div class="thermo-grid">
{chr(10).join(thermos)}
</div>
<div class="thermo-note">四升一降：指数与广度全面修复，唯独恐贪从71°降到64°——午后69家炸板，把追高的人埋在了涨停板上。<br>分数按 scoring-v4 锚点复算；涨停均值用近10日替代（9/23-9/30池数据缺失，已标注）。</div>

<!-- 验证点对答案 -->
<div class="eyebrow"><span class="num">✓</span><span class="label">昨日三问 · 对答案（10/27 收盘复盘）</span></div>
<table class="verify-t">
  <thead><tr><th style="text-align:left">昨日预判</th><th>今日实际</th><th style="width:60px">判定</th></tr></thead>
  <tbody>
    <tr><td>沪指能否收复3650</td><td>最低3652.37，收盘3681.47</td><td style="color:#c0392b;font-weight:800">✓</td></tr>
    <tr><td>银行/红利防御能否延续</td><td>银行-0.35%、红利+0.03%，熄火</td><td style="color:#0a8f5b;font-weight:800">✗</td></tr>
    <tr><td>涨停家数能否回到50+</td><td>72家，较昨41家近翻倍</td><td style="color:#c0392b;font-weight:800">✓</td></tr>
  </tbody>
</table>

<!-- ② TOP10 -->
<div class="eyebrow"><span class="num">🔥</span><span class="label">散户围观榜 TOP10 · 今天大家在聊什么</span></div>
<h2 class="sec-title">十张卡看懂：从机器人涨停潮，到午后炸板潮</h2>
<div class="sec-desc">按讨论热度排序：涨停潮、炸板潮、ETF缺席三条线，构成今天的全部叙事。</div>

{ranks}

<!-- ③ 深吃瓜 -->
<div class="eyebrow"><span class="num">2</span><span class="label">前六大板块深吃瓜（含 L1~L5 散户分级）</span></div>
<h2 class="sec-title">每张卡片：核心数据 + 散户五级 + 一句话断症</h2>

<div class="deep-grid">
{deeps}
</div>

<!-- 韭菜浓度普查 -->
<div class="eyebrow"><span class="num">🔍</span><span class="label">韭菜浓度普查 · 谁最菜？</span></div>
<h2 class="sec-title">故事浓度最高、避险盘浓度最低——反弹日的人群分布图</h2>

<div class="det-box">
  <div class="det-head"><span class="dt">大V解剖</span><span class="dn">韭菜浓度普查：<b>机器人58%最高、白酒银行22%最低</b></span></div>
  <div class="det-kicker">核心发现：<b>人形机器人 L1+L2 58% 全场最高，白酒/银行 22% 最低、L4+L5 50%</b>。故事越新韭菜越浓，但“机构多”不等于“会涨”——今天防御端照样跌。</div>
  <div style="overflow-x:auto">
  <table class="l5-t">
    <thead>
      <tr><th style="text-align:left">板块</th><th>L1 纯韭菜</th><th>L2 嫩韭菜</th><th>L3 路人</th><th>L4 老手</th><th>L5 机构</th><th>L1+L2 韭菜占比</th><th>韭菜构成条</th></tr>
    </thead>
    <tbody>
{census_rows}
    </tbody>
  </table>
  </div>
  <div class="l5-legend">
    <span class="d1"><b>L1 纯韭菜</b> 刚开户/追涨杀跌</span>
    <span class="d2"><b>L2 嫩韭菜</b> 懂概念/不会卖</span>
    <span class="d3"><b>L3 路人</b> 看热闹/轻仓</span>
    <span class="d4"><b>L4 老手</b> 有体系/会止损</span>
    <span class="d5"><b>L5 机构</b> 专业/大资金</span>
  </div>
  <div class="det-verdict">侦探结论：机器人58%的韭菜浓度，配的是“2028年进工厂”的故事；白酒银行22%的机构浓度，配的是今天的下跌。<b>浓度只描述人群结构，不预测涨跌</b>——真正的信号是：韭菜在往新故事跑，机构在从旧防御撤。</div>
</div>

<!-- ④ 国家队 -->
<div class="eyebrow"><span class="num">4</span><span class="label">国家队资金动向 · ETF大搜查 · 16只全网格对账：今天到底来没来？</span></div>
<h2 class="sec-title">答案：没来——300/50宽基全线缩量，成长宽基自己放量</h2>

<div class="etf-verdict">
  <div class="stamp"><div class="big">国家队没上班</div><div class="sub">成长股自己嗨</div></div>
  <div class="why">
    <b>① 权重宽基缩量：</b>510300 仅0.62x、510050 0.82x、510310 0.23x（14日均量），没有托底痕迹。<br>
    <b>② 成长宽基放量：</b>512100 1.21x、159915 1.20x、512480 1.06x——钱去了高弹性。<br>
    <b>③ 无尾盘脉冲：</b>510300尾盘30分钟仅占全天16.0%、510050占21.0%，没有10/16那种79%的尾盘扫货。<br>
    <b>④ 量级不够：</b>16只合计473亿，最大1.21x，离5x救市门槛差得远。
  </div>
</div>

<div class="det-box">
  <div class="det-head"><span class="dt">资金侦探</span><span class="dn">16只ETF放量倍数对账：<b>宽基10只+行业6只</b></span></div>
  <div class="det-kicker">今日成交 ÷ 昨日成交、今日成交 ÷ 近14个交易日（10/8~10/27）日均成交（东财日K收盘口径，单位亿元）。</div>
  <table style="width:100%;border-collapse:collapse;font-size:13px;margin:6px 0 4px;background:#fff">
    <thead><tr style="background:var(--ink);color:var(--paper)">
      <th style="padding:6px 9px;text-align:left;border:1px solid var(--ink)">ETF（按今日成交排序）</th>
      <th style="padding:6px 9px;text-align:right;border:1px solid var(--ink)">今日成交</th>
      <th style="padding:6px 9px;text-align:right;border:1px solid var(--ink)">vs昨日</th>
      <th style="padding:6px 9px;text-align:right;border:1px solid var(--ink)">vs 14日日均</th>
      <th style="padding:6px 9px;text-align:left;border:1px solid var(--ink)">判读</th>
    </tr></thead>
    <tbody>
{etf_rows}
    </tbody>
  </table>

  <h2 class="sec-title" style="font-size:17px;margin-top:18px">ETF放量全景 · 1.0x均量线，谁在裸泳</h2>
  <svg viewBox="0 0 1080 480" style="width:100%;height:auto;background:#fff;border:1px solid var(--line);border-radius:8px">
    <text x="230" y="18" font-size="12" font-weight="800" fill="#1f4e79">14日日均成交倍数（1.0x=均量线，1.5x=明显放量）</text>
    <line x1="560" y1="28" x2="560" y2="452" stroke="#6b6457" stroke-width="1.2" stroke-dasharray="5,4"/>
    <text x="560" y="474" font-size="10.5" fill="#6b6457" text-anchor="middle">1.0x</text>
    <line x1="725" y1="28" x2="725" y2="452" stroke="#c0392b" stroke-width="1.2" stroke-dasharray="5,4"/>
    <text x="725" y="474" font-size="10.5" fill="#c0392b" text-anchor="middle">1.5x</text>
{chart}
  </svg>

  <h2 class="sec-title" style="font-size:17px;margin-top:20px">四维验证：今天为什么不是“国家队行情”</h2>
  <table class="verify-t">
    <thead><tr><th style="text-align:left">维度</th><th>救市样本特征</th><th>10/28 实际</th><th style="width:88px">判定</th></tr></thead>
    <tbody>
      <tr><td>① 载体</td><td>300/50等权重宽基爆量</td><td>510300 0.62x、510050 0.82x</td><td style="color:#0a8f5b;font-weight:800">❌ 反向</td></tr>
      <tr><td>② 时点</td><td>尾盘定点脉冲</td><td>510300尾盘30分钟仅16.0%、510050 21.0%</td><td style="color:#0a8f5b;font-weight:800">❌ 无痕迹</td></tr>
      <tr><td>③ 结构</td><td>只买权重，中小盘躺平</td><td>创业板/中证1000领涨，权重滞涨</td><td style="color:#0a8f5b;font-weight:800">❌ 游资主导</td></tr>
      <tr><td>④ 量级</td><td>单日5x起步</td><td>最大1.21x，16只合计473亿</td><td style="color:#0a8f5b;font-weight:800">❌ 未达门槛</td></tr>
    </tbody>
  </table>

  <div class="det-verdict">侦探结论：四条全否——载体反、时点无、结构偏、量级不够。今天放量的是创业板/中证1000/半导体，不是300/50，这是存量资金从防御端撤出、冲向成长超跌反弹，不是国家队托底。明天验证：①300/50是否重新放量 ②创业板ETF能否连续2天1.2x ③炸板潮是否收敛。</div>
</div>

<!-- 尾盘节奏 -->
<h2 class="sec-title" style="font-size:17px;margin-top:20px">尾盘节奏还原 · 从涨停潮到炸板潮</h2>
<table class="timeline-table">
  <thead><tr><th>时间窗</th><th>盘面动作</th><th>ETF端动作</th><th>性质判读</th></tr></thead>
  <tbody>
    <tr><td>9:30-10:30</td><td>高开高走，机器人/半导体领涨，沪指站上3660</td><td>创业板ETF放量，300/50平稳</td><td style="font-size:11.5px">自发修复，非护盘</td></tr>
    <tr><td>10:30-11:30</td><td>涨停家数破60，封板率近80%，人形机器人涨停潮</td><td>量能温和放大，无单一ETF爆量</td><td style="font-size:11.5px">情绪高点</td></tr>
    <tr><td>13:00-14:00</td><td>机器人链批量炸板，炸板数升至69，封板率跌破60%</td><td>宽基ETF无脉冲</td><td style="font-size:11.5px">先手资金出货</td></tr>
    <tr><td>14:00-14:40</td><td>指数横盘，半导体/CPO承接，涨停维持70+</td><td>159915/512100持续放量</td><td style="font-size:11.5px">高低切换</td></tr>
    <tr><td>14:40-15:00</td><td>尾盘小幅回落，创业板收+3.40%，封板率51.1%</td><td>510300尾盘30分钟仅16.0%、510050 21.0%</td><td style="font-size:11.5px">反弹定调，非反转</td></tr>
  </tbody>
</table>

<!-- ⑤ 资金 -->
<div class="eyebrow"><span class="num">5</span><span class="label">主力资金 · 板块口径（不看个股）</span></div>
<div class="fund-box">
  <div class="fund-cols">
    <div class="fund-col in">
      <div class="fh">🔴 资金流入方向（成长端回血）</div>
      <div class="fund-row"><span class="fn">🤖 人形机器人</span><span class="fv">+4.76% · 涨停潮核心</span></div>
      <div class="fund-row"><span class="fn">🔬 半导体</span><span class="fv">+4.88% · 全场第一</span></div>
      <div class="fund-row"><span class="fn">💾 CPO/PCB</span><span class="fv">+3.80%/+3.98% · 超跌修复</span></div>
      <div class="fund-row"><span class="fn">🔧 汽车零部件</span><span class="fv">+3.47% · 机器人映射</span></div>
      <div class="fund-row"><span class="fn">📈 创业板ETF</span><span class="fv">116.1亿 · 1.20x</span></div>
    </div>
    <div class="fund-col out">
      <div class="fh">🟢 资金流出方向（防御端失血）</div>
      <div class="fund-row"><span class="fn">🍶 白酒</span><span class="fv">-0.92% · 防御退潮</span></div>
      <div class="fund-row"><span class="fn">🏦 银行</span><span class="fv">-0.35% · 红利仅+0.03%</span></div>
      <div class="fund-row"><span class="fn">🥇 黄金ETF</span><span class="fv">0.70x · 避险降温</span></div>
      <div class="fund-row"><span class="fn">🛡 红利低波ETF</span><span class="fv">0.66x · 防御缩量</span></div>
      <div class="fund-row"><span class="fn">📉 证券ETF</span><span class="fv">0.79x · 进攻不彻底</span></div>
    </div>
  </div>
  <div class="fund-note"><b>一句话总结：</b>钱不是新进来的，是从防御端搬到了成长端——16只ETF合计473亿、最大1.21x，没有增量资金的“救市脸”。主力净流入接口今日不可用，本节以板块涨幅+ETF量能代理。</div>
</div>

<!-- ⑥ 核心矛盾 -->
<div class="eyebrow"><span class="num">6</span><span class="label">全天核心矛盾 · 三条看懂</span></div>
<div class="pre-wrap">
  <div class="conf-item">🔴 <b>多头说：</b>创业板+3.40%、72家涨停、4156家上涨，超跌修复全面铺开；半导体+4.88%、机器人+4.76%，成长主线重新聚拢；量能1.63万亿回到20日均量上方。</div>
  <div class="conf-item">🟢 <b>空头说：</b>封板率从近80%掉到51%、69家炸板，午后追高全线被埋；300/50宽基缩量，国家队没来；白酒/银行失血说明只是存量搬家，没有增量。</div>
  <div class="conf-item">🔮 <b>关键变量：</b>①创业板ETF能否连续2天1.2x ②300/50是否重新放量 ③炸板潮明天是否收敛 ④苹果折叠屏/机器人订单能否从故事变业绩 ⑤三季报尾声的暴雷风险。</div>
</div>

<!-- ⑦ 明天预判 -->
<div class="eyebrow"><span class="num">🧭</span><span class="label">明天预判 · 精简3情景</span></div>
<div class="pre-wrap">
  <div class="pre-item"><b>情景A｜延续反弹（概率35%）</b>→ 机器人/半导体承接，创业板站稳2630，涨停维持70+；但需创业板ETF连续放量，否则是最后一冲。</div>
  <div class="pre-item"><b>情景B｜冲高回落·炸板延续（概率45%）</b>→ 早盘惯性高开，午后炸板率再超50%，沪指回踩3650；超跌反弹三天内结束，<b>最可能</b>。</div>
  <div class="pre-item"><b>情景C｜防御反扑·风格再切（概率20%）</b>→ 成长熄火，银行/红利重新吸金，沪指守住3680但创业板回吐一半；说明增量资金仍不愿进场。</div>
</div>

<!-- 数据说明 -->
<div class="disc">
  <b>📌 口径：</b>指数为10/28收盘：沪指3681.47/+0.91%（高3684.49/低3652.37）、深成+2.02%、创业板+3.40%、科创50+2.45%；成交1.63万亿（16,284.8亿），较10/27放量1,675亿；4156涨/1239跌（财联社），东财A股子集3872涨/1176跌/170平（76.7%）；涨停72/炸板69/跌停5/封板率51.1%/最高5板（襄阳轴承）/连板8家（东财涨停池15:05快照，与财联社口径可能±1）。<br>
  <b>📌 温度计：</b>按 scoring-v4 锚点复算；市场热度量比100.6%、上涨占比76.7%；赚钱效应涨停家数用近10日均值53.0（9/23-9/30池数据缺失，降级替代）；讨论热度环比+11.5%；恐贪封板率51.1%、5板+8；风险偏好进攻组（券商/半导体/机器人/军工/有色）均值+2.70% − 防御组（银行/白酒/电力/公用）-0.17% = +2.87pct。<br>
  <b>📌 ETF口径：</b>今日成交÷近14日（10/8~10/27）日均成交，东财日K收盘口径；16只合计473.4亿；尾盘占比用东财1分钟线（14:30后成交额÷全天）；「救市级门槛」参照2024/2汇金样本单日5x起步。<br>
  <b>📌 L1-L5：</b>本期未完成每板块≥15条股吧/雪球样本采集，分布为盘面结构+关注度估算，按v4.0规则降级，不作为情绪结论；韭菜浓度=L1+L2，机构浓度=L4+L5。<br>
  <b>📌 资金流：</b>东财板块主力净流入接口今日不可用，第五节用板块涨幅+ETF量能代理，标注降级。<br>
  <b>📌 免责：</b>本报告为娱乐化的市场情绪观察，不构成任何投资建议；市场有风险，吃瓜需理性。
</div>

<div class="footer">
  🍉 <b>韭菜指数</b> · 2026.10.28 全天（国家队没上班，成长股自己嗨：创业板+3.40%·机器人涨停潮→午后炸板潮——超跌反弹，非全面进攻） · 编制人：土豆 + Buddy<br>
  数据来源：东方财富 + 财联社/中国证券报/上海证券报 + 公开讨论 · ⚠️ 仅为散户情绪观察，不构成投资建议
</div>

</div>
</body>
</html>'''

html_doc = prefix + body
open(OUT_HTML, "w", encoding="utf-8").write(html_doc)

# 可见中文字符统计
vis = re.sub(r"<style.*?</style>", "", html_doc, flags=re.S)
vis = re.sub(r"<script.*?</script>", "", vis, flags=re.S)
vis = re.sub(r"<!--.*?-->", "", vis, flags=re.S)
vis = re.sub(r"<[^>]+>", "", vis)
vis = html.unescape(vis)
cn = len(re.findall(r"[一-鿿]", vis))
open(os.path.join(BASE, "_字数.txt"), "w", encoding="utf-8").write(f"可见中文字符：{cn}\n预算：4500\n")
print("HTML:", OUT_HTML)
print("可见中文字符:", cn)
