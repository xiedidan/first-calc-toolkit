#!/bin/bash
# ============================================
# 数据库初始化脚本
# ============================================

set -e

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
echo ""

# 等待数据库就绪
echo ">>> 等待数据库就绪..."
for i in {1..30}; do
    if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c '\q' 2>/dev/null; then
        echo "✓ 数据库连接成功"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "✗ 数据库连接超时"
        exit 1
    fi
    echo "等待数据库启动... ($i/30)"
    sleep 2
done

# 导入数据库数据
if [ -f "database/database_export.json.gz" ]; then
    echo ""
    echo ">>> 导入数据库数据（使用Python脚本）..."
    echo "⚠ 这将导入数据到数据库，是否继续? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        # 解压数据文件
        gunzip -c database/database_export.json.gz > database/database_export.json
        
        # 使用Docker容器内的Python导入数据
        docker cp database/database_export.json hospital_backend_offline:/app/
        docker exec hospital_backend_offline python import_database.py
        
        # 清理临时文件
        rm -f database/database_export.json
        
        echo "✓ 数据库数据导入完成"
    else
        echo "跳过数据导入"
    fi
elif [ -f "database/database_export.json" ]; then
    echo ""
    echo ">>> 导入数据库数据（使用Python脚本）..."
    echo "⚠ 这将导入数据到数据库，是否继续? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        # 使用Docker容器内的Python导入数据
        docker cp database/database_export.json hospital_backend_offline:/app/
        docker exec hospital_backend_offline python import_database.py
        
        echo "✓ 数据库数据导入完成"
    else
        echo "跳过数据导入"
    fi
else
    echo "⚠ 未找到数据库数据文件，跳过导入"
    echo ">>> 执行数据库迁移..."
    docker exec hospital_backend_offline alembic upgrade head || echo "⚠ 数据库迁移失败，容器可能未启动"
fi

echo ""
echo "=========================================="
echo "  数据库初始化完成"
echo "=========================================="
