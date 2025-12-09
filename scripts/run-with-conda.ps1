# Run command with conda environment
# Usage: .\scripts\run-with-conda.ps1 "python script.py"

param(
    [Parameter(Mandatory=$true)]
    [string]$Command
)

$condaPath = "C:\software\anaconda3"
$condaHook = "$condaPath\shell\condabin\conda-hook.ps1"
$envName = "hospital-backend"

if (-not (Test-Path $condaHook)) {
    Write-Host "ERROR: Conda not found at $condaPath" -ForegroundColor Red
    exit 1
}

# Initialize conda
& $condaHook

# Check if environment exists
$envExists = conda env list | Select-String -Pattern $envName
if (-not $envExists) {
    Write-Host "ERROR: Environment '$envName' not found" -ForegroundColor Red
    Write-Host "Please run setup-conda-env.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Run command in environment
Write-Host "Running in environment: $envName" -ForegroundColor Cyan
Write-Host "Command: $Command" -ForegroundColor Yellow
Write-Host ""

conda run -n $envName --no-capture-output $Command
