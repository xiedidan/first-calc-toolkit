#!/bin/bash
# ============================================
# Prerequisites Check Script
# ============================================

echo "=========================================="
echo "  Check Deployment Prerequisites"
echo "=========================================="
echo ""

# Check Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo "OK: Docker installed: $DOCKER_VERSION"
else
    echo "ERROR: Docker not installed, please install Docker first"
    exit 1
fi

# Check if Docker is running
if docker info &> /dev/null; then
    echo "OK: Docker service running"
else
    echo "ERROR: Docker service not running, please start Docker"
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo "OK: Docker Compose installed: $COMPOSE_VERSION"
elif docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version)
    echo "OK: Docker Compose installed: $COMPOSE_VERSION"
else
    echo "ERROR: Docker Compose not installed, please install first"
    exit 1
fi

# Check disk space
AVAILABLE_SPACE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ $AVAILABLE_SPACE -gt 10 ]; then
    echo "OK: Disk space sufficient: ${AVAILABLE_SPACE}GB"
else
    echo "WARNING: Disk space low, recommend at least 10GB, current: ${AVAILABLE_SPACE}GB"
fi

# Check port availability
echo ""
echo "Checking port availability:"
PORTS=(80 8000 6379)
for PORT in "${PORTS[@]}"; do
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":$PORT "; then
        echo "WARNING: Port $PORT is in use"
    else
        echo "OK: Port $PORT available"
    fi
done

echo ""
echo "=========================================="
echo "  Prerequisites Check Complete"
echo "=========================================="
