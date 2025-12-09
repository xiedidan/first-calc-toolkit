#!/bin/bash
# ============================================
# 医院科室业务价值评估工具 - 离线部署包构建脚本
# 适用于: Windows 11 WSL2 + Docker Desktop
# 
# 重要提示:
# 1. 确保所有代码更改已提交
# 2. 确保 backend/alembic/versions/ 包含所有迁移文件
# 3. 构建的 Docker 镜像将包含当前代码和迁移文件
# ============================================

set -e

echo "=========================================="
echo "  离线部署包构建工具"
echo "=========================================="
echo ""

# 检查迁移文件
echo ">>> 检查迁移文件..."
MIGRATION_COUNT=$(ls -1 backend/alembic/versions/*.py 2>/dev/null | wc -l)
if [ $MIGRATION_COUNT -eq 0 ]; then
    echo "⚠ 警告: 未找到迁移文件"
    echo "  请确保 backend/alembic/versions/ 目录包含迁移文件"
else
    echo "✓ 找到 $MIGRATION_COUNT 个迁移文件"
fi

# 检查迁移文件链的完整性
echo ">>> 检查迁移文件链..."
cd backend
HEADS_COUNT=$(python -c "
from alembic.config import Config
from alembic.script import ScriptDirectory
try:
    cfg = Config('alembic.ini')
    script = ScriptDirectory.from_config(cfg)
    heads = script.get_revisions('heads')
    print(len(heads))
except Exception as e:
    print('ERROR')
" 2>/dev/null)
cd ..

if [ "$HEADS_COUNT" = "1" ]; then
    echo "✓ 迁移文件链正常（1 head）"
elif [ "$HEADS_COUNT" = "ERROR" ]; then
    echo "⚠ 警告: 无法检查迁移文件链"
    echo "  请确保 Python 环境已安装 alembic"
else
    echo "⚠ 警告: 检测到 $HEADS_COUNT 个迁移分支（heads）"
    echo ""
    echo "这不会影响离线部署！"
    echo "init-database.sh 脚本会自动处理多个 heads："
    echo "  1. 自动尝试升级所有分支"
    echo "  2. 如果失败，自动创建合并迁移"
    echo "  3. 无需任何手动干预"
    echo ""
    echo "但为了更干净的迁移历史，建议现在修复："
    echo "  1. cd backend"
    echo "  2. alembic heads  # 查看所有 heads"
    echo "  3. alembic merge -m 'merge branches' head1 head2  # 合并分支"
    echo ""
    read -p "是否继续打包? (y/n，默认 y): " CONTINUE
    CONTINUE=${CONTINUE:-y}
    if [[ ! "$CONTINUE" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "取消打包"
        exit 1
    fi
    echo ">>> 继续打包（部署时会自动修复）..."
fi
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

echo ">>> 清理旧的打包目录..."
if [ -d "$PACKAGE_DIR" ]; then
    echo "  发现旧的 $PACKAGE_DIR 目录，清理中..."
    rm -rf "$PACKAGE_DIR"
    echo "  ✓ 旧目录已清理"
fi

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
echo "  步骤 3/5: 导出数据库（使用 pg_dump）"
echo "=========================================="

# 检查是否有.env文件
if [ -f "backend/.env" ]; then
    echo ">>> 使用 pg_dump 导出完整数据库..."
    echo ""
    
    # 读取数据库连接信息（只读取未注释的行）
    DATABASE_URL=$(grep -v '^\s*#' backend/.env | grep 'DATABASE_URL=' | tail -1 | cut -d'=' -f2-)
    
    # 提取数据库连接信息
    if [[ $DATABASE_URL =~ postgresql://([^:]+):([^@]+)@([^:]+):([0-9]+)/(.+) ]]; then
        DB_USER="${BASH_REMATCH[1]}"
        DB_PASSWORD="${BASH_REMATCH[2]}"
        DB_HOST="${BASH_REMATCH[3]}"
        DB_PORT="${BASH_REMATCH[4]}"
        DB_NAME="${BASH_REMATCH[5]}"
    else
        echo "✗ 无法解析DATABASE_URL"
        echo "  跳过数据库导出"
        echo ""
        DB_USER=""
    fi
    
    if [ -n "$DB_USER" ]; then
        # 处理 host.docker.internal
        if [ "$DB_HOST" = "host.docker.internal" ]; then
            DB_HOST="localhost"
        fi
        
        echo "数据库主机: $DB_HOST"
        echo "数据库端口: $DB_PORT"
        echo "数据库名称: $DB_NAME"
        echo ""
        
        # 检查 pg_dump 是否可用
        if command -v pg_dump &> /dev/null; then
            echo ">>> 使用本地 pg_dump 分离导出（结构 + 部分数据）..."
            echo ""
            
            # 从配置文件读取排除列表
            EXCLUDE_FILE=".offline-package-exclude-tables.txt"
            if [ ! -f "$EXCLUDE_FILE" ]; then
                echo "✗ 未找到排除列表文件: $EXCLUDE_FILE"
                echo "  请创建该文件并列出要排除的表名（每行一个）"
                exit 1
            fi
            
            # 读取并过滤排除列表（忽略空行和注释）
            TABLES_SCHEMA_ONLY=()
            while IFS= read -r line; do
                # 跳过注释和空行
                if [[ ! "$line" =~ ^[[:space:]]*# ]] && [[ -n "${line// }" ]]; then
                    # 去除前后空格
                    table=$(echo "$line" | xargs)
                    TABLES_SCHEMA_ONLY+=("$table")
                fi
            done < "$EXCLUDE_FILE"
            
            if [ ${#TABLES_SCHEMA_ONLY[@]} -eq 0 ]; then
                echo "⚠ 排除列表为空，将导出所有表的数据"
            fi
            
            echo "导出策略:"
            echo "  - 排除列表文件: $EXCLUDE_FILE"
            echo "  - 大数据表（仅结构）: ${#TABLES_SCHEMA_ONLY[@]} 个"
            echo "  - 其他所有表（含数据）: 自动包含"
            echo ""
            
            if [ ${#TABLES_SCHEMA_ONLY[@]} -gt 0 ]; then
                echo "排除数据的表:"
                for table in "${TABLES_SCHEMA_ONLY[@]}"; do
                    echo "  - $table"
                done
                echo ""
            fi
            
            # 1. 导出完整的表结构（所有表）
            echo ">>> 步骤 1/3: 导出完整表结构..."
            PGPASSWORD=$DB_PASSWORD pg_dump \
                -h $DB_HOST \
                -p $DB_PORT \
                -U $DB_USER \
                -d $DB_NAME \
                -f "$DATABASE_DIR/schema.sql" \
                --schema-only \
                --no-owner \
                --no-acl
            
            if [ $? -ne 0 ]; then
                echo "✗ 表结构导出失败"
                rm -f "$DATABASE_DIR/schema.sql"
                exit 1
            fi
            echo "✓ 表结构导出完成"
            
            # 2. 导出所有表的数据（使用排除列表）
            echo ">>> 步骤 2/3: 导出数据（排除大数据表）..."
            EXCLUDE_ARGS=""
            for table in "${TABLES_SCHEMA_ONLY[@]}"; do
                EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude-table-data=$table"
            done
            
            PGPASSWORD=$DB_PASSWORD pg_dump \
                -h $DB_HOST \
                -p $DB_PORT \
                -U $DB_USER \
                -d $DB_NAME \
                -f "$DATABASE_DIR/data.sql" \
                --data-only \
                --no-owner \
                --no-acl \
                $EXCLUDE_ARGS
            
            if [ $? -ne 0 ]; then
                echo "✗ 数据导出失败"
                rm -f "$DATABASE_DIR/data.sql"
                exit 1
            fi
            echo "✓ 数据导出完成"
            
            # 3. 合并文件
            echo ">>> 步骤 3/3: 合并 SQL 文件..."
            cat "$DATABASE_DIR/schema.sql" "$DATABASE_DIR/data.sql" > "$DATABASE_DIR/database.sql"
            rm -f "$DATABASE_DIR/schema.sql" "$DATABASE_DIR/data.sql"
            echo "✓ SQL 文件合并完成"
            
            # 4. 压缩
            echo ">>> 压缩 SQL 文件..."
            gzip -9 "$DATABASE_DIR/database.sql"
            
            DB_SIZE=$(du -h "$DATABASE_DIR/database.sql.gz" | cut -f1)
            PG_VERSION=$(pg_dump --version | grep -oP '\d+\.\d+' | head -1)
            
            echo ""
            echo "✓ 数据库导出完成 ($DB_SIZE)"
            echo ""
            echo "导出内容:"
            echo "  - PostgreSQL 版本: $PG_VERSION"
            echo "  - 所有表结构（含索引、约束）"
            echo "  - 所有表数据（排除 ${#TABLES_SCHEMA_ONLY[@]} 个大数据表）"
            echo ""
            echo "排除数据的表（仅结构）:"
            for table in "${TABLES_SCHEMA_ONLY[@]}"; do
                echo "  - $table"
            done
            echo ""
            echo "注意: 部署后需要导入业务数据到上述表"
        else
            echo "⚠ 本地未安装 pg_dump"
            echo "  尝试使用 Docker 中的 PostgreSQL 客户端..."
            
            # 使用 PostgreSQL Docker 镜像导出
            if docker image inspect postgres:16 &> /dev/null || docker pull postgres:16; then
                docker run --rm \
                    --network host \
                    -v "$(pwd)/$DATABASE_DIR:/backup" \
                    -e PGPASSWORD=$DB_PASSWORD \
                    postgres:16 \
                    pg_dump \
                        -h $DB_HOST \
                        -p $DB_PORT \
                        -U $DB_USER \
                        -d $DB_NAME \
                        -f /backup/database.sql \
                        --verbose \
                        --no-owner \
                        --no-acl
                
                if [ $? -eq 0 ]; then
                    echo ">>> 压缩 SQL 文件..."
                    gzip -9 "$DATABASE_DIR/database.sql"
                    DB_SIZE=$(du -h "$DATABASE_DIR/database.sql.gz" | cut -f1)
                    echo "✓ 数据库导出完成 ($DB_SIZE)"
                else
                    echo "✗ 数据库导出失败"
                    rm -f "$DATABASE_DIR/database.sql"*
                fi
            else
                echo "✗ 无法获取 PostgreSQL Docker 镜像"
                echo "  跳过数据库导出"
            fi
        fi
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
- database/ - 数据库完整备份（.dump 格式）
- config/ - 配置文件
- scripts/ - 部署脚本
- docs/ - 部署文档

## 数据库恢复方式

本部署包使用 PostgreSQL 原生的 pg_dump/pg_restore 方式：
- ✅ 简单可靠：一条命令完整恢复
- ✅ 包含所有内容：表结构、数据、索引、约束、序列
- ✅ 无需迁移：不依赖 Alembic 迁移文件
- ✅ 快速高效：比逐表导入快得多

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
