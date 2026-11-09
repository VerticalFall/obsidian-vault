# -*- coding: utf-8 -*-
"""第四锚扩展：A股与美股市场结构评分、折价区间与敏感性。
在 build_structure_overlay.py 之后运行。"""
import json, csv, os
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

BASE = "输出/指数/2026-11-08"
rows = json.load(open(f"{BASE}/_data/index_valuation_model.json", encoding="utf-8"))

def discount_range(r):
    if r["k"] == "hsi":
        return 0.05, 0.15
    if r["k"] == "hstech":
        return 0.10, 0.25
    if r["market"] == "A股":
        return 0.00, 0.05
    return 0.00, 0.05

def verdict(level, base, low, high):
    if level < low:
        return "低估区"
    if level > high:
        return "高估区"
    return "合理区偏下" if level < base else "合理区偏上"

for r in rows:
    lo, hi = discount_range(r)
    r["struct_discount_low"] = lo
    r["struct_discount_high"] = hi
    r["base_val_adj_low"] = round(r["base_val"] * (1 - lo))
    r["base_val_adj_high"] = round(r["base_val"] * (1 - hi))
    for tag, base_x in (("low", r["base_val_adj_low"]), ("high", r["base_val_adj_high"])):
        low_x = max(r["bear_val"], base_x * (1 - r["mos"]))
        high_x = min(r["bull_val"], base_x * (1 + r["mos"]))
        r[f"low_line_adj_{tag}"] = round(low_x)
        r[f"high_line_adj_{tag}"] = round(high_x)
        r[f"verdict_adj_{tag}"] = verdict(r["level"], base_x, low_x, high_x)

json.dump(rows, open(f"{BASE}/_data/index_valuation_model.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
keys = list(rows[0].keys())
for _r in rows:
    for _k in _r.keys():
        if _k not in keys:
            keys.append(_k)
with open(f"{BASE}/_data/index_valuation_model.csv", "w", encoding="utf-8-sig", newline="") as fo:
    w = csv.DictWriter(fo, fieldnames=keys)
    w.writeheader()
    w.writerows(rows)

def fmt(x): return f"{x:,.0f}" if isinstance(x, (int, float)) else "—"

# ---------------- 13 号备忘录 ----------------
a_rows = [r for r in rows if r["market"] == "A股"]
us_rows = [r for r in rows if r["market"] == "美股"]
def sens_table(rs):
    out = ["| 指数 | 基准中枢 | 低折价中枢 | 高折价中枢 | 现价 | 高折价结论 |", "|---|---:|---:|---:|---:|---|"]
    for r in rs:
        out.append(f"| {r['name']} | {fmt(r['base_val'])} | {fmt(r['base_val_adj_low'])} | {fmt(r['base_val_adj_high'])} | {fmt(r['level'])} | {r['verdict_adj_high']} |")
    return "\n".join(out)

memo = f"""# A股与美股市场结构评估：流动性、定价权、政策与治理（第四锚扩展）

> 数据日：2026-11-06｜报告日：2026-11-08｜补充模块：巴菲特指数基准版

## 0. 结论

把“第四锚”从港股扩展到A股和美股后，三个市场的结构差异可以总结为：

- **A股**：流动性总量高，但结构上“散户+量化”主导、交易向头部集中；定价权在国内资金，外资持股仅约3.7%流通市值；政策/监管与国企治理是主要折价来源。基准结构折价0%，敏感性0%—5%。若按5%折价，沪深300合理中枢约4,035（现价4,054，基本合理）、上证约3,394（现价3,649，偏上）、创业板约2,900（现价2,465，仍偏低）。
- **美股**：全球最深流动性、机构定价、SEC披露与执法强；但标普500前十大权重约40%—43%、Mag7约33%—34%，为历史极值，集中度/反垄断/财政是主要结构风险。基准结构折价0%，敏感性0%—5%。若按5%折价，标普合理中枢约7,240（现价7,377，偏上）、道指约48,305（现价51,286，明显偏上）、纳指约28,475（现价26,990，仍偏低）。
- **港股**：结构折价最高（恒指5%—15%、恒生科技10%—25%），详见 [[12_港股市场结构评估_流动性定价权与治理]]。

## 1. A股：流动性高，但定价结构偏内部

### 1.1 关键数据（2026年上半年，口径有差异）

| 指标 | 数据 | 说明 |
|---|---|---|
| 日均成交额 | 约3万亿元（券商周报口径） | 2026年5月一度3.4万亿，周度波动大；另有1.2万亿的自媒体口径，不采信 |
| 散户成交占比 | 约60%以上 | 同花顺2026年5月末口径；另有18.6%的冲突说法，可能指活跃散户 |
| 量化成交占比 | 约36.8% | 量化持股市值仅占流通市值2%—3%，部分交易日成交占比>40% |
| 北向持股 | 约2.4万亿元，占流通市值约3.7% | 全口径境外持股可能更高（含QFII/RQFII） |
| 两融余额 | 约2.92万亿元 | 两融成交占比约9.8%—10.3% |
| 交易集中度 | 前5%个股占成交额约47.8% | 流动性总量高但结构分化 |
| 流通市值结构 | 产业资本约45%、自然人约33%、机构约22% | 口径为2026年5—6月 |

### 1.2 评分

| 维度 | 评分 | 判断 |
|---|---:|---|
| 流动性 | 4.0/5 | 总量高、换手快；但向头部集中，小盘股流动性分化 |
| 定价权 | 3.0/5 | 国内散户+量化+机构主导，外资占比低；政策/国家队影响大 |
| 政策/监管 | 3.0/5 | IPO/再融资、T+1、涨跌停、印花税、国企考核；政策周期影响大 |
| 治理/股东回报 | 3.0/5 | 国企权重高、关联交易与市值管理并存；分红/回购在改善 |
| **综合** | **3.25/5** | 结构折价0%—5%（基准0%） |

### 1.3 含义

- A股的“流动性溢价”是结构性的：散户与量化提供高换手，但定价权并不完全市场化；政策与国企治理折价应从估值中扣除。
- 若按5%政策/治理折价，A股宽基的“便宜”会明显收窄：沪深300从-4.5%变为基本合理，上证从+2.1%变为偏上，创业板仍偏低。
- 5%折价敏感性：

{sens_table(a_rows)}

## 2. 美股：流动性最深，但集中度是历史极值

### 2.1 关键数据（2026年中）

| 指标 | 数据 | 说明 |
|---|---|---|
| 标普500前十大权重 | 约40%—43% | 2026年7月约43%（RBC/InvestmentNews），为历史最高；1990—2015年均值约18%—23% |
| Mag7权重 | 约33%—34% | 2026年6月约33.8%，是2016年约12.5%的近三倍 |
| 信息技术板块 | 约34.6% | Wedbush，2026年1月 |
| 前十大盈利占比 | 约三分之一 | 低于其43%的市值占比，说明估值溢价高 |
| 流动性/定价权 | 全球最深 | 机构定价、SEC披露与执法强、股东回报文化成熟 |

### 2.2 评分

| 维度 | 评分 | 判断 |
|---|---:|---|
| 流动性 | 5.0/5 | 全球最深，买卖价差小，可容纳大资金 |
| 定价权 | 5.0/5 | 全球机构定价，美元资产；外资/被动资金持续流入 |
| 政策/监管 | 4.5/5 | SEC披露/执法强；但反垄断、财政、关税与行业监管仍有不确定性 |
| 治理/股东回报 | 4.5/5 | 回购/分红成熟；但双重股权、高管薪酬与集中度问题存在 |
| **综合** | **4.75/5** | 结构折价0%—5%（基准0%） |

### 2.3 含义

- 美股的结构优势是真实的：流动性、法治、披露、股东回报都强于A股/港股；因此基准不给结构折价。
- 但“指数集中度”是新的结构性风险：前十大占40%—43%，Mag7占33%—34%，指数越来越像“科技七巨头+其余493家”。一旦AI资本开支回报不及预期或反垄断升温，5%的集中度/监管折价是合理的压力测试。
- 5%折价敏感性：

{sens_table(us_rows)}

## 3. 三市场对比

| 市场 | 流动性 | 定价权 | 政策/监管 | 治理/股东回报 | 综合 | 结构折价区间 |
|---|---:|---:|---:|---:|---:|---|
| A股 | 4.0 | 3.0 | 3.0 | 3.0 | 3.25 | 0%—5% |
| 港股 | 2.5 | 2.0 | 2.0 | 2.5 | 2.25 | 恒指5%—15%；恒生科技10%—25% |
| 美股 | 5.0 | 5.0 | 4.5 | 4.5 | 4.75 | 0%—5% |

## 4. 结论

- **A股**：结构不是“完美市场”，但流动性总量和国内定价权支撑估值；0%—5%折价是合理的政策/治理补偿。基准0%时沪深300/A500偏低；5%压力下沪深300基本合理、上证偏上、创业板仍偏低。
- **美股**：结构评分最高，基准0%折价；但集中度处于历史极值，5%压力测试下标普/道指更贵、纳指仍低于中枢。
- **港股**：结构评分最低，折价最高；恒生科技的低估是“结构性低估”，不是“深度低估”。

## 5. 来源

- A股成交/散户/量化/北向：同花顺《2026年5月末A股散户与机构持仓集中方向统计分析报告》，http://t.10jqka.com.cn/pid_637908389.shtml；国泰海通周报（新浪财经），https://stock.finance.sina.com.cn/stock/view/paper.php?symbol=sh000001&reportid=833220327430&autocallup=no&isfromsina=no；A股资金结构，https://www.sina.cn/news/detail/5341535295243433.html
- 美股集中度：InvestmentNews，https://www.investmentnews.com/equities/index-concentration/267368；KuCoin，https://www.kucoin.com/news/flash/top-10-us-stocks-now-account-for-43-of-s-p-500-market-cap；Wedbush，https://investor.wedbush.com/wedbush/article/marketminute-2026-1-28-the-tech-tsunami-s-and-p-500-hits-7000-as-tech-concentration-reaches-historic-34；ATB，https://www.atb.com/wealth/good-advice/markets/beyond-the-magnificent-seven-how-to-fix-the-sp-500s-record-concentration-risk/
- 港股：见 [[12_港股市场结构评估_流动性定价权与治理]] 第9节

> 免责声明：本报告为估值与市场结构研究，不构成投资建议；评分与折价为研究判断，数据口径以来源为准。
"""
open(f"{BASE}/13_A股与美股市场结构评估_流动性定价权政策与治理.md", "w", encoding="utf-8").write(memo)

# ---------------- 给 A股/美股分报告插入第四锚 ----------------
A_TEXT = """
## 4.5 第四锚：市场结构（A股）

- 评分：流动性4.0/5、定价权3.0、政策/监管3.0、治理/股东回报3.0，综合3.25/5；基准结构折价0%，敏感性0%—5%。
- 结构特征：2026H1全A日均成交约3万亿元（券商口径）；散户成交占比约六成、量化约36.8%、北向持股约3.7%流通市值；交易向头部5%个股集中（约47.8%成交）。定价权在国内资金，政策/监管与国企治理是主要折价来源。
- 若按5%政策/治理折价：合理中枢约 {base_high} 点（现价 {level}，{pos_high}）；结论：{verdict_high}。
- 详见 [[13_A股与美股市场结构评估_流动性定价权政策与治理]]。

"""
US_TEXT = """
## 4.5 第四锚：市场结构（美股）

- 评分：流动性5.0/5、定价权5.0、政策/监管4.5、治理/股东回报4.5，综合4.75/5；基准结构折价0%，敏感性0%—5%。
- 结构特征：全球最深流动性、机构定价、SEC披露与执法强；但标普500前十大权重约40%—43%（2026年中，历史极值），Mag7约33%—34%，科技板块约34.6%；集中度、反垄断与财政/利率是主要结构风险。
- 若按5%集中度/监管折价：合理中枢约 {base_high} 点（现价 {level}，{pos_high}）；结论：{verdict_high}。
- 详见 [[13_A股与美股市场结构评估_流动性定价权政策与治理]]。

"""
files = {
    "sh": "01_上证指数.md", "sz": "02_深证成指.md", "hs300": "03_沪深300.md",
    "a500": "04_中证A500.md", "cyb": "05_创业板指.md", "kc50": "06_科创50.md",
    "spx": "09_标普500.md", "dji": "10_道琼斯.md", "ndx": "11_纳斯达克100.md",
}
for r in rows:
    if r["k"] not in files:
        continue
    p = f"{BASE}/{files[r['k']]}"
    s = open(p, encoding="utf-8").read()
    if "## 4.5 第四锚" in s:
        continue
    tpl = A_TEXT if r["market"] == "A股" else US_TEXT
    sec = tpl.format(base_high=fmt(r["base_val_adj_high"]), level=fmt(r["level"]),
                     pos_high=f"{(r['level']/r['base_val_adj_high']-1)*100:+.1f}%",
                     verdict_high=r["verdict_adj_high"])
    s = s.replace("## 5. 多空要点", sec + "## 5. 多空要点")
    open(p, "w", encoding="utf-8").write(s)

# ---------------- 更新总览 ----------------
p = f"{BASE}/00_十一大指数基准与估值区间_总览.md"
s = open(p, encoding="utf-8").read()
s = s.replace("| 港股 | 2.5 | 2.0 | 2.0 | 2.5 | 2.25 | 恒指10%，恒生科技15% |",
              "| 港股 | 2.5 | 2.0 | 2.0 | 2.5 | 2.25 | 恒指5%—15%，恒生科技10%—25% |")
s = s.replace("| 美股 | 5.0 | 5.0 | 4.5 | 4.5 | 4.75 | 0% |",
              "| 美股 | 5.0 | 5.0 | 4.5 | 4.5 | 4.75 | 0%—5% |")
anchor = "- 详细见 [[12_港股市场结构评估_流动性定价权与治理]]。"
addition = """
- **A股/美股结构敏感性**：A股基准折价0%，若按5%政策/治理折价，沪深300合理中枢约4,035（现价4,054，基本合理）、上证约3,394（现价3,649，偏上）、创业板约2,900（现价2,465，仍偏低）；美股基准0%，若按5%集中度/监管折价，标普约7,240（现价7,377，偏上）、道指约48,305（现价51,286，明显偏上）、纳指约28,475（现价26,990，仍偏低）。
- A股/美股结构评分与折价敏感性详见 [[13_A股与美股市场结构评估_流动性定价权政策与治理]]。
"""
if "A股/美股结构敏感性" not in s:
    s = s.replace(anchor, anchor + addition)
# 分指数报告列表补充 12/13
s = s.replace("- [[11_纳斯达克100]]", "- [[11_纳斯达克100]]\n- [[12_港股市场结构评估_流动性定价权与治理]]\n- [[13_A股与美股市场结构评估_流动性定价权政策与治理]]")
open(p, "w", encoding="utf-8").write(s)

# ---------------- README ----------------
p = f"{BASE}/README.md"
s = open(p, encoding="utf-8").read()
if "13_A股与美股" not in s:
    s += """
- [[13_A股与美股市场结构评估_流动性定价权政策与治理]]：A股/美股第四锚评分与0%—5%折价敏感性。
- 运行顺序：`build_reports.py` → `build_structure_overlay.py` → `build_structure_overlay_all.py`。
"""
open(p, "w", encoding="utf-8").write(s)

# ---------------- Excel 结构折价表（含折价区间） ----------------
xlsx = f"{BASE}/指数基准分析_2026-11-08.xlsx"
wb = load_workbook(xlsx)
if "结构折价" in wb.sheetnames:
    del wb["结构折价"]
ws = wb.create_sheet("结构折价")
ws.append(["指数", "市场", "流动性", "定价权", "政策监管", "治理股东回报", "综合评分",
           "基准折价", "折价下限", "折价上限", "原合理中枢",
           "调整后中枢(基准)", "调整后中枢(低折价)", "调整后中枢(高折价)",
           "基准结论", "高折价结论", "现价"])
for r in rows:
    ws.append([r["name"], r["market"], r["liq_score"], r["pricing_score"], r["policy_score"],
               r["governance_score"], r["struct_score"], r["struct_discount"],
               r["struct_discount_low"], r["struct_discount_high"], r["base_val"],
               r["base_val_adj"], r["base_val_adj_low"], r["base_val_adj_high"],
               r["verdict_adj"], r["verdict_adj_high"], r["level"]])
hdr_fill = PatternFill("solid", fgColor="1F4E78")
hdr_font = Font(color="FFFFFF", bold=True)
for c in ws[1]:
    c.fill = hdr_fill
    c.font = hdr_font
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
for i, w in enumerate([14, 8, 8, 8, 9, 12, 9, 9, 9, 9, 11, 13, 14, 14, 14, 12, 10], 1):
    ws.column_dimensions[chr(64 + i)].width = w
ws.freeze_panes = "A2"
for row in ws.iter_rows(min_row=2):
    for c in row:
        c.alignment = Alignment(horizontal="center", vertical="center")
    for idx in (7, 8, 9):
        row[idx].number_format = "0%"
    for idx in (10, 11, 12, 13, 16):
        row[idx].number_format = "#,##0"
wb.save(xlsx)
print("A/US structure overlay done")
