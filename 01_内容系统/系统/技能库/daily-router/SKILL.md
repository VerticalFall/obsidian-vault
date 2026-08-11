---
name: daily-router
description: >
  手动运行每日路由：读当日四源报告（AI-HOT / X-Tweets / TrendRadar / FollowBuilders），
  用 DeepSeek 三层漏斗（内容锚定 → 框架适配 → 传播价值评分）筛选题，
  产出 _路由/YYYY-MM-DD.md 并更新 _选题池.md。
  当用户说"跑路由 / 执行每日路由 / 手动触发今日路由 / 跑 router / 补跑某天路由"时使用。
  注意：每日 12:20 已由 GitHub Action 自动运行，本技能只用于手动触发、调试或补跑缺失日期；
  已存在路由文件的日期不要重跑（会覆盖当天文件）。
---

# daily_router · 每日路由

> 脚本：`01_内容系统/知识库/每日日报/.github/scripts/run_daily_router.py`
> 模型：DeepSeek（环境变量 `ROUTER_MODEL`，默认 `deepseek-v4-flash`）

## 这是什么 / 何时用

- **自动**：GitHub Action 每天 12:20 自动运行，无需人工。
- **手动**：本技能用于——当天自动跑挂了要补跑、调试脚本、为历史日期补建路由、或用户明确要求手动触发。
- 已在 `_路由/` 存在的日期**不要重跑**，除非确认要重建当天文件。

## 前置条件（不满足不要跑）

- 当日四源文件已存在：`AI-HOT/YYYY-MM-DD.md`、`X-Tweets/…`、`TrendRadar/…`、`FollowBuilders/…`
  （缺源 → 漏斗输入不完整；先补齐数据，或确认该源当天按设计跳票）
- 环境变量 `DEEPSEEK_API_KEY` 已设置。
- 工作目录：`01_内容系统/知识库/每日日报`

## 执行步骤

1. **先干跑**（不写正式输出，只产出两个预览文件）：
   ```powershell
   cd "C:\Users\user\Documents\Obsidian Vault\01_内容系统\知识库\每日日报"
   $env:TODAY_OVERRIDE = "YYYY-MM-DD"; $env:ROUTER_DRY_RUN = "1"
   python .github/scripts/run_daily_router.py
   ```
   干跑输出：`_router_dryrun_route.md` + `_router_dryrun_topics.md`（临时预览，核对后删除）。
2. **核对预览**：⭐高优先级 / 普通选题 / 更新现有选题 三大 section 齐全；高优先级 ≤5 条；角度与锚点匹配。
3. **正式运行**（不设 `ROUTER_DRY_RUN`，`TODAY_OVERRIDE` 可留空=今天）：
   ```powershell
   $env:TODAY_OVERRIDE = "YYYY-MM-DD"; python .github/scripts/run_daily_router.py
   ```
4. **验证**（见下），并清理 `_router_dryrun_*.md`。

## 输出校验（交付前自查）

- [ ] `_路由/YYYY-MM-DD.md` 已生成，⭐区有高优先级选题
- [ ] `_选题池.md` 🔥 区新增条目，且没有把已归档选题重新激活
- [ ] 有异常时查 `_系统健康/YYYY-MM-DD.md` 当日报告，定位后再处置

## 红线

- **先干跑后落地**，避免直接污染选题池。
- **缺源不硬跑**：数据源缺失要记录（走 health-monitor / PM），不能让漏斗在残缺输入上"照常输出"。
- 本技能只动 `每日日报` 仓库内的文件；`_观点.md` 的修正走 weekly-distill / PM 流程，不在此处改。
