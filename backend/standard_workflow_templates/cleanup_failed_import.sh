#!/bin/bash

# 清理失败的导入记录
# 使用方法: bash cleanup_failed_import.sh

# 读取.env配置
ENV_FILE="../.env"
export $(grep -v '^#' "$ENV_FILE" | grep -E '^DATABASE_' | xargs)

# 解析DATABASE_URL
if [ -n "$DATABASE_URL" ] && [ -z "$DATABASE_HOST" ]; then
    if [[ $DATABASE_URL =~ postgresql://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+) ]]; then
        DATABASE_USER="${BASH_REMATCH[1]}"
        DATABASE_PASSWORD="${BASH_REMATCH[2]}"
        DATABASE_HOST="${BASH_REMATCH[3]}"
        DATABASE_PORT="${BASH_REMATCH[4]}"
        DATABASE_NAME="${BASH_REMATCH[5]}"
    fi
fi

export PGPASSWORD="$DATABASE_PASSWORD"

echo "查询最近创建的计算流程..."
psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -c \
    "SELECT id, name, created_at FROM calculation_workflows ORDER BY created_at DESC LIMIT 5;"

echo ""
echo "如果需要删除某个流程,请执行:"
echo "psql -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER -d $DATABASE_NAME -c \"DELETE FROM calculation_workflows WHERE id = <ID>;\""

unset PGPASSWORD
