# ============================================
# Hospital Department Value Assessment Tool - Offline Package Build Script
# Simplified version: Export entire public schema
# ============================================

param([int]$StartFrom = 1)

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Offline Package Build Tool" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
Write-Host ">>> Checking Docker..." -ForegroundColor Yellow
try {
    $null = docker version 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Docker failed" }
    Write-Host "Docker OK" -ForegroundColor Green
} catch {
    Write-Host "Docker not running" -ForegroundColor Red
    exit 1
}

$VERSION = "1.0.0"
$PACKAGE_DIR = "offline-package"
$IMAGES_DIR = "$PACKAGE_DIR\images"
$DATABASE_DIR = "$PACKAGE_DIR\database"
$CONFIG_DIR = "$PACKAGE_DIR\config"
$SCRIPTS_DIR = "$PACKAGE_DIR\scripts"

if ($StartFrom -le 1) {
    if (Test-Path $PACKAGE_DIR) { Remove-Item -Path $PACKAGE_DIR -Recurse -Force }
    New-Item -ItemType Directory -Path $IMAGES_DIR, $DATABASE_DIR, $CONFIG_DIR, $SCRIPTS_DIR -Force | Out-Null
}

# Step 1: Pull images
if ($StartFrom -le 1) {
Write-Host "Step 1/5: Pull base images" -ForegroundColor Cyan
Write-Host "Pulling python:3.12..." -ForegroundColor Yellow
docker pull python:3.12
if ($LASTEXITCODE -ne 0) { Write-Host "Warning: Failed to pull python:3.12" -ForegroundColor Yellow }

Write-Host "Pulling node:18-alpine..." -ForegroundColor Yellow
docker pull node:18-alpine
if ($LASTEXITCODE -ne 0) { Write-Host "Warning: Failed to pull node:18-alpine" -ForegroundColor Yellow }

Write-Host "Pulling nginx:alpine..." -ForegroundColor Yellow
docker pull nginx:alpine
if ($LASTEXITCODE -ne 0) { Write-Host "Warning: Failed to pull nginx:alpine" -ForegroundColor Yellow }

Write-Host "Images ready" -ForegroundColor Green
}

# Step 2: Build images
if ($StartFrom -le 2) {
Write-Host "Step 2/5: Build Docker images" -ForegroundColor Cyan

Write-Host "Building backend..." -ForegroundColor Yellow
docker build --platform linux/amd64 -t hospital-backend:latest .\backend
if ($LASTEXITCODE -ne 0) { Write-Host "Error: Backend build failed" -ForegroundColor Red; exit 1 }

Write-Host "Building frontend..." -ForegroundColor Yellow
docker build --platform linux/amd64 -t hospital-frontend:latest .\frontend
if ($LASTEXITCODE -ne 0) { Write-Host "Error: Frontend build failed" -ForegroundColor Red; exit 1 }

Write-Host "Pulling redis..." -ForegroundColor Yellow
docker pull redis:7-alpine
if ($LASTEXITCODE -ne 0) { Write-Host "Warning: Failed to pull redis" -ForegroundColor Yellow }

Write-Host "Images built" -ForegroundColor Green
}

# Step 3: Export images
if ($StartFrom -le 3) {
Write-Host "Step 3/5: Export Docker images" -ForegroundColor Cyan

Write-Host "Exporting backend..." -ForegroundColor Yellow
docker save hospital-backend:latest -o "$IMAGES_DIR\backend.tar"
Write-Host "Compressing backend..." -ForegroundColor Yellow
& 7z a "$IMAGES_DIR\backend.tar.gz" "$IMAGES_DIR\backend.tar" -mx=1 > $null
Remove-Item "$IMAGES_DIR\backend.tar" -Force

Write-Host "Exporting frontend..." -ForegroundColor Yellow
docker save hospital-frontend:latest -o "$IMAGES_DIR\frontend.tar"
Write-Host "Compressing frontend..." -ForegroundColor Yellow
& 7z a "$IMAGES_DIR\frontend.tar.gz" "$IMAGES_DIR\frontend.tar" -mx=1 > $null
Remove-Item "$IMAGES_DIR\frontend.tar" -Force

Write-Host "Exporting redis..." -ForegroundColor Yellow
docker save redis:7-alpine -o "$IMAGES_DIR\redis.tar"
Write-Host "Compressing redis..." -ForegroundColor Yellow
& 7z a "$IMAGES_DIR\redis.tar.gz" "$IMAGES_DIR\redis.tar" -mx=1 > $null
Remove-Item "$IMAGES_DIR\redis.tar" -Force

Write-Host "Images exported" -ForegroundColor Green
}


# Step 4: Export database
if ($StartFrom -le 4) {
Write-Host "Step 4/5: Export database" -ForegroundColor Cyan

if (Test-Path "backend\.env") {
    # Read DATABASE_URL (skip comments)
    $envLine = Get-Content "backend\.env" | Where-Object { $_ -notmatch '^\s*#' -and $_ -match 'DATABASE_URL=' } | Select-Object -First 1
    
    if ($envLine -match 'DATABASE_URL=postgresql://([^:]+):([^@]+)@([^:]+):([0-9]+)/(.+)') {
        $DB_USER = $matches[1]
        $DB_PASSWORD = $matches[2]
        $DB_HOST = $matches[3]
        $DB_PORT = $matches[4]
        $DB_NAME = $matches[5]
        
        if ($DB_HOST -eq "host.docker.internal") { $DB_HOST = "localhost" }
        
        Write-Host "Database: ${DB_HOST}:${DB_PORT}/${DB_NAME}" -ForegroundColor Cyan
        
        # Find pg_dump
        $pgDumpPath = $null
        $paths = @(
            "C:\Program Files\PostgreSQL\*\bin\pg_dump.exe",
            "C:\Program Files (x86)\PostgreSQL\*\bin\pg_dump.exe",
            "C:\software\PostgreSQL\*\bin\pg_dump.exe"
        )
        foreach ($pattern in $paths) {
            $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($found) {
                $pgDumpPath = $found.FullName
                break
            }
        }
        if (-not $pgDumpPath) {
            $pgDumpPath = (Get-Command pg_dump -ErrorAction SilentlyContinue).Source
        }
        
        if ($pgDumpPath) {
            $env:PGPASSWORD = $DB_PASSWORD
            
            Write-Host "Exporting public schema..." -ForegroundColor Yellow
            & $pgDumpPath `
                -h $DB_HOST `
                -p $DB_PORT `
                -U $DB_USER `
                -d $DB_NAME `
                -n public `
                -f "$DATABASE_DIR\database.sql" `
                --no-owner `
                --no-acl
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Compressing database..." -ForegroundColor Yellow
                & 7z a "$DATABASE_DIR\database.sql.gz" "$DATABASE_DIR\database.sql" -mx=9 > $null
                if ($LASTEXITCODE -eq 0) {
                    Remove-Item "$DATABASE_DIR\database.sql" -Force
                    $dbSize = [math]::Round((Get-Item "$DATABASE_DIR\database.sql.gz").Length / 1MB, 2)
                    Write-Host "Database exported ($dbSize MB)" -ForegroundColor Green
                } else {
                    Write-Host "Compression failed, keeping uncompressed" -ForegroundColor Yellow
                    $dbSize = [math]::Round((Get-Item "$DATABASE_DIR\database.sql").Length / 1MB, 2)
                    Write-Host "Database exported ($dbSize MB, uncompressed)" -ForegroundColor Green
                }
            } else {
                Write-Host "Export failed" -ForegroundColor Red
                exit 1
            }
        } else {
            Write-Host "pg_dump not found" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "Cannot parse DATABASE_URL" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "backend\.env not found" -ForegroundColor Red
    exit 1
}
}


# Step 5: Create package
if ($StartFrom -le 5) {
Write-Host "Step 5/5: Create final package" -ForegroundColor Cyan

# Copy config files
if (Test-Path "docker-compose.offline.yml") {
    Copy-Item "docker-compose.offline.yml" "$CONFIG_DIR\" -Force
}
if (Test-Path "backend\.env.offline.template") {
    Copy-Item "backend\.env.offline.template" "$CONFIG_DIR\" -Force
}

# Copy scripts
$scripts = @("deploy-offline.sh", "load-images.sh", "init-database.sh")
foreach ($script in $scripts) {
    if (Test-Path "scripts\$script") {
        Copy-Item "scripts\$script" "$SCRIPTS_DIR\" -Force
    }
}

# Create README
$readme = @"
# Hospital Value Assessment Tool - Offline Package v$VERSION

## Contents
- images/ - Docker images
- database/ - Database dump (public schema)
- config/ - Configuration files
- scripts/ - Deployment scripts

## Quick Start
1. Extract: tar -xzf package.tar.gz
2. Load images: bash scripts/load-images.sh
3. Configure: cp config/.env.offline.template .env
4. Init database: bash scripts/init-database.sh
5. Start: docker-compose -f config/docker-compose.offline.yml up -d

## Access
- Frontend: http://localhost:80
- Backend: http://localhost:8000/docs
"@
$readmePath = Join-Path (Get-Location) "$PACKAGE_DIR\README.md"
[System.IO.File]::WriteAllText($readmePath, $readme, [System.Text.UTF8Encoding]::new($false))

# Create package
$PACKAGE_NAME = "hospital-value-toolkit-offline-v$VERSION.tar.gz"
tar -czf $PACKAGE_NAME $PACKAGE_DIR

if ($LASTEXITCODE -eq 0) {
    $packageSize = [math]::Round((Get-Item $PACKAGE_NAME).Length / 1MB, 2)
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "  Build Complete!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Package: $PACKAGE_NAME" -ForegroundColor Cyan
    Write-Host "Size: $packageSize MB" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host "Package creation failed" -ForegroundColor Red
    exit 1
}
}
