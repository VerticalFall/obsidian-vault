# -*- coding: utf-8 -*-
"""Render the AAPL valuation dashboard as SVG + PNG (Chrome headless)."""
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
SVG = BASE / "AAPL-估值仪表盘-2026-10-29.svg"
HTML = BASE / "AAPL-估值仪表盘-2026-10-29.html"
PNG = BASE / "AAPL-估值仪表盘-2026-10-29.png"
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


def circle(x, y, r, fill=GREEN, stroke=WHITE, sw=2):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


parts = []
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
parts.append(rect(0, 0, W, H, fill=LIGHT, stroke=LIGHT, rx=0))

# Header
parts.append(text(60, 52, "苹果 AAPL · 巴菲特框架估值", 30, DARK, "bold"))
parts.append(text(60, 82, "好生意，但 5 万亿美元的价格没有安全边际｜结论：观察，不追高", 15, GREY))
parts.append(text(1140, 52, "价格日 2026-10-28", 12, GREY, anchor="end"))
parts.append(text(1140, 76, "收盘 $343.83｜市值 $5.02T", 12, GREY, anchor="end"))
parts.append(line(50, 100, 1150, 100, CREAM, 1))

# Top-left panel: scenario bars
parts.append(rect(50, 120, 540, 330))
parts.append(text(75, 155, "三情景每股价值 vs 现价", 18, DARK, "bold"))
parts.append(text(75, 178, "FCFF DCF；基准 WACC 9.6%，终值增长 3%", 12, GREY))
bar_x = 210
bar_max = 300
scale = bar_max / 360.0
bars = [
    ("悲观", 117.37, BROWN),
    ("基准", 177.32, GREEN),
    ("乐观", 260.11, GOLD),
    ("现价", 343.83, RED),
]
for i, (label, value, color) in enumerate(bars):
    y = 205 + i * 45
    w = value * scale
    parts.append(text(75, y + 17, label, 14, DARK, "bold" if label == "基准" else "normal"))
    parts.append(f'<rect x="{bar_x}" y="{y}" width="{w:.1f}" height="26" rx="5" fill="{color}" opacity="0.92"/>')
    parts.append(text(bar_x + w + 9, y + 18, f"${value:,.0f}", 13, color, "bold"))
parts.append(text(75, 398, "基准价值较现价低 48%；乐观情景仍低 24%", 13, RED, "bold"))
parts.append(text(75, 422, "现价 $343.83；基准 $177；悲观 $117；乐观 $260", 11, GREY))
parts.append(line(75, 433, 565, 433, CREAM, 1))

# Top-right panel: reverse DCF line chart
parts.append(rect(610, 120, 540, 330))
parts.append(text(635, 155, "反推 DCF：现价隐含的 10 年 FCFF 增速", 18, DARK, "bold"))
parts.append(text(635, 178, "终值增长 3%；横轴为 WACC；现价对应约 14.9%", 12, GREY))

x0, x1 = 705, 1108
y0, y1 = 195, 365  # y0 = 18%, y1 = 10%
gmin, gmax = 10.0, 18.0
wmin, wmax = 8.0, 10.5


def xmap(w):
    return x0 + (w - wmin) / (wmax - wmin) * (x1 - x0)


def ymap(g):
    return y1 - (g - gmin) / (gmax - gmin) * (y1 - y0)


# grid
for g in [10, 12, 14, 16, 18]:
    y = ymap(g)
    parts.append(line(x0, y, x1, y, "#E5DFD3", 1))
    parts.append(text(x0 - 10, y + 4, f"{g}%", 10, GREY, anchor="end"))
for w in [8.0, 8.5, 9.0, 9.5, 10.0, 10.5]:
    x = xmap(w)
    parts.append(line(x, y1, x, y1 + 5, "#CFC7B8", 1))
    parts.append(text(x, y1 + 20, f"{w:.1f}%", 10, GREY, anchor="middle"))

# 10.5% consensus revenue growth reference
y_cons = ymap(10.5)
parts.append(line(x0, y_cons, x1, y_cons, "#A8A095", 1.2, "4 4"))
parts.append(text(x1, y_cons - 7, "FY2027 收入共识 +10.5%", 10, GREY, anchor="end"))

# implied growth curve
points = [(8.0, 10.83), (8.5, 12.19), (9.0, 13.48), (9.5, 14.70), (9.6, 14.94), (10.0, 15.88), (10.5, 17.01)]
path = " ".join(("M" if i == 0 else "L") + f"{xmap(w):.1f},{ymap(g):.1f}" for i, (w, g) in enumerate(points))
parts.append(f'<path d="{path}" fill="none" stroke="{GREEN}" stroke-width="2.6" stroke-linejoin="round"/>')
for w, g in points:
    parts.append(circle(xmap(w), ymap(g), 3.6, GREEN, WHITE, 1.5))

# highlight 9.6%
xh, yh = xmap(9.6), ymap(14.94)
parts.append(line(xh, y0, xh, y1, RED, 1.2, "3 3"))
parts.append(circle(xh, yh, 6.2, RED, WHITE, 2))
parts.append(f'<rect x="{xh-58}" y="{yh-44}" width="116" height="30" rx="6" fill="{RED}"/>')
parts.append(text(xh, yh - 24, "9.6% → 14.9%", 11, WHITE, "bold", "middle"))
parts.append(text(635, 405, "过去 5 年 FCF CAGR 仅 1.5%（受营运资金影响）", 10, GREY))
parts.append(text(635, 422, "即便按 FY2027 收入共识 +10.5%，仍低于现价隐含的 14.9%", 10, GREY))

# Bottom panel: cross-checks
parts.append(rect(50, 475, 1100, 250))
parts.append(text(75, 507, "估值交叉检查：现价处于十年高位", 18, DARK, "bold"))
# table header
hy = 538
parts.append(text(75, hy, "指标", 11, GREY, "bold"))
parts.append(text(390, hy, "当前", 11, GREY, "bold"))
parts.append(text(570, hy, "历史 / 基准", 11, GREY, "bold"))
parts.append(text(900, hy, "读数", 11, GREY, "bold"))
parts.append(line(75, hy + 10, 1125, hy + 10, CREAM, 1))
rows = [
    ("P/E（TTM）", "39.4x", "5 年均值 31–33x", "高约 20–25%", RED),
    ("远期 P/E", "38.9x", "10 年均值 24.3x", "高约 60%", RED),
    ("EV/FCFF", "38.7x", "10 年中位数约 25x", "高约 55%", RED),
    ("FCF 收益率", "2.55%", "10Y 美债 5.03%", "低 2.48pp", RED),
]
for i, (a, b, c, d, color) in enumerate(rows):
    y = 568 + i * 32
    parts.append(text(75, y, a, 13, DARK, "bold" if i == 0 else "normal"))
    parts.append(text(390, y, b, 13, DARK, "bold"))
    parts.append(text(570, y, c, 13, GREY))
    parts.append(text(900, y, d, 13, color, "bold"))
    if i < len(rows) - 1:
        parts.append(line(75, y + 12, 1125, y + 12, "#EEE8DC", 1))

parts.append(text(75, 710, "结论：好公司，但价格没有安全边际；现价较基准价值高 94%。", 12, RED, "bold"))
parts.append(text(75, 732, "数据：SEC 10-K/10-Q、Apple Newsroom、Yahoo Finance、StockAnalysis、YCharts；估值假设见报告。非投资建议。", 9.5, GREY))

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
subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
print("saved:", SVG)
print("saved:", HTML)
print("saved:", PNG, PNG.stat().st_size, "bytes")
