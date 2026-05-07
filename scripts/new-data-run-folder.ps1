#Requires -Version 5.1
# 在 data/ 下按「今天」创建 YYYY-MM-DD 目录（工作流必选步骤之一）。
# 指标 Excel：同日多次追加 Sheet 请用 cn-fund persist-run --date <同日> --json ...
$Root = Split-Path -Parent $PSScriptRoot
$date = Get-Date -Format "yyyy-MM-dd"
$dir = Join-Path $Root "data\$date"
New-Item -ItemType Directory -Force -Path $dir | Out-Null
Write-Host "Ready: $dir"
Write-Host "Copy or write 01_*.md ... meta.json per workflows/how-to-invoke-real-agents.md"
