# 图表题注草稿（Figure / Table Captions）

> 题注是**factual 描述**，只说"图里有什么、怎么测的"，**不下"说明什么/意味着什么"的判断**（那留给你）。
> 已按 LaTeX 习惯给出编号占位。可微调措辞，但不要加解读性语句。
> 图文件在 `figures/`；数字来源 `results/*.jsonl`。

---

## 图（Figures）

**Figure 1 — Learning curves by accuracy (RQ1).**
Test accuracy of the generative (Naive Bayes, blue) and discriminative (SVM, orange) classifiers as a function of the number of training sentences (log scale), evaluated on a fixed 20% held-out test set from the 50% agreement corpus. Mean over 5 stratified train/test splits; shaded bands show ±1 standard deviation. Features were fit on each training subset independently (per-subset mode). The dashed line marks the crossover size at which SVM accuracy first reaches or exceeds that of Naive Bayes (between 256 and 512 training sentences).

**Figure 2 — Learning curves by macro-F1 (RQ1).**
As in Figure 1, but reporting macro-averaged F1 instead of accuracy. SVM macro-F1 is higher than Naive Bayes at every training size in the range 32–3877.

**Figure 3 — Within-subset performance across agreement tiers (RQ2a).**
macro-F1 from stratified 10-fold cross-validation, computed separately within each annotator-agreement subset (100%, >75%, >66%, >50%). Error bars are standard deviations across 5 seeds. Note the subsets are nested: lower agreement thresholds contain more sentences and labels of lower consensus.

**Figure 4 — Generalisation to clean labels vs. training agreement tier (RQ2b).**
macro-F1 on a fixed clean test set (20% hold-out of the 100% agreement subset) for models trained on each of the four agreement subsets (test sentences excluded from training). Error bars are standard deviations across 5 seeds.

**Figure 5 — Fixed-size training across agreement bins (RQ2c).**
macro-F1 on the same fixed clean test set for models trained on 600 sentences drawn from each of the four non-overlapping agreement bins (100%, 75–100%, 66–75%, 50–66%), stratified by class. Error bars are standard deviations across 5 seeds. Panel title in the source figure labels the non-overlapping bins.

**Figure 6 — Class-imbalance recovery mechanisms (RQ3).**
macro-F1 (solid bars) and negative-class F1 (hatched bars) from stratified 10-fold cross-validation on the full 50% agreement corpus, for four configurations: Naive Bayes with empirical and uniform priors; SVM unweighted and with class_weight='balanced'. Error bars are standard deviations across 5 seeds.

---

## 表（Tables）

**Table 1 — Financial PhraseBank agreement subsets and class distribution.**
Number of sentences and per-class counts (positive/neutral/negative) for the four annotator-agreement subsets. Subsets are nested: each lower threshold contains all sentences of the higher one. From the 50% corpus the negative class accounts for 12.5% of sentences.

| subset | threshold | n | pos | neu | neg |
|---|---|---|---|---|---|
| AllAgree | 100% | 2,264 | 570 | 1,391 | 303 |
| 75Agree | >75% | 3,453 | 887 | 2,146 | 420 |
| 66Agree | >66% | 4,217 | 1,168 | 2,535 | 514 |
| 50Agree | >50% | 4,846 | 1,363 | 2,879 | 604 |

**Table 2 — Baseline comparison on the full 50% agreement corpus.**
Stratified 10-fold cross-validation (mean over 5 seeds) of Multinomial Naive Bayes and Linear SVM under an identical TF-IDF (1–2 grams, min_df=2) feature representation.

| model | accuracy | macro-F1 |
|---|---|---|
| NB | 0.698 | 0.516 |
| SVM | 0.757 | 0.691 |

**Table 3 — RQ2 results across the three experimental layers.**
(a) within-subset 10-fold CV macro-F1; (b) macro-F1 on the fixed clean (100%-agreement) test set after training on each agreement subset; (c) macro-F1 on the same clean test after training on 600 sentences from each non-overlapping agreement bin. Mean over 5 seeds.

| layer | NB (all→50) | SVM (all→50) |
|---|---|---|
| (a) within-subset | 0.623 → 0.515 | 0.802 → 0.691 |
| (b) clean test | 0.607 → 0.626 | 0.766 → 0.777 |
| (c) fixed n=600 | 0.548 → 0.312 | 0.707 → 0.438 |

**Table 4 — RQ3: class-imbalance recovery mechanisms.**
Accuracy, macro-F1, and negative-class F1 / recall / precision for the four configurations, stratified 10-fold CV, mean over 5 seeds.

| configuration | accuracy | macro-F1 | neg F1 | neg recall | neg precision |
|---|---|---|---|---|---|
| NB, empirical prior | 0.698 | 0.515 | 0.256 | 0.151 | 0.891 |
| NB, uniform prior | 0.714 | 0.632 | 0.513 | 0.456 | 0.591 |
| SVM, unweighted | 0.757 | 0.691 | 0.598 | 0.516 | 0.717 |
| SVM, balanced | 0.752 | 0.695 | 0.612 | 0.582 | 0.650 |

**Table 5 — Summary of research questions and main findings.**
(洛哥填写"findings"列措辞；数字列已给。）

| RQ | question | key finding |
|---|---|---|
| RQ1 | sample size | crossover at n≈256–512 (accuracy); SVM leads at all sizes (macro-F1) |
| RQ2 | label agreement | performance falls as agreement falls, even as n grows; NB negative class collapses (neg-F1→0) under low-certainty labels |
| RQ3 | imbalance | NB uniform prior: neg-F1 0.256→0.513 (free lunch); SVM balanced best at 0.612 |
