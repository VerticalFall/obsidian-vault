# -*- coding: utf-8 -*-
"""Render the GOOGL valuation dashboard as SVG + PNG (Chrome headless)."""
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
SVG = BASE / "GOOGL-估值仪表盘-2026-10-29.svg"
HTML = BASE / "GOOGL-估值仪表盘-2026-10-29.html"
PNG = BASE / "GOOGL-估值仪表盘-2026-10-29.png"
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


def circle(x, y, r, fill=GREEN, stroke=WHITE, sw=2):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


parts = []
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
parts.append(rect(0, 0, W, H, fill=LIGHT, stroke=LIGHT, rx=0))

# Header
parts.append(text(60, 52, "Alphabet GOOGL · 巴菲特框架估值", 30, DARK, "bold"))
parts.append(text(60, 82, "好生意，但正在用现金换 AI 未来｜价格大致合理，没有安全边际｜结论：观察", 15, GREY))
parts.append(text(1140, 52, "价格日 2026-10-28", 12, GREY, anchor="end"))
parts.append(text(1140, 76, "盘后 $291.50｜收盘 $324.89", 12, GREY, anchor="end"))
parts.append(line(50, 100, 1150, 100, CREAM, 1))

# Top-left panel: scenario bars
parts.append(rect(50, 120, 540, 330))
parts.append(text(75, 155, "三情景每股价值 vs 现价", 18, DARK, "bold"))
parts.append(text(75, 178, "FCFF DCF；基准 WACC 8.8%，终值增长 3.5%", 12, GREY))
bar_x = 210
bar_max = 300
scale = bar_max / 600.0
bars = [
    ("悲观", 125.95, BROWN),
    ("基准", 270.20, GREEN),
    ("乐观", 566.36, GOLD),
    ("盘后价", 291.50, RED),
]
for i, (label, value, color) in enumerate(bars):
    y = 205 + i * 45
    w = value * scale
    parts.append(text(75, y + 17, label, 14, DARK, "bold" if label == "基准" else "normal"))
    parts.append(f'<rect x="{bar_x}" y="{y}" width="{w:.1f}" height="26" rx="5" fill="{color}" opacity="0.92"/>')
    shown = f"${value:,.0f}" if label != "盘后价" else f"${value:,.2f}"
    parts.append(text(bar_x + w + 9, y + 18, shown, 13, color, "bold"))
parts.append(text(75, 398, "基准 270 较盘后价低 7%，较收盘价低 17%", 13, RED, "bold"))
parts.append(text(75, 422, "悲观 126；基准 270；乐观 566；盘后 291.5", 11, GREY))
parts.append(line(75, 433, 565, 433, CREAM, 1))

# Top-right panel: FCFF path
parts.append(rect(610, 120, 540, 330))
parts.append(text(635, 155, "基准情景 FCFF：先负后正", 18, DARK, "bold"))
parts.append(text(635, 178, "十亿美元；Y1–Y10（约 2027–2036E）；Y4 转正", 12, GREY))

x0, x1 = 700, 1100
y0, y1 = 200, 380  # y0 = +350, y1 = -150
vmin, vmax = -150.0, 350.0


def ymap(v):
    return y1 - (v - vmin) / (vmax - vmin) * (y1 - y0)


base = ymap(0)
parts.append(line(x0, base, x1, base, "#A8A095", 1.2))
for v in [-100, 0, 100, 200, 300]:
    y = ymap(v)
    parts.append(line(x0, y, x1, y, "#E5DFD3", 0.8, "2 4"))
    parts.append(text(x0 - 8, y + 4, f"{v}", 9, GREY, anchor="end"))

fcf = [-49, -112, -43, 52, 126, 184, 224, 253, 283, 312]
years = [f"Y{i}" for i in range(1, 11)]
step = (x1 - x0) / len(fcf)
bw = 24
for i, (yr, v) in enumerate(zip(years, fcf)):
    cx = x0 + step * (i + 0.5)
    top = min(base, ymap(v))
    h = abs(ymap(v) - base)
    color = RED if v < 0 else GREEN
    parts.append(f'<rect x="{cx-bw/2:.1f}" y="{top:.1f}" width="{bw}" height="{h:.1f}" rx="3" fill="{color}" opacity="0.88"/>')
    if i in (0, 1, 2, 3, 9):
        parts.append(text(cx, ymap(v) + (-8 if v >= 0 else 14), f"{v}", 9,
                          color, "bold", "middle"))
    if i % 2 == 0:
        parts.append(text(cx, 398, str(yr), 8.5, GREY, anchor="middle"))

parts.append(text(635, 430, "Y1–Y3 为负；Y4 转正；Y10 终值 FCF 312B", 10, GREY))
parts.append(text(635, 445, "资本开支高峰是现金流拐点的关键", 10, GREY))

# Bottom panel
parts.append(rect(50, 475, 1100, 250))
parts.append(text(75, 507, "估值交叉检查与关键事实", 18, DARK, "bold"))

# Left table
hy = 536
parts.append(text(75, hy, "指标", 10.5, GREY, "bold"))
parts.append(text(330, hy, "GOOGL", 10.5, GREY, "bold"))
parts.append(text(470, hy, "参照", 10.5, GREY, "bold"))
parts.append(text(720, hy, "读数", 10.5, GREY, "bold"))
parts.append(line(75, hy + 10, 700, hy + 10, CREAM, 1))
rows = [
    ("EV / TTM EBIT", "22.1x", "Apple ~32x", "便宜", GREEN),
    ("P/E 2027E", "19.2x", "Apple ~36x", "便宜", GREEN),
    ("FCF 收益率", "0.55%", "Apple 2.55%", "现金少", RED),
    ("EV / TTM FCF", "175x", "Apple ~39x", "极贵", RED),
    ("反推收入 CAGR", "13.4%", "基准 12.2%", "略高", GOLD),
]
for i, (a, b, c, d, color) in enumerate(rows):
    y = 566 + i * 29
    parts.append(text(75, y, a, 12, DARK, "bold" if i < 2 else "normal"))
    parts.append(text(330, y, b, 12, DARK, "bold"))
    parts.append(text(470, y, c, 11, GREY))
    parts.append(text(720, y, d, 11.5, color, "bold"))
    if i < len(rows) - 1:
        parts.append(line(75, y + 11, 700, y + 11, "#EEE8DC", 0.8))

# Right side: key facts / thesis
parts.append(line(790, 530, 790, 700, CREAM, 1))
parts.append(text(815, 536, "多空关键", 11, GREY, "bold"))
facts = [
    ("Cloud", "+103% YoY；利润率 36.2%；backlog 561B"),
    ("Capex", "2026 195–205B；2027 显著增加（>300B）"),
    ("FCF", "TTM 19.7B；Q3 为 -9.1B；capex/收入 34%"),
    ("资本配置", "回购暂停；2026 YTD 发债 85B、ATM 43B"),
    ("护城河", "Search 63B/季；Gemini 10 亿用户；TPU 外供"),
    ("风险", "Search 被 AI 分流；反垄断；折旧压利润率"),
]
for i, (k, v) in enumerate(facts):
    y = 562 + i * 26
    parts.append(text(815, y, k, 10.5, DARK, "bold"))
    parts.append(text(885, y, v, 10.5, GREY))

parts.append(text(75, 710, "结论：好生意，但价格没有安全边际；等 FCF 拐点，而不是追资本开支的故事。", 12, RED, "bold"))
parts.append(text(75, 732, "数据：SEC 10-K/8-K、Alphabet 业绩会、Yahoo Finance、StockAnalysis；估值假设见报告。非投资建议。", 9.3, GREY))

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
