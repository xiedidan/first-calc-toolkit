# Start All Development Services
# This script will start backend, Celery and frontend in new windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Start All Development Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if in project root
if (-not (Test-Path "scripts")) {
    Write-Host "ERROR: Please run this script from project root directory" -ForegroundColor Red
    exit 1
}

# Start Docker services
Write-Host "1. Starting Docker services (PostgreSQL + Redis)..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to start
Write-Host "Waiting for database and Redis to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check Docker service status
$postgresRunning = docker ps | Select-String -Pattern "hospital_postgres_dev"
$redisRunning = docker ps | Select-String -Pattern "hospital_redis_dev"

if ($postgresRunning -and $redisRunning) {
    Write-Host "PostgreSQL and Redis started successfully" -ForegroundColor Green
} else {
    Write-Host "Docker services failed to start, please check Docker Desktop" -ForegroundColor Red
    exit 1
}

# Start backend (new window)
Write-Host ""
Write-Host "2. Starting backend service (new window)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\scripts\dev-start-backend.ps1"

# Wait for backend to start
Start-Sleep -Seconds 3

# Start Celery (new window)
Write-Host "3. Starting Celery Worker (new window)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\scripts\dev-start-celery.ps1"

# Wait for Celery to start
Start-Sleep -Seconds 2

# Start frontend (new window)
Write-Host "4. Starting frontend service (new window)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\scripts\dev-start-frontend.ps1"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "All services started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  Backend API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Backend ReDoc: http://localhost:8000/redoc" -ForegroundColor White
Write-Host ""
Write-Host "TIP: Close each PowerShell window to stop the corresponding service" -ForegroundColor Yellow
Write-Host "Or run: .\scripts\dev-stop-all.ps1 to stop all services" -ForegroundColor Yellow
Write-Host ""