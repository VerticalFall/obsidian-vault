# 参考文献清单（References）

> **合规要求**：只登记真实来源，严禁编造。带 ✅ 的已核实书目信息；带 ⚠️ 的为"核心可信、细节待核实"（终稿前统一核对卷/期/页）。
> 目标 25–35 篇。下面列出的都是经典文献，**真实存在**；⚠️ 仅书目细节待二次核对。
> 终稿时转 BibTeX（`refs.bib`）。引用时只引用你**实际读过/用到的**，宁少勿凑。

---

## ✅ 已核实（书目信息已核对）

1. **Ng, A. Y., & Jordan, M. I. (2002).** On discriminative vs. generative classifiers: A comparison of logistic regression and naive Bayes. *Advances in Neural Information Processing Systems 14 (NIPS 2001)*, 841–848.
   - 用途：全文理论核心（RQ1 的试金石）。
2. **Malo, P., Sinha, A., Korhonen, P., Wallenius, J., & Takala, P. (2014).** Good debt or bad debt: Detecting semantic orientations in economic texts. *Journal of the Association for Information Science and Technology*, 65(4), 782–796. DOI: 10.1002/asi.23062.
   - 用途：数据集出处（Financial PhraseBank）。
3. **Kumar, B. S., & Ravi, V. (2016).** A survey of the applications of text mining in financial domain. *Knowledge-Based Systems*, 114, 128–147. DOI: 10.1016/j.knosys.2016.10.003.
   - 用途：金融文本挖掘领域综述入口（2.1）。
4. **Frénay, B., & Verleysen, M. (2014).** Classification in the presence of label noise: A survey. *IEEE Transactions on Neural Networks and Learning Systems*, 25(5), 845–869.
   - 用途：标签噪声综述（2.5、3.5）。

## ⚠️ 待核实书目细节（内容真实，卷/期/页终稿前核对）

5. **Cortes, C., & Vapnik, V. (1995).** Support-vector networks. *Machine Learning*, 20(3), 273–297.
   - 用途：SVM 奠基（2.3）。
6. **Vapnik, V. N. (1998).** *Statistical Learning Theory*. Wiley.
   - 用途：判别式"直接求解"原则的思想源头（2.2/2.4 可引）。
7. **Domingos, P., & Pazzani, M. (1997).** On the optimality of the simple Bayesian classifier under zero-one loss. *Machine Learning*, 29, 103–130.
   - 用途：NB 理论性质（2.3）。
8. **Zhang, H. (2004).** The optimality of naive Bayes. *Proceedings of the 17th International Florida Artificial Intelligence Research Society Conference (FLAIRS)*, 562–567.
   - 用途：NB 条件独立假设下仍最优的讨论（2.3）。
9. **Joachims, T. (1998).** Text categorization with support vector machines: Learning with many relevant features. *European Conference on Machine Learning (ECML)*, 137–142.
   - 用途：SVM 文本分类经典（2.3）。
10. **Loughran, T., & McDonald, B. (2011).** When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. *Journal of Finance*, 66(1), 35–65.
    - 用途：金融文本词典法 / 领域词汇差异（2.1）。
11. **Tetlock, P. C. (2007).** Giving content to investor sentiment: The role of media in the stock market. *Journal of Finance*, 62(3), 1139–1168.
    - 用途：媒体情绪与市场（2.1，可选）。
12. **He, H., & Garcia, E. A. (2009).** Learning from imbalanced data. *IEEE Transactions on Knowledge and Data Engineering*, 21(9), 1263–1284.
    - 用途：类别不平衡综述（2.5、3.6）。
13. **Galar, M., et al. (2012).** A review on ensembles for the class imbalance problem: Bagging-, boosting-, and hybrid-based approaches. *IEEE Transactions on Systems, Man, and Cybernetics, Part C*, 42(4), 463–484.
    - 用途：不平衡方法（2.5，可选）。
14. **Provost, F., & Fawcett, T. (2001).** Robust classification for imprecise environments. *Machine Learning*, 42(3), 203–231.
    - 用途：代价/不平衡下的评估视角（3.7/5.3，可选）。
15. **Wang, S., & Manning, C. D. (2012).** Baselines and bigrams: Simple, good sentiment and topic classification. *Proceedings of ACL*, 90–94.
    - 用途：支持"简单线性模型 + n-gram 仍具竞争力"（2.4，呼应 LLM 时代定位）。
16. **Zhang, P., & Xing, F. (2022).** Financial sentiment analysis: An investigation into common mistakes and silver bullets. *Proceedings of COLING*, 978–987.
    - 用途：金融情感分析的常见坑（2.1/5.4，可选，呼应我们数据/评估上的谨慎）。

## 备注

- 上述 16 篇构成核心；若要冲 25–35 篇，可补充：Ng-Jordan 的后续讨论、金融词典扩展（Loughran & McDonald 2016 词典更新）、不平衡的 SMOTE（Chawla et al. 2002）、标签噪声下的学习（Nataranjan et al. 2013）、情感分析综述（Liu 2012 等）——但**只引实际用到的**。
- ⚠️ 条目的卷/期/页：终稿阶段（Phase 4）我会统一用 DOI/官方页面逐条核对后生成 `refs.bib`。
- 引用格式以你选的期刊风格为准（参考 §2.11 手册建议：可挑一个目标期刊的 author guidelines）。
