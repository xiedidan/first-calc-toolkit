# 测试 .env 文件解析
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  测试 .env 文件解析" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host ">>> PowerShell 方式:" -ForegroundColor Yellow
$envContent = Get-Content "backend\.env" | Where-Object { $_ -notmatch '^\s*#' -and $_ -match 'DATABASE_URL=' } | Select-Object -First 1
Write-Host "读取到的行: $envContent" -ForegroundColor Cyan

if ($envContent -match 'DATABASE_URL=postgresql://([^:]+):([^@]+)@([^:]+):([0-9]+)/(.+)') {
    Write-Host "✓ 匹配成功!" -ForegroundColor Green
    Write-Host "  DB_USER: $($matches[1])"
    Write-Host "  DB_PASSWORD: $($matches[2])"
    Write-Host "  DB_HOST: $($matches[3])"
    Write-Host "  DB_PORT: $($matches[4])"
    Write-Host "  DB_NAME: $($matches[5])"
} else {
    Write-Host "✗ 匹配失败!" -ForegroundColor Red
}

Write-Host ""
Write-Host ">>> Bash 方式 (WSL):" -ForegroundColor Yellow
$bashResult = wsl bash -c "grep -v '^\s*#' backend/.env | grep 'DATABASE_URL=' | tail -1"
Write-Host "读取到的行: $bashResult" -ForegroundColor Cyan

if ($bashResult -match 'DATABASE_URL=postgresql://([^:]+):([^@]+)@([^:]+):([0-9]+)/(.+)') {
    Write-Host "✓ 匹配成功!" -ForegroundColor Green
    Write-Host "  DB_USER: $($matches[1])"
    Write-Host "  DB_PASSWORD: $($matches[2])"
    Write-Host "  DB_HOST: $($matches[3])"
    Write-Host "  DB_PORT: $($matches[4])"
    Write-Host "  DB_NAME: $($matches[5])"
} else {
    Write-Host "✗ 匹配失败!" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  测试完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
