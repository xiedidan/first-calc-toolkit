#!/bin/bash
# ============================================
# Database Initialization Script
# ============================================
# Version 1.0

set -e

# ============================================
# Configuration Options
# ============================================
# If local pg_restore not available, specify a Docker container with PostgreSQL client tools
# Leave empty for auto-detection
PG_DOCKER_CONTAINER="${PG_DOCKER_CONTAINER:-}"

# Or specify PostgreSQL Docker image (if available locally)
# Leave empty to use postgres:16 (if exists)
PG_DOCKER_IMAGE="${PG_DOCKER_IMAGE:-postgres:16}"

echo "=========================================="
echo "  Initialize Database"
echo "=========================================="
echo ""

# Check .env file
if [ ! -f ".env" ]; then
    echo "ERROR: .env config file not found"
    echo "Please copy config/.env.offline.template to .env and configure"
    exit 1
fi

# Read configuration
source .env

# Validate required environment variables
echo ">>> Validating environment variables..."
MISSING_VARS=()

if [ -z "$DATABASE_URL" ]; then
    MISSING_VARS+=("DATABASE_URL")
fi

if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-secret-key-change-this-in-production" ]; then
    MISSING_VARS+=("SECRET_KEY (need to generate random key)")
fi

if [ -z "$ENCRYPTION_KEY" ] || [ "$ENCRYPTION_KEY" = "your-encryption-key-change-this-in-production" ]; then
    MISSING_VARS+=("ENCRYPTION_KEY (need to generate Fernet key)")
fi

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "ERROR: The following environment variables are not configured:"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    echo ""
    echo "Please edit .env file and set these variables:"
    echo "  SECRET_KEY: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
    echo "  ENCRYPTION_KEY: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
    exit 1
fi

echo "OK: Environment variables validated"
echo ""

# Extract database connection info
if [[ $DATABASE_URL =~ postgresql://([^:]+):([^@]+)@([^:]+):([0-9]+)/(.+) ]]; then
    DB_USER="${BASH_REMATCH[1]}"
    DB_PASSWORD="${BASH_REMATCH[2]}"
    DB_HOST="${BASH_REMATCH[3]}"
    DB_PORT="${BASH_REMATCH[4]}"
    DB_NAME="${BASH_REMATCH[5]}"
else
    echo "ERROR: Cannot parse DATABASE_URL"
    exit 1
fi

# Handle host.docker.internal
if [ "$DB_HOST" = "host.docker.internal" ]; then
    DB_HOST="localhost"
fi

echo "Database host: $DB_HOST"
echo "Database port: $DB_PORT"
echo "Database name: $DB_NAME"

# Ask whether to clean entire database
echo ""
echo "=========================================="
echo "  Database Initialization Options"
echo "=========================================="
echo ""
echo "Please select initialization method:"
echo "  1. Clean entire database and rebuild (recommended, cleanest)"
echo "  2. Keep existing data, only update table structure"
echo ""
read -p "Enter option (1/2, default 1): " INIT_OPTION
INIT_OPTION=${INIT_OPTION:-1}

if [ "$INIT_OPTION" = "1" ]; then
    echo ""
    echo "WARNING: This will delete all tables and data in the database!"
    echo "Database: $DB_NAME"
    echo ""
    read -p "Confirm clean entire database? (yes/no): " CONFIRM
    
    if [[ "$CONFIRM" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo ""
        echo ">>> Cleaning entire database (using PostgreSQL container)..."
        
        # Use configured PostgreSQL container, auto-detect if not configured
        if [ -z "$PG_DOCKER_CONTAINER" ]; then
            PG_CONTAINER=$(docker ps --format '{{.Names}}' | grep -i postgres | head -1)
            if [ -z "$PG_CONTAINER" ]; then
                echo "ERROR: PostgreSQL container not found"
                echo "  Please set PG_DOCKER_CONTAINER in .env"
                exit 1
            fi
            echo "  Auto-detected container: $PG_CONTAINER"
        else
            PG_CONTAINER="$PG_DOCKER_CONTAINER"
            echo "  Using configured container: $PG_CONTAINER"
        fi
        
        # Use psql in PostgreSQL container to clean database
        # Simple approach: drop and recreate public schema
        docker exec -e PGPASSWORD=$DB_PASSWORD $PG_CONTAINER \
            psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
        
        if [ $? -eq 0 ]; then
            echo "OK: Database cleaned"
        else
            echo "ERROR: Database cleanup failed"
            exit 1
        fi
    else
        echo "Cancelled, exiting"
        exit 0
    fi
else
    echo ""
    echo ">>> Cleaning old migration version records (using PostgreSQL container)..."
    
    # Use configured PostgreSQL container, auto-detect if not configured
    if [ -z "$PG_DOCKER_CONTAINER" ]; then
        PG_CONTAINER=$(docker ps --format '{{.Names}}' | grep -i postgres | head -1)
        if [ -z "$PG_CONTAINER" ]; then
            echo "ERROR: PostgreSQL container not found"
            echo "  Please set PG_DOCKER_CONTAINER in .env"
            exit 1
        fi
        echo "  Auto-detected container: $PG_CONTAINER"
    else
        PG_CONTAINER="$PG_DOCKER_CONTAINER"
        echo "  Using configured container: $PG_CONTAINER"
    fi
    
    docker exec -e PGPASSWORD=$DB_PASSWORD $PG_CONTAINER \
        psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
        -c "DELETE FROM alembic_version;" 2>/dev/null || echo "  OK: Table does not exist or already empty"
fi

# Restore database
echo ""
echo ">>> Restoring database..."

# Check if SQL file exists
if [ -f "database/database.sql.gz" ] || [ -f "database/database.sql" ]; then
    echo ">>> Using psql to restore full database..."
    echo "WARNING: This will restore complete database structure and data"
    echo ""
    
    # Decompress SQL file (if compressed)
    if [ -f "database/database.sql.gz" ]; then
        echo ">>> Decompressing SQL file..."
        gunzip -c database/database.sql.gz > database/database.sql
        CLEANUP_SQL=true
    else
        CLEANUP_SQL=false
    fi
    
    # Use psql to restore SQL file
    if command -v psql &> /dev/null; then
        PSQL_VERSION=$(psql --version | grep -oP '\d+\.\d+' | head -1)
        echo ">>> Using local psql (version $PSQL_VERSION)..."
        
        # Use --set ON_ERROR_STOP=0 to continue even if errors occur (e.g., version differences)
        PGPASSWORD=$DB_PASSWORD psql \
            -h $DB_HOST \
            -p $DB_PORT \
            -U $DB_USER \
            -d $DB_NAME \
            -f database/database.sql \
            --quiet \
            --set ON_ERROR_STOP=0 \
            2>&1 | grep -v "unrecognized configuration parameter" || true
        
        echo "OK: Database restore complete"
        USE_DOCKER=false
    fi
    
    # If local tools not available, use Docker
    if [ ! -v USE_DOCKER ] || [ "$USE_DOCKER" = true ]; then
        if [ ! -v USE_DOCKER ]; then
            echo "WARNING: Local psql not installed"
        fi
        echo "  Trying PostgreSQL client in Docker container..."
        
        # Check for available PostgreSQL container
        PG_CONTAINER=""
        
        # Method 1: Use configured container
        if [ -n "$PG_DOCKER_CONTAINER" ]; then
            if docker ps --format '{{.Names}}' | grep -q "^${PG_DOCKER_CONTAINER}$"; then
                PG_CONTAINER="$PG_DOCKER_CONTAINER"
                echo "  Using configured container: $PG_CONTAINER"
            else
                echo "  WARNING: Configured container $PG_DOCKER_CONTAINER not running"
            fi
        fi
        
        # Method 2: Auto-detect running PostgreSQL container
        if [ -z "$PG_CONTAINER" ]; then
            if docker ps --format '{{.Names}}' | grep -q postgres; then
                PG_CONTAINER=$(docker ps --format '{{.Names}}' | grep postgres | head -1)
                echo "  Auto-detected PostgreSQL container: $PG_CONTAINER"
            fi
        fi
        
        # If container found, use psql in container
        if [ -n "$PG_CONTAINER" ]; then
            echo "  Using psql in container $PG_CONTAINER"
            
            # Copy SQL file to container
            docker cp database/database.sql $PG_CONTAINER:/tmp/database.sql
            
            # Execute psql in container
            docker exec -e PGPASSWORD=$DB_PASSWORD $PG_CONTAINER \
                psql \
                    -h $DB_HOST \
                    -p $DB_PORT \
                    -U $DB_USER \
                    -d $DB_NAME \
                    -f /tmp/database.sql \
                    --quiet \
                    --set ON_ERROR_STOP=0
            
            if [ $? -eq 0 ]; then
                echo "OK: Database restore complete"
            else
                echo "WARNING: Warnings during restore (usually can be ignored)"
            fi
            
            # Clean up temp file
            docker exec $PG_CONTAINER rm -f /tmp/database.sql
        else
            # Method 3: Use local PostgreSQL image (no pull)
            if docker image inspect $PG_DOCKER_IMAGE &> /dev/null; then
                echo "  Using local image: $PG_DOCKER_IMAGE"
                docker run --rm \
                    --network host \
                    -v "$(pwd)/database:/backup" \
                    -e PGPASSWORD=$DB_PASSWORD \
                    $PG_DOCKER_IMAGE \
                    psql \
                        -h $DB_HOST \
                        -p $DB_PORT \
                        -U $DB_USER \
                        -d $DB_NAME \
                        -f /backup/database.sql \
                        --quiet \
                        --set ON_ERROR_STOP=0
                
                if [ $? -eq 0 ]; then
                    echo "OK: Database restore complete"
                else
                    echo "WARNING: Warnings during restore (usually can be ignored)"
                fi
            else
                echo "ERROR: PostgreSQL container or image not found"
                echo ""
                echo "Solutions:"
                echo "  1. Install PostgreSQL client tools"
                echo "  2. Or specify Docker container with psql:"
                echo "     export PG_DOCKER_CONTAINER=<container_name>"
                echo "     bash scripts/init-database.sh"
                echo ""
                echo "  3. Or manually restore database:"
                echo "     PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f database/database.sql"
                echo ""
                exit 1
            fi
        fi
    fi
    
    # Clean up temp SQL file
    if [ "$CLEANUP_SQL" = true ]; then
        rm -f database/database.sql
    fi
    
    echo ""
    echo ">>> Validating database (using PostgreSQL container)..."
    
    # Use configured PostgreSQL container
    if [ -z "$PG_DOCKER_CONTAINER" ]; then
        PG_CONTAINER=$(docker ps --format '{{.Names}}' | grep -i postgres | head -1)
    else
        PG_CONTAINER="$PG_DOCKER_CONTAINER"
    fi
    
    if [ -n "$PG_CONTAINER" ]; then
        TABLE_COUNT=$(docker exec -e PGPASSWORD=$DB_PASSWORD $PG_CONTAINER \
            psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t \
            -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
        
        if [ -n "$TABLE_COUNT" ] && [ "$TABLE_COUNT" -gt "0" ]; then
            echo "OK: Database validation passed"
            echo "  Table count: $TABLE_COUNT"
        else
            echo "WARNING: Database may not be restored correctly"
        fi
    else
        echo "WARNING: PostgreSQL container not found, skipping validation"
    fi
else
    echo "WARNING: Database dump file not found (database/database.dump)"
    echo "  Will use Alembic migration to create table structure..."
    echo ""
    
    # Check if container is running
    if ! docker ps | grep -q hospital_backend_offline; then
        echo "WARNING: Backend container not running, trying to start..."
        docker-compose -f config/docker-compose.offline.yml up -d backend
        echo "Waiting for container to start..."
        sleep 5
    fi
    
    # Use Alembic to create table structure
    echo ">>> Running database migration..."
    docker exec hospital_backend_offline alembic upgrade head
    
    if [ $? -eq 0 ]; then
        echo "OK: Database table structure created"
    else
        echo "WARNING: Migration failed, trying with heads parameter..."
        docker exec hospital_backend_offline alembic upgrade heads
    fi
    
    # Initialize admin user
    echo ""
    echo ">>> Initializing admin user..."
    docker exec hospital_backend_offline python scripts/init_admin.py
    if [ $? -eq 0 ]; then
        echo "OK: Admin user initialized"
    else
        echo "WARNING: Admin user initialization failed (may already exist)"
    fi
fi

echo ""
echo "=========================================="
echo "  Database Initialization Complete"
echo "=========================================="
