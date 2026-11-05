$ErrorActionPreference = "Stop"
$base = "C:\Users\user\Documents\Obsidian Vault\大土豆开源最新文件\估值skills（持续更新）\巴菲特skills-改良版"
$xlsx = Join-Path $base "输出\港股\1810.HK-2026-11-05\1810.HK-估值模型-2026-11-05.xlsx"
$pdf  = Join-Path $base "_work\2026-11-05\_qa_xiaomi.pdf"
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$wb = $excel.Workbooks.Open($xlsx)
$excel.CalculateFullRebuild()
$errCount = 0
foreach ($s in $wb.Worksheets) {
    $lastRow = [Math]::Min($s.UsedRange.Row + $s.UsedRange.Rows.Count - 1, 80)
    $lastCol = [Math]::Min($s.UsedRange.Column + $s.UsedRange.Columns.Count - 1, 10)
    for ($i = 1; $i -le $lastRow; $i++) {
        for ($j = 1; $j -le $lastCol; $j++) {
            $t = $s.Cells.Item($i, $j).Text
            if ($t -like "#*") { $errCount++; Write-Output ("ERR " + $s.Name + " " + $i + "," + $j + " " + $t) }
        }
    }
}
Write-Output ("ERRORS " + $errCount)
$wb.Save()
$wb.ExportAsFixedFormat(0, $pdf)
$wb.Close($true)
$excel.Quit()
Write-Output "exported"
