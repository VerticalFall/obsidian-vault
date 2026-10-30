# -*- coding: utf-8 -*-
import sys, subprocess, tempfile
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model_config import COMPANIES

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / "输出" / "A股"
DATE = "2026-10-30"
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


def scenario_chart(c):
    svg = []
    svg.append(t(75, 155, "三情景每股价值 vs 现价", 18, INK, "bold"))
    svg.append(t(75, 178, {"600900.SH": "FCFF DCF 与 DDM 各 50%", "000001.SZ": "剩余收益 RI 70% + DDM 30%",
                            "601088.SH": "FCFF DCF 50% + DDM 30% + PE 20%"}[c.code], 12, MUTED))
    names = ["悲观", "基准", "乐观", "现价"]
    vals = [c.scenario_values["悲观"], c.scenario_values["基准"], c.scenario_values["乐观"], c.price]
    colors = [BROWN, GREEN, GOLD, RED]
    maxv = max(vals) * 1.06
    for i, (n, v, col) in enumerate(zip(names, vals, colors)):
        y = 205 + i * 45
        svg.append(t(75, y + 19, n, 14, INK, "bold" if n == "基准" else "normal"))
        w = max(6, v / maxv * 260)
        svg.append(f'<rect x="210" y="{y}" width="{w:.1f}" height="26" rx="5" fill="{col}" opacity="0.92"/>')
        svg.append(t(218 + w, y + 19, f"¥{v:.2f}", 12.5, col, "bold"))
    base = c.scenario_values["基准"]
    svg.append(t(75, 398, f"现价较基准{'低' if c.price < base else '高'} {abs(c.price / base - 1) * 100:.1f}%", 13,
                 RED if c.price > base else GREEN, "bold"))
    svg.append(t(75, 422, f"悲观 ¥{c.scenario_values['悲观']:.2f}；基准 ¥{c.scenario_values['基准']:.2f}；乐观 ¥{c.scenario_values['乐观']:.2f}", 11, MUTED))
    svg.append(line(75, 433, 565, 433))
    return "".join(svg)


def trend_chart(c):
    svg = []
    svg.append(t(635, 155, "归母净利润（亿元）", 18, INK, "bold"))
    svg.append(t(635, 178, "2021–2025 年度；2026E 为模型估计" if c.code != "000001.SZ" else "2021–2025 年度；2026E 为模型估计", 12, MUTED))
    years = c.years + ["2026E"]
    vals = c.net_profit + [c.net_profit_2026e]
    maxv = max(vals) * 1.18
    base_y = 380.0
    top_y = 205.0
    x0 = 695
    step = 67
    barw = 38
    # grid
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
    if c.code == "600900.SH":
        foot1 = "2026H1 净利 147.6 亿；Q3 发电量 -14.9%"
        foot2 = "2026E 净利 322 亿；分红率 70%"
    elif c.code == "000001.SZ":
        foot1 = "2026Q3 净利 391.9 亿；NIM 1.80%"
        foot2 = "不良 1.05%、拨备 214.75%、CET1 11.26%"
    else:
        foot1 = "2026Q3 净利 444.0 亿；煤价 448 元/吨"
        foot2 = "收购并表 11 家；资产负债率 40.8%"
    svg.append(t(635, 428, foot1, 10, MUTED))
    svg.append(t(635, 444, foot2, 10, MUTED))
    return "".join(svg)


def bottom_panel(c):
    svg = []
    svg.append(rect(50, 475, 1100, 250))
    svg.append(t(75, 507, "估值交叉检查与关键事实", 18, INK, "bold"))
    headers = ["指标", "标的", "参照", "读数"]
    xs = [75, 330, 470, 690]
    for x, h in zip(xs, headers):
        svg.append(t(x, 536, h, 10.5, MUTED, "bold"))
    svg.append(line(75, 546, 700, 546))
    rows = c.key_rows
    for i, row in enumerate(rows):
        y = 566 + i * 29
        svg.append(t(75, y, row[0], 12, INK, "bold" if i == 0 else "normal"))
        svg.append(t(330, y, row[1], 12, INK, "bold"))
        svg.append(t(470, y, row[2], 10.5, MUTED))
        good = row[3] in ("接近基准", "略低于基准", "高 ROE 支撑")
        bad = row[3] in ("高 36%", "为高位盈利付费", "股息模型更低", "股息模型偏谨慎")
        col = GREEN if good else (RED if bad else GOLD)
        svg.append(t(690, y, row[3], 11.5, col, "bold"))
        if i < len(rows) - 1:
            svg.append(line(75, y + 11, 700, y + 11, "#EEE8DC", 0.8))
    svg.append(line(800, 530, 800, 700))
    svg.append(t(820, 536, "多空关键", 11, MUTED, "bold"))
    facts = {
        "600900.SH": [("2026H1 净利", "+13.0%"), ("Q3 发电量", "-14.9%"), ("分红率", "≥70%"),
                      ("净债务", "2,735 亿"), ("2026E 股息率", "3.1%")],
        "000001.SZ": [("营收", "+2.4%"), ("净利", "+2.2%"), ("NIM", "1.80%"),
                      ("拨备覆盖率", "214.75%"), ("关注类", "2.07%")],
        "601088.SH": [("煤价", "448 元/吨"), ("自产煤毛利率", "42.4%"), ("电力毛利率", "13.4%"),
                      ("收购作价", "1,335.98 亿"), ("资产负债率", "40.8%")],
    }[c.code]
    for i, (k, v) in enumerate(facts):
        y = 560 + i * 24
        svg.append(t(820, y, k, 10.5, INK, "bold"))
        svg.append(t(930, y, v, 10.5, MUTED))
    concl = {
        "600900.SH": "合理偏贵：DCF/DDM 基准 27.59 元，现价 29.74 元；好资产，但价格已在上沿。",
        "000001.SZ": "静态便宜、动态偏贵：0.47 倍 PB 已定价 ROE 下行；现价高于基准约 5.5%。",
        "601088.SH": "昂贵：现价 51.99 元接近乐观情景 50.09 元；为周期高位盈利付费。",
    }[c.code]
    svg.append(t(75, 708, concl, 12, RED if c.price > c.blended_value * 1.15 else (GREEN if c.price < c.blended_value else GOLD), "bold"))
    svg.append(t(75, 750, "数据截至 2026-10-30；价格日 2026-10-30；不构成投资建议。", 9.3, MUTED))
    return "".join(svg)


def build_svg(c):
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="780" viewBox="0 0 1200 780">']
    svg.append(rect(0, 0, 1200, 780, BG, BG, 0))
    svg.append(t(60, 52, f"{c.name} {c.code} · 巴菲特框架估值", 30, INK, "bold"))
    svg.append(t(60, 82, c.subtitle, 14.5, MUTED))
    svg.append(t(1140, 52, "价格日 2026-10-30", 12, MUTED, anchor="end"))
    svg.append(t(1140, 76, f"2026-10-30 收盘 ¥{c.price:.2f}", 12, MUTED, anchor="end"))
    svg.append(line(50, 100, 1150, 100))
    svg.append(rect(50, 120, 540, 330))
    svg.append(scenario_chart(c))
    svg.append(rect(610, 120, 540, 330))
    svg.append(trend_chart(c))
    svg.append(bottom_panel(c))
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


def main():
    for c in COMPANIES:
        outdir = OUT / f"{c.code}-{DATE}"
        outdir.mkdir(parents=True, exist_ok=True)
        svg = build_svg(c)
        base = f"{c.code}-估值仪表盘-{DATE}"
        (outdir / f"{base}.svg").write_text(svg, encoding="utf-8")
        (outdir / f"{base}.html").write_text(build_html(svg), encoding="utf-8")
        render_png(outdir / f"{base}.html", outdir / f"{base}.png")


if __name__ == "__main__":
    main()
