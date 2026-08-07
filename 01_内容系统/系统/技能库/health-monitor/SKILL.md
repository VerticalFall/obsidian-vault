---
name: health-monitor
description: >
  L1 系统健康体检：零 LLM 零成本检查四源产出、X 推文计数、路由日志、选题池存量、翻译成功率，
  输出 _系统健康/YYYY-MM-DD.md 日报 + 滚动 _告警摘要.md（仅 🔴/🟡）+ _待追加_待验证问题.md。
  当用户说"检查系统健康 / 看监控 / 跑健康检查 / 系统正常吗 / 今天有告警吗"时使用。
  每日已由 GitHub Action 自动运行；本技能用于本地手动检查 / 诊断 / 补跑。
---

# health-monitor · L1 系统健康监控

> 脚本：`01_内容系统/知识库/每日日报/.github/scripts/check_health.py`（纯 Python 标准库，零 LLM、零成本）
> 定位：**体检报告，不是修理工**。体检发现问题 → 转 PM / DevOps 走提案处理。

## 检查 5 项

| # | 检查项 | 判据 |
|---|--------|------|
| 1 | 四源产出 | AI-HOT / X-Tweets / TrendRadar / FollowBuilders 当日文件是否生成 |
| 2 | X 推文计数 | 当日拉取数量是否正常 |
| 3 | 路由日志 | `_路由/YYYY-MM-DD.md` 是否生成 |
| 4 | 选题池存量 | `_选题池.md` 🔥+🌿 数量是否健康 |
| 5 | 翻译成功率 | X-Tweets 翻译是否正常 |

输出：`_系统健康/YYYY-MM-DD.md` + 滚动 `_告警摘要.md`（**仅记 🔴/🟡**）+ `_待追加_待验证问题.md`。

## 执行步骤

```powershell
cd "C:\Users\user\Documents\Obsidian Vault\01_内容系统\知识库\每日日报"
python .github/scripts/check_health.py                                    # 今天
$env:TODAY_OVERRIDE = "YYYY-MM-DD"; python .github/scripts/check_health.py   # 指定日期
```

## 判读与处置

| 信号 | 含义 | 处置 |
|------|------|------|
| 🔴 | 链路断裂 / 数据缺失 | 转 PM / DevOps 尽快走提案处理 |
| 🟡 | 部分降级 | 观察，记入告警摘要 |
| 静默跳过 | X-Tweets（付费 API）/ TrendRadar（上游爬虫）依赖外部 | **正常不算故障**，`continue-on-error` 设计如此 |

## 输出校验（交付前自查）

- [ ] 日报已生成；🔴/🟡 已进入 `_告警摘要.md`
- [ ] 只有**需人工核实**的事项才写入 `_待追加_待验证问题.md`
- [ ] 有 🔴 时，明确转交对象（PM / DevOps）与上下文，不让问题挂在日报里无人认领

## 红线

- 告警摘要只记 🔴/🟡，**不记绿色**（绿色是常态，不刷存在感）。
- **不把推测当结论**：需要人工核实的才写进待验证问题。
- 本技能是只读体检；修复动作属于 DevOps，不在体检时顺手改文件。
