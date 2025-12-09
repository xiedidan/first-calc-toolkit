#!/bin/bash
# ============================================
# 数据库初始化脚本
# ============================================
# Version 1.0

set -e

# ============================================
# 配置选项
# ============================================
# 如果本地没有 pg_restore，可以指定一个包含 PostgreSQL 客户端工具的 Docker 容器
# 留空则自动检测
PG_DOCKER_CONTAINER="${PG_DOCKER_CONTAINER:-}"

# 或者指定 PostgreSQL Docker 镜像（如果本地已有）
# 留空则使用 postgres:16（如果存在）
PG_DOCKER_IMAGE="${PG_DOCKER_IMAGE:-postgres:16}"

echo "=========================================="
echo "  初始化数据库"
echo "=========================================="
echo ""

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "✗ 未找到.env配置文件"
    echo "请先复制config/.env.offline.template为.env并配置"
    exit 1
fi

# 读取配置
source .env

# 验证必需的环境变量
echo ">>> 验证环境变量..."
MISSING_VARS=()

if [ -z "$DATABASE_URL" ]; then
    MISSING_VARS+=("DATABASE_URL")
fi

if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-secret-key-change-this-in-production" ]; then
    MISSING_VARS+=("SECRET_KEY (需要生成随机密钥)")
fi

if [ -z "$ENCRYPTION_KEY" ] || [ "$ENCRYPTION_KEY" = "your-encryption-key-change-this-in-production" ]; then
    MISSING_VARS+=("ENCRYPTION_KEY (需要生成 Fernet 密钥)")
fi

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "✗ 以下环境变量未正确配置:"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    echo ""
    echo "请编辑 .env 文件并设置这些变量："
    echo "  SECRET_KEY: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
    echo "  ENCRYPTION_KEY: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
    exit 1
fi

echo "✓ 环境变量验证通过"
echo ""

# 提取数据库连接信息
if [[ $DATABASE_URL =~ postgresql://([^:]+):([^@]+)@([^:]+):([0-9]+)/(.+) ]]; then
    DB_USER="${BASH_REMATCH[1]}"
    DB_PASSWORD="${BASH_REMATCH[2]}"
    DB_HOST="${BASH_REMATCH[3]}"
    DB_PORT="${BASH_REMATCH[4]}"
    DB_NAME="${BASH_REMATCH[5]}"
else
    echo "✗ 无法解析DATABASE_URL"
    exit 1
fi

# 处理host.docker.internal
if [ "$DB_HOST" = "host.docker.internal" ]; then
    DB_HOST="localhost"
fi

echo "数据库主机: $DB_HOST"
echo "数据库端口: $DB_PORT"
echo "数据库名称: $DB_NAME"

# 询问是否清理整个数据库
echo ""
echo "=========================================="
echo "  数据库初始化选项"
echo "=========================================="
echo ""
echo "请选择初始化方式："
echo "  1. 清理整个数据库并重建（推荐，最干净）"
echo "  2. 保留现有数据，只更新表结构"
echo ""
read -p "请输入选项 (1/2，默认为1): " INIT_OPTION
INIT_OPTION=${INIT_OPTION:-1}

if [ "$INIT_OPTION" = "1" ]; then
    echo ""
    echo "⚠ 警告: 这将删除数据库中的所有表和数据！"
    echo "数据库: $DB_NAME"
    echo ""
    read -p "确认清理整个数据库? (yes/no): " CONFIRM
    
    if [[ "$CONFIRM" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo ""
        echo ">>> 清理整个数据库（使用 PostgreSQL 容器）..."
        
        # 使用配置的 PostgreSQL 容器，如果未配置则自动查找
        if [ -z "$PG_DOCKER_CONTAINER" ]; then
            PG_CONTAINER=$(docker ps --format '{{.Names}}' | grep -i postgres | head -1)
            if [ -z "$PG_CONTAINER" ]; then
                echo "✗ 未找到 PostgreSQL 容器"
                echo "  请在 .env 中设置 PG_DOCKER_CONTAINER"
                exit 1
            fi
            echo "  自动检测到容器: $PG_CONTAINER"
        else
            PG_CONTAINER="$PG_DOCKER_CONTAINER"
            echo "  使用配置的容器: $PG_CONTAINER"
        fi
        
        # 使用 PostgreSQL 容器中的 psql 清理数据库
        # 简单粗暴：删除并重建 public schema
        docker exec -e PGPASSWORD=$DB_PASSWORD $PG_CONTAINER \
            psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
        
        if [ $? -eq 0 ]; then
            echo "✓ 数据库已清理"
        else
            echo "✗ 数据库清理失败"
            exit 1
        fi
    else
        echo "取消清理，退出"
        exit 0
    fi
else
    echo ""
    echo ">>> 清理旧的迁移版本记录（使用 PostgreSQL 容器）..."
    
    # 使用配置的 PostgreSQL 容器，如果未配置则自动查找
    if [ -z "$PG_DOCKER_CONTAINER" ]; then
        PG_CONTAINER=$(docker ps --format '{{.Names}}' | grep -i postgres | head -1)
        if [ -z "$PG_CONTAINER" ]; then
            echo "✗ 未找到 PostgreSQL 容器"
            echo "  请在 .env 中设置 PG_DOCKER_CONTAINER"
            exit 1
        fi
        echo "  自动检测到容器: $PG_CONTAINER"
    else
        PG_CONTAINER="$PG_DOCKER_CONTAINER"
        echo "  使用配置的容器: $PG_CONTAINER"
    fi
    
    docker exec -e PGPASSWORD=$DB_PASSWORD $PG_CONTAINER \
        psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
        -c "DELETE FROM alembic_version;" 2>/dev/null || echo "  ✓ 表不存在或已清空"
fi

# 恢复数据库
echo ""
echo ">>> 恢复数据库..."

# 检查是否有 SQL 文件
if [ -f "database/database.sql.gz" ] || [ -f "database/database.sql" ]; then
    echo ">>> 使用 psql 恢复完整数据库..."
    echo "⚠ 这将恢复完整的数据库结构和数据"
    echo ""
    
    # 解压 SQL 文件（如果是压缩的）
    if [ -f "database/database.sql.gz" ]; then
        echo ">>> 解压 SQL 文件..."
        gunzip -c database/database.sql.gz > database/database.sql
        CLEANUP_SQL=true
    else
        CLEANUP_SQL=false
    fi
    
    # 使用 psql 恢复 SQL 文件
    if command -v psql &> /dev/null; then
        PSQL_VERSION=$(psql --version | grep -oP '\d+\.\d+' | head -1)
        echo ">>> 使用本地 psql (版本 $PSQL_VERSION)..."
        
        # 使用 --set ON_ERROR_STOP=0 继续执行即使遇到错误（如版本差异导致的参数不兼容）
        PGPASSWORD=$DB_PASSWORD psql \
            -h $DB_HOST \
            -p $DB_PORT \
            -U $DB_USER \
            -d $DB_NAME \
            -f database/database.sql \
            --quiet \
            --set ON_ERROR_STOP=0 \
            2>&1 | grep -v "unrecognized configuration parameter" || true
        
        echo "✓ 数据库恢复完成"
        USE_DOCKER=false
    fi
    
    # 如果本地工具不可用，使用 Docker
    if [ ! -v USE_DOCKER ] || [ "$USE_DOCKER" = true ]; then
        if [ ! -v USE_DOCKER ]; then
            echo "⚠ 本地未安装 psql"
        fi
        echo "  尝试使用 Docker 容器中的 PostgreSQL 客户端..."
        
        # 检查是否有可用的 PostgreSQL 容器
        PG_CONTAINER=""
        
        # 方法1: 使用配置指定的容器
        if [ -n "$PG_DOCKER_CONTAINER" ]; then
            if docker ps --format '{{.Names}}' | grep -q "^${PG_DOCKER_CONTAINER}$"; then
                PG_CONTAINER="$PG_DOCKER_CONTAINER"
                echo "  使用配置指定的容器: $PG_CONTAINER"
            else
                echo "  ⚠ 配置的容器 $PG_DOCKER_CONTAINER 未运行"
            fi
        fi
        
        # 方法2: 自动检测运行中的 PostgreSQL 容器
        if [ -z "$PG_CONTAINER" ]; then
            if docker ps --format '{{.Names}}' | grep -q postgres; then
                PG_CONTAINER=$(docker ps --format '{{.Names}}' | grep postgres | head -1)
                echo "  自动检测到 PostgreSQL 容器: $PG_CONTAINER"
            fi
        fi
        
        # 如果找到了容器，使用容器中的 psql
        if [ -n "$PG_CONTAINER" ]; then
            echo "  使用容器 $PG_CONTAINER 中的 psql"
            
            # 复制 SQL 文件到容器
            docker cp database/database.sql $PG_CONTAINER:/tmp/database.sql
            
            # 在容器中执行 psql
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
                echo "✓ 数据库恢复完成"
            else
                echo "⚠ 恢复过程中有警告（通常可以忽略）"
            fi
            
            # 清理临时文件
            docker exec $PG_CONTAINER rm -f /tmp/database.sql
        else
            # 方法3: 使用本地的 PostgreSQL 镜像（不拉取）
            if docker image inspect $PG_DOCKER_IMAGE &> /dev/null; then
                echo "  使用本地镜像: $PG_DOCKER_IMAGE"
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
                    echo "✓ 数据库恢复完成"
                else
                    echo "⚠ 恢复过程中有警告（通常可以忽略）"
                fi
            else
                echo "✗ 未找到 PostgreSQL 容器或镜像"
                echo ""
                echo "解决方案："
                echo "  1. 安装 PostgreSQL 客户端工具"
                echo "  2. 或指定包含 psql 的 Docker 容器："
                echo "     export PG_DOCKER_CONTAINER=<container_name>"
                echo "     bash scripts/init-database.sh"
                echo ""
                echo "  3. 或手动恢复数据库："
                echo "     PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f database/database.sql"
                echo ""
                exit 1
            fi
        fi
    fi
    
    # 清理临时 SQL 文件
    if [ "$CLEANUP_SQL" = true ]; then
        rm -f database/database.sql
    fi
    
    echo ""
    echo ">>> 验证数据库（使用 PostgreSQL 容器）..."
    
    # 使用配置的 PostgreSQL 容器
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
            echo "✓ 数据库验证通过"
            echo "  表数量: $TABLE_COUNT"
        else
            echo "⚠ 数据库可能未正确恢复"
        fi
    else
        echo "⚠ 未找到 PostgreSQL 容器，跳过验证"
    fi
else
    echo "⚠ 未找到数据库 dump 文件 (database/database.dump)"
    echo "  将使用 Alembic 迁移创建表结构..."
    echo ""
    
    # 检查容器是否运行
    if ! docker ps | grep -q hospital_backend_offline; then
        echo "⚠ 后端容器未运行，尝试启动..."
        docker-compose -f config/docker-compose.offline.yml up -d backend
        echo "等待容器启动..."
        sleep 5
    fi
    
    # 使用 Alembic 创建表结构
    echo ">>> 执行数据库迁移..."
    docker exec hospital_backend_offline alembic upgrade head
    
    if [ $? -eq 0 ]; then
        echo "✓ 数据库表结构创建完成"
    else
        echo "⚠ 迁移失败，尝试使用 heads 参数..."
        docker exec hospital_backend_offline alembic upgrade heads
    fi
    
    # 初始化管理员用户
    echo ""
    echo ">>> 初始化管理员用户..."
    docker exec hospital_backend_offline python scripts/init_admin.py
    if [ $? -eq 0 ]; then
        echo "✓ 管理员用户初始化完成"
    else
        echo "⚠ 管理员用户初始化失败（可能已存在）"
    fi
fi

echo ""
echo "=========================================="
echo "  数据库初始化完成"
echo "=========================================="
