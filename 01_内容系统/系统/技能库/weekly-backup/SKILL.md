---
name: weekly-backup
description: 全库手动备份（weekly-backup）。把 vault 全部本地内容（书籍/输出/技能/框架/配置，排除每日日报子仓库与缓存）提交并 push 到私有仓库 VerticalFall/obsidian-vault 的 vault-backup 分支。每日双向同步（sync-vault.ps1，计划任务 13:00 + 登录时）已自动覆盖；本技能保留为手动全量快照与周一存档兜底。防止磁盘丢失/重装导致知识库再次全丢。在用户说"备份/全库备份/提交备份/做个备份/手动快照"时使用。
---

# weekly-backup · 全库远程备份

> 目的：把 vault 里**不在每日日报 git 仓库管辖内**的本地资产（书籍、公众号输出、技能库、蒸馏定稿、改进提案、框架、封面图、Obsidian 配置）定期推送到远程私有仓库，避免 C 盘丢失/重装时再次全丢。
> 频率：**每日由 `sync-vault.ps1` 自动同步**（计划任务 `ObsidianVault-SyncVault-13h` + `-Logon`，远程→本地 pull + 本地→远程 push，见 P-20260808-02）；本技能保留为**手动全量快照 / 周一存档兜底**，随时可按需触发。

## 一、备份范围

- **包含**：`obsidian知识库框架.md`、`欢迎.md`、`image*.png`、`01_内容系统/`（知识库/书籍、输出/公众号、系统/技能库、系统/蒸馏、系统/改进提案）、`.obsidian/` 配置（含插件 realclaudian）。
- **排除**（vault 根 `.gitignore` 已配置，`git add -A` 自动跳过）：
  - `01_内容系统/知识库/每日日报/` —— 它自带 git 仓库，由 GitHub Action 每天同步到远程 `main`，无需重复备份；
  - `.claudian/sessions/` —— Claude 会话聊天记录，非知识资产；
  - `.obsidian/workspace*.json`、`.obsidian/cache`、`.trash/` —— 本地 UI 状态与缓存；
  - `.claude/skills/` —— junction，指向技能库本体（本体已在备份范围）。

## 二、前置

- vault 根已是 git 仓库（`.git` 在 `C:\Users\user\Documents\Obsidian Vault\.git`），远程 `origin = https://github.com/VerticalFall/obsidian-vault.git`，本地分支 `main` 追踪 `origin/vault-backup`。
- git 可执行：`C:\Program Files\Git\cmd\git.exe`（或 PATH 中的 git）。

## 三、执行步骤

1. **确认备份仓库就位**：
   ```powershell
   cd "C:\Users\user\Documents\Obsidian Vault"
   git status                 # 应正常；确认是备份仓库而非每日日报仓库
   git remote -v              # origin → obsidian-vault.git
   ```
2. **暂存全部改动**（`git add -A`，排除项由 `.gitignore` 兜底）：
   ```powershell
   git add -A
   git status --short         # 快速核对：不应出现 .claudian/sessions、.obsidian/workspace、每日日报/
   ```
3. **若没有改动**：提示"全库已是最新备份"，结束。
4. **若有改动**：提交 + 推送：
   ```powershell
   git commit -m "backup: 全库快照 YYYY-MM-DD"
   git push origin main:vault-backup
   ```
5. **验证**：
   ```powershell
   git status --short                       # 应为空（干净）
   git log --oneline -1                     # 最新提交是本次备份
   git ls-remote --heads origin             # 远程存在 refs/heads/vault-backup
   ```
6. 若本周还跑了 `每日日报` 的 `pull-reports.ps1`，顺带确认其日志 OK（拉取链路正常）。

## 四、与每日自动同步的关系

- **每日自动同步**（`01_内容系统/系统/scripts/sync-vault.ps1`，计划任务 `ObsidianVault-SyncVault-13h` / `-Logon`）已覆盖全库增量：本地任意改动当天自动 push，远程（机器人收件箱）改动当天自动 pull。
- **本技能定位**：手动全量快照（大改动前、周存档、或用户明确要求"做个备份"）；周一蒸馏定稿后跑一次可留明确的周存档 commit（不跑也不影响——每日同步已覆盖）。
- 手动快照与每日同步共用同一仓库与分支，互不冲突；冲突保护（本地为权威，冲突中止不覆盖）由 `sync-vault.ps1` 承担。

## 五、红线

- **不 push 每日日报仓库**（那是 GitHub Action 的活；本地 `01_内容系统/知识库/每日日报/` 的 git 操作只 pull，不 push）。
- **不带入会话日志与缓存**：若 `git status` 出现 `.claudian/sessions/` 或 `.obsidian/workspace`，检查 `.gitignore` 后重试，不要强行 add。
- **提交信息规范**：`backup: 全库快照 YYYY-MM-DD`，便于回滚定位。
- 首次初始化已由 2026-08-07 完成（提交 `0c07320`）；此后每日增量由 `sync-vault.ps1` 自动完成，手动跑本技能只产生额外快照 commit。
