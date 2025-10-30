#!/bin/bash
# ============================================
# 一键部署脚本
# ============================================

set -e

echo "=========================================="
echo "  医院科室业务价值评估工具"
echo "  离线部署"
echo "=========================================="
echo ""

# 步骤1: 检查前置条件
echo "步骤 1/6: 检查前置条件"
echo "=========================================="
bash scripts/check-prerequisites.sh
echo ""

# 步骤2: 导入Docker镜像
echo "步骤 2/6: 导入Docker镜像"
echo "=========================================="
bash scripts/load-images.sh
echo ""

# 步骤3: 配置环境
echo "步骤 3/6: 配置环境"
echo "=========================================="
if [ ! -f ".env" ]; then
    echo ">>> 创建配置文件..."
    cp config/.env.offline.template .env
    echo "✓ 配置文件已创建: .env"
    echo ""
    echo "⚠ 请编辑 .env 文件，配置以下信息:"
    echo "  1. 数据库连接信息 (DATABASE_URL)"
    echo "  2. JWT密钥 (SECRET_KEY)"
    echo "  3. 加密密钥 (ENCRYPTION_KEY)"
    echo ""
    echo "生成密钥的方法:"
    echo "  SECRET_KEY: python3 -c \"import secrets; print(secrets.token_urlsafe(32))\""
    echo "  ENCRYPTION_KEY: python3 -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
    echo ""
    echo "配置完成后，重新运行此脚本"
    exit 0
else
    echo "✓ 配置文件已存在"
fi
echo ""

# 步骤4: 启动服务
echo "步骤 4/6: 启动服务"
echo "=========================================="
echo ">>> 启动Docker容器..."
docker-compose -f config/docker-compose.offline.yml up -d
echo "✓ 服务启动完成"
echo ""

# 步骤5: 等待服务就绪
echo "步骤 5/6: 等待服务就绪"
echo "=========================================="
echo ">>> 等待容器启动..."
sleep 10

echo ">>> 检查容器状态..."
docker-compose -f config/docker-compose.offline.yml ps
echo ""

# 步骤6: 初始化数据库
echo "步骤 6/6: 初始化数据库"
echo "=========================================="
bash scripts/init-database.sh
echo ""

# 验证部署
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo ""
echo "服务访问地址:"
echo "  前端: http://localhost:${FRONTEND_PORT:-80}"
echo "  后端API: http://localhost:${BACKEND_PORT:-8000}/docs"
echo ""
echo "常用命令:"
echo "  查看服务状态: docker-compose -f config/docker-compose.offline.yml ps"
echo "  查看日志: docker-compose -f config/docker-compose.offline.yml logs -f"
echo "  停止服务: docker-compose -f config/docker-compose.offline.yml stop"
echo "  启动服务: docker-compose -f config/docker-compose.offline.yml start"
echo "  重启服务: docker-compose -f config/docker-compose.offline.yml restart"
echo ""
