# -*- coding: utf-8 -*-
"""
用 PIL(FreeType) 精确排版 + 页面高度核算。
PIL font.getlength() 返回 FreeType 真实 advance，对 CJK 与拉丁都权威。
换行规则模拟 Word 的东亚版式：CJK 逐字断行、拉丁按空格断行、标点避头尾。
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.text import WD_LINE_SPACING

DOCX = r"C:\Users\user\Documents\Obsidian Vault\01_内容系统\输出\简历\杨洛华-数据分析师-中文简历.docx"
PNG = r"C:\Users\user\Documents\Obsidian Vault\01_内容系统\输出\简历\杨洛华-数据分析师-中文简历-预览.png"
MSYH = r"C:\Windows\Fonts\msyh.ttc"
MSYHB = r"C:\Windows\Fonts\msyhbd.ttc"

SCALE = 4  # 4px/pt 超采样


def F(path, pt, idx=0):
    # 用点数*scale 作为像素尺寸，得到与 Word 一致的比例
    return ImageFont.truetype(path, int(round(pt * SCALE)), index=idx)


_cache = {}


def font(path, pt):
    k = (path, round(pt, 2))
    if k not in _cache:
        _cache[k] = F(path, pt)
    return _cache[k]


draw = ImageDraw.Draw(Image.new("L", (10, 10)))


def text_w(s, pt, bold=False):
    if not s:
        return 0.0
    f = font(MSYHB if bold else MSYH, pt)
    return draw.textlength(s, font=f) / SCALE


def measure(s, pt, bold=False):
    """(advance_pt, ink_x0, ink_x1) —— advance 用于排版，ink 用于绘制位置"""
    f = font(MSYHB if bold else MSYH, pt)
    adv = draw.textlength(s, font=f) / SCALE
    try:
        bb = f.getbbox(s)  # (x0,y0,x1,y1) in px
        return adv, bb[0] / SCALE, bb[2] / SCALE
    except Exception:
        return adv, 0.0, adv


# ───────── 读取 DOCX ─────────
doc = Document(DOCX)
s = doc.sections[0]
PW, PH = s.page_width.pt, s.page_height.pt
LM, RM, TM, BM = s.left_margin.pt, s.right_margin.pt, s.top_margin.pt, s.bottom_margin.pt
AVAIL = PW - LM - RM
BULLET_IND = 15.6      # 0.55cm
USABLE = PH - TM - BM

print(f"页面 {PW:.1f}×{PH:.1f}pt | 可用宽 {AVAIL:.2f}pt | 可用高 {USABLE:.2f}pt")

NO_START = set("，。、；：！？）》」』】…·%”’")
NO_END = set("（《「『【")


def wrap(segs, avail):
    """segs: [(text, bold, pt)] -> [[(tok,bold,pt),...], ...]"""
    toks = []
    for text, bold, pt in segs:
        cur = ""
        for ch in text:
            if ch == "\u00a0":
                ch = " "
            if ch == " " or "\u4e00" <= ch <= "\u9fff" or ch in NO_START or ch in NO_END or ch in "—“”‘’":
                if cur:
                    toks.append((cur, bold, pt)); cur = ""
                toks.append((ch, bold, pt))
            else:
                cur += ch
        if cur:
            toks.append((cur, bold, pt))

    lines, cur, w = [], [], 0.0
    for tok, bold, pt in toks:
        tw = text_w(tok, pt, bold)
        if cur and w + tw > avail + 0.5:
            if tok and tok[0] in NO_START:          # 标点不能行首 → 挤在本行
                cur.append((tok, bold, pt)); w += tw
                lines.append(cur); cur, w = [], 0.0
                continue
            lines.append(cur); cur, w = [], 0.0
            if tok == " ":                           # 行首空格丢弃
                continue
        cur.append((tok, bold, pt)); w += tw
    if cur:
        lines.append(cur)
    return lines or [[]]


rows = []
for p in doc.paragraphs:
    if not p.text.strip():
        continue
    pf = p.paragraph_format
    segs = [(r.text, bool(r.font.bold), r.font.size.pt if r.font.size else 9.5)
            for r in p.runs if r.text]
    if not segs:
        continue
    size = max(sz for _, _, sz in segs)
    is_sec = segs[0][1] and size >= 10.5
    is_bul = p.style.name == "List Bullet"
    lh = pf.line_spacing.pt if hasattr(pf.line_spacing, "pt") else size * 1.15
    rows.append(dict(
        segs=segs, size=size, is_sec=is_sec, is_bul=is_bul, lh=lh,
        sb=pf.space_before.pt if pf.space_before else 0.0,
        sa=pf.space_after.pt if pf.space_after else 0.0,
        center=p.alignment is not None and "CENTER" in str(p.alignment),
        tab="\t" in "".join(t for t, _, _ in segs),
    ))

# ───────── 高度核算 ─────────
y = TM
layout = []
total_body_lines = 0
for r in rows:
    ind = BULLET_IND if r["is_bul"] else 0.0
    avail = AVAIL - ind
    if r["tab"]:
        full = "".join(t for t, _, _ in r["segs"])
        left, right = full.split("\t")
        lw = text_w(left, r["size"], True)
        rw = text_w(right, 9.5, False)
        lines = 1 if lw + rw + 8 <= avail else 2
        nlines = lines
    else:
        segs = ([("• ", False, r["size"])] + r["segs"]) if r["is_bul"] else r["segs"]
        L = wrap(segs, avail)
        nlines = len(L)
        layout.append((r, L))
        total_body_lines += nlines
        y += r["sb"] + nlines * r["lh"] + r["sa"]
        if r["is_sec"]:
            y += 1
        continue
    layout.append((r, None))
    total_body_lines += nlines
    y += r["sb"] + nlines * r["lh"] + r["sa"]
    if r["is_sec"]:
        y += 1

print(f"正文行数 {total_body_lines} 行")
print(f"内容总高 {y:.1f}pt / 可用 {USABLE:.1f}pt -> "
      f"{'✅ 一页内，余 %.0fpt' % (USABLE - y) if y <= USABLE else '❌ 超出 %.0fpt（约 %.1f 行）' % (y - USABLE, (y - USABLE) / 11.6)}")

print("\n=== 多行段落明细 ===")
for r, L in layout:
    if L and len(L) > 1:
        w0 = sum(text_w(t, pt, b) for t, b, pt in L[0])
        print(f"  {len(L)}行 首行宽 {w0:6.1f}/{AVAIL - (BULLET_IND if r['is_bul'] else 0):.1f} | "
              f"{''.join(t for t, _, _ in r['segs'])[:30]}")

# ───────── 渲染 PNG ─────────
img = Image.new("RGB", (int(PW * SCALE), int(PH * SCALE)), "white")
d = ImageDraw.Draw(img)
y = TM
for r, L in layout:
    ind = BULLET_IND if r["is_bul"] else 0.0
    if r["is_sec"]:
        base = y + r["sb"] + r["lh"] * 0.78
        d.text((LM * SCALE, base * SCALE), "".join(t for t, _, _ in r["segs"]),
               font=font(MSYHB, r["size"]), fill=(31, 56, 100))
        y += r["sb"] + r["lh"] + r["sa"]
        d.line([(LM * SCALE, (y - 1) * SCALE), ((LM + AVAIL) * SCALE, (y - 1) * SCALE)],
               fill=(128, 128, 128), width=1)
        y += 1
        continue
    if r["center"]:
        txt = "".join(t for t, _, _ in r["segs"])
        bold = r["segs"][0][1]
        tw = text_w(txt, r["size"], bold)
        base = y + r["sb"] + r["lh"] * 0.78
        d.text(((PW - tw) / 2 * SCALE, base * SCALE), txt,
               font=font(MSYHB if bold else MSYH, r["size"]), fill=(0, 0, 0))
        y += r["sb"] + r["lh"] + r["sa"]
        continue
    if r["tab"]:
        full = "".join(t for t, _, _ in r["segs"])
        left, right = full.split("\t")
        base = y + r["sb"] + r["lh"] * 0.78
        d.text((LM * SCALE, base * SCALE), left, font=font(MSYHB, r["size"]), fill=(0, 0, 0))
        rw = text_w(right, 9.5)
        d.text(((LM + AVAIL - rw) * SCALE, base * SCALE), right,
               font=font(MSYH, 9.5), fill=(64, 64, 64))
        y += r["sb"] + r["lh"] + r["sa"]
        continue
    for ln in L:
        base = y + r["sb"] + r["lh"] * 0.78
        x = LM + ind
        for tok, bold, pt in ln:
            d.text((x * SCALE, base * SCALE), tok, font=font(MSYHB if bold else MSYH, pt),
                   fill=(0, 0, 0))
            x += text_w(tok, pt, bold)
        y += r["lh"]
        r["sb"] = 0
    y += r["sa"]

# 画一条"页面下边界"参考线
d.line([(0, (PH - BM) * SCALE), (PW * SCALE, (PH - BM) * SCALE)], fill=(255, 200, 200), width=2)
img.save(PNG)
print("\n预览 PNG:", PNG, img.size)
