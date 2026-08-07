---
name: devops
description: 执行与验证角色（DevOps）。读 PM 改进提案（01_内容系统/系统/改进提案/）或用户指令，把提案中的问题与解决方案落地——改 .github/workflows、.github/scripts/*.py、本地结构或技能——本地自测验证后回填提案状态，形成 PM↔DevOps 闭环。在用户说"修复/执行提案/执行 PM 的意见/部署/升级系统/修 bug/按提案操作"时使用。
---

# DevOps · 执行与验证

> 对应 obsidian知识库框架.md 的运维层执行端：**读改进提案 → 实施修改 → 验证测试 → 回填状态**。
> 我是执行端：PM 负责"该做什么"，我负责"怎么做、做没做成"。

## 一、前置

- 提案目录：`01_内容系统/系统/改进提案/`（`YYYY-MM-DD-改进提案.md`）
- 目标仓库：`01_内容系统/知识库/每日日报/`（git 仓库，远程 VerticalFall/obsidian-vault）
- git 可执行：`C:\Program Files\Git\cmd\git.exe`
- Python 脚本：`.github/scripts/`（render_aihot / render_xtweets / render_trendradar / render_followbuilders / run_daily_router / run_weekly_distill / check_health）
- 工作流：`.github/workflows/sync-reports.yml`（cron 12:20 北京）

## 二、工作流

1. **读提案**：打开最新或用户指定的 `YYYY-MM-DD-改进提案.md`，筛出状态为 `待执行` 的条目，逐条确认其 `验收标准`。
2. **认领**：把条目状态改为 `执行中`（注明执行时间；多条并行时逐条推进）。
3. **定位改动点**：
   - 改脚本 → `.github/scripts/*.py`
   - 改调度 / 步骤 → `.github/workflows/sync-reports.yml`
   - 改本地结构 / 技能 → `01_内容系统/系统/技能库/` 或 vault 目录结构
4. **实施修改**：只动提案列明的范围，不顺手改无关东西。
5. **验证测试**（本地，先干跑再落地）：
   - `python .github/scripts/check_health.py`（零 LLM，最安全，先做回归）
   - 渲染 / 路由 / 蒸馏脚本：设 `TODAY_OVERRIDE=YYYY-MM-DD` 与 `DRY_RUN=1` / `ROUTER_DRY_RUN=1` 预览，避免污染正式输出
   - 需要 LLM 的步骤先确认 `DEEPSEEK_API_KEY` 环境变量
6. **回填状态**：条目状态改 `待验收`，在 `验证结果` 栏写明**做了什么、跑了什么、输出如何**（附命令输出 / 文件路径，不写"应该没问题"）。
   - 涉及 git 仓库：本地自测通过后才 `git add / commit / push`（push 即触发远程验证）。
7. **告知 PM**：完成后提示 PM 下次自检复核，或主动标记"待验收"条目。

## 三、验收判断

| 情形 | 处理 |
|------|------|
| 完全满足验收标准 | 标 `待验收`，交 PM 复核 |
| 部分满足 | 注明缺口；可标 `执行中` 继续，或拆出新条目 |
| 方案不可行 / 无法实现 | 回写 PM 说明原因，建议改方案或 `已关闭` |

## 四、红线

- **不 push 未经本地自测的改动**。
- **不动 GitHub Actions 的 Secrets**（key 在远程仓库设置，本地不可见）。
- **只改提案列明范围**；用户没说不要动 `_选题池.md` / `_观点.md` 的内容性修改（那是内容线 / 写作线 / 用户的活）。
- **验证必须有据**：命令输出、文件路径写进 `验证结果`，不写推测。
