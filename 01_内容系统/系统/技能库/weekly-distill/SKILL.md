---
name: weekly-distill
description: 周常信息蒸馏（weekly_distill），对应 01_内容系统/知识库/每日日报/.github/scripts/run_weekly_distill.py。每周一回看 7 天路由日志→信号群聚类→冷却判断→沉淀可复用框架，产出蒸馏草稿，人工审核后定稿到 01_内容系统/系统/蒸馏/。在用户说"跑周度蒸馏/周常汇总/审核蒸馏草稿/蒸馏"时使用。
---

# weekly_distill · 周度蒸馏

> GitHub Action 每周一自动跑脚本；本技能用于**本地手动触发 + 人工审核定稿**。
> 脚本：`01_内容系统/知识库/每日日报/.github/scripts/run_weekly_distill.py`

## 做什么

读 7 天路由日志 + 选题池 + 观点，用 DeepSeek 做三件事：

1. **信号群合并**：跨天信号聚类，标注成熟度（🌳可写级 / 🌿发酵中 / 🌱早期 / 🍂消退中）
2. **冷却判断**：选题池瘦身（哪些降温、哪些归档）
3. **沉淀可复用框架 + 回顾观点**：对照 `_观点.md` 判断是否需要修正观点

脚本产出草稿：`_蒸馏/W{ISO周}-draft.md`（草稿头部标注定稿路径 `01_内容系统/系统/蒸馏/{week_label}.md`）。

## 本地运行

前置：环境变量 `DEEPSEEK_API_KEY` 已设置。

```powershell
cd "C:\Users\user\Documents\Obsidian Vault\01_内容系统\知识库\每日日报"
python .github/scripts/run_weekly_distill.py
# 干跑预览
$env:DRY_RUN = "1"; python .github/scripts/run_weekly_distill.py
```

## 人工审核定稿（Phase 3-4）

1. 读草稿 `_蒸馏/W*-draft.md`
2. 确认信号群成熟度分级是否合理
3. 冷却判断：哪些选题应从 `_选题池.md` 降温/归档
4. 提取可复用框架，写入 `_蒸馏` 或知识库
5. 对照 `_观点.md`：是否有判断需要修正（AI 提议、用户确认后写入，并在变更记录追加一行）
6. **定稿**：复制到 `01_内容系统/系统/蒸馏/W{周}.md`（脚本会提示最终路径）

## 红线

- 观点修正必须用户确认后才写入 `_观点.md`
- 冷却判断要克制：单日波动不降级，多日无信号才降级
