# 全文样稿（学习参考用，非论文正文）

> **这是干什么的**：按 `00_thesis_skeleton.md` + `04_paragraph_templates.md` 的模板，把全文各节各写一遍，示范"每一段在模板里扮演什么角色、句子怎么组织、数字怎么报"。
> **红线提醒**：这是**骨架辅助**。所有 `【示例解释】` 标记处是演示性措辞，**必须由你用自己的话重写**；其余句子也请当作结构示范而非成文。正文措辞永远出自你手。
> **数字来源**：取自 `02_bullet_materials.md`（源自 `results/SUMMARY.md` / `*.jsonl`）。使用前请与 jsonl 逐一核对。
> **词数**：每节标注建议预算与样稿实词数，帮你校准手感。

---

# Executive Summary（预算 ~350 词 · 样稿 ~330）

> 模板 8：问题一句 → 方法一句 → 三 RQ 发现（各 1–2 句带数字）→ 结论一句 + 意义一句。给没空读全文的人，30 秒懂你。

Financial sentiment analysis — assigning positive, neutral, or negative polarity to financial news — matters for trading decisions and risk management, but it is hard: financial language inverts everyday meaning ("costs fell" can be good news), and expert annotation is slow and expensive, so labelled data is permanently scarce. When data are scarce, which classifier should a practitioner choose?

This thesis answers this question empirically, comparing a generative classifier (multinomial Naive Bayes, NB) with a discriminative one (linear Support Vector Machine, SVM) on the Financial PhraseBank (4,846 sentences, three classes, annotated by 16 finance experts), across three research questions: learning curves, label uncertainty, and the rare negative class.

Under accuracy, NB leads at small training sizes (0.600 vs 0.576 at n=32), with a crossover between n≈256 and 512 after which SVM dominates — consistent with the Ng–Jordan prediction. Under macro-F1, however, SVM leads at every scale (0.681 vs 0.501 at full data). As label agreement drops, both models degrade, but NB's negative class collapses (negative-class F1 from 0.169 to 0.000 at the 66–75% interval, with zero recall), while SVM retains a floor (0.332). A uniform prior lifts NB's negative recall from 0.151 to 0.456 and macro-F1 from 0.515 to 0.632; SVM with balanced weights remains best overall (negative-class F1 0.612).

The generative–discriminative choice on financial text is therefore data- and metric-dependent. For risk-sensitive applications where the negative class matters, a discriminative model with class weighting is the safer default; in small-data settings, NB with a uniform prior is a cost-free rescue.

---

# 1. Introduction（预算 ~650 词 · 样稿 ~560）

> 四步逻辑：1.1 制造需求（价值→难点→稀缺→问题浮现）→ 1.2 提出理论（Ng–Jordan 交叉点 + 为什么不用 LLM）→ 1.3 三个 RQ + 贡献 + 路线图。不给任何实验数字。

## 1.1 Motivation: financial sentiment and its difficulty

*段落角色：opening / challenge。模板 1：主张 → 背景 → 反差 → 收束。*

Automated analysis of financial text is valuable because such text shapes markets: earnings announcements, analyst reports, and news items move prices and inform risk assessment at a scale no analyst can read manually. Financial sentiment analysis is the task of extracting the polarity of such texts — whether a statement is positive, neutral, or negative news for a company.

Yet the task is deceptively difficult for general-purpose methods. Financial language inverts everyday meaning: "costs fell" is a positive signal for a company, whereas "profits fell" is negative, and a general sentiment lexicon systematically misreads such sentences. Domain expertise is therefore required for reliable annotation, which makes it slow and expensive; each PhraseBank sentence in our dataset was labelled by up to eight financial experts. The consequence is structural: labelled financial text is scarce and will remain scarce.

This scarcity raises a concrete practical question: *given little data, which model family should we trust?* Classical statistical learning has a theoretical answer, and this thesis tests it in the financial domain.

## 1.2 Generative versus discriminative: the theoretical question

*段落角色：method-advantage（理论定位）。模板 2 的压缩版：主张 → 两阶段 → 交叉点 → 本文检验。*

Ng and Jordan (2002) showed that generative classifiers reach their asymptotic error faster than discriminative ones: a generative model's estimation error shrinks roughly as O(log n), while a discriminative model's shrinks as O(n). Their analysis predicts a two-phase picture — the generative model wins on small samples, the discriminative model wins in the large-data limit, and a crossover exists in between. Naive Bayes (NB) and the linear Support Vector Machine (SVM) are the canonical representatives of the two families, and both are cheap, interpretable, and competitive on small text corpora. We deliberately restrict attention to these classic linear models rather than large language models: the regime under study — scarce data — is precisely where LLMs are least practical and least interpretable, and where a theoretically grounded choice matters most (§2.4 returns to this).

## 1.3 Research questions and contributions

*段落角色：challenge→commitment。RQ 每行 1–2 句，贡献 2–3 点，最后一段是路线图。*

This thesis tests the Ng–Jordan prediction on a real financial corpus — the Financial PhraseBank — through three research questions:

- **RQ1 (learning curves).** Does the predicted small-sample advantage of the generative model, and the crossover into discriminative dominance, appear in financial sentiment classification — under accuracy, and under macro-F1?
- **RQ2 (label uncertainty).** Does either model's advantage survive when label quality degrades, using annotator agreement as a proxy for label noise?
- **RQ3 (class imbalance).** Can the rare negative class be recovered, and which model configuration recovers it best?

The contributions are threefold. First, we provide the first systematic test of the Ng–Jordan prediction on a financial sentiment corpus, showing that it holds under accuracy but not under macro-F1. Second, we localize the generative model's weakness: it degrades sharply on the rare negative class under label uncertainty, while the discriminative model degrades gracefully. Third, we compare four configurations for negative-class recovery and derive actionable guidance for practitioners.

The rest of the thesis is organized as follows. Section 2 reviews financial sentiment analysis, the Ng–Jordan theory, the two classifiers, and the place of classic models in the LLM era. Section 3 describes the data, features, and the design of the three experiments. Section 4 reports the results, Section 5 discusses their meaning and implications, and Section 6 concludes.

> 【学习点】1.3 的"路线图"必须与 §5 目录一一对应（"§5 讨论意义与启示"）——这是全文地图，后面每节都要兑现。

---

# 2. Background & Related Work（预算 ~1,100 词 · 样稿 ~980）

> 五步逻辑：2.1 承上（领域脉络）→ 2.2 理论支柱 → 2.3 两个模型 → 2.4 LLM 时代辩护 → 2.5 噪声与不平衡 → 落到 PhraseBank。心法：每小节结尾都落到"所以我要做点什么"。

## 2.1 Financial sentiment analysis

*段落角色：related-work（承上）。*

Financial sentiment analysis has developed in two waves. The first wave was dictionary-based: fixed word lists, such as the Loughran–McDonald dictionary built for 10-K filings (Loughran & McDonald, 2011) or Tetlock's media-content measures (Tetlock, 2007), assign polarity by vocabulary lookup. Such methods are transparent and need no labelled data, but they are brittle in the financial domain, where the same word can flip polarity by context — the dictionary cannot know that "costs fell" is good news. The second wave is learning-based: models are trained on manually labelled financial text, which adapts to domain semantics at the price of requiring exactly the scarce annotation discussed in §1.1 (Kumar & Ravi, 2016, survey this line). Our study belongs to the second wave and examines its scarce-data constraint.

## 2.2 Ng–Jordan theory of learning curves

*段落角色：theory（全文支柱）。模板 2：主张 → 证据1 → 证据2 → 推导位置 → 结论 → 过渡。*

The theoretical question of this thesis is whether generative or discriminative classifiers should be preferred when data are limited. Ng and Jordan (2002) answer this with a two-stage argument. First, asymptotically — with unlimited data — a discriminative classifier's error is never higher than a generative classifier's, because it directly models the decision boundary rather than the full data-generating distribution. Second, in finite samples the generative classifier's parameter estimates converge faster: roughly O(log n) for the generative model versus O(n) for the discriminative one. The two effects trade off: with little data, the generative model's faster convergence wins despite its worse asymptotic error; with much data, the discriminative model's better asymptotic error dominates. The crossover between the two phases depends on the problem. A formal sketch of this error decomposition (asymptotic term plus estimation term) is given in Appendix A; the body of this thesis uses only the intuitive two-phase picture.

This theory is our test bed: RQ1 asks whether the predicted crossover appears on financial text, and at what sample size.

## 2.3 The two classifiers

*段落角色：method（定义）。注意 2.3 埋钩子：NB 的平滑参数 = 先验，为 RQ3 埋伏笔。*

Naive Bayes is the representative generative classifier: it models the joint distribution of features and labels under a conditional-independence assumption, then classifies by Bayes' rule. Despite the assumption being false in practice, NB is near-optimal under zero-one loss in many settings (Domingos & Pazzani, 1997; Zhang, 2004). For text, we use the multinomial variant with Laplace smoothing; the smoothing parameter acts as a prior over class proportions — a detail that becomes central in RQ3 (§3.6). The SVM is the representative discriminative classifier: it learns a maximum-margin decision boundary directly, without modelling the data distribution (Cortes & Vapnik, 1995), and it has long been one of the strongest linear learners for text (Joachims, 1998). We use the linear-kernel form, so that the two models consume identical features and differ only in learning philosophy — generative versus discriminative.

## 2.4 Classic models in the LLM era

*段落角色：positioning（回应"都 2026 年了还研究 NB/SVM？"——口试必问，必须正面答）。*

Why study NB and SVM when large language models dominate the field? Three reasons. First, data: LLMs need large in-domain corpora to fine-tune, and the entire PhraseBank is smaller than a single paragraph of a modern pretraining corpus — in the regime this thesis studies, LLM fine-tuning is often not even applicable. Second, cost and reproducibility: NB and SVM train in seconds on a laptop, with deterministic, fully documented configurations (Appendix B), whereas LLM results depend on sampling, decoding, and prompt choices. Third, interpretability: the linear decision boundary and class-conditional probabilities are directly inspectable, which matters in regulated financial settings. This is not to claim classic models beat LLMs; it is to claim the question "which classic model, and under what data conditions" is still the one that is practically answerable for scarce, high-stakes financial text (cf. Wang & Manning, 2012, on strong simple linear baselines).

## 2.5 Label noise and class imbalance

*段落角色：related-work→gap（汇聚到 PhraseBank）。*

Two further properties of real financial data complicate the picture. The first is label noise: human annotation is imperfect, and disagreement between annotators is a well-documented source of label uncertainty (Frénay & Verleysen, 2014). The second is class imbalance: in financial text, negative statements — often the most decision-relevant — are typically the rarest class (He & Garcia, 2009). Both problems have rich literatures, but they are usually studied on synthetic datasets. The Financial PhraseBank offers a natural joint experimental field: because every sentence was annotated 5–8 times by finance experts, the dataset ships with an agreement score, and its four nested agreement subsets (2,264 / 3,453 / 4,217 / 4,846 sentences at 100% / 75% / 66% / 50% agreement thresholds) provide graded label uncertainty, while its negative class forms only 12.5% of the data. This combination lets us study label noise and class imbalance in a real financial corpus with no artificial corruption — the setting of §3.

---

# 3. Methodology（预算 ~1,300 词 · 样稿 ~1,100）

> 逻辑：数据（3.1，引 Table 1）→ 特征（3.2，两模型共用 = 公平性声明）→ 模型参数（3.3）→ 按 RQ 逐个写实验设计（3.4/3.5/3.6）→ 统一评估（3.7）。§3 是"承诺"，§4 按同样顺序"兑现"（4.2↔3.4，一一对应）。

## 3.1 Data: the Financial PhraseBank

*段落角色：data（可复现的第一块砖）。*

We use the Financial PhraseBank (Malo et al., 2014), a corpus of 4,846 English sentences sampled from financial news, each annotated for polarity — positive, neutral, or negative — from the perspective of a stock investor ("does this news affect the company's share price?"). Annotation was performed by 16 finance professionals (3 researchers and 13 MSc finance students), with every sentence annotated 5–8 times. Crucially for this thesis, the corpus publishes an agreement score per sentence; the four nested agreement subsets — 2,264 sentences on which all annotators agree, and 3,453 / 4,217 / 4,846 at the 75% / 66% / 50% thresholds — form the experimental field for RQ2. Class distribution is strongly imbalanced: neutral 59.4%, positive 28.1%, negative 12.5% (Table 1). The dataset is released under CC BY-NC-SA 3.0 and used for non-commercial research only; 【示例解释：伦理结论一句——经与导师确认后使用】.

## 3.2 Preprocessing and features

*段落角色：method（公平性声明）。*

Both models consume an identical feature pipeline: TF-IDF vectors over word 1- and 2-grams, with min_df=2, sublinear term frequency, and English stopwords removed. Sharing one vectorizer is a deliberate fairness decision: any performance difference between NB and SVM can then be attributed to the learning algorithm, not to feature engineering (full configuration in Appendix B).

## 3.3 Models and hyperparameters

*段落角色：method（配置固定，可复现）。*

We train a multinomial Naive Bayes with Laplace smoothing α=1 (the default prior), and a linear Support Vector Machine (LinearSVC) with C=1, both from scikit-learn. We deliberately fix hyperparameters at their defaults rather than tuning them per model, so that the comparison reflects the two learning philosophies as used out of the box — the situation of a practitioner with scarce data, who cannot afford a tuning loop either.

## 3.4 RQ1 design: learning curves

*段落角色：experiment-design（承诺 1）。*

RQ1 asks whether the Ng–Jordan crossover appears in financial sentiment classification. We construct learning curves by stratified 80/20 splitting, holding out a fixed test set, and training on increasing subsets of the remaining data at sizes [32, 64, 128, 256, 512, 1024, 2048, 3877], across 5 random seeds. As the primary mode, each training subset is drawn within a single agreement stratum (per-subset), matching how a practitioner would collect data of a given quality; as a robustness check, we also train on fixed-pool random samples across all agreement levels. We report accuracy, which mirrors the 0–1 error of the Ng–Jordan framework, and macro-F1, which treats the rare negative class as equally important.

## 3.5 RQ2 design: agreement as a label-noise proxy

*段落角色：experiment-design（承诺 2）+ 诚实声明。⚠️ 这一段是口试生死线——假设必须写明，不写就是硬伤。*

RQ2 asks how the two models behave as label quality degrades, using the agreement strata as a proxy for label noise. Three layers of evidence isolate the effect. (a) Within-subset cross-validation: train and test inside each agreement subset, measuring the joint effect of data quantity and label uncertainty. (b) A fixed clean test set: train on each agreement subset but always evaluate on a held-out 20% of the all-agreement sentences, which removes test-set difficulty from the comparison. (c) Fixed-size disjoint intervals: with n fixed at 600, non-overlapping agreement bands (all / 75–100% / 66–75% / 50–66%) isolate label certainty from data quantity entirely.

【示例解释——这段必须由你用自己的话重写，口试 100% 被问】 We treat agreement as an operationalization of label noise, and this is an assumption, not a fact: low agreement need not equal random label corruption — it may reflect that the sentence itself is genuinely harder, and our agreement bands are nested, so lower thresholds also admit more data. Design (c) removes the data-quantity confound, and design (b) separates "labels are wrong" from "test sentences are harder", but the proxy limitation remains: results in this section are evidence about low-consensus text, which we interpret as label uncertainty under this stated assumption.

## 3.6 RQ3 design: recovering the rare negative class

*段落角色：experiment-design（承诺 3）。*

RQ3 asks whether the 12.5% negative class can be recovered. We compare four configurations: NB with its empirical class prior (the default) versus a uniform prior — the smoothing hook from §2.3 — and SVM without versus with balanced class weights. The uniform prior and balanced weights are the textbook remedies for imbalance (He & Garcia, 2009), and the question is which model family converts them into a better recovered minority class. We report negative-class F1 and recall (the recovery targets), plus macro-F1 and accuracy.

## 3.7 Evaluation

*段落角色：evaluation（统一标准）。*

All main results use stratified 10-fold cross-validation with 5 random seeds, reported as mean ± standard deviation; the RQ1 learning curves use the fixed held-out protocol described in §3.4. 【示例解释：显著性检验是终稿选项——若终稿补充配对 bootstrap / McNemar 检验，在这里留出位置。】 Every number below is reproducible from the pinned configuration in Appendix B.

---

# 4. Experiments & Results（预算 ~1,700 词 · 样稿 ~1,300，图表为主）

> 心法：Results 只允许"数据显示 X"，不允许"这说明 Y"——解释是 §5 的活。每段格式固定：复述设计一句 → 报数字（引图/表）→ 一句"值得注意的现象"（不解释）。

## 4.1 Baseline and overall comparison

*段落角色：evidence（全貌）。*

Table 2 reports the full-scale comparison on the whole corpus (10-fold CV, 5 seeds). SVM outperforms NB on both metrics: accuracy 0.757 vs 0.698 (+0.059), and macro-F1 0.691 vs 0.516 (+0.175). The macro-F1 gap is nearly three times the accuracy gap. This baseline frames the two questions below: whether the gap ever closes at small scale (RQ1), and whether it is driven by the negative class (RQ2, RQ3).

## 4.2 RQ1: learning curves

*段落角色：evidence（逐 RQ 报数）。*

**Accuracy (Fig. 1).** The learning curves show the predicted two-phase pattern. NB is ahead at every size up to n=256 (0.600 vs 0.576 at n=32; 0.641 vs 0.636 at n=256); the largest generative lead is 0.046 at n=64. At n=512, SVM overtakes (0.659 vs 0.657), and the lead widens with data. The crossover therefore lies between n≈256 and 512, and it occurred in all 5 seeds.

**Macro-F1 (Fig. 2).** Under macro-F1 the picture is different: SVM leads at every scale, from 0.389 vs 0.317 at n=32 to 0.681 vs 0.501 at full data, with no crossover.

**Robustness.** In the fixed-pool mode, the small-sample NB lead in accuracy also disappears: SVM matches or leads from n=32 onward (0.596 vs 0.594). One phenomenon is worth noting: the NB small-sample advantage is present in per-subset mode but absent in fixed-pool mode; its explanation is deferred to §5.

## 4.3 RQ2: robustness to label uncertainty

*段落角色：evidence（逐 RQ 报数）。*

**(a) Within-subset CV (Fig. 3).** As the agreement threshold relaxes from 100% to 50% — and the data *grow* from 2,264 to 4,846 sentences — macro-F1 *falls* for both models: NB from 0.623 to 0.515, SVM from 0.802 to 0.691. The performance drop despite more data indicates that the label-uncertainty effect dominates the data-quantity effect.

**(b) Fixed clean test set (Fig. 4).** Trained on degraded subsets but tested on clean all-agreement sentences, both models are nearly flat: SVM 0.766 → 0.777, NB 0.607 → 0.626. The low-agreement labels are thus mostly correct in absolute terms; the within-subset decline of (a) partly reflects harder test sentences rather than wrong labels.

**(c) Fixed n=600 intervals (Fig. 5, Table 3).** With sample size held constant, agreement is decisive: macro-F1 drops monotonically from the all band to the 66–75% band — NB 0.548 → 0.357 → 0.306 → 0.312; SVM 0.707 → 0.575 → 0.390 → 0.438. The most striking number is in the negative class: NB's negative-class F1 falls to 0.000 in the 66–75% band, with recall exactly zero — it labels no negative sentence correctly — while SVM's negative-class F1, though also declining (0.561 → 0.332), never approaches collapse.

## 4.4 RQ3: recovering the negative class

*段落角色：evidence（逐 RQ 报数）。*

Table 4 and Fig. 6 report the four configurations. With the default empirical prior, NB catches only 15.1% of negative sentences (negative recall 0.151, F1 0.256, precision 0.891 — high precision, low recall) and reaches macro-F1 0.515, accuracy 0.698. The uniform prior changes the picture: negative recall triples to 0.456, negative F1 rises to 0.513, macro-F1 to 0.632 (+0.117), and — unusually — accuracy also rises, to 0.714 (+0.016). SVM without weights already reaches negative F1 0.598 and recall 0.516; balanced weights add a further 0.066 recall (F1 0.612) at a cost of 0.005 accuracy. The best recovered configuration is SVM with balanced weights (negative F1 0.612), which still beats NB with a uniform prior (0.513) by a wide margin.

## 4.5 Summary of findings

*段落角色：evidence（汇总收束）。*

Table 5 consolidates the three RQs. Under accuracy, the Ng–Jordan crossover appears between n≈256 and 512. Under macro-F1, SVM leads at all scales. Under label uncertainty, NB's negative class collapses (F1 0.000) while SVM degrades gracefully. Under imbalance, prior adjustment rescues NB but balanced-weight SVM remains the strongest configuration. The three results lines converge on a single pattern: 【示例解释：一句话现象概括由你下——比如"判别式的稳健性集中在它对稀少负类的处理上"。这里只陈述现象，机理放 §5。】

> 【学习点】§4 与 §3 一一对应：4.2↔3.4、4.3↔3.5、4.4↔3.6。写完自查表头顺序是否一致。

---

# 5. Discussion（预算 ~1,100 词 · 样稿 ~950）

> 五步逻辑：5.1 回扣理论（部分成立 + 解释"分裂"）→ 5.2 归纳证据链 → 5.3 实际建议（Distinction 关键段）→ 5.4 诚实局限 → 5.5 未来。全文最有分量的部分——"为什么"全在这里。

## 5.1 The Ng–Jordan prediction holds under accuracy, but not under macro-F1

*段落角色：interpretation（回扣理论，你的原创思考主场）。*

The results give a split verdict on the Ng–Jordan theory. Under accuracy, the prediction is confirmed: NB leads on small samples, the crossover appears between n≈256 and 512, and SVM dominates thereafter (Fig. 1) — and the crossover is stable across all five seeds. Under macro-F1, the prediction fails: SVM leads at every scale, with no crossover (Fig. 2).

【示例解释——这段是你的原创思考，必须用自己的话重写】 A plausible reading is that the two metrics ask different questions. Ng and Jordan's analysis is framed in 0–1 error, which weights every instance equally; under accuracy, our results match their prediction. Macro-F1 weights classes equally instead of instances, so the generative model's weakness is concentrated where the instance weights are lightest: the rare negative class, whose F1 contribution is drowned out under accuracy but is fully exposed under macro-F1. The "split" may therefore not be a refutation of the theory but a boundary condition on it: the generative small-sample advantage survives when errors are counted per instance, and vanishes when rare classes are counted per class. This reading is consistent with RQ3, where NB's default configuration systematically underpredicts the negative class.

## 5.2 The minority class as the persistent weakness of the generative model

*段落角色：synthesis（三 RQ 证据链汇聚）。模板 6。*

Three independent experiments converge on one pattern. RQ1: under macro-F1, NB trails at every scale (0.501 vs 0.681 at full data), a gap that accuracy hides. RQ2: when label certainty drops, NB's negative class collapses to F1 0.000 with zero recall, while SVM holds a floor. RQ3: even with a uniform prior tripling NB's negative recall (0.151 → 0.456), NB (negative F1 0.513) never catches the default SVM (0.598), let alone the balanced one (0.612). 【示例解释：为什么生成式在负类上系统性弱——你的理论。一条可用的线索：NB 把每个类别的分布分开估计，稀有类别只有 12.5% 的数据可估，估计误差在类别层面最尖锐；判别式不建模类别分布，直接把边界推向稀有类，代价不对称天然由 hinge loss 的间隔控制。】 The practical meaning is direct: in financial text, the negative class is typically the risk signal, and the generative model's blind spot sits exactly there.

## 5.3 Practical implications

*段落角色：implication（拿 Distinction 的关键段——给可操作建议）。*

Two recommendations follow. First, for risk-sensitive financial applications — credit news screening, short-side monitoring, early warning — the negative class is the signal, and SVM with balanced weights is the safer default: it recovered negative F1 0.612 at a 0.005 accuracy cost (§4.4), and it degrades gracefully rather than collapsing under label uncertainty (§4.3). Second, in genuinely small-data settings (n below a few hundred), a generative model is not a mistake: NB with a uniform prior delivered a free lunch — negative recall 0.456 (×3) *and* accuracy +0.016 (§4.4) — and its class-conditional probabilities are directly interpretable. A third, broader lesson is about data quality rather than quantity: with n fixed at 600, agreement determined macro-F1 more than anything else (SVM 0.707 → 0.438 from the all band to 50–66%), so a practitioner should spend annotation effort on consensus-building before adding more sentences.

## 5.4 Limitations

*段落角色：limitation（主动认错反而加分）。*

Four limitations bound this study. First, the agreement-based operationalization is a proxy for label noise, not random corruption; low-agreement text may be genuinely harder, and our interpretation rests on the assumption stated in §3.5. Second, all evidence comes from a single corpus, PhraseBank, and a single language. Third, we compare only two linear models with fixed default hyperparameters; no tuning was performed, and no significance tests accompany the differences reported in §4 — although the cross-over is stable across all five seeds, the small-sample intervals (n ≤ 256) are noisy. Fourth, per-subset training couples data quality with data quantity; we decoupled them in design (c), but the 66–75% band's NB collapse deserves replication on other agreement-stratified corpora before being generalized.

## 5.5 Future work

*段落角色：future（一句带过）。*

Natural extensions include replicating the design on additional financial corpora and languages, adding deep-learning and LLM baselines in the large-data regime where they become viable, and refining the agreement proxy with per-item difficulty models — which would also test whether the generative model's minority-class weakness is specific to sentiment text or general.

---

# 6. Conclusion（预算 ~450 词 · 样稿 ~420）

> 三 RQ 结论各一句（带数字）→ 可行动建议 2 条 → 一句收束。与 §1 的三 RQ 逐条呼应，形成闭环。

This thesis asked whether the choice between a generative and a discriminative classifier matters on financial text, and the answer is yes — in ways that are specific, measurable, and actionable.

**RQ1 (learning curves).** Under accuracy, the Ng–Jordan prediction holds on the Financial PhraseBank: NB leads at small training sizes, the crossover occurs between n≈256 and 512, and SVM dominates beyond it. Under macro-F1, the prediction does not hold: SVM leads at every scale, 0.681 vs 0.501 at full data.

**RQ2 (label uncertainty).** Using annotator agreement as a proxy for label noise, both models degrade as agreement drops, but asymmetrically: NB's negative class collapses to F1 0.000 at the 66–75% band with zero recall, while SVM retains a floor of 0.332. With sample size held constant, agreement was the dominant factor — SVM macro-F1 fell from 0.707 to 0.438 between the cleanest and noisiest bands.

**RQ3 (class imbalance).** The rare negative class can be recovered by configuration, not just by model choice: a uniform prior tripled NB's negative recall (0.151 → 0.456) and raised its macro-F1 by 0.117 — while also raising accuracy — yet SVM with balanced weights remained the strongest overall configuration (negative F1 0.612).

Two recommendations follow for practitioners. In risk-sensitive applications where negative news is the signal, use a discriminative model with class weighting. In small-data settings where interpretability and cost matter, NB with a uniform prior is a defensible and nearly free choice. And one broader lesson: in this domain, the quality of labels outranks the quantity of data.

On financial text, generative and discriminative classifiers are not interchangeable; the theory that separates them predicts where each wins, and the negative class decides the rest.

---

# 附录：自检与 claim-evidence 对照（样稿自查，供你参考这套检查方法）

## 迷你大纲（每节一句话）

- ES：问题 → 方法 → 三发现（带数字）→ 结论与建议
- §1：价值/难点/稀缺 → 理论（Ng–Jordan + 为什么线性模型）→ 三 RQ + 贡献 + 路线图
- §2：领域脉络（词典→学习）→ 理论支柱 → 两模型定义 → LLM 时代辩护 → 噪声/不平衡 → PhraseBank
- §3：数据 → 特征（公平声明）→ 模型 → 三 RQ 设计（含 RQ2 假设声明）→ 评估
- §4：全貌 → 逐 RQ 报数（引图表）→ 汇总表；只报"数据显示 X"
- §5：回扣理论 → 证据链 → 建议 → 局限 → 未来；才允许"这说明 Y"
- §6：三 RQ 各带数字 → 两条建议 → 收束；与 §1 闭环

## 五维自检清单（每写完一节跑一遍）

1. **段落主张**：每段第一句是否即本段主张？(检查 §2.1–2.5 各段首句)
2. **术语一致**：generative/discriminative、agreement/consensus、negative class 全文是否同一称呼？(统一用后者/前者)
3. **claim–evidence 对齐**：凡出现数字的句子，是否都引用了对应图/表或标注了出处？
4. **未支撑主张**：§5 的"为什么"部分是否全部是【示例解释】待洛哥重写？是——禁止无标注的解释进入正文。
5. **承诺兑现**：§1.3 路线图（§2 文献 → §3 设计 → §4 结果 → §5 讨论 → §6 结论）与 §3.4–3.6 ↔ §4.2–4.4 的对应是否完整？

## Claim–Evidence Map（主要主张 → 证据 → 状态）

| Claim | Evidence | Status |
|---|---|---|
| 金融文本情感有价值且难（§1.1） | PhraseBank 标注设计（5–8 重/句）+ Loughran–McDonald 词典局限 | supported（文献） |
| 小样本生成式占优、有交叉点（RQ1） | Fig. 1：n≤256 NB 领先、n=512 SVM 反超、5/5 seeds | supported（§4.2） |
| macro-F1 下判别式全规模占优 | Fig. 2：0.681 vs 0.501 全量；n=32 即 0.389 vs 0.317 | supported（§4.2） |
| 低一致下 NB 负类崩溃、SVM 保底 | Fig. 5/Table 3：NB neg-F1 → 0.000（recall 0）；SVM → 0.332 | supported（§4.3） |
| 均匀先验救回 NB 负类但追不上 SVM | Table 4：recall 0.151→0.456；0.513 vs 0.612 | supported（§4.4） |
| Ng–Jordan 在金融文本上部分成立（§5.1） | Fig. 1 交叉 vs Fig. 2 无交叉 | supported，**解释待洛哥** |
| "分裂"来自负类在 macro-F1 下的暴露 | RQ1–RQ3 三线汇聚 | **解释待洛哥**（示例解释已标记） |
| 数据质量 > 数据量（§5.3） | 固定 n=600 时 agreement 决定性能（SVM 0.707→0.438） | supported（§4.3c），**建议措辞待洛哥** |

> 用法：正式写每节时，先把这张表扩成该节的版本，写完逐格核对——这是 skill 里"adversarial review"的落地方案。

