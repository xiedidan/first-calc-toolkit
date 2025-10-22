# Simple Database Setup
# Directly creates tables and inserts data without using Alembic

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Simple Database Setup" -ForegroundColor Cyan
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

# Check if in project root
if (-not (Test-Path "backend")) {
    Write-Host "ERROR: Please run this script from project root directory" -ForegroundColor Red
    exit 1
}

# Environment name
$envName = "hospital-backend"

Write-Host "Running database initialization..." -ForegroundColor Yellow
Write-Host ""

# Try to use conda run, if fails, show instructions
try {
    conda run -n $envName --no-capture-output python backend/scripts/init_data.py
    
    if ($LASTEXITCODE -eq 0) {
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
    } else {
        Write-Host ""
        Write-Host "ERROR: Database initialization failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "ERROR: Could not run conda command" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run this script in Anaconda PowerShell Prompt:" -ForegroundColor Yellow
    Write-Host "  1. Open 'Anaconda PowerShell Prompt' from Start Menu" -ForegroundColor White
    Write-Host "  2. cd C:\project\first-calc-toolkit" -ForegroundColor White
    Write-Host "  3. .\scripts\db-setup-simple.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Or use the batch file: double-click 'open-anaconda-prompt.bat'" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
