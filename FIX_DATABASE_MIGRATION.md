# 修复数据库迁移问题

> **错误**: relation "model_versions" does not exist

---

## 🔍 问题原因

数据库表 `model_versions` 和 `model_nodes` 还没有创建，需要执行数据库迁移。

---

## ✅ 解决方案

### 方法1: 使用批处理文件（最简单）

双击运行项目根目录的 `run-migration.bat` 文件

### 方法2: 使用Anaconda Prompt

1. 打开Anaconda Prompt（双击 `open-anaconda-prompt.bat`）
2. 执行以下命令：

```bash
cd backend
alembic upgrade head
```

### 方法3: 使用PowerShell脚本

```powershell
.\scripts\db-migrate.ps1
```

---

## 📝 执行步骤

### 1. 打开Anaconda Prompt

双击项目根目录的 `open-anaconda-prompt.bat`

### 2. 激活环境

```bash
conda activate hospital_value
```

### 3. 进入backend目录

```bash
cd backend
```

### 4. 查看当前迁移状态

```bash
alembic current
```

### 5. 执行迁移

```bash
alembic upgrade head
```

### 6. 验证迁移

```bash
alembic current
```

应该显示：
```
g1h2i3j4k5l6 (head)
```

---

## 🔍 验证数据库

### 连接数据库

使用数据库客户端（如DBeaver、pgAdmin）连接到PostgreSQL：

- Host: localhost
- Port: 5432
- Database: hospital_value
- Username: postgres
- Password: postgres

### 检查表是否存在

执行SQL：

```sql
-- 查看所有表
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- 检查model_versions表
SELECT * FROM model_versions;

-- 检查model_nodes表
SELECT * FROM model_nodes;
```

---

## 🎯 预期结果

执行迁移后，应该看到：

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade f0384ea4c792 -> g1h2i3j4k5l6, Add model_versions and model_nodes tables
```

---

## 🔄 重启后端服务

迁移完成后，重启后端服务：

```bash
# 停止当前运行的后端服务（Ctrl+C）

# 重新启动
.\scripts\dev-start-backend.ps1
```

---

## ✅ 测试

1. 访问 http://localhost:3000
2. 登录系统
3. 点击"评估模型管理"
4. 应该能正常显示空列表（不再报错）

---

## 🐛 常见问题

### Q1: 提示"alembic: command not found"

**A**: 确保已激活conda环境：
```bash
conda activate hospital_value
```

### Q2: 提示"No module named 'alembic'"

**A**: 安装alembic：
```bash
pip install alembic
```

### Q3: 迁移执行失败

**A**: 检查数据库连接配置：
- 查看 `backend/.env` 文件
- 确保PostgreSQL服务正在运行
- 确保数据库连接信息正确

### Q4: 提示"Target database is not up to date"

**A**: 先执行之前的迁移：
```bash
alembic upgrade head
```

---

## 📚 相关文档

- [迁移指南](./MIGRATION_GUIDE.md)
- [快速开始](./MODEL_VERSION_QUICKSTART.md)
- [数据库设置](./DATABASE_SETUP_FIXED.md)

---

## 🎉 完成

迁移成功后，模型管理功能就可以正常使用了！

---

**最后更新**: 2025-10-22
