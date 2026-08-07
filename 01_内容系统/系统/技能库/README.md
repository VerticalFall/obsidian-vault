---
title: 技能库索引
type: index
tags: [技能库, 索引]
---

# 技能库索引（8 个 Claude 技能）

> Claude Code 通过 vault 根目录 `.claude/skills` 目录联接（junction）加载本目录的 8 个技能。
> 目录名用 ASCII 便于 Claude Code 稳定加载；中文标签写在 description 中（模型靠它触发）。

| 目录 | 中文标签 | 对应脚本/角色 |
|------|---------|--------------|
| [[pm/SKILL.md\|pm]] | PM（产品经理） | 规范性自检（架构/链路/内容/查漏/升级）→ 改进提案 → 验收回路 |
| [[devops/SKILL.md\|devops]] | DevOps（执行验证） | 读改进提案 → 实施 → 验证测试 → 回填状态 |
| [[wechat-writing/SKILL.md\|wechat-writing]] | 公众号写作 | 选题 → 两步调研 → 去 AI 味 → 四层自检 |
| [[daily-router/SKILL.md\|daily-router]] | daily_router | `run_daily_router.py`（DeepSeek 三层漏斗） |
| [[weekly-distill/SKILL.md\|weekly-distill]] | weekly_distill | `run_weekly_distill.py`（周度信号蒸馏） |
| [[health-monitor/SKILL.md\|health-monitor]] | 日常监控 | `check_health.py`（L1 零 LLM 体检） |
| [[weekly-backup/SKILL.md\|weekly-backup]] | 全库备份 | 周一随蒸馏：vault 本地内容 → 远程 `vault-backup` 分支 |
| [[book-summary/SKILL.md\|book-summary]] | 书籍核心观点提炼 | 诚实提炼作者核心思想（不绑定系统） |

## 目录联接说明

```
.claude/skills  →  01_内容系统/系统/技能库  (Junction)
```

Windows 目录联接（junction）无需管理员权限。若损坏，重建命令：

```powershell
New-Item -ItemType Junction -Path "C:\Users\user\Documents\Obsidian Vault\.claude\skills" -Target "C:\Users\user\Documents\Obsidian Vault\01_内容系统\系统\技能库"
```
