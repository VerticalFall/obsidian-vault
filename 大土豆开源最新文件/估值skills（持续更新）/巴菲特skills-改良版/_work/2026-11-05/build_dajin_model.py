# -*- coding: utf-8 -*-
"""Build Dajin Heavy Industry (002487.SZ) valuation workbook (2026-11-05)."""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / "输出" / "A股" / "002487.SZ-2026-11-05" / "大金重工-002487.SZ-估值模型-2026-11-05.xlsx"

GREEN = "2F6B4F"; GOLD = "C9A227"; RED = "B23A2E"; BROWN = "8C6D5A"
INK = "1F2933"; MUTED = "5B6770"; BORDER = "D9D2C5"
TITLE_FILL = PatternFill("solid", fgColor=GREEN)
SECTION_FILL = PatternFill("solid", fgColor="E8EFE9")
HEADER_FILL = PatternFill("solid", fgColor="EFE8D8")
NOTE_FILL = PatternFill("solid", fgColor="FBF7EA")
GREEN_FILL = PatternFill("solid", fgColor="E3EFE7")
GOLD_FILL = PatternFill("solid", fgColor="F7EFD2")
RED_FILL = PatternFill("solid", fgColor="F8E5E1")
THIN = Side(style="thin", color=BORDER)
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
FONT = "Microsoft YaHei"


def title(ws, text, ncols):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
    c = ws.cell(row=1, column=1, value=text)
    c.font = Font(name=FONT, size=15, bold=True, color="FFFFFF")
    c.fill = TITLE_FILL
    c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[1].height = 30


def subtitle(ws, text, ncols):
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ncols)
    c = ws.cell(row=2, column=1, value=text)
    c.font = Font(name=FONT, size=9, color=MUTED)
    c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[2].height = 18


def section(ws, row, text, ncols):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)
    c = ws.cell(row=row, column=1, value=text)
    c.font = Font(name=FONT, size=11, bold=True, color=GREEN)
    c.fill = SECTION_FILL
    c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[row].height = 22


def header(ws, row, values, widths=None):
    for j, v in enumerate(values, 1):
        c = ws.cell(row=row, column=j, value=v)
        c.font = Font(name=FONT, size=9.5, bold=True, color="5B4A3A")
        c.fill = HEADER_FILL
        c.border = BORDER_ALL
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 30
    if widths:
        for j, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(j)].width = w


def cell(ws, row, col, value, fmt=None, bold=False, color=INK, fill=None,
         align="right", wrap=False, size=9.5):
    c = ws.cell(row=row, column=col, value=value)
    c.font = Font(name=FONT, size=size, bold=bold, color=color)
    c.border = BORDER_ALL
    c.alignment = Alignment(horizontal=align, vertical="center", wrap_text=wrap)
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    return c


def block(ws, r1, c1, r2, c2, text, size=9.5, color=INK, fill=None, height=None):
    ws.merge_cells(start_row=r1, start_column=c1, end_row=r2, end_column=c2)
    c = ws.cell(row=r1, column=c1, value=text)
    c.font = Font(name=FONT, size=size, color=color)
    c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True, indent=1)
    if fill:
        c.fill = fill
    if height:
        ws.row_dimensions[r1].height = height


def finish(ws, ncols, freeze="A5"):
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = freeze
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_options.horizontalCentered = True
    ws.sheet_properties.tabColor = GREEN
    ws.page_setup.paperSize = 9


def sheet_one(wb):
    ws = wb.active
    ws.title = "一图流"
    title(ws, "大金重工 002487.SZ · 巴菲特框架估值", 8)
    subtitle(ws, "报告日 2026-11-05｜价格日 2026-11-05 收盘｜单位：人民币亿元、元/股", 8)
    widths = [20, 16, 26, 10, 20, 16, 34, 3]
    for j, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(j)].width = w
    section(ws, 4, "一句话结论", 8)
    block(ws, 5, 1, 5, 8,
          "好生意，但 2026 年是交付节奏造成的利润低谷；A 股现价 34.82 元低于综合基准 40.42 元约 13.8%，算“合理偏低”，"
          "但相对 H 股仍有 76% 溢价。2027 年看欧洲订单修复 + 曹妃甸产能 + 造船第二曲线。",
          fill=GOLD_FILL, size=10.5, height=48)
    section(ws, 7, "关键读数", 8)
    header(ws, 8, ["指标", "数值", "说明", "", "指标", "数值", "说明", ""])
    rows = [
        ("现价", 34.82, "元/股", "2026E PE", 25.8, "倍"),
        ("总市值", 257.7, "亿元", "2027E PE", 17.8, "倍"),
        ("2025 净利", 11.03, "亿元", "DCF", 41.64, "元"),
        ("2026E 净利", 10.0, "亿元", "PE 法", 39.19, "元"),
        ("综合基准", 40.42, "元", "安全边际", 0.138, "%"),
        ("20% 边际价", 32.34, "元", "评级", "合理偏低", ""),
    ]
    for i, (l1, v1, u1, l2, v2, u2) in enumerate(rows):
        r = 9 + i
        cell(ws, r, 1, l1, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        fmt1 = "0.0%" if u1 == "%" else ("#,##0.0" if abs(v1) > 1000 else "0.00")
        cell(ws, r, 2, v1, fmt=fmt1, bold=True)
        cell(ws, r, 3, u1, align="left", color=MUTED)
        cell(ws, r, 5, l2, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        if isinstance(v2, str):
            cell(ws, r, 6, v2, bold=True, color=GOLD, align="center")
        else:
            fmt2 = "0.0%" if u2 == "%" else ("#,##0" if abs(v2) > 1000 else "0.00")
            cell(ws, r, 6, v2, fmt=fmt2, bold=True)
        cell(ws, r, 7, u2, align="left", color=MUTED)
    section(ws, 16, "三情景每股价值", 8)
    header(ws, 17, ["情景", "DCF", "PE", "综合", "现价", "较现价", "核心假设", ""])
    scen = [
        ("悲观", 20.16, 20.81, 20.49, "2027E 净利 11 亿、PE 14x；DCF F0 7 亿"),
        ("基准", 41.64, 39.19, 40.42, "2027E 净利 14.5 亿、PE 20x；DCF F0 10 亿"),
        ("乐观", 71.70, 55.14, 63.42, "2027E 净利 17 亿、PE 24x；DCF F0 13 亿"),
    ]
    for i, (name, dcf, pe, blend, cond) in enumerate(scen):
        r = 18 + i
        fill = GOLD_FILL if name == "基准" else None
        cell(ws, r, 1, name, align="center", bold=True, fill=fill)
        cell(ws, r, 2, dcf, fmt="0.00", bold=True, fill=fill)
        cell(ws, r, 3, pe, fmt="0.00", bold=True, fill=fill)
        cell(ws, r, 4, blend, fmt="0.00", bold=True, fill=fill)
        cell(ws, r, 5, 34.82, fmt="0.00", fill=fill)
        cell(ws, r, 6, blend / 34.82 - 1, fmt="0.0%", bold=True,
             color=(GREEN if blend > 34.82 else RED), fill=fill)
        block(ws, r, 7, r, 8, cond, size=8.5, color=MUTED, fill=fill)
        ws.row_dimensions[r].height = 28
    block(ws, 22, 1, 24, 8,
          "A/H：A 股 34.82 元 vs H 股 23.08 港元（约 19.76 元），A/H 溢价 76%。同一资产，H 股明显更便宜；"
          "若可投港股，H 股的安全边际更大。",
          size=9, color=MUTED, fill=NOTE_FILL, height=42)
    finish(ws, 8)
    ws.print_area = "A1:H24"


def sheet_valuation(wb):
    ws = wb.create_sheet("估值系统")
    title(ws, "估值系统 · DCF + PE 双锚", 8)
    subtitle(ws, "单位：人民币亿元、元/股；现价 34.82 元；本文假设，不是公司指引", 8)
    widths = [24, 14, 16, 12, 24, 14, 16, 3]
    for j, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(j)].width = w
    section(ws, 4, "一、核心假设", 8)
    header(ws, 5, ["假设", "数值", "说明", "", "假设", "数值", "说明", ""])
    rows = [
        ("2026E 净利", 10.0, "9M 7.10 + Q4 2.9", "2027E 净利", 14.5, "JPM 16.0、Citi 14–15"),
        ("2026E EPS", 1.35, "10.0 / 7.40", "2027E EPS", 1.96, "14.5 / 7.40"),
        ("DCF F0", 10.0, "正常化 FCF", "增速起点", 0.15, "2027 年"),
        ("WACC", 0.095, "Ke 11%、Kd 3%", "终端 g", 0.03, "长期通胀"),
        ("净现金", 50.75, "2026Q3", "总股本", 7.40, "A+H"),
        ("目标 PE", 20, "2027E 增速 +45%", "现价", 34.82, "2026-11-05"),
    ]
    for i, (a, b, c, d, e, f) in enumerate(rows):
        r = 6 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 2, b, fmt="0.0%" if isinstance(b, float) and b < 1 else "0.00", bold=True)
        cell(ws, r, 3, c, align="left", size=9, color=MUTED)
        cell(ws, r, 5, d, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 6, e, fmt="0.0%" if isinstance(e, float) and e < 1 else "0.00", bold=True)
        cell(ws, r, 7, f, align="left", size=9, color=MUTED)
    section(ws, 13, "二、估值结果", 8)
    header(ws, 14, ["方法", "每股价值", "权重", "", "方法", "每股价值", "说明", ""])
    res = [
        ("DCF", 41.64, 0.5, "PE", 39.19, "2027E EPS 1.96 × 20x"),
        ("综合基准", 40.42, 1.0, "现价", 34.82, "折价 13.8%"),
        ("悲观", 20.49, None, "乐观", 63.42, "综合三情景"),
        ("20% 边际价", 32.34, None, "A/H 溢价", 0.762, "A 股 vs H 股"),
    ]
    for i, (a, b, w, d, e, f) in enumerate(res):
        r = 15 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 2, b, fmt="0.0%" if a == "A/H 溢价" else "0.00", bold=True)
        if w is not None:
            cell(ws, r, 3, w, fmt="0%")
        else:
            cell(ws, r, 3, "—", align="center", color=MUTED)
        cell(ws, r, 5, d, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 6, e, fmt="0.00", bold=True)
        cell(ws, r, 7, f, align="left", size=9, color=MUTED)
    section(ws, 20, "三、DCF 敏感性（元/股）", 8)
    header(ws, 21, ["WACC \\ g", "2.50%", "2.75%", "3.00%", "3.25%", "3.50%", "", ""])
    sens = [
        ("9.00%", 38.9, 40.3, 41.8, 43.5, 45.3),
        ("9.25%", 37.3, 38.6, 40.0, 41.5, 43.1),
        ("9.50%", 35.9, 37.1, 38.4, 39.8, 41.3),
        ("9.75%", 34.5, 35.6, 36.8, 38.1, 39.5),
        ("10.00%", 33.2, 34.2, 35.3, 36.5, 37.8),
    ]
    for i, row in enumerate(sens):
        r = 22 + i
        cell(ws, r, 1, row[0], align="center", bold=True)
        for j, v in enumerate(row[1:], 2):
            cell(ws, r, j, v, fmt="0.0")
    block(ws, 28, 1, 31, 8,
          "读法：DCF 区间约 33–45 元；现价 34.82 位于下沿。若 WACC 9.0%、g 3.5%，价值 45.3；"
          "若 WACC 10%、g 2.5%，价值 33.2。现价不贵，但安全垫不厚。",
          size=9, color=MUTED, fill=NOTE_FILL, height=48)
    finish(ws, 8)
    ws.print_area = "A1:H31"


def sheet_financials(wb):
    ws = wb.create_sheet("财务")
    title(ws, "财务 · 2021–2026E", 9)
    subtitle(ws, "单位：人民币亿元；2026E 为本文估计，2026 9M 为实际", 9)
    widths = [20, 13, 13, 13, 13, 13, 13, 3, 3]
    for j, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(j)].width = w
    section(ws, 4, "一、损益与现金流", 9)
    header(ws, 5, ["指标", "2021", "2022", "2023", "2024", "2025", "2026E", "", ""])
    data = [
        ("营业收入", [44.32, 51.06, 43.25, 37.80, 61.74, 62.0], "#,##0.0"),
        ("归母净利", [5.77, 4.50, 4.25, 4.74, 11.03, 10.0], "#,##0.0"),
        ("经营现金流", [0.21, 1.12, 8.09, 10.83, 12.27, 25.0], "#,##0.0"),
        ("毛利率（%）", [None, None, None, None, 31.2, 33.0], "0.0"),
        ("ROE（%）", [21.35, 12.94, 6.32, 6.68, 14.0, 7.0], "0.0"),
    ]
    for i, (name, vals, fmt) in enumerate(data):
        r = 6 + i
        cell(ws, r, 1, name, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        for j, v in enumerate(vals):
            if v is None:
                cell(ws, r, 2 + j, "—", align="center", color=MUTED)
            else:
                cell(ws, r, 2 + j, v, fmt=fmt, bold=(name == "归母净利"))
    section(ws, 12, "二、2026 年三季报", 9)
    header(ws, 13, ["指标", "2026 9M", "同比", "2026Q3", "同比", "", "", "", ""])
    q3 = [
        ("营业收入", 43.63, "-5.05%", 11.11, "-36.68%"),
        ("归母净利", 7.10, "-19.97%", 1.10, "-67.85%"),
        ("毛利率", 35.6, "+4.5pct", 30.1, "—"),
        ("经营现金流", 20.43, "+35.39%", None, "—"),
        ("合同负债", 31.55, "+96.11%", None, "—"),
    ]
    for i, (a, b, c, d, e) in enumerate(q3):
        r = 14 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 2, b, fmt="0.0" if isinstance(b, float) else "#,##0.0", bold=True)
        cell(ws, r, 3, c, align="center")
        if d is None:
            cell(ws, r, 4, "—", align="center", color=MUTED)
        else:
            cell(ws, r, 4, d, fmt="0.0" if isinstance(d, float) else "#,##0.0", bold=True)
        cell(ws, r, 5, e, align="center")
    section(ws, 20, "三、资产负债表（2026-09-30）", 9)
    header(ws, 21, ["项目", "金额", "说明", "", "", "", "", "", ""])
    bs = [
        ("货币资金", 75.20, "H 股募资后大幅增加"),
        ("交易性金融资产", 17.03, "理财"),
        ("有息负债", 24.45, "长期借款 22.79 亿"),
        ("净现金", 50.75, "货币资金 − 有息负债"),
        ("总资产", 231.55, "+59.79%"),
        ("归母净资产", 146.05, "+76.39%"),
        ("在建工程", 27.69, "+77.23%"),
        ("固定资产", 43.98, "+40.43%"),
    ]
    for i, (a, b, c) in enumerate(bs):
        r = 22 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 2, b, fmt="#,##0.0", bold=True)
        block(ws, r, 3, r, 9, c, size=9, color=MUTED)
    block(ws, 31, 1, 34, 9,
          "判断：2026Q3 是交付节奏低点，不是需求崩塌；毛利率、经营现金流、合同负债都在改善。"
          "但在建工程/资本开支大，2027 年 FCF 仍可能承压。",
          size=9, color=MUTED, fill=NOTE_FILL, height=48)
    finish(ws, 9)
    ws.print_area = "A1:I34"


def sheet_orders(wb):
    ws = wb.create_sheet("订单与产能")
    title(ws, "订单、产能与海外布局", 8)
    subtitle(ws, "截至 2026-09-30 / 2026-11 公告；单位：人民币亿元", 8)
    widths = [24, 18, 14, 12, 12, 3, 3, 3]
    for j, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(j)].width = w
    section(ws, 4, "一、订单", 8)
    header(ws, 5, ["项目", "金额/数量", "说明", "", "", "", "", ""])
    orders = [
        ("海外海风在手订单", ">70 亿", "英国、德国、法国、波兰等；未来三年兑现"),
        ("造船在手订单", "约 120 亿", "24 艘，2027–2030 交付，2028 年高峰"),
        ("海外+造船合计", ">190 亿", "合同负债 31.55 亿，同比 +96%"),
        ("2025 年末海外订单", ">100 亿", "2025 年报披露"),
        ("2027 年船舶交付", "2 艘", "国信预计 2027/2028/2029 交付 2/7/14 艘"),
    ]
    for i, (a, b, c) in enumerate(orders):
        r = 6 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 2, b, align="center", bold=True)
        block(ws, r, 3, r, 8, c, size=9, color=MUTED)
    section(ws, 13, "二、产能与布局", 8)
    header(ws, 14, ["项目", "数值", "说明", "", "", "", "", ""])
    cap = [
        ("曹妃甸基地", "50 万吨", "2025-12 试生产，2026 投产；15–25MW 单桩/浮式基础"),
        ("蓬莱/阜新等基地", "—", "原有产能；具体以年报为准"),
        ("欧洲单桩份额", "29.1%", "2025H1 单桩销售金额口径，排名第一；2024 年 18.5%"),
        ("海外母港", "4 处", "丹麦、德国、西班牙等"),
        ("自有运输船", "3 艘 KING", "4 万吨级；8000 吨安装船设计签约"),
    ]
    for i, (a, b, c) in enumerate(cap):
        r = 15 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 2, b, align="center", bold=True)
        block(ws, r, 3, r, 8, c, size=9, color=MUTED)
    section(ws, 22, "三、2025 年收入结构", 8)
    header(ws, 23, ["业务", "收入", "同比", "占比", "毛利率", "", "", ""])
    seg = [
        ("风电装备", 58.7, "+66%", "95%", "29.1%"),
        ("新能源发电", 2.5, "+16.4%", "4%", "69.5%"),
        ("其他", 0.3, "—", "1%", "—"),
    ]
    for i, (a, b, c, d, e) in enumerate(seg):
        r = 24 + i
        cell(ws, r, 1, a, align="left", bold=True)
        cell(ws, r, 2, b, fmt="#,##0.0")
        cell(ws, r, 3, c, align="center")
        cell(ws, r, 4, d, align="center")
        cell(ws, r, 5, e, align="center")
    block(ws, 28, 1, 31, 8,
          "2025 年出口收入 45.97 亿（+165.26%），占 74.46%，出口毛利率 33.95%；2026H1 出口占比 82.25%、出口毛利率 39.36%。"
          "欧洲是核心市场，2025 年欧洲收入占比 68.8%。",
          size=9, color=MUTED, fill=NOTE_FILL, height=48)
    finish(ws, 8, freeze="A4")
    ws.print_area = "A1:H31"


def sheet_risk(wb):
    ws = wb.create_sheet("风险与跟踪")
    title(ws, "风险与跟踪", 8)
    subtitle(ws, "风险不是预测，而是需要持续验证的变量", 8)
    widths = [22, 46, 28, 10, 3, 3, 3, 3]
    for j, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(j)].width = w
    section(ws, 4, "一、主要风险", 8)
    header(ws, 5, ["风险", "机制", "监控指标", "等级", "", "", "", ""])
    risks = [
        ("欧洲订单空窗", "2026 年新签少，2027 年拍卖才修复", "新签订单、合同负债", "高"),
        ("欧洲本土产能", "2024–2027 年产能 120→270 万吨", "欧洲产能、项目延期", "中高"),
        ("贸易壁垒", "欧盟审查中国单桩/钢结构", "关税/反倾销", "中高"),
        ("汇率", "欧元贬值/汇兑损失", "欧元/人民币、财务费用", "中"),
        ("交付节奏", "船期、港口、验收", "季度发运吨数、收入", "高"),
        ("造船执行", "24 艘/120 亿订单", "交付艘数、毛利率", "中"),
        ("杠杆/capex", "在建工程 27.69 亿", "有息负债、FCF", "中"),
        ("A/H 溢价", "A 股比 H 股贵 76%", "A/H 价差、H 股回购", "中"),
    ]
    for i, (a, b, c, d) in enumerate(risks):
        r = 6 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 2, b, align="left", size=9)
        cell(ws, r, 3, c, align="left", size=9)
        cell(ws, r, 4, d, align="center", bold=True,
             color=(RED if d == "高" else (BROWN if d == "中高" else GOLD)))
    section(ws, 15, "二、监控触发条件", 8)
    header(ws, 16, ["指标", "当前", "触发阈值", "动作", "", "", "", ""])
    triggers = [
        ("2027Q1 欧洲新签订单", "待观察", "<20 亿", "下调 2027E 净利"),
        ("合同负债", "31.55 亿", "连续两季下降", "订单预警"),
        ("季度发运吨数", "Q3 3.2 万吨", "<2.5 万吨", "交付节奏恶化"),
        ("出口毛利率", "39.36%（H1）", "<32%", "价格/汇率/成本压力"),
        ("2027E 净利", "14.5 亿（本文）", "下修 >15%", "重估 PE"),
        ("造船交付", "2027 年 2 艘", "延期/亏损", "下调第二曲线"),
        ("A/H 溢价", "76%", ">90%", "A 股相对更贵"),
    ]
    for i, (a, b, c, d) in enumerate(triggers):
        r = 17 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 2, b, align="center")
        cell(ws, r, 3, c, align="center", color=RED)
        block(ws, r, 4, r, 8, d, size=9, color=MUTED)
    finish(ws, 8)
    ws.print_area = "A1:H23"


def sheet_sources(wb):
    ws = wb.create_sheet("来源")
    title(ws, "数据与来源", 8)
    subtitle(ws, "报告日 2026-11-05；财务截止 2026-09-30", 8)
    widths = [22, 80, 3, 3, 3, 3, 3, 3]
    for j, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(j)].width = w
    block(ws, 4, 1, 12, 2,
          "2025 年报：收入 61.74 亿、净利 11.03 亿、出口 45.97 亿（74.46%）、毛利率 31.2%、经营现金流 12.27 亿。\n"
          "2026 三季报：收入 43.63 亿（-5.05%）、净利 7.10 亿（-19.97%）、Q3 净利 1.10 亿（-67.85%）、毛利率 35.6%、经营现金流 20.43 亿、合同负债 31.55 亿。\n"
          "2026 半年报：收入 32.53 亿、净利 6.01 亿、出口毛利率 39.36%、出口占比 82.25%。\n"
          "订单/产能：海外海风 >70 亿、造船 24 艘/120 亿、曹妃甸 50 万吨、欧洲单桩份额 29.1%。\n"
          "券商：Citi 目标 34 港元（2027E PE 10.3x、PB 0.9x）；JPM 目标 43 港元；Citi 下调 2026–28 净利 23–29%。\n"
          "价格：A 股 34.82 元（2026-11-05）；H 股 23.08 港元（2026-11-05）。",
          size=9, color=INK, height=180)
    block(ws, 14, 1, 18, 2,
          "免责声明：本模型为研究记录，不构成投资建议。2026Q3 受交付节奏/汇率影响，2027E 依赖欧洲订单修复；"
          "估值对假设敏感，A/H 溢价可能变化，请独立判断。",
          size=9, color=MUTED, fill=NOTE_FILL, height=50)
    finish(ws, 8, freeze="A4")
    ws.print_area = "A1:H18"


def main():
    wb = Workbook()
    sheet_one(wb)
    sheet_valuation(wb)
    sheet_financials(wb)
    sheet_orders(wb)
    sheet_risk(wb)
    sheet_sources(wb)
    wb.save(OUT)
    print("saved", OUT.name)


if __name__ == "__main__":
    main()
