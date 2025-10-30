#!/bin/bash
# ============================================
# Docker镜像导入脚本
# ============================================

set -e

echo "=========================================="
echo "  导入Docker镜像"
echo "=========================================="
echo ""

IMAGES_DIR="./images"

if [ ! -d "$IMAGES_DIR" ]; then
    echo "✗ 镜像目录不存在: $IMAGES_DIR"
    exit 1
fi

# 导入后端镜像
if [ -f "$IMAGES_DIR/backend.tar.gz" ]; then
    echo ">>> 导入后端镜像..."
    docker load < $IMAGES_DIR/backend.tar.gz
    echo "✓ 后端镜像导入完成"
else
    echo "✗ 未找到后端镜像文件"
    exit 1
fi

# 导入前端镜像
if [ -f "$IMAGES_DIR/frontend.tar.gz" ]; then
    echo ">>> 导入前端镜像..."
    docker load < $IMAGES_DIR/frontend.tar.gz
    echo "✓ 前端镜像导入完成"
else
    echo "✗ 未找到前端镜像文件"
    exit 1
fi

# 导入Redis镜像
if [ -f "$IMAGES_DIR/redis.tar.gz" ]; then
    echo ">>> 导入Redis镜像..."
    docker load < $IMAGES_DIR/redis.tar.gz
    echo "✓ Redis镜像导入完成"
else
    echo "✗ 未找到Redis镜像文件"
    exit 1
fi

echo ""
echo "=========================================="
echo "  镜像导入完成"
echo "=========================================="
echo ""
echo "已导入的镜像:"
docker images | grep -E "hospital|redis" || echo "未找到相关镜像"
