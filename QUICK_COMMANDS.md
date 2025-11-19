# 快速命令参考

## 📍 导航

```powershell
# 项目根目录
cd C:\project\first-calc-toolkit

# 后端目录
cd backend

# 前端目录
cd frontend
```

## 🗄️ 数据库命令

### 从项目根目录

```powershell
# 完整设置（创建表+插入数据）
.\scripts\db-setup.ps1

# 只创建表
.\scripts\db-init.ps1

# 只插入数据
.\scripts\db-seed.ps1

# 测试连接
.\scripts\test-connection.ps1
```

### 从backend目录

```powershell
# 完整设置
.\setup-db.ps1

# 或使用相对路径
..\scripts\db-setup.ps1
```

## 🐳 Docker命令

```powershell
# 启动服务
docker-compose -f docker-compose.dev.yml up -d

# 查看状态
docker-compose -f docker-compose.dev.yml ps

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f

# 停止服务
docker-compose -f docker-compose.dev.yml down

# 连接PostgreSQL
docker exec -it hospital_postgres_dev psql -U admin -d hospital_value

# 连接Redis
docker exec -it hospital_redis_dev redis-cli
```

## 🚀 启动服务

```powershell
# 一键启动所有服务
.\scripts\dev-start-all.ps1

# 单独启动后端
.\scripts\dev-start-backend.ps1

# 单独启动Celery
.\scripts\dev-start-celery.ps1

# 单独启动前端
.\scripts\dev-start-frontend.ps1

# 停止所有服务
.\scripts\dev-stop-all.ps1
```

## 🔧 环境设置

```powershell
# 检查环境
.\scripts\check-environment.ps1

# 设置Conda环境
.\scripts\setup-conda-env.ps1

# 安装前端依赖
cd frontend
npm install
cd ..
```

## 📊 数据库查询

### 在psql中

```sql
-- 查看所有表
\dt

-- 查看用户
SELECT * FROM users;

-- 查看角色
SELECT * FROM roles;

-- 查看权限
SELECT * FROM permissions;

-- 查看用户的角色
SELECT u.username, r.name as role_name
FROM users u
JOIN user_roles ur ON u.id = ur.user_id
JOIN roles r ON ur.role_id = r.id;

-- 查看角色的权限
SELECT r.name as role_name, p.name as permission_name
FROM roles r
JOIN role_permissions rp ON r.id = rp.role_id
JOIN permissions p ON rp.permission_id = p.id
ORDER BY r.name, p.name;

-- 退出
\q
```

## 🔐 默认登录信息

```
Username: admin
Password: admin123
```

## 🌐 访问地址

```
Frontend:     http://localhost:3000
Backend API:  http://localhost:8000/docs
Backend Health: http://localhost:8000/health
ReDoc:        http://localhost:8000/redoc
```

## 📝 常用文件位置

```
项目根目录/
├── scripts/              # 所有PowerShell脚本
├── backend/
│   ├── app/             # 应用代码
│   ├── alembic/         # 数据库迁移
│   ├── scripts/         # Python脚本
│   └── setup-db.ps1     # 数据库设置快捷方式
├── frontend/
│   └── src/             # 前端代码
└── 文档/
    ├── START_HERE.md
    ├── QUICK_COMMANDS.md (本文件)
    ├── AUTH_MODULE_PROGRESS.md
    └── RUN_DB_SETUP.md
```

## 🆘 遇到问题？

1. **Docker未运行**: 启动Docker Desktop
2. **Conda未找到**: 使用Anaconda PowerShell Prompt
3. **端口被占用**: 查看 `netstat -ano | findstr :8000`
4. **数据库连接失败**: 检查Docker服务是否运行

## 📚 详细文档

- **START_HERE.md** - 快速开始
- **RUN_DB_SETUP.md** - 数据库设置详解
- **AUTH_MODULE_PROGRESS.md** - 认证模块进度
- **DEVELOPMENT_PLAN.md** - 开发计划

---

**提示**: 将此文件保存为书签，方便随时查看！
