# sync-vault.ps1 — vault 备份仓库每日双向同步（远程→本地 pull，本地→远程 push）
# 由 Windows 计划任务调用：登录时 + 每天 13:00（与每日日报 pull-reports 同一节奏，见 P-20260808-02）
#
# 冲突保护（绝不自动覆盖数据）：
#   pull 一律 --ff-only；被本地未提交改动挡住 → stash 后重试；
#   stash pop 仍冲突 → 中止并写 FATAL 日志（stash 保留，数据未丢），人工处理后下次自动恢复。
$ErrorActionPreference = 'Continue'
$git  = 'C:\Program Files\Git\cmd\git.exe'
$repo = 'C:\Users\user\Documents\Obsidian Vault'
$log  = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) 'sync-vault.log'
$stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'

Add-Content -Path $log -Value "[$stamp] === sync start ===" -Encoding UTF8
if (-not (Test-Path $git))  { Add-Content -Path $log -Value "[$stamp] ERROR: git not found: $git" -Encoding UTF8; exit 1 }
if (-not (Test-Path $repo)) { Add-Content -Path $log -Value "[$stamp] ERROR: repo not found: $repo" -Encoding UTF8; exit 1 }

# ── 1. 远程 → 本地：ff-only pull ──
& $git -C $repo pull --ff-only origin vault-backup *>> $log
if ($LASTEXITCODE -ne 0) {
    # 本地有未提交改动挡住了 ff-only → stash 后重试
    Add-Content -Path $log -Value "[$stamp] pull blocked, stash-and-retry..." -Encoding UTF8
    & $git -C $repo stash push -u -m "sync-auto-$(Get-Date -Format 'yyyyMMdd-HHmmss')" *>> $log
    & $git -C $repo pull --ff-only origin vault-backup *>> $log
    $exit2 = $LASTEXITCODE
    & $git -C $repo stash pop *>> $log
    $exit3 = $LASTEXITCODE
    if ($exit2 -ne 0 -or $exit3 -ne 0) {
        Add-Content -Path $log -Value "[$stamp] FATAL: 同步中止——远程改动与本地改动冲突，数据已保留（stash 未丢），需人工处理" -Encoding UTF8
        exit 2
    }
    Add-Content -Path $log -Value "[$stamp] stash-retry OK (pull=$exit2 pop=$exit3)" -Encoding UTF8
}

# ── 2. 本地 → 远程：add/commit/push（无改动则跳过）──
& $git -C $repo add -A *>> $log
& $git -C $repo diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Add-Content -Path $log -Value "[$stamp] 本地无改动，跳过 push" -Encoding UTF8
} else {
    & $git -C $repo commit -m "backup: 每日同步 $(Get-Date -Format 'yyyy-MM-dd')" *>> $log
    & $git -C $repo push origin main:vault-backup *>> $log
    if ($LASTEXITCODE -ne 0) {
        Add-Content -Path $log -Value "[$stamp] FATAL: push 失败（网络/凭证），本地数据未丢失，下次运行自动重试" -Encoding UTF8
        exit 3
    }
}
Add-Content -Path $log -Value "[$stamp] === sync done ===" -Encoding UTF8
exit 0
