# Start Frontend Service (Development Environment)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Start Frontend Service (Development)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if in project root
if (-not (Test-Path "frontend")) {
    Write-Host "ERROR: Please run this script from project root directory" -ForegroundColor Red
    exit 1
}

# Enter frontend directory
Set-Location frontend

# Check node_modules
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}

# Start development server
Write-Host ""
Write-Host "Starting Vue development server..." -ForegroundColor Green
Write-Host "Access URL: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the service" -ForegroundColor Yellow
Write-Host ""

npm run dev