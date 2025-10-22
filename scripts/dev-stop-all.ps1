# Stop All Development Services

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Stop All Development Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Stop Docker services
Write-Host "Stopping Docker services..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml down

# Stop Python processes (uvicorn and celery)
Write-Host "Stopping backend and Celery processes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*uvicorn*" -or $_.ProcessName -like "*celery*"} | Stop-Process -Force -ErrorAction SilentlyContinue

# Stop Node processes
Write-Host "Stopping frontend processes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*node*"} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "All services stopped!" -ForegroundColor Green
Write-Host ""