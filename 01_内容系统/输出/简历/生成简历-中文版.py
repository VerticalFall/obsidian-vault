# -*- coding: utf-8 -*-
"""
生成中文简历：杨洛华 / 数据分析师（2026 届）
内容对应 Luohua_Yang_CV_DataAnalyst.pdf（英文原版，1 页），经用户确认的改动：
  1. 删除英国地区（Selly Oak, Birmingham, UK）与英国手机号(+44 7906 84527)
  2. 电话改为国内手机号 13025537306
  3. 邮箱改为 1771602053@qq.com
  4. LinkedIn 使用真实短链；GitHub 保留
  5. 结构、项目、数据、时间全部忠实对应英文原稿

排版采用"固定行高"（exact line spacing），保证在 Word 中稳定落在 1 页 A4。
"""
import io
import sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

OUT = r"C:\Users\user\Documents\Obsidian Vault\01_内容系统\输出\简历\杨洛华-数据分析师-中文简历.docx"

CN = "微软雅黑"
EN = "Calibri"

BODY = 9.5         # 正文
BODY_LH = 11.0     # 正文固定行高
SEC = 10.5         # 小节标题
SEC_LH = 13.0
ENTRY = 9.5        # 项目/职位标题行
ENTRY_LH = 11.8
TEXT_W = 18.2      # 正文可用宽度(cm)，对应左右边距 1.4cm


def set_run(run, size=BODY, bold=False, color="000000"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = EN
    run.font.color.rgb = RGBColor.from_string(color)
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), EN)
    rfonts.set(qn("w:hAnsi"), EN)
    rfonts.set(qn("w:eastAsia"), CN)
    # 固定行高，避免 Word 自动行距撑高版面
    return run


def para(doc, space_before=0, space_after=2, line_pt=None, align=None, keep_next=False):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    if line_pt:
        pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        pf.line_spacing = Pt(line_pt)
    if align is not None:
        p.alignment = align
    if keep_next:
        pf.keep_with_next = True
    return p


def add_bottom_border(p, sz=6, color="808080"):
    ppr = p._element.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(sz))
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), color)
    borders.append(bottom)
    ppr.append(borders)


def section(doc, text):
    p = para(doc, space_before=4, space_after=1.5, line_pt=SEC_LH, keep_next=True)
    set_run(p.add_run(text), size=SEC, bold=True, color="1F3864")
    add_bottom_border(p)
    return p


def entry(doc, left, right=""):
    p = para(doc, space_before=3, space_after=1, line_pt=ENTRY_LH, keep_next=True)
    set_run(p.add_run(left), size=ENTRY, bold=True)
    if right:
        p.paragraph_format.tab_stops.add_tab_stop(Cm(18.2), WD_TAB_ALIGNMENT.RIGHT)
        set_run(p.add_run("\t" + right), size=9.0, color="404040")
    return p


def bullet(doc, segments):
    p = doc.add_paragraph(style="List Bullet")
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(1.5)
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(BODY_LH)
    pf.left_indent = Cm(0.48)
    pf.first_line_indent = Cm(-0.32)
    if isinstance(segments, str):
        segments = [(segments, False)]
    for text, bold in segments:
        set_run(p.add_run(text), size=BODY, bold=bold)
    return p


doc = Document()

sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.top_margin = Cm(1.2)
sec.bottom_margin = Cm(1.2)
sec.left_margin = Cm(1.4)
sec.right_margin = Cm(1.4)

style = doc.styles["Normal"]
style.font.name = EN
style.font.size = Pt(BODY)
style.element.rPr.rFonts.set(qn("w:eastAsia"), CN)

# ─────────── 抬头 ───────────
p = para(doc, space_after=1.5, line_pt=24, align=WD_ALIGN_PARAGRAPH.CENTER)
set_run(p.add_run("杨洛华"), size=18, bold=True)

p = para(doc, space_after=1.5, line_pt=14, align=WD_ALIGN_PARAGRAPH.CENTER)
set_run(p.add_run("数据分析师 · 2026 届毕业生"), size=10.5, color="404040")

p = para(doc, space_after=0, line_pt=12.5, align=WD_ALIGN_PARAGRAPH.CENTER)
set_run(
    p.add_run("13025537306  •  1771602053@qq.com  •  "
              "linkedin.com/in/洛华-杨-3ba236406  •  github.com/VerticalFall"),
    size=9.0,
)

# ─────────── 个人简介 ───────────
section(doc, "个人简介")
p = para(doc, space_after=2, line_pt=BODY_LH)
set_run(p.add_run(
    "伯明翰大学统计学（数据科学方向）硕士，擅长把原始数据转化为清晰、可落地的洞察："
    "从定时采集与存储，到 SQL 分析、BI 看板，再到面向业务方的汇报材料。熟练使用 SQL 与 Python"
    "（pandas、NumPy），具备搭建交互式看板（Tableau、ECharts）并将分析结论转化为业务建议的能力。"
    "中英文双语工作无障碍，统计学与金融学背景使分析始终扎根于真实业务问题。"
))

# ─────────── 精选项目 ───────────
section(doc, "精选项目")

entry(doc, "stock-monitor · 多市场个股分析与每日报告系统", "2025 – 2026")
bullet(doc, "搭建每日选股看板，将人工研究时间压缩约 90%，每天在 4 个市场中自动筛出 5 个以上可操作的买入区间标的。")
bullet(doc, "以 Flask + ECharts 看板交付（K 线图、双因子雷达图、安全边际买入区间），覆盖 20 余只股票；数据来自多源管线"
            "（yfinance，AKShare/baostock 兜底；Tavily 新闻），由 GitHub Actions 每日定时调度并推送飞书预警。")
bullet(doc, "将估值成长性假设与三个独立来源交叉验证（PEG 隐含增速、市场一致预期、历史增速，上限设为 50%），避免单季度业绩波动扭曲结果。")
bullet(doc, "主导系统架构设计并负责代码评审，同时与 Claude Code 全程结对编程；源码见 github.com/VerticalFall/stock-monitor。")

entry(doc, "obsidian-vault · 全球新闻自动化知识库与每日简报", "2025 – 2026")
bullet(doc, "用 GitHub Actions 搭建数据管线，将四类内容源（AI 热点、跟踪的 X/Twitter 账号、热点榜单、AI 从业者的推文/博客/播客）聚合成结构化知识库。")
bullet(doc, "搭建选题路由管线，把每天 100 余篇文章提炼成 5 分钟中英双语简报；自 2026 年 7 月起已发布 160 余期，基础设施零成本。")
bullet(doc, "增加自动化的数据完整性与管线健康检查，在故障影响读者之前先行发现。")

# ─────────── 实习与项目经历 ───────────
section(doc, "实习与项目经历")

entry(doc, "数据运营实习生 · 探迹科技（Tungee，AI 销售情报 SaaS，约 1,000 人）", "2024.06 – 2024.09")
bullet(doc, "设计并落地定时数据管线，采集抖音、B 站 50 余个 KOL 账号的每日关键指标（粉丝数、播放量、评论数），取代人工每日登记，日均处理数万行数据。")
bullet(doc, "搭建交互式 Tableau 看板，对 KOL 内容表现做留存与漏斗分析，发现的趋势被用于每周内容复盘。")
bullet(doc, "把数据结论转化为内容策略建议，帮助运营团队识别高效内容形式的效率提升约 2 倍。")

entry(doc, "科研项目成员 · 广东外语外贸大学", "2021 – 2025")
bullet(doc, "负责东南亚数据源（泰国、印尼、新加坡）的采集：旅游/文化门户网站与政府新闻网站。")
bullet(doc, "搭建并维护每周定时增量爬虫（requests、MySQL），将新闻全文持续灌入偏好标注管线，可靠性与覆盖率随时间持续提升。")

# ─────────── 教育背景 ───────────
section(doc, "教育背景")

entry(doc, "伯明翰大学（University of Birmingham）· 统计学数据科学 硕士（预计获 Distinction）", "2025.09 – 2026.12")
bullet(doc, "在读；预计 2026 年 12 月毕业（学位授予时间）。")
bullet(doc, "毕业论文《金融新闻情感分析》：在 Financial PhraseBank 数据集（4,846 条、三分类、16 位金融专家标注）上对比"
            "生成式模型（朴素贝叶斯）与判别式模型（线性 SVM），检验 Ng–Jordan 学习曲线理论：小样本下生成式模型领先"
            "（交叉点约在 n≈256–512），全量数据上 SVM 最佳（准确率 0.757 对 0.698；宏平均 F1 0.691 对 0.515）。")
bullet(doc, "开展标注噪声敏感性与类别不平衡的鲁棒性实验，通过类别先验/权重调整，将少数类（负面类）召回率从 0.151 提升至 0.456。")
bullet(doc, "课程涵盖机器学习、统计学、深度学习、计量经济学。")

entry(doc, "广东外语外贸大学 · 统计学 学士", "2021 – 2025")
bullet(doc, "主要课程：概率论、数理统计、计量经济学。")

# ─────────── 核心技能 ───────────
section(doc, "核心技能")


def skill(label, value):
    p = para(doc, space_after=2, line_pt=BODY_LH)
    set_run(p.add_run(label), bold=True)
    set_run(p.add_run(value))


skill("数据分析：", "SQL（窗口函数、同期群/留存分析、漏斗分析）、Tableau、ECharts、看板设计、报表自动化管线")
skill("编程：", "Python（pandas、NumPy、scikit-learn）、SQL、JavaScript")
skill("数据运维：", "网页爬取（requests）、定时任务管线（GitHub Actions、cron）、MySQL、REST API 集成")
skill("机器学习 / AI：", "分类与情感分析；熟悉多家主流大模型服务商的接入与集成")
skill("工具：", "Git、Linux、Docker、Flask、飞书/Lark API、Claude Code")
skill("语言：", "中文（母语）、英语（专业工作水平）")

doc.save(OUT)
print("SAVED:", OUT)

