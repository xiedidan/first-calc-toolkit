# Environment Check Script
# Check if all required tools are installed

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Environment Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check WSL2
Write-Host "Checking WSL2..." -NoNewline
try {
    $wslVersion = wsl --list --verbose 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " FAILED" -ForegroundColor Red
        Write-Host "  WSL2 not installed or not configured" -ForegroundColor Yellow
        $allGood = $false
    }
} catch {
    Write-Host " FAILED" -ForegroundColor Red
    Write-Host "  WSL2 not installed" -ForegroundColor Yellow
    $allGood = $false
}

# Check Docker
Write-Host "Checking Docker..." -NoNewline
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
        Write-Host "  Version: $dockerVersion" -ForegroundColor Gray
    } else {
        Write-Host " FAILED" -ForegroundColor Red
        Write-Host "  Docker not installed or not running" -ForegroundColor Yellow
        $allGood = $false
    }
} catch {
    Write-Host " FAILED" -ForegroundColor Red
    Write-Host "  Docker not installed" -ForegroundColor Yellow
    $allGood = $false
}

# Check Docker Compose
Write-Host "Checking Docker Compose..." -NoNewline
try {
    $composeVersion = docker-compose --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
        Write-Host "  Version: $composeVersion" -ForegroundColor Gray
    } else {
        Write-Host " FAILED" -ForegroundColor Red
        Write-Host "  Docker Compose not installed" -ForegroundColor Yellow
        $allGood = $false
    }
} catch {
    Write-Host " FAILED" -ForegroundColor Red
    Write-Host "  Docker Compose not installed" -ForegroundColor Yellow
    $allGood = $false
}

# Check Conda
Write-Host "Checking Conda..." -NoNewline
try {
    $condaVersion = conda --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
        Write-Host "  Version: $condaVersion" -ForegroundColor Gray
    } else {
        Write-Host " FAILED" -ForegroundColor Red
        Write-Host "  Conda not installed or not configured" -ForegroundColor Yellow
        $allGood = $false
    }
} catch {
    Write-Host " FAILED" -ForegroundColor Red
    Write-Host "  Conda not installed" -ForegroundColor Yellow
    $allGood = $false
}

# Check Node.js
Write-Host "Checking Node.js..." -NoNewline
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
        Write-Host "  Version: $nodeVersion" -ForegroundColor Gray
    } else {
        Write-Host " FAILED" -ForegroundColor Red
        Write-Host "  Node.js not installed" -ForegroundColor Yellow
        $allGood = $false
    }
} catch {
    Write-Host " FAILED" -ForegroundColor Red
    Write-Host "  Node.js not installed" -ForegroundColor Yellow
    $allGood = $false
}

# Check npm
Write-Host "Checking npm..." -NoNewline
try {
    $npmVersion = npm --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
        Write-Host "  Version: $npmVersion" -ForegroundColor Gray
    } else {
        Write-Host " FAILED" -ForegroundColor Red
        Write-Host "  npm not installed" -ForegroundColor Yellow
        $allGood = $false
    }
} catch {
    Write-Host " FAILED" -ForegroundColor Red
    Write-Host "  npm not installed" -ForegroundColor Yellow
    $allGood = $false
}

# Check port availability
Write-Host ""
Write-Host "Checking port availability..." -ForegroundColor Cyan

$ports = @(5432, 6379, 8000, 3000)
$portsOk = $true

foreach ($port in $ports) {
    $portCheck = netstat -ano | Select-String ":$port " | Select-Object -First 1
    if ($portCheck) {
        Write-Host "  Port $port is in use" -ForegroundColor Yellow
        $portsOk = $false
    } else {
        Write-Host "  Port $port is available" -ForegroundColor Green
    }
}

# Check project files
Write-Host ""
Write-Host "Checking project files..." -ForegroundColor Cyan

$requiredFiles = @(
    "docker-compose.dev.yml",
    "docker-compose.prod.yml",
    "backend/requirements.txt",
    "backend/.env.dev",
    "backend/.env.prod",
    "frontend/package.json",
    "scripts/dev-start-all.ps1"
)

$filesOk = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  $file OK" -ForegroundColor Green
    } else {
        Write-Host "  $file MISSING" -ForegroundColor Red
        $filesOk = $false
    }
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

if ($allGood -and $filesOk) {
    Write-Host "Environment check PASSED!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    if (-not $portsOk) {
        Write-Host "WARNING: Some ports are in use. Please free them before starting services." -ForegroundColor Yellow
        Write-Host ""
    }
    
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Setup Conda environment: .\scripts\setup-conda-env.ps1" -ForegroundColor White
    Write-Host "  2. Install frontend dependencies: cd frontend; npm install" -ForegroundColor White
    Write-Host "  3. Start development services: .\scripts\dev-start-all.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Or see QUICKSTART.md for detailed instructions" -ForegroundColor White
} else {
    Write-Host "Environment check FAILED!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install missing tools and run this script again" -ForegroundColor Yellow
    Write-Host "See deployment documentation for installation guide" -ForegroundColor Yellow
}

Write-Host ""