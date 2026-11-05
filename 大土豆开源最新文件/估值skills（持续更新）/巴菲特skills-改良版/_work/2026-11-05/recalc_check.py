# -*- coding: utf-8 -*-
import sys
from pathlib import Path
import win32com.client as win32

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catl_data as D

XLSX = (Path(__file__).resolve().parents[2] / "输出" / "A股" /
        f"300750.SZ-{D.DATE}" / f"300750.SZ-估值模型-{D.DATE}.xlsx")

app = win32.Excel.Application()
app.Visible = False
app.DisplayAlerts = False
wb = app.Workbooks.Open(str(XLSX))
app.CalculateFullRebuild()

ws = wb.Worksheets("估值系统")
for addr in ["B7", "B9", "B14", "B17", "B19", "B47", "B48", "B49", "B52", "B53",
             "B54", "B60", "B69", "B70", "B71", "B72", "B77", "B78", "B84", "B85"]:
    print("估值系统", addr, ws.Range(addr).Value)

ws2 = wb.Worksheets("估值与假设")
for addr in ["B10", "B14", "G18", "G20", "G22", "B40", "B41", "B42", "C40", "C41", "C42"]:
    print("假设", addr, ws2.Range(addr).Value)

ws3 = wb.Worksheets("一图流")
for addr in ["B10", "B11", "B12", "B13", "B14", "B15", "F10", "F11", "F12", "F13", "F14", "F15"]:
    print("一图流", addr, ws3.Range(addr).Value)

# error scan
errs = []
for sh in wb.Worksheets:
    used = sh.UsedRange
    vals = used.Value
    if vals is None:
        continue
    if not isinstance(vals, tuple):
        vals = ((vals,),)
    for i, row in enumerate(vals, 1):
        for j, v in enumerate(row, 1):
            if isinstance(v, str) and v.startswith("#"):
                errs.append((sh.Name, i, j, v))
print("ERRORS", len(errs))
for e in errs[:30]:
    print(e)

wb.Save()
wb.Close(SaveChanges=True)
app.Quit()
print("saved")
