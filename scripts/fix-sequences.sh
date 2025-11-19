#!/bin/bash
# ============================================
# 修复数据库序列脚本
# 用于解决导入数据后主键冲突的问题
# ============================================

set -e

echo "=========================================="
echo "  修复数据库序列"
echo "=========================================="
echo ""
echo "此脚本将重置所有表的自增序列到正确的值"
echo "解决 'duplicate key value violates unique constraint' 错误"
echo ""

# 检查容器是否运行
if ! docker ps | grep -q hospital_backend_offline; then
    echo "✗ 后端容器未运行"
    echo "请先启动服务: docker-compose -f config/docker-compose.offline.yml up -d"
    exit 1
fi

echo ">>> 执行序列重置..."
docker exec hospital_backend_offline python reset_sequences.py

echo ""
echo "=========================================="
echo "  序列修复完成"
echo "=========================================="
echo ""
echo "现在可以正常创建新记录了！"
