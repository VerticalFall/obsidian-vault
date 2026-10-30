# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import ColorScaleRule

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model_config import COMPANIES

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / "输出" / "A股"
DATE = "2026-10-30"

GREEN = "2F6B4F"; BROWN = "8C6D5A"; GOLD = "C9A227"; RED = "B23A2E"
INK = "1F2933"; MUTED = "5B6770"; BORDER = "D9D2C5"
TITLE_FILL = PatternFill("solid", fgColor=GREEN)
SECTION_FILL = PatternFill("solid", fgColor="E8EFE9")
HEADER_FILL = PatternFill("solid", fgColor="EFE8D8")
INPUT_FILL = PatternFill("solid", fgColor="F2F7FB")
NOTE_FILL = PatternFill("solid", fgColor="FBF7EA")
THIN = Side(style="thin", color=BORDER)
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
FONT_CN = "Microsoft YaHei"


def title(ws, text, ncols=8, row=1):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)
    c = ws.cell(row=row, column=1, value=text)
    c.font = Font(name=FONT_CN, size=14, bold=True, color="FFFFFF")
    c.fill = TITLE_FILL
    c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[row].height = 28


def subtitle(ws, text, ncols=8, row=2):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)
    c = ws.cell(row=row, column=1, value=text)
    c.font = Font(name=FONT_CN, size=9, color=MUTED)
    c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[row].height = 18


def section(ws, row, text, ncols=8):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)
    c = ws.cell(row=row, column=1, value=text)
    c.font = Font(name=FONT_CN, size=11, bold=True, color=GREEN)
    c.fill = SECTION_FILL
    c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[row].height = 22


def header(ws, row, values, widths=None):
    for j, v in enumerate(values, 1):
        c = ws.cell(row=row, column=j, value=v)
        c.font = Font(name=FONT_CN, size=9.5, bold=True, color="5B4A3A")
        c.fill = HEADER_FILL
        c.border = BORDER_ALL
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 28
    if widths:
        for j, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(j)].width = w


def cell(ws, row, col, value, fmt=None, bold=False, color=INK, fill=None, align="right", wrap=False, size=9.5):
    c = ws.cell(row=row, column=col, value=value)
    c.font = Font(name=FONT_CN, size=size, bold=bold, color=color)
    c.border = BORDER_ALL
    c.alignment = Alignment(horizontal=align, vertical="center", wrap_text=wrap)
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    return c


def input_cell(ws, row, col, value, fmt=None, align="right"):
    return cell(ws, row, col, value, fmt=fmt, color="1A73E8", fill=INPUT_FILL, align=align)


def note(ws, row, text, ncols=8):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)
    c = ws.cell(row=row, column=1, value=text)
    c.font = Font(name=FONT_CN, size=8.5, color=MUTED, italic=True)
    c.fill = NOTE_FILL
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
    ws.row_dimensions[row].height = 30


def finish(ws, ncols=8, freeze="A5"):
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = freeze
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_options.horizontalCentered = True
    ws.sheet_properties.tabColor = GREEN


def add_bar_chart(ws, data_row, cat_row, col_start=2, col_end=7, anchor="A23", title_text="归母净利润（亿元）"):
    chart = BarChart()
    chart.type = "col"
    chart.style = 10
    chart.title = title_text
    chart.y_axis.title = "亿元"
    data = Reference(ws, min_col=col_start, max_col=col_end, min_row=data_row, max_row=data_row)
    cats = Reference(ws, min_col=col_start, max_col=col_end, min_row=cat_row, max_row=cat_row)
    chart.add_data(data, from_rows=True, titles_from_data=False)
    chart.set_categories(cats)
    chart.height = 7.5
    chart.width = 13
    chart.legend = None
    chart.gapWidth = 55
    ws.add_chart(chart, anchor)


def sheet_conclusion(wb, c):
    ws = wb.active
    ws.title = "结论"
    title(ws, f"{c.name} {c.code} · 巴菲特框架估值模型", 7)
    subtitle(ws, f"报告日 {DATE}｜价格日 {DATE}｜单位：人民币亿元、元/股｜蓝色=输入，黑色=公式", 7)
    note(ws, 3, "本模型只用于研究记录，不构成投资建议。事实、计算、假设与判断分开标注；来源见“来源”页。", 7)
    section(ws, 5, "一、市场与估值结论", 7)
    header(ws, 6, ["指标", "数值", "单位 / 说明", "", "", "", ""], [26, 16, 40, 3, 3, 3, 3])
    rows = [
        ("收盘价", c.price, "元/股", "input", "0.00"),
        ("总股本", c.shares, "亿股", "input", "#,##0.00"),
        ("总市值", "=B7*B8", "亿元", "formula", "#,##0.00"),
        ("净债务", c.net_debt, "亿元", "input", "#,##0.00"),
        ("少数股东权益", c.minority, "亿元", "input", "#,##0.00"),
        ("2026E 归母净利", c.net_profit_2026e, "亿元", "input", "#,##0.0"),
        ("2026E EPS", "=B12/B8", "元/股", "formula", "0.000"),
        ("2026E DPS", c.dps_2026e, "元/股", "input", "0.000"),
        ("2026E 股息率", "=B14/B7", "%", "formula", "0.00%"),
        ("2026E PE", "=B7/B13", "倍", "formula", "0.0"),
        ("每股净资产 BPS", c.bps, "元/股", "input", "0.00"),
        ("PB", "=B7/B17", "倍", "formula", "0.00"),
        ("2026E ROE", c.roe_2026e / 100, "%", "input", "0.00%"),
    ]
    r = 7
    for label, val, unit, kind, fmt in rows:
        cell(ws, r, 1, label, align="left")
        if kind == "input":
            input_cell(ws, r, 2, val, fmt=fmt)
        else:
            cell(ws, r, 2, val, fmt=fmt, bold=True)
        cell(ws, r, 3, unit, align="left", color=MUTED)
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)
        r += 1
    cell(ws, r, 1, f"估值方法 1：{c.method1_name}", align="left")
    cell(ws, r, 2, c.method1_value, fmt="0.00", bold=True)
    cell(ws, r, 3, "元/股", align="left", color=MUTED)
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)
    r += 1
    cell(ws, r, 1, f"估值方法 2：{c.method2_name}", align="left")
    cell(ws, r, 2, c.method2_value, fmt="0.00", bold=True)
    cell(ws, r, 3, "元/股", align="left", color=MUTED)
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)
    r += 1
    if c.method3_value:
        cell(ws, r, 1, f"估值方法 3：{c.method3_name}", align="left")
        cell(ws, r, 2, c.method3_value, fmt="0.00", bold=True)
        cell(ws, r, 3, "元/股", align="left", color=MUTED)
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)
        r += 1
    if c.method3_value:
        formula = f"=B20*{c.method1_weight}+B21*{c.method2_weight}+B22*{c.method3_weight}"
    else:
        formula = f"=B20*{c.method1_weight}+B21*{c.method2_weight}"
    cell(ws, r, 1, "综合基准价值", align="left", bold=True)
    cell(ws, r, 2, formula, fmt="0.00", bold=True, color=GREEN)
    cell(ws, r, 3, "元/股", align="left", color=MUTED)
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)
    base_row = r
    r += 1
    cell(ws, r, 1, "安全边际", align="left", bold=True)
    cell(ws, r, 2, f"=1-B7/B{base_row}", fmt="0.0%", bold=True,
         color=GREEN if c.margin_of_safety > 0 else RED)
    cell(ws, r, 3, "正=折价，负=溢价", align="left", color=MUTED)
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)
    r += 1
    cell(ws, r, 1, "评级", align="left", bold=True)
    cell(ws, r, 2, c.rating, align="center", bold=True,
         color=GREEN if c.rating in ("便宜", "合理偏低") else (RED if c.rating == "昂贵" else GOLD))
    cell(ws, r, 3, "", align="left")
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)
    r += 1
    cell(ws, r, 1, "置信度", align="left")
    cell(ws, r, 2, c.confidence, align="center")
    cell(ws, r, 3, "", align="left")
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)
    r += 1
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
    cc = ws.cell(row=r, column=1, value="结论：" + c.conclusion)
    cc.font = Font(name=FONT_CN, size=10.5, bold=True, color=RED if c.margin_of_safety < -0.1 else INK)
    cc.fill = NOTE_FILL
    cc.border = BORDER_ALL
    cc.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
    ws.row_dimensions[r].height = 42
    r += 2
    section(ws, r, "二、关键假设", 7)
    r += 1
    header(ws, r, ["假设", "数值", "说明", "", "", "", ""], [26, 16, 40, 3, 3, 3, 3])
    r += 1
    if c.code == "600900.SH":
        assumptions = [
            ("归一化 FCFF", 430, "亿元；2025 CFO 605.6 − capex 184.9 + 利息/营运资金调整", "#,##0.0"),
            ("WACC", 0.060, "无风险 1.62% + 风险溢价；水电类低杠杆", "0.00%"),
            ("永续增长 g", 0.018, "电量与电价长期温和增长", "0.00%"),
            ("DPS（归一化）", 1.00, "2025 年分红 1.00 元；2026-2030 承诺 ≥70%", "0.000"),
            ("COE", 0.060, "DDM 折现率", "0.00%"),
            ("DDM 永续 g", 0.020, "股息长期增长", "0.00%"),
        ]
    elif c.code == "000001.SZ":
        assumptions = [
            ("BPS", 24.56, "2026Q3 归母净资产 / 总股本", "0.00"),
            ("可持续 ROE", 0.075, "2026E 8.8%，考虑 NIM 与信用成本后下调", "0.00%"),
            ("COE", 0.115, "Rf 1.62% + 银行股权风险溢价", "0.00%"),
            ("永续增长 g", 0.035, "与资本补充、分红率相匹配", "0.00%"),
            ("DPS（归一化）", 0.65, "2026E 分红率约 29%", "0.000"),
            ("DDM g", 0.035, "与 RI 的 g 一致", "0.00%"),
        ]
    else:
        assumptions = [
            ("归一化 FCFF", 620, "亿元；2026E CFO − capex，按中周期煤价调整", "#,##0.0"),
            ("WACC", 0.080, "周期资源股要求回报", "0.00%"),
            ("永续增长 g", 0.015, "煤价长期通胀，低于名义 GDP", "0.00%"),
            ("DPS（2026E）", 1.95, "分红率约 75%", "0.000"),
            ("COE", 0.080, "DDM 折现率", "0.00%"),
            ("DDM g", 0.020, "股息长期增长", "0.00%"),
            ("PE 中枢", 15.0, "周期股中周期合理 PE", "0.0"),
        ]
    for label, val, desc, fmt in assumptions:
        cell(ws, r, 1, label, align="left")
        input_cell(ws, r, 2, val, fmt=fmt)
        cell(ws, r, 3, desc, align="left", color=MUTED, wrap=True)
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)
        ws.row_dimensions[r].height = 24
        r += 1
    r += 1
    section(ws, r, "三、三情景", 7)
    r += 1
    header(ws, r, ["情景", "每股价值（元）", "相对现价", "核心假设", "", "", ""], [16, 16, 14, 46, 3, 3, 3])
    r += 1
    scen_desc = {
        "600900.SH": {"悲观": "来水偏枯、利率上行；FCFF 400 亿、WACC 6.5%",
                      "基准": "正常来水；FCFF 430 亿、WACC 6.0%、g 1.8%",
                      "乐观": "来水偏丰、电价改革；FCFF 470 亿、WACC 5.7%"},
        "000001.SZ": {"悲观": "ROE 6.5%、COE 12.0%；资产质量恶化",
                      "基准": "ROE 7.5%、COE 11.5%、g 3.5%",
                      "乐观": "ROE 8.5%、COE 11.0%；零售修复"},
        "601088.SH": {"悲观": "煤价回落；FCFF 520 亿、WACC 8.5%",
                      "基准": "中周期煤价；FCFF 620 亿、WACC 8.0%",
                      "乐观": "煤价高位、收购协同；FCFF 720 亿、WACC 7.5%"},
    }[c.code]
    for name in ["悲观", "基准", "乐观"]:
        val = c.scenario_values[name]
        cell(ws, r, 1, name, align="center", bold=(name == "基准"))
        cell(ws, r, 2, val, fmt="0.00", bold=(name == "基准"), color=GREEN if name == "基准" else INK)
        cell(ws, r, 3, f"=B{r}/B7-1", fmt="0.0%", bold=(name == "基准"), color=GREEN if val > c.price else RED)
        cell(ws, r, 4, scen_desc[name], align="left", wrap=True, color=MUTED)
        ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=7)
        ws.row_dimensions[r].height = 30
        r += 1
    r += 1
    section(ws, r, "四、结论边界", 7)
    r += 1
    notes = {
        "600900.SH": [
            "好生意：六库联调、边际成本近零、现金流可预测；但来水与利率是外生变量。",
            "估值不便宜：2026E PE 22.6 倍、股息率 3.1%，现价高于综合基准约 7.8%。",
            "若要求 20% 安全边际，对应价格约 22.1 元；现价不满足。",
        ],
        "000001.SZ": [
            "静态便宜：0.47 倍 PB、5.6% 前瞻股息率；但 ROE 8.8% 低于 COE 11.5%。",
            "低 PB 是结果，不是理由：市场在定价 ROE 下行与资产质量尾部风险。",
            "若要求 20% 安全边际，对应价格约 8.8 元；现价不满足。",
        ],
        "601088.SH": [
            "一体化煤炭龙头，长协煤与煤电运化对冲部分周期；但仍是周期股。",
            "现价 20 倍 PE，接近乐观情景；A/H 溢价显著，H 股股息率约 6.7%。",
            "若要求 20% 安全边际，对应价格约 29.3 元；现价不满足。",
        ],
    }[c.code]
    for t in notes:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
        cc = ws.cell(row=r, column=1, value="• " + t)
        cc.font = Font(name=FONT_CN, size=9, color=INK)
        cc.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
        ws.row_dimensions[r].height = 26
        r += 1
    finish(ws, 7, freeze="A7")


def sheet_history(wb, c):
    ws = wb.create_sheet("历史财务")
    title(ws, f"{c.name} · 2021–2025 财务与分红", 9)
    subtitle(ws, "单位：亿元、元/股、%；2026E 为模型估计；银行口径为营业收入/归母净利润", 9)
    note(ws, 3, "数据来源：公司年报/季报、东方财富 F10；ROE 2021–2023 为按平均归母权益计算，2024–2025 采用披露值。", 9)
    if c.code == "000001.SZ":
        header(ws, 5, ["指标", "2021", "2022", "2023", "2024", "2025", "2026E/最新", "", ""],
               [24, 12, 12, 12, 12, 12, 14, 3, 3])
        rows = [
            ("营业收入", c.revenue, "#,##0.0"),
            ("归母净利润", c.net_profit, "#,##0.0"),
            ("EPS（元）", c.eps, "0.000"),
            ("ROE（%）", c.roe, "0.00"),
            ("净息差（%）", [2.74, 2.75, 2.38, 1.87, 1.78], "0.00"),
            ("不良率（%）", [1.02, 1.05, 1.06, 1.06, 1.05], "0.00"),
            ("拨备覆盖率（%）", [288.42, 290.28, 261.14, 250.71, 220.88], "0.0"),
            ("核心一级资本（%）", [8.60, 8.64, 9.22, 10.69, 11.49], "0.00"),
            ("DPS（元）", c.dps, "0.000"),
            ("分红率（%）", c.payout, "0.0"),
        ]
        latest_map = {"营业收入": 1031.0, "归母净利润": 391.86, "EPS（元）": 1.94, "ROE（%）": 8.07,
                      "净息差（%）": 1.80, "不良率（%）": 1.05, "拨备覆盖率（%）": 214.75,
                      "核心一级资本（%）": 11.26, "DPS（元）": 0.249, "分红率（%）": None}
        for i, (label, vals, fmt) in enumerate(rows, 6):
            cell(ws, i, 1, label, align="left", bold=(label in ("归母净利润", "ROE（%）")))
            for j, v in enumerate(vals, 2):
                cell(ws, i, j, v, fmt=fmt)
            cell(ws, i, 7, latest_map[label] if latest_map[label] is not None else "—", fmt=fmt, color=GREEN, bold=True)
        r = 16
        section(ws, r, "2026E 关键假设", 9)
        r += 1
        header(ws, r, ["项目", "数值", "说明", "", "", "", "", "", ""], [24, 14, 62, 3, 3, 3, 3, 3, 3])
        r += 1
        for label, val, desc, fmt in [
            ("2026E 归母净利", 435, "9M 391.86 亿 + Q4 约 43 亿", "#,##0.0"),
            ("2026E EPS", 2.24, "归母净利 / 194.06 亿股", "0.00"),
            ("2026E DPS", 0.65, "分红率约 29%", "0.000"),
            ("2026E ROE", 8.8, "较 2025 年 9.15% 继续下行", "0.0"),
        ]:
            cell(ws, r, 1, label, align="left")
            input_cell(ws, r, 2, val, fmt=fmt)
            cell(ws, r, 3, desc, align="left", color=MUTED)
            ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=9)
            r += 1
        add_bar_chart(ws, 7, 5, 2, 7, anchor="A23", title_text="归母净利润（亿元）")
    else:
        header(ws, 5, ["指标", "2021", "2022", "2023", "2024", "2025", "2026E", "", ""],
               [24, 12, 12, 12, 12, 12, 12, 3, 3])
        rows = [
            ("营业收入", c.revenue, "#,##0.0"),
            ("归母净利润", c.net_profit, "#,##0.0"),
            ("EPS（元）", c.eps, "0.000"),
            ("ROE（%）", c.roe, "0.00"),
            ("毛利率（%）", c.gross_margin, "0.0"),
            ("净利率（%）", c.net_margin, "0.0"),
            ("资产负债率（%）", c.debt_ratio, "0.0"),
            ("DPS（元）", c.dps, "0.000"),
            ("分红率（%）", c.payout, "0.0"),
        ]
        if c.code == "600900.SH":
            latest_map = {"营业收入": 820.0, "归母净利润": 322.0, "EPS（元）": 1.316, "ROE（%）": 14.6,
                          "毛利率（%）": 58.0, "净利率（%）": 39.3, "资产负债率（%）": 58.0,
                          "DPS（元）": 0.92, "分红率（%）": 70.0}
        else:
            latest_map = {"营业收入": 3960.0, "归母净利润": 565.0, "EPS（元）": 2.60, "ROE（%）": 12.0,
                          "毛利率（%）": 35.0, "净利率（%）": 19.1, "资产负债率（%）": 40.8,
                          "DPS（元）": 1.95, "分红率（%）": 75.0}
        for i, (label, vals, fmt) in enumerate(rows, 6):
            cell(ws, i, 1, label, align="left", bold=(label in ("归母净利润", "ROE（%）")))
            for j, v in enumerate(vals, 2):
                cell(ws, i, j, v, fmt=fmt)
            cell(ws, i, 7, latest_map[label], fmt=fmt, color=GREEN, bold=True)
        r = 16
        section(ws, r, "2026E 关键假设", 9)
        r += 1
        header(ws, r, ["项目", "数值", "说明", "", "", "", "", "", ""], [24, 14, 62, 3, 3, 3, 3, 3, 3])
        r += 1
        if c.code == "600900.SH":
            items = [
                ("2026E 归母净利", 322, "H1 147.56 + Q3E 约 116 + Q4E 约 58", "#,##0.0"),
                ("2026E EPS", 1.316, "/ 244.68 亿股", "0.000"),
                ("2026E DPS", 0.92, "分红率 70%", "0.000"),
                ("2026E ROE", 14.6, "归母净利 / 平均归母权益", "0.0"),
            ]
        else:
            items = [
                ("2026E 归母净利", 565, "9M 444.03 + Q4E 约 121", "#,##0.0"),
                ("2026E EPS", 2.60, "/ 216.89 亿股", "0.00"),
                ("2026E DPS", 1.95, "分红率约 75%", "0.000"),
                ("2026E ROE", 12.0, "归母净利 / 平均归母权益", "0.0"),
            ]
        for label, val, desc, fmt in items:
            cell(ws, r, 1, label, align="left")
            input_cell(ws, r, 2, val, fmt=fmt)
            cell(ws, r, 3, desc, align="left", color=MUTED)
            ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=9)
            r += 1
        add_bar_chart(ws, 7, 5, 2, 7, anchor="A23", title_text="归母净利润（亿元）")
    finish(ws, 9, freeze="A6")


def sheet_segments(wb, c):
    ws = wb.create_sheet("分部")
    if c.code == "600900.SH":
        title(ws, "长江电力 · 运营指标与电站结构", 8)
        subtitle(ws, "2026Q3 单季发电量 923.14 亿 kWh，同比 -14.89%；前三季度 2,250.58 亿 kWh，同比 -4.28%", 8)
        header(ws, 4, ["电站", "2026Q3 发电量（亿 kWh）", "同比", "来水/调度要点", "", "", "", ""],
               [18, 22, 12, 62, 3, 3, 3, 3])
        data = [
            ("乌东德", 131.5210, "-10.46%", "乌东德水库来水 757.36 亿 m³，同比偏枯 9.29%"),
            ("白鹤滩", 194.2104, "-8.45%", "与乌东德联合调度，Q3 电量承压"),
            ("溪洛渡", 187.8558, "-3.18%", "相对稳定"),
            ("向家坝", 102.8065, "-5.97%", "相对稳定"),
            ("三峡", 253.1851, "-29.23%", "Q3 来水偏枯，电量降幅最大"),
            ("葛洲坝", 53.5618, "-17.04%", "跟随三峡来水"),
            ("合计", 923.1405, "-14.89%", "前三季度 2,250.58 亿 kWh，同比 -4.28%"),
        ]
        r = 5
        for name, val, yoy, desc in data:
            cell(ws, r, 1, name, align="left", bold=(name == "合计"))
            cell(ws, r, 2, val, fmt="#,##0.00", bold=(name == "合计"))
            cell(ws, r, 3, yoy, align="center", color=RED if yoy.startswith("-") else GREEN)
            cell(ws, r, 4, desc, align="left", wrap=True, color=MUTED)
            ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=8)
            ws.row_dimensions[r].height = 26
            r += 1
        r += 1
        section(ws, r, "经营杠杆", 8)
        r += 1
        header(ws, r, ["项目", "2025H1", "2026H1", "同比", "说明", "", "", ""],
               [18, 14, 14, 10, 56, 3, 3, 3])
        r += 1
        for row in [
            ("营业收入（亿元）", 366.98, 379.29, "+3.36%", "来水偏丰、电量增长"),
            ("归母净利（亿元）", 130.56, 147.56, "+13.02%", "财务费用下降、折旧到期"),
            ("财务费用（亿元）", 48.63, 42.01, "-13.61%", "存量债务成本下降"),
            ("经营现金流（亿元）", 239.9, 241.28, "+0.57%", "现金流稳定"),
            ("capex（亿元）", None, 44.35, "—", "维护性资本开支为主"),
        ]:
            cell(ws, r, 1, row[0], align="left")
            cell(ws, r, 2, row[1] if row[1] is not None else "—", fmt="#,##0.00")
            cell(ws, r, 3, row[2], fmt="#,##0.00")
            cell(ws, r, 4, row[3], align="center", color=GREEN if row[3].startswith("+") else RED)
            cell(ws, r, 5, row[4], align="left", color=MUTED)
            ws.merge_cells(start_row=r, start_column=5, end_row=r, end_column=8)
            r += 1
    elif c.code == "000001.SZ":
        title(ws, "平安银行 · 零售银行结构与资产质量", 8)
        subtitle(ws, "2026Q3 零售客户 1.3028 亿户、AUM 4.39 万亿；个人贷款 1.7225 万亿", 8)
        header(ws, 4, ["指标", "2025", "2026Q3", "同比/较上年末", "说明", "", "", ""],
               [26, 14, 14, 16, 50, 3, 3, 3])
        data = [
            ("零售客户数（万户）", None, 13028, "+1.9%", "零售客户基础"),
            ("零售 AUM（万亿）", None, 4.39, "+3.6%", "财富管理规模"),
            ("私行 AUM（万亿）", None, 2.10, "+5.2%", "高净值客户"),
            ("个人贷款（万亿）", None, 1.7225, "-0.3%", "主动压降高风险零售"),
            ("净息差（%）", 1.78, 1.80, "+1bp", "同比企稳"),
            ("不良率（%）", 1.05, 1.05, "持平", "总体稳定"),
            ("关注类占比（%）", None, 2.07, "+24bp", "需重点跟踪"),
            ("逾期率（%）", None, 1.59, "+10bp", "需重点跟踪"),
            ("拨备覆盖率（%）", 220.88, 214.75, "-6.13pct", "缓冲变薄"),
            ("核心一级资本（%）", 11.49, 11.26, "-0.23pct", "资本充足"),
        ]
        r = 5
        for row in data:
            cell(ws, r, 1, row[0], align="left")
            cell(ws, r, 2, row[1] if row[1] is not None else "—", fmt="#,##0.00")
            cell(ws, r, 3, row[2] if row[2] is not None else "—", fmt="#,##0.00")
            cell(ws, r, 4, row[3], align="center", color=RED if row[3].startswith("-") else GREEN)
            cell(ws, r, 5, row[4], align="left", color=MUTED)
            ws.merge_cells(start_row=r, start_column=5, end_row=r, end_column=8)
            r += 1
        r += 1
        section(ws, r, "零售资产质量拆分（2026Q3）", 8)
        r += 1
        header(ws, r, ["产品", "不良率", "环比", "说明", "", "", "", ""], [26, 12, 12, 56, 3, 3, 3, 3])
        r += 1
        for row in [("信用卡", 2.15, "-8bp", "仍处高位，但边际改善"), ("消费贷", 1.16, "-8bp", "压降高风险客群"),
                    ("按揭", 0.26, "—", "最优质资产"), ("经营贷", 1.17, "—", "需跟踪小微景气")]:
            cell(ws, r, 1, row[0], align="left")
            cell(ws, r, 2, row[1], fmt="0.00")
            cell(ws, r, 3, row[2], align="center")
            cell(ws, r, 4, row[3], align="left", color=MUTED)
            ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=8)
            r += 1
    else:
        title(ws, "中国神华 · 2026 年前三季度分部", 8)
        subtitle(ws, "煤电路港航化一体化；2026Q3 煤价 448 元/吨（+7.4%），自产煤毛利率 42.4%", 8)
        header(ws, 4, ["分部", "收入（亿元）", "毛利（亿元）", "毛利率", "同比", "说明", "", ""],
               [18, 16, 16, 12, 12, 52, 3, 3])
        data = [
            ("煤炭", None, 672.98, "42.4%（自产）", "+7.1%", "产量 3.82 亿吨（-2.3%），销量 4.61 亿吨（+0.1%）"),
            ("发电", None, None, "13.4%", "-4.9pct", "发电 2,175 亿 kWh（+2.3%），电价 370 元/MWh"),
            ("煤化工", 237.39, 66.83, "28.2%", "+450.9%", "收入 +50%，扭亏为盈"),
            ("运输/港口", None, None, "—", "—", "一体化配套，稳定器"),
        ]
        r = 5
        for row in data:
            cell(ws, r, 1, row[0], align="left")
            cell(ws, r, 2, row[1] if row[1] is not None else "—", fmt="#,##0.00")
            cell(ws, r, 3, row[2] if row[2] is not None else "—", fmt="#,##0.00")
            cell(ws, r, 4, row[3], align="center")
            cell(ws, r, 5, row[4], align="center", color=GREEN if row[4].startswith("+") else RED)
            cell(ws, r, 6, row[5], align="left", color=MUTED, wrap=True)
            ws.merge_cells(start_row=r, start_column=6, end_row=r, end_column=8)
            ws.row_dimensions[r].height = 28
            r += 1
        r += 1
        section(ws, r, "运营数据", 8)
        r += 1
        header(ws, r, ["指标", "2026 9M", "同比", "说明", "", "", "", ""], [24, 16, 12, 56, 3, 3, 3, 3])
        r += 1
        for row in [("商品煤产量（亿吨）", 3.82, "-2.3%", "核定产能约束"), ("商品煤销量（亿吨）", 4.61, "+0.1%", "外购煤增加"),
                    ("自产煤销量（亿吨）", 3.76, "-3.1%", ""), ("自产煤售价（元/吨）", 448, "+7.4%", "长协价 717 元/吨"),
                    ("自产煤单位成本（元/吨）", 157.5, "-3.9%", "成本控制良好"), ("发电量（亿 kWh）", 2175, "+2.3%", "装机 7,208 万千瓦"),
                    ("上网电价（元/MWh）", 370, "+0.5%", ""), ("电力成本（元/MWh）", 337.5, "+8.1%", "煤价上行挤压")]:
            cell(ws, r, 1, row[0], align="left")
            cell(ws, r, 2, row[1], fmt="#,##0.00")
            cell(ws, r, 3, row[2], align="center", color=GREEN if row[2].startswith("+") else RED)
            cell(ws, r, 4, row[3], align="left", color=MUTED)
            ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=8)
            r += 1
    finish(ws, 8, freeze="A5")


def sheet_valuation(wb, c):
    if c.code == "600900.SH":
        ws = wb.create_sheet("DCF")
        title(ws, "长江电力 · FCFF DCF 与 DDM 交叉", 8)
        subtitle(ws, "FCFF = EBIT×(1−t)+D&A−capex−ΔWC；股权价值 = EV − 净债务 − 少数股东权益", 8)
        section(ws, 4, "A. FCFF DCF", 8)
        header(ws, 5, ["项目", "数值", "单位", "公式/说明", "", "", "", ""], [30, 16, 12, 60, 3, 3, 3, 3])
        rows = [("归一化 FCFF", 430, "亿元", "输入", True, "#,##0.0"),
                ("WACC", 0.060, "%", "输入", True, "0.00%"),
                ("永续增长 g", 0.018, "%", "输入", True, "0.00%"),
                ("企业价值 EV", "=B6/(B7-B8)", "亿元", "FCFF/(WACC−g)", False, "#,##0.0"),
                ("减：净债务", 2734.9, "亿元", "输入", True, "#,##0.0"),
                ("减：少数股东权益", 119.8, "亿元", "输入", True, "#,##0.0"),
                ("股权价值", "=B9-B10-B11", "亿元", "EV−净债务−少数", False, "#,##0.0"),
                ("总股本", 244.68217716, "亿股", "输入", True, "#,##0.00"),
                ("每股价值", "=B12/B13", "元/股", "股权价值/股本", False, "0.00")]
        r = 6
        for label, val, unit, desc, is_input, fmt in rows:
            cell(ws, r, 1, label, align="left")
            if is_input:
                input_cell(ws, r, 2, val, fmt=fmt)
            else:
                cell(ws, r, 2, val, fmt=fmt, bold=True)
            cell(ws, r, 3, unit, align="center", color=MUTED)
            cell(ws, r, 4, desc, align="left", color=MUTED)
            ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=8)
            r += 1
        r += 1
        section(ws, r, "B. DDM", 8)
        r += 1
        header(ws, r, ["项目", "数值", "单位", "公式/说明", "", "", "", ""], [30, 16, 12, 60, 3, 3, 3, 3])
        r += 1
        start = r
        cell(ws, start, 1, "归一化 DPS", align="left")
        input_cell(ws, start, 2, 1.00, fmt="0.000")
        cell(ws, start, 3, "元/股", align="center", color=MUTED)
        cell(ws, start, 4, "2025 年分红 1.00 元；2026-2030 承诺 ≥70%", align="left", color=MUTED)
        ws.merge_cells(start_row=start, start_column=4, end_row=start, end_column=8)
        cell(ws, start + 1, 1, "COE", align="left")
        input_cell(ws, start + 1, 2, 0.060, fmt="0.00%")
        cell(ws, start + 1, 3, "%", align="center", color=MUTED)
        cell(ws, start + 1, 4, "股权成本", align="left", color=MUTED)
        ws.merge_cells(start_row=start + 1, start_column=4, end_row=start + 1, end_column=8)
        cell(ws, start + 2, 1, "永续增长 g", align="left")
        input_cell(ws, start + 2, 2, 0.020, fmt="0.00%")
        cell(ws, start + 2, 3, "%", align="center", color=MUTED)
        cell(ws, start + 2, 4, "股息长期增长", align="left", color=MUTED)
        ws.merge_cells(start_row=start + 2, start_column=4, end_row=start + 2, end_column=8)
        cell(ws, start + 3, 1, "DDM 每股价值", align="left")
        cell(ws, start + 3, 2, f"=B{start}/(B{start + 1}-B{start + 2})", fmt="0.00", bold=True, color=GREEN)
        cell(ws, start + 3, 3, "元/股", align="center", color=MUTED)
        cell(ws, start + 3, 4, "DPS/(COE−g)", align="left", color=MUTED)
        ws.merge_cells(start_row=start + 3, start_column=4, end_row=start + 3, end_column=8)
        r = start + 5
        section(ws, r, "C. 反向 DCF", 8)
        r += 1
        header(ws, r, ["项目", "数值", "单位", "说明", "", "", "", ""], [30, 16, 12, 60, 3, 3, 3, 3])
        r += 1
        ev_row = r
        cell(ws, ev_row, 1, "现价隐含 EV", align="left")
        cell(ws, ev_row, 2, "=29.74*244.68217716+2734.9+119.8", fmt="#,##0.0", bold=True)
        cell(ws, ev_row, 3, "亿元", align="center", color=MUTED)
        cell(ws, ev_row, 4, "市值+净债务+少数股东权益", align="left", color=MUTED)
        ws.merge_cells(start_row=ev_row, start_column=4, end_row=ev_row, end_column=8)
        cell(ws, ev_row + 1, 1, "隐含永续 g（WACC 6.0%）", align="left")
        cell(ws, ev_row + 1, 2, f"=0.06-B6/B{ev_row}", fmt="0.00%", bold=True)
        cell(ws, ev_row + 1, 3, "%", align="center", color=MUTED)
        cell(ws, ev_row + 1, 4, "WACC − FCF/EV", align="left", color=MUTED)
        ws.merge_cells(start_row=ev_row + 1, start_column=4, end_row=ev_row + 1, end_column=8)
        cell(ws, ev_row + 2, 1, "隐含 WACC（g 1.8%）", align="left")
        cell(ws, ev_row + 2, 2, f"=0.018+B6/B{ev_row}", fmt="0.00%", bold=True)
        cell(ws, ev_row + 2, 3, "%", align="center", color=MUTED)
        cell(ws, ev_row + 2, 4, "g + FCF/EV", align="left", color=MUTED)
        ws.merge_cells(start_row=ev_row + 2, start_column=4, end_row=ev_row + 2, end_column=8)
        finish(ws, 8, freeze="A6")
    elif c.code == "000001.SZ":
        ws = wb.create_sheet("RI")
        title(ws, "平安银行 · 剩余收益（RI）与 PB-ROE", 8)
        subtitle(ws, "RI = BPS + (ROE − COE) × BPS / (COE − g)；Justified PB = (ROE − g)/(COE − g)", 8)
        section(ws, 4, "A. 剩余收益", 8)
        header(ws, 5, ["项目", "数值", "单位", "公式/说明", "", "", "", ""], [30, 16, 12, 60, 3, 3, 3, 3])
        rows = [("BPS", 24.56, "元/股", "2026Q3", True, "0.00"),
                ("可持续 ROE", 0.075, "%", "输入", True, "0.00%"),
                ("COE", 0.115, "%", "输入", True, "0.00%"),
                ("永续增长 g", 0.035, "%", "输入", True, "0.00%"),
                ("RI 每股价值", "=B6+(B7-B8)*B6/(B8-B9)", "元/股", "BPS+(ROE−COE)×BPS/(COE−g)", False, "0.00")]
        r = 6
        for label, val, unit, desc, is_input, fmt in rows:
            cell(ws, r, 1, label, align="left")
            if is_input:
                input_cell(ws, r, 2, val, fmt=fmt)
            else:
                cell(ws, r, 2, val, fmt=fmt, bold=True, color=GREEN)
            cell(ws, r, 3, unit, align="center", color=MUTED)
            cell(ws, r, 4, desc, align="left", color=MUTED)
            ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=8)
            r += 1
        r += 1
        section(ws, r, "B. PB-ROE 交叉", 8)
        r += 1
        header(ws, r, ["项目", "数值", "单位", "说明", "", "", "", ""], [30, 16, 12, 60, 3, 3, 3, 3])
        r += 1
        just_row = r
        cell(ws, just_row, 1, "Justified PB", align="left")
        cell(ws, just_row, 2, "=(B7-B9)/(B8-B9)", fmt="0.00", bold=True)
        cell(ws, just_row, 3, "倍", align="center", color=MUTED)
        cell(ws, just_row, 4, "(ROE−g)/(COE−g)", align="left", color=MUTED)
        ws.merge_cells(start_row=just_row, start_column=4, end_row=just_row, end_column=8)
        cell(ws, just_row + 1, 1, "PB 估值", align="left")
        cell(ws, just_row + 1, 2, f"=B6*B{just_row}", fmt="0.00", bold=True, color=GREEN)
        cell(ws, just_row + 1, 3, "元/股", align="center", color=MUTED)
        cell(ws, just_row + 1, 4, "BPS×Justified PB", align="left", color=MUTED)
        ws.merge_cells(start_row=just_row + 1, start_column=4, end_row=just_row + 1, end_column=8)
        cell(ws, just_row + 2, 1, "现价隐含 ROE", align="left")
        cell(ws, just_row + 2, 2, "=0.474*(B8-B9)+B9", fmt="0.00%", bold=True)
        cell(ws, just_row + 2, 3, "%", align="center", color=MUTED)
        cell(ws, just_row + 2, 4, "PB×(COE−g)+g", align="left", color=MUTED)
        ws.merge_cells(start_row=just_row + 2, start_column=4, end_row=just_row + 2, end_column=8)
        r = just_row + 4
        section(ws, r, "C. DDM 交叉", 8)
        r += 1
        header(ws, r, ["项目", "数值", "单位", "说明", "", "", "", ""], [30, 16, 12, 60, 3, 3, 3, 3])
        r += 1
        start = r
        cell(ws, start, 1, "归一化 DPS", align="left")
        input_cell(ws, start, 2, 0.65, fmt="0.000")
        cell(ws, start, 3, "元/股", align="center", color=MUTED)
        cell(ws, start, 4, "2026E 分红率约 29%", align="left", color=MUTED)
        ws.merge_cells(start_row=start, start_column=4, end_row=start, end_column=8)
        cell(ws, start + 1, 1, "COE", align="left")
        input_cell(ws, start + 1, 2, 0.115, fmt="0.00%")
        cell(ws, start + 1, 3, "%", align="center", color=MUTED)
        cell(ws, start + 1, 4, "与 RI 一致", align="left", color=MUTED)
        ws.merge_cells(start_row=start + 1, start_column=4, end_row=start + 1, end_column=8)
        cell(ws, start + 2, 1, "DDM g", align="left")
        input_cell(ws, start + 2, 2, 0.035, fmt="0.00%")
        cell(ws, start + 2, 3, "%", align="center", color=MUTED)
        cell(ws, start + 2, 4, "与 RI 一致", align="left", color=MUTED)
        ws.merge_cells(start_row=start + 2, start_column=4, end_row=start + 2, end_column=8)
        cell(ws, start + 3, 1, "DDM 每股价值", align="left")
        cell(ws, start + 3, 2, f"=B{start}/(B{start + 1}-B{start + 2})", fmt="0.00", bold=True, color=GREEN)
        cell(ws, start + 3, 3, "元/股", align="center", color=MUTED)
        cell(ws, start + 3, 4, "DPS/(COE−g)", align="left", color=MUTED)
        ws.merge_cells(start_row=start + 3, start_column=4, end_row=start + 3, end_column=8)
        finish(ws, 8, freeze="A6")
    else:
        ws = wb.create_sheet("DCF")
        title(ws, "中国神华 · FCFF DCF、DDM 与 PE 交叉", 8)
        subtitle(ws, "周期资源股：以中周期 FCF 为主，避免用峰值利润×低 PE；EV 扣除净债务与少数股东权益", 8)
        section(ws, 4, "A. FCFF DCF", 8)
        header(ws, 5, ["项目", "数值", "单位", "公式/说明", "", "", "", ""], [30, 16, 12, 60, 3, 3, 3, 3])
        rows = [("归一化 FCFF", 620, "亿元", "输入", True, "#,##0.0"),
                ("WACC", 0.080, "%", "输入", True, "0.00%"),
                ("永续增长 g", 0.015, "%", "输入", True, "0.00%"),
                ("企业价值 EV", "=B6/(B7-B8)", "亿元", "FCFF/(WACC−g)", False, "#,##0.0"),
                ("减：净债务", 285.9, "亿元", "输入", True, "#,##0.0"),
                ("减：少数股东权益", 969.25, "亿元", "输入", True, "#,##0.0"),
                ("股权价值", "=B9-B10-B11", "亿元", "EV−净债务−少数", False, "#,##0.0"),
                ("总股本", 216.89434304, "亿股", "输入", True, "#,##0.00"),
                ("每股价值", "=B12/B13", "元/股", "股权价值/股本", False, "0.00")]
        r = 6
        for label, val, unit, desc, is_input, fmt in rows:
            cell(ws, r, 1, label, align="left")
            if is_input:
                input_cell(ws, r, 2, val, fmt=fmt)
            else:
                cell(ws, r, 2, val, fmt=fmt, bold=True)
            cell(ws, r, 3, unit, align="center", color=MUTED)
            cell(ws, r, 4, desc, align="left", color=MUTED)
            ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=8)
            r += 1
        r += 1
        section(ws, r, "B. DDM 与 PE", 8)
        r += 1
        header(ws, r, ["项目", "数值", "单位", "说明", "", "", "", ""], [30, 16, 12, 60, 3, 3, 3, 3])
        r += 1
        start = r
        cell(ws, start, 1, "2026E DPS", align="left")
        input_cell(ws, start, 2, 1.95, fmt="0.000")
        cell(ws, start, 3, "元/股", align="center", color=MUTED)
        cell(ws, start, 4, "分红率约 75%", align="left", color=MUTED)
        ws.merge_cells(start_row=start, start_column=4, end_row=start, end_column=8)
        cell(ws, start + 1, 1, "COE", align="left")
        input_cell(ws, start + 1, 2, 0.080, fmt="0.00%")
        cell(ws, start + 1, 3, "%", align="center", color=MUTED)
        cell(ws, start + 1, 4, "与 WACC 一致", align="left", color=MUTED)
        ws.merge_cells(start_row=start + 1, start_column=4, end_row=start + 1, end_column=8)
        cell(ws, start + 2, 1, "DDM g", align="left")
        input_cell(ws, start + 2, 2, 0.020, fmt="0.00%")
        cell(ws, start + 2, 3, "%", align="center", color=MUTED)
        cell(ws, start + 2, 4, "股息长期增长", align="left", color=MUTED)
        ws.merge_cells(start_row=start + 2, start_column=4, end_row=start + 2, end_column=8)
        cell(ws, start + 3, 1, "DDM 每股价值", align="left")
        cell(ws, start + 3, 2, f"=B{start}/(B{start + 1}-B{start + 2})", fmt="0.00", bold=True, color=GREEN)
        cell(ws, start + 3, 3, "元/股", align="center", color=MUTED)
        cell(ws, start + 3, 4, "DPS/(COE−g)", align="left", color=MUTED)
        ws.merge_cells(start_row=start + 3, start_column=4, end_row=start + 3, end_column=8)
        cell(ws, start + 4, 1, "2026E EPS", align="left")
        input_cell(ws, start + 4, 2, 2.60, fmt="0.00")
        cell(ws, start + 4, 3, "元/股", align="center", color=MUTED)
        cell(ws, start + 4, 4, "归母净利/股本", align="left", color=MUTED)
        ws.merge_cells(start_row=start + 4, start_column=4, end_row=start + 4, end_column=8)
        cell(ws, start + 5, 1, "中周期 PE", align="left")
        input_cell(ws, start + 5, 2, 15.0, fmt="0.0")
        cell(ws, start + 5, 3, "倍", align="center", color=MUTED)
        cell(ws, start + 5, 4, "周期股合理中枢", align="left", color=MUTED)
        ws.merge_cells(start_row=start + 5, start_column=4, end_row=start + 5, end_column=8)
        cell(ws, start + 6, 1, "PE 每股价值", align="left")
        cell(ws, start + 6, 2, f"=B{start + 4}*B{start + 5}", fmt="0.00", bold=True, color=GREEN)
        cell(ws, start + 6, 3, "元/股", align="center", color=MUTED)
        cell(ws, start + 6, 4, "EPS×PE", align="left", color=MUTED)
        ws.merge_cells(start_row=start + 6, start_column=4, end_row=start + 6, end_column=8)
        r = start + 8
        section(ws, r, "C. 反向 DCF", 8)
        r += 1
        header(ws, r, ["项目", "数值", "单位", "说明", "", "", "", ""], [30, 16, 12, 60, 3, 3, 3, 3])
        r += 1
        ev_row = r
        cell(ws, ev_row, 1, "现价隐含 EV", align="left")
        cell(ws, ev_row, 2, "=51.99*216.89434304+285.9+969.25", fmt="#,##0.0", bold=True)
        cell(ws, ev_row, 3, "亿元", align="center", color=MUTED)
        cell(ws, ev_row, 4, "市值+净债务+少数股东权益", align="left", color=MUTED)
        ws.merge_cells(start_row=ev_row, start_column=4, end_row=ev_row, end_column=8)
        cell(ws, ev_row + 1, 1, "隐含永续 g（WACC 8.0%）", align="left")
        cell(ws, ev_row + 1, 2, f"=0.08-B6/B{ev_row}", fmt="0.00%", bold=True)
        cell(ws, ev_row + 1, 3, "%", align="center", color=MUTED)
        cell(ws, ev_row + 1, 4, "WACC − FCF/EV", align="left", color=MUTED)
        ws.merge_cells(start_row=ev_row + 1, start_column=4, end_row=ev_row + 1, end_column=8)
        cell(ws, ev_row + 2, 1, "隐含 WACC（g 1.5%）", align="left")
        cell(ws, ev_row + 2, 2, f"=0.015+B6/B{ev_row}", fmt="0.00%", bold=True)
        cell(ws, ev_row + 2, 3, "%", align="center", color=MUTED)
        cell(ws, ev_row + 2, 4, "g + FCF/EV", align="left", color=MUTED)
        ws.merge_cells(start_row=ev_row + 2, start_column=4, end_row=ev_row + 2, end_column=8)
        finish(ws, 8, freeze="A6")


def sheet_sensitivity(wb, c):
    ws = wb.create_sheet("敏感性")
    if c.code == "600900.SH":
        title(ws, "长江电力 · DCF 敏感性：WACC × 永续 g", 8)
        subtitle(ws, "单元格为每股价值（元/股）；现价 29.74 元；绿色=高于现价，红色=低于现价", 8)
        waccs = [0.054, 0.056, 0.058, 0.060, 0.062, 0.064, 0.066]
        gs = [0.012, 0.015, 0.018, 0.021, 0.024]
        header(ws, 4, ["WACC \\ g"] + [f"{g * 100:.1f}%" for g in gs] + ["", ""], [14] + [12] * 5 + [3, 3])
        for i, w in enumerate(waccs, 5):
            cell(ws, i, 1, f"{w * 100:.1f}%", align="center", bold=True)
            for j, g in enumerate(gs, 2):
                ev = 430 / (w - g)
                eq = ev - 2734.9 - 119.8
                v = eq / 244.68217716
                cell(ws, i, j, round(v, 2), fmt="0.00", color=GREEN if v > 29.74 else RED)
        ws.conditional_formatting.add("B5:F11", ColorScaleRule(start_type="min", start_color="F8D7DA",
                                                                mid_type="percentile", mid_value=50,
                                                                mid_color="FFF3CD", end_type="max",
                                                                end_color="D4EDDA"))
        note(ws, 13, "计算：EV=FCF/(WACC−g)；股权=EV−净债务−少数股东权益；每股=股权/244.68 亿股。", 8)
    elif c.code == "000001.SZ":
        title(ws, "平安银行 · RI 敏感性：COE × 可持续 ROE", 8)
        subtitle(ws, "单元格为每股价值（元/股）；BPS 24.56 元、g 3.5%；现价 11.64 元", 8)
        coes = [0.105, 0.1075, 0.110, 0.1125, 0.115, 0.1175, 0.120]
        roes = [0.065, 0.070, 0.075, 0.080, 0.085]
        header(ws, 4, ["COE \\ ROE"] + [f"{r * 100:.1f}%" for r in roes] + ["", ""], [14] + [12] * 5 + [3, 3])
        for i, coe in enumerate(coes, 5):
            cell(ws, i, 1, f"{coe * 100:.2f}%", align="center", bold=True)
            for j, roe in enumerate(roes, 2):
                v = 24.56 + (roe - coe) * 24.56 / (coe - 0.035)
                cell(ws, i, j, round(v, 2), fmt="0.00", color=GREEN if v > 11.64 else RED)
        ws.conditional_formatting.add("B5:F11", ColorScaleRule(start_type="min", start_color="F8D7DA",
                                                                mid_type="percentile", mid_value=50,
                                                                mid_color="FFF3CD", end_type="max",
                                                                end_color="D4EDDA"))
        note(ws, 13, "计算：RI=BPS+(ROE−COE)×BPS/(COE−g)。ROE 低于 COE 时，价值低于账面。", 8)
    else:
        title(ws, "中国神华 · DCF 敏感性：WACC × 归一化 FCFF", 8)
        subtitle(ws, "单元格为每股价值（元/股）；净债务 285.9 亿、少数股东 969.25 亿；现价 51.99 元", 8)
        waccs = [0.070, 0.0725, 0.075, 0.0775, 0.080, 0.0825, 0.085]
        fcfs = [520, 560, 600, 620, 660, 700, 720]
        header(ws, 4, ["WACC \\ FCF"] + [f"{f}" for f in fcfs] + ["", ""], [14] + [10] * 7 + [3])
        for i, w in enumerate(waccs, 5):
            cell(ws, i, 1, f"{w * 100:.2f}%", align="center", bold=True)
            for j, fcf in enumerate(fcfs, 2):
                ev = fcf / (w - 0.015)
                eq = ev - 285.9 - 969.25
                v = eq / 216.89434304
                cell(ws, i, j, round(v, 2), fmt="0.00", color=GREEN if v > 51.99 else RED)
        ws.conditional_formatting.add("B5:H11", ColorScaleRule(start_type="min", start_color="F8D7DA",
                                                                mid_type="percentile", mid_value=50,
                                                                mid_color="FFF3CD", end_type="max",
                                                                end_color="D4EDDA"))
        note(ws, 13, "计算：EV=FCF/(WACC−1.5%)；股权=EV−净债务−少数股东权益；每股=股权/216.89 亿股。", 8)
    finish(ws, 10, freeze="B5")


def sheet_scenarios(wb, c):
    ws = wb.create_sheet("情景")
    title(ws, f"{c.name} · 三情景假设与结果", 8)
    subtitle(ws, "悲观/基准/乐观不是预测，而是用于界定估值区间；所有情景均使用同一套会计口径", 8)
    header(ws, 4, ["假设/结果", "悲观", "基准", "乐观", "说明", "", "", ""], [26, 14, 14, 14, 56, 3, 3, 3])
    if c.code == "600900.SH":
        rows = [
            ("归一化 FCFF（亿元）", "400", "430", "470", "来水与电价正常化"),
            ("WACC", "6.5%", "6.0%", "5.7%", "利率与风险溢价"),
            ("永续 g", "1.5%", "1.8%", "2.0%", "长期电量/电价"),
            ("DCF 每股（元）", "21.85", "30.17", "40.48", "FCFF/(WACC−g)"),
            ("DPS（元）", "0.88", "1.00", "1.08", "分红率 70%"),
            ("COE", "6.5%", "6.0%", "5.7%", ""),
            ("DDM g", "1.5%", "2.0%", "2.2%", ""),
            ("DDM 每股（元）", "17.60", "25.00", "30.86", "DPS/(COE−g)"),
            ("综合每股（元）", "19.73", "27.59", "35.67", "50/50 加权"),
            ("相对现价", "-33.7%", "-7.2%", "+20.0%", "现价 29.74"),
        ]
    elif c.code == "000001.SZ":
        rows = [
            ("可持续 ROE", "6.5%", "7.5%", "8.5%", "NIM/信用成本/零售修复"),
            ("COE", "12.0%", "11.5%", "11.0%", "股权风险溢价"),
            ("永续 g", "3.0%", "3.5%", "4.0%", "资本补充与分红"),
            ("RI 每股（元）", "9.55", "12.28", "15.79", "BPS 24.56"),
            ("DPS（元）", "0.55", "0.65", "1.00", "分红率提升情景"),
            ("DDM g", "3.0%", "3.5%", "4.0%", ""),
            ("DDM 每股（元）", "6.11", "8.13", "14.29", "DPS/(COE−g)"),
            ("综合每股（元）", "8.52", "11.03", "15.34", "70/30 加权"),
            ("相对现价", "-26.8%", "-5.2%", "+31.8%", "现价 11.64"),
        ]
    else:
        rows = [
            ("归一化 FCFF（亿元）", "520", "620", "720", "中周期煤价与收购协同"),
            ("WACC", "8.5%", "8.0%", "7.5%", "周期股要求回报"),
            ("永续 g", "1.0%", "1.5%", "2.0%", "长期通胀"),
            ("DCF 每股（元）", "26.18", "38.19", "54.57", "FCFF/(WACC−g)"),
            ("DPS（元）", "1.70", "1.95", "2.20", "分红率 65–75%"),
            ("COE", "8.5%", "8.0%", "7.5%", ""),
            ("DDM g", "1.5%", "2.0%", "2.0%", ""),
            ("DDM 每股（元）", "24.29", "32.50", "40.00", "DPS/(COE−g)"),
            ("PE（倍）", "11.0", "15.0", "18.0", "中周期"),
            ("PE 每股（元）", "25.85", "39.00", "54.00", "EPS 2.35/2.60/3.00"),
            ("综合每股（元）", "25.55", "36.64", "50.09", "50/30/20 加权"),
            ("相对现价", "-50.9%", "-29.5%", "-3.7%", "现价 51.99"),
        ]
    r = 5
    for row in rows:
        cell(ws, r, 1, row[0], align="left", bold=("综合" in row[0]))
        for j, v in enumerate(row[1:4], 2):
            cell(ws, r, j, v, align="center", bold=("综合" in row[0]),
                 color=GREEN if ("综合" in row[0] and j == 3) else INK)
        cell(ws, r, 5, row[4], align="left", color=MUTED)
        ws.merge_cells(start_row=r, start_column=5, end_row=r, end_column=8)
        r += 1
    finish(ws, 8, freeze="A5")


def sheet_sources(wb, c):
    ws = wb.create_sheet("来源")
    title(ws, f"{c.name} · 数据与来源", 8)
    subtitle(ws, "价格日 2026-10-30；财务数据以公司披露为准；第三方数据仅用于交叉核对", 8)
    header(ws, 4, ["类别", "来源", "日期", "用途/备注", "链接", "", "", ""], [16, 30, 12, 50, 60, 3, 3, 3])
    if c.code == "600900.SH":
        rows = [
            ("行情", "腾讯证券 / 东方财富", "2026-10-30", "收盘价 29.74 元、市值 7,276.85 亿、PE 20.10、PB 3.37", "https://qt.gtimg.cn/q=sh600900"),
            ("2026 半年报", "长江电力 2026 年半年度报告", "2026-08-30", "营收 379.29 亿、归母净利 147.56 亿、CFO 241.28 亿", "https://www.cnstock.com/commonDetail/783474"),
            ("2026 Q3 发电量", "长江电力 2026 年三季度发电量公告", "2026-10-12", "前三季度 2,250.58 亿 kWh（-4.28%）、Q3 923.14 亿 kWh（-14.89%）", "https://www.cnfin.com/announ/detail/index.html?id=845134363539&code=600900&dannoun=lcdetail&announ=lc"),
            ("2025 年报", "长江电力 2025 年年度报告", "2026-04", "营收 862.42 亿、归母净利 345.03 亿、DPS 1.00 元", "https://www.sse.com.cn/"),
            ("分红政策", "2026–2030 年股东分红回报规划", "2026", "每年现金分红不低于当年归母净利 70%", "https://www.sse.com.cn/"),
            ("财务数据", "东方财富 F10", "2026-10-30", "历史报表、分红、估值指标", "https://emweb.securities.eastmoney.com/"),
            ("无风险利率", "中国 10 年期国债", "2026-10-29", "1.6233%", "https://datacenter-web.eastmoney.com/"),
        ]
    elif c.code == "000001.SZ":
        rows = [
            ("行情", "腾讯证券 / 东方财富", "2026-10-30", "收盘价 11.64 元、市值 2,258.86 亿、PE 5.20、PB 0.47", "https://qt.gtimg.cn/q=sz000001"),
            ("2026 三季报", "平安银行 2026 年第三季度报告", "2026-10-24", "营收 1,031 亿、归母净利 391.86 亿、NPL 1.05%、拨备 214.75%", "https://finance.eastmoney.com/a/202610243907088337.html"),
            ("2025 年报", "平安银行 2025 年年度报告", "2026-03", "营收 1,314.42 亿、归母净利 426.33 亿、DPS 0.596 元", "https://www.szse.cn/"),
            ("分红", "2025 年度及 2026 中期分红公告", "2026", "2025 全年 0.596 元；2026 中期 0.249 元", "https://www.szse.cn/"),
            ("财务数据", "东方财富 F10（银行报表）", "2026-10-30", "BINCOME/BCASHFLOW/BBALANCE", "https://emweb.securities.eastmoney.com/"),
            ("无风险利率", "中国 10 年期国债", "2026-10-29", "1.6233%", "https://datacenter-web.eastmoney.com/"),
        ]
    else:
        rows = [
            ("行情", "腾讯证券 / 东方财富", "2026-10-30", "收盘价 51.99 元、总市值 11,276.34 亿、PE 20.70、PB 2.54", "https://qt.gtimg.cn/q=sh601088"),
            ("2026 三季报", "中国神华 2026 年第三季度报告", "2026-10-24", "营收 2,960.31 亿、归母净利 444.03 亿、扣非 428.08 亿", "http://app.cnstock.com/zzb/zgzqb/html/2026-10/24/nw.D110000zgzqb_20261024_1-B151.htm"),
            ("收购", "发行股份及支付现金购买资产并配套募资", "2026-03", "12 家标的、作价 1,335.98 亿；11 家并表；同一控制下合并", "http://app.cnstock.com/zzb/zgzqb/html/2026-10/24/nw.D110000zgzqb_20261024_1-B151.htm"),
            ("2025 年报", "中国神华 2025 年年度报告", "2026-03", "营收 2,949.16 亿、归母净利 528.49 亿、DPS 2.01 元", "https://www.sse.com.cn/"),
            ("分红政策", "2025–2027 年股东回报规划", "2025", "每年现金分红不低于 65%", "https://www.sse.com.cn/"),
            ("财务数据", "东方财富 F10", "2026-10-30", "历史报表、分红、估值指标", "https://emweb.securities.eastmoney.com/"),
            ("煤价", "秦皇岛 5500 现货 / 长协", "2026-10-30", "现货 1,020 元/吨；年度长协 717 元/吨", "https://www.cctd.com.cn/"),
        ]
    r = 5
    for row in rows:
        for j, v in enumerate(row, 1):
            cell(ws, r, j, v, align="left" if j in (2, 4, 5) else "center", wrap=(j in (4, 5)),
                 color="1A73E8" if j == 5 else INK)
        ws.merge_cells(start_row=r, start_column=5, end_row=r, end_column=8)
        if row[4].startswith("http"):
            ws.cell(row=r, column=5).hyperlink = row[4]
        ws.row_dimensions[r].height = 30
        r += 1
    note(ws, r + 1, "注：部分公告链接为交易所/公司公告页；东方财富 F10 为数据供应商，原始数据以公司公告为准。", 8)
    finish(ws, 8, freeze="A5")


def make_workbook(c):
    wb = Workbook()
    sheet_conclusion(wb, c)
    sheet_history(wb, c)
    sheet_segments(wb, c)
    sheet_valuation(wb, c)
    sheet_sensitivity(wb, c)
    sheet_scenarios(wb, c)
    sheet_sources(wb, c)
    wb.properties.title = f"{c.name} {c.code} 估值模型"
    wb.properties.creator = "Claudian · 巴菲特框架"
    wb.properties.subject = "巴菲特框架估值，不构成投资建议"
    outdir = OUT / f"{c.code}-{DATE}"
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f"{c.code}-估值模型-{DATE}.xlsx"
    wb.save(path)
    print("saved", path)
    return path


if __name__ == "__main__":
    for c in COMPANIES:
        make_workbook(c)
