# 论文骨架（洛哥写作用的结构底稿）

> **这是骨架，不是正文。** 所有需要你写的地方用 `[洛哥填：...]` 标出。
> 词数为建议预算（1.5 倍行距 ≈ 400 词/页）；图/表与 References/Appendix 不计页。
> 初稿（8/21，6–9 页）与终稿（9/18，15–18 页）**同一标题、同一结构**；Executive Summary 仅初稿有。

**工作标题**（首次督导会与导师定稿后保持 Draft/Oral/Final 一致）：
> Generative versus Discriminative Classifiers for Financial Sentiment Analysis: Naive Bayes and Support Vector Machines on the Financial PhraseBank

---

## Executive Summary（仅初稿，~350 词，第 1 页）

问题 → 方法 → 三 RQ 主要发现（每个发现 1–2 句，给数字）→ 结论一句。

> 写最后（8/20），等正文字数和数字都定了再写。结构见 `04_paragraph_templates.md`。

## 1. Introduction（1.5 页，~650 词）

**1.1 Motivation: financial sentiment and its difficulty**
- 金融文本情感为什么有价值（市场、风险、投资者）
- 领域语义难点：`[洛哥填：用自己的话说清 "costs fell is good, profits fell is bad"]`
- 稀缺数据现实 → 引出小样本问题

**1.2 Generative vs discriminative: the theoretical question**
- Ng–Jordan 理论一句话
- 为什么用 NB（生成式代表）vs SVM（判别式代表）
- `[洛哥填：为什么聚焦线性模型而非 LLM——一句话定位，见 2.4]`

**1.3 Research questions and contributions**
- RQ1 / RQ2 / RQ3（三行，每行 1–2 句）
- 贡献点 2–3 个（bullet）
- 论文结构预览（一段，可参考 §5 结构一句话带过）

## 2. Background & Related Work（2.5 页，~1,100 词）

**2.1 Financial sentiment analysis**
- 词典法（Loughran–McDonald / Tetlock）vs 学习法 → 过渡到学习法
- 综述锚点：`[洛哥填：用 Kumar & Ravi 2016 一句话引出领域]`
- 金融文本难点（一句带过，详细在 1.1）

**2.2 Ng–Jordan theory of learning curves**
- 生成式 vs 判别式的双阶段理论（快收敛 vs 低渐近误差）
- 数学推导放 Appendix A，正文只讲直觉与结论
- 实证预期：小样本生成式占优、大样本判别式占优

**2.3 The two classifiers**
- NB：生成式，条件独立假设 + Laplace 平滑即先验（连接 RQ3）
- SVM：判别式，max-margin / hinge loss / 线性核
- `[洛哥填：指出两模型可看作同一特征的两种学习哲学]`

**2.4 Classic models in the LLM era**（§5 目录中的定位点）
- 为何在 LLM 时代仍研究 NB/SVM：小数据、可解释、可复现、成本
- `[洛哥填：给 1–2 句你自己的定位论述]`

**2.5 Label noise and class imbalance**
- 标签噪声（Frénay & Verleysen 2014 综述锚点）
- 类别不平衡（He & Garcia 2009 综述锚点）
- PhraseBank 的一致度分层正好提供这两者的天然实验场 → 过渡到 §3

## 3. Methodology（3.0 页，~1,300 词）

**3.1 Data: Financial PhraseBank**
- 数据集事实：~4,846 句 / 3 类 / 16 位金融专家 / Malo 2014
- 四个一致度子集（嵌套）与类别分布（引 Table 1）
- License 与伦理：CC BY-NC-SA 3.0 非商业研究；`[洛哥填：说明与导师确认的伦理结论]`

**3.2 Preprocessing and features**
- TF-IDF, 1–2gram, min_df=2, sublinear, English stopwords
- 两模型共用同一向量器（可比性声明）

**3.3 Models and hyperparameters**
- NB: MultinomialNB, α=1（Laplace）
- SVM: LinearSVC, C=1
- 完整配置表 → Appendix B

**3.4 RQ1 design: learning curves**
- 80/20 分层切分，固定 held-out test
- 训练规模 [32…3877]（log 梯度），跨 5 seeds
- 特征模式：per-subset（主）vs fixed-pool（稳健性）
- 指标：accuracy（Ng–Jordan 0-1 错误率框架）+ macro-F1（不平衡公平）

**3.5 RQ2 design: agreement as a label-noise proxy**
- ⚠️ **必须写明的操作化假设**：一致度阈值子集 ≠ 随机噪声注入；一致度与句子难度相关
- 三层设计：(a) 子集内部 CV；(b) 固定干净测试集；(c) 固定 n=600 非重叠区间
- `[洛哥填：用你自己的话说明这个假设及其局限——口试必问]`

**3.6 RQ3 design: recovering the rare negative class**
- 四种配置（NB 经验/均匀先验；SVM 无/balanced 权重）
- 指标：negative-class F1 + recall（恢复目标）、macro-F1、accuracy

**3.7 Evaluation**
- 分层 10 折 CV、5 seeds、mean ± std
- （可选，终稿补）配对 bootstrap / McNemar 显著性

## 4. Experiments & Results（4.0 页，~1,700 词，以图表为主）

**4.1 Baseline and overall comparison**（引 Table 2）
- NB vs SVM 全量 10 折 CV 数字

**4.2 RQ1: learning curves**（引 Fig. 1 accuracy / Fig. 2 macro-F1）
- accuracy：小样本 NB 占优 → 交叉 ~256–512 → SVM 反超
- macro-F1：SVM 全规模占优
- fixed-pool 稳健性（可进 Appendix C）

**4.3 RQ2: robustness to label uncertainty**（引 Fig. 3–5 + Table 3）
- (a) 子集内部 CV 下降曲线
- (b) 固定干净测试集近持平
- (c) 固定 n 下陡降 + NB 负类崩溃

**4.4 RQ3: recovering the negative class**（引 Fig. 6 + Table 4）
- NB 默认灾难 → 均匀先验免费午餐
- SVM balanced 精调 → 仍最优

**4.5 Summary of findings**（引 Table 5 汇总对照）
- 三 RQ 一览表

## 5. Discussion（2.5 页，~1,100 词）

**5.1 Ng–Jordan on financial text: where it holds and where it does not**
- accuracy 成立 / macro-F1 不成立的解释
- `[洛哥填：你自己的解释——NB 优势来自多数类建模？]`

**5.2 The minority class as the persistent weakness of the generative model**
- 三 RQ 汇聚的证据链

**5.3 Practical implications**
- 对金融情感应用的启示（负类即风险信号；数据质量>数据量；何时选 NB）
- **拿 Distinction 的关键段**：给可操作建议

**5.4 Limitations**
- 一致度≠纯噪声（同 3.5）
- 单一数据集 / 线性模型 / 无超参数搜索 / 无显著性检验（若终稿未补）
- 小样本区间的稳定性

**5.5 Future work**
- 更多数据 / 深度学习对照 / 其他语种 / 更细一致度

## 6. Conclusion（1.0 页，~450 词）

- 三 RQ 结论各一句（带数字）
- 可行动结论 2–3 条
- 一句话收束

## References（25–35 篇，不计页）

见 `05_references.md`（已核实的 + 待核实清单）。

## Appendix A：Ng–Jordan 推导（不计页）

- 生成式/判别式误差分解：渐近项 + 估计项
- O(log n) vs O(n) 估计误差的直觉推导
- `[洛哥填：深度和严谨度由你把握，这是技术分亮点]`

## Appendix B：超参数与实验配置（不计页）

- 向量器参数 / 模型参数 / 切分与种子 / 运行环境版本

## Appendix C：完整分类报告与额外图表（不计页）

- 全部分类报告（per-class P/R/F1）
- fixed-pool RQ1 曲线
- 混淆矩阵 / 误判例（若做）

---

## 写作顺序建议（初稿 8/18–21）

1. **先写 §4（Results）**——有数据支撑，最容易下笔，用 `02_bullet_materials.md` + `03_figure_captions.md`
2. **再写 §3（Methodology）**——实验设计已在 `results/SUMMARY.md` 和代码里定死
3. **然后 §2（Background）**——需要文献，`05_references.md` 里有锚点
4. **最后 §1 / §5 / §6 / Executive Summary**——需要全貌，最后写最顺

> 每一节动笔前，先看 `01_section_briefs.md` 的该节简报（论证骨架 + 必引数据），再对照 `02_bullet_materials.md` 取数据碎片，用 `04_paragraph_templates.md` 的段落结构组织。
