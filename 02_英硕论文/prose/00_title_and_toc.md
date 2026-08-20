# 标题页 + 目录（洛哥放入 Word 用）

> 本文件是**版式参考与占位骨架**，不是论文正文。
> 英文部分是可直接复制进 Word 的标题页内容；中文块注释是你需要核对/填写的地方。
> 对应 handbook 条款：§2.8（三版同标题）、§2.12（2cm 边距、12pt、15–18 页不含参考文献/附录）、§2.14（Draft 6–9 页、首页 Executive Summary、同标题同结构）、§2.16（终稿不含 Executive Summary、需随交 Plagiarism Declaration Form）。

---

## A. 标题页（Title Page）

```text
Generative versus Discriminative Classifiers for
Financial Sentiment Analysis: Naive Bayes and Support Vector
Machines on the Financial PhraseBank

                    [居中，加粗，上下留白]

A dissertation submitted in partial fulfilment of the requirements
for the degree of MSc in [洛哥填：学位项目全称，如 Mathematics / Mathematical
Finance / Statistics，与录取文件一致]

by

[洛哥填：你的全名]

Supervisor: [洛哥填：导师姓名]

School of Mathematics
University of Birmingham

[洛哥填：提交日期 —— Draft 约 2026 年 8 月 21 日；Final 不晚于 2026 年 9 月 18 日 16:00（handbook §2.16）]
```

**标题合规提示（handbook §2.8）**：上面这个标题就是工作标题（与 `00_thesis_skeleton.md` 一致）。标题一旦与导师确认，**Draft / Oral Exam / Final 三版必须完全相同**——改标题会影响评分一致性（Presentation 12 分里含 "coherence between written Dissertation and Draft and Oral Examination"）。不要为了 Draft 临时缩短标题。

**伦理提示（handbook §6.1，重要）**：手册规定"secondary data analysis and analysis of anonymised datasets"属于需要完整 Ethical Review 的情形。Financial PhraseBank 是公开、已授权（CC BY-NC-SA 3.0）的二手标注数据，但严格按字面属于二手数据分析。**请与导师确认是否需要填写 Ethical Review Form**（§6 规定责任在 supervisor）。至少 **Plagiarism Declaration Form 是必须**随终稿提交的（§2.16，不交则得 0 分，§4.4）。

**Word 版式三件事（handbook §2.12）**：① 页面边距 2 cm；② 正文字号 12 pt；③ 正文 15–18 页，**参考文献和附录不计入页数**（所以 Appendix A/B 可以放开写）。

**Draft 与 Final 的区别（§2.14 / §2.16）**：Draft 首页必须是 Executive Summary（6–9 页）；终稿**不含** Executive Summary。

---

## B. 目录（Table of Contents）

目录条目与 `论文.md` 的实际标题逐字对应。在 Word 里用"引用 → 目录"自动生成即可，页码自动填充；若手打，把 `[页码]` 替换成 Word 自动目录即可（不必手填）。

```text
Executive Summary .............................................. [页码]   ← 仅 Draft 版（§2.14）；终稿删除（§2.16）
1.  Introduction
    1.1  Motivation: financial sentiment and its difficulty ......... [页码]
    1.2  Generative versus discriminative: the theoretical question . [页码]
    1.3  Research questions and contributions ....................... [页码]
2.  Background & Related Work
    2.1  Financial sentiment analysis .............................. [页码]
    2.2  Ng–Jordan theory of learning curves ....................... [页码]
    2.3  The two classifiers
         2.3.1  Multinomial Naive Bayes ............................ [页码]
         2.3.2  Linear SVM ......................................... [页码]
    2.4  Classic models in the LLM era ............................. [页码]
    2.5  Label noise and class imbalance ........................... [页码]
3.  Methodology
    3.1  Data: the Financial PhraseBank ............................ [页码]
    3.2  Preprocessing and features ................................ [页码]
    3.3  Models and hyperparameters ................................ [页码]
    3.4  RQ1 design: learning curves ............................... [页码]
    3.5  RQ2 design: agreement as a label-noise proxy ............... [页码]
    3.6  RQ3 design: recovering the rare negative class ............. [页码]
    3.7  Evaluation ................................................ [页码]
4.  Experiments & Results
    4.1  Baseline and overall comparison ........................... [页码]
    4.2  RQ1: learning curves ...................................... [页码]
    4.3  RQ2: robustness to label uncertainty ...................... [页码]
    4.4  RQ3: recovering the negative class ........................ [页码]
    4.5  Summary of findings ....................................... [页码]
5.  Discussion
    5.1  The Ng–Jordan prediction holds under accuracy, but not under macro-F1 [页码]
    5.2  The minority class as the persistent weakness of the generative model [页码]
    5.3  Practical implications .................................... [页码]
    5.4  Limitations ............................................... [页码]
    5.5  Future work ............................................... [页码]
6.  Conclusion .................................................... [页码]
References ....................................................... [页码]
Appendix A: Error decomposition of generative and discriminative learning [页码]
Appendix B: Experimental configuration ........................... [页码]
```

> 备注：骨架里还规划过 **Appendix C（完整分类报告 / fixed-pool 曲线 / 混淆矩阵）**。你这次只要 A 和 B；若保留 C，记得在目录里加一行，并把 A/B/C 的字母与正文引用保持一致（正文目前只提到 Appendix A 和 Appendix B，见 `论文.md` §2.2 / §3.7）。
