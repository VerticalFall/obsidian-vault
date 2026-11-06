# -*- coding: utf-8 -*-
"""Build SpaceX (SPCX) SOTP workbook (2026-11-05)."""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / "输出" / "美股" / "SPCX-2026-11-05" / "SPCX-估值模型-2026-11-05.xlsx"

GREEN = "2F6B4F"; GOLD = "C9A227"; RED = "B23A2E"
INK = "1F2933"; MUTED = "5B6770"; BORDER = "D9D2C5"
TITLE_FILL = PatternFill("solid", fgColor=GREEN)
SECTION_FILL = PatternFill("solid", fgColor="E8EFE9")
HEADER_FILL = PatternFill("solid", fgColor="EFE8D8")
NOTE_FILL = PatternFill("solid", fgColor="FBF7EA")
INPUT_FILL = PatternFill("solid", fgColor="F2F7FB")
RED_FILL = PatternFill("solid", fgColor="F8E5E1")
GREEN_FILL = PatternFill("solid", fgColor="E3EFE7")
GOLD_FILL = PatternFill("solid", fgColor="F7EFD2")
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


def header(ws, row, values):
    for j, v in enumerate(values, 1):
        c = ws.cell(row=row, column=j, value=v)
        c.font = Font(name=FONT, size=9.5, bold=True, color="5B4A3A")
        c.fill = HEADER_FILL
        c.border = BORDER_ALL
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 30


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


def widths(ws, values):
    for j, w in enumerate(values, 1):
        ws.column_dimensions[get_column_letter(j)].width = w


def finish(ws, freeze="A5"):
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = freeze
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_options.horizontalCentered = True
    ws.sheet_properties.tabColor = GREEN
    ws.page_setup.paperSize = 9


def sheet_sotp(wb):
    ws = wb.active
    ws.title = "SOTP"
    title(ws, "SpaceX SPCX · 分部估值（SOTP）", 6)
    subtitle(ws, "单位：十亿美元；现价 135.92 美元；蓝色为输入，黑色为公式；数据截至 2026-11-04", 6)
    widths(ws, [22, 30, 14, 14, 14, 34])
    header(ws, 4, ["分部", "估值指标", "悲观", "基准", "乐观", "说明"])
    rows = [
        ("Starlink", "2026E EBITDA × 倍数", "=假设!$B$6*假设!B7", "=假设!$B$6*假设!C7", "=假设!$B$6*假设!D7", "18x / 30x / 40x"),
        ("Space", "2026E 收入 × 倍数", "=假设!$B$8*假设!B9", "=假设!$B$8*假设!C9", "=假设!$B$8*假设!D9", "4x / 8x / 12x"),
        ("AI", "2026E 收入 × 倍数", "=假设!$B$10*假设!B11", "=假设!$B$10*假设!C11", "=假设!$B$10*假设!D11", "4x / 11x / 18x"),
        ("Starship 期权", "概率加权", "=假设!B12", "=假设!C12", "=假设!D12", "0 / 130 / 300"),
        ("净债务", "扣除", "=-假设!$B$13", "=-假设!$B$13", "=-假设!$B$13", "长期债务约 290 亿，净债务估算 150 亿"),
    ]
    for i, (a, b, c, d, e, note_) in enumerate(rows):
        r = 5 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 2, b, align="left", size=9, color=MUTED)
        cell(ws, r, 3, c, fmt="#,##0", bold=True)
        cell(ws, r, 4, d, fmt="#,##0", bold=True)
        cell(ws, r, 5, e, fmt="#,##0", bold=True)
        cell(ws, r, 6, note_, align="left", size=9, color=MUTED)
    # total
    r = 10
    cell(ws, r, 1, "股权价值", align="left", bold=True, fill=GOLD_FILL)
    cell(ws, r, 2, "合计", align="left", size=9, color=MUTED, fill=GOLD_FILL)
    for col in (3, 4, 5):
        cell(ws, r, col, f"=SUM({get_column_letter(col)}5:{get_column_letter(col)}9)", fmt="#,##0", bold=True, fill=GOLD_FILL)
    cell(ws, r, 6, "十亿美元", align="left", size=9, color=MUTED, fill=GOLD_FILL)
    # per share
    r = 11
    cell(ws, r, 1, "每股价值", align="left", bold=True)
    cell(ws, r, 2, "股权价值 / 13.58 亿股", align="left", size=9, color=MUTED)
    for col in (3, 4, 5):
        cell(ws, r, col, f"={get_column_letter(col)}10/假设!$B$17", fmt="0.00", bold=True)
    cell(ws, r, 6, "美元/股", align="left", size=9, color=MUTED)
    # current
    r = 12
    cell(ws, r, 1, "现价", align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
    cell(ws, r, 2, "2026-11-04 收盘", align="left", size=9, color=MUTED)
    cell(ws, r, 3, "=假设!$B$18", fmt="0.00", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
    cell(ws, r, 4, "=假设!$B$18", fmt="0.00", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
    cell(ws, r, 5, "=假设!$B$18", fmt="0.00", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
    cell(ws, r, 6, "美元/股", align="left", size=9, color=MUTED)
    # premium
    r = 13
    cell(ws, r, 1, "现价 / SOTP", align="left", bold=True, fill=RED_FILL)
    cell(ws, r, 2, "溢价（正=现价高）", align="left", size=9, color=MUTED, fill=RED_FILL)
    for col in (3, 4, 5):
        cell(ws, r, col, f"=C12/{get_column_letter(col)}11-1", fmt="0.0%", bold=True, fill=RED_FILL)
    cell(ws, r, 6, "现价高于基准约 105%，高于乐观约 29%", align="left", size=9, color=MUTED, fill=RED_FILL)
    # reverse
    r = 15
    cell(ws, r, 1, "反向 SOTP", align="left", bold=True, fill=GOLD_FILL)
    cell(ws, r, 2, "现价隐含的 AI 倍数", align="left", size=9, color=MUTED, fill=GOLD_FILL)
    cell(ws, r, 3, "=(假设!$B$19-(假设!$B$6*假设!D7+假设!$B$8*假设!D9+假设!D12-假设!$B$13))/假设!$B$10", fmt="0.0x", bold=True, fill=GOLD_FILL)
    cell(ws, r, 4, "Starlink 40x、Starship 300、Space 12x", align="left", size=9, color=MUTED, fill=GOLD_FILL)
    r = 16
    cell(ws, r, 1, "反向 SOTP", align="left", bold=True)
    cell(ws, r, 2, "现价隐含的 Starship 价值", align="left", size=9, color=MUTED)
    cell(ws, r, 3, "=假设!$B$19-(假设!$B$6*假设!D7+假设!$B$8*假设!D9+假设!$B$10*假设!D11-假设!$B$13)", fmt="#,##0", bold=True)
    cell(ws, r, 4, "十亿美元；AI 18x", align="left", size=9, color=MUTED)
    block(ws, 18, 1, 21, 6,
          "读法：SOTP 是“当前可见现金流 + 有限期权价值”的估值，不是对 AI/Starship 成功的信仰测试。"
          "现价高于基准约 105%，意味着市场把 AI 和 Starship 的成功同时定价；若你接受超级牛案，现价可以成立，但没有安全边际。",
          size=9, color=MUTED, fill=NOTE_FILL, height=54)
    finish(ws)
    ws.print_area = "A1:F21"


def sheet_assumptions(wb):
    ws = wb.create_sheet("假设")
    title(ws, "关键假设 · 可改参数", 6)
    subtitle(ws, "改蓝色单元格，SOTP 自动重算；单位：十亿美元、十亿股、美元", 6)
    widths(ws, [30, 14, 14, 14, 40, 3])
    section(ws, 4, "一、分部假设", 6)
    header(ws, 5, ["假设", "悲观", "基准", "乐观", "说明", ""])
    rows = [
        ("Starlink 2026E EBITDA", 14.0, 14.0, 14.0, "Quilty 预测 2026E EBITDA 约 140 亿美元"),
        ("Starlink 倍数", 18, 30, 40, "EBITDA 倍数；增长 30–50%"),
        ("Space 2026E 收入", 7.0, 7.0, 7.0, "Q3 年化约 72 亿美元"),
        ("Space 倍数", 4, 8, 12, "收入倍数；低毛利"),
        ("AI 2026E 收入", 28.0, 28.0, 28.0, "Q3 年化约 300 亿美元，取保守"),
        ("AI 倍数", 4, 11, 18, "收入倍数；利润率低、capex 高"),
        ("Starship 期权价值", 0, 130, 300, "概率加权；0 = 失败，300 = 成功"),
        ("净债务", 15.0, 15.0, 15.0, "长期债务约 290 亿，净债务估算"),
    ]
    for i, (a, b, c, d, e) in enumerate(rows):
        r = 6 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 2, b, fmt="0.0" if isinstance(b, float) else "0", bold=True, color="1A73E8", fill=INPUT_FILL)
        cell(ws, r, 3, c, fmt="0.0" if isinstance(c, float) else "0", bold=True, color="1A73E8", fill=INPUT_FILL)
        cell(ws, r, 4, d, fmt="0.0" if isinstance(d, float) else "0", bold=True, color="1A73E8", fill=INPUT_FILL)
        block(ws, r, 5, r, 6, e, size=9, color=MUTED)
    section(ws, 15, "二、股本与价格", 6)
    header(ws, 16, ["项目", "数值", "说明", "", "", ""])
    more = [
        ("股本（十亿股）", 13.58, "约 13.58 亿股"),
        ("现价（美元）", 135.92, "2026-11-04 收盘"),
        ("市值（十亿美元）", 1846, "约 1.846 万亿美元"),
    ]
    for i, (a, b, c) in enumerate(more):
        r = 17 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 2, b, fmt="0.00" if isinstance(b, float) else "#,##0", bold=True, color="1A73E8", fill=INPUT_FILL)
        block(ws, r, 3, r, 6, c, size=9, color=MUTED)
    block(ws, 21, 1, 24, 6,
          "参数不是永久值：AI 收入/利润率、Starlink ARPU、Starship 进度变化时，先改收入与倍数，再改期权价值。"
          "净债务为估算，实际以 10-Q 为准。",
          size=9, color=MUTED, fill=NOTE_FILL, height=48)
    finish(ws, freeze="A4")
    ws.print_area = "A1:F24"


def sheet_financials(wb):
    ws = wb.create_sheet("财务")
    title(ws, "财务概览 · 2025 / 2026Q1 / 2026Q3", 6)
    subtitle(ws, "单位：十亿美元；2026Q3 为合并 xAI 后第一个完整季度", 6)
    widths(ws, [24, 16, 16, 16, 30, 3])
    header(ws, 4, ["项目", "2025", "2026Q1", "2026Q3", "说明", ""])
    rows = [
        ("收入", 18.7, 4.69, 14.58, "Q3 同比 +161%"),
        ("经营利润", -2.6, None, 2.8, "2025 经营亏损"),
        ("净利润", -4.9, -4.28, 4.4, "Q3 含一次性/会计因素"),
        ("调整后 EBITDA", None, None, 8.8, "Q3"),
        ("资本开支", 20.7, 10.1, 20.0, "Q3 约 200 亿，主要 AI"),
        ("Starlink 收入", 11.4, 3.26, 5.25, "Q3 +69%"),
        ("Starlink 用户（百万）", None, 10.3, 13.6, "Q3 净增 160 万"),
        ("AI 收入", 3.2, 0.818, 7.56, "xAI；Q3 +830%"),
        ("EPS（美元）", None, None, 0.35, "Q3"),
    ]
    for i, (a, b, c, d, e) in enumerate(rows):
        r = 5 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        for col, v in ((2, b), (3, c), (4, d)):
            if v is None:
                cell(ws, r, col, "—", align="center", color=MUTED)
            else:
                cell(ws, r, col, v, fmt="0.00" if isinstance(v, float) else "0.0", bold=True)
        block(ws, r, 5, r, 6, e, size=9, color=MUTED)
    block(ws, 16, 1, 20, 6,
          "关键读数：Starlink 是利润引擎（Q3 经营利润 23.7 亿，占集团约 85%）；AI 收入已超过 Starlink，但经营利润率仅 5.7%、"
          "季度 capex 164 亿；集团 2026E FCF 约 -514 亿，仍靠债务/股权融资。",
          size=9.5, color=INK, fill=NOTE_FILL, height=60)
    finish(ws)
    ws.print_area = "A1:F20"


def sheet_sources(wb):
    ws = wb.create_sheet("来源")
    title(ws, "数据与来源", 6)
    subtitle(ws, "报告日 2026-11-05；价格日 2026-11-04 收盘", 6)
    widths(ws, [22, 80, 3, 3, 3, 3])
    block(ws, 4, 1, 14, 2,
          "S-1（2026-05-20）：2025 收入 187 亿美元、净亏 49 亿、Starlink 收入 114 亿、xAI 亏损 63.6 亿。\n"
          "2026Q1 业绩：收入 46.9 亿、净亏 42.8 亿；xAI 经营亏损 24.7 亿。\n"
          "2026Q3 业绩（2026-10-20）：收入 145.8 亿、经营利润 28 亿、净利 44 亿、EPS 0.35；Starlink 收入 52.5 亿、经营利润 23.7 亿；AI 收入 75.6 亿、经营利润 4.31 亿；capex 约 200 亿。\n"
          "2026E 一致预期：收入约 451 亿、净利约 31 亿、FCF 约 -514 亿、经营现金流约 218 亿。\n"
          "价格：2026-11-04 收盘 135.92 美元，市值 1.846 万亿美元，约 13.58 亿股。\n"
          "Starship：Flight 14 首次轨道（2026-09-28）；FAA 25/44 次发射上限；NASA HLS 合同约 29 亿美元（含选项约 40–44 亿）。\n"
          "EchoStar 频谱：约 170 亿美元交易，Direct-to-Cell。",
          size=9, color=INK, height=180)
    block(ws, 16, 1, 20, 2,
          "免责声明：本模型为研究记录，不构成投资建议。SpaceX 上市时间短，AI 分部与 Starship 不确定性高；"
          "估值对假设敏感，净债务为估算，实际以公司 10-Q/10-K 为准。",
          size=9, color=MUTED, fill=NOTE_FILL, height=50)
    finish(ws, freeze="A4")
    ws.print_area = "A1:F20"


def main():
    wb = Workbook()
    sheet_sotp(wb)
    sheet_assumptions(wb)
    sheet_financials(wb)
    sheet_sources(wb)
    wb.save(OUT)
    print("saved", OUT.name)


if __name__ == "__main__":
    main()
