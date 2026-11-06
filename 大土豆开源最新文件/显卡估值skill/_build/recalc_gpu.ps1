$ErrorActionPreference = "Stop"
$base = "C:\Users\user\Documents\Obsidian Vault\大土豆开源最新文件\显卡估值skill"
$xlsx = Join-Path $base "输出\显卡估值表-2026-11-05.xlsx"
$pdf  = Join-Path $base "输出\_qa_gpu.pdf"
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$wb = $excel.Workbooks.Open($xlsx)
$excel.CalculateFullRebuild()
$ws = $wb.Worksheets.Item("估值表")
foreach ($r in 5..10) {
  Write-Output ($ws.Range("A$r").Text + " | 公允 " + $ws.Range("H$r").Text + " | 可买 " + $ws.Range("I$r").Text + " | 上限 " + $ws.Range("J$r").Text + " | 溢价 " + $ws.Range("K$r").Text)
}
$errCount = 0
foreach ($s in $wb.Worksheets) {
  $lastRow = [Math]::Min($s.UsedRange.Row + $s.UsedRange.Rows.Count - 1, 40)
  $lastCol = [Math]::Min($s.UsedRange.Column + $s.UsedRange.Columns.Count - 1, 14)
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
Write-Output "done"
