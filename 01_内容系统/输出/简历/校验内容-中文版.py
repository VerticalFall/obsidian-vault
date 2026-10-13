# -*- coding: utf-8 -*-
"""终版 DOCX 校验：结构、字体、页边距、遗留内容。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from docx import Document

DOCX = r"C:\Users\user\Documents\Obsidian Vault\01_内容系统\输出\简历\杨洛华-数据分析师-中文简历.docx"
d = Document(DOCX)
ps = [p for p in d.paragraphs if p.text.strip()]
s = d.sections[0]

print("段落数:", len(ps))
print("首段:", ps[0].text)
print("末段:", ps[-1].text)
print("页边距(cm): 上 %.2f 下 %.2f 左 %.2f 右 %.2f" %
      (s.top_margin.cm, s.bottom_margin.cm, s.left_margin.cm, s.right_margin.cm))
print("页面(cm): %.1f × %.1f" % (s.page_width.cm, s.page_height.cm))

bad = [p.text for p in ps if any(k in p.text for k in
       ("——", "Selly", "Birmingham, UK", "+44", "1771602053az"))]
print("遗留待清理内容:", bad if bad else "无 ✓")

print("\n=== 全文 ===")
for p in ps:
    indent = "  •" if p.style.name == "List Bullet" else "   "
    print(indent, p.text)
