# Seed Database with Initial Data
# Create default roles, permissions, and admin user

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Seed Database with Initial Data" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if in project root
if (-not (Test-Path "backend")) {
    Write-Host "ERROR: Please run this script from project root directory" -ForegroundColor Red
    exit 1
}

# Save current directory
$originalDir = Get-Location

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

Write-Host ""
Write-Host "Running initialization script..." -ForegroundColor Yellow
Write-Host ""

conda run -n $envName --no-capture-output python backend/scripts/init_data.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Failed to seed database" -ForegroundColor Red
    Set-Location $originalDir
    exit 1
}

# Return to original directory
Set-Location $originalDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Database seeded successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
