---
name: daily-router
description: 日常流程编排（daily_router），对应 01_内容系统/知识库/每日日报/.github/scripts/run_daily_router.py。用 DeepSeek V4 Pro 跑三层漏斗：读四源日报→筛选题→写 _路由/YYYY-MM-DD.md→更新 _选题池.md。在用户说"跑路由/执行每日路由/手动触发今日路由/跑 router"时使用。
---

# daily_router · 每日路由

> GitHub Action 每天 12:20 自动运行本脚本；本技能用于**本地手动触发/调试/兜底**。
> 脚本：`01_内容系统/知识库/每日日报/.github/scripts/run_daily_router.py`

## 做什么

读当日四源报告（AI-HOT / X-Tweets / TrendRadar / FollowBuilders），用 DeepSeek 做三层漏斗：

1. **内容锚定**：锚点 A=AI、B=金融、C=金融史、D=高传播叙事
2. **框架适配**：用 8 本标尺书（[[叙事经济学]]、[[穷查理宝典]]、[[思考快与慢]]、[[明朝那些事儿]]、[[聪明的投资者]]、[[巴菲特致股东的信]]、[[文明现代化价值投资与中国]]、[[全球视野下的投资机会]]）讲出独特分析
3. **传播价值评分**：冲突/新鲜/情绪/解释/关联 5 要素

输出：`_路由/YYYY-MM-DD.md`（⭐高优先级 + 普通选题表 + 更新现有选题 + 丢弃摘要）+ 更新 `_选题池.md`。

## 本地运行

前置：当日四源文件已存在；环境变量 `DEEPSEEK_API_KEY` 已设置。

```powershell
cd "C:\Users\user\Documents\Obsidian Vault\01_内容系统\知识库\每日日报"
# 正常跑
python .github/scripts/run_daily_router.py
# 指定日期 + 干跑预览（不写正式输出）
$env:TODAY_OVERRIDE = "2026-08-07"; $env:ROUTER_DRY_RUN = "1"; python .github/scripts/run_daily_router.py
```

## 输出校验

- `_路由/YYYY-MM-DD.md` 三大 section 齐全（⭐高优先级 / 普通选题 / 更新现有选题）
- `_选题池.md` 🔥 区新增条目
- 异常查 `_系统健康/YYYY-MM-DD.md` 当日报告

## 红线

- 运行前确认当日数据源齐全（缺源会导致漏斗输入不完整）
- 干跑（DRY_RUN）优先：先预览再落地，避免污染选题池
