# CLAUDE.md — Obsidian 知识库工作约定

本仓库是「AI × 经济」Obsidian 知识库（vault 根）。任何 Claude Code 会话在本目录内工作时，默认遵守以下约定。系统蓝图见 `obsidian知识库框架.md`（权威）。

## 目录结构

```
01_内容系统/
├── 知识库/          # 沉淀内容：书籍（核心观点/《书名》笔记）、观点（_观点.md）、每日日报
├── 输出/            # 对外输出：公众号（占位/成文/选题池）
└── 系统/            # 运维层：技能库、改进提案、机器人、蒸馏、scripts、inbox
```

- `01_内容系统/系统/技能库/`：全部技能（SKILL.md），经 `.claude/skills/` junction 加载，改完即时生效
- `01_内容系统/知识库/每日日报/`：内容生产线（采集 → 路由 → 选题池 → 写作 → 输出），自带子 git 仓库
- `01_内容系统/系统/改进提案/`：PM 提案（`YYYY-MM-DD-改进提案.md`），状态机见其 README

## 路径与格式约定

- vault 内文件一律用**相对路径**（不带盘符、不带前导斜杠）
- 引用笔记用 wikilink：`[[路径/文件名]]`；回应时用 `[[文件]]` 便于点击
- 图片：外链先下载到本地再替换为 `![[文件名]]` 嵌入
- 写文件用 UTF-8；Windows 下 PowerShell 脚本需带 BOM，否则 PS 5.1 解析中文会乱

## Git 规则（双仓库，极易踩坑）

- **根仓库**：远程 `VerticalFall/obsidian-vault`；本地 commit 后 push 一律 `git push origin main:vault-backup`（**不推 main**）
- **每日日报子仓库**（`01_内容系统/知识库/每日日报/`）：远程 main，GitHub Action 每日 12:20 自动同步 → **本地只 commit、绝不 push**，且不修改 `.github/workflows` 与脚本（除非提案明确要求）
- 备份排除项：`.claudian/sessions/`、`.obsidian/workspace`、`.obsidian/cache`、`.trash/`（不 add、不提交）
- 冲突时**本地为权威**；`--ff-only` 失败则 stash→pull→pop，仍冲突即中止并告警，**绝不自动覆盖任何一方数据**
- 提交信息以 `Co-Authored-By: Claude <noreply@anthropic.com>` 结尾

## 内容红线（不可逾越）

- `_观点.md` / `_选题池.md` / 公众号文章正文的内容修改 → **必须经用户确认**后才动手
- 书籍提炼（book-summary）：忠于作者原意、不编造、不绑定知识库框架
- 机器人（CowAgent）写入仅限 `01_内容系统/系统/inbox/`，命名 `微信-YYYYMMDD-HHmm.md`
- PM 只出提案不执行；不编造问题（观测 vs 推测必须标注）；每条提案必须有可验证的验收标准

## 角色与流程速览

| 角色 | 入口 | 职责 |
|------|------|------|
| PM | `技能库/pm/SKILL.md` | 5 维自检（架构/链路/内容/查漏/升级）→ 出改进提案 |
| DevOps | `技能库/devops/SKILL.md` | 执行提案、测试、验证、回填状态 |
| 健康检查 | `每日日报/.github/scripts/check_health.py` | L1 自动检查 → `_系统健康/_告警摘要.md` + `待验证问题.md` |
| 蒸馏 | `技能库/weekly-distill/SKILL.md` | 每周一；随做选题池维护（🔥 冷却/表格卫生） |

- 提案状态机：待执行 → 执行中 → 待验收 → 已验收 ✅ / 已关闭
- 提案格式规范见 `技能库/pm/SKILL.md` §四（文件结构骨架 + 模板 + 硬性规则），示例 `改进提案/2026-08-08-改进提案.md`

## 技能索引（8 个，全部在 `01_内容系统/系统/技能库/`）

`pm` · `devops` · `daily-router` · `weekly-distill` · `weekly-backup` · `health-monitor` · `book-summary` · `wechat-writing`
