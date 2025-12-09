# Hospital Value Assessment Tool - Offline Package v1.0.0

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