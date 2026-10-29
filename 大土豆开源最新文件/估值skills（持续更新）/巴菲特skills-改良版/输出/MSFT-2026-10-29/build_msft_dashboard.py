# -*- coding: utf-8 -*-
"""Render the MSFT valuation dashboard as SVG + PNG (Chrome headless)."""
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
SVG = BASE / "MSFT-估值仪表盘-2026-10-29.svg"
HTML = BASE / "MSFT-估值仪表盘-2026-10-29.html"
PNG = BASE / "MSFT-估值仪表盘-2026-10-29.png"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

W, H = 1200, 780
FONT = "Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
DARK = "#1F2933"
GREY = "#5B6770"
LIGHT = "#F7F4EC"
CREAM = "#E8E2D5"
RED = "#B23A2E"
GREEN = "#2F6B4F"
GOLD = "#C9A227"
BLUE = "#1A73E8"
BROWN = "#8C6D5A"
WHITE = "#FFFFFF"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=13, color=DARK, weight="normal", anchor="start", opacity=1.0):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" font-weight="{weight}" text-anchor="{anchor}" '
            f'opacity="{opacity}">{esc(s)}</text>')


def line(x1, y1, x2, y2, color=CREAM, width=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"{d}/>'


def rect(x, y, w, h, fill=WHITE, stroke=CREAM, rx=10, opacity=1.0):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" opacity="{opacity}"/>')


parts = []
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
parts.append(rect(0, 0, W, H, fill=LIGHT, stroke=LIGHT, rx=0))

# Header
parts.append(text(60, 52, "微软 MSFT · 巴菲特框架估值", 30, DARK, "bold"))
parts.append(text(60, 82, "好生意，合理价格，但没有安全边际｜结论：观察，等 FCF 拐点", 15, GREY))
parts.append(text(1140, 52, "价格日 2026-10-28", 12, GREY, anchor="end"))
parts.append(text(1140, 76, "盘后 $546.39｜收盘 $531.01", 12, GREY, anchor="end"))
parts.append(line(50, 100, 1150, 100, CREAM, 1))

# Top-left panel: scenario bars
parts.append(rect(50, 120, 540, 330))
parts.append(text(75, 155, "三情景每股价值 vs 现价", 18, DARK, "bold"))
parts.append(text(75, 178, "FCFF DCF；基准 WACC 8.8%，终值增长 3.5%", 12, GREY))
bar_x = 210
bar_max = 300
scale = bar_max / 900.0
bars = [
    ("悲观", 243.85, BROWN),
    ("基准", 540.34, GREEN),
    ("乐观", 838.66, GOLD),
    ("盘后价", 546.39, RED),
]
for i, (label, value, color) in enumerate(bars):
    y = 205 + i * 45
    w = value * scale
    parts.append(text(75, y + 17, label, 14, DARK, "bold" if label == "基准" else "normal"))
    parts.append(f'<rect x="{bar_x}" y="{y}" width="{w:.1f}" height="26" rx="5" fill="{color}" opacity="0.92"/>')
    shown = f"${value:,.0f}" if label != "盘后价" else f"${value:,.2f}"
    parts.append(text(bar_x + w + 9, y + 18, shown, 13, color, "bold"))
parts.append(text(75, 398, "基准 540 与盘后价几乎持平；收盘价 531 低 2%", 13, RED, "bold"))
parts.append(text(75, 422, "悲观 244；基准 540；乐观 839；盘后 546.4", 11, GREY))
parts.append(line(75, 433, 565, 433, CREAM, 1))

# Top-right panel: FCFF path
parts.append(rect(610, 120, 540, 330))
parts.append(text(635, 155, "基准情景 FCFF：2027 年触底后回升", 18, DARK, "bold"))
parts.append(text(635, 178, "十亿美元；Y1–Y10（约 2027–2036E）；Y1 58B", 12, GREY))

x0, x1 = 700, 1100
y0, y1 = 200, 380
vmin, vmax = 0.0, 350.0


def ymap(v):
    return y1 - (v - vmin) / (vmax - vmin) * (y1 - y0)


base = ymap(0)
parts.append(line(x0, base, x1, base, "#A8A095", 1.2))
for v in [0, 100, 200, 300]:
    y = ymap(v)
    parts.append(line(x0, y, x1, y, "#E5DFD3", 0.8, "2 4"))
    parts.append(text(x0 - 8, y + 4, f"{v}", 9, GREY, anchor="end"))

fcf = [58, 96, 142, 186, 220, 250, 274, 298, 316, 332]
years = [f"Y{i}" for i in range(1, 11)]
step = (x1 - x0) / len(fcf)
bw = 24
for i, (yr, v) in enumerate(zip(years, fcf)):
    cx = x0 + step * (i + 0.5)
    top = ymap(v)
    h = base - top
    parts.append(f'<rect x="{cx-bw/2:.1f}" y="{top:.1f}" width="{bw}" height="{h:.1f}" rx="3" fill="{GREEN}" opacity="0.85"/>')
    if i in (0, 2, 4, 6, 9):
        parts.append(text(cx, top - 6, f"{v}", 9, GREEN, "bold", "middle"))
    if i % 2 == 0:
        parts.append(text(cx, 398, str(yr), 8.5, GREY, anchor="middle"))

parts.append(text(635, 430, "Y1–Y3 capex 高峰，FCF 58→142B；Y10 332B", 10, GREY))
parts.append(text(635, 445, "关键变量是 capex 正常化速度，而非收入", 10, GREY))

# Bottom panel
parts.append(rect(50, 475, 1100, 250))
parts.append(text(75, 507, "估值交叉检查与关键事实", 18, DARK, "bold"))

# Left table
hy = 536
parts.append(text(75, hy, "指标", 10.5, GREY, "bold"))
parts.append(text(330, hy, "MSFT", 10.5, GREY, "bold"))
parts.append(text(470, hy, "参照", 10.5, GREY, "bold"))
parts.append(text(720, hy, "读数", 10.5, GREY, "bold"))
parts.append(line(75, hy + 10, 700, hy + 10, CREAM, 1))
rows = [
    ("EV / TTM EBIT", "25.1x", "Google 22.1x｜Apple ~32x", "居中", GOLD),
    ("P/E FY2027E", "27.3x", "Google 19.2x｜Apple ~36x", "居中", GOLD),
    ("FCF 收益率", "1.48%", "Google 0.55%｜Apple 2.55%", "居中", GOLD),
    ("EV / TTM FCF", "68x", "Google 175x｜Apple ~39x", "偏贵", RED),
    ("反推收入 CAGR", "10.9%", "基准 10.4%", "略高", GOLD),
]
for i, (a, b, c, d, color) in enumerate(rows):
    y = 566 + i * 29
    parts.append(text(75, y, a, 12, DARK, "bold" if i < 2 else "normal"))
    parts.append(text(330, y, b, 12, DARK, "bold"))
    parts.append(text(470, y, c, 10.5, GREY))
    parts.append(text(720, y, d, 11.5, color, "bold"))
    if i < len(rows) - 1:
        parts.append(line(75, y + 11, 700, y + 11, "#EEE8DC", 0.8))

# Right side: key facts / thesis
parts.append(line(790, 530, 790, 700, CREAM, 1))
parts.append(text(815, 536, "多空关键", 11, GREY, "bold"))
facts = [
    ("Azure", "+48%；33.2B；Q2 指引 49–50%"),
    ("Cloud", "Q1 63.9B +30%；RPO 677B +73%"),
    ("Capex", "FY27 约 170B；Q1 现金 39.4B（42%）"),
    ("FCF", "Q1 18.6B；TTM 60B；FY27E 触底 58B"),
    ("资本配置", "Q1 回报 10.2B；股息率 0.67%"),
    ("护城河", "Office/Windows 分发；企业信任"),
    ("风险", "折旧压利润率；反垄断；OpenAI 集中"),
]
for i, (k, v) in enumerate(facts):
    y = 560 + i * 24
    parts.append(text(815, y, k, 10.5, DARK, "bold"))
    parts.append(text(885, y, v, 10.5, GREY))

parts.append(text(75, 708, "结论：好生意，合理价格，没有安全边际；不追高，等 FCF 拐点或 20% 回调。", 12, RED, "bold"))
parts.append(text(75, 750, "数据：SEC 10-K/10-Q/8-K、微软业绩会、Yahoo Finance；估值假设见报告。非投资建议。", 9.3, GREY))

parts.append("</svg>")
svg = "\n".join(parts)
SVG.write_text(svg, encoding="utf-8")

html = f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
html,body{{margin:0;padding:0;background:{LIGHT};}}
svg{{display:block;width:{W}px;height:{H}px;}}
</style></head><body>
{svg}
</body></html>"""
HTML.write_text(html, encoding="utf-8")

cmd = [
    CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
    "--force-device-scale-factor=2", f"--window-size={W},{H}",
    f"--screenshot={PNG}", HTML.as_uri(),
]
subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
print("saved:", SVG)
print("saved:", HTML)
print("saved:", PNG, PNG.stat().st_size, "bytes")
