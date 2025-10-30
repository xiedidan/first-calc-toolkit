# 医院科室业务价值评估工具 - 离线部署包 v1.0.0

## 部署包内容

- images/ - Docker镜像文件（约500MB）
- database/ - 数据库数据文件
- config/ - 配置文件
- scripts/ - 部署脚本
- docs/ - 部署文档

## 快速开始

### 1. 解压部署包

```bash
tar -xzf hospital-value-toolkit-offline-v1.0.0.tar.gz
cd offline-package
```

### 2. 导入Docker镜像

```bash
bash scripts/load-images.sh
```

### 3. 配置环境

```bash
cp config/.env.offline.template .env
vi .env  # 编辑数据库连接信息
```

### 4. 初始化数据库

```bash
bash scripts/init-database.sh
```

### 5. 启动服务

```bash
docker-compose -f config/docker-compose.offline.yml up -d
```

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
