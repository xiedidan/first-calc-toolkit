#!/bin/bash
# ============================================
# 前置条件检查脚本
# ============================================

echo "=========================================="
echo "  检查部署前置条件"
echo "=========================================="
echo ""

# 检查Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo "✓ Docker已安装: $DOCKER_VERSION"
else
    echo "✗ Docker未安装，请先安装Docker"
    exit 1
fi

# 检查Docker是否运行
if docker info &> /dev/null; then
    echo "✓ Docker服务运行正常"
else
    echo "✗ Docker服务未运行，请启动Docker"
    exit 1
fi

# 检查Docker Compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo "✓ Docker Compose已安装: $COMPOSE_VERSION"
elif docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version)
    echo "✓ Docker Compose已安装: $COMPOSE_VERSION"
else
    echo "✗ Docker Compose未安装，请先安装"
    exit 1
fi

# 检查磁盘空间
AVAILABLE_SPACE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ $AVAILABLE_SPACE -gt 10 ]; then
    echo "✓ 磁盘空间充足: ${AVAILABLE_SPACE}GB"
else
    echo "⚠ 磁盘空间不足，建议至少10GB，当前: ${AVAILABLE_SPACE}GB"
fi

# 检查端口占用
echo ""
echo "检查端口占用情况:"
PORTS=(80 8000 6379)
for PORT in "${PORTS[@]}"; do
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":$PORT "; then
        echo "⚠ 端口 $PORT 已被占用"
    else
        echo "✓ 端口 $PORT 可用"
    fi
done

echo ""
echo "=========================================="
echo "  前置条件检查完成"
echo "=========================================="
