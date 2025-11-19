# 快速启动指南

## 🎯 目标

本指南帮助你在5分钟内启动开发环境。

## ✅ 前置条件检查

在开始之前，请确保已安装：

- [x] Windows 10/11
- [x] WSL2 + Ubuntu
- [x] Docker Desktop（已启用WSL2集成）
- [x] Anaconda
- [x] Node.js 18+

### 验证环境

在PowerShell中运行：

```powershell
# 验证WSL2
wsl --list --verbose

# 验证Docker
docker --version
docker-compose --version

# 验证Conda
conda --version

# 验证Node.js
node --version
npm --version
```

## 🚀 三步启动

### 步骤1: 设置Python环境（首次运行）

```powershell
# 在项目根目录运行
.\scripts\setup-conda-env.ps1
```

这将创建名为 `hospital-backend` 的Conda环境并安装所有Python依赖。

### 步骤2: 安装前端依赖（首次运行）

```powershell
cd frontend
npm install
cd ..
```

### 步骤3: 启动所有服务

```powershell
# 一键启动所有服务
.\scripts\dev-start-all.ps1
```

这个脚本会：
1. 启动PostgreSQL和Redis容器
2. 在新窗口中启动后端服务
3. 在新窗口中启动Celery Worker
4. 在新窗口中启动前端服务

## 🌐 访问应用

启动完成后，打开浏览器访问：

- **前端**: http://localhost:3000
- **后端API文档**: http://localhost:8000/docs
- **后端ReDoc**: http://localhost:8000/redoc

## 🛑 停止服务

```powershell
# 停止所有服务
.\scripts\dev-stop-all.ps1
```

或者直接关闭各个PowerShell窗口。

## 📝 日常开发流程

### 启动开发环境

```powershell
# 方式1: 一键启动（推荐）
.\scripts\dev-start-all.ps1

# 方式2: 分别启动
# 1. 启动数据库和Redis
docker-compose -f docker-compose.dev.yml up -d

# 2. 启动后端（新终端）
.\scripts\dev-start-backend.ps1

# 3. 启动Celery（新终端）
.\scripts\dev-start-celery.ps1

# 4. 启动前端（新终端）
.\scripts\dev-start-frontend.ps1
```

### 查看服务状态

```powershell
# 查看Docker容器状态
docker-compose -f docker-compose.dev.yml ps

# 查看容器日志
docker-compose -f docker-compose.dev.yml logs -f
```

### 停止开发环境

```powershell
# 停止所有服务
.\scripts\dev-stop-all.ps1
```

## 🔧 常见问题

### Q1: 端口被占用怎么办？

**问题**: 启动时提示端口5432、6379、8000或3000被占用

**解决方案**:
```powershell
# 查看端口占用
netstat -ano | findstr :5432

# 结束占用进程
taskkill /PID <PID> /F
```

### Q2: Docker容器无法启动

**问题**: PostgreSQL或Redis容器启动失败

**解决方案**:
```powershell
# 检查Docker Desktop是否运行
# 重启Docker Desktop

# 清理并重新启动
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

### Q3: Conda环境激活失败

**问题**: 无法激活hospital-backend环境

**解决方案**:
```powershell
# 初始化Conda（首次使用）
conda init powershell

# 重启PowerShell后再试
conda activate hospital-backend
```

### Q4: 前端依赖安装失败

**问题**: npm install报错

**解决方案**:
```powershell
# 清理缓存
cd frontend
npm cache clean --force

# 删除node_modules
Remove-Item -Recurse -Force node_modules

# 重新安装
npm install
```

### Q5: 后端无法连接数据库

**问题**: 后端启动时报数据库连接错误

**解决方案**:
```powershell
# 1. 确保PostgreSQL容器正在运行
docker ps | findstr postgres

# 2. 检查.env.dev配置
# 确保DATABASE_URL=postgresql://admin:admin123@localhost:5432/hospital_value

# 3. 测试数据库连接
docker exec -it hospital_postgres_dev psql -U admin -d hospital_value
```

## 📚 下一步

环境启动成功后，你可以：

1. 查看[API设计文档](./API设计文档.md)了解接口定义
2. 查看[系统设计文档](./系统设计文档.md)了解架构设计
3. 开始开发具体功能模块

## 💡 开发技巧

### 使用VS Code调试

1. 打开VS Code
2. 按F5选择"Python: FastAPI"或"Python: Celery Worker"
3. 设置断点进行调试

### 热重载

- **后端**: 代码修改后自动重载（uvicorn --reload）
- **前端**: 代码修改后自动刷新（Vite HMR）
- **Celery**: 需要手动重启

### 查看日志

```powershell
# Docker服务日志
docker-compose -f docker-compose.dev.yml logs -f postgres
docker-compose -f docker-compose.dev.yml logs -f redis

# 后端日志：在启动后端的PowerShell窗口查看
# 前端日志：在启动前端的PowerShell窗口查看
# Celery日志：在启动Celery的PowerShell窗口查看
```

## 🎉 完成！

现在你已经成功启动了开发环境，可以开始开发了！

如有问题，请查看[部署文档](./部署文档.md)获取更详细的信息。
