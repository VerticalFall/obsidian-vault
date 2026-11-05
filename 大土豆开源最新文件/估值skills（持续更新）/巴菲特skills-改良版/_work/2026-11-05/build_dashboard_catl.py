# -*- coding: utf-8 -*-
"""宁德时代 300750.SZ 估值仪表盘（1200×780，2x PNG）"""
import sys, subprocess, tempfile
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catl_data as D

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / "输出" / "A股" / f"300750.SZ-{D.DATE}"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

BG = "#F7F4EC"; CARD = "#FFFFFF"; BORDER = "#E8E2D5"; INK = "#1F2933"; MUTED = "#5B6770"
GREEN = "#2F6B4F"; BROWN = "#8C6D5A"; GOLD = "#C9A227"; RED = "#B23A2E"; BLUE = "#1A73E8"
FONT = "Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"


def t(x, y, s, size=12, color=INK, weight="normal", anchor="start", opacity=1.0):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{color}" '
            f'font-weight="{weight}" text-anchor="{anchor}" opacity="{opacity}">{escape(str(s))}</text>')


def rect(x, y, w, h, fill=CARD, stroke=BORDER, rx=10, opacity=1.0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" opacity="{opacity}"/>'


def line(x1, y1, x2, y2, color=BORDER, width=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"{d}/>'


def scenario_chart():
    svg = []
    svg.append(t(75, 155, "三情景每股价值 vs 现价", 18, INK, "bold"))
    svg.append(t(75, 178, "FCFF DCF 与 PE 各 50%；PE 用 2027E EPS", 12, MUTED))
    names = ["悲观", "基准", "乐观", "现价"]
    vals = [D.BLEND_BEAR, D.BLEND_BASE, D.BLEND_BULL, D.PRICE]
    colors = [BROWN, GREEN, GOLD, RED]
    maxv = max(vals) * 1.06
    for i, (n, v, col) in enumerate(zip(names, vals, colors)):
        y = 205 + i * 45
        svg.append(t(75, y + 19, n, 14, INK, "bold" if n == "基准" else "normal"))
        w = max(6, v / maxv * 260)
        svg.append(f'<rect x="210" y="{y}" width="{w:.1f}" height="26" rx="5" fill="{col}" opacity="0.92"/>')
        svg.append(t(218 + w, y + 19, f"¥{v:.2f}", 12.5, col, "bold"))
    svg.append(t(75, 398, f"现价较基准低 {(1 - D.PRICE / D.BLEND_BASE) * 100:.1f}%", 13, GREEN, "bold"))
    svg.append(t(75, 422, f"悲观 ¥{D.BLEND_BEAR:.2f}；基准 ¥{D.BLEND_BASE:.2f}；乐观 ¥{D.BLEND_BULL:.2f}", 11, MUTED))
    svg.append(line(75, 433, 565, 433))
    return "".join(svg)


def trend_chart():
    svg = []
    svg.append(t(635, 155, "归母净利润（亿元）", 18, INK, "bold"))
    svg.append(t(635, 178, "2021–2025 年度；2026E 为机构一致预期", 12, MUTED))
    years = D.YEARS + ["2026E"]
    vals = D.NP + [D.NP_2026E]
    maxv = max(vals) * 1.18
    base_y, top_y, x0, step, barw = 380.0, 205.0, 695, 67, 38
    for frac in [0, 0.25, 0.5, 0.75, 1.0]:
        y = base_y - frac * (base_y - top_y)
        svg.append(line(700, y, 1100, y, "#E5DFD3", 0.8, "2 4"))
        svg.append(t(692, y + 3.5, f"{maxv * frac:,.0f}", 9, MUTED, anchor="end"))
    for i, (yr, v) in enumerate(zip(years, vals)):
        h = max(3, v / maxv * (base_y - top_y))
        x = x0 + i * step
        col = BLUE if yr != "2026E" else "#7FA8D9"
        svg.append(f'<rect x="{x}" y="{base_y - h:.1f}" width="{barw}" height="{h:.1f}" rx="3" fill="{col}" opacity="0.9"/>')
        svg.append(t(x + barw / 2, base_y - h - 7, f"{v:,.0f}", 9, BLUE, "bold", "middle"))
        svg.append(t(x + barw / 2, 398, yr, 8.5, MUTED, anchor="middle"))
    svg.append(t(635, 428, "2026 9M 净利 645.3 亿（+31.6%）；Q3 单位盈利约 0.082 元/Wh", 10, MUTED))
    svg.append(t(635, 444, "税负：消费税 2027-09 升至 4%；出口退税 2027-01 取消", 10, RED))
    return "".join(svg)


def bottom_panel():
    svg = []
    svg.append(rect(50, 475, 1100, 250))
    svg.append(t(75, 507, "估值交叉与关键读数", 18, INK, "bold"))
    headers = ["项目", "结果", "说明"]
    for x, h in zip([75, 330, 470], headers):
        svg.append(t(x, 536, h, 10.5, MUTED, "bold"))
    svg.append(line(75, 546, 700, 546))
    rows = [
        ("FCFF DCF", f"¥{D.DCF_BASE:.2f}", "WACC 7.8%、g 2.5%、10 年 fade"),
        ("PE 法", f"¥{D.PE_BASE_V:.2f}", "2027E EPS 22.50 × 15.3x"),
        ("综合基准", f"¥{D.BLEND_BASE:.2f}", "DCF 50% + PE 50%"),
        ("现价", f"¥{D.PRICE:.2f}", f"市值 {D.MARKET_CAP:,.0f} 亿"),
        ("安全边际", f"+{D.MOS * 100:.1f}%", "1 − 现价 / 基准"),
        ("20% 边际价", f"¥{D.MOS20_PRICE:.2f}", "基准 × 0.8"),
    ]
    for i, (a, b, c) in enumerate(rows):
        y = 562 + i * 24
        svg.append(t(75, y, a, 11.5, INK, "bold" if a in ("综合基准", "安全边际") else "normal"))
        col = GREEN if a in ("综合基准", "安全边际") else INK
        svg.append(t(330, y, b, 11.5, col, "bold"))
        svg.append(t(470, y, c, 10, MUTED))
        if i < len(rows) - 1:
            svg.append(line(75, y + 10, 700, y + 10, "#EEE8DC", 0.8))
    svg.append(line(720, 530, 720, 700))
    svg.append(t(745, 536, "多空关键", 11, MUTED, "bold"))
    facts = [
        ("2026E PE", "13.6x", GREEN),
        ("2027E PE", "11.8x", GREEN),
        ("净现金", "2,427 亿", INK),
        ("股息率（总）", "3.7%", INK),
        ("回购上限", "400 亿", INK),
        ("2026Q3 毛利率", "20.7%", RED),
    ]
    for i, (k, v, col) in enumerate(facts):
        y = 562 + i * 24
        svg.append(t(745, y, k, 10.5, INK, "bold"))
        svg.append(t(870, y, v, 10.5, col, "bold" if col != INK else "normal"))
    concl = "便宜，但有条件的便宜：基准 347 元，现价 265.94 元；前提是税负部分转嫁、单位盈利不破 0.07 元/Wh。"
    svg.append(t(75, 708, concl, 11.6, GREEN, "bold"))
    svg.append(t(75, 738, "数据截至 2026-09-30 财报；价格日 2026-11-05 午间；来源见报告「数据与来源」。不构成投资建议。", 9.3, MUTED))
    return "".join(svg)


def build_svg():
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="780" viewBox="0 0 1200 780">']
    svg.append(rect(0, 0, 1200, 780, BG, BG, 0))
    svg.append(t(60, 52, "宁德时代 300750.SZ · 巴菲特框架估值", 30, INK, "bold"))
    svg.append(t(60, 82, "全球动力电池 39.2% + 储能 30.4%｜周期成长股，不是红利股", 14.5, MUTED))
    svg.append(t(1140, 52, "价格日 2026-11-05 午间", 12, MUTED, anchor="end"))
    svg.append(t(1140, 76, f"现价 ¥{D.PRICE:.2f}｜市值 {D.MARKET_CAP:,.0f} 亿", 12, MUTED, anchor="end"))
    svg.append(line(50, 100, 1150, 100))
    svg.append(rect(50, 120, 540, 330))
    svg.append(scenario_chart())
    svg.append(rect(610, 120, 540, 330))
    svg.append(trend_chart())
    svg.append(bottom_panel())
    svg.append("</svg>")
    return "".join(svg)


def build_html(svg):
    return ("<!doctype html><html><head><meta charset=\"utf-8\"><style>"
            "html,body{margin:0;padding:0;background:#F7F4EC;}svg{display:block;width:1200px;height:780px;}"
            "</style></head><body>" + svg + "</body></html>")


def render_png(html_path, png_path):
    raw = Path(tempfile.gettempdir()) / (png_path.stem + "_raw.png")
    if raw.exists():
        raw.unlink()
    cmd = [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
           "--force-device-scale-factor=2", "--window-size=1200,780",
           f"--screenshot={raw}", html_path.as_uri()]
    subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
    from PIL import Image
    im = Image.open(raw).convert("RGB")
    im = im.crop((0, 0, 2400, 1560))
    im.save(png_path, optimize=True)
    print("saved", png_path, im.size)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    svg = build_svg()
    base = f"300750.SZ-估值仪表盘-{D.DATE}"
    (OUT / f"{base}.svg").write_text(svg, encoding="utf-8")
    (OUT / f"{base}.html").write_text(build_html(svg), encoding="utf-8")
    render_png(OUT / f"{base}.html", OUT / f"{base}.png")
