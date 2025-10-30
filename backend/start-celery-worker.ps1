# Celery Worker 启动脚本
# 用于开发环境

Write-Host "正在启动 Celery Worker..." -ForegroundColor Green
Write-Host "环境: 开发环境" -ForegroundColor Yellow
Write-Host "日志级别: INFO" -ForegroundColor Yellow
Write-Host ""

# 启动 Celery Worker
celery -A app.celery_app worker --loglevel=info --pool=solo

# 如果出错，暂停以便查看错误信息
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Celery Worker 启动失败！" -ForegroundColor Red
    Write-Host "请检查:" -ForegroundColor Yellow
    Write-Host "1. Redis 是否正在运行" -ForegroundColor Yellow
    Write-Host "2. 数据库连接是否正常" -ForegroundColor Yellow
    Write-Host "3. 环境变量是否正确配置" -ForegroundColor Yellow
    pause
}
