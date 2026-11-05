# -*- coding: utf-8 -*-
"""Build Xiaomi 1810.HK Buffett-framework Excel model (9 sheets) — layout v2."""
import sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import xiaomi_data as D

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / "输出" / "港股" / f"1810.HK-{D.DATE}"
OUT.mkdir(parents=True, exist_ok=True)
XLSX = OUT / f"1810.HK-估值模型-{D.DATE}.xlsx"

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


def widths(ws, values):
    for j, w in enumerate(values, 1):
        ws.column_dimensions[get_column_letter(j)].width = w


def header(ws, row, values):
    """values: list of (col, text, span)."""
    for col, text, span in values:
        if span > 1:
            ws.merge_cells(start_row=row, start_column=col, end_row=row,
                           end_column=col + span - 1)
        c = ws.cell(row=row, column=col, value=text)
        c.font = Font(name=FONT_CN, size=9.5, bold=True, color="5B4A3A")
        c.fill = HEADER_FILL
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        for j in range(col, col + span):
            ws.cell(row=row, column=j).border = BORDER_ALL
    ws.row_dimensions[row].height = 28


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


def block(ws, r1, c1, r2, c2, text, bold=False, color=INK, fill=None, size=10, height=None):
    ws.merge_cells(start_row=r1, start_column=c1, end_row=r2, end_column=c2)
    c = ws.cell(row=r1, column=c1, value=text)
    c.font = Font(name=FONT_CN, size=size, bold=bold, color=color)
    c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True, indent=1)
    if fill:
        c.fill = fill
    if height:
        ws.row_dimensions[r1].height = height


def finish(ws, ncols=8, freeze="A5", paper=None):
    ws.sheet_view.showGridLines = False
    if freeze:
        ws.freeze_panes = freeze
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_options.horizontalCentered = True
    ws.sheet_properties.tabColor = GREEN
    if paper:
        ws.page_setup.paperSize = paper


A3 = 8
A4 = 9


def hkd(v):
    return v / D.FX


# ---------------------------------------------------------------- 1 一图流
def sheet_one(wb):
    ws = wb.active
    ws.title = "一图流"
    widths(ws, [20, 14, 26, 10, 20, 14, 38, 3])
    title(ws, "小米集团 1810.HK · 巴菲特框架估值", 8)
    subtitle(ws, f"报告日 {D.DATE}｜价格日 {D.PRICE_NOTE}｜单位：人民币亿元、元/股（另注港元）｜蓝色=输入，黑色=公式", 8)
    note(ws, 3, "本模型只用于研究记录，不构成投资建议。事实、计算、假设与判断分开标注；来源见「数据与来源」页。", 8)

    section(ws, 5, "一句话结论", 8)
    block(ws, 6, 1, 6, 8,
          f"好生意，合理价格，但没有安全边际。手机×AIoT 提供现金流，汽车是第二增长曲线；"
          f"2026 年利润处于低谷（经调整净利 {D.NP_ADJ_2026E:.0f} 亿元，同比约 -36%），"
          f"现价 HK${D.PRICE_HKD:.2f}（¥{D.PRICE:.2f}）对应 2026E PE {D.MARKET_CAP/D.NP_ADJ_2026E:.1f} 倍、"
          f"2027E PE {D.MARKET_CAP/D.NP_ADJ_2027E_BASE:.1f} 倍。DCF HK${hkd(D.DCF_BASE):.2f}、"
          f"PE HK${hkd(D.PE_BASE_V):.2f}，综合基准 HK${hkd(D.BLEND_BASE):.2f}，"
          f"现价仅低 {D.MOS*100:.1f}%。20% 安全边际价 HK${hkd(D.MOS20_PRICE):.2f}，现价仍高出 "
          f"{(D.PRICE/D.MOS20_PRICE-1)*100:.0f}%。",
          fill=GOLD_FILL, size=10.5, height=64)

    section(ws, 8, "关键读数", 8)
    header(ws, 9, [(1, "指标", 1), (2, "数值", 1), (3, "说明", 1),
                   (5, "指标", 1), (6, "数值", 1), (7, "说明", 1)])
    rows = [
        ("现价（港元）", D.PRICE_HKD, "港元/股", "2026E PE", D.MARKET_CAP / D.NP_ADJ_2026E, "倍"),
        ("现价（人民币）", D.PRICE, "元/股", "2027E PE", D.MARKET_CAP / D.NP_ADJ_2027E_BASE, "倍"),
        ("总市值（港元）", D.MARKET_CAP_HKD, "亿港元", "TTM PE", D.TTM_PE, "倍"),
        ("总市值（人民币）", D.MARKET_CAP, "亿元", "PB", D.PRICE / D.BPS, "倍"),
        ("净现金", D.NET_CASH, "亿元", "2026E 股息率", 0.0, "%"),
        ("综合基准（港元）", hkd(D.BLEND_BASE), "港元/股", "评级", "合理", ""),
    ]
    for i, (l1, v1, u1, l2, v2, u2) in enumerate(rows):
        r = 10 + i
        cell(ws, r, 1, l1, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        fmt1 = "0.00%" if u1 == "%" else ("#,##0" if abs(v1) > 1000 else "0.00")
        cell(ws, r, 2, v1, fmt=fmt1, bold=True)
        cell(ws, r, 3, u1, align="left", color=MUTED)
        cell(ws, r, 5, l2, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        if isinstance(v2, str):
            cell(ws, r, 6, v2, bold=True, color=GOLD, align="center")
        else:
            fmt2 = "0.0%" if u2 == "%" else ("#,##0" if abs(v2) > 1000 else "0.0")
            cell(ws, r, 6, v2, fmt=fmt2, bold=True)
        cell(ws, r, 7, u2, align="left", color=MUTED)
    cell(ws, 15, 6, "合理", bold=True, color=GOLD, align="center", fill=GOLD_FILL)

    section(ws, 17, "三情景每股价值（港元）", 8)
    header(ws, 18, [(1, "情景", 1), (2, "DCF", 1), (3, "PE", 1), (4, "综合", 1),
                    (5, "现价", 1), (6, "综合较现价", 1), (7, "核心假设", 2)])
    scen = [
        ("悲观", hkd(D.DCF_BEAR), hkd(D.PE_BEAR_V), hkd(D.BLEND_BEAR),
         "存储涨价；汽车价格战；2027 净利 280 亿"),
        ("基准", hkd(D.DCF_BASE), hkd(D.PE_BASE_V), hkd(D.BLEND_BASE),
         "2027 净利 350 亿；汽车减亏；手机毛利修复"),
        ("乐观", hkd(D.DCF_BULL), hkd(D.PE_BULL_V), hkd(D.BLEND_BULL),
         "2027 净利 420 亿；汽车扭亏；AI 变现超预期"),
    ]
    for i, (name, dcf, pe, blend, cond) in enumerate(scen):
        r = 19 + i
        fill = GOLD_FILL if name == "基准" else None
        cell(ws, r, 1, name, align="center", bold=True, fill=fill)
        cell(ws, r, 2, dcf, fmt="0.00", bold=True, fill=fill)
        cell(ws, r, 3, pe, fmt="0.00", bold=True, fill=fill)
        cell(ws, r, 4, blend, fmt="0.00", bold=True, fill=fill)
        cell(ws, r, 5, D.PRICE_HKD, fmt="0.00", fill=fill)
        cell(ws, r, 6, blend / D.PRICE_HKD - 1, fmt="0.0%",
             color=(GREEN if blend > D.PRICE_HKD else RED), bold=True, fill=fill)
        block(ws, r, 7, r, 8, cond, size=8.5, color=MUTED, fill=fill)
        ws.row_dimensions[r].height = 26
    note(ws, 22, "综合 = DCF 50% + PE 50%。PE 法使用 2027E EPS（基准 1.354 元）× 目标 PE 22 倍；港元按 0.85601 折算。", 8)

    section(ws, 24, "三条判断", 8)
    block(ws, 25, 1, 30, 2,
          "好生意：全球手机份额 13.3%、IoT 生态与互联网服务提供高毛利现金流；2025 年经调整净利 392 亿元、"
          "经营现金流 341 亿元。护城河来自品牌、生态与成本效率，但手机是成熟品类，汽车仍在投入期",
          fill=GREEN_FILL, size=9, height=90)
    block(ws, 25, 3, 30, 5,
          f"合理价格：现价 HK${D.PRICE_HKD:.2f}，2026E PE {D.MARKET_CAP/D.NP_ADJ_2026E:.1f} 倍、"
          f"2027E PE {D.MARKET_CAP/D.NP_ADJ_2027E_BASE:.1f} 倍；综合基准 HK${hkd(D.BLEND_BASE):.2f}，"
          f"仅高 {D.MOS*100:.1f}%。便宜来自利润低谷与汽车亏损，不是来自生意变差；但也没有 20% 安全边际",
          fill=GOLD_FILL, size=9, height=90)
    block(ws, 25, 6, 30, 8,
          "主要风险：① 存储芯片涨价压制手机毛利率；② 汽车价格战与澎程放量不及预期；③ AI 投入回报低；"
          "④ 股权激励稀释抵消回购；⑤ 印度/欧洲地缘与监管。任何一条恶化，悲观情景 HK$19.89",
          fill=RED_FILL, size=9, height=90)
    note(ws, 31, "财务截至 2026-06-30 中报；2026Q3 业绩将于 2026-11-24 发布，本文用 Q3 前瞻。价格日 2026-11-05 收盘。", 8)
    finish(ws, 8, paper=A3)
    ws.print_area = "A1:H31"


# ---------------------------------------------------------------- 2 投资结论
def sheet_conclusion(wb):
    ws = wb.create_sheet("投资结论")
    widths(ws, [22, 30, 58, 3, 3, 3])
    title(ws, "投资结论 · 小米集团 1810.HK", 6)
    subtitle(ws, f"报告日 {D.DATE}｜价格日 {D.PRICE_NOTE}｜评级：合理｜置信度：中", 6)

    block(ws, 4, 1, 4, 6,
          "好生意，合理价格，但没有安全边际。小米的手机×AIoT 现金流仍然稳健，汽车是第二增长曲线；"
          "但 2026 年存储涨价、汽车价格战与 AI 投入同时压缩利润，经调整净利预计从 2025 年的 392 亿元降至 250 亿元。"
          "现价 HK$30.90 对应 2026E PE 27.3 倍、2027E PE 19.5 倍，综合基准 HK$32.08，仅高 3.7%。",
          bold=True, fill=GOLD_FILL, size=10.5, height=58)

    section(ws, 6, "关键锚点", 6)
    header(ws, 7, [(1, "项目", 1), (2, "数值", 1), (3, "说明", 4)])
    rows = [
        ("现价", f"HK${D.PRICE_HKD:.2f} / ¥{D.PRICE:.2f}", "2026-11-05 收盘；前收 HK$28.76"),
        ("总市值", f"HK${D.MARKET_CAP_HKD:,.0f} 亿 / ¥{D.MARKET_CAP:,.0f} 亿", f"{D.SHARES:.1f} 亿股 × 现价"),
        ("净现金", "1,800 亿元", "2026H1 现金储备 2,193 − 借款 393"),
        ("TTM 经调整净利", f"{D.TTM_NP_ADJ:.1f} 亿元", "2025Q3–2026Q2；TTM PE 22.9x"),
        ("2026E 经调整净利", f"{D.NP_ADJ_2026E:.0f} 亿元", "同比约 -36%；中金 247、华泰 254"),
        ("2027E 经调整净利", f"{D.NP_ADJ_2027E_BASE:.0f} 亿元", "中金 403、华泰 336；取中值偏保守"),
        ("DCF 每股", f"HK${hkd(D.DCF_BASE):.2f}", "F0 200 亿、g 13%→3%、WACC 9.6%"),
        ("PE 每股", f"HK${hkd(D.PE_BASE_V):.2f}", "2027E EPS 1.354 元 × 22x"),
        ("综合基准", f"HK${hkd(D.BLEND_BASE):.2f}", "DCF 50% + PE 50%"),
        ("安全边际", f"+{D.MOS*100:.1f}%", "1 − 现价 / 基准"),
        ("20% 安全边际价", f"HK${hkd(D.MOS20_PRICE):.2f}", "基准 × 0.8"),
        ("评级 / 置信度", "合理 / 中", "观察；等更好价格或盈利拐点"),
    ]
    for i, (a, b, c) in enumerate(rows):
        r = 8 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 2, b, bold=True, align="center")
        block(ws, r, 3, r, 6, c, size=9, color=MUTED)

    section(ws, 21, "为什么是“合理”而不是“便宜”", 6)
    block(ws, 22, 1, 27, 6,
          "① 2026 年是利润低谷，不是常态：Q1 经调整净利 61 亿、Q2 62 亿，Q3 前瞻 41–50 亿，全年约 250 亿，"
          "较 2025 年的 392 亿下降约 36%。低利润基数把 PE 推到 27 倍，看起来不便宜。\n"
          "② 2027 年修复依赖两个条件：存储价格回落、汽车亏损收窄。中金预测 403 亿、华泰 336 亿，分歧很大；"
          "本文取 350 亿，对应 19.5 倍 PE，仍不是“闭眼买”的价格。\n"
          "③ 净现金 1,800 亿元、回购 200 亿港元全部注销，提供下行缓冲；但股权激励每年发行新股，稀释抵消了部分回购。\n"
          "④ DCF 基准 HK$29.34 低于现价，PE 基准 HK$34.81 高于现价，综合 HK$32.08，仅高 3.7%——"
          "两法分歧说明“盈利修复”是估值的关键变量，而不是当前现金流。",
          size=9.5, height=150)

    section(ws, 29, "什么会改变结论", 6)
    block(ws, 30, 1, 33, 2,
          "上调：Q4 汽车交付超 16 万辆、澎程月销稳定 2 万辆以上；手机毛利率回到 10% 以上；"
          "2027E 经调整净利上修至 400 亿以上；回购加速。",
          fill=GREEN_FILL, size=9, height=70)
    block(ws, 30, 3, 33, 6,
          "下调：存储涨价延续到 2027 年；汽车价格战使单车亏损扩大；手机份额跌破 12%；"
          "AI 资本开支超预期而无收入；2027E 净利下修至 280 亿以下。",
          fill=RED_FILL, size=9, height=70)
    note(ws, 35, "评级是研究判断，不是买卖指令。数据与假设见「估值与假设」「数据与来源」。", 6)
    finish(ws, 6, paper=A4)
    ws.print_area = "A1:F35"


# ---------------------------------------------------------------- 3 估值系统
def sheet_valuation(wb):
    ws = wb.create_sheet("估值系统")
    widths(ws, [24, 14, 16, 14, 16, 14, 30, 3])
    title(ws, "估值系统 · DCF + PE 双锚", 8)
    subtitle(ws, f"单位：人民币亿元、元/股；港元按 {D.FX:.5f} 折算；蓝色为输入", 8)

    section(ws, 4, "一、FCFF DCF（基准）", 8)
    header(ws, 5, [(1, "假设 / 步骤", 1), (2, "数值", 1), (3, "说明", 6)])
    rows = [
        ("2026E FCFF", D.F0, "经调整净利 250 + 折旧摊销 130 + SBC 40 − capex 180 − 营运资本 40"),
        ("增速起点", D.G1, "2027 年；前五年反映汽车放量，后五年收敛"),
        ("折现年数", D.FADE_YEARS, "线性 fade 至终端 g"),
        ("终端 g", D.G_TERM, "略高于长期通胀"),
        ("WACC", D.WACC, "Ke 11.0%、Kd 3.0%、D/(D+E) 6%"),
        ("净现金", D.NET_CASH, "2026H1 现金储备 2,193 − 借款 393"),
        ("少数股东", D.MINORITY, "无重大少数股东"),
        ("总股本", D.SHARES, "亿股；含 A 类与 B 类"),
    ]
    for i, (a, b, c) in enumerate(rows):
        r = 6 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        fmt = "0.0%" if isinstance(b, float) and b < 1 else ("0.0" if a == "总股本" else "#,##0.0")
        cell(ws, r, 2, b, fmt=fmt, bold=True, color="1A73E8", fill=INPUT_FILL)
        block(ws, r, 3, r, 8, c, size=9, color=MUTED)

    section(ws, 15, "二、DCF 逐年路径", 8)
    header(ws, 16, [(1, "年度", 1), (2, "增速", 1), (3, "FCFF", 1), (4, "折现因子", 1), (5, "现值", 1)])
    d = D.dcf()
    for i, (t, g, fcf, disc, pv) in enumerate(d["rows"]):
        r = 17 + i
        cell(ws, r, 1, f"Y{t}", align="center")
        cell(ws, r, 2, g, fmt="0.0%")
        cell(ws, r, 3, fcf, fmt="#,##0.0")
        cell(ws, r, 4, disc, fmt="0.000")
        cell(ws, r, 5, pv, fmt="#,##0.0")
    r = 27
    for label, val, fmt in [
        ("现值合计", d["pv"], "#,##0.0"),
        ("终值", d["tv"], "#,##0.0"),
        ("终值现值", d["tv_pv"], "#,##0.0"),
        ("企业价值 EV", d["ev"], "#,##0.0"),
        ("股权价值", d["equity"], "#,##0.0"),
    ]:
        cell(ws, r, 1, label, align="left", bold=True)
        cell(ws, r, 3, val, fmt=fmt, bold=True)
        r += 1
    cell(ws, r, 1, "每股价值（元）", align="left", bold=True, fill=GREEN_FILL)
    cell(ws, r, 3, d["value"], fmt="0.00", bold=True, fill=GREEN_FILL)
    cell(ws, r, 4, "港元", align="left", color=MUTED)
    cell(ws, r, 5, hkd(d["value"]), fmt="0.00", bold=True, color=GREEN, fill=GREEN_FILL)
    note(ws, 34, f"终值占 EV 的 {d['tv_pv']/d['ev']*100:.1f}%；DCF 对 WACC 与终端 g 敏感，区间比单点更重要。", 8)

    section(ws, 36, "三、PE 法与综合", 8)
    header(ws, 37, [(1, "方法", 1), (2, "每股价值（元）", 1), (3, "港元", 1), (4, "权重", 1), (5, "说明", 4)])
    pe_rows = [
        ("FCFF DCF", D.DCF_BASE, hkd(D.DCF_BASE), 0.5, "F0 200 亿、g 13%→3%、WACC 9.6%"),
        ("PE 法", D.PE_BASE_V, hkd(D.PE_BASE_V), 0.5, "2027E EPS 1.354 元 × 22x"),
        ("综合基准", D.BLEND_BASE, hkd(D.BLEND_BASE), 1.0, "两法各半"),
    ]
    for i, (a, b, c, w, note_) in enumerate(pe_rows):
        r = 38 + i
        fill = GOLD_FILL if a == "综合基准" else None
        cell(ws, r, 1, a, align="left", bold=True, fill=fill)
        cell(ws, r, 2, b, fmt="0.00", bold=True, fill=fill)
        cell(ws, r, 3, c, fmt="0.00", bold=True, fill=fill)
        cell(ws, r, 4, w, fmt="0%", fill=fill)
        block(ws, r, 5, r, 8, note_, size=9, color=MUTED, fill=fill)

    section(ws, 43, "四、三情景", 8)
    header(ws, 44, [(1, "情景", 1), (2, "DCF（元）", 1), (3, "PE（元）", 1), (4, "综合（元）", 1),
                    (5, "综合（港元）", 1), (6, "较现价", 1), (7, "核心假设", 2)])
    scen = [
        ("悲观", D.DCF_BEAR, D.PE_BEAR_V, D.BLEND_BEAR, "F0 160、g 5%、WACC 10.6%"),
        ("基准", D.DCF_BASE, D.PE_BASE_V, D.BLEND_BASE, "F0 200、g 13%、WACC 9.6%"),
        ("乐观", D.DCF_BULL, D.PE_BULL_V, D.BLEND_BULL, "F0 230、g 17%、WACC 9.0%"),
    ]
    for i, (a, dcf, pe, blend, cond) in enumerate(scen):
        r = 45 + i
        fill = GOLD_FILL if a == "基准" else None
        cell(ws, r, 1, a, align="center", bold=True, fill=fill)
        cell(ws, r, 2, dcf, fmt="0.00", fill=fill)
        cell(ws, r, 3, pe, fmt="0.00", fill=fill)
        cell(ws, r, 4, blend, fmt="0.00", bold=True, fill=fill)
        cell(ws, r, 5, hkd(blend), fmt="0.00", bold=True, fill=fill)
        cell(ws, r, 6, hkd(blend) / D.PRICE_HKD - 1, fmt="0.0%", bold=True,
             color=(GREEN if hkd(blend) > D.PRICE_HKD else RED), fill=fill)
        block(ws, r, 7, r, 8, cond, size=8.5, color=MUTED, fill=fill)

    section(ws, 49, "五、反向估值与安全边际", 8)
    header(ws, 50, [(1, "项目", 1), (2, "数值", 1), (3, "说明", 6)])
    rev = [
        ("现价（港元）", D.PRICE_HKD, "2026-11-05 收盘", "0.00"),
        ("综合基准（港元）", hkd(D.BLEND_BASE), "DCF 50% + PE 50%", "0.00"),
        ("安全边际", D.MOS, "1 − 现价 / 基准", "0.0%"),
        ("20% 安全边际价（港元）", hkd(D.MOS20_PRICE), "基准 × 0.8", "0.00"),
        ("现价隐含 2026E FCFF", D.DCF_AT_PRICE_F0, "按基准 DCF 反推；基准 200 亿", "#,##0.0"),
        ("隐含 FCFF 较基准", D.DCF_AT_PRICE_F0 / D.F0 - 1, "正数 = 市场比基准更乐观", "0.0%"),
    ]
    for i, (a, b, c, fmt) in enumerate(rev):
        r = 51 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 2, b, fmt=fmt, bold=True)
        block(ws, r, 3, r, 8, c, size=9, color=MUTED)

    section(ws, 58, "六、敏感性：DCF 每股价值（元），WACC × 终端 g", 8)
    header(ws, 59, [(1, "WACC \\ g", 1)] + [(2 + j, f"{g*100:.2f}%", 1) for j, g in enumerate(D.SENS_G)])
    for i, w in enumerate(D.SENS_WACC):
        r = 60 + i
        cell(ws, r, 1, f"{w*100:.1f}%", align="center", bold=True)
        for j, v in enumerate(D.SENS[i]):
            cell(ws, r, 2 + j, v, fmt="0.0")
    note(ws, 66, f"现价 ¥{D.PRICE:.2f}；表中数值为 DCF 每股价值（元），港元按 0.85601 折算。", 8)

    finish(ws, 8, paper=A3)
    ws.print_area = "A1:H66"


# ---------------------------------------------------------------- 4 生意与护城河
def sheet_business(wb):
    ws = wb.create_sheet("生意与护城河")
    widths(ws, [22, 14, 12, 12, 12, 12, 12, 3])
    title(ws, "生意与护城河 · 小米集团", 8)
    subtitle(ws, "手机 × AIoT × 互联网 × 汽车；从“性价比硬件”到“人车家全生态”", 8)

    section(ws, 4, "一、巴菲特八问", 8)
    header(ws, 5, [(1, "问题", 1), (2, "回答", 7)])
    qa = [
        ("1. 我能看懂吗？", "能。手机/IoT 是硬件生意，看份额、ASP、毛利率；互联网是变现层，看 MAU 与 ARPU；汽车看交付、ASP、单车亏损。"),
        ("2. 护城河是什么？", "品牌 + 生态（手机/家居/汽车互联）+ 成本效率 + 渠道。手机全球第三、份额 13.3%；但硬件没有提价权。"),
        ("3. 能长久吗？", "手机与 IoT 大概率长期存在；汽车是十年维度的新业务，胜率未定；AI 可能重构入口。"),
        ("4. 资本回报如何？", "2025 年 ROE 约 18%；轻资产手机业务回报高，汽车重资产拉低整体回报。"),
        ("5. 增长来自哪里？", "汽车（2025 年收入 1,033 亿、+222%）、IoT 出海、互联网服务、AI；手机进入成熟期。"),
        ("6. 管理层是否可信？", "雷军创始人控制，执行力强；回购全部注销、不分红；但汽车/AI 投入大，资本配置纪律待验证。"),
        ("7. 最大风险是什么？", "存储涨价压制手机毛利；汽车价格战与放量不及预期；AI 投入回报低；股权激励稀释。"),
        ("8. 估值是否合理？", "2026E PE 27.3x、2027E PE 19.5x；综合基准 HK$32.08，现价 HK$30.90，仅高 3.7%；合理，无安全边际。"),
    ]
    for i, (q, a) in enumerate(qa):
        r = 6 + i
        cell(ws, r, 1, q, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"), wrap=True)
        block(ws, r, 2, r, 8, a, size=9, height=34)

    section(ws, 15, "二、2025 年收入结构", 8)
    header(ws, 16, [(1, "业务", 1), (2, "收入（亿元）", 1), (3, "同比", 1), (4, "占比", 1), (5, "毛利率", 1)])
    for i, (name, rev, yoy, share, gm) in enumerate(D.SEG_2025):
        r = 17 + i
        cell(ws, r, 1, name, align="left", bold=True)
        cell(ws, r, 2, rev, fmt="#,##0.0")
        cell(ws, r, 3, yoy / 100, fmt="0.0%")
        cell(ws, r, 4, share / 100, fmt="0.0%")
        cell(ws, r, 5, gm / 100, fmt="0.0%")
    r = 22
    cell(ws, r, 1, "合计", align="left", bold=True, fill=GOLD_FILL)
    cell(ws, r, 2, 4572.9, fmt="#,##0.0", bold=True, fill=GOLD_FILL)
    cell(ws, r, 3, 0.25, fmt="0.0%", bold=True, fill=GOLD_FILL)
    cell(ws, r, 4, 1.0, fmt="0.0%", bold=True, fill=GOLD_FILL)
    cell(ws, r, 5, 0.223, fmt="0.0%", bold=True, fill=GOLD_FILL)

    section(ws, 24, "三、2026Q2 分部（最新实际）", 8)
    header(ws, 25, [(1, "业务", 1), (2, "收入（亿元）", 1), (3, "同比", 1), (4, "毛利率", 1)])
    for i, (name, rev, yoy, gm) in enumerate(D.SEG_2026Q2):
        r = 26 + i
        cell(ws, r, 1, name, align="left", bold=True)
        cell(ws, r, 2, rev, fmt="#,##0.0")
        cell(ws, r, 3, yoy / 100, fmt="0.0%")
        cell(ws, r, 4, gm / 100, fmt="0.0%")
    note(ws, 30, "2026Q2 集团毛利率 19.8%（同比 -2.7pct）；手机毛利率 8.5% 为主要拖累，互联网服务 76.8% 是毛利最大来源。", 8)

    section(ws, 32, "四、护城河评分（1–5）", 8)
    header(ws, 33, [(1, "维度", 1), (2, "评分", 1), (3, "依据", 6)])
    moat = [
        ("品牌与用户心智", 4, "全球手机第三、IoT 全球领先；“性价比”标签强，但高端化仍在爬坡。"),
        ("生态与切换成本", 4, "手机/家居/汽车互联，用户多设备协同；但单品可替换，粘性弱于 iOS。"),
        ("成本与渠道效率", 4, "硬件综合净利率低、周转快；线上线下渠道覆盖广。"),
        ("技术壁垒", 3, "芯片/系统仍依赖外部；汽车智驾与电池技术需持续投入。"),
        ("定价权", 2, "手机/IoT 价格战常态；互联网服务有定价权，但占比小。"),
    ]
    for i, (a, s, c) in enumerate(moat):
        r = 34 + i
        cell(ws, r, 1, a, align="left", bold=True)
        cell(ws, r, 2, s, fmt="0", bold=True, align="center", color=(GREEN if s >= 4 else GOLD))
        block(ws, r, 3, r, 8, c, size=9, color=MUTED)
    note(ws, 39, "综合护城河 3.4/5：品牌与生态强，定价权弱；属于“好生意”，但不是“伟大生意”。", 8)

    section(ws, 41, "五、行业结构", 8)
    header(ws, 42, [(1, "角色", 1), (2, "主要内容", 7)])
    industry = [
        ("竞争者", "苹果、三星、华为、OPPO/vivo、荣耀；汽车：比亚迪、特斯拉、理想、问界、零跑。"),
        ("客户", "C 端消费者、运营商、企业客户；汽车为个人与家庭用户。"),
        ("供应商", "高通/联发科、存储芯片、屏幕、电池、代工厂；存储涨价是 2026 年最大成本变量。"),
        ("替代品", "手机换机周期延长；汽车替代燃油车；AI 硬件可能改变入口。"),
        ("监管", "印度/欧洲数据与贸易政策、汽车安全法规、反垄断。"),
    ]
    for i, (a, c) in enumerate(industry):
        r = 43 + i
        cell(ws, r, 1, a, align="left", bold=True)
        block(ws, r, 2, r, 8, c, size=9, color=MUTED, height=30)

    finish(ws, 8, paper=A4)
    ws.print_area = "A1:H47"


# ---------------------------------------------------------------- 5 财务与现金流
def sheet_financials(wb):
    ws = wb.create_sheet("财务与现金流")
    widths(ws, [20, 13, 13, 13, 13, 13, 13, 13, 3])
    title(ws, "财务与现金流 · 2021–2026E", 9)
    subtitle(ws, "单位：人民币亿元；2026E 为本文估计，2026H1 为实际", 9)

    section(ws, 4, "一、五年损益", 9)
    header(ws, 5, [(1, "指标", 1), (2, "2021", 1), (3, "2022", 1), (4, "2023", 1),
                   (5, "2024", 1), (6, "2025", 1), (7, "2026E", 1), (8, "2026H1", 1)])
    data = [
        ("营业收入", D.REVENUE + [4400.0, 2080.6], "#,##0.0"),
        ("归母净利", D.NP + [250.0, 141.86], "#,##0.0"),
        ("经调整净利", D.NP_ADJ + [250.0, 122.9], "#,##0.0"),
        ("经营现金流", D.OCF + [120.0, 20.5], "#,##0.0"),
        ("资本开支", D.CAPEX + [180.0, 60.0], "#,##0.0"),
        ("自由现金流", D.FCF + [-60.0, -39.5], "#,##0.0"),
        ("EPS（元）", D.EPS + [0.97, 0.55], "0.00"),
        ("ROE（%）", [12.0, 1.5, 10.0, 12.0, 18.0, 9.0, 5.2], "0.0"),
    ]
    for i, (name, vals, fmt) in enumerate(data):
        r = 6 + i
        cell(ws, r, 1, name, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        for j, v in enumerate(vals):
            cell(ws, r, 2 + j, v, fmt=fmt, bold=(name in ("经调整净利",)))

    section(ws, 16, "二、关键比率", 9)
    header(ws, 17, [(1, "比率", 1), (2, "2021", 1), (3, "2022", 1), (4, "2023", 1),
                    (5, "2024", 1), (6, "2025", 1), (7, "2026E", 1)])
    ratios = [
        ("收入增速", ["—", "-14.7%", "-3.2%", "35.0%", "25.0%", "-3.8%"]),
        ("经调整净利率", ["6.7%", "3.0%", "7.1%", "7.4%", "8.6%", "5.7%"]),
        ("毛利率", ["17.7%", "17.0%", "21.2%", "20.9%", "22.3%", "20.0%"]),
        ("经营现金流/净利", ["2.21x", "-1.78x", "2.36x", "1.67x", "0.82x", "0.48x"]),
        ("资本开支/收入", ["1.5%", "2.1%", "2.3%", "2.0%", "2.8%", "4.1%"]),
    ]
    for i, (name, vals) in enumerate(ratios):
        r = 18 + i
        cell(ws, r, 1, name, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        for j, v in enumerate(vals):
            cell(ws, r, 2 + j, v, align="center")

    section(ws, 24, "三、2026H1 现金流与资产负债表", 9)
    header(ws, 25, [(1, "项目", 1), (2, "金额（亿元）", 1), (3, "说明", 7)])
    bs = [
        ("现金储备", 2193.0, "公司口径，含现金、定期存款与理财"),
        ("借款总额", 393.0, "短期 97.1 + 长期 295.7"),
        ("净现金", 1800.0, "现金储备 − 借款"),
        ("2026H1 经营现金流", 20.5, "同比大幅下降，营运资本与汽车投入占用"),
        ("2026H1 资本开支", 60.0, "Q2 36.21 亿，其中汽车/AI 23.83 亿"),
        ("2026H1 自由现金流", -39.5, "经营现金流 − 资本开支"),
        ("2026H1 研发投入", 182.0, "占收入 8.7%"),
        ("2026H1 回购", 117.0, "港元；全部注销"),
    ]
    for i, (a, b, c) in enumerate(bs):
        r = 26 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 2, b, fmt="#,##0.0", bold=True)
        block(ws, r, 3, r, 9, c, size=9, color=MUTED)

    section(ws, 35, "四、现金流质量判断", 9)
    block(ws, 36, 1, 41, 9,
          "2025 年经营现金流 341 亿元、资本开支 128 亿元，自由现金流 214 亿元，覆盖回购与投资；"
          "2026H1 经营现金流仅 20.5 亿元、自由现金流 -39.5 亿元，主因是汽车产能与 AI 投入、以及营运资本占用。"
          "这不是现金流断裂——账上仍有 2,193 亿元现金储备、1,800 亿元净现金——但说明“高分红/大回购”与“高资本开支”不能同时最大化。"
          "2026 年回购 200 亿港元的上限，约占现金储备的 9%，资金上可承受；真正的约束是汽车业务何时自负盈亏。",
          size=9.5, height=90)

    finish(ws, 9, paper=A4)
    ws.print_area = "A1:I41"


# ---------------------------------------------------------------- 6 分红与股东回报
def sheet_dividend(wb):
    ws = wb.create_sheet("分红与股东回报")
    widths(ws, [30, 28, 56, 3, 3, 3, 3, 3])
    title(ws, "分红与股东回报 · 回购替代股息", 8)
    subtitle(ws, "小米上市以来无现金分红；股东回报以回购注销为主", 8)

    section(ws, 4, "一、股东回报事实", 8)
    header(ws, 5, [(1, "项目", 1), (2, "数值", 1), (3, "说明", 6)])
    facts = [
        ("现金分红", "0 元", "2018 年上市以来累计现金分红为 0；管理层明确暂无分红计划"),
        ("2025 年回购", "约 63 亿港元", "2025 年全年回购金额"),
        ("旧回购计划（2025.6–2026.6）", "约 146 亿港元 / 3.996 亿股", "回购股份全部注销"),
        ("新回购计划（2026.5 起 12 个月）", "上限 200 亿港元", "截至 2026-09-29 已执行约 39.9 亿，进度约 20%"),
        ("2026 年内回购（至 9 月）", "约 123 亿港元", "港股回购金额第二，仅次于腾讯"),
        ("总股本", "约 258.4 亿股", "2024 年底约 251 亿股，2025 年底约 260 亿股；股权激励持续发行"),
        ("2026E 股息率", "0%", "不分红；回购收益率约 1.8%（200 亿港元 / 市值）"),
    ]
    for i, (a, b, c) in enumerate(facts):
        r = 6 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 2, b, bold=True, align="center")
        block(ws, r, 3, r, 8, c, size=9, color=MUTED)

    section(ws, 15, "二、回购与稀释", 8)
    block(ws, 16, 1, 21, 8,
          "小米的回购是“注销式回购”，理论上是提高每股价值的最直接方式；但公司同时因股权激励持续发行新股，"
          "2026 年 7 月回购约 7,980 万股、同期因员工激励发行约 5,419 万股，回购效果被部分抵消。"
          "按 30 港元均价测算，200 亿港元约回购 6.66 亿股，占总股本约 2.58%；若同期股权激励发行 1.5–2%，"
          "净减少股本仅 0.6–1.1%。因此，回购是正面因素，但不能按“200 亿 / 市值 = 2.6% 股东回报”简单外推。",
          size=9.5, height=100)

    section(ws, 23, "三、与红利股的区别", 8)
    block(ws, 24, 1, 28, 8,
          "小米不是红利资产：没有股息，回购也不承诺固定金额；股东回报取决于股价、回购执行与股权激励稀释。"
          "对追求现金收益的资金，它不适合替代红利股；对追求成长的资金，回购注销是“锦上添花”，不是“安全垫”。"
          "真正的安全垫是 1,800 亿元净现金与手机/IoT 的现金流，而不是股息。",
          size=9.5, height=80)

    finish(ws, 8, paper=A4)
    ws.print_area = "A1:H28"


# ---------------------------------------------------------------- 7 估值与假设
def sheet_assumptions(wb):
    ws = wb.create_sheet("估值与假设")
    widths(ws, [22, 12, 12, 12, 18, 12, 12, 3])
    title(ws, "估值与假设 · 关键变量", 8)
    subtitle(ws, "所有输入均可追溯；改变假设会显著改变结果", 8)

    section(ws, 4, "一、核心假设", 8)
    header(ws, 5, [(1, "假设", 1), (2, "基准", 1), (3, "悲观", 1), (4, "乐观", 1), (5, "依据", 4)])
    rows = [
        ("2026E 经调整净利（亿元）", "250", "230", "270", "Q1 61 + Q2 62 + Q3 45 + Q4 82"),
        ("2027E 经调整净利（亿元）", "350", "280", "420", "中金 403、华泰 336；取中值"),
        ("2027E EPS（元）", f"{D.EPS_2027E_BASE:.3f}", f"{D.EPS_2027E_BEAR:.3f}", f"{D.EPS_2027E_BULL:.3f}", "净利 / 258.4 亿股"),
        ("目标 PE（倍）", "22", "17", "25", "对应 2027E 增速与 ROE；高于当前 19.5x"),
        ("DCF F0（亿元）", "200", "160", "230", "净利 250 + D&A 130 + SBC 40 − capex 180"),
        ("DCF 增速起点", "13%", "5%", "17%", "汽车放量 vs 手机成熟"),
        ("WACC", "9.6%", "10.6%", "9.0%", "Ke 11.0%、Kd 3.0%、D/(D+E) 6%"),
        ("终端 g", "3.0%", "2.5%", "3.5%", "长期通胀 + 温和增长"),
        ("净现金（亿元）", "1,800", "1,800", "1,800", "2026H1"),
        ("总股本（亿股）", "258.4", "258.4", "258.4", "当前股本，未考虑回购注销"),
    ]
    for i, (a, b, c, d, e) in enumerate(rows):
        r = 6 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 2, b, align="center", bold=True)
        cell(ws, r, 3, c, align="center", color=BROWN)
        cell(ws, r, 4, d, align="center", color=GREEN)
        block(ws, r, 5, r, 8, e, size=9, color=MUTED)
        ws.row_dimensions[r].height = 30

    section(ws, 17, "二、估值结果", 8)
    header(ws, 18, [(1, "情景", 1), (2, "DCF（元）", 1), (3, "PE（元）", 1), (4, "综合（元）", 1),
                    (5, "综合（港元）", 1), (6, "较现价", 1)])
    for i, (name, dcf, pe, blend) in enumerate([
        ("悲观", D.DCF_BEAR, D.PE_BEAR_V, D.BLEND_BEAR),
        ("基准", D.DCF_BASE, D.PE_BASE_V, D.BLEND_BASE),
        ("乐观", D.DCF_BULL, D.PE_BULL_V, D.BLEND_BULL),
    ]):
        r = 19 + i
        fill = GOLD_FILL if name == "基准" else None
        cell(ws, r, 1, name, align="center", bold=True, fill=fill)
        cell(ws, r, 2, dcf, fmt="0.00", fill=fill)
        cell(ws, r, 3, pe, fmt="0.00", fill=fill)
        cell(ws, r, 4, blend, fmt="0.00", bold=True, fill=fill)
        cell(ws, r, 5, hkd(blend), fmt="0.00", bold=True, fill=fill)
        cell(ws, r, 6, hkd(blend) / D.PRICE_HKD - 1, fmt="0.0%", bold=True, fill=fill)

    section(ws, 24, "三、敏感性（DCF，元）", 8)
    header(ws, 25, [(1, "WACC \\ g", 1)] + [(2 + j, f"{g*100:.2f}%", 1) for j, g in enumerate(D.SENS_G)])
    for i, w in enumerate(D.SENS_WACC):
        r = 26 + i
        cell(ws, r, 1, f"{w*100:.1f}%", align="center", bold=True)
        for j, v in enumerate(D.SENS[i]):
            cell(ws, r, 2 + j, v, fmt="0.0")

    section(ws, 32, "四、交叉检查", 8)
    block(ws, 33, 1, 38, 8,
          f"① DCF ¥{D.DCF_BASE:.2f} vs PE ¥{D.PE_BASE_V:.2f}：相差 {abs(D.PE_BASE_V/D.DCF_BASE-1)*100:.1f}%，"
          f"分歧来自“盈利修复”假设；DCF 更看重当前现金流，PE 更看重 2027 年恢复。\n"
          f"② 现价 ¥{D.PRICE:.2f} 对应 2026E PE 27.3x、2027E PE 19.5x；TTM PE 22.9x。\n"
          f"③ 净现金 1,800 亿元，占市值 {D.NET_CASH/D.MARKET_CAP*100:.1f}%；EV/2026E 经调整净利 "
          f"{(D.MARKET_CAP-D.NET_CASH)/D.NP_ADJ_2026E:.1f}x。\n"
          f"④ 2026E 股息率 0%；回购上限 200 亿港元，约占市值 2.5%。\n"
          f"⑤ 反向 DCF：现价隐含 2026E FCFF {D.DCF_AT_PRICE_F0:.0f} 亿元，比基准 200 亿元高 "
          f"{(D.DCF_AT_PRICE_F0/D.F0-1)*100:.1f}%——市场比本文基准略乐观，但低于 2025 年 214 亿元的自由现金流。",
          size=9.5, height=110)

    finish(ws, 8, paper=A4)
    ws.print_area = "A1:H38"


# ---------------------------------------------------------------- 8 风险与跟踪
def sheet_risk(wb):
    ws = wb.create_sheet("风险与跟踪")
    widths(ws, [22, 48, 30, 10, 3, 3, 3, 3])
    title(ws, "风险与跟踪 · 小米集团", 8)
    subtitle(ws, "风险不是预测，而是需要持续验证的变量", 8)

    section(ws, 4, "一、主要风险矩阵", 8)
    header(ws, 5, [(1, "风险", 1), (2, "机制", 1), (3, "监控指标", 1), (4, "等级", 1)])
    risks = [
        ("存储涨价", "内存/闪存价格上涨 → 手机毛利率 8.5% → 净利下修", "手机毛利率、存储现货价", "高"),
        ("汽车价格战", "车企降价 → 单车 ASP 下降 → 汽车亏损扩大", "交付量、ASP、分部亏损", "高"),
        ("澎程放量不及预期", "新车订单/产能爬坡慢 → 2026 年 45 万辆目标落空", "月交付、订单 backlog", "中高"),
        ("AI 投入回报低", "AI 资本开支与研发上升 → 费用率上升 → FCF 承压", "研发费用率、AI 收入", "中"),
        ("股权激励稀释", "每年发行新股 → 抵消回购注销 → EPS 增厚打折", "总股本、回购注销数", "中"),
        ("地缘政治", "印度/欧洲贸易与数据监管 → 海外收入受限", "海外收入占比、政策", "中"),
    ]
    for i, (a, b, c, level) in enumerate(risks):
        r = 6 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 2, b, align="left", size=9, wrap=True)
        cell(ws, r, 3, c, align="left", size=9)
        cell(ws, r, 4, level, align="center", bold=True,
             color=(RED if level == "高" else (BROWN if level == "中高" else GOLD)))

    section(ws, 13, "二、三个永久性损失风险", 8)
    block(ws, 14, 1, 17, 8,
          "① 汽车业务失败：投入数百亿、年销未达规模，长期亏损吞噬手机现金流；概率中低，但一旦发生，估值逻辑重写。\n"
          "② 手机业务结构性萎缩：存储涨价 + 竞争加剧 + 换机周期延长，份额跌破 10%，现金流与生态入口同时受损。\n"
          "③ 品牌/安全事件：汽车或手机出现重大安全/质量危机，信任受损，生态协同反噬。概率低，但不可逆。",
          fill=RED_FILL, size=9.5, height=90)

    section(ws, 19, "三、监控触发条件", 8)
    header(ws, 20, [(1, "指标", 1), (2, "当前", 1), (3, "触发阈值", 1), (4, "动作", 5)])
    triggers = [
        ("2026Q4 汽车交付", "10 月 >5 万", "< 4.5 万/月", "下调 2027 年汽车收入与估值"),
        ("汽车分部亏损", "Q2 -26 亿", "连续两季 > 35 亿", "确认价格战恶化，转向悲观"),
        ("手机毛利率", "8.5%（Q2）", "< 8% 连续两季", "下调 2027E 净利 10%"),
        ("IoT 毛利率", "20.1%（Q2）", "< 18%", "检查存储成本与补贴退坡"),
        ("互联网收入增速", "-0.6%（Q2）", "连续两季负增长", "下调高毛利业务估值"),
        ("2027E 经调整净利", "350 亿（本文）", "下修 > 15%", "重估 PE 基准"),
        ("回购执行", "约 123 亿港元", "< 100 亿（12 个月）", "股东回报低于预期"),
    ]
    for i, (a, b, c, d) in enumerate(triggers):
        r = 21 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        cell(ws, r, 2, b, align="center")
        cell(ws, r, 3, c, align="center", color=RED)
        block(ws, r, 4, r, 8, d, size=9, color=MUTED)

    section(ws, 30, "四、跟踪日历", 8)
    header(ws, 31, [(1, "时间", 1), (2, "事件", 1), (3, "看什么", 6)])
    cal = [
        ("2026-11-24", "Q3 业绩", "经调整净利 41–50 亿？汽车亏损 31–36 亿？手机毛利率？"),
        ("2026-12", "11 月交付", "澎程月销能否稳定 2 万辆以上"),
        ("2027-03", "2026 年报", "全年交付、汽车分部亏损、2027 指引、回购进度"),
        ("2027-05", "Q1 业绩", "存储价格是否回落；手机毛利率修复"),
        ("季度", "交付/份额", "月交付、全球手机份额、IoT 增速"),
    ]
    for i, (a, b, c) in enumerate(cal):
        r = 32 + i
        cell(ws, r, 1, a, align="center", bold=True)
        cell(ws, r, 2, b, align="left")
        block(ws, r, 3, r, 8, c, size=9, color=MUTED)

    finish(ws, 8, paper=A4)
    ws.print_area = "A1:H36"


# ---------------------------------------------------------------- 9 数据与来源
def sheet_sources(wb):
    ws = wb.create_sheet("数据与来源")
    widths(ws, [34, 14, 64, 3, 3, 3, 3, 3])
    title(ws, "数据与来源 · 口径说明", 8)
    subtitle(ws, f"报告日 {D.DATE}；财务截止 2026-06-30；价格日 2026-11-05 收盘", 8)

    section(ws, 4, "一、关键口径", 8)
    header(ws, 5, [(1, "项目", 1), (2, "口径", 7)])
    defs = [
        ("货币", "财务以人民币报告；股价以港元交易；本文按 HKD/CNY 0.85601 折算。"),
        ("市值", f"{D.SHARES:.1f} 亿股 × HK${D.PRICE_HKD:.2f} = HK${D.MARKET_CAP_HKD:,.0f} 亿；折 ¥{D.MARKET_CAP:,.0f} 亿。"),
        ("净现金", "2026H1 现金储备 2,193 亿元 − 借款 393 亿元 = 1,800 亿元；现金储备含定期存款/理财。"),
        ("经调整净利", "非 IFRS 口径，剔除股权激励、投资公允价值变动等；与 IFRS 净利不同。"),
        ("2026E", "本文估计：经调整净利 250 亿元；不是公司指引。"),
        ("2027E", "本文假设：经调整净利 350 亿元；中金 403、华泰 336，分歧较大。"),
        ("DCF", "FCFF = 经调整净利 + 折旧摊销 + SBC − 资本开支 − 营运资本增加；不含投资收益。"),
        ("价格", "2026-11-05 收盘 HK$30.90；前收 HK$28.76。"),
    ]
    for i, (a, b) in enumerate(defs):
        r = 6 + i
        cell(ws, r, 1, a, align="left", bold=True, fill=PatternFill("solid", fgColor="FAF8F2"))
        block(ws, r, 2, r, 8, b, size=9, color=MUTED)

    section(ws, 16, "二、主要来源", 8)
    header(ws, 17, [(1, "来源", 1), (2, "日期", 1), (3, "用途", 6)])
    src = [
        ("小米集团 2025 年年度业绩公告", "2026-03-24", "FY2025 营收、净利、分部、交付、研发、现金流"),
        ("小米集团 2026 年第一季度业绩公告", "2026-05-26", "Q1 营收、经调整净利、汽车交付、手机毛利率"),
        ("小米集团 2026 年中期业绩公告", "2026-08-18", "H1 营收、净利、Q2 分部、现金储备、借款、研发"),
        ("小米集团 2026 年 Q3 业绩前瞻（券商）", "2026-11-03/05", "中金/华泰/花旗/中信建投 Q3 预测；不是官方数据"),
        ("回购公告与统计", "2026-05-26 起", "200 亿港元回购计划、执行进度、注销"),
        ("中国货币网", "2026-11-05", "HKD/CNY 中间价 0.85601"),
    ]
    for i, (a, b, c) in enumerate(src):
        r = 18 + i
        cell(ws, r, 1, a, align="left", bold=True)
        cell(ws, r, 2, b, align="center")
        block(ws, r, 3, r, 8, c, size=9, color=MUTED)

    section(ws, 25, "三、数据质量提示", 8)
    block(ws, 26, 1, 31, 8,
          "① 2026Q3 官方业绩尚未发布（预计 2026-11-24），本文 Q3 数据来自券商前瞻，存在误差；\n"
          "② 2026E/2027E 为本文估计，与中金、华泰等机构预测存在差异；\n"
          "③ 分部毛利率为财报口径，2025 年“其他”与内部抵销可能影响合计；\n"
          "④ 经调整净利为非 IFRS，不能与 IFRS 净利直接比较；\n"
          "⑤ 港元折算按 2026-11-05 中间价，汇率变动 1% 会改变港元计价价值约 1%。",
          size=9.5, height=100)

    section(ws, 33, "四、免责声明", 8)
    block(ws, 34, 1, 37, 8,
          "本报告为研究记录，不构成任何投资建议、要约或承诺。估值依赖假设，假设变化会显著改变结果。"
          "作者可能不持有相关证券，也可能不了解报告发布后的最新变化。读者应独立判断，并咨询持牌专业人士。",
          size=9, color=MUTED, height=60)

    finish(ws, 8, paper=A4)
    ws.print_area = "A1:H37"


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
    print("saved", XLSX.name)


if __name__ == "__main__":
    main()
