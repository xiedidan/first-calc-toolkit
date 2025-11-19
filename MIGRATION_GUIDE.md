# 数据库迁移指南

> 如何执行模型管理模块的数据库迁移

---

## 📋 迁移内容

本次迁移将创建以下数据库表：
- `model_versions` - 模型版本表
- `model_nodes` - 模型节点表

---

## 🚀 执行迁移

### 方法1: 使用Anaconda Prompt（推荐）

```bash
# 1. 打开Anaconda Prompt
# 可以双击项目根目录的 open-anaconda-prompt.bat

# 2. 激活环境
conda activate hospital_value

# 3. 进入backend目录
cd backend

# 4. 查看当前迁移状态
alembic current

# 5. 查看待执行的迁移
alembic history

# 6. 执行迁移
alembic upgrade head

# 7. 验证迁移结果
alembic current
```

### 方法2: 使用PowerShell脚本

```powershell
# 在项目根目录执行
.\scripts\db-migrate.ps1
```

---

## 🔍 验证迁移

### 检查数据库表

连接到PostgreSQL数据库，执行以下SQL：

```sql
-- 查看所有表
\dt

-- 查看model_versions表结构
\d model_versions

-- 查看model_nodes表结构
\d model_nodes

-- 查看外键约束
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
  AND tc.table_name IN ('model_versions', 'model_nodes');
```

### 预期结果

应该看到以下表：
- ✅ `model_versions`
- ✅ `model_nodes`

以及相关的索引和外键约束。

---

## 🔄 回滚迁移

如果需要回滚迁移：

```bash
# 回滚到上一个版本
alembic downgrade -1

# 回滚到指定版本
alembic downgrade f0384ea4c792

# 回滚所有迁移
alembic downgrade base
```

---

## ⚠️ 常见问题

### Q1: 提示"No module named 'alembic'"

**A**: 确保已激活conda环境
```bash
conda activate hospital_value
pip install alembic
```

### Q2: 提示"Can't locate revision identified by 'head'"

**A**: 检查alembic版本表
```sql
SELECT * FROM alembic_version;
```

如果表不存在或为空，执行：
```bash
alembic stamp head
```

### Q3: 提示"Target database is not up to date"

**A**: 先执行之前的迁移
```bash
alembic upgrade head
```

### Q4: 迁移执行失败

**A**: 检查错误信息，常见原因：
1. 数据库连接失败 - 检查 `.env` 配置
2. 表已存在 - 可能已经执行过迁移
3. 权限不足 - 检查数据库用户权限

---

## 📝 迁移文件

本次迁移文件位置：
```
backend/alembic/versions/g1h2i3j4k5l6_add_model_version_and_node_tables.py
```

迁移内容：
- 创建 `model_versions` 表
- 创建 `model_nodes` 表
- 添加索引
- 添加外键约束

---

## 🔗 相关文档

- [模型版本管理文档](./MODEL_VERSION_COMPLETED.md)
- [快速开始指南](./MODEL_VERSION_QUICKSTART.md)
- [数据库设计](./系统设计文档.md#4-数据库设计)

---

## 📞 获取帮助

如果遇到问题：
1. 查看本文档的常见问题部分
2. 查看Alembic日志输出
3. 检查数据库连接配置
4. 联系项目负责人

---

**最后更新**: 2025-10-22
