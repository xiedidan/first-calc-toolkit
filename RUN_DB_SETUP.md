# 运行数据库设置

## ⚠️ 重要提示

数据库设置脚本位于项目根目录的 `scripts` 文件夹中。

## 📍 当前位置

你现在在：`C:\project\first-calc-toolkit\backend`

脚本位于：`C:\project\first-calc-toolkit\scripts`

## ✅ 正确的运行方式

### 方式1：回到项目根目录运行（推荐）

```powershell
# 回到项目根目录
cd C:\project\first-calc-toolkit

# 或者
cd ..

# 然后运行脚本
.\scripts\db-setup.ps1
```

### 方式2：使用完整路径

```powershell
# 在backend目录下运行
..\scripts\db-setup.ps1
```

### 方式3：使用绝对路径

```powershell
C:\project\first-calc-toolkit\scripts\db-setup.ps1
```

## 🚀 完整步骤

```powershell
# 1. 回到项目根目录
cd C:\project\first-calc-toolkit

# 2. 确保Docker服务运行
docker-compose -f docker-compose.dev.yml ps

# 3. 如果没运行，启动Docker服务
docker-compose -f docker-compose.dev.yml up -d

# 4. 运行数据库设置
.\scripts\db-setup.ps1
```

## 📋 脚本说明

`db-setup.ps1` 会自动执行：

1. **检查PostgreSQL是否运行**
2. **运行 db-init.ps1** - 创建数据库表（Alembic迁移）
3. **运行 db-seed.ps1** - 插入初始数据（权限、角色、管理员用户）

## 🎯 预期结果

成功后你会看到：

```
========================================
Database setup complete!
========================================

Default admin credentials:
  Username: admin
  Password: admin123

Please change the password after first login!
```

## 🔍 验证数据库

```powershell
# 连接到PostgreSQL
docker exec -it hospital_postgres_dev psql -U admin -d hospital_value

# 查看所有表
\dt

# 查看用户
SELECT * FROM users;

# 查看角色
SELECT * FROM roles;

# 查看权限
SELECT * FROM permissions;

# 退出
\q
```

## ❓ 常见问题

### Q: 提示"PostgreSQL container not running"

**A**: 先启动Docker服务：
```powershell
docker-compose -f docker-compose.dev.yml up -d
```

### Q: 提示"Conda environment not found"

**A**: 先设置Conda环境：
```powershell
.\scripts\setup-conda-env.ps1
```

### Q: 提示"Database already initialized"

**A**: 数据库已经初始化过了，可以直接使用。如果需要重新初始化：
```powershell
# 删除所有表（谨慎操作！）
docker exec -it hospital_postgres_dev psql -U admin -d hospital_value -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# 然后重新运行设置
.\scripts\db-setup.ps1
```

## 📝 下一步

数据库设置完成后，你可以：

1. 启动后端服务测试API
2. 开始实现认证API
3. 开始实现前端登录页面

查看 **AUTH_MODULE_PROGRESS.md** 了解详细的开发进度。
