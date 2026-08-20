# Appendix B：Experimental Configuration

> 本文件是**客观配置清单**（全部来自 `src/config.py`、`src/experiment_utils.py`、各 `scripts/run_*.py` 与运行环境，均已读取核对），英文部分可直接粘贴进论文；中文注释是给你的说明。
> 正文 §2.4 / §3.2 / §3.7 都提到 "Appendix B"，字母与内容对齐。
> 所有参数如实列出，**不评判、不解释**——解释性句子由你写。

---

## B.1 Software and hardware environment

All experiments were run with the following pinned versions:

| Component | Version |
|---|---|
| Python | 3.14.7 |
| scikit-learn | 1.9.0 |
| NumPy | 2.5.2 |
| SciPy | 1.18.0 |
| pandas | 3.0.5 |
| matplotlib | 3.11.1 |
| joblib | 1.5.3 |

`[洛哥填：硬件一行（如 CPU/内存/操作系统，若论文要求；大部分论文可不写）。版本号以你复现时的 `pip list` 为准——上面的 scikit-learn 1.9.0 等来自本机 venv，若你在别的环境重跑，改成实际版本。]`

## B.2 Dataset

**Financial PhraseBank v1.0** (Malo et al., 2014), four nested agreement subsets (each a separate file):

| Subset | Agreement threshold | Sentences | Positive | Neutral | Negative |
|---|---|---|---|---|---|
| AllAgree | 100% | 2,264 | 570 | 1,391 | 303 |
| 75Agree | >75% | 3,453 | 887 | 2,146 | 420 |
| 66Agree | >66% | 4,217 | 1,168 | 2,535 | 514 |
| 50Agree | >50% | 4,846 | 1,363 | 2,879 | 604 |

- Class order fixed throughout: `[positive, neutral, negative]`.
- File encoding: latin-1; each line a sentence, with the gold label separated by `@`.
- Licence: CC BY-NC-SA 3.0 (non-commercial; research use compliant).
- Each sentence was annotated 5–8 times by 16 finance experts (3 researchers and 13 MSc finance students); the agreement score per sentence is the operationalisation used in RQ2.

## B.3 Feature pipeline (shared by both models)

A single `TfidfVectorizer` (scikit-learn) is fitted once per experimental condition and shared by NB and SVM, so that any performance difference is attributable to the classifier, not to feature engineering:

| Parameter | Value |
|---|---|
| `ngram_range` | (1, 2) — unigrams and bigrams |
| `min_df` | 2 (terms must appear in ≥ 2 documents) |
| `stop_words` | `"english"` (scikit-learn's built-in list) |
| `sublinear_tf` | `True` (term frequency as 1 + log tf) |
| `lowercase` | `True` |
| remaining defaults | `norm='l2'`, `use_idf=True`, `smooth_idf=True` |

## B.4 Models and configurations

Both models are wrapped in a scikit-learn `Pipeline(vec, clf)`. Hyperparameters are fixed at their defaults (no per-model tuning), reflecting a scarce-data practitioner.

**Naive Bayes.** `MultinomialNB(alpha=1.0)` (Laplace smoothing). In RQ3, the prior is adjusted via `class_prior`:

| Configuration (RQ3) | `alpha` | `class_prior` |
|---|---|---|
| NB, empirical prior (default) | 1.0 | `None` (empirical class frequencies) |
| NB, uniform prior | 1.0 | `[1/3, 1/3, 1/3]` |

**Support Vector Machine.** `LinearSVC(C=1.0, class_weight=None, random_state=0, max_iter=5000)`. In RQ3, cost sensitivity is enabled via `class_weight`:

| Configuration (RQ3) | `C` | `class_weight` |
|---|---|---|
| SVM, unweighted (default) | 1.0 | `None` |
| SVM, balanced | 1.0 | `"balanced"` |

The balanced weighting assigns to class $j$ the weight $w_j = m / (C_{\text{classes}} \cdot m_j)$, where $m$ is the total number of training sentences, $m_j$ the number in class $j$, and $C_{\text{classes}} = 3$.

## B.5 Evaluation protocol

- **Cross-validation.** Stratified 10-fold CV (`StratifiedKFold(shuffle=True)`), repeated over 5 random seeds $\{0, 1, 2, 3, 4\}$.
- **Reporting.** Mean and standard deviation of the per-fold metrics, averaged across folds and then across seeds.
- **Metrics.** Accuracy, macro-averaged F1, weighted F1, and per-class precision / recall / F1 (with `zero_division=0`).

## B.6 Research-question specific settings

**RQ1 (learning curves).** Stratified 80/20 split (`StratifiedShuffleSplit`, `TEST_FRACTION = 0.2`) per seed; a fixed held-out test set; training sizes

$$[32,\ 64,\ 128,\ 256,\ 512,\ 1024,\ 2048,\ 3876],$$

the last being the full 80% training pool (3,876 of 4,846). Two feature modes: **per-subset** — the vectorizer is re-fitted on each training subset (vocabulary grows with sample size; the primary mode, reproducing Ng–Jordan's setup); **fixed-pool** — the vectorizer is fitted once on the full training pool (fixed vocabulary; robustness check isolating the classifier).

**RQ2 (label uncertainty).** Three layers: (a) within-subset stratified 10-fold CV on each of the four agreement subsets; (b) fixed clean test — training on each agreement subset, always evaluating on a held-out 20% of the AllAgree (100% agreement) sentences, with those test sentences excluded from training; (c) fixed-size disjoint bands — 600 sentences drawn from each non-overlapping agreement bin (all / 75–100% / 66–75% / 50–66%), stratified by class, evaluated on the same clean test set.

**RQ3 (class imbalance).** The four configurations of §B.4, run on the full 50Agree corpus (4,846 sentences) with stratified 10-fold CV over the 5 seeds.

## B.7 Reproducibility

- Configuration source of truth: `src/config.py`; shared evaluation utilities: `src/experiment_utils.py`; plotting: `src/plot_utils.py`.
- All experiments log their configuration snapshot and results to `results/*.jsonl`; figures are rendered at 300 dpi (PNG) plus vector PDF in `figures/`.

> 说明：B.3 的"remaining defaults"（`norm='l2'` 等）是 scikit-learn 默认值，未在代码里显式写出但生效；写附录时如实注明即可。**每个数字请对照你的 `results/*.jsonl` 与 `src/config.py` 复核一遍**，确认与正文 §3–§4 一致。
