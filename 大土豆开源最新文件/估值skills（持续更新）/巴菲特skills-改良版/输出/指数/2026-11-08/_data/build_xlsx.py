# -*- coding: utf-8 -*-
import json, csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

BASE = "输出/指数/2026-11-08"
rows = json.load(open(f"{BASE}/_data/index_valuation_model.json", encoding="utf-8"))

wb = Workbook()
hdr_fill = PatternFill("solid", fgColor="1F4E78")
hdr_font = Font(color="FFFFFF", bold=True)
center = Alignment(horizontal="center", vertical="center")

ws = wb.active
ws.title = "总览"
headers = ["指数", "代码", "现价", "PE", "PE口径", "历史分位", "股息率", "合理中枢", "低估线", "高估线", "现价vs中枢", "结论", "ERP(pp)"]
ws.append(headers)
for r in rows:
    ws.append([r["name"], r["code"], r["level"], r["pe"], r["pe_label"], r["pct"], r["div"],
               r["base_val"], r["low_line"], r["high_line"], r["pos_vs_base"] / 100, r["verdict"], r["erp"]])
for c in ws[1]:
    c.fill = hdr_fill
    c.font = hdr_font
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
widths = [14, 12, 10, 10, 20, 10, 9, 10, 10, 10, 11, 14, 10]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[chr(64 + i)].width = w
ws.freeze_panes = "A2"
for row in ws.iter_rows(min_row=2):
    for c in row:
        c.alignment = center
    row[2].number_format = "#,##0"
    row[3].number_format = "0.00"
    row[5].number_format = "0.0"
    row[6].number_format = "0.00"
    row[7].number_format = "#,##0"
    row[8].number_format = "#,##0"
    row[9].number_format = "#,##0"
    row[10].number_format = "0.0%"
    row[12].number_format = "+0.0;-0.0"

ws2 = wb.create_sheet("估值模型")
keys = list(rows[0].keys())
ws2.append(keys)
for r in rows:
    ws2.append([(", ".join(map(str, r.get(k))) if isinstance(r.get(k), list) else r.get(k)) for k in keys])
for c in ws2[1]:
    c.fill = hdr_fill
    c.font = hdr_font
    c.alignment = Alignment(horizontal="center", wrap_text=True)
ws2.freeze_panes = "A2"
for i in range(1, len(keys) + 1):
    ws2.column_dimensions[chr(64 + i) if i <= 26 else "A"].width = 16

ws3 = wb.create_sheet("标普PE历史")
ws3.append(["date", "pe"])
with open(f"{BASE}/_data/spx_pe_monthly.csv", encoding="utf-8") as f:
    for line in f.read().splitlines()[1:]:
        if line:
            a, b = line.split(",")
            ws3.append([a, float(b)])
for c in ws3[1]:
    c.fill = hdr_fill
    c.font = hdr_font
ws3.freeze_panes = "A2"

ws4 = wb.create_sheet("方法与来源")
notes = [
    ["项目", "说明"],
    ["数据日", "2026-11-06收盘；报告日2026-11-08"],
    ["方法", "历史分位锚 + 盈利锚（2027E三情景）+ 利率锚（EY-10Y国债ERP）+ 安全边际"],
    ["合理中枢", "基准EPS × 中枢PE"],
    ["低估线", "max(悲观价值, 中枢×(1-安全边际))"],
    ["高估线", "min(乐观价值, 中枢×(1+安全边际))"],
    ["安全边际", "宽基20%；高波动成长指数25%-30%"],
    ["重要提示", "各指数PE口径不同；2027E增速与PE带为假设；不构成投资建议"],
    ["来源", "CSIndex、同花顺/证券之星、中信证券、multpl、SSGA、Barron's/WSJ、Siblis Research、DollarLiquidity、FRED、akshare"],
]
for row in notes:
    ws4.append(row)
for c in ws4[1]:
    c.fill = hdr_fill
    c.font = hdr_font
ws4.column_dimensions["A"].width = 18
ws4.column_dimensions["B"].width = 100

out = f"{BASE}/指数基准分析_2026-11-08.xlsx"
wb.save(out)
print("saved", out)
