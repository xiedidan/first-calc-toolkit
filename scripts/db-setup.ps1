# Complete Database Setup
# Initialize database and seed with initial data

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Complete Database Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker services are running
Write-Host "Checking Docker services..." -ForegroundColor Yellow
$postgresRunning = docker ps | Select-String -Pattern "hospital_postgres_dev"

if (-not $postgresRunning) {
    Write-Host "ERROR: PostgreSQL container not running" -ForegroundColor Red
    Write-Host "Please start it first: docker-compose -f docker-compose.dev.yml up -d" -ForegroundColor Yellow
    exit 1
}

Write-Host "PostgreSQL is running" -ForegroundColor Green
Write-Host ""

# Save current directory
$originalDir = Get-Location

# Step 1: Initialize database (create tables)
Write-Host "Step 1: Initialize database..." -ForegroundColor Cyan
& "$PSScriptRoot\db-init.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Database initialization failed" -ForegroundColor Red
    Set-Location $originalDir
    exit 1
}

# Make sure we're back in project root
Set-Location $originalDir

# Step 2: Seed database (insert initial data)
Write-Host ""
Write-Host "Step 2: Seed database..." -ForegroundColor Cyan
& "$PSScriptRoot\db-seed.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Database seeding failed" -ForegroundColor Red
    Set-Location $originalDir
    exit 1
}

# Return to original directory
Set-Location $originalDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Database setup complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Default admin credentials:" -ForegroundColor Cyan
Write-Host "  Username: admin" -ForegroundColor White
Write-Host "  Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "Please change the password after first login!" -ForegroundColor Yellow
Write-Host ""
