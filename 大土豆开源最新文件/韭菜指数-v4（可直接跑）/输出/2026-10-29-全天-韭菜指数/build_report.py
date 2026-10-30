# -*- coding: utf-8 -*-
"""生成 2026-10-29 韭菜指数 v4.0 全天版 HTML"""
import os, re, html

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
TEMPLATE = os.path.join(ROOT, "references", "template-全天.html")
OUT_HTML = os.path.join(BASE, "10月29号-全天-韭菜指数.html")

src = open(TEMPLATE, encoding="utf-8").read()
prefix = src[:src.find('<div class="wrap">')]
prefix = re.sub(r"<title>.*?</title>", "<title>韭菜指数 · 2026.10.29 全天 · 昨天KTV，今天ICU</title>", prefix, flags=re.S)

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
    thermo("市场热度", 42, 73, "量能97.7%·仅14.5%上涨", "#4a90d9", up=False),
    thermo("赚钱效应", 30, 83, "39涨停·4板·普跌", "#4a90d9", up=False),
    thermo("讨论热度", 52, 71, "成交额环比-4.4%", "#ff7a00", up=False),
    thermo("恐贪情绪", 66, 64, "封板率60.9%·炸板25家", "#c8a415"),
    thermo("风险偏好", 14, 90, "进攻-2.3% vs 防御-0.4%", "#0a8f5b", up=False),
]

TOPS = [
    ("💥 创业板-4.45%·14个月新低", "开盘即最高", "创业板-4.45%创14个月新低，科创50-4.27%；开盘即最高，收盘接近最低。", 99, "#e74c3c"),
    ("💾 CPO/光模块·预期差", "天孚-19.77%", "CPO-6.78%、主力净流出205.6亿；天孚-19.77%、新易盛-11%、中际-8.53%。", 97, "#e74c3c"),
    ("🏦 银行·市值破10万亿", "避险主战场", "银行+1.98%、保险+1.61%，工行+2.57%、建行+2.29%，四大行总市值破10万亿。", 95, "#c0392b"),
    ("🚀 商业航天·逆势涨停", "上海卫星方案", "上海卫星互联网行动方案催化，中国卫星、航天晨光涨停；中国卫星盘中炸板8次。", 92, "#ff7a00"),
    ("🔬 半导体·存储补跌", "佰维-15.79%", "半导体-5.55%、存储大跌，佰维-15.79%；主力净流出136.4亿。", 89, "#0a8f5b"),
    ("📉 情绪冰点·涨停缩半", "39 vs 72", "涨停39家（昨72）、炸板25家、跌停41家；124只跌超9.8%，封板率60.9%。", 86, "#4a90d9"),
    ("🌍 海外科技·隔夜共振", "Alphabet-10%", "Alphabet盘后-10%、三星Q3 miss；美10年期国债5.028%，全球科技杀估值。", 83, "#8a8272"),
    ("🍔 食品消费·低位涨停", "青岛食品4板", "巴比食品、惠发食品、一鸣食品涨停，青岛食品4板；低位消费成避风港。", 80, "#c0392b"),
    ("🤖 机器人·退潮", "襄阳炸板20次", "机器人-5.51%、汽零-3.64%；襄阳轴承炸板20次仍收+6.47%，光洋4板。", 77, "#0a8f5b"),
    ("🛢 煤炭/红利·内部分化", "开滦涨停", "煤炭+0.57%、开滦股份涨停；有色-2.60%、黄金ETF仅0.79x，资源内部分化。", 73, "#ff7a00"),
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
    ("c1", "💾 CPO/光模块", "💾 预期差·机构夺门", "-6.78%", "CPO板块·L1+L2 39%", "#0a8f5b",
     [("盘面", "CPO-6.78%、通信设备-5.53%，主力净流出205.6亿"),
      ("个股", "天孚-19.77%、新易盛-11.06%、中际旭创-8.53%")],
     (15, 24, 32, 22, 7),
     "断症：天孚Q3净利8.79亿、同比+55.3%仍低于预期，把“光模块永动机”砸出裂缝——L1+L2 39%不高，但L4+L5 29%的机构也在跑。这是杀估值，不是杀情绪。"),
    ("c2", "🏦 银行/红利", "🏦 市值破10万亿·避险", "+1.98%", "银行板块·L1+L2 16%", "#c0392b",
     [("盘面", "银行+1.98%、保险+1.61%，主力净流入1.11亿"),
      ("个股", "工行+2.57%、建行+2.29%、农行+1.75%、中行+1.99%")],
     (6, 10, 24, 38, 22),
     "断症：四大行总市值破10万亿、工行建行股价新高，L1+L2只有16%、L4+L5 60%——这是机构与红利的阵地战，不是散户的狂欢。避险资金用脚投票：不要故事，要股息。"),
    ("c3", "🚀 商业航天/卫星", "🚀 新故事·逆势涨停", "+10.00%", "中国卫星·L1+L2 60%", "#ff7a00",
     [("催化", "上海发布卫星互联网行动方案，商业航天约10股涨停"),
      ("盘面", "中国卫星、航天晨光涨停；板块仍-1.81%，中国卫星炸板8次")],
     (30, 30, 24, 12, 4),
     "断症：中国卫星10:24封板、盘中炸8次，L1+L2 60%全场最高——新故事、大空间、人人懂。但板块-1.81%，说明只有龙头在飞，跟风股没人接。"),
    ("c4", "🍔 食品/大消费", "🍔 低位补涨·避风港", "4板", "青岛食品·L1+L2 56%", "#c0392b",
     [("盘面", "食品饮料-0.47%，白酒-1.45%；茅台逆势+1.75%"),
      ("个股", "巴比食品、惠发食品、一鸣食品涨停，青岛食品4板")],
     (28, 28, 26, 14, 4),
     "断症：高位AI崩了，低位食品被翻出来：L1+L2 56%，故事朴素到不用研报。青岛食品4板、三家食品首板——这是避险，也是高切低。"),
    ("c5", "🔬 半导体/存储", "🔬 补跌·筹码最散", "-5.55%", "半导体·L1+L2 44%", "#0a8f5b",
     [("盘面", "半导体-5.55%、消费电子-5.05%，主力净流出136.4亿"),
      ("个股", "佰维存储-15.79%，存储/先进封装全线补跌")],
     (18, 26, 32, 18, 6),
     "断症：佰维-15.79%把存储故事打回原形；L1+L2 44%，L3 32%——半懂不懂的人最多。AI叙事还在，但筹码先撤了。"),
    ("c6", "🤖 机器人/汽零", "🤖 退潮·封不住", "-5.51%", "机器人·L1+L2 50%", "#0a8f5b",
     [("盘面", "机器人-5.51%、汽车零部件-3.64%，主力净流出7.05亿"),
      ("个股", "襄阳轴承炸板20次收+6.47%，光洋股份4板但炸17次")],
     (22, 28, 30, 15, 5),
     "断症：昨天涨停潮，今天退潮：L1+L2 50%，L3 30%，全是短线客。光洋4板炸17次、襄阳炸20次——封不住的不是股价，是信心。"),
]

def deep_card(d):
    cls, name, tag, big, unit, color, rows, lv, ding = d
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
    ("🚀 商业航天", (30, 30, 24, 12, 4), "60%"),
    ("🍔 食品/消费", (28, 28, 26, 14, 4), "56%"),
    ("🤖 机器人/汽零", (22, 28, 30, 15, 5), "50%"),
    ("🔬 半导体", (18, 26, 32, 18, 6), "44%"),
    ("💾 CPO/光模块", (15, 24, 32, 22, 7), "39%"),
    ("🏦 银行/红利", (6, 10, 24, 38, 22), "16%"),
]

def census_row(name, lv, total):
    cells = "".join(f'<td class="c-l{k}">{v}%</td>' for k, v in zip(range(1, 6), lv))
    bars = "".join(f'<i class="b{k}" style="width:{v}%"></i>' for k, v in zip(range(1, 6), lv))
    color = "#c0392b" if total in ("60%", "56%", "50%") else ("#0a6e44" if total == "16%" else "#1f4e79")
    return f'''      <tr>
        <td class="name">{name}</td>
        {cells}
        <td style="color:{color};font-size:14px">{total}</td>
        <td><div class="l5-bar">{bars}</div></td>
      </tr>'''

census_rows = "\n".join(census_row(*c) for c in CENSUS)

ETFS = [
    ("159915 创业板ETF易方达", "127.5亿", "116.1亿", "101.2亿", "1.26x", "放量杀跌·接飞刀", True),
    ("588000 科创50ETF华夏", "115.2亿", "93.0亿", "98.9亿", "1.16x", "科创50逆势承接", True),
    ("510300 沪深300ETF华泰", "89.1亿", "45.6亿", "74.8亿", "1.19x", "300放量·未爆量", True),
    ("510500 中证500ETF南方", "47.2亿", "40.4亿", "42.3亿", "1.11x", "中盘温和", False),
    ("159919 沪深300ETF嘉实", "42.6亿", "11.2亿", "20.2亿", "2.11x", "低基数反弹", True),
    ("512100 中证1000ETF南方", "40.2亿", "48.2亿", "41.6亿", "0.97x", "小盘缩量", False),
    ("518880 黄金ETF华安", "24.6亿", "22.1亿", "31.0亿", "0.79x", "黄金降温", False),
    ("510050 上证50ETF华夏", "23.6亿", "24.8亿", "31.2亿", "0.76x", "50缩量·未见托底", False),
    ("588080 科创板50ETF易方达", "20.6亿", "20.5亿", "19.9亿", "1.03x", "科创50持平", False),
    ("510310 沪深300ETF易方达", "18.6亿", "8.2亿", "35.6亿", "0.52x", "300内部隐身", False),
    ("512880 证券ETF国泰", "14.2亿", "11.8亿", "14.9亿", "0.95x", "券商缩量", False),
    ("512480 半导体ETF国联安", "10.5亿", "12.3亿", "11.6亿", "0.90x", "半导体缩量跌", False),
    ("512890 红利低波ETF华泰", "8.6亿", "5.8亿", "8.7亿", "0.98x", "红利持平", False),
    ("512690 酒ETF鹏华", "4.0亿", "4.6亿", "4.2亿", "0.95x", "酒ETF分歧", False),
    ("510330 沪深300ETF华夏", "3.7亿", "7.9亿", "19.3亿", "0.19x", "几乎停摆", False),
    ("512200 房地产ETF南方", "1.0亿", "0.9亿", "1.6亿", "0.65x", "地产躺平", False),
]

def etf_row(e):
    name, amt, y, avg, ratio, note, shade = e
    bg = ' style="background:#fdf3f1"' if shade else ""
    return f'''      <tr{bg}><td style="padding:5px 9px;border:1px solid var(--line)">{name}</td><td style="padding:5px 9px;border:1px solid var(--line);text-align:right;font-weight:700">{amt}</td><td style="padding:5px 9px;border:1px solid var(--line);text-align:right">{y}</td><td style="padding:5px 9px;border:1px solid var(--line);text-align:right;color:var(--soft)">{avg}</td><td style="padding:5px 9px;border:1px solid var(--line);text-align:right;font-weight:800">{ratio}</td><td style="padding:5px 9px;border:1px solid var(--line)">{note}</td></tr>'''

etf_rows = "\n".join(etf_row(e) for e in ETFS)

CHART = sorted(ETFS, key=lambda x: float(x[4].replace("x", "")), reverse=True)

def chart_rows():
    out = []
    for i, (name, amt, y, avg, ratio, note, _) in enumerate(CHART):
        r = float(ratio.replace("x", ""))
        ypos = 50 + i * 26
        w = round(r * 250)
        if r >= 1.5:
            c = "#c0392b"
        elif r >= 1.0:
            c = "#ff7a00"
        elif r >= 0.7:
            c = "#8a8272"
        else:
            c = "#0a8f5b"
        short = {
            "159915": "创业板ETF", "588000": "科创50ETF", "510300": "300ETF华泰",
            "510500": "中证500ETF", "159919": "300ETF嘉实", "512100": "中证1000ETF",
            "518880": "黄金ETF", "510050": "上证50ETF", "588080": "科创50ETF易",
            "510310": "300ETF易方达", "512880": "证券ETF", "512480": "半导体ETF",
            "512890": "红利低波ETF", "512690": "酒ETF", "510330": "300ETF华夏",
            "512200": "房地产ETF",
        }.get(name.split(" ", 1)[0], name.split(" ", 1)[1])
        label = name.split(" ", 1)[0] + " " + short
        out.append(f'''  <text x="218" y="{ypos+12}" font-size="11.5" text-anchor="end" fill="#0d1117">{label}</text>
  <rect x="230" y="{ypos+1}" width="{w}" height="14" rx="3" fill="{c}"/>
  <text x="{230+w+7}" y="{ypos+12}" font-size="11.5" font-weight="800" fill="{c}">{ratio}</text>''')
    return "\n".join(out)

chart = chart_rows()

body = f'''<div class="wrap">

<header class="hero">
  <div class="kicker"><span class="type-tag">韭菜指数</span> 散户吃瓜指数 · Retail Watcher · 2026.10.29 全天收盘（周四）</div>
  <h1>昨天KTV，今天ICU：<em>创业板-4.45%</em>创14个月新低，<br>银行+1.98%四大行市值破10万亿——AI硬件杀估值，钱躲进红利</h1>
  <div class="meta">
    版本：韭菜指数 TOP10 · 全天收盘 15:00 · 环比参考：10/28 全天（上一期）；温度计环比基准：10/28 全天读数<br>
    数据来源：东方财富日K/涨停池收盘口径（16只ETF逐一对账） + 腾讯行情 + 财联社/21财经 + 公开讨论（v4.0 精简版）
  </div>
  <div class="badge-row">
    <span class="badge w">📉 沪指 -0.82% 报 3651.43 · 深成 -2.92% · 创业板 -4.45% · 科创50 -4.27%</span>
    <span class="badge w">📊 量能 1.56 万亿 · 较昨缩 720 亿 · 为20日均量的 97.7%</span>
    <span class="badge w">🌱 756 涨 / 4400 跌（14.5%）· 涨停 39 · 炸板 25 · 跌停 41 · 封板率 60.9% · 最高4板</span>
    <span class="badge hl-badge">💾 AI硬件：CPO -6.78% · PCB -5.55% · 半导体 -5.55% · 通信设备 -5.53%</span>
    <span class="badge fun-badge">🏦 防御：银行 +1.98% · 保险 +1.61% · 煤炭 +0.57% · 白酒 -1.45%</span>
    <span class="badge g">🏛 国家队：300ETF四只合计1.03x · 50ETF 0.76x · 16只合计591亿</span>
  </div>
  <div class="lead">
    <b>一句话看懂：</b>昨天还是KTV，今天直接ICU——<b>但钱没消失，是换岗了</b>。天孚通信业绩不及预期-19.77%，叠加Alphabet盘后-10%、三星Q3 miss，AI硬件链被集体杀估值；银行/保险/煤炭/食品接走避险资金，四大行总市值破10万亿。<b>指数被权重护住，成长被抽干</b>：沪指仅-0.82%，创业板-4.45%。
  </div>
</header>

<!-- ① 温度计 -->
<div class="eyebrow"><span class="num">🌡</span><span class="label">市场体温计 · 2026.10.29 全天收盘 · 环比 10/28 全天</span></div>

<div class="thermo-grid">
{chr(10).join(thermos)}
</div>
<div class="thermo-note">四降一升：指数、赚钱、讨论、风险偏好全部降温，唯独恐贪从64°升到66°——涨停从72家缩到39家，封板率却从51%升到61%，留下来的都是硬板。<br>分数按 scoring-v4 锚点复算；涨停均值用近14日替代（9/23-10/8池数据缺失，已标注）。</div>

<!-- 验证点对答案 -->
<div class="eyebrow"><span class="num">✓</span><span class="label">昨日三问 · 对答案（10/28 收盘复盘）</span></div>
<table class="verify-t">
  <thead><tr><th style="text-align:left">昨日预判</th><th>今日实际</th><th style="width:60px">判定</th></tr></thead>
  <tbody>
    <tr><td>A｜延续反弹（35%）</td><td>创业板未站稳2630，收2517.59，-4.45%</td><td style="color:#0a8f5b;font-weight:800">✗</td></tr>
    <tr><td>B｜冲高回落（45%）</td><td>开盘即最高，全天单边下行；沪指回踩3650兑现</td><td style="color:#b8860b;font-weight:800">半对</td></tr>
    <tr><td>C｜防御反扑（20%）</td><td>银行+1.98%、四大行市值破10万亿；但沪指失守3680</td><td style="color:#c0392b;font-weight:800">方向✓</td></tr>
  </tbody>
</table>
<div class="thermo-note">最大误判：只给防御反扑20%——低估了“业绩雷+海外科技杀跌”的共振，也高估了超跌反弹的持续性。</div>

<!-- ② TOP10 -->
<div class="eyebrow"><span class="num">🔥</span><span class="label">散户围观榜 TOP10 · 今天大家在聊什么</span></div>
<h2 class="sec-title">十张卡看懂：从AI硬件预期差，到银行红利走强</h2>
<div class="sec-desc">按讨论热度排序：业绩雷、杀估值、避险搬家三条线，构成今天的全部叙事。</div>

{ranks}

<!-- ③ 深吃瓜 -->
<div class="eyebrow"><span class="num">2</span><span class="label">前六大板块深吃瓜（含 L1~L5 散户分级）</span></div>
<h2 class="sec-title">每张卡片：核心数据 + 散户五级 + 一句话断症</h2>

<div class="deep-grid">
{deeps}
</div>

<!-- 韭菜浓度普查 -->
<div class="eyebrow"><span class="num">🔍</span><span class="label">韭菜浓度普查 · 谁最菜？</span></div>
<h2 class="sec-title">故事浓度最高、避险盘浓度最低——杀估值日的人群分布图</h2>

<div class="det-box">
  <div class="det-head"><span class="dt">大V解剖</span><span class="dn">韭菜浓度普查：<b>商业航天60%最高、银行红利16%最低</b></span></div>
  <div class="det-kicker">核心发现：<b>商业航天 L1+L2 60% 全场最高，银行/红利 16% 最低、L4+L5 60%</b>。故事越新韭菜越浓，但“机构多”不等于“会涨”——今天银行涨，是因为避险，不是因为人多。</div>
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
  <div class="det-verdict">侦探结论：商业航天60%最高、银行16%最低——一个靠新故事，一个靠旧股息。但浓度只描述人群，不预测涨跌：今天韭菜最浓的商业航天有涨停，机构最浓的银行也涨；真正危险的是CPO——韭菜不多，机构却在夺门而出。</div>
</div>

<!-- ④ 国家队 -->
<div class="eyebrow"><span class="num">4</span><span class="label">国家队资金动向 · ETF大搜查 · 16只全网格对账：今天到底来没来？</span></div>
<h2 class="sec-title">答案：托而不举——300ETF内部裂开，50ETF缩量，成长ETF在接飞刀</h2>

<div class="etf-verdict">
  <div class="stamp"><div class="big">托而不举</div><div class="sub">护指数，不救成长</div></div>
  <div class="why">
    <b>① 300ETF内部裂开：</b>四只合计154亿、仅1.03x均量；159919 2.11x，但510310 0.52x、510330 0.19x。<br>
    <b>② 50ETF缩量：</b>510050仅0.76x，权重端没有连续托底痕迹。<br>
    <b>③ 成长ETF放量下跌：</b>159915 1.26x、588000 1.16x，价格却-4.30%/-4.51%——更像接飞刀。<br>
    <b>④ 量级不够：</b>16只合计591亿，占两市成交3.8%；最大2.11x，离5x救市门槛差得远。
  </div>
</div>

<div class="det-box">
  <div class="det-head"><span class="dt">资金侦探</span><span class="dn">16只ETF放量倍数对账：<b>宽基10只+行业6只</b></span></div>
  <div class="det-kicker">今日成交 ÷ 昨日成交、今日成交 ÷ 近14个交易日（10/9~10/28）日均成交（东财日K收盘口径，单位亿元）。</div>
  <table style="width:100%;border-collapse:collapse;font-size:13px;margin:6px 0 4px;background:#fff">
    <thead><tr style="background:var(--ink);color:var(--paper)">
      <th style="padding:6px 9px;text-align:left;border:1px solid var(--ink)">ETF（按今日成交排序）</th>
      <th style="padding:6px 9px;text-align:right;border:1px solid var(--ink)">今日</th>
      <th style="padding:6px 9px;text-align:right;border:1px solid var(--ink)">昨日</th>
      <th style="padding:6px 9px;text-align:right;border:1px solid var(--ink)">14日均</th>
      <th style="padding:6px 9px;text-align:right;border:1px solid var(--ink)">倍数</th>
      <th style="padding:6px 9px;text-align:left;border:1px solid var(--ink)">判读</th>
    </tr></thead>
    <tbody>
{etf_rows}
    </tbody>
  </table>

  <h2 class="sec-title" style="font-size:17px;margin-top:18px">ETF放量全景 · 1.0x均量线，谁在裸泳</h2>
  <svg viewBox="0 0 1080 500" style="width:100%;height:auto;background:#fff;border:1px solid var(--line);border-radius:8px">
    <text x="230" y="22" font-size="12" font-weight="800" fill="#1f4e79">14日日均成交倍数（1.0x=均量线，1.5x=明显放量）</text>
    <line x1="480" y1="32" x2="480" y2="472" stroke="#6b6457" stroke-width="1.2" stroke-dasharray="5,4"/>
    <text x="480" y="492" font-size="10.5" fill="#6b6457" text-anchor="middle">1.0x</text>
    <line x1="605" y1="32" x2="605" y2="472" stroke="#c0392b" stroke-width="1.2" stroke-dasharray="5,4"/>
    <text x="605" y="492" font-size="10.5" fill="#c0392b" text-anchor="middle">1.5x</text>
    <text x="1040" y="22" font-size="10.5" fill="#8a8272" text-anchor="end">5x救市门槛在画外 →</text>
{chart}
  </svg>

  <h2 class="sec-title" style="font-size:17px;margin-top:20px">四维验证：今天为什么不是“国家队行情”</h2>
  <table class="verify-t">
    <thead><tr><th style="text-align:left">维度</th><th>救市样本特征</th><th>10/29 实际</th><th style="width:88px">判定</th></tr></thead>
    <tbody>
      <tr><td>① 载体</td><td>300/50等权重宽基爆量</td><td>300四只合计1.03x、50仅0.76x</td><td style="color:#0a8f5b;font-weight:800">❌ 反向</td></tr>
      <tr><td>② 结构</td><td>只买权重，中小盘躺平</td><td>创业板/科创50ETF逆势放量，权重缩量</td><td style="color:#0a8f5b;font-weight:800">❌ 非护盘</td></tr>
      <tr><td>③ 时点</td><td>尾盘定点脉冲</td><td>尾盘宽基ETF有集体放量，但无单只爆量</td><td style="color:#b8860b;font-weight:800">⚠️ 存疑</td></tr>
      <tr><td>④ 量级</td><td>单日5x起步</td><td>最大2.11x（低基数），16只合计591亿</td><td style="color:#0a8f5b;font-weight:800">❌ 未达门槛</td></tr>
    </tbody>
  </table>

  <div class="det-verdict">侦探结论：四条里三条否——载体反、结构偏、量级不够，只有尾盘有放量迹象。今天不是国家队大举进场，更像300ETF内部做低成本托底；成长ETF的放量，是散户和游资在接飞刀。明天验证：①300ETF四只是否同向放量 ②50ETF能否回到1.0x ③创业板ETF是否连续第三天放量。</div>
</div>

<!-- 尾盘节奏 -->
<h2 class="sec-title" style="font-size:17px;margin-top:20px">尾盘节奏还原 · 从低开到单边下杀</h2>
<table class="timeline-table">
  <thead><tr><th>时间窗</th><th>盘面动作</th><th>ETF端动作</th><th>性质判读</th></tr></thead>
  <tbody>
    <tr><td>9:30-10:00</td><td>创业板低开-1.46%报2596，反抽2597即全天最高；AI硬件领跌，银行红盘</td><td>300ETF开盘温和放量</td><td style="font-size:11.5px">开盘即定调：防守</td></tr>
    <tr><td>10:00-11:30</td><td>沪指围绕3660，创业板跌破2550；中国卫星10:24、航天晨光10:25封板</td><td>159915/588000持续放量</td><td style="font-size:11.5px">主题独舞，权重护盘</td></tr>
    <tr><td>13:00-14:00</td><td>创业板续跌，最低2516.78；CPO/PCB/半导体跌幅扩大</td><td>宽基ETF午后量能抬升</td><td style="font-size:11.5px">单边下杀，无抵抗</td></tr>
    <tr><td>14:00-14:40</td><td>天孚-19.77%，东山精密/沪电跌停；跌停家数升至41</td><td>尾盘宽基ETF集体放量（新闻口径）</td><td style="font-size:11.5px">恐慌盘与接飞刀对撞</td></tr>
    <tr><td>14:40-15:00</td><td>创业板收2517.59近最低，沪指3651.43；银行/保险守高位</td><td>30分钟占比缺失，仅确认真实放量</td><td style="font-size:11.5px">收盘无反弹，情绪冰点</td></tr>
  </tbody>
</table>

<!-- ⑤ 资金 -->
<div class="eyebrow"><span class="num">5</span><span class="label">主力资金 · 板块口径（不看个股）</span></div>
<div class="fund-box">
  <div class="fund-cols">
    <div class="fund-col in">
      <div class="fh">🔴 资金流入方向（避险端）</div>
      <div class="fund-row"><span class="fn">🏦 银行</span><span class="fv">+1.98% · 主力+1.11亿</span></div>
      <div class="fund-row"><span class="fn">🍶 白酒</span><span class="fv">主力+3.31亿 · 茅台+1.75%</span></div>
      <div class="fund-row"><span class="fn">🛢 煤炭</span><span class="fv">+0.57% · 开滦股份涨停</span></div>
      <div class="fund-row"><span class="fn">🛡 保险</span><span class="fv">+1.61% · 防御板块跟涨</span></div>
      <div class="fund-row"><span class="fn">🍔 食品加工</span><span class="fv">巴比/惠发/一鸣涨停</span></div>
    </div>
    <div class="fund-col out">
      <div class="fh">🟢 资金流出方向（AI硬件端）</div>
      <div class="fund-row"><span class="fn">💾 CPO</span><span class="fv">-6.78% · 主力-205.59亿</span></div>
      <div class="fund-row"><span class="fn">🔌 PCB</span><span class="fv">-5.55% · 主力-147.75亿</span></div>
      <div class="fund-row"><span class="fn">🔬 半导体</span><span class="fv">-5.55% · 主力-136.40亿</span></div>
      <div class="fund-row"><span class="fn">📡 通信设备</span><span class="fv">-5.53% · 主力-111.15亿</span></div>
      <div class="fund-row"><span class="fn">🥇 有色金属</span><span class="fv">-2.60% · 主力-30.03亿</span></div>
    </div>
  </div>
  <div class="fund-note"><b>一句话总结：</b>不是存量搬家那么简单——AI硬件四板块单日净流出600.9亿（CPO+PCB+半导体+通信设备），银行/白酒只接住零头；大部分钱在场外看戏，成交额缩了720亿。</div>
</div>

<!-- ⑥ 核心矛盾 -->
<div class="eyebrow"><span class="num">6</span><span class="label">全天核心矛盾 · 三条看懂</span></div>
<div class="pre-wrap">
  <div class="conf-item">🔴 <b>多头说：</b>沪指仅-0.82%、银行走强、成交仍1.56万亿；AI硬件跌是业绩雷，不是系统性风险，跌完更便宜。</div>
  <div class="conf-item">🟢 <b>空头说：</b>创业板14个月新低、124只跌超9.8%、跌停41家；CPO四板块净流出601亿，机构在夺门而出。</div>
  <div class="conf-item">🔮 <b>关键变量：</b>①创业板能否守2500 ②天孚/中际能否止跌 ③银行红利是否继续吸金 ④300ETF是否真放量 ⑤今晚美股科技股。</div>
</div>

<!-- ⑦ 明天预判 -->
<div class="eyebrow"><span class="num">🧭</span><span class="label">明天预判 · 精简3情景</span></div>
<div class="pre-wrap">
  <div class="pre-item"><b>情景A｜超跌修复（概率30%）</b>→ 创业板站稳2500，CPO龙头止跌，涨停回升50+；需300/500ETF持续放量。</div>
  <div class="pre-item"><b>情景B｜继续杀估值（概率45%）</b>→ 创业板跌破2500，跌停30+，银行/红利继续吸金；业绩雷向其他AI硬件扩散，<b>最可能</b>。</div>
  <div class="pre-item"><b>情景C｜风格再平衡（概率25%）</b>→ 成长止跌、银行歇脚，沪指围绕3650，成交缩到1.4万亿；方向等新催化。</div>
</div>

<!-- 数据说明 -->
<div class="disc">
  <b>📌 口径：</b>指数为10/29收盘：沪指3651.43/-0.82%（高3678.46/低3645.26）、深成-2.92%、创业板-4.45%、科创50-4.27%；成交1.56万亿（15,565.2亿），较10/28缩719.6亿；东财A股子集756涨/4400跌/62平（14.5%），财联社全市场781涨/4728跌；涨停39/炸板25/跌停41/封板率60.9%/最高4板（东财涨停池15:05快照，与财联社口径可能±1）。<br>
  <b>📌 温度计：</b>按 scoring-v4 锚点复算；市场热度量比97.7%、上涨占比14.5%；赚钱效应涨停家数用近14日均值53.4（9/23-10/8池数据缺失，降级替代）；讨论热度环比-4.4%；恐贪封板率60.9%、4板无修正；风险偏好进攻组（券商/半导体/军工/有色/煤炭）均值-2.33% − 防御组（银行/白酒/电力/公用）-0.36% = -1.98pct，落在10-24区间取14°。<br>
  <b>📌 ETF口径：</b>今日成交÷近14日（10/9~10/28）日均成交，东财日K收盘口径；16只合计591.0亿；尾盘30分钟占比因分钟线接口缺失未计算，仅保留“宽基ETF尾盘集体放量”的新闻口径；「救市级门槛」参照2024/2汇金样本单日5x起步。<br>
  <b>📌 L1-L5：</b>本期未完成每板块≥15条股吧/雪球样本采集，分布为盘面结构+关注度估算，按v4.0规则降级，不作为情绪结论；韭菜浓度=L1+L2，机构浓度=L4+L5。<br>
  <b>📌 资金流：</b>东财板块主力净流入为收盘快照，仅覆盖部分板块；白酒+3.31亿与白酒板块-1.45%并存，系茅台等权重与中小酒分化。<br>
  <b>📌 免责：</b>本报告为娱乐化的市场情绪观察，不构成任何投资建议；市场有风险，吃瓜需理性。
</div>

<div class="footer">
  🍉 <b>韭菜指数</b> · 2026.10.29 全天（昨天KTV，今天ICU：创业板-4.45%创14个月新低·银行+1.98%四大行市值破10万亿——AI硬件杀估值，红利成避风港） · 编制人：土豆 + Buddy<br>
  数据来源：东方财富 + 腾讯行情 + 财联社/21财经 + 公开讨论 · ⚠️ 仅为散户情绪观察，不构成投资建议
</div>

</div>
</body>
</html>'''

html_doc = prefix + body
open(OUT_HTML, "w", encoding="utf-8").write(html_doc)

vis = re.sub(r"<style.*?</style>", "", html_doc, flags=re.S)
vis = re.sub(r"<script.*?</script>", "", vis, flags=re.S)
vis = re.sub(r"<!--.*?-->", "", vis, flags=re.S)
vis = re.sub(r"<[^>]+>", "", vis)
vis = html.unescape(vis)
cn = len(re.findall(r"[一-鿿]", vis))
open(os.path.join(BASE, "_字数.txt"), "w", encoding="utf-8").write(f"可见中文字符：{cn}\n预算：4500\n")
print("HTML:", OUT_HTML)
print("可见中文字符:", cn)
