# Start Celery Worker (Development Environment)
# Using Anaconda environment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Start Celery Worker (Development)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if in project root
if (-not (Test-Path "backend")) {
    Write-Host "ERROR: Please run this script from project root directory" -ForegroundColor Red
    exit 1
}

# Environment name
$envName = "hospital-backend"

# Initialize Conda
$condaPath = "C:\software\anaconda3"
$condaHook = "$condaPath\shell\condabin\conda-hook.ps1"

if (Test-Path $condaHook) {
    Write-Host "Initializing Conda..." -ForegroundColor Yellow
    & $condaHook
} else {
    Write-Host "ERROR: Conda hook not found at $condaHook" -ForegroundColor Red
    exit 1
}

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

# Check Redis connection
Write-Host "Checking Redis connection..." -ForegroundColor Yellow
$redisCheck = docker ps | Select-String -Pattern "hospital_redis_dev"
if (-not $redisCheck) {
    Write-Host "WARNING: Redis container not running" -ForegroundColor Yellow
    Write-Host "Please start it first: docker-compose -f docker-compose.dev.yml up -d" -ForegroundColor Yellow
}

# Start Celery Worker using conda run
Write-Host ""
Write-Host "Starting Celery Worker..." -ForegroundColor Green
Write-Host "NOTE: Using --pool=solo for Windows compatibility" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the service" -ForegroundColor Yellow
Write-Host ""

conda run -n $envName --no-capture-output celery -A app.celery_app worker --loglevel=info --pool=solo