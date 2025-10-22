# Start Backend Service (Development Environment)
# Using Anaconda environment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Start Backend Service (Development)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if in project root
if (-not (Test-Path "backend")) {
    Write-Host "ERROR: Please run this script from project root directory" -ForegroundColor Red
    exit 1
}

# Environment name
$envName = "hospital-backend"

# Check if conda environment exists
Write-Host "Checking Conda environment: $envName" -ForegroundColor Yellow
$envExists = conda env list | Select-String -Pattern $envName

if (-not $envExists) {
    Write-Host "ERROR: Conda environment '$envName' not found" -ForegroundColor Red
    Write-Host "Please run: .\scripts\setup-conda-env.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "Conda environment found: $envName" -ForegroundColor Green

# Enter backend directory
Set-Location backend

# Check .env.dev file
if (-not (Test-Path ".env.dev")) {
    Write-Host "ERROR: .env.dev file not found" -ForegroundColor Red
    exit 1
}

# Copy environment variables
Copy-Item .env.dev .env -Force
Write-Host "Loaded development environment configuration" -ForegroundColor Green

# Check database connection
Write-Host "Checking database connection..." -ForegroundColor Yellow
$dbCheck = docker ps | Select-String -Pattern "hospital_postgres_dev"
if (-not $dbCheck) {
    Write-Host "WARNING: PostgreSQL container not running" -ForegroundColor Yellow
    Write-Host "Please start it first: docker-compose -f docker-compose.dev.yml up -d" -ForegroundColor Yellow
}

# Start FastAPI using conda run
Write-Host ""
Write-Host "Starting FastAPI service..." -ForegroundColor Green
Write-Host "Access URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the service" -ForegroundColor Yellow
Write-Host ""

conda run -n $envName --no-capture-output uvicorn app.main:app --reload --host 0.0.0.0 --port 8000