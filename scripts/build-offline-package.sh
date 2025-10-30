#!/bin/bash
# ============================================
# 医院科室业务价值评估工具 - 离线部署包构建脚本
# 适用于: Windows 11 WSL2 + Docker Desktop
# ============================================

set -e

echo "=========================================="
echo "  离线部署包构建工具"
echo "=========================================="
echo ""

# 检查Docker是否运行
echo ">>> 检查Docker环境..."
if ! docker version &> /dev/null; then
    echo "✗ Docker未运行，请启动Docker Desktop"
    exit 1
fi
echo "✓ Docker运行正常"

# 设置版本号
VERSION="1.0.0"

echo ">>> 构建版本: $VERSION"
echo ""

# 创建输出目录
PACKAGE_DIR="offline-package"
IMAGES_DIR="$PACKAGE_DIR/images"
DATABASE_DIR="$PACKAGE_DIR/database"
CONFIG_DIR="$PACKAGE_DIR/config"
SCRIPTS_DIR="$PACKAGE_DIR/scripts"
DOCS_DIR="$PACKAGE_DIR/docs"

echo ">>> 创建目录结构..."
mkdir -p "$IMAGES_DIR"
mkdir -p "$DATABASE_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$SCRIPTS_DIR"
mkdir -p "$DOCS_DIR"
echo "✓ 目录创建完成"
echo ""

# 步骤1: 拉取基础镜像
echo "=========================================="
echo "  步骤 1/6: 拉取基础镜像"
echo "=========================================="

# 拉取Python基础镜像
echo ">>> 检查/拉取 python:3.12 镜像..."
if docker image inspect python:3.12 &> /dev/null; then
    echo "✓ 使用本地 python:3.12 镜像"
else
    echo ">>> 拉取 python:3.12 镜像（约1GB，请耐心等待）..."
    docker pull python:3.12
    if [ $? -eq 0 ]; then
        echo "✓ python:3.12 镜像拉取完成"
    else
        echo "✗ 镜像拉取失败，尝试使用已有的 python:3.12-slim"
        if ! docker image inspect python:3.12-slim &> /dev/null; then
            docker pull python:3.12-slim
        fi
    fi
fi

# 拉取Node基础镜像
echo ">>> 检查/拉取 node:18-alpine 镜像..."
if docker image inspect node:18-alpine &> /dev/null; then
    echo "✓ 使用本地 node:18-alpine 镜像"
else
    echo ">>> 拉取 node:18-alpine 镜像..."
    docker pull node:18-alpine || echo "⚠ 镜像拉取失败，将使用本地镜像"
fi

# 拉取Nginx基础镜像
echo ">>> 检查/拉取 nginx:alpine 镜像..."
if docker image inspect nginx:alpine &> /dev/null; then
    echo "✓ 使用本地 nginx:alpine 镜像"
else
    echo ">>> 拉取 nginx:alpine 镜像..."
    docker pull nginx:alpine || echo "⚠ 镜像拉取失败，将使用本地镜像"
fi
echo ""

# 步骤2: 构建Docker镜像
echo "=========================================="
echo "  步骤 2/6: 构建Docker镜像"
echo "=========================================="

# 构建后端镜像（使用离线专用Dockerfile，包含更多预编译依赖）
echo ">>> 构建后端镜像（使用python:3.12完整镜像，避免编译依赖）..."
if [ -f "backend/Dockerfile.offline" ]; then
    docker build --platform linux/amd64 -f backend/Dockerfile.offline -t hospital-backend:latest ./backend
else
    docker build --platform linux/amd64 -t hospital-backend:latest ./backend
fi
echo "✓ 后端镜像构建完成"

# 构建前端镜像
echo ">>> 构建前端镜像..."
docker build --platform linux/amd64 -t hospital-frontend:latest ./frontend
echo "✓ 前端镜像构建完成"

# 检查Redis镜像
echo ">>> 检查Redis镜像..."
if docker image inspect redis:7-alpine &> /dev/null; then
    echo "✓ 使用本地Redis镜像"
else
    echo ">>> 拉取Redis镜像..."
    docker pull redis:7-alpine
    echo "✓ Redis镜像拉取完成"
fi
echo ""

# 步骤2: 导出Docker镜像
echo "=========================================="
echo "  步骤 2/5: 导出Docker镜像"
echo "=========================================="

# 导出后端镜像
echo ">>> 导出后端镜像..."
docker save hospital-backend:latest | gzip > "$IMAGES_DIR/backend.tar.gz"
BACKEND_SIZE=$(du -h "$IMAGES_DIR/backend.tar.gz" | cut -f1)
echo "✓ 后端镜像导出完成 ($BACKEND_SIZE)"

# 导出前端镜像
echo ">>> 导出前端镜像..."
docker save hospital-frontend:latest | gzip > "$IMAGES_DIR/frontend.tar.gz"
FRONTEND_SIZE=$(du -h "$IMAGES_DIR/frontend.tar.gz" | cut -f1)
echo "✓ 前端镜像导出完成 ($FRONTEND_SIZE)"

# 导出Redis镜像
echo ">>> 导出Redis镜像..."
docker save redis:7-alpine | gzip > "$IMAGES_DIR/redis.tar.gz"
REDIS_SIZE=$(du -h "$IMAGES_DIR/redis.tar.gz" | cut -f1)
echo "✓ Redis镜像导出完成 ($REDIS_SIZE)"
echo ""

# 步骤3: 导出数据库数据
echo "=========================================="
echo "  步骤 3/5: 导出数据库数据"
echo "=========================================="

# 检查是否有.env文件
if [ -f "backend/.env" ]; then
    echo ">>> 使用Docker容器导出数据库..."
    
    # 启动临时容器来导出数据
    echo ">>> 启动临时后端容器..."
    docker run --rm \
        --network host \
        -v "$(pwd)/backend:/app" \
        -w /app \
        --env-file backend/.env \
        hospital-backend:latest \
        python export_database.py
    
    # 检查导出是否成功
    if [ -f "backend/database_export.json" ]; then
        # 移动导出文件到database目录
        mv backend/database_export.json "$DATABASE_DIR/"
        
        # 压缩JSON文件
        echo ">>> 压缩数据文件..."
        gzip "$DATABASE_DIR/database_export.json"
        
        DB_SIZE=$(du -h "$DATABASE_DIR/database_export.json.gz" | cut -f1)
        echo "✓ 数据库导出完成 ($DB_SIZE)"
    else
        echo "⚠ 数据库导出失败"
        echo "  如需导出数据，可以手动运行:"
        echo "  docker run --rm --network host -v \$(pwd)/backend:/app -w /app --env-file backend/.env hospital-backend:latest python export_database.py"
    fi
else
    echo "⚠ 未找到backend/.env文件，跳过数据库导出"
    echo "  如需导出数据，请配置backend/.env文件后重新运行"
fi
echo ""

# 步骤4: 复制配置文件和脚本
echo "=========================================="
echo "  步骤 4/5: 打包配置文件和脚本"
echo "=========================================="

# 复制Docker Compose配置
echo ">>> 复制配置文件..."
if [ -f "docker-compose.offline.yml" ]; then
    cp docker-compose.offline.yml "$CONFIG_DIR/"
    echo "✓ 复制 docker-compose.offline.yml"
fi

# 复制环境变量模板
if [ -f "backend/.env.offline.template" ]; then
    cp backend/.env.offline.template "$CONFIG_DIR/"
    echo "✓ 复制 .env.offline.template"
fi

# 复制部署脚本
echo ">>> 复制部署脚本..."
if [ -f "scripts/deploy-offline.sh" ]; then
    cp scripts/deploy-offline.sh "$SCRIPTS_DIR/"
    chmod +x "$SCRIPTS_DIR/deploy-offline.sh"
    echo "✓ 复制 deploy-offline.sh"
fi
if [ -f "scripts/load-images.sh" ]; then
    cp scripts/load-images.sh "$SCRIPTS_DIR/"
    chmod +x "$SCRIPTS_DIR/load-images.sh"
    echo "✓ 复制 load-images.sh"
fi
if [ -f "scripts/init-database.sh" ]; then
    cp scripts/init-database.sh "$SCRIPTS_DIR/"
    chmod +x "$SCRIPTS_DIR/init-database.sh"
    echo "✓ 复制 init-database.sh"
fi
if [ -f "scripts/check-prerequisites.sh" ]; then
    cp scripts/check-prerequisites.sh "$SCRIPTS_DIR/"
    chmod +x "$SCRIPTS_DIR/check-prerequisites.sh"
    echo "✓ 复制 check-prerequisites.sh"
fi

# 复制文档
echo ">>> 复制文档..."
if [ -f "离线部署方案.md" ]; then
    cp "离线部署方案.md" "$DOCS_DIR/"
    echo "✓ 复制 离线部署方案.md"
fi
if [ -f "OFFLINE_DEPLOYMENT_GUIDE.md" ]; then
    cp OFFLINE_DEPLOYMENT_GUIDE.md "$DOCS_DIR/"
    echo "✓ 复制 OFFLINE_DEPLOYMENT_GUIDE.md"
fi

# 创建README
echo ">>> 创建README..."
cat > "$PACKAGE_DIR/README.md" << EOF
# 医院科室业务价值评估工具 - 离线部署包 v$VERSION

## 部署包内容

- images/ - Docker镜像文件（约500MB）
- database/ - 数据库数据文件
- config/ - 配置文件
- scripts/ - 部署脚本
- docs/ - 部署文档

## 快速开始

### 1. 解压部署包

\`\`\`bash
tar -xzf hospital-value-toolkit-offline-v$VERSION.tar.gz
cd offline-package
\`\`\`

### 2. 导入Docker镜像

\`\`\`bash
bash scripts/load-images.sh
\`\`\`

### 3. 配置环境

\`\`\`bash
cp config/.env.offline.template .env
vi .env  # 编辑数据库连接信息
\`\`\`

### 4. 初始化数据库

\`\`\`bash
bash scripts/init-database.sh
\`\`\`

### 5. 启动服务

\`\`\`bash
docker-compose -f config/docker-compose.offline.yml up -d
\`\`\`

### 6. 访问系统

- 前端: http://localhost:80
- 后端API: http://localhost:8000/docs

## 详细说明

请参考 docs/OFFLINE_DEPLOYMENT_GUIDE.md 获取详细的部署指南。

## 系统要求

- Linux服务器
- Docker 20.10+
- Docker Compose 2.0+
- PostgreSQL 数据库（已有实例）
- 至少8GB内存
- 至少50GB磁盘空间

## 技术支持

如遇问题，请查看文档或联系技术支持。
EOF

echo "✓ 创建 README.md"
echo ""

# 步骤5: 生成最终部署包
echo "=========================================="
echo "  步骤 5/5: 生成最终部署包"
echo "=========================================="

PACKAGE_NAME="hospital-value-toolkit-offline-v$VERSION.tar.gz"

echo ">>> 打包文件..."
tar -czf "$PACKAGE_NAME" "$PACKAGE_DIR"

if [ $? -eq 0 ]; then
    PACKAGE_SIZE=$(du -h "$PACKAGE_NAME" | cut -f1)
    echo "✓ 部署包生成完成"
    echo ""
    echo "=========================================="
    echo "  构建完成！"
    echo "=========================================="
    echo ""
    echo "部署包: $PACKAGE_NAME"
    echo "大小: $PACKAGE_SIZE"
    echo ""
    echo "下一步:"
    echo "1. 将 $PACKAGE_NAME 传输到目标Linux服务器"
    echo "2. 在目标服务器上解压并执行部署脚本"
    echo "3. 详细步骤请参考 offline-package/docs/OFFLINE_DEPLOYMENT_GUIDE.md"
else
    echo "✗ 打包失败"
    exit 1
fi

echo ""
echo "构建完成！"
