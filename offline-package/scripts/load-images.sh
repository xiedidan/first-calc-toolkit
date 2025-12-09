#!/bin/bash
# ============================================
# Docker镜像导入脚本
# ============================================

set -e

echo "=========================================="
echo "  导入Docker镜像"
echo "=========================================="
echo ""

# 检查Docker是否运行
echo ">>> 检查Docker环境..."
if ! docker version &> /dev/null; then
    echo "✗ Docker未运行或无权限访问"
    echo ""
    echo "可能的解决方案："
    echo "1. 启动Docker服务："
    echo "   sudo systemctl start docker"
    echo ""
    echo "2. 将当前用户添加到docker组（需要重新登录）："
    echo "   sudo usermod -aG docker \$USER"
    echo ""
    echo "3. 使用sudo运行此脚本："
    echo "   sudo bash scripts/load-images.sh"
    exit 1
fi
echo "✓ Docker运行正常"
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
