# -*- coding: utf-8 -*-
"""Build AAPL Buffett-framework valuation workbook and SVG dashboard.

All figures in USD billions unless noted. Data cut-off: 2026-10-29.
Official financials: FY2025 10-K (ended 2025-09-27) and FY2026 Q3 10-Q
(ended 2026-06-27, filed 2026-07-31). FY2026 Q4 not yet reported.
"""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.utils import get_column_letter

BASE = Path(__file__).resolve().parent
XLSX = BASE / "AAPL-估值模型-2026-10-29.xlsx"
SVG = BASE / "AAPL-估值仪表盘-2026-10-29.svg"
HTML = BASE / "AAPL-估值仪表盘-2026-10-29.html"

# ----------------------------------------------------------------------------
# Model inputs and outputs (computed independently of Excel formulas)
# ----------------------------------------------------------------------------
PRICE = 343.83
SHARES = 14.59418
NET_CASH = 39.544 + 22.855 + 84.118 - 1.997 - 11.007 - 71.340
MCAP = PRICE * SHARES
EV = MCAP - NET_CASH
FCF0 = 128.0

SCEN = {
    "bear": dict(g1=0.03, g2=0.02, gt=0.025, wacc=0.105, label="悲观"),
    "base": dict(g1=0.07, g2=0.05, gt=0.030, wacc=0.096, label="基准"),
    "bull": dict(g1=0.10, g2=0.07, gt=0.035, wacc=0.088, label="乐观"),
}


def dcf(fcf0, g1, g2, gt, wacc, years=10, split=5):
    fcf = fcf0
    pv = 0.0
    flows = []
    for t in range(1, years + 1):
        fcf *= 1 + (g1 if t <= split else g2)
        pv += fcf / (1 + wacc) ** t
        flows.append(fcf)
    tv = flows[-1] * (1 + gt) / (wacc - gt)
    pvtv = tv / (1 + wacc) ** years
    equity = pv + pvtv + NET_CASH
    return dict(equity=equity, ps=equity / SHARES, pv=pv, pvtv=pvtv, tv=tv, flows=flows)


def bisect(f, lo, hi, tol=1e-10):
    flo, fhi = f(lo), f(hi)
    for _ in range(300):
        mid = (lo + hi) / 2
        fm = f(mid)
        if abs(fm) < tol:
            return mid
        if flo * fm < 0:
            hi = mid
        else:
            lo = mid
            flo = fm
    return (lo + hi) / 2


RESULTS = {
    k: dcf(FCF0, v["g1"], v["g2"], v["gt"], v["wacc"])
    for k, v in SCEN.items()
}
IRR = {
    k: bisect(
        lambda w, g1=v["g1"], g2=v["g2"], gt=v["gt"]:
            dcf(FCF0, g1, g2, gt, w)["equity"] - EV,
        v["gt"] + 0.005, 0.30,
    )
    for k, v in SCEN.items()
}
IMPLIED_G = {
    w: bisect(lambda g: dcf(FCF0, g, g, 0.03, w)["equity"] - EV, -0.2, 0.4)
    for w in [0.080, 0.085, 0.090, 0.095, 0.096, 0.100, 0.105]
}
IMPLIED_WACC = bisect(
    lambda w: dcf(FCF0, 0.07, 0.05, 0.03, w)["equity"] - EV, 0.04, 0.20
)

# ----------------------------------------------------------------------------
# Styling helpers
# ----------------------------------------------------------------------------
FONT = "Microsoft YaHei"
C_DARK = "1F2933"
C_LIGHT = "F7F4EC"
C_CREAM = "E8E2D5"
C_RED = "B23A2E"
C_GREEN = "2F6B4F"
C_GOLD = "C9A227"
C_GREY = "5B6770"
C_YELLOW = "FFF2CC"
C_WHITE = "FFFFFF"

thin = Side(style="thin", color="D8D2C4")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)


def title(ws, cell, text, size=16):
    ws[cell] = text
    ws[cell].font = Font(name=FONT, size=size, bold=True, color=C_DARK)


def subtitle(ws, cell, text):
    ws[cell] = text
    ws[cell].font = Font(name=FONT, size=10, color=C_GREY)


def section(ws, row, text, ncols=8):
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(name=FONT, size=11, bold=True, color=C_DARK)
    cell.fill = PatternFill("solid", fgColor=C_CREAM)
    for c in range(1, ncols + 1):
        ws.cell(row=row, column=c).fill = PatternFill("solid", fgColor=C_CREAM)
        ws.cell(row=row, column=c).border = BORDER


def header_row(ws, row, values):
    for j, v in enumerate(values, 1):
        cell = ws.cell(row=row, column=j, value=v)
        cell.font = Font(name=FONT, size=9, bold=True, color=C_WHITE)
        cell.fill = PatternFill("solid", fgColor=C_DARK)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER


def body_cell(ws, row, col, value, fmt=None, bold=False, align="right", color=None):
    cell = ws.cell(row=row, column=col, value=value)
    cell.font = Font(name=FONT, size=9, bold=bold, color=color or C_DARK)
    cell.alignment = Alignment(horizontal=align, vertical="center")
    cell.border = BORDER
    if fmt:
        cell.number_format = fmt
    return cell


def widths(ws, mapping):
    for col, w in mapping.items():
        ws.column_dimensions[col].width = w


# ----------------------------------------------------------------------------
# Workbook
# ----------------------------------------------------------------------------
wb = Workbook()

# --- Sheet 1: 结论 -----------------------------------------------------------
ws = wb.active
ws.title = "结论"
ws.sheet_view.showGridLines = False
widths(ws, {"A": 24, "B": 18, "C": 20, "D": 22, "E": 14})

title(ws, "A1", "苹果公司（AAPL）巴菲特框架估值")
subtitle(ws, "A2", "研究日 2026-10-29｜价格日 2026-10-28 收盘｜币种：美元｜最新财报：FY2026 Q3（2026-06-27）")
subtitle(ws, "A3", "FY2026 Q4 尚未发布（预定 2026-11-02）；FY2026 全年为一致预期，不是实际值。")

section(ws, 5, "一句话结论", 5)
ws["A6"] = "好生意，但 5 万亿美元的价格没有安全边际；结论：观察，不追高。"
ws["A6"].font = Font(name=FONT, size=12, bold=True, color=C_RED)
ws["A6"].alignment = Alignment(wrap_text=True, vertical="center")
ws.merge_cells("A6:E6")
ws.row_dimensions[6].height = 32

section(ws, 8, "关键数据（十亿美元 / 倍 / 百分比）", 5)
header_row(ws, 9, ["项目", "数值", "备注"])
rows = [
    ("收盘价（美元）", PRICE, "2026-10-28 收盘", "$#,##0.00"),
    ("期末股数（十亿股）", SHARES, "2026-07-17 披露", "0.000"),
    ("市值（十亿美元）", "=B10*B11", "价格 × 股数", "#,##0.0"),
    ("净现金（十亿美元）", round(NET_CASH, 3), "现金及证券 − 总债务", "#,##0.0"),
    ("企业价值（十亿美元）", "=B12-B13", "市值 − 净现金", "#,##0.0"),
    ("TTM 收入", 466.823, "FY2025 + 9M FY2026 − 9M FY2025", "#,##0.0"),
    ("TTM 净利润", 128.930, "同上", "#,##0.0"),
    ("TTM EPS（美元）", 8.72, "稀释", "0.00"),
    ("正常化 FCFF", FCF0, "见“FCFF桥”", "#,##0.0"),
    ("P/E（TTM）", "=B10/B17", "现价 / TTM EPS", '0.0"x"'),
    ("P/E（FY2026E）", "=B10/8.84", "一致预期 EPS 8.84", '0.0"x"'),
    ("P/E（FY2027E）", "=B10/9.56", "一致预期 EPS 9.56", '0.0"x"'),
    ("FCF 收益率", "=B18/B12", "正常化 FCFF / 市值", "0.00%"),
    ("EV/FCFF", "=B14/B18", "企业价值 / 正常化 FCFF", '0.0"x"'),
    ("10 年期美债", 0.0503, "2026-10-28", "0.00%"),
    ("盈利收益率 − 10Y", "=1/B20-B24", "远期盈利收益率减无风险利率", "0.00%"),
]
for i, (label, value, note, fmt) in enumerate(rows, start=10):
    body_cell(ws, i, 1, label, align="left")
    body_cell(ws, i, 2, value, fmt=fmt, bold=isinstance(value, str) and value.startswith("="))
    body_cell(ws, i, 3, note, align="left")

section(ws, 27, "三情景 DCF（FCFF，WACC 折现，加净现金）", 5)
header_row(ws, 28, ["情景", "每股价值（美元）", "较现价", "安全边际（1−现价/价值）", "10 年 IRR"])
for i, k in enumerate(["bear", "base", "bull"], start=29):
    r = RESULTS[k]
    body_cell(ws, i, 1, SCEN[k]["label"], align="left", bold=(k == "base"))
    body_cell(ws, i, 2, round(r["ps"], 2), fmt="$#,##0.00", bold=(k == "base"))
    body_cell(ws, i, 3, f"=B{i}/$B$10-1", fmt="0.0%")
    body_cell(ws, i, 4, f"=1-$B$10/B{i}", fmt="0.0%")
    body_cell(ws, i, 5, round(IRR[k], 4), fmt="0.00%")
body_cell(ws, 32, 1, "现价", align="left", bold=True, color=C_RED)
body_cell(ws, 32, 2, PRICE, fmt="$#,##0.00", bold=True, color=C_RED)
body_cell(ws, 32, 3, 0, fmt="0.0%")
body_cell(ws, 32, 4, 0, fmt="0.0%")
body_cell(ws, 32, 5, "—", align="center")

section(ws, 34, "结论与观察条件", 5)
notes = [
    "基准价值约 177 美元，较现价低 48%；乐观情景 260 美元，仍较现价低 24%。",
    "当前价格隐含未来 10 年 FCFF 年增约 14.9%，或 WACC 降至约 6.5%。",
    "若要求 20% 安全边际：基准情景观察价约 142 美元；乐观情景约 208 美元。",
    "现价 343.83 美元高于两者。结论是“观察”，不是“卖出”指令。",
    "这不是投资建议；估值对 WACC、终值增长和正常化 FCFF 高度敏感。",
]
for i, text in enumerate(notes, start=35):
    ws.cell(row=i, column=1, value="• " + text).font = Font(name=FONT, size=10, color=C_DARK)
    ws.cell(row=i, column=1).alignment = Alignment(wrap_text=True, vertical="center")
    ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=5)
    ws.row_dimensions[i].height = 22

# Bar chart: scenario values vs current price
chart = BarChart()
chart.type = "bar"
chart.style = 10
chart.title = "每股价值：三情景 vs 现价（美元）"
chart.y_axis.title = "美元/股"
chart.x_axis.title = None
data = Reference(ws, min_col=2, min_row=28, max_row=32)
cats = Reference(ws, min_col=1, min_row=29, max_row=32)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
chart.height = 7.5
chart.width = 13
chart.legend = None
ws.add_chart(chart, "G9")

# --- Sheet 2: 历史财务 -------------------------------------------------------
ws = wb.create_sheet("历史财务")
ws.sheet_view.showGridLines = False
widths(ws, {"A": 26, "B": 12, "C": 12, "D": 12, "E": 12, "F": 12, "G": 13, "H": 13, "I": 30})
title(ws, "A1", "苹果五年财务与现金流（十亿美元，除每股数据）")
subtitle(ws, "A2", "FY2021–FY2025 来自 10-K；TTM = FY2025 + 9M FY2026 − 9M FY2025；FY2026E 为一致预期/正常化估计。")

header_row(ws, 4, ["项目", "FY2021", "FY2022", "FY2023", "FY2024", "FY2025", "TTM", "FY2026E", "备注"])
hist = {
    "收入": [365.817, 394.328, 383.285, 391.035, 416.161, 466.823, 477.85],
    "营业利润": [108.949, 119.437, 114.301, 123.216, 133.050, 154.859, None],
    "净利润": [94.680, 99.803, 96.995, 93.736, 112.010, 128.930, 129.10],
    "经营现金流": [104.038, 122.151, 110.543, 118.254, 111.482, 146.724, None],
    "资本开支": [11.085, 10.708, 10.959, 9.447, 12.715, 10.041, None],
    "稀释 EPS（美元）": [5.61, 6.11, 6.13, 6.08, 7.46, 8.72, 8.84],
    "稀释股数（十亿股）": [16.865, 16.326, 15.813, 15.408, 15.005, 14.715, 14.594],
}
row = 5
for label, vals in hist.items():
    body_cell(ws, row, 1, label, align="left", bold=True)
    for j, v in enumerate(vals, 2):
        body_cell(ws, row, j, v, fmt=("0.00" if "EPS" in label else ("0.000" if "股数" in label else "#,##0.0")))
    row += 1

# growth and margin rows
body_cell(ws, 12, 1, "收入增速", align="left", bold=True)
for col in range(3, 8):
    body_cell(ws, 12, col, f"={get_column_letter(col)}5/{get_column_letter(col-1)}5-1", fmt="0.0%")
body_cell(ws, 12, 8, "=H5/F5-1", fmt="0.0%")
body_cell(ws, 12, 9, "TTM 对 FY2025；FY2026E 对 FY2025", align="left")

body_cell(ws, 13, 1, "营业利润率", align="left", bold=True)
for col in range(2, 8):
    body_cell(ws, 13, col, f"={get_column_letter(col)}6/{get_column_letter(col)}5", fmt="0.0%")

body_cell(ws, 14, 1, "净利率", align="left", bold=True)
for col in range(2, 9):
    body_cell(ws, 14, col, f"={get_column_letter(col)}7/{get_column_letter(col)}5", fmt="0.0%")

body_cell(ws, 15, 1, "自由现金流（CFO−Capex）", align="left", bold=True)
for col in range(2, 8):
    body_cell(ws, 15, col, f"={get_column_letter(col)}8-{get_column_letter(col)}9", fmt="#,##0.0")

body_cell(ws, 16, 1, "FCF 利润率", align="left", bold=True)
for col in range(2, 8):
    body_cell(ws, 16, col, f"={get_column_letter(col)}15/{get_column_letter(col)}5", fmt="0.0%")

body_cell(ws, 17, 1, "FCF / 净利润", align="left", bold=True)
for col in range(2, 8):
    body_cell(ws, 17, col, f"={get_column_letter(col)}15/{get_column_letter(col)}7", fmt="0.00")

subtitle(ws, "A19", "要点：FY2025 FCF 仅 98.8B，受约 25B 营运资金拖累；TTM FCF 136.7B 又受营运资金同比改善和关税退款推动。正常化 FCFF 取 128B。")
ws["A19"].alignment = Alignment(wrap_text=True)
ws.merge_cells("A19:I19")
ws.row_dimensions[19].height = 30
subtitle(ws, "A20", "来源：SEC EDGAR Apple CIK 0000320193；FY2025 10-K（2025-10-31）；FY2026 Q3 10-Q（2026-07-31）；FY2026E 收入/EPS 为 Yahoo Finance/StockAnalysis 一致预期（2026-10-28）。")

# --- Sheet 3: FCFF桥 ---------------------------------------------------------
ws = wb.create_sheet("FCFF桥")
ws.sheet_view.showGridLines = False
widths(ws, {"A": 34, "B": 18, "C": 52})
title(ws, "A1", "正常化 FCFF 桥（TTM，十亿美元）")
subtitle(ws, "A2", "从 EBIT 出发，避免把股权激励和一次性营运资金/关税退款当成可持续现金流。")

header_row(ws, 4, ["项目", "数值", "说明"])
bridge = [
    ("EBIT（TTM）", 154.859, "营业利润"),
    ("税前利润（TTM）", 155.906, "含少量非经营净收益"),
    ("所得税（TTM）", 26.976, "10-Q 累计口径"),
    ("有效税率", "=B7/B6", "所得税 / 税前利润"),
    ("NOPAT", "=B5*(1-B8)", "EBIT × (1−税率)"),
    ("加：折旧摊销", 13.100, "TTM"),
    ("减：资本开支", 10.041, "TTM"),
    ("减：正常化营运资金增加", 2.000, "按收入增长约 5% 的温和假设"),
    ("减：一次性关税退款（税后）", 1.810, "Q3 FY2026 约 2pp 毛利率的一次性影响"),
    ("正常化 FCFF", "=B9+B10-B11-B12-B13", "DCF 使用值取整 128.0"),
]
for i, (label, value, note) in enumerate(bridge, start=5):
    body_cell(ws, i, 1, label, align="left", bold=(label in ("NOPAT", "正常化 FCFF")))
    body_cell(ws, i, 2, value, fmt=("0.0%" if label == "有效税率" else "#,##0.0"), bold=(label == "正常化 FCFF"))
    body_cell(ws, i, 3, note, align="left")

subtitle(ws, "A16", "对照：TTM CFO 146.724；TTM FCF（CFO−Capex）136.683；FY2025 FCF 98.767；FY2025 营运资金拖累约 25.178。")
ws["A16"].alignment = Alignment(wrap_text=True)
ws.merge_cells("A16:C16")
ws.row_dimensions[16].height = 30
subtitle(ws, "A17", "结论：报表 FCF 的波动主要来自营运资金和一次性项目，不是生意变差或变好；用 128B 作为正常化起点更接近可持续水平。")

# --- Sheet 4: DCF ------------------------------------------------------------
ws = wb.create_sheet("DCF")
ws.sheet_view.showGridLines = False
widths(ws, {"A": 24, "B": 14, "C": 14, "D": 14, "E": 14, "F": 14, "G": 14, "H": 14, "I": 14, "J": 14, "K": 14})
title(ws, "A1", "三情景 DCF（FCFF / WACC）")
subtitle(ws, "A2", "黄色单元格为假设，可修改；其余为公式。终值 = 第10年FCFF × (1+g) / (WACC−g)，再折回估值日。")

header_row(ws, 4, ["参数", "值", "说明"])
assumptions = [
    ("正常化 FCFF（十亿美元）", FCF0, "来自 FCFF桥"),
    ("净现金（十亿美元）", round(NET_CASH, 3), "2026-06-27"),
    ("股数（十亿股）", SHARES, "2026-07-17"),
    ("现价（美元）", PRICE, "2026-10-28"),
    ("预测期（年）", 10, "10 年明确预测"),
    ("前段年数", 5, "前 5 年用 g1"),
    ("终值增长", 0.03, "基准 3.0%"),
]
for i, (label, value, note) in enumerate(assumptions, start=5):
    body_cell(ws, i, 1, label, align="left")
    c = body_cell(ws, i, 2, value, fmt=("0.0%" if label == "终值增长" else ("0.000" if "股数" in label else ("$#,##0.00" if "现价" in label else "#,##0.0"))))
    c.fill = PatternFill("solid", fgColor=C_YELLOW)
    body_cell(ws, i, 3, note, align="left")
    ws.merge_cells(start_row=i, start_column=3, end_row=i, end_column=5)

header_row(ws, 13, ["情景", "WACC", "前段增速 g1", "后段增速 g2", "终值增长 g"])
for i, k in enumerate(["bear", "base", "bull"], start=14):
    v = SCEN[k]
    body_cell(ws, i, 1, v["label"], align="left", bold=(k == "base"))
    for j, key, fmt in [(2, "wacc", "0.0%"), (3, "g1", "0.0%"), (4, "g2", "0.0%"), (5, "gt", "0.0%")]:
        c = body_cell(ws, i, j, v[key], fmt=fmt)
        c.fill = PatternFill("solid", fgColor=C_YELLOW)


def dcf_block(ws, start, scen_row):
    title_row = start
    year_row = start + 1
    fcf_row = start + 2
    df_row = start + 3
    pv_row = start + 4
    sum_row = start + 6
    fcf10_row = start + 7
    tv_row = start + 8
    pvtv_row = start + 9
    ev_row = start + 10
    nc_row = start + 11
    eq_row = start + 12
    ps_row = start + 13
    up_row = start + 14
    mos_row = start + 15
    irr_row = start + 16
    cf_label_row = start + 17
    cf_row = start + 18

    title(ws, f"A{title_row}", f"{SCEN[list(SCEN)[scen_row - 14]]['label']}情景")
    body_cell(ws, year_row, 1, "年份", align="left", bold=True)
    for t in range(1, 11):
        body_cell(ws, year_row, 1 + t, t, fmt="0", align="center")
    body_cell(ws, fcf_row, 1, "FCFF", align="left", bold=True)
    for t in range(1, 11):
        col = 1 + t
        prev = get_column_letter(col - 1) if t > 1 else None
        growth_ref = f"$C${scen_row}" if t <= 5 else f"$D${scen_row}"
        if t == 1:
            formula = f"=$B$5*(1+{growth_ref})"
        else:
            formula = f"={prev}{fcf_row}*(1+{growth_ref})"
        body_cell(ws, fcf_row, col, formula, fmt="#,##0.0")
    body_cell(ws, df_row, 1, "折现因子", align="left")
    for t in range(1, 11):
        col = 1 + t
        body_cell(ws, df_row, col, f"=1/(1+$B${scen_row})^{get_column_letter(col)}{year_row}", fmt="0.000")
    body_cell(ws, pv_row, 1, "现值", align="left", bold=True)
    for t in range(1, 11):
        col = 1 + t
        body_cell(ws, pv_row, col, f"={get_column_letter(col)}{fcf_row}*{get_column_letter(col)}{df_row}", fmt="#,##0.0")

    body_cell(ws, sum_row, 1, "合计现值", align="left", bold=True)
    body_cell(ws, sum_row, 2, f"=SUM(B{pv_row}:K{pv_row})", fmt="#,##0.0")
    body_cell(ws, fcf10_row, 1, "第10年 FCFF", align="left")
    body_cell(ws, fcf10_row, 2, f"=K{fcf_row}", fmt="#,##0.0")
    body_cell(ws, tv_row, 1, "终值", align="left")
    body_cell(ws, tv_row, 2, f"=B{fcf10_row}*(1+$E${scen_row})/($B${scen_row}-$E${scen_row})", fmt="#,##0.0")
    body_cell(ws, pvtv_row, 1, "终值现值", align="left")
    body_cell(ws, pvtv_row, 2, f"=B{tv_row}/(1+$B${scen_row})^$B$9", fmt="#,##0.0")
    body_cell(ws, ev_row, 1, "企业价值", align="left", bold=True)
    body_cell(ws, ev_row, 2, f"=B{sum_row}+B{pvtv_row}", fmt="#,##0.0")
    body_cell(ws, nc_row, 1, "加：净现金", align="left")
    body_cell(ws, nc_row, 2, "=$B$6", fmt="#,##0.0")
    body_cell(ws, eq_row, 1, "股权价值", align="left", bold=True)
    body_cell(ws, eq_row, 2, f"=B{ev_row}+B{nc_row}", fmt="#,##0.0")
    body_cell(ws, ps_row, 1, "每股价值（美元）", align="left", bold=True)
    body_cell(ws, ps_row, 2, f"=B{eq_row}/$B$7", fmt="$#,##0.00")
    body_cell(ws, up_row, 1, "较现价", align="left")
    body_cell(ws, up_row, 2, f"=B{ps_row}/$B$8-1", fmt="0.0%")
    body_cell(ws, mos_row, 1, "安全边际", align="left")
    body_cell(ws, mos_row, 2, f"=1-$B$8/B{ps_row}", fmt="0.0%")
    body_cell(ws, irr_row, 1, "10年 IRR", align="left", bold=True)
    body_cell(ws, irr_row, 2, f"=IRR(B{cf_row}:L{cf_row})", fmt="0.00%")
    body_cell(ws, cf_label_row, 1, "现金流（用于IRR）", align="left")
    body_cell(ws, cf_row, 2, f"=-B{ev_row}", fmt="#,##0.0")
    for t in range(1, 11):
        col = 2 + t
        if t < 10:
            body_cell(ws, cf_row, col, f"={get_column_letter(col - 1)}{fcf_row}", fmt="#,##0.0")
        else:
            body_cell(ws, cf_row, col, f"={get_column_letter(col - 1)}{fcf_row}+B{tv_row}", fmt="#,##0.0")


dcf_block(ws, 20, 14)
dcf_block(ws, 42, 15)
dcf_block(ws, 64, 16)

subtitle(ws, "A85", "说明：Excel 公式在打开时重算；本报告结论数值由 Python 模型独立计算，未依赖 Excel 重算。终值占比：悲观约45%、基准约55%、乐观约64%。")

# --- Sheet 5: 敏感性 ---------------------------------------------------------
ws = wb.create_sheet("敏感性")
ws.sheet_view.showGridLines = False
widths(ws, {"A": 12, "B": 12, "C": 12, "D": 12, "E": 12, "F": 12, "G": 12})
title(ws, "A1", "敏感性与反推 DCF")
subtitle(ws, "A2", "每股价值（美元）；g2 = g1 − 2pp；终值增长 3%；FCFF0 = 128B。")

body_cell(ws, 4, 1, "g1 \\ WACC", align="center", bold=True)
for j, w in enumerate([0.080, 0.085, 0.090, 0.095, 0.100, 0.105], start=2):
    body_cell(ws, 4, j, w, fmt="0.0%", align="center", bold=True)
for i, g1 in enumerate([0.03, 0.05, 0.07, 0.09, 0.11], start=5):
    body_cell(ws, i, 1, g1, fmt="0%", align="center", bold=True)
    for j, w in enumerate([0.080, 0.085, 0.090, 0.095, 0.100, 0.105], start=2):
        val = dcf(FCF0, g1, max(g1 - 0.02, 0.005), 0.03, w)["ps"]
        body_cell(ws, i, j, round(val, 0), fmt="$#,##0")

body_cell(ws, 12, 1, "反推 DCF：现价隐含的 10 年 FCFF 年增速（终值 3%）", align="left", bold=True)
ws.merge_cells("A12:F12")
header_row(ws, 13, ["WACC", "隐含 g"])
for i, w in enumerate([0.080, 0.085, 0.090, 0.095, 0.096, 0.100, 0.105], start=14):
    body_cell(ws, i, 1, w, fmt="0.0%")
    body_cell(ws, i, 2, round(IMPLIED_G[w], 4), fmt="0.0%")

subtitle(ws, "A22", f"基准路径（7%/5%/3%）下，使现值等于当前企业价值的 WACC = {IMPLIED_WACC:.2%}。")
ws["A22"].alignment = Alignment(wrap_text=True)
ws.merge_cells("A22:F22")

# Line chart for reverse DCF
chart2 = LineChart()
chart2.title = "现价隐含的10年FCFF增速 vs WACC"
chart2.y_axis.title = "隐含 g"
chart2.x_axis.title = "WACC"
data2 = Reference(ws, min_col=2, min_row=13, max_row=20)
cats2 = Reference(ws, min_col=1, min_row=14, max_row=20)
chart2.add_data(data2, titles_from_data=True)
chart2.set_categories(cats2)
chart2.height = 7
chart2.width = 12
ws.add_chart(chart2, "D4")

# --- Sheet 6: 来源 -----------------------------------------------------------
ws = wb.create_sheet("来源")
ws.sheet_view.showGridLines = False
widths(ws, {"A": 34, "B": 40, "C": 16, "D": 60})
title(ws, "A1", "决定性来源与日期")
subtitle(ws, "A2", "关键值优先回原始财报；第三方数据只作价格、预期和交叉检查。")
header_row(ws, 4, ["数据/结论", "来源", "日期/期间", "链接/备注"])
sources = [
    ("FY2021–FY2025 财务", "SEC EDGAR, Apple Form 10-K (FY2025)", "2025-10-31", "https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/0000320193-25-000079-index.htm"),
    ("FY2026 Q3 财务/资产负债表", "SEC EDGAR, Apple Form 10-Q", "2026-07-31", "https://www.sec.gov/Archives/edgar/data/320193/000032019326000020/aapl-20260627.htm"),
    ("XBRL 原始值", "SEC companyfacts API, CIK 0000320193", "截至 2026-06-27", "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json"),
    ("Q3 FY2026 业绩/指引", "Apple Newsroom 中文稿", "2026-07-30", "https://www.apple.com.cn/newsroom/2026/07/apple-reports-third-quarter-results/"),
    ("Q4 财报日期", "9to5Mac", "2026-10-06", "https://9to5mac.com/2026/10/06/apple-sets-q4-2026-earnings-release-for-november-2/"),
    ("Q4 指引/内存成本", "Pepperstone Q4 FY2026 preview", "2026-10", "https://pepperstone.com/en-ae/insights/market-analysis/equities/apple-q4-2026-earnings-preview-rising-memory-costs-test-margins-can-premium-products-support-the-share-price"),
    ("价格/一致预期/目标价", "Yahoo Finance; StockAnalysis", "2026-10-28", "https://finance.yahoo.com/quote/AAPL/ ; https://stockanalysis.com/stocks/aapl/forecast/"),
    ("10 年期美债", "YCharts / CNBC", "2026-10-28", "https://ycharts.com/indicators/10_year_treasury_rate"),
    ("Beta", "Yahoo Finance 1.07; Morningstar 1.02", "2026-10", "取 1.05 作为中间值"),
    ("管理层交接", "Xinhua/CGTN", "2026-09-02", "http://english.news.cn/northamerica/20260902/e52e10456e1244318e93bb784baafc87/c.html"),
    ("iPhone Duo/高盛目标价", "Investing.com; 财联社", "2026-10", "https://www.investing.com/news/stock-market-news/analysts-split-on-apple-after-foldable-iphone-duo-debut-4895660"),
    ("AI/反垄断风险", "PYMNTS/Bona Law", "2026", "https://www.pymnts.com/cpi-posts/apples-gemini-siri-deal-is-the-next-microsoft-antitrust-case-not-the-next-app-store-fight/"),
    ("历史估值/记录高位", "Yahoo Finance; FinanceCharts; GuruFocus", "2026-10", "https://finance.yahoo.com/markets/stocks/articles/apple-hits-highest-valuation-level-194516959.html"),
]
for i, (a, b, c, d) in enumerate(sources, start=5):
    body_cell(ws, i, 1, a, align="left", bold=True)
    body_cell(ws, i, 2, b, align="left")
    body_cell(ws, i, 3, c, align="left")
    body_cell(ws, i, 4, d, align="left")
    ws.row_dimensions[i].height = 28
    ws.cell(row=i, column=4).alignment = Alignment(wrap_text=True, vertical="center")

# save
wb.save(XLSX)
print("saved:", XLSX)
print("scenario:", {k: round(v["ps"], 2) for k, v in RESULTS.items()})
print("IRR:", {k: round(v, 4) for k, v in IRR.items()})
print("implied g @9.6%:", round(IMPLIED_G[0.096], 4))
print("implied WACC:", round(IMPLIED_WACC, 4))
