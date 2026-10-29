---
name: bank-research-excel
description: Research and value listed commercial banks—especially Chinese A-share and H-share banks—from current official disclosures and market data, then create either a compact shareable ranking package or a full Excel research report. Use for bank valuation, dividend sustainability, peer comparison, investor-profile ranking, Bilibili/social-media scorecards, or full bank investment research. Do not use for non-bank companies, personal banking products, or generic macro commentary.
---

# 银行估值系统

把银行研究做成可复核的量化结果。低估值只是待验证的假设，不能直接等同于低风险或高回报。

## 先选择输出模式

- 用户提到“简版、传播版、B站动态、排行榜、总榜、几张图”时，默认使用**传播版**，读取 `references/shareable-output-spec.md`。
- 用户明确要求“完整、深度、十一页、一图流研究报告”时，使用**完整版**，读取 `references/excel-workbook-spec.md`。
- 若用户未说明，但任务是全市场多银行排名，优先传播版；若任务是单家银行深度研究，优先完整版。

两种模式都必须读取：

1. `references/bank-research-methodology.md`
2. `references/data-and-period-rules.md`
3. `references/investor-profile.md`

`assets/A股银行量化榜_B站动态简版_20261015.xlsx` 仅用于展示传播版结构与视觉标准。它是 2026-10-15 收盘时点的历史快照，不得被当作持续更新的数据源。

## 共同原则

### 1. 固定研究边界

- 明确银行、上市地、代码、币种、经营数据截止日、股价日和同业快照日。
- 经营数据日期与市场价格日期分开显示。
- “最新”属于时效信息，必须核验；未披露的数据不能推测填充。

### 2. 数据可追溯

- 财务与监管指标优先使用财报、交易所公告、投资者关系材料和监管披露。
- 行情数据可使用可靠市场数据源，关键价格应交叉核对。
- 统一单位和口径，保留来源、日期及必要的页码或表格位置。

### 3. 先看质量，再谈估值

至少覆盖盈利趋势、净息差、减值贡献、资产质量、重点风险暴露、资本充足率和分红能力。不得让低 PB、低 PE 或高股息完全抵消明显的资本与资产质量风险。

### 4. 公正性与投资者适配分开

- 四项基础分固定为：盈利质量、风险资本、估值、股息，均为 0–100 分。
- 固定权重的“基准研究分”用于跨投资者比较，不能随问卷变化。
- 问卷只生成稳健收息、均衡复利、进取修复三种“画像匹配分”，不得改写原始数据、基础分或基准估值。
- 权重必须事先固定，不能看完排名后再调参。
- 执行 `investor-profile.md` 的非补偿性风险上限；基础风险过低时，再便宜也不能获得不受限制的高排名。

### 5. 估值保持多锚点

完整版原则上使用剩余收益、PB–ROE、历史 PB、历史 PE、同业 ROE 调整 PB、两阶段 DDM，并以股息率反推价值交叉验证。传播版可以只展示最终估值分，但底层计算必须来自同一套可复核口径。

## 传播版工作流

1. 汇总全市场或指定银行范围，检查股票代码、银行类别与日期。
2. 计算四项基础分、固定基准研究分、三类画像匹配分与风险上限后的排名。
3. 生成两页简版 Excel 和两张适合社交媒体直接发布的 PNG。
4. 用户要求“四类银行全部明细”时，另交付五页榜单：总榜、四大行、股份行、城商行、农商行。
5. 页面只保留结论、得分、日期、口径和必要风险提示；不附检查日志、预览缓存或中间数据。
6. 按 `shareable-output-spec.md` 完成尺寸、可读性和传播检查。

## 完整版工作流

1. 建立来源台账并核对财务、每股、分红和资本数据。
2. 区分报告 ROE 与可持续 ROE，解释所有标准化调整。
3. 评估盈利、资产质量、资本、流动性、治理与分红约束。
4. 使用多模型估值，披露权重及两种安全边际。
5. 按 `excel-workbook-spec.md` 生成十一张工作表，公式联动并逐页检查。

## 验证

- 重新计算工作簿并扫描 `#REF!`、`#DIV/0!`、`#VALUE!`、`#NAME?`、`#N/A` 等错误。
- 完整版测试至少一个估值假设和一个问卷答案；基准研究分不得随问卷变化。
- 传播版核对榜单数值与底层表一致，检查两张图片无裁切、无行列标题、手机端可读。
- 运行 `scripts/check_bank_report.py <workbook.xlsx>`；脚本会自动识别完整版、传播版或五页分类榜。

## 交付

传播版默认交付：

- 两页简版 `.xlsx`；
- 两张可直接发布的 `.png`；
- 如用户需要，再附五页四类银行评分与总榜 `.xlsx`。

完整版默认交付一份十一页 `.xlsx`，并概述合理价值区间、双安全边际、核心假设、主要风险、经营数据日期和股价日期。

不要给出个性化买卖指令。把结果表述为研究结论、适配度、假设区间和跟踪条件。
