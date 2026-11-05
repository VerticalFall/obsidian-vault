$ErrorActionPreference = "Stop"
$base = "C:\Users\user\Documents\Obsidian Vault\大土豆开源最新文件\估值skills（持续更新）\巴菲特skills-改良版"
$xlsx = Join-Path $base "输出\A股\300750.SZ-2026-11-05\300750.SZ-估值模型-2026-11-05.xlsx"
$pdf  = Join-Path $base "输出\A股\300750.SZ-2026-11-05\300750.SZ-估值模型-2026-11-05.pdf"

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$wb = $excel.Workbooks.Open($xlsx)
$excel.CalculateFullRebuild()

$ws = $wb.Worksheets.Item("估值系统")
$addrs = @("B7","B9","B14","B17","B19","B47","B48","B49","B52","B53","B54","B60","B69","B70","B71","B72","B77","B78","B84","B85")
foreach ($a in $addrs) { Write-Output ("估值系统 " + $a + " = " + $ws.Range($a).Text) }

$ws2 = $wb.Worksheets.Item("估值与假设")
$addrs2 = @("B10","B14","G18","G19","G20","B40","B41","B42","C40","C41","C42")
foreach ($a in $addrs2) { Write-Output ("假设 " + $a + " = " + $ws2.Range($a).Text) }

$ws3 = $wb.Worksheets.Item("一图流")
$addrs3 = @("B10","B11","B12","B13","B14","B15","F10","F11","F12","F13","F14","F15")
foreach ($a in $addrs3) { Write-Output ("一图流 " + $a + " = " + $ws3.Range($a).Text) }

$errCount = 0
foreach ($s in $wb.Worksheets) {
    $lastRow = [Math]::Min($s.UsedRange.Row + $s.UsedRange.Rows.Count - 1, 70)
    $lastCol = [Math]::Min($s.UsedRange.Column + $s.UsedRange.Columns.Count - 1, 10)
    for ($i = 1; $i -le $lastRow; $i++) {
        for ($j = 1; $j -le $lastCol; $j++) {
            $t = $s.Cells.Item($i, $j).Text
            if ($t -like "#*") {
                $errCount++
                Write-Output ("ERR " + $s.Name + " " + $i + "," + $j + " " + $t)
            }
        }
    }
}
Write-Output ("ERRORS " + $errCount)

$wb.Save()
$wb.ExportAsFixedFormat(0, $pdf)
$wb.Close($true)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Output "saved"
