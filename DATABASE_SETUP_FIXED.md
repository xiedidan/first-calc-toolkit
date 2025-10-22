# 数据库设置问题已修复

## ✅ 已修复的问题

### 问题1：脚本不返回原始目录 ✅
- **修复**: 所有脚本现在都会保存并返回原始目录
- **影响**: `db-init.ps1`, `db-seed.ps1`, `db-setup.ps1`

### 问题2：环境变量缺失 ✅
- **修复**: `init_data.py`现在会自动设置默认环境变量
- **影响**: 不再需要`.env`文件就能运行初始化脚本

## 🚀 现在可以运行

### 方式1：完整设置（推荐）

```powershell
.\scripts\db-setup.ps1
```

这会：
1. 创建数据库表（如果还没创建）
2. 插入初始数据（权限、角色、管理员用户）

### 方式2：只插入数据

如果表已经创建，只需要插入数据：

```powershell
.\scripts\db-seed.ps1
```

### 方式3：使用批处理文件

双击：
```
seed-database.bat
```

## 📊 预期结果

成功后你会看到：

```
========================================
Initialize Database with Default Data
========================================

Creating database tables...
✓ Tables created

Initializing permissions...
✓ Created 21 permissions

Initializing roles...
✓ Created 5 roles

Initializing admin user...
✓ Created admin user
  Username: admin
  Password: admin123
  Please change the password after first login!

========================================
Initialization complete!
========================================

You can now login with:
  Username: admin
  Password: admin123
```

## 🔍 验证数据库

```powershell
# 连接到PostgreSQL
docker exec -it hospital_postgres_dev psql -U admin -d hospital_value

# 查看用户
SELECT * FROM users;

# 查看角色
SELECT * FROM roles;

# 查看权限数量
SELECT COUNT(*) FROM permissions;

# 退出
\q
```

## 📝 初始数据详情

### 权限（21个）
- 用户管理：create, read, update, delete
- 角色管理：create, read, update, delete
- 模型管理：create, read, update, delete
- 科室管理：create, read, update, delete
- 计算管理：create, read, cancel
- 结果管理：read, export

### 角色（5个）
1. **admin** - 系统管理员（所有权限）
2. **model_designer** - 模型设计师
3. **data_analyst** - 数据分析师
4. **business_expert** - 业务专家
5. **dept_manager** - 科室管理者

### 默认用户（1个）
- **用户名**: admin
- **密码**: admin123
- **角色**: admin（系统管理员）
- **状态**: active

## 🎯 下一步

数据库设置完成后，你可以：

1. **启动后端服务**
   ```powershell
   .\scripts\dev-start-backend.ps1
   ```

2. **访问API文档**
   - http://localhost:8000/docs

3. **测试登录**
   - 用户名：admin
   - 密码：admin123

4. **开始实现API**
   - 查看 `AUTH_MODULE_PROGRESS.md` 了解下一步开发任务

## ⚠️ 重要提示

### 如果需要重新初始化数据库

```powershell
# 1. 删除所有数据（谨慎！）
docker exec -it hospital_postgres_dev psql -U admin -d hospital_value -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# 2. 重新运行设置
.\scripts\db-setup.ps1
```

### 如果数据已存在

脚本会检测到已有数据并跳过：
```
Database already initialized!
Found 1 existing users
```

这是正常的，说明数据库已经设置好了。

## ✨ 所有问题已解决！

现在你可以顺利运行数据库设置脚本了。试试运行：

```powershell
.\scripts\db-seed.ps1
```

或者

```powershell
.\scripts\db-setup.ps1
```

祝开发顺利！🚀
