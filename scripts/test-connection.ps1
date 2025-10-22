# Test Database and Redis Connection
# Make sure Docker services are running

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Service Connections" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker services are running
Write-Host "Checking Docker services..." -ForegroundColor Yellow
$postgresRunning = docker ps | Select-String -Pattern "hospital_postgres_dev"
$redisRunning = docker ps | Select-String -Pattern "hospital_redis_dev"

if (-not $postgresRunning -or -not $redisRunning) {
    Write-Host "ERROR: Docker services not running" -ForegroundColor Red
    Write-Host "Please start them first: docker-compose -f docker-compose.dev.yml up -d" -ForegroundColor Yellow
    exit 1
}

Write-Host "Docker services are running" -ForegroundColor Green
Write-Host ""

# Test PostgreSQL connection
Write-Host "Testing PostgreSQL connection..." -ForegroundColor Yellow
try {
    $pgTest = docker exec hospital_postgres_dev psql -U admin -d hospital_value -c "SELECT version();" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "PostgreSQL connection successful" -ForegroundColor Green
        Write-Host "  Database: hospital_value" -ForegroundColor Gray
        Write-Host "  User: admin" -ForegroundColor Gray
        Write-Host "  Port: 5432" -ForegroundColor Gray
    } else {
        Write-Host "PostgreSQL connection failed" -ForegroundColor Red
    }
} catch {
    Write-Host "PostgreSQL connection failed" -ForegroundColor Red
}

Write-Host ""

# Test Redis connection
Write-Host "Testing Redis connection..." -ForegroundColor Yellow
try {
    $redisTest = docker exec hospital_redis_dev redis-cli ping 2>&1
    if ($redisTest -match "PONG") {
        Write-Host "Redis connection successful" -ForegroundColor Green
        Write-Host "  Port: 6379" -ForegroundColor Gray
    } else {
        Write-Host "Redis connection failed" -ForegroundColor Red
    }
} catch {
    Write-Host "Redis connection failed" -ForegroundColor Red
}

Write-Host ""

# Show connection information
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Connection Information" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "PostgreSQL:" -ForegroundColor Yellow
Write-Host "  Host: localhost" -ForegroundColor White
Write-Host "  Port: 5432" -ForegroundColor White
Write-Host "  Database: hospital_value" -ForegroundColor White
Write-Host "  Username: admin" -ForegroundColor White
Write-Host "  Password: admin123" -ForegroundColor White
Write-Host "  Connection String: postgresql://admin:admin123@localhost:5432/hospital_value" -ForegroundColor Gray
Write-Host ""
Write-Host "Redis:" -ForegroundColor Yellow
Write-Host "  Host: localhost" -ForegroundColor White
Write-Host "  Port: 6379" -ForegroundColor White
Write-Host "  Connection String: redis://localhost:6379/0" -ForegroundColor Gray
Write-Host ""

# Show Docker container status
Write-Host "Docker Container Status:" -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml ps

Write-Host ""