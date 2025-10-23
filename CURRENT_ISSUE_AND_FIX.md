# 当前问题和解决方案

> **问题**: 前端访问模型管理页面时报错 "relation model_versions does not exist"

---

## 🔍 问题分析

### 错误信息
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedTable) 
relation "model_versions" does not exist
```

### 原因
数据库表 `model_versions` 和 `model_nodes` 还没有创建。这是因为：
1. 我们创建了新的数据模型
2. 创建了数据库迁移脚本
3. **但还没有执行迁移**

---

## ✅ 解决方案

### 最简单的方法（推荐）

#### 1. 打开Anaconda Prompt
双击 `open-anaconda-prompt.bat`

#### 2. 执行迁移
```bash
cd backend
alembic upgrade head
```

#### 3. 重启后端
在后端服务窗口按 `Ctrl+C`，然后：
```bash
.\scripts\dev-start-backend.ps1
```

#### 4. 刷新浏览器
问题解决！✅

---

## 📚 详细文档

如果上述方法不行，请查看：

1. **[如何执行迁移](./HOW_TO_MIGRATE.md)** - 图文详解
2. **[执行迁移步骤.txt](./执行迁移步骤.txt)** - 简明步骤
3. **[修复指南](./FIX_DATABASE_MIGRATION.md)** - 完整说明
4. **[迁移指南](./MIGRATION_GUIDE.md)** - 技术文档

---

## 🎯 快速参考

### 检查迁移状态
```bash
cd backend
alembic current
```

### 查看迁移历史
```bash
alembic history
```

### 执行迁移
```bash
alembic upgrade head
```

### 回滚迁移
```bash
alembic downgrade -1
```

---

## 🔧 备用方案

### 方案1: 使用Python直接执行
```bash
cd backend
python -m alembic upgrade head
```

### 方案2: 使用批处理文件
双击 `migrate-simple.bat`

### 方案3: 手动创建表
如果迁移一直失败，可以手动执行SQL：
```sql
-- 查看迁移脚本
-- backend/alembic/versions/g1h2i3j4k5l6_*.py
```

---

## ⚠️ 注意事项

1. **必须先执行迁移**才能使用模型管理功能
2. **迁移只需执行一次**
3. **迁移后需要重启后端服务**
4. **确保PostgreSQL正在运行**

---

## 🎉 预期结果

### 迁移成功后
```
INFO  [alembic.runtime.migration] Running upgrade f0384ea4c792 -> g1h2i3j4k5l6, Add model_versions and model_nodes tables
```

### 前端正常显示
- 能访问"评估模型管理"页面
- 显示空列表（不报错）
- 能创建新版本

---

## 📞 获取帮助

如果还有问题：
1. 查看 [HOW_TO_MIGRATE.md](./HOW_TO_MIGRATE.md)
2. 查看 [FIX_DATABASE_MIGRATION.md](./FIX_DATABASE_MIGRATION.md)
3. 检查数据库连接配置（backend/.env）
4. 确认PostgreSQL服务状态

---

**解决时间**: 约2分钟  
**难度**: ⭐☆☆☆☆  
**最后更新**: 2025-10-22
