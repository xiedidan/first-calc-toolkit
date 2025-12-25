#!/bin/bash
# ============================================
# One-click Deployment Script
# ============================================

set -e

echo "=========================================="
echo "  Hospital Value Assessment Tool"
echo "  Offline Deployment"
echo "=========================================="
echo ""

# Step 1: Check prerequisites
echo "Step 1/6: Check prerequisites"
echo "=========================================="
bash scripts/check-prerequisites.sh
echo ""

# Step 2: Import Docker images
echo "Step 2/6: Import Docker images"
echo "=========================================="
bash scripts/load-images.sh
echo ""

# Step 3: Configure environment
echo "Step 3/6: Configure environment"
echo "=========================================="
if [ ! -f ".env" ]; then
    echo ">>> Creating config file..."
    cp config/.env.offline.template .env
    echo "OK: Config file created: .env"
    echo ""
    echo "WARNING: Please edit .env file and configure:"
    echo "  1. Database connection (DATABASE_URL)"
    echo "  2. JWT secret key (SECRET_KEY)"
    echo "  3. Encryption key (ENCRYPTION_KEY)"
    echo ""
    echo "Key generation methods:"
    echo "  SECRET_KEY: python3 -c \"import secrets; print(secrets.token_urlsafe(32))\""
    echo "  ENCRYPTION_KEY: python3 -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
    echo ""
    echo "After configuration, run this script again"
    exit 0
else
    echo "OK: Config file exists"
fi
echo ""

# Step 4: Start services
echo "Step 4/6: Start services"
echo "=========================================="
echo ">>> Starting Docker containers..."
docker-compose -f config/docker-compose.offline.yml up -d
echo "OK: Services started"
echo ""

# Step 5: Wait for services ready
echo "Step 5/6: Wait for services ready"
echo "=========================================="
echo ">>> Waiting for containers to start..."
sleep 10

echo ">>> Checking container status..."
docker-compose -f config/docker-compose.offline.yml ps
echo ""

# Step 6: Initialize database
echo "Step 6/6: Initialize database"
echo "=========================================="
bash scripts/init-database.sh
echo ""

# Verify deployment
echo "=========================================="
echo "  Deployment Complete!"
echo "=========================================="
echo ""
echo "Service URLs:"
echo "  Frontend: http://localhost:${FRONTEND_PORT:-80}"
echo "  Backend API: http://localhost:${BACKEND_PORT:-8000}/docs"
echo ""
echo "Common commands:"
echo "  Check status: docker-compose -f config/docker-compose.offline.yml ps"
echo "  View logs: docker-compose -f config/docker-compose.offline.yml logs -f"
echo "  Stop services: docker-compose -f config/docker-compose.offline.yml stop"
echo "  Start services: docker-compose -f config/docker-compose.offline.yml start"
echo "  Restart services: docker-compose -f config/docker-compose.offline.yml restart"
echo ""
