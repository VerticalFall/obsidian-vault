# -*- coding: utf-8 -*-
"""Build CATL Buffett-framework Excel model (9 sheets)."""
import sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import ColorScaleRule

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catl_data as D

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / "输出" / "A股" / f"300750.SZ-{D.DATE}"
OUT.mkdir(parents=True, exist_ok=True)
XLSX = OUT / f"300750.SZ-估值模型-{D.DATE}.xlsx"

GREEN = "2F6B4F"; BROWN = "8C6D5A"; GOLD = "C9A227"; RED = "B23A2E"
INK = "1F2933"; MUTED = "5B6770"; BORDER = "D9D2C5"
TITLE_FILL = PatternFill("solid", fgColor=GREEN)
SECTION_FILL = PatternFill("solid", fgColor="E8EFE9")
HEADER_FILL = PatternFill("solid", fgColor="EFE8D8")
INPUT_FILL = PatternFill("solid", fgColor="F2F7FB")
NOTE_FILL = PatternFill("solid", fgColor="FBF7EA")
RED_FILL = PatternFill("solid", fgColor="F8E5E1")
GREEN_FILL = PatternFill("solid", fgColor="E3EFE7")
GOLD_FILL = PatternFill("solid", fgColor="F7EFD2")
THIN = Side(style="thin", color=BORDER)
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
FONT_CN = "Microsoft YaHei"


def title(ws, text, ncols=8, row=1):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)
    c = ws.cell(row=row, column=1, value=text)
    c.font = Font(name=FONT_CN, size=15, bold=True, color="FFFFFF")
    c.fill = TITLE_FILL
    c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[row].height = 30


def subtitle(ws, text, ncols=8, row=2):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)
    c = ws.cell(row=row, column=1, value=text)
    c.font = Font(name=FONT_CN, size=9, color=MUTED)
    c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[row].height = 18


def note(ws, row, text, ncols=8, height=30):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)
    c = ws.cell(row=row, column=1, value=text)
    c.font = Font(name=FONT_CN, size=8.5, color=MUTED, italic=True)
    c.fill = NOTE_FILL
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
    ws.row_dimensions[row].height = height


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


def cell(ws, row, col, value, fmt=None, bold=False, color=INK, fill=None,
         align="right", wrap=False, size=9.5):
    c = ws.cell(row=row, column=col, value=value)
    c.font = Font(name=FONT_CN, size=size, bold=bold, color=color)
    c.border = BORDER_ALL
    c.alignment = Alignment(horizontal=align, vertical="center", wrap_text=wrap)
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    return c


def inp(ws, row, col, value, fmt=None, align="right"):
    return cell(ws, row, col, value, fmt=fmt, color="1A73E8", fill=INPUT_FILL, align=align)


def block(ws, r1, c1, r2, c2, text, bold=False, color=INK, fill=None, size=10, height=None):
    ws.merge_cells(start_row=r1, start_column=c1, end_row=r2, end_column=c2)
    c = ws.cell(row=r1, column=c1, value=text)
    c.font = Font(name=FONT_CN, size=size, bold=bold, color=color)
    c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True, indent=1)
    if fill:
        c.fill = fill
    if height:
        ws.row_dimensions[r1].height = height


def finish(ws, ncols=8, freeze="A5", paper=None, fit_height=1):
    ws.sheet_view.showGridLines = False
    if freeze:
        ws.freeze_panes = freeze
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = fit_height
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_options.horizontalCentered = True
    ws.sheet_properties.tabColor = GREEN
    if paper:
        ws.page_setup.paperSize = paper


A3 = 8      # Excel paper size code for A3
A4 = 9


# ---------------------------------------------------------------- 1 一图流
def sheet_one(wb):
    ws = wb.active
    ws.title = "一图流"
    title(ws, "宁德时代 300750.SZ · 巴菲特框架估值", 8)
    subtitle(ws, f"报告日 {D.DATE}｜价格日 {D.PRICE_NOTE}｜单位：人民币亿元、元/股｜蓝色=输入，黑色=公式", 8)
    note(ws, 3, "本模型只用于研究记录，不构成投资建议。事实、计算、假设与判断分开标注；来源见「数据与来源」页。", 8)

    section(ws, 5, "一句话结论", 8)
    block(ws, 6, 1, 6, 8,
          f"便宜，但有条件的便宜。全球动力电池龙头，2026E PE {D.PRICE/D.EPS_2026E:.1f} 倍、"
          f"2027E PE {D.PRICE/D.EPS_2027E_BASE:.1f} 倍；DCF {D.DCF_BASE:.0f} 元、PE {D.PE_BASE_V:.0f} 元，"
          f"综合基准 {D.BLEND_BASE:.0f} 元，现价 {D.PRICE:.2f} 元，安全边际 {D.MOS*100:.1f}%。"
          f"便宜的前提是 2027 年税负能部分转嫁、单位盈利不再破位；若不能，基准价值下修到 {D.BLEND_BEAR:.0f} 元附近。",
          bold=False, fill=GREEN_FILL, size=10.5, height=52)

    section(ws, 8, "关键读数", 8)
    header(ws, 9, ["指标", "数值", "说明", "", "指标", "数值", "说明", ""],
           [18, 14, 26, 12, 18, 14, 40, 2])
    rows = [
        ("现价", D.PRICE, "元/股", "2026E PE", D.PRICE / D.EPS_2026E, "倍"),
        ("总市值", D.MARKET_CAP, "亿元", "2027E PE", D.PRICE / D.EPS_2027E_BASE, "倍"),
        ("DCF 每股", D.DCF_BASE, "元", "PB", D.PRICE / D.BPS, "倍"),
        ("PE 每股", D.PE_BASE_V, "元", "股息率", D.DPS_2026E / D.PRICE, "%"),
        ("综合基准", D.BLEND_BASE, "元", "净现金", D.NET_CASH, "亿元"),
        ("安全边际", D.MOS, "%", "评级", "便宜", ""),
    ]
    for i, (l1, v1, u1, l2, v2, u2) in enumerate(rows):
        r = 10 + i
        cell(ws, r, 1, l1, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        fmt1 = "0.00%" if u1 == "%" else ("#,##0.0" if abs(v1) > 1000 else "0.00")
        cell(ws, r, 2, v1, fmt=fmt1, bold=True)
        cell(ws, r, 3, u1, align="left", color=MUTED)
        cell(ws, r, 5, l2, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        if isinstance(v2, str):
            cell(ws, r, 6, v2, bold=True, color=GREEN, align="center")
        else:
            fmt2 = "0.00%" if u2 == "%" else ("#,##0" if abs(v2) > 1000 else "0.0")
            cell(ws, r, 6, v2, fmt=fmt2, bold=True)
        cell(ws, r, 7, u2, align="left", color=MUTED)
    cell(ws, 15, 2, D.MOS, fmt="0.0%", bold=True, color=GREEN)
    cell(ws, 15, 6, "便宜", bold=True, color=GREEN, align="center", fill=GREEN_FILL)
    cell(ws, 15, 7, "结论", align="left", color=MUTED)

    section(ws, 17, "三情景每股价值", 8)
    header(ws, 18, ["情景", "DCF", "PE", "综合", "现价", "综合较现价", "触发条件", ""])
    scen = [
        ("悲观", D.DCF_BEAR, D.PE_BEAR_V, D.BLEND_BEAR, "价格战延续；2027 消费税 4% 无法转嫁；海外扩张受阻"),
        ("基准", D.DCF_BASE, D.PE_BASE_V, D.BLEND_BASE, "单位盈利企稳；税负部分转嫁；出货量增长 20% 左右"),
        ("乐观", D.DCF_BULL, D.PE_BULL_V, D.BLEND_BULL, "储能与海外高增；单位盈利修复；估值回到 18 倍"),
    ]
    for i, (name, dcf, pe, blend, cond) in enumerate(scen):
        r = 19 + i
        fill = GOLD_FILL if name == "基准" else None
        cell(ws, r, 1, name, align="center", bold=True, fill=fill)
        cell(ws, r, 2, dcf, fmt="0.0", bold=True, fill=fill)
        cell(ws, r, 3, pe, fmt="0.0", bold=True, fill=fill)
        cell(ws, r, 4, blend, fmt="0.0", bold=True, fill=fill)
        cell(ws, r, 5, D.PRICE, fmt="0.00", fill=fill)
        cell(ws, r, 6, blend / D.PRICE - 1, fmt="0.0%", color=(GREEN if blend > D.PRICE else RED), bold=True, fill=fill)
        block(ws, r, 7, r, 8, cond, size=8.5, color=MUTED)
        ws.row_dimensions[r].height = 26
    note(ws, 22, "综合 = DCF 50% + PE 50%。PE 法使用 2027E EPS（基准 22.50 元，低于一致预期 23.57 元）× 目标 PE。", 8)

    section(ws, 24, "三条判断", 8)
    block(ws, 25, 1, 30, 2,
          "好生意：全球动力电池份额 39.2%，储能份额 30.4%；2025 年毛利率 26.3%、ROE 24.9%、经营现金流 1,332 亿。"
          "护城河来自规模成本、客户认证与产业链垂直整合，但不是提价权。",
          fill=GREEN_FILL, size=9, height=90)
    block(ws, 25, 3, 30, 5,
          f"好价格：现价 {D.PRICE:.2f} 元，对应 2026E PE {D.PRICE/D.EPS_2026E:.1f} 倍、2027E PE "
          f"{D.PRICE/D.EPS_2027E_BASE:.1f} 倍；综合基准 {D.BLEND_BASE:.0f} 元，安全边际 {D.MOS*100:.1f}%。"
          "便宜来自市场对税负与价格战的担忧，不是来自生意变差。",
          fill=GOLD_FILL, size=9, height=90)
    block(ws, 25, 6, 30, 8,
          "主要风险：① 2027 年消费税升至 4%、出口退税取消，税负无法转嫁；② 价格战导致单位盈利继续下台阶；"
          "③ 海外建厂与地缘政治；④ 技术路线变化；⑤ 客户集中与存货。任何一条恶化，悲观情景 219 元。",
          fill=RED_FILL, size=9, height=90)
    note(ws, 31, "数据截至 2026-09-30 财报；价格日 2026-11-05 午间。来源见「数据与来源」。不构成投资建议。", 8)
    finish(ws, 8, paper=A3)
    ws.print_area = "A1:H31"


# ---------------------------------------------------------------- 2 投资结论
def sheet_conclusion(wb):
    ws = wb.create_sheet("投资结论")
    title(ws, "投资结论 · 宁德时代 300750.SZ", 6)
    subtitle(ws, f"报告日 {D.DATE}｜价格日 {D.PRICE_NOTE}｜评级：便宜｜置信度：中", 6)

    block(ws, 4, 1, 4, 6,
          "便宜，但有条件的便宜。现价低于综合基准约 23%，但这不是“闭眼买”的便宜：2027 年税负上升、"
          "价格战与海外政策都会压缩单位盈利。安全边际来自“即使盈利下修，现价也不算贵”，而不是来自“盈利一定会修复”。",
          bold=True, fill=GREEN_FILL, size=10.5, height=54)

    section(ws, 6, "一、估值锚点", 6)
    header(ws, 7, ["锚点", "数值", "说明", "", "", ""], [26, 16, 52, 2, 2, 2])
    anchors = [
        ("现价", f"¥{D.PRICE:.2f}", "2026-11-05 午间；前收 252.88 元"),
        ("总市值", f"{D.MARKET_CAP:,.0f} 亿元", f"{D.SHARES:.4f} 亿股 × {D.PRICE:.2f} 元"),
        ("TTM 归母净利", f"{D.TTM_NP:,.1f} 亿元", "2025 年报 − 2025 前三季 + 2026 前三季"),
        ("TTM PE", f"{D.PRICE/D.TTM_EPS:.1f}x", f"TTM EPS {D.TTM_EPS:.2f} 元"),
        ("2026E PE", f"{D.PRICE/D.EPS_2026E:.1f}x", f"EPS {D.EPS_2026E:.2f} 元（一致预期净利 906 亿）"),
        ("2027E PE", f"{D.PRICE/D.EPS_2027E_BASE:.1f}x", f"EPS {D.EPS_2027E_BASE:.2f} 元（本报告假设，低于一致预期 23.57）"),
        ("PB", f"{D.PRICE/D.BPS:.2f}x", f"BPS {D.BPS:.2f} 元（2026Q3 归母净资产 3,868.8 亿）"),
        ("DCF 每股", f"¥{D.DCF_BASE:.2f}", "FCFF 490 亿、WACC 7.8%、g 2.5%、10 年 fade"),
        ("PE 每股", f"¥{D.PE_BASE_V:.2f}", "2027E EPS 22.50 元 × 15.3 倍"),
        ("综合基准", f"¥{D.BLEND_BASE:.2f}", "DCF 50% + PE 50%"),
        ("安全边际", f"{D.MOS*100:.1f}%", f"1 − {D.PRICE:.2f}/{D.BLEND_BASE:.2f}"),
        ("悲观 / 基准 / 乐观", f"¥{D.BLEND_BEAR:.0f} / {D.BLEND_BASE:.0f} / {D.BLEND_BULL:.0f}", "三情景综合价值"),
        ("20% 安全边际价", f"¥{D.MOS20_PRICE:.2f}", f"综合基准 × 0.8"),
        ("2026E 股息率", f"{D.DPS_2026E/D.PRICE*100:.1f}%", f"DPS {D.DPS_2026E:.2f} 元（假设 50% 总派息）"),
    ]
    for i, (a, b, c) in enumerate(anchors):
        r = 8 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 2, b, align="center", bold=True)
        block(ws, r, 3, r, 6, c, size=9, color=MUTED)
        ws.row_dimensions[r].height = 20

    section(ws, 23, "二、为什么是这个结论", 6)
    reasons = [
        "[事实] 2025 年营收 4,237 亿、归母净利 722 亿、经营现金流 1,332 亿、FCF 909 亿；全球动力电池份额 39.2%，储能份额 30.4%。",
        "[事实] 2026 前三季营收 4,421 亿（+56.2%）、归母净利 645 亿（+31.6%）；但 Q3 毛利率 20.7%、净利率 13.6%，单位盈利约 0.082 元/Wh，均为阶段低位。",
        f"[计算] 现价对应 2026E PE {D.PRICE/D.EPS_2026E:.1f}x、2027E PE {D.PRICE/D.EPS_2027E_BASE:.1f}x；DCF {D.DCF_BASE:.0f} 元、PE {D.PE_BASE_V:.0f} 元，综合 {D.BLEND_BASE:.0f} 元，安全边际 {D.MOS*100:.1f}%。",
        "[判断] 市场担心的是税负与价格战把 2027 年利润打下去。现价已经隐含 FCFF 比 2026E 低约 24%（反向 DCF 隐含 372 亿 vs 490 亿），但没有把“永久性衰退”定价进去。",
    ]
    for i, t in enumerate(reasons):
        block(ws, 24 + i, 1, 24 + i, 6, t, size=9.5, height=34)

    section(ws, 29, "三、什么会改变这个结论", 6)
    header(ws, 30, ["方向", "触发因素", "", "", "", ""])
    changes = [
        ("上调", "单位盈利连续两季回升至 0.09 元/Wh 以上；税负成功转嫁；储能出货超预期；海外工厂按期投产。"),
        ("上调", "2027 年一致预期 EPS 不再下修，或回购注销规模接近 400 亿上限。"),
        ("下调", "Q4 单位盈利跌破 0.07 元/Wh；2027 年消费税 4% 落地后毛利率跌破 18%。"),
        ("下调", "全球动力电池份额跌破 35%；海外收入占比或毛利率明显下滑。"),
        ("下调", "存货/营收升破 25%，或经营现金流连续两季负增长。"),
    ]
    for i, (d, t) in enumerate(changes):
        r = 31 + i
        cell(ws, r, 1, d, align="center", bold=True, color=(GREEN if d == "上调" else RED),
             fill=(GREEN_FILL if d == "上调" else RED_FILL))
        block(ws, r, 2, r, 6, t, size=9.5, height=28)

    section(ws, 37, "四、质量与估值分开", 6)
    header(ws, 38, ["维度", "判断", "依据", "", "", ""])
    quality = [
        ("生意质量", "高", "全球份额第一、成本曲线领先、客户认证周期长；但产品是工业品，没有提价权。"),
        ("财务质量", "高", "净现金 2,427 亿；ROE 24.9%；FCF 从 2021 年 -9 亿改善到 2025 年 909 亿。"),
        ("治理", "中", "创始人控制、分红率提升、回购注销；但资本开支大、海外扩张与关联交易需跟踪。"),
        ("估值", "便宜", f"综合基准 {D.BLEND_BASE:.0f} 元，现价 {D.PRICE:.2f} 元，安全边际 {D.MOS*100:.1f}%。"),
    ]
    for i, (a, b, c) in enumerate(quality):
        r = 39 + i
        cell(ws, r, 1, a, align="left", bold=True)
        cell(ws, r, 2, b, align="center", bold=True, color=(GREEN if b in ("高", "便宜") else GOLD))
        block(ws, r, 3, r, 6, c, size=9.5, height=26)

    section(ws, 44, "五、适用边界", 6)
    block(ws, 45, 1, 47, 6,
          "本结论适用于 3 年以上、能承受 30%–40% 回撤的资金。CATL 是周期成长股，不是类债红利：单位盈利、税率、"
          "海外政策都会让利润在两年内出现 20% 以上的波动。若要求“每年稳定分红”，应看红利专区，而不是这份报告。",
          size=9.5, height=54)
    note(ws, 48, "不构成投资建议。价格、财报与政策数据截至 2026-11-05；来源见「数据与来源」。", 6)
    finish(ws, 6, paper=A4)
    ws.print_area = "A1:F48"


# ---------------------------------------------------------------- 3 估值系统
def sheet_valuation(wb):
    ws = wb.create_sheet("估值系统")
    title(ws, "估值系统 · DCF + PE 双轨", 6)
    subtitle(ws, "蓝色=输入；黑色=公式；所有金额单位：人民币亿元，每股单位：元", 6)
    note(ws, 3, "DCF 用 FCFF，从企业价值减少数股东、加净现金得到股权价值；PE 用 2027E EPS × 目标倍数。两者各 50%。", 6)

    section(ws, 5, "一、市场与股本", 6)
    header(ws, 6, ["项目", "数值", "单位 / 说明", "", "", ""], [24, 16, 20, 14, 16, 2])
    inputs = [
        ("现价", D.PRICE, "元/股", "input", "0.00"),
        ("总股本", D.SHARES, "亿股", "input", "#,##0.0000"),
        ("总市值", "=B7*B8", "亿元", "formula", "#,##0.0"),
        ("净现金", D.NET_CASH, "亿元", "input", "#,##0.0"),
        ("少数股东权益", D.MINORITY, "亿元", "input", "#,##0.0"),
        ("每股净资产 BPS", D.BPS, "元/股", "input", "0.00"),
        ("2026E 归母净利", D.NP_2026E, "亿元", "input", "#,##0.0"),
        ("2026E EPS", "=B13/B8", "元/股", "formula", "0.00"),
        ("2026E DPS", D.DPS_2026E, "元/股", "input", "0.00"),
        ("2026E 股息率", "=B15/B7", "%", "formula", "0.00%"),
        ("2026E PE", "=B7/B14", "倍", "formula", "0.0"),
        ("2027E EPS（基准）", D.EPS_2027E_BASE, "元/股", "input", "0.00"),
        ("2027E PE", "=B7/B18", "倍", "formula", "0.0"),
        ("PB", "=B7/B12", "倍", "formula", "0.00"),
        ("TTM EPS", D.TTM_EPS, "元/股", "input", "0.00"),
        ("TTM PE", "=B7/B21", "倍", "formula", "0.0"),
    ]
    for i, (a, b, c, kind, fmt) in enumerate(inputs):
        r = 7 + i
        cell(ws, r, 1, a, align="left", bold=True)
        if kind == "input":
            inp(ws, r, 2, b, fmt=fmt)
        else:
            cell(ws, r, 2, b, fmt=fmt, bold=True)
        cell(ws, r, 3, c, align="left", color=MUTED)

    section(ws, 24, "二、DCF 假设", 6)
    header(ws, 25, ["参数", "数值", "说明", "", "", ""])
    dcf_inputs = [
        ("2026E FCFF", D.F0, "亿元", "input", "#,##0.0"),
        ("未来 10 年增速起点", D.G1, "%", "input", "0.0%"),
        ("终端增速 g", D.G_TERM, "%", "input", "0.0%"),
        ("WACC", D.WACC, "%", "input", "0.0%"),
        ("折现年数", D.FADE_YEARS, "年", "input", "0"),
        ("净现金", "=B10", "亿元", "formula", "#,##0.0"),
        ("少数股东权益", "=B11", "亿元", "formula", "#,##0.0"),
        ("总股本", "=B8", "亿股", "formula", "#,##0.0000"),
    ]
    for i, (a, b, c, kind, fmt) in enumerate(dcf_inputs):
        r = 26 + i
        cell(ws, r, 1, a, align="left", bold=True)
        if kind == "input":
            inp(ws, r, 2, b, fmt=fmt)
        else:
            cell(ws, r, 2, b, fmt=fmt, bold=True)
        cell(ws, r, 3, c, align="left", color=MUTED)

    section(ws, 35, "三、FCFF 折现", 6)
    header(ws, 36, ["年份", "增长率", "FCFF（亿元）", "折现因子", "现值（亿元）", ""])
    for i in range(10):
        r = 37 + i
        cell(ws, r, 1, 2027 + i, fmt="0", align="center")
        cell(ws, r, 2, f"=$B$27+($B$28-$B$27)*(ROW()-ROW($A$37))/($B$30-1)", fmt="0.0%")
        if i == 0:
            cell(ws, r, 3, "=$B$26*(1+B37)", fmt="#,##0.0")
        else:
            cell(ws, r, 3, f"=C{r-1}*(1+B{r})", fmt="#,##0.0")
        cell(ws, r, 4, f"=1/(1+$B$29)^(ROW()-ROW($A$37)+1)", fmt="0.000")
        cell(ws, r, 5, f"=C{r}*D{r}", fmt="#,##0.0")

    rows_tail = [
        ("终值 TV", "=C46*(1+$B$28)/($B$29-$B$28)", "#,##0.0", "Gordon 永续"),
        ("终值现值", "=B47*D46", "#,##0.0", "TV × 第 10 年折现因子"),
        ("企业价值 EV", "=SUM(E37:E46)+B48", "#,##0.0", "10 年 PV + TV PV"),
        ("减：少数股东", "=B32", "#,##0.0", "从 EV 到股权价值"),
        ("加：净现金", "=B31", "#,##0.0", "2026Q3"),
        ("股权价值", "=B49-B50+B51", "#,##0.0", ""),
        ("每股价值", "=B52/B33", "0.00", "DCF 基准"),
        ("较现价", "=B53/B7-1", "0.0%", "上行/下行"),
    ]
    for i, (a, b, fmt, c) in enumerate(rows_tail):
        r = 47 + i
        cell(ws, r, 1, a, align="left", bold=True)
        cell(ws, r, 2, b, fmt=fmt, bold=True)
        block(ws, r, 3, r, 6, c, size=8.5, color=MUTED)
        ws.row_dimensions[r].height = 18

    section(ws, 56, "四、PE 估值", 6)
    header(ws, 57, ["项目", "数值", "说明", "", "", ""])
    pe_rows = [
        ("2027E EPS", "=B18", "0.00", "本报告假设 22.50 元"),
        ("目标 PE", D.PE_BASE, "0.0", "15.3 倍：15% 增长 + 24% ROE + 净现金"),
        ("PE 每股价值", "=B58*B59", "0.00", "EPS × 目标 PE"),
        ("现价对应 2027E PE", "=B7/B58", "0.0", "反向检查"),
    ]
    for i, (a, b, fmt, c) in enumerate(pe_rows):
        r = 58 + i
        cell(ws, r, 1, a, align="left", bold=True)
        if a == "目标 PE":
            inp(ws, r, 2, b, fmt=fmt)
        else:
            cell(ws, r, 2, b, fmt=fmt, bold=True)
        block(ws, r, 3, r, 6, c, size=9, color=MUTED)

    section(ws, 63, "五、综合与评级", 6)
    header(ws, 64, ["项目", "数值", "说明", "", "", ""])
    mix_rows = [
        ("DCF 权重", D.DCF_WEIGHT, "%", "input", "0%"),
        ("PE 权重", D.PE_WEIGHT, "%", "input", "0%"),
        ("DCF 每股", "=B53", "元", "formula", "0.00"),
        ("PE 每股", "=B60", "元", "formula", "0.00"),
        ("综合每股", "=B65*B67+B66*B68", "元", "formula", "0.00"),
        ("安全边际", "=1-B7/B69", "%", "formula", "0.0%"),
        ("评级", '=IF(B70>0.2,"便宜",IF(B70>0.05,"合理偏低",IF(B70>-0.05,"合理",IF(B70>-0.2,"合理偏贵","昂贵"))))', "", "formula", "@"),
        ("20% 安全边际价", "=B69*0.8", "元", "formula", "0.00"),
        ("现价较基准", "=B69/B7-1", "%", "formula", "0.0%"),
    ]
    for i, (a, b, c, kind, fmt) in enumerate(mix_rows):
        r = 65 + i
        cell(ws, r, 1, a, align="left", bold=True)
        if kind == "input":
            inp(ws, r, 2, b, fmt=fmt)
        else:
            cell(ws, r, 2, b, fmt=fmt, bold=True,
                 color=(GREEN if a == "评级" else INK),
                 fill=(GREEN_FILL if a == "评级" else None))
        cell(ws, r, 3, c, align="left", color=MUTED)

    section(ws, 75, "六、反向估值", 6)
    header(ws, 76, ["项目", "数值", "说明", "", "", ""])
    rev_rows = [
        ("现价隐含 2026E FCFF", "=B26*B7/B67", "#,##0.0", "假设增速/WACC 不变，反推 F0"),
        ("较基准 FCFF", "=B77/B26-1", "0.0%", "市场定价的现金流折价"),
        ("现价隐含 2027E PE", "=B7/B18", "0.0", "与目标 PE 对照"),
    ]
    for i, (a, b, fmt, c) in enumerate(rev_rows):
        r = 77 + i
        cell(ws, r, 1, a, align="left", bold=True)
        cell(ws, r, 2, b, fmt=fmt, bold=True)
        block(ws, r, 3, r, 6, c, size=9, color=MUTED)

    section(ws, 81, "七、交叉检查", 6)
    header(ws, 82, ["检查项", "数值", "结论", "", "", ""])
    checks = [
        ("权重合计", "=B65+B66", "=IF(ABS(B83-1)<0.0001,\"OK\",\"权重不等于 100%\")", "0%"),
        ("DCF 对应 2027E PE", "=B53/B18", "=IF(B84>5,\"合理区间\",\"偏低\")", "0.0"),
        ("PE 隐含 2027E 净利", "=B58*B33", "=IF(B85>800,\"高于 2026E 906 亿，反映增长\",\"低于 2026E\")", "#,##0"),
    ]
    for i, (a, b, c, fmt) in enumerate(checks):
        r = 83 + i
        cell(ws, r, 1, a, align="left", bold=True)
        cell(ws, r, 2, b, fmt=fmt, bold=True)
        block(ws, r, 3, r, 6, c, size=9, color=MUTED)

    finish(ws, 6, paper=A3)
    ws.print_area = "A1:F85"


# ---------------------------------------------------------------- 4 生意与护城河
def sheet_business(wb):
    ws = wb.create_sheet("生意与护城河")
    title(ws, "生意与护城河 · 动力电池 + 储能 + 材料", 7)
    subtitle(ws, "收入结构、经营数据、护城河评分与反证", 7)
    note(ws, 3, "护城河评分是研究判断（1–5 分），不是精确指标；分数用于横向比较与跟踪，不进入估值公式。", 7)

    section(ws, 5, "一、收入结构（2025 年报）", 7)
    header(ws, 6, ["业务", "收入（亿元）", "占比", "毛利率", "备注", "", ""], [18, 12, 10, 10, 40, 12, 2])
    for i, (name, rev, share, gm) in enumerate(D.SEGMENTS_2025):
        r = 7 + i
        cell(ws, r, 1, name, align="left", bold=True)
        cell(ws, r, 2, rev, fmt="#,##0.0")
        cell(ws, r, 3, share, fmt="0.0%")
        cell(ws, r, 4, gm, fmt="0.0%")
        note_txt = {
            "动力电池系统": "全球份额 39.2%；2025 销量 541GWh（+41.9%）",
            "储能电池系统": "全球份额 30.4%；2025 销量 121GWh（+29.1%）",
            "电池材料及回收": "锂矿、正极、回收；内部供应 + 外售",
            "其他": "电池矿产、换电等",
        }[name]
        block(ws, r, 5, r, 7, note_txt, size=8.5, color=MUTED)
    r = 11
    cell(ws, r, 1, "合计", align="left", bold=True, fill=HEADER_FILL)
    cell(ws, r, 2, sum(x[1] for x in D.SEGMENTS_2025), fmt="#,##0.0", bold=True, fill=HEADER_FILL)
    cell(ws, r, 3, sum(x[2] for x in D.SEGMENTS_2025), fmt="0.0%", bold=True, fill=HEADER_FILL)
    cell(ws, r, 4, 0.263, fmt="0.0%", bold=True, fill=HEADER_FILL)
    block(ws, r, 5, r, 7, "2025 综合毛利率 26.3%", size=8.5, color=MUTED, fill=HEADER_FILL)

    section(ws, 13, "二、2026H1 结构变化", 7)
    header(ws, 14, ["业务", "收入（亿元）", "占比", "毛利率", "变化", "", ""])
    for i, (name, rev, share, gm) in enumerate(D.SEGMENTS_2026H1):
        r = 15 + i
        cell(ws, r, 1, name, align="left", bold=True)
        cell(ws, r, 2, rev, fmt="#,##0.0")
        cell(ws, r, 3, share, fmt="0.0%")
        cell(ws, r, 4, gm, fmt="0.0%")
        chg = {
            "动力电池系统": "占比 74.7%→69.4%；毛利率 23.8%→20.6%",
            "储能电池系统": "占比 14.7%→19.2%；毛利率 26.7%→24.0%",
            "电池材料及回收": "占比 7.1%→7.9%；毛利率 12.1%→11.0%",
            "其他": "占比基本稳定",
        }[name]
        block(ws, r, 5, r, 7, chg, size=8.5, color=MUTED)

    section(ws, 20, "三、经营数据", 7)
    header(ws, 21, ["指标", "2024", "2025", "2026E / 最新", "说明", "", ""])
    ops = [
        ("电池销量（GWh）", "475", f"{D.SALES_2025:.0f}", "约 1,000（目标）", "2025 +39.2%；2026 目标翻倍增长"),
        ("产能（GWh）", "676", f"{D.CAPACITY_2025:.0f}", "在建 321", "2025 产能利用率 96.9%"),
        ("全球动力电池份额", "38.0%", "39.2%", "39% 左右", "SNE Research；连续 9 年第一"),
        ("储能电池份额", "—", "30.4%", "约 30%", "连续 5 年全球第一"),
        ("海外收入占比", "—", "30.6%", "31.5%（2026H1）", "海外毛利率 31.4%，显著高于国内"),
        ("研发投入（亿元）", "—", "221", "—", "约占营收 5.2%"),
    ]
    for i, row in enumerate(ops):
        r = 22 + i
        cell(ws, r, 1, row[0], align="left", bold=True)
        for j, v in enumerate(row[1:4], 2):
            cell(ws, r, j, v, align="center")
        block(ws, r, 5, r, 7, row[4], size=8.5, color=MUTED)

    section(ws, 29, "四、护城河评分", 7)
    header(ws, 30, ["维度", "权重", "评分（1–5）", "证据", "", "趋势", ""])
    moat = [
        ("规模与成本", "30%", 5, "772GWh 产能、661GWh 销量；单位成本行业最低之一；2025 年毛利率 26.3%，高于二线 5–10pct。", "持平"),
        ("客户认证", "25%", 4, "车企认证周期 2–3 年；前五大客户占 39%，第一大 13.7%；但车企多供策略削弱粘性。", "略降"),
        ("技术与产品", "20%", 5, "麒麟、神行、钠新、凝聚态；研发 221 亿、2 万+ 研发人员；LFP 快充与储能领先。", "持平"),
        ("产业链整合", "15%", 4, "锂矿、正极、回收一体化；原材料波动时成本更稳；但锂价下行时库存减值。", "持平"),
        ("海外本地化", "10%", 3, "德国、匈牙利、西班牙（Stellantis JV）、印尼；海外毛利率 31.4%，但地缘政治风险高。", "上升"),
    ]
    for i, (a, w, s, ev, tr) in enumerate(moat):
        r = 31 + i
        cell(ws, r, 1, a, align="left", bold=True)
        cell(ws, r, 2, w, align="center")
        cell(ws, r, 3, s, fmt="0", align="center", bold=True,
             color=(GREEN if s >= 4 else GOLD), fill=(GREEN_FILL if s >= 4 else GOLD_FILL))
        block(ws, r, 4, r, 5, ev, size=8.5)
        cell(ws, r, 6, tr, align="center", color=(GREEN if tr == "上升" else (RED if tr == "略降" else MUTED)))
        ws.row_dimensions[r].height = 38
    block(ws, 36, 1, 36, 7,
          "综合：4.3 / 5。护城河真实存在，但它是“成本曲线上的护城河”，不是“提价权上的护城河”。"
          "当行业价格战激烈时，龙头也只能用成本优势守住份额，无法阻止单价和单位盈利下行。",
          bold=True, fill=GREEN_FILL, size=9.5, height=38)

    section(ws, 38, "五、反证与空头论点", 7)
    bears = [
        "份额见顶：全球动力电池份额从 2024 年 38.0% 到 2025 年 39.2%，提升放缓；国内份额被比亚迪、中创新航、亿纬锂能分流。",
        "车企去宁德化：特斯拉 4680、大众 PowerCo、通用 Ultium、吉利/广汽自研；二供、三供是车企的标准策略。",
        "技术收敛：LFP 快充、储能电芯逐步标准化，二线产品差距缩小；固态电池若提前产业化，现有产能面临重估。",
        "价格战：2026Q3 单位盈利 0.082 元/Wh 为阶段低位；若 2027 年税负无法转嫁，单位盈利可能跌破 0.07 元。",
        "海外政策：美国 IRA FEOC、欧盟电池法规、关税；海外高毛利（31.4%）是估值的关键支撑，也是最脆弱的部分。",
    ]
    for i, t in enumerate(bears):
        r = 39 + i
        block(ws, r, 1, r, 7, f"{i+1}. {t}", size=9, height=30)

    finish(ws, 7, paper=A3)
    ws.print_area = "A1:G43"


# ---------------------------------------------------------------- 5 财务与现金流
def sheet_financials(wb):
    ws = wb.create_sheet("财务与现金流")
    title(ws, "财务与现金流 · 2021–2026Q3", 8)
    subtitle(ws, "增长、利润率、ROE、经营现金流、资本开支与自由现金流", 8)
    note(ws, 3, "2021/2022 每股指标按当时股本，未做统一复权；跨年比较以营收、净利、ROE、利润率为准。", 8)

    section(ws, 5, "一、年度损益与现金流", 8)
    header(ws, 6, ["指标", "2021", "2022", "2023", "2024", "2025", "2026 9M", ""],
           [20, 13, 13, 13, 13, 13, 13, 2])
    rows = [
        ("营业收入（亿元）", D.REVENUE + [4421.37], "#,##0.0"),
        ("营收同比", [None, 1.521, 0.220, -0.097, 0.170, 0.562], "0.0%"),
        ("归母净利（亿元）", D.NP + [645.30], "#,##0.0"),
        ("净利同比", [None, 0.929, 0.436, 0.150, 0.423, 0.316], "0.0%"),
        ("EPS（元）", D.EPS + [14.13], "0.00"),
        ("ROE", D.ROE + [0.1764], "0.0%"),
        ("毛利率", D.GM + [0.2272], "0.0%"),
        ("净利率", D.NM + [0.1459], "0.0%"),
        ("经营现金流（亿元）", D.OCF + [616.30], "#,##0.0"),
        ("资本开支（亿元）", D.CAPEX + [421.67], "#,##0.0"),
        ("自由现金流（亿元）", D.FCF + [194.63], "#,##0.0"),
    ]
    for i, (name, vals, fmt) in enumerate(rows):
        r = 7 + i
        cell(ws, r, 1, name, align="left", bold=True)
        for j, v in enumerate(vals):
            if v is None:
                cell(ws, r, 2 + j, "—", align="center", color=MUTED)
            else:
                color = RED if (name == "自由现金流（亿元）" and v < 0) else INK
                cell(ws, r, 2 + j, v, fmt=fmt, color=color)
    ws.row_dimensions[9].height = 20

    section(ws, 19, "二、2026 分季", 8)
    header(ws, 20, ["指标", "2026Q1", "2026Q2", "2026Q3", "说明", "", "", ""])
    qrows = [
        ("营业收入（亿元）", D.Q_REV, "#,##0.0"),
        ("归母净利（亿元）", D.Q_NP, "#,##0.0"),
        ("毛利率", D.Q_GM, "0.0%"),
    ]
    for i, (name, vals, fmt) in enumerate(qrows):
        r = 21 + i
        cell(ws, r, 1, name, align="left", bold=True)
        for j, v in enumerate(vals):
            cell(ws, r, 2 + j, v, fmt=fmt)
    block(ws, 21, 5, 23, 8,
          "Q3 营收同比 +58.6%、环比 +11.8%；净利同比 +14.5%、环比 −5.8%；毛利率 20.7%，为 2022Q4 以来低位。"
          "增收不增利的主因：消费税开征、出口退税率下调、低毛利产品占比上升、存货减值。",
          size=8.5, color=MUTED, height=60)

    section(ws, 25, "三、2026Q3 资产负债表", 8)
    header(ws, 26, ["项目", "金额（亿元）", "说明", "", "项目", "金额（亿元）", "说明", ""])
    bs = [
        ("货币资金", D.CASH, "含库存现金、银行存款", "总资产", D.TOTAL_ASSETS, "2026-09-30"),
        ("交易性金融资产", D.TRADING_FA, "理财、债券等", "总负债", D.TOTAL_LIAB, "资产负债率 64.2%"),
        ("有息负债", D.INTEREST_DEBT, "短期借款+长期借款+应付债券", "归母净资产", D.PARENT_EQUITY, "BPS 83.61 元"),
        ("净现金", D.NET_CASH, "货币+交易性金融−有息负债", "少数股东权益", D.MINORITY, "从 EV 到股权价值需扣除"),
    ]
    for i, row in enumerate(bs):
        r = 27 + i
        cell(ws, r, 1, row[0], align="left", bold=True)
        cell(ws, r, 2, row[1], fmt="#,##0.0", bold=True)
        block(ws, r, 3, r, 4, row[2], size=8.5, color=MUTED)
        cell(ws, r, 5, row[3], align="left", bold=True)
        cell(ws, r, 6, row[4], fmt="#,##0.0", bold=True)
        block(ws, r, 7, r, 8, row[5], size=8.5, color=MUTED)

    section(ws, 32, "四、营运资本与现金质量", 8)
    header(ws, 33, ["指标", "2023", "2024", "2025", "2026Q3", "解读", "", ""])
    wc = [
        ("存货（亿元）", "454.3", "598.4", "945.3", "—", "2025 存货 +58%，为销量增长与锂价备货；2026 需盯减值"),
        ("应收账款（亿元）", "—", "—", "—", "—", "车企账期长；2026 公司主动缩短供应商账期，自身回款需跟踪"),
        ("应付账款（亿元）", "—", "—", "1,603.3", "—", "占用上游资金是现金流优势，但缩短账期会反噬 OCF"),
        ("经营现金流/净利", "2.10", "1.91", "1.84", "0.96", "2026 9M 降至 0.96，主因预付款与账期调整"),
        ("资本开支/折旧", "—", "—", "—", "—", "2026 9M 资本开支 421.7 亿，同比 +40%"),
    ]
    for i, row in enumerate(wc):
        r = 34 + i
        cell(ws, r, 1, row[0], align="left", bold=True)
        for j, v in enumerate(row[1:5], 2):
            cell(ws, r, j, v, align="center")
        block(ws, r, 6, r, 8, row[5], size=8.5, color=MUTED)
        ws.row_dimensions[r].height = 26

    note(ws, 40, "2026 9M 为前三季度累计，不与年度直接可比；ROE 17.64% 为加权未年化。来源见「数据与来源」。", 8)
    finish(ws, 8, paper=A3)
    ws.print_area = "A1:H40"


# ---------------------------------------------------------------- 6 分红与股东回报
def sheet_dividend(wb):
    ws = wb.create_sheet("分红与股东回报")
    title(ws, "分红与股东回报 · 特别股息 + 回购注销", 6)
    subtitle(ws, "DPS、派息率、回购与总股东回报", 6)
    note(ws, 3, "2025 年 DPS 含特别股息 4.779 元/股；用总派息率看股东回报，用普通股息率看可持续性。", 6)

    section(ws, 5, "一、DPS 与派息率", 6)
    header(ws, 6, ["年度", "DPS（元）", "派息率", "按现价股息率", "备注", ""], [20, 14, 12, 16, 46, 2])
    notes = {
        "2022": "10 转 8 派 25.20 元（转增前口径）",
        "2023": "10 派 20.11 元；派息率约 20%",
        "2024": "10 派 45.53 元；派息率约 39%",
        "2025": "中期 1.007 + 年度 6.957（含特别 4.779）；合计 7.964",
        "2026E": "中期 1.411 已派；假设全年 50% 总派息",
    }
    for i, (y, dps, po) in enumerate(zip(D.DIV_YEARS, D.DPS, D.PAYOUT)):
        r = 7 + i
        cell(ws, r, 1, y, align="center", bold=True)
        cell(ws, r, 2, dps, fmt="0.000")
        cell(ws, r, 3, po, fmt="0%")
        cell(ws, r, 4, dps / D.PRICE, fmt="0.00%")
        block(ws, r, 5, r, 6, notes[y], size=8.5, color=MUTED)
        ws.row_dimensions[r].height = 24

    section(ws, 13, "二、2025 年分红拆解", 6)
    header(ws, 14, ["项目", "每 10 股（元）", "合计（亿元）", "性质", "说明", ""])
    div = [
        ("中期股息", "10.07", 45.68, "普通", "2025-08 A 股派发"),
        ("年度普通股息", "21.78", 98.80, "普通", "年度分红中的常规部分"),
        ("年度特别股息", "47.79", 216.52, "特别", "一次性；不应年化"),
        ("合计", "79.64", 361.01, "—", "派息率 50.0%"),
    ]
    for i, (a, b, c, d, e) in enumerate(div):
        r = 15 + i
        fill = HEADER_FILL if a == "合计" else None
        cell(ws, r, 1, a, align="left", bold=True, fill=fill)
        cell(ws, r, 2, b, align="center", fill=fill)
        cell(ws, r, 3, c, fmt="#,##0.0", bold=(a == "合计"), fill=fill)
        cell(ws, r, 4, d, align="center", color=(GOLD if d == "特别" else INK), fill=fill)
        block(ws, r, 5, r, 6, e, size=8.5, color=MUTED, fill=fill)
    note(ws, 19, "2025 年普通股息合计约 144.5 亿元（DPS 3.185 元），对应普通派息率约 20%；特别股息 216.5 亿元是一次性回报，不能当作可持续股息。", 6, height=34)

    section(ws, 21, "三、回购注销", 6)
    header(ws, 22, ["项目", "内容", "说明", "", "", ""])
    buyback = [
        ("方案", "200–400 亿元，价格上限 573 元/股", "2026-07-24 公告；A 股史上最大单次回购"),
        ("用途", "全部注销并减少注册资本", "直接增厚 EPS，不是股权激励"),
        ("期限", "股东会通过后 12 个月", "回购规模取决于股价与执行节奏"),
        ("已执行", "约 53.6 亿元（截至 2026-10-31）", "实际成交价 227–332 元，远低于 573 元上限"),
        ("上限测算", "400 亿 / 573 元 ≈ 6,981 万股", "约占总股本 1.51%；下限 200 亿约 0.75%"),
    ]
    for i, (a, b, c) in enumerate(buyback):
        r = 23 + i
        cell(ws, r, 1, a, align="left", bold=True)
        block(ws, r, 2, r, 3, b, size=9)
        block(ws, r, 4, r, 6, c, size=8.5, color=MUTED)
        ws.row_dimensions[r].height = 24

    section(ws, 29, "四、总股东回报（按现价）", 6)
    header(ws, 30, ["项目", "收益率", "口径", "", "", ""])
    total = [
        ("2026E 股息率", D.DPS_2026E / D.PRICE, "假设 50% 总派息，含可能特别股息"),
        ("回购收益率（年化）", 300 / D.MARKET_CAP, "假设 300 亿元回购在 12 个月内执行"),
        ("合计股东回报", D.DPS_2026E / D.PRICE + 300 / D.MARKET_CAP, "一次性回购不可持续，仅作当年参考"),
        ("普通股息率", 3.185 / D.PRICE, "2025 年普通 DPS 3.185 元，更接近可持续水平"),
    ]
    for i, (a, b, c) in enumerate(total):
        r = 31 + i
        cell(ws, r, 1, a, align="left", bold=True)
        cell(ws, r, 2, b, fmt="0.00%", bold=(a == "合计股东回报"),
             color=(GREEN if a == "合计股东回报" else INK))
        block(ws, r, 3, r, 6, c, size=9, color=MUTED)

    note(ws, 36, "CATL 不是红利股：股息率 3.7% 来自 50% 总派息假设，普通股息率仅约 1.2%。回购注销是更重要的股东回报形式。", 6, height=34)
    finish(ws, 6, paper=A4)
    ws.print_area = "A1:F36"


# ---------------------------------------------------------------- 7 估值与假设
def sheet_assumptions(wb):
    ws = wb.create_sheet("估值与假设")
    title(ws, "估值与假设 · WACC、情景与敏感性", 8)
    subtitle(ws, "WACC 构建、三情景参数、DCF 敏感性", 8)
    note(ws, 3, "情景价值为同一 DCF 公式的输出（冻结值），用于展示区间；修改上方参数不会自动重算情景表。", 8)

    section(ws, 5, "一、WACC 构建", 8)
    header(ws, 6, ["参数", "数值", "说明", "", "", "", "", ""], [22, 14, 12, 12, 12, 12, 12, 12])
    wacc_rows = [
        ("无风险利率 Rf", 0.018, "中国 10 年期国债，约 1.8%"),
        ("股权风险溢价 ERP", 0.060, "成熟市场 5% + 中国溢价 1%"),
        ("Beta", 1.15, "动力电池龙头，周期成长属性"),
        ("股权成本 Ke", "=B7+B8*B9", "CAPM"),
        ("债务成本 Kd", 0.025, "平均融资成本"),
        ("税率", 0.15, "高新技术企业 15%"),
        ("债务权重 D/(D+E)", 0.13, "有息负债 1,899 亿 /（市值+负债）"),
        ("WACC", "=B10*(1-B13)+B11*(1-B12)*B13", "加权平均资本成本"),
    ]
    for i, (a, b, c) in enumerate(wacc_rows):
        r = 7 + i
        cell(ws, r, 1, a, align="left", bold=True)
        if a in ("无风险利率 Rf", "股权风险溢价 ERP", "Beta", "债务成本 Kd", "税率", "债务权重 D/(D+E)"):
            inp(ws, r, 2, b, fmt=("0.00" if a == "Beta" else "0.0%"))
        else:
            cell(ws, r, 2, b, fmt="0.0%", bold=True)
        block(ws, r, 3, r, 8, c, size=9, color=MUTED)

    section(ws, 16, "二、三情景假设", 8)
    header(ws, 17, ["情景", "FCFF 基数", "增速起点", "WACC", "2027E EPS", "目标 PE", "DCF 价值", "综合价值"])
    scenarios = [
        ("悲观", D.BEAR_F0, D.BEAR_G1, D.BEAR_WACC, D.EPS_2027E_BEAR, D.PE_BEAR, D.DCF_BEAR, D.BLEND_BEAR),
        ("基准", D.F0, D.G1, D.WACC, D.EPS_2027E_BASE, D.PE_BASE, D.DCF_BASE, D.BLEND_BASE),
        ("乐观", D.BULL_F0, D.BULL_G1, D.BULL_WACC, D.EPS_2027E_BULL, D.PE_BULL, D.DCF_BULL, D.BLEND_BULL),
    ]
    for i, row in enumerate(scenarios):
        r = 18 + i
        fill = GOLD_FILL if row[0] == "基准" else None
        cell(ws, r, 1, row[0], align="center", bold=True, fill=fill)
        cell(ws, r, 2, row[1], fmt="#,##0", fill=fill)
        cell(ws, r, 3, row[2], fmt="0.0%", fill=fill)
        cell(ws, r, 4, row[3], fmt="0.0%", fill=fill)
        cell(ws, r, 5, row[4], fmt="0.00", fill=fill)
        cell(ws, r, 6, row[5], fmt="0.0", fill=fill)
        cell(ws, r, 7, row[6], fmt="0.0", bold=True, fill=fill)
        cell(ws, r, 8, row[7], fmt="0.0", bold=True, fill=fill)
    note(ws, 21, "悲观：价格战 + 税负无法转嫁 + 海外受阻；基准：单位盈利企稳、税负部分转嫁；乐观：储能/海外高增、估值修复。", 8, height=34)

    section(ws, 23, "三、DCF 敏感性（每股价值，元）", 8)
    header(ws, 24, ["WACC \\ g", "1.5%", "2.0%", "2.5%", "3.0%", "3.5%", "", ""])
    for i, w in enumerate(D.WACC_GRID):
        r = 25 + i
        cell(ws, r, 1, w, fmt="0.0%", bold=True, align="center", fill=HEADER_FILL)
        for j, v in enumerate(D.SENS[i]):
            cell(ws, r, 2 + j, v, fmt="0.0", bold=(abs(w - D.WACC) < 1e-9 and j == 2),
                 fill=(GOLD_FILL if abs(w - D.WACC) < 1e-9 and j == 2 else None))
    ws.conditional_formatting.add("B25:F29",
        ColorScaleRule(start_type="min", start_color="F8E5E1",
                       mid_type="percentile", mid_value=50, mid_color="F7EFD2",
                       end_type="max", end_color="E3EFE7"))

    section(ws, 31, "四、关键假设说明", 8)
    assumptions = [
        ("FCFF 基数 490 亿", "2026E 净利 906 + 折旧摊销约 500 + 利息约 30 − 资本开支约 700 − 营运资本增加约 250。"),
        ("增速 12% → 2.5%", "2027–2036 线性 fade；前五年反映储能/海外增长，后五年收敛到终端。"),
        ("WACC 7.8%", "Ke 8.7%（Rf 1.8% + 1.15×6.0%），Kd 2.5%，D/(D+E) 13%，税率 15%。"),
        ("2027E EPS 22.50", "低于一致预期 23.57，已反映消费税 4% 与出口退税取消的部分影响；不是公司指引。"),
        ("目标 PE 15.3x", "对应 2027E 15% 增长、24% ROE、净现金；低于 2021–2025 年平均，高于当前 11.8x。"),
    ]
    for i, (a, b) in enumerate(assumptions):
        r = 32 + i
        cell(ws, r, 1, a, align="left", bold=True)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        block(ws, r, 3, r, 8, b, size=9, color=MUTED)
        ws.row_dimensions[r].height = 28

    section(ws, 38, "五、交叉检查", 8)
    header(ws, 39, ["检查", "数值", "结论", "", "", "", "", ""])
    checks = [
        ("WACC 与估值系统一致", "=B14", '=IF(ABS(B40-0.078)<0.001,"OK","与估值系统不一致")'),
        ("基准 DCF 与估值系统一致", "=G19", '=IF(ABS(B41-349.9)<1,"OK","与估值系统不一致")'),
        ("悲观 < 基准 < 乐观", "=G18", '=IF(AND(G18<G19,G19<G20),"OK","区间异常")'),
    ]
    for i, (a, b, c) in enumerate(checks):
        r = 40 + i
        cell(ws, r, 1, a, align="left", bold=True)
        cell(ws, r, 2, b, fmt=("0.00%" if r == 40 else "0.0"), bold=True)
        block(ws, r, 3, r, 8, c, size=9, color=MUTED)

    finish(ws, 8, paper=A3)
    ws.print_area = "A1:H42"


# ---------------------------------------------------------------- 8 风险与跟踪
def sheet_risk(wb):
    ws = wb.create_sheet("风险与跟踪")
    title(ws, "风险与跟踪 · 三个永久性损失风险", 7)
    subtitle(ws, "风险矩阵、永久性损失、监控触发条件", 7)

    section(ws, 4, "一、风险矩阵", 7)
    header(ws, 5, ["风险", "概率", "影响", "传导路径", "缓释因素", "", ""], [24, 18, 16, 40, 40, 2, 2])
    risks = [
        ("价格战 / 单位盈利下滑", "高", "高", "车企压价 → 单价下降 → 单位盈利 0.082→0.06 元/Wh → 净利下修 20%+", "成本领先、份额 39%、储能占比提升"),
        ("税负无法转嫁", "中高", "高", "消费税 2%→4%、出口退税 9%→0 → 毛利率 −2~3pct → 2027 净利下修", "与客户协商分担、海外本地生产、产品升级"),
        ("海外地缘政治", "中", "高", "IRA/EU 关税/本地化要求 → 海外收入受限 → 失去 31% 高毛利", "德国/匈牙利/西班牙/印尼本地化"),
        ("技术路线变化", "低", "高", "固态电池提前产业化 → 现有产能与 LFP 技术重估", "凝聚态/钠电/固态研发投入 221 亿"),
        ("客户集中", "中", "中", "前五大 39%、第一大 13.7%；大客户转单 → 收入波动", "客户覆盖广、海外车企增量"),
        ("存货 / 减值", "中", "中", "存货 945 亿（2025）+ 锂价下行 → 减值 → 利润波动", "库存周转管理、长协"),
    ]
    for i, row in enumerate(risks):
        r = 6 + i
        cell(ws, r, 1, row[0], align="left", bold=True)
        cell(ws, r, 2, row[1], align="center", color=(RED if row[1] in ("高", "中高") else GOLD))
        cell(ws, r, 3, row[2], align="center", color=(RED if row[2] == "高" else GOLD))
        block(ws, r, 4, r, 4, row[3], size=8.5)
        block(ws, r, 5, r, 7, row[4], size=8.5, color=MUTED)
        ws.row_dimensions[r].height = 32

    section(ws, 13, "二、三个永久性损失风险", 7)
    perms = [
        ("技术被颠覆", "固态电池/新体系由竞争对手率先量产，CATL 的产能与技术资产被重估。概率低，但一旦发生，估值不是跌 30%，而是商业逻辑重写。"),
        ("海外市场被强制分割", "美国/欧盟以安全或本地化理由限制中国电池，CATL 失去海外高毛利市场；国内价格战更激烈，ROE 长期跌破 WACC。"),
        ("价格战长期化", "产能过剩 + 车企自研，电池变成标准化大宗品，单位盈利永久性下台阶；CATL 仍是龙头，但赚不到超额利润。"),
    ]
    for i, (a, b) in enumerate(perms):
        r = 14 + i
        block(ws, r, 1, r, 2, a, bold=True, color=RED, fill=RED_FILL, size=10)
        block(ws, r, 3, r, 7, b, size=9, height=44)
        ws.row_dimensions[r].height = 44

    section(ws, 19, "三、监控触发条件", 7)
    header(ws, 20, ["指标", "当前", "触发阈值", "动作", "", "", ""])
    triggers = [
        ("季度单位盈利（元/Wh）", "0.082（2026Q3）", "< 0.06", "下调 2027E EPS 10–15%，重估基准"),
        ("毛利率", "20.7%（2026Q3）", "< 18% 连续两季", "确认价格战恶化，转向悲观情景"),
        ("全球动力电池份额", "39.2%（2025）", "< 35%", "护城河预警，下调目标 PE"),
        ("海外收入占比", "31.5%（2026H1）", "< 25%", "地缘政治受损，下调长期增速"),
        ("经营现金流 / 净利", "0.96（2026 9M）", "< 0.7", "检查应收/存货/预付款"),
        ("存货 / 营收", "22.3%（2025）", "> 25%", "减值风险，下调利润"),
        ("2027E 一致预期 EPS", "23.57", "下修 > 15%", "重估 PE 基准"),
        ("回购执行", "53.6 亿（至 10/31）", "< 100 亿（12 个月）", "股东回报低于预期"),
    ]
    for i, row in enumerate(triggers):
        r = 21 + i
        cell(ws, r, 1, row[0], align="left", bold=True)
        cell(ws, r, 2, row[1], align="center")
        cell(ws, r, 3, row[2], align="center", color=RED)
        block(ws, r, 4, r, 7, row[3], size=8.5, color=MUTED)
        ws.row_dimensions[r].height = 24

    section(ws, 30, "四、悲观情景测算", 7)
    block(ws, 31, 1, 35, 7,
          f"若 2027 年 EPS 降至 17.50 元（较一致预期 −26%）、目标 PE 12.5 倍，PE 价值 {D.PE_BEAR_V:.0f} 元；"
          f"DCF 用 FCFF 435 亿、增速 5%、WACC 8.6%，价值 {D.DCF_BEAR:.0f} 元；综合 {D.BLEND_BEAR:.0f} 元，"
          f"较现价 {D.BLEND_BEAR/D.PRICE-1:+.0%}。现价 265.94 元高于悲观价值约 21%，说明市场并未定价“永久性衰退”。",
          size=9.5, fill=RED_FILL, height=80)
    note(ws, 37, "触发条件每季度复核；任一核心指标触发，回到本报告重估。不构成投资建议。", 7)
    finish(ws, 7, paper=A4)
    ws.print_area = "A1:G37"


# ---------------------------------------------------------------- 9 数据与来源
def sheet_sources(wb):
    ws = wb.create_sheet("数据与来源")
    title(ws, "数据与来源 · 证据账本", 7)
    subtitle(ws, f"取数日 {D.DATE}｜价格日 {D.PRICE_NOTE}｜财报截止 2026-09-30", 7)
    note(ws, 3, "状态：硬数据=公司公告/交易所；软数据=媒体/第三方；假设=本报告模型；待核=尚未取得原始文件。", 7)

    header(ws, 5, ["项目", "数值", "来源", "日期", "状态", "", ""], [24, 34, 50, 14, 10, 2, 2])
    sources = [
        ("2026 三季报营收", "4,421.37 亿元（+56.19%）", "宁德时代 2026 年三季报 / 上海证券报", "2026-10-20", "硬数据"),
        ("2026 三季报归母净利", "645.30 亿元（+31.60%）", "同上", "2026-10-20", "硬数据"),
        ("2026Q3 单季营收 / 净利", "1,652.21 亿 / 212.46 亿", "同上", "2026-10-20", "硬数据"),
        ("2025 年报营收 / 净利", "4,237.02 亿 / 722.01 亿", "宁德时代 2025 年年度报告", "2026-03-09", "硬数据"),
        ("2025 电池销量 / 份额", "661GWh / 39.2%", "SNE Research、公司年报", "2026-03", "硬数据"),
        ("2026Q3 资产负债", "总资产 11,831.7 亿；归母权益 3,868.8 亿", "2026 年三季报", "2026-09-30", "硬数据"),
        ("净现金", "2,426.7 亿元", "货币资金 3,698.1 + 交易性金融 627.8 − 有息负债 1,899.2", "2026-09-30", "计算"),
        ("2025 分红", "DPS 7.964 元；合计 361 亿；派息率 50%", "2025 年度利润分配公告", "2026-03-10", "硬数据"),
        ("2025 分红拆解", "中期 1.007 + 普通 2.178 + 特别 4.779", "公司公告 / 媒体核对", "2026-03", "硬数据"),
        ("回购方案", "200–400 亿元，上限 573 元，全部注销", "公司公告（2026-07-24）", "2026-07-24", "硬数据"),
        ("回购执行", "约 53.6 亿元（至 2026-10-31）", "公司回购进展公告 / 市场报道", "2026-10-31", "待核"),
        ("消费税", "2026-09 起 2%，2027-09 起 4%", "财政部/海关总署/税务总局 2026 年第 20 号公告", "2026", "硬数据"),
        ("出口退税", "2026-04 起 9%→6%，2027-01 起取消", "2026 年第 2 号公告", "2026", "硬数据"),
        ("2026E 净利", "906 亿元（EPS 19.58）", "机构一致预期（Eastmoney）", "2026-11", "软数据"),
        ("2027E EPS 一致预期", "23.57 元", "机构一致预期（Eastmoney）", "2026-11", "软数据"),
        ("2027E EPS 本报告", "22.50 元（悲观 17.50 / 乐观 25.00）", "本报告假设", "2026-11-05", "假设"),
        ("DCF 参数", "FCFF 490 亿、WACC 7.8%、g 2.5%", "本报告假设", "2026-11-05", "假设"),
    ]
    for i, row in enumerate(sources):
        r = 6 + i
        cell(ws, r, 1, row[0], align="left", bold=True)
        block(ws, r, 2, r, 2, row[1], size=8.5)
        block(ws, r, 3, r, 3, row[2], size=8.5, color=MUTED)
        cell(ws, r, 4, row[3], align="center")
        st = row[4]
        cell(ws, r, 5, st, align="center", bold=True,
             color=(GREEN if st == "硬数据" else (GOLD if st in ("软数据", "计算") else MUTED)))
        ws.row_dimensions[r].height = 28

    section(ws, 25, "主要链接", 7)
    links = [
        ("三季报快讯", "https://www.cnstock.com/commonDetail/805599"),
        ("2025 年报", "https://www.catl.com/news/9654.html"),
        ("回购方案", "https://www.stcn.com/article/detail/4041042.html"),
        ("税费政策", "https://egs.stcn.com/news/detail/2352186.html"),
        ("Q3 毛利率", "https://businesstimescn.com/articles/630600.html"),
    ]
    for i, (a, b) in enumerate(links):
        r = 26 + i
        cell(ws, r, 1, a, align="left", bold=True)
        block(ws, r, 2, r, 7, b, size=8.5, color="1A73E8")

    note(ws, 33, "本报告仅用于研究资料归档，不构成任何投资建议。价格、财报与政策可能变化，使用前请核对原始公告。", 7)
    finish(ws, 7, paper=A4)
    ws.print_area = "A1:G33"


def main():
    wb = Workbook()
    sheet_one(wb)
    sheet_conclusion(wb)
    sheet_valuation(wb)
    sheet_business(wb)
    sheet_financials(wb)
    sheet_dividend(wb)
    sheet_assumptions(wb)
    sheet_risk(wb)
    sheet_sources(wb)
    wb.save(XLSX)
    print("saved", XLSX)


if __name__ == "__main__":
    main()
