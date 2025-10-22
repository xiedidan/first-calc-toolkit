# Setup Conda Environment
# Create and configure backend development environment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Conda Environment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if conda is installed
$condaCheck = Get-Command conda -ErrorAction SilentlyContinue
if (-not $condaCheck) {
    Write-Host "ERROR: conda command not found" -ForegroundColor Red
    Write-Host "Please make sure Anaconda is installed correctly" -ForegroundColor Yellow
    Write-Host "" 
    Write-Host "See CONDA_SETUP.md for configuration guide" -ForegroundColor Yellow
    exit 1
}

Write-Host "Conda is installed" -ForegroundColor Green

# Environment name
$envName = "hospital-backend"

# Check if environment already exists
$envExists = conda env list | Select-String -Pattern $envName

if ($envExists) {
    Write-Host ""
    Write-Host "Environment '$envName' already exists" -ForegroundColor Yellow
    $response = Read-Host "Do you want to remove and recreate it? (y/N)"
    
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host "Removing existing environment..." -ForegroundColor Yellow
        conda env remove -n $envName -y
    } else {
        Write-Host "Keeping existing environment" -ForegroundColor Green
        exit 0
    }
}

# Create new environment
Write-Host ""
Write-Host "Creating Conda environment: $envName (Python 3.12)" -ForegroundColor Yellow
conda create -n $envName python=3.12 -y

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create environment" -ForegroundColor Red
    exit 1
}

Write-Host "Environment created successfully" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow

# Check requirements.txt
if (-not (Test-Path "backend/requirements.txt")) {
    Write-Host "ERROR: backend/requirements.txt not found" -ForegroundColor Red
    exit 1
}

# Install dependencies using conda run
conda run -n $envName pip install -r backend/requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host "Dependencies installed successfully" -ForegroundColor Green

# Show environment info
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Environment setup complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Environment name: $envName" -ForegroundColor Cyan
Write-Host "Python version: 3.12" -ForegroundColor Cyan
Write-Host ""
Write-Host "To activate the environment:" -ForegroundColor Yellow
Write-Host "  conda activate $envName" -ForegroundColor White
Write-Host ""
Write-Host "To view installed packages:" -ForegroundColor Yellow
Write-Host "  conda run -n $envName pip list" -ForegroundColor White
Write-Host ""