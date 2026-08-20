# Appendix A：Error Decomposition of Generative and Discriminative Learning

> **本文是推导骨架，数学内容可直接采用，但必须由洛哥逐条核对后定稿。**
> - 数学公式与结论口径已按 Ng & Jordan (2002) 的摘要与主要命题核实（见文末「核实说明」）；但**命题编号、确切的界式以你手头的原论文为准**，这是数学系论文的底线。
> - `[洛哥填：...]` 的句子是解释性过渡文字，按合规红线由你写；下面的公式与推导步骤属客观数学内容，可以直接用。
> - 正文 §2.2 引用本附录为"A formal sketch … in Appendix A"。

---

## A.1 Setup and the error decomposition

Notation. Let $P(X, Y)$ be the joint distribution on $\mathcal{X} \times \mathcal{Y}$, with $\mathcal{Y} = \{1, \dots, C\}$ classes (in this thesis $C = 3$). Let $S_m = \{(x_i, y_i)\}_{i=1}^m$ be $m$ i.i.d. training examples. A classifier $h: \mathcal{X} \to \mathcal{Y}$ incurs the 0–1 risk

$$R(h) \;=\; \mathbb{P}_{(X,Y) \sim P}\bigl[\, h(X) \neq Y \,\bigr],$$

and $R^{*} = \inf_{h} R(h)$ denotes the Bayes error over all measurable classifiers.

Let $\hat h_m$ be the classifier returned by a given learning rule from $S_m$, and let $h_\infty = \lim_{m \to \infty} \hat h_m$ be its infinite-data (asymptotic) limit within the chosen model family. The expected risk of the finite-sample classifier decomposes as

$$\mathbb{E}_{S_m}\bigl[ R(\hat h_m) \bigr] \;=\; \underbrace{\bigl[\, R(h_\infty) - R^{*} \,\bigr]}_{\text{asymptotic (bias) term}} \;+\; \underbrace{\mathbb{E}_{S_m}\bigl[\, R(\hat h_m) - R(h_\infty) \,\bigr]}_{\text{estimation term}}.$$

The first bracket is the **asymptotic term**: how far the model family's infinite-data solution sits above the Bayes error. It depends only on the model family and the true distribution — not on $m$. The second bracket is the **estimation term**: how far the finite-sample solution sits above the family's own asymptote; this is the term that shrinks as $m$ grows, and it is where the generative and discriminative families differ in *rate*.

Ng and Jordan (2002) compare the two families along these two axes. We restate their two claims and the mechanism behind each.

## A.2 Asymptotic term: the discriminative model is never worse in the limit

- **Discriminative (linear SVM / logistic regression).** $h_\infty^{disc}$ minimizes the population objective over the linear hypothesis class directly — it optimizes the decision boundary, with no structural assumption on the data-generating process beyond linear separability.
- **Generative (naive Bayes).** $h_\infty^{gen}$ is the classifier obtained by applying Bayes' rule to the maximum-likelihood estimate of the joint model under the *conditional-independence* ("naive") assumption.

**Claim 1 (asymptotic comparison; Ng & Jordan 2002, Prop. 1).** If the conditional-independence assumption holds for $P$, both families converge to the same classifier in the limit. If it fails, the generative model's infinite-data classifier is constrained by an incorrect assumption, whereas the discriminative model's is not. Equivalently, the naive-Bayes posterior is a specific parametric form that the linear-discriminative family can represent, so the latter's population optimum is at least as good:

$$R\bigl(h_\infty^{disc}\bigr) \;\le\; R\bigl(h_\infty^{gen}\bigr).$$

`[洛哥填：一句话用自己的话解释"判别式直接学边界、不学分布，所以渐进误差不高于生成式"——正文 §2.2 已经讲了直觉，附录这里只需一句承上启下即可，可引用 Prop. 1。]`

## A.3 Estimation term: why the generative model needs fewer examples

Here the crucial object is the **number of parameters of the model family, which the original paper denotes by $n$**. (Careful: this $n$ is *not* the training sample size; in this appendix we keep $m$ for the sample size.) For $d$ features the two families each have on the order of $O(d)$ parameters.

**Claim 2 (sample complexity; Ng & Jordan 2002, Props. 2 and Lemma/Corollary in §4).** To reach within a fixed tolerance of its own asymptotic error,

- the **generative** model needs on the order of $O(\log n)$ training examples, and
- the **discriminative** model needs on the order of $O(n)$ training examples,

where $n$ is the number of parameters (VC dimension) of the model.

The mechanism is the coupling or decoupling of the parameter estimates.

**Generative model — decoupled parameters.** The naive-Bayes parameters are the class-conditional probabilities $\{P(x_i \mid y)\}$, estimated independently, one class and one feature at a time, by relative-frequency counting on that class's own examples. Consider estimating a single such probability (a Bernoulli mean) to within $\delta$ with probability at least $1 - \eta$: by Hoeffding's / Chernoff's inequality, $m = O\bigl(\delta^{-2} \log(1/\eta)\bigr)$ examples of that class suffice. To make *all* $n$ parameters accurate simultaneously, take a union bound over the $n$ parameters — replace $\eta$ by $\eta / n$ — giving

$$m_{gen} \;=\; O\Bigl( \delta^{-2} \log \frac{n}{\eta} \Bigr).$$

For fixed tolerance $(\delta, \eta)$, the required sample size therefore grows **only logarithmically in the number of parameters $n$**. Moreover, small perturbations of the parameter vector move the induced decision boundary by a correspondingly small amount (the 0–1 risk is Lipschitz in the parameter error), so the *risk* estimation error is controlled by the parameter error. Hence NB attains its asymptotic error with $O(\log n)$ examples.

**Discriminative model — coupled parameters.** The linear-SVM / logistic-regression parameters are the solution of a single joint optimization over all $n$ parameters at once; they cannot be decomposed into independent sub-problems. Uniform-convergence bounds over the class of linear separators in $\mathbb{R}^d$ — whose VC dimension is $O(n)$ — yield sample requirements that scale **linearly** in $n$,

$$m_{disc} \;=\; O(n \cdot \text{(factor depending on the tolerance))}.$$

`[洛哥填：上面两条"机制"段的措辞可自由重写，但方向别反——核心对比是"生成式参数解耦、逐个独立估，误差经并集界只叠加 log n；判别式参数耦合、联合优化，样本需求随参数数线性增长"。若你要把界式写成精确形式，请直接抄原论文 §4 的定理，不要用我这里的 O(·) 口语化写法。]`

## A.4 Two regimes and the crossover

Putting A.2 and A.3 together gives the two-phase picture used throughout the thesis:

- **Small $m$.** NB is already within $O(\delta^{-2} \log(n/\eta))$ of its (possibly worse) asymptote; the discriminative model is still far from its (better) asymptote. The generative model can therefore win.
- **Large $m$.** The discriminative model has converged to its lower asymptote; the generative model's asymptotic penalty dominates. The discriminative model wins.

A crossover exists where the two effects balance, and its location is problem-dependent (it depends on $P$, the feature dimension, and the signal strength).

**Relation to RQ1.** The claim is about sample complexity in the number of *parameters* $n$; the thesis fixes the model size (one feature pipeline, fixed hyperparameters) and varies the *sample size* $m$ across $\{32, \dots, 3876\}$. With $n$ fixed, increasing $m$ traverses exactly the two regimes above, so the predicted crossover should appear in the 0–1 error (accuracy) — which is precisely RQ1's accuracy result (§4.2). The macro-F1 metric, which weights classes equally, is outside the 0–1 framework of this appendix; §5.1 discusses why the prediction fails there.

## Verification note（洛哥核对清单）

1. 本文口径（两轴分解 + 渐进比较 + $\log n$ vs $n$ 的样本复杂度、$n$ = 参数个数/VC 维）已与 Ng & Jordan (2002) 摘要及多份忠实转述核对一致。
2. 你手头有原论文时，**把 Claim 1/Claim 2 与原文 Prop. 1、Prop. 2、Lemma 3、Corollary 6 逐一对照**，命题编号以原文为准。
3. 若你决定把界式写精确（如判别式侧的 $O\!\left(\sqrt{(n/m)\log(m/n)}\right)$ 形式），务必直接抄录原文，不要凭记忆改写。
4. 正文 §2.2 只说"正式推导在 Appendix A"——本附录的深度由你定，但**数学必须自洽**。
