#!/bin/bash
# ============================================
# Docker Image Import Script
# ============================================

set -e

echo "=========================================="
echo "  Import Docker Images"
echo "=========================================="
echo ""

# Check if Docker is running
echo ">>> Checking Docker environment..."
if ! docker version &> /dev/null; then
    echo "ERROR: Docker not running or no permission"
    echo ""
    echo "Possible solutions:"
    echo "1. Start Docker service:"
    echo "   sudo systemctl start docker"
    echo ""
    echo "2. Add current user to docker group (requires re-login):"
    echo "   sudo usermod -aG docker \$USER"
    echo ""
    echo "3. Run this script with sudo:"
    echo "   sudo bash scripts/load-images.sh"
    exit 1
fi
echo "OK: Docker running"
echo ""

IMAGES_DIR="./images"

if [ ! -d "$IMAGES_DIR" ]; then
    echo "ERROR: Images directory not found: $IMAGES_DIR"
    exit 1
fi

# Import backend image
if [ -f "$IMAGES_DIR/backend.tar.gz" ]; then
    echo ">>> Importing backend image..."
    docker load < $IMAGES_DIR/backend.tar.gz
    echo "OK: Backend image imported"
else
    echo "ERROR: Backend image file not found"
    exit 1
fi

# Import frontend image
if [ -f "$IMAGES_DIR/frontend.tar.gz" ]; then
    echo ">>> Importing frontend image..."
    docker load < $IMAGES_DIR/frontend.tar.gz
    echo "OK: Frontend image imported"
else
    echo "ERROR: Frontend image file not found"
    exit 1
fi

# Import Redis image
if [ -f "$IMAGES_DIR/redis.tar.gz" ]; then
    echo ">>> Importing Redis image..."
    docker load < $IMAGES_DIR/redis.tar.gz
    echo "OK: Redis image imported"
else
    echo "ERROR: Redis image file not found"
    exit 1
fi

echo ""
echo "=========================================="
echo "  Image Import Complete"
echo "=========================================="
echo ""
echo "Imported images:"
docker images | grep -E "hospital|redis" || echo "No related images found"
