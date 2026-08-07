---
name: health-monitor
description: L1 系统健康监控（日常监控），对应 01_内容系统/知识库/每日日报/.github/scripts/check_health.py。零 LLM 零成本，检查四源产出、X 推文计数、路由日志、选题池存量、翻译成功率，输出 _系统健康/ 日报 + 滚动告警摘要。在用户说"检查系统健康/看监控/跑健康检查/系统正常吗"时使用。
---

# health-monitor · L1 系统健康监控

> GitHub Action 每天自动运行；本技能用于**本地手动检查/诊断**。
> 脚本：`01_内容系统/知识库/每日日报/.github/scripts/check_health.py`（纯 Python 标准库，零 LLM）

## 检查 5 项

1. 四源产出：AI-HOT / X-Tweets / TrendRadar / FollowBuilders 当日文件是否生成
2. X 推文计数：当日拉取数量是否正常
3. 路由日志：`_路由/YYYY-MM-DD.md` 是否生成
4. 选题池存量：`_选题池.md` 🔥+🌿 数量是否健康
5. 翻译成功率：X-Tweets 翻译是否正常

输出：`_系统健康/YYYY-MM-DD.md` + 滚动 `_告警摘要.md`（仅 🔴/🟡）+ `_待追加_待验证问题.md`。

## 本地运行

```powershell
cd "C:\Users\user\Documents\Obsidian Vault\01_内容系统\知识库\每日日报"
python .github/scripts/check_health.py
# 检查指定日期
$env:TODAY_OVERRIDE = "2026-08-07"; python .github/scripts/check_health.py
```

## 判读与处置

| 信号 | 含义 | 处置 |
|------|------|------|
| 🔴 | 链路断裂/数据缺失 | 转 PM/DevOps 尽快处理 |
| 🟡 | 部分降级 | 观察，记入告警摘要 |
| 静默跳过 | X-Tweets（付费 API）/ TrendRadar（上游爬虫）依赖外部 | **正常不算故障**，`continue-on-error` 设计如此 |

## 红线

- 告警摘要只记 🔴/🟡，不记绿
- 需人工核实的才写 `_待追加_待验证问题.md`，不把推测当结论
