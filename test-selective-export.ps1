# Test selective export configuration
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Test Selective Data Export" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 从配置文件读取排除列表
$excludeFile = ".offline-package-exclude-tables.txt"

if (-not (Test-Path $excludeFile)) {
    Write-Host "Error: Exclude file not found: $excludeFile" -ForegroundColor Red
    exit 1
}

# 读取并过滤排除列表（忽略空行和注释）
$tablesSchemaOnly = Get-Content $excludeFile | 
    Where-Object { $_ -notmatch '^\s*#' -and $_ -notmatch '^\s*$' } |
    ForEach-Object { $_.Trim() }

Write-Host "Export Strategy:" -ForegroundColor Cyan
Write-Host "  Exclude file: $excludeFile" -ForegroundColor Cyan
Write-Host "  Excluded tables (schema only): $($tablesSchemaOnly.Count)" -ForegroundColor Yellow
Write-Host "  All other tables (with data): Auto-included" -ForegroundColor Green
Write-Host ""

Write-Host "Excluded tables (schema only):" -ForegroundColor Yellow
$tablesSchemaOnly | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }

Write-Host ""
Write-Host "All other tables will export data automatically" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Configuration OK" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
