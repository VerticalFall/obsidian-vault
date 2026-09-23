---
name: daily-digest
description: >
  生成/查看「每日精选」——把当日四源（AI-HOT / TrendRadar / X-Tweets / FollowBuilders）
  与路由日志统合成一份可读的当日精选：跨领域要闻 + 数字速览 + 领域速览 + 今天可写选题。
  当用户说"今天看什么 / 每日精选 / 今天的新闻 / 今天有什么值得写的 / 跑一下精选 /
  今天的信息统合一下"时使用。
---

# daily-digest · 每日精选

> 脚本：`01_内容系统/知识库/每日日报/.github/scripts/render_daily_digest.py`
> 产物：`01_内容系统/知识库/每日日报/_每日精选/YYYY-MM-DD.md`
> 模型：DeepSeek（环境变量 `DIGEST_MODEL`，默认 `deepseek-flash` = V4.1 Flash）
>
> ⚠️ **不要改用 `deepseek-chat`**：该别名已于 2026-07-24 停用，用了会静默失败。
> 模型名的机械守卫见 `每日日报/_test_model_names.py`。

## 这是什么 / 解决什么问题

四源报告按源分文件，路由日志又是给写作用的筛选结果——**每天要看 5 个文件才拼得出全貌**。
本技能把它们合成一份：读完这一份就知道今天发生了什么、什么最重要、可以写什么。

链路里的位置：**消费层**，与 router 不重叠。

```
采集（四源）→ 筛选（daily-router → 路由日志 + 选题池）→ 消费（本技能：每日精选）→ 写作（wechat-writing）
```

- `daily-router` 回答「今天什么值得写」（筛选）
- `daily-digest` 回答「今天发生了什么、什么最重要」（提纯 + 可读化）

## 什么时候用

- **自动**：GitHub Action 每天 12:20 在路由之后自动跑，产物随每日报告同步到本地。
- **手动**：本地补跑（Action 失败、或想立刻看今天的内容）。

## 执行步骤

1. **确认四源已同步**：
   ```powershell
   cd "C:\Users\user\Documents\Obsidian Vault\01_内容系统\知识库\每日日报"
   git pull --ff-only
   ```
   若 `AI-HOT/`、`TrendRadar/` 没有当天文件，先解决采集问题，不要硬跑。

2. **生成精选**：
   ```powershell
   $env:DEEPSEEK_API_KEY = "<key>"
   python .github\scripts\render_daily_digest.py
   # 预览（写 _每日精选_dryrun.md，不覆盖正式产物）：
   $env:DIGEST_DRY_RUN = "1"; python .github\scripts\render_daily_digest.py
   # 降级版（不调 LLM，机械提取；API 故障期间也能每天有一份）：
   $env:DIGEST_NO_LLM = "1"; python .github\scripts\render_daily_digest.py
   ```
   指定日期补跑：`$env:TODAY_OVERRIDE = "2026-09-23"`

3. **读产物**：`_每日精选/YYYY-MM-DD.md`。四个区必须齐全：最重要的 5 条 / 数字速览 /
   领域速览 / 今天可写。缺区说明输出被截断，脚本会打印 `WARNING: 精选体检未通过`。

4. **进入写作**：从「今天可写」区挑一条 → 走 `wechat-writing` 技能。

## 降级版（LLM 不可用时）

LLM 调用失败时脚本**不再直接归零**，而是产出「降级版精选」：

| | 正常版 | 降级版 |
|---|---|---|
| 触发 | LLM 正常 | LLM 失败，或 `DIGEST_NO_LLM=1` |
| 标题 | `# 每日精选 · 日期` | `# 每日精选（降级版）· 日期` |
| 数字速览 | LLM 提炼并解释含义 | 脚本从四源机械摘录（含原文上下文） |
| 今天最重要的 | LLM 跨领域排序 | 路由日志里的 ⭐ 选题原文 |
| 可信度 | 经编辑加工 | **未经加工，数字未核对语义**，文件头有明确标注 |

设计理由：LLM 一坏整条产出层就归零，而本机 LLM 恰恰已经坏了几周。产出层不能
建立在单点上——哪怕只给机械摘录，也比"今天什么都没有"有用。

## 输出校验（交付前自查）

- [ ] 产物落在 `_每日精选/YYYY-MM-DD.md`
- [ ] 「数字速览」区有真数字（不是"成本在下降"这类无数字描述）
- [ ] 「今天可写」区的选题与当日路由日志一致（不要凭空冒出新选题）
- [ ] 脚本无 `WARNING: 精选体检未通过` 输出
- [ ] 若产物是降级版：确认头部有「未经 LLM 编辑加工」标注，且**引用前先核对数字**

## 红线

- **不许编造数字**：精选里的每个数字必须来自当日四源或路由日志；材料里没有就少写一条。
- **不替代写作**：精选是输入不是成品，公众号正文仍走 `wechat-writing` 的两步调研 + 四层自检。
- **`_每日精选/` 是 Action 产物**：不要手改（会被下次 `git pull` 覆盖），要改就改脚本。
