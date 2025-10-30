# ============================================
# 医院科室业务价值评估工具 - 离线部署包构建脚本
# 适用于: Windows 11 + Docker Desktop
# ============================================

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  离线部署包构建工具" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Docker是否运行
Write-Host ">>> 检查Docker环境..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "✓ Docker运行正常" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker未运行，请启动Docker Desktop" -ForegroundColor Red
    exit 1
}

# 设置版本号
$VERSION = "1.0.0"

Write-Host ">>> 构建版本: $VERSION" -ForegroundColor Cyan
Write-Host ""

# 创建输出目录
$PACKAGE_DIR = "offline-package"
$IMAGES_DIR = "$PACKAGE_DIR\images"
$DATABASE_DIR = "$PACKAGE_DIR\database"
$CONFIG_DIR = "$PACKAGE_DIR\config"
$SCRIPTS_DIR = "$PACKAGE_DIR\scripts"
$DOCS_DIR = "$PACKAGE_DIR\docs"

Write-Host ">>> 创建目录结构..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $IMAGES_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $DATABASE_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $CONFIG_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $SCRIPTS_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $DOCS_DIR | Out-Null
Write-Host "✓ 目录创建完成" -ForegroundColor Green
Write-Host ""

# 步骤1: 构建Docker镜像
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  步骤 1/5: 构建Docker镜像" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan


# 构建后端镜像
Write-Host ">>> 构建后端镜像..." -ForegroundColor Yellow
docker build --platform linux/amd64 -t hospital-backend:latest ./backend
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ 后端镜像构建失败" -ForegroundColor Red
    exit 1
}
Write-Host "✓ 后端镜像构建完成" -ForegroundColor Green

# 构建前端镜像
Write-Host ">>> 构建前端镜像..." -ForegroundColor Yellow
docker build --platform linux/amd64 -t hospital-frontend:latest ./frontend
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ 前端镜像构建失败" -ForegroundColor Red
    exit 1
}
Write-Host "✓ 前端镜像构建完成" -ForegroundColor Green

# 拉取Redis镜像
Write-Host ">>> 拉取Redis镜像..." -ForegroundColor Yellow
docker pull redis:7-alpine
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Redis镜像拉取失败" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Redis镜像拉取完成" -ForegroundColor Green
Write-Host ""

# 步骤2: 导出Docker镜像
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  步骤 2/5: 导出Docker镜像" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 导出后端镜像
Write-Host ">>> 导出后端镜像..." -ForegroundColor Yellow
docker save hospital-backend:latest | gzip > "$IMAGES_DIR\backend.tar.gz"
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ 后端镜像导出失败" -ForegroundColor Red
    exit 1
}
$backendSize = (Get-Item "$IMAGES_DIR\backend.tar.gz").Length / 1MB
Write-Host "✓ 后端镜像导出完成 ($([math]::Round($backendSize, 2)) MB)" -ForegroundColor Green

# 导出前端镜像
Write-Host ">>> 导出前端镜像..." -ForegroundColor Yellow
docker save hospital-frontend:latest | gzip > "$IMAGES_DIR\frontend.tar.gz"
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ 前端镜像导出失败" -ForegroundColor Red
    exit 1
}
$frontendSize = (Get-Item "$IMAGES_DIR\frontend.tar.gz").Length / 1MB
Write-Host "✓ 前端镜像导出完成 ($([math]::Round($frontendSize, 2)) MB)" -ForegroundColor Green

# 导出Redis镜像
Write-Host ">>> 导出Redis镜像..." -ForegroundColor Yellow
docker save redis:7-alpine | gzip > "$IMAGES_DIR\redis.tar.gz"
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Redis镜像导出失败" -ForegroundColor Red
    exit 1
}
$redisSize = (Get-Item "$IMAGES_DIR\redis.tar.gz").Length / 1MB
Write-Host "✓ Redis镜像导出完成 ($([math]::Round($redisSize, 2)) MB)" -ForegroundColor Green
Write-Host ""

# 步骤3: 导出数据库数据
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  步骤 3/5: 导出数据库数据" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "⚠ 数据库导出需要手动执行" -ForegroundColor Yellow
Write-Host "  如果需要导出数据库，请手动执行以下命令:" -ForegroundColor Gray
Write-Host "  pg_dump -h localhost -p 5432 -U admin -d hospital_value --clean --if-exists --no-owner --no-privileges -f $DATABASE_DIR\hospital_value.sql" -ForegroundColor Gray
Write-Host "  gzip $DATABASE_DIR\hospital_value.sql" -ForegroundColor Gray
Write-Host ""

# 步骤4: 复制配置文件和脚本
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  步骤 4/5: 打包配置文件和脚本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 复制Docker Compose配置
Write-Host ">>> 复制配置文件..." -ForegroundColor Yellow
if (Test-Path "docker-compose.offline.yml") {
    Copy-Item "docker-compose.offline.yml" "$CONFIG_DIR\" -Force
    Write-Host "✓ 复制 docker-compose.offline.yml" -ForegroundColor Green
}

# 复制环境变量模板
if (Test-Path "backend\.env.offline.template") {
    Copy-Item "backend\.env.offline.template" "$CONFIG_DIR\" -Force
    Write-Host "✓ 复制 .env.offline.template" -ForegroundColor Green
}

# 复制部署脚本
Write-Host ">>> 复制部署脚本..." -ForegroundColor Yellow
if (Test-Path "scripts\deploy-offline.sh") {
    Copy-Item "scripts\deploy-offline.sh" "$SCRIPTS_DIR\" -Force
    Write-Host "✓ 复制 deploy-offline.sh" -ForegroundColor Green
}
if (Test-Path "scripts\load-images.sh") {
    Copy-Item "scripts\load-images.sh" "$SCRIPTS_DIR\" -Force
    Write-Host "✓ 复制 load-images.sh" -ForegroundColor Green
}
if (Test-Path "scripts\init-database.sh") {
    Copy-Item "scripts\init-database.sh" "$SCRIPTS_DIR\" -Force
    Write-Host "✓ 复制 init-database.sh" -ForegroundColor Green
}
if (Test-Path "scripts\check-prerequisites.sh") {
    Copy-Item "scripts\check-prerequisites.sh" "$SCRIPTS_DIR\" -Force
    Write-Host "✓ 复制 check-prerequisites.sh" -ForegroundColor Green
}

# 复制文档
Write-Host ">>> 复制文档..." -ForegroundColor Yellow
if (Test-Path "离线部署方案.md") {
    Copy-Item "离线部署方案.md" "$DOCS_DIR\" -Force
    Write-Host "✓ 复制 离线部署方案.md" -ForegroundColor Green
}
if (Test-Path "OFFLINE_DEPLOYMENT_GUIDE.md") {
    Copy-Item "OFFLINE_DEPLOYMENT_GUIDE.md" "$DOCS_DIR\" -Force
    Write-Host "✓ 复制 OFFLINE_DEPLOYMENT_GUIDE.md" -ForegroundColor Green
}

# 创建README
Write-Host ">>> 创建README..." -ForegroundColor Yellow
$readmeContent = @"
# 医院科室业务价值评估工具 - 离线部署包 v$VERSION

## 部署包内容

- images/ - Docker镜像文件（约500MB）
- database/ - 数据库数据文件
- config/ - 配置文件
- scripts/ - 部署脚本
- docs/ - 部署文档

## 快速开始

### 1. 解压部署包

bash
tar -xzf hospital-value-toolkit-offline-v$VERSION.tar.gz
cd offline-package


### 2. 导入Docker镜像

bash
bash scripts/load-images.sh


### 3. 配置环境

bash
cp config/.env.offline.template .env
vi .env


### 4. 初始化数据库

bash
bash scripts/init-database.sh


### 5. 启动服务

bash
docker-compose -f config/docker-compose.offline.yml up -d


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
"@

$readmeContent | Out-File -FilePath "$PACKAGE_DIR\README.md" -Encoding UTF8
Write-Host "✓ 创建 README.md" -ForegroundColor Green
Write-Host ""

# 步骤5: 生成最终部署包
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  步骤 5/5: 生成最终部署包" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$PACKAGE_NAME = "hospital-value-toolkit-offline-v$VERSION.tar.gz"

Write-Host ">>> 打包文件..." -ForegroundColor Yellow
Write-Host "⚠ 需要手动打包" -ForegroundColor Yellow
Write-Host "  请执行以下命令之一:" -ForegroundColor Gray
Write-Host "  1. 使用WSL: wsl tar -czf $PACKAGE_NAME $PACKAGE_DIR" -ForegroundColor Gray
Write-Host "  2. 使用Git Bash: tar -czf $PACKAGE_NAME $PACKAGE_DIR" -ForegroundColor Gray
Write-Host "  3. 使用7-Zip等工具手动压缩 $PACKAGE_DIR 目录" -ForegroundColor Gray
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  构建完成！" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "已创建目录: $PACKAGE_DIR" -ForegroundColor Green
Write-Host "包含以下内容:" -ForegroundColor Gray
Write-Host "  - Docker镜像文件 (images/)" -ForegroundColor Gray
Write-Host "  - 配置文件 (config/)" -ForegroundColor Gray
Write-Host "  - 部署脚本 (scripts/)" -ForegroundColor Gray
Write-Host "  - 文档 (docs/)" -ForegroundColor Gray
Write-Host ""
Write-Host "下一步:" -ForegroundColor Yellow
Write-Host "1. 如需导出数据库，请手动执行pg_dump命令" -ForegroundColor Gray
Write-Host "2. 打包 $PACKAGE_DIR 目录为 $PACKAGE_NAME" -ForegroundColor Gray
Write-Host "3. 将部署包传输到目标Linux服务器" -ForegroundColor Gray
Write-Host "4. 在目标服务器上解压并执行部署脚本" -ForegroundColor Gray
Write-Host ""
