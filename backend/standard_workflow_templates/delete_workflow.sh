#!/bin/bash

# 快速删除指定的 workflow 及其所有关联数据
# 使用方法: bash delete_workflow.sh <WORKFLOW_ID>
# 示例: bash delete_workflow.sh 13

# 检查参数
if [ -z "$1" ]; then
    echo "错误: 请指定要删除的 workflow ID"
    echo "使用方法: bash delete_workflow.sh <WORKFLOW_ID>"
    echo "示例: bash delete_workflow.sh 13"
    exit 1
fi

WORKFLOW_ID=$1

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

echo "=========================================="
echo "开始删除 workflow_id=$WORKFLOW_ID 及其所有关联数据..."
echo "=========================================="
echo ""

# 先查询流程信息
echo "查询流程信息:"
psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -c \
    "SELECT id, name, created_at FROM calculation_workflows WHERE id = $WORKFLOW_ID;"

echo ""
read -p "确认删除 workflow_id=$WORKFLOW_ID 吗? (y/N): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "取消删除操作"
    unset PGPASSWORD
    exit 0
fi

echo ""
echo "正在删除..."

psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" << EOF
-- 删除步骤日志
DELETE FROM calculation_step_logs WHERE task_id IN (SELECT task_id FROM calculation_tasks WHERE workflow_id = $WORKFLOW_ID);

-- 删除计算汇总
DELETE FROM calculation_summaries WHERE task_id IN (SELECT task_id FROM calculation_tasks WHERE workflow_id = $WORKFLOW_ID);

-- 删除计算结果
DELETE FROM calculation_results WHERE task_id IN (SELECT task_id FROM calculation_tasks WHERE workflow_id = $WORKFLOW_ID);

-- 删除计算任务
DELETE FROM calculation_tasks WHERE workflow_id = $WORKFLOW_ID;

-- 删除计算步骤
DELETE FROM calculation_steps WHERE workflow_id = $WORKFLOW_ID;

-- 删除流程
DELETE FROM calculation_workflows WHERE id = $WORKFLOW_ID;

-- 显示结果
SELECT 'workflow_id=$WORKFLOW_ID 已成功删除' as status;
EOF

echo ""
echo "=========================================="
echo "删除完成!"
echo "=========================================="

unset PGPASSWORD
