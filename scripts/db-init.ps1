# Initialize Database
# Create initial migration and apply it

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Initialize Database" -ForegroundColor Cyan
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

# Save current directory
$originalDir = Get-Location

# Enter backend directory
Set-Location backend

Write-Host ""
Write-Host "Creating initial migration..." -ForegroundColor Yellow
conda run -n $envName --no-capture-output alembic revision --autogenerate -m "Initial migration: users, roles, permissions"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create migration" -ForegroundColor Red
    Set-Location $originalDir
    exit 1
}

Write-Host ""
Write-Host "Applying migration..." -ForegroundColor Yellow
conda run -n $envName --no-capture-output alembic upgrade head

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to apply migration" -ForegroundColor Red
    Set-Location $originalDir
    exit 1
}

# Return to original directory
Set-Location $originalDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Database initialized successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
