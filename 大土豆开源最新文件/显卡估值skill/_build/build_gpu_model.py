# -*- coding: utf-8 -*-
"""Build GPU valuation workbook (2026-11-05)."""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "输出" / "显卡估值表-2026-11-05.xlsx"

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

CARDS = [
    ("RTX 5070", 12, 4599, 6999, 7899, 100, "不买；等 ≤5,310，理想 ≤3,920"),
    ("RTX 5070 Ti", 16, 6299, 9699, 11999, 125, "不买；等 ≤7,650，理想 ≤5,650"),
    ("RTX 5080", 16, 8299, 12199, 15999, 155, "不买；等 ≤10,080，理想 ≤7,450"),
    ("RX 9070 GRE", 12, 4199, 3900, 4700, 88, "3,900–4,000 可买；4,200 公允；≥4,800 不买"),
    ("RX 9070", 16, 4499, 5200, 5800, 120, "观望；≤4,750 可买，≥5,460 不买"),
    ("RX 9070 XT", 16, 4999, 5700, 6900, 135, "5,700 可接受；≤5,300 可买；≥6,070 不买"),
]


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


def sheet_table(wb):
    ws = wb.active
    ws.title = "估值表"
    title(ws, "显卡估值表 · 2026-11-05", 13)
    subtitle(ws, "单位：人民币元；当前价为渠道/电商参考价，非京东自营实时价；蓝色为输入，黑色为公式", 13)
    widths(ws, [16, 8, 11, 11, 11, 11, 9, 11, 11, 11, 11, 11, 34])
    header(ws, 4, ["型号", "显存", "首发价", "当前低价", "当前高价", "当前中值",
                   "性能指数", "公允价", "可买价", "上限价", "当前/公允", "公允元/点", "结论"])
    for i, (name, vram, msrp, low, high, perf, concl) in enumerate(CARDS):
        r = 5 + i
        cell(ws, r, 1, name, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 2, vram, fmt="0", align="center")
        cell(ws, r, 3, msrp, fmt="#,##0", color="1A73E8", fill=INPUT_FILL)
        cell(ws, r, 4, low, fmt="#,##0", color="1A73E8", fill=INPUT_FILL)
        cell(ws, r, 5, high, fmt="#,##0", color="1A73E8", fill=INPUT_FILL)
        cell(ws, r, 6, f"=(D{r}+E{r})/2", fmt="#,##0")
        cell(ws, r, 7, perf, fmt="0", align="center")
        cell(ws, r, 8, f"=C{r}*假设!$B$6*假设!$B$7*IF(B{r}=12,假设!$B$8,假设!$B$9)", fmt="#,##0", bold=True)
        cell(ws, r, 9, f"=H{r}*假设!$B$10", fmt="#,##0")
        cell(ws, r, 10, f"=H{r}*假设!$B$11", fmt="#,##0")
        cell(ws, r, 11, f"=F{r}/H{r}-1", fmt="0.0%", bold=True)
        cell(ws, r, 12, f"=H{r}/G{r}", fmt="0.0")
        cell(ws, r, 13, concl, align="left", size=8.8, wrap=True)
        prem = (low + high) / 2 / (msrp * 1.20 * 0.88 * (0.95 if vram == 12 else 1.0)) - 1
        fill = GREEN_FILL if prem <= 0.05 else (GOLD_FILL if prem <= 0.15 else RED_FILL)
        ws.cell(row=r, column=11).fill = fill
        ws.row_dimensions[r].height = 38
    block(ws, 12, 1, 15, 13,
          "读法：当前价 ≤ 可买价 = 好价；可买价~公允价 = 公允偏低；公允价~上限价 = 偏贵；> 上限价 = 不买（除非刚需/专业需求）。"
          "公允价 = 首发价 × 内存因子 × 年龄因子 × 显存寿命因子；参数在「假设」页，可改。",
          size=9, color=MUTED, fill=NOTE_FILL, height=54)
    block(ws, 16, 1, 19, 13,
          "2026-11 快照：N 卡当前价约比公允高 60%（5070/5070Ti/5080 均在 +60% 附近）；A 卡溢价小得多："
          "9070 GRE 约 +2%，9070 约 +16%，9070 XT 约 +19%。现在不是买 N 卡的时候；A 卡只有 9070 GRE 低价可买，9070 XT 5700 附近可接受但不算便宜。",
          size=10, color=GREEN, fill=GREEN_FILL, height=54)
    finish(ws)
    ws.print_area = "A1:M19"


def sheet_assumptions(wb):
    ws = wb.create_sheet("假设")
    title(ws, "估值假设 · 可改参数", 6)
    subtitle(ws, "改蓝色单元格，估值表会自动重算；2026-11 参数按内存短缺环境设定", 6)
    widths(ws, [24, 14, 50, 3, 3, 3])
    section(ws, 4, "一、核心参数", 6)
    header(ws, 5, ["参数", "取值", "说明", "", "", ""])
    rows = [
        ("内存因子", 1.20, "GDDR6/GDDR7 涨价向显卡传导；短缺缓解后下调"),
        ("年龄因子", 0.88, "首发约 20 个月，按年 7% 折旧"),
        ("12GB 显存寿命因子", 0.95, "2027–2028 更早遇到 4K/纹理瓶颈"),
        ("16GB 显存寿命因子", 1.00, "16GB 作为基准，不额外折扣"),
        ("可买折扣", 0.85, "15% 安全边际"),
        ("上限溢价", 1.15, "高于公允 15% 不买"),
    ]
    for i, (a, b, c) in enumerate(rows):
        r = 6 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 2, b, fmt="0.00", bold=True, color="1A73E8", fill=INPUT_FILL)
        block(ws, r, 3, r, 6, c, size=9, color=MUTED)
    section(ws, 13, "二、性能指数（1440p 光栅，RTX 5070 = 100）", 6)
    header(ws, 14, ["型号", "指数", "定位", "", "", ""])
    perf = [
        ("RTX 5070", 100, "1440p 高刷"),
        ("RTX 5070 Ti", 125, "1440p/4K 入门"),
        ("RTX 5080", 155, "4K"),
        ("RX 9070 GRE", 88, "1440p 性价比"),
        ("RX 9070", 120, "1440p/4K"),
        ("RX 9070 XT", 135, "4K 性价比"),
    ]
    for i, (a, b, c) in enumerate(perf):
        r = 15 + i
        cell(ws, r, 1, a, align="left", bold=True)
        cell(ws, r, 2, b, fmt="0", align="center")
        block(ws, r, 3, r, 6, c, size=9, color=MUTED)
    block(ws, 22, 1, 25, 6,
          "指数用于横向比较“元/性能点”，不是绝对帧数；实际帧数受 CPU、游戏、驱动影响。"
          "参数不是永久值：内存暴涨/回落、下一代发布前后，先改内存因子，再改年龄因子。",
          size=9, color=MUTED, fill=NOTE_FILL, height=48)
    finish(ws, freeze="A4")
    ws.print_area = "A1:F25"


def sheet_tracking(wb):
    ws = wb.create_sheet("价格跟踪")
    title(ws, "价格跟踪 · 手动记录", 6)
    subtitle(ws, "建议每周记录一次；低于可买价时标黄，高于上限价时标红", 6)
    widths(ws, [14, 18, 12, 12, 26, 30])
    header(ws, 4, ["日期", "型号", "低价", "高价", "来源", "备注"])
    for r in range(5, 25):
        for c in range(1, 7):
            cell(ws, r, c, None, align="center" if c in (1, 3, 4) else "left")
    finish(ws)
    ws.print_area = "A1:F24"


def sheet_method(wb):
    ws = wb.create_sheet("方法与来源")
    title(ws, "方法与来源", 6)
    subtitle(ws, "公允价是模型估算，不是价格预测；下单前以实时页面为准", 6)
    widths(ws, [20, 80, 3, 3, 3, 3])
    block(ws, 4, 1, 12, 2,
          "一、公式\n"
          "公允价 = 首发价 × 内存因子 × 年龄因子 × 显存寿命因子\n"
          "可买价 = 公允价 × 0.85；上限价 = 公允价 × 1.15\n\n"
          "二、为什么用首发价做锚\n"
          "首发价反映厂商对性能定位、BOM 和竞争的定价；当前价含缺货溢价、渠道炒作和 AIC 调价。"
          "直接用当前价估值，会把泡沫当价值。\n\n"
          "三、参数含义\n"
          "内存因子 1.20：GDDR6/GDDR7 涨价；年龄因子 0.88：约 20 个月折旧；"
          "12GB 显存因子 0.95：2027–2028 更早遇到 4K/纹理瓶颈；16GB 为 1.00。",
          size=9.5, color=INK, height=150)
    block(ws, 14, 1, 21, 2,
          "四、数据来源\n"
          "价格：什么值得买 11 月显卡行情、博板堂/今日头条渠道报价、ZOL、AMD Q4 建议价报道。\n"
          "性能：TechPowerUp、Tom’s Hardware、超能网、极客湾；统一为 1440p 光栅相对指数。\n"
          "迭代：超能网 RTX 50 SUPER 报道、ITHome/17173、AMD RDNA 5 报道。\n"
          "内存：EET-China、TrendForce/Counterpoint。\n\n"
          "五、局限\n"
          "价格波动大；品牌/散热/保修/地区差异会影响成交；公允价不预测短期涨跌。"
          "内存周期或下一代发布时间变化时，应重算参数。",
          size=9.5, color=MUTED, height=120)
    finish(ws, freeze="A4")
    ws.print_area = "A1:F21"


def main():
    wb = Workbook()
    sheet_table(wb)
    sheet_assumptions(wb)
    sheet_tracking(wb)
    sheet_method(wb)
    wb.save(OUT)
    print("saved", OUT.name)


if __name__ == "__main__":
    main()
