# 修复收费项目迁移问题

## 问题描述

如果在运行 `alembic upgrade head` 时遇到以下错误：

```
sqlalchemy.exc.InternalError: (psycopg2.errors.InFailedSqlTransaction) 
current transaction is aborted, commands ignored until end of transaction block
```

这是因为之前的迁移操作失败，导致数据库事务处于失败状态。

## 解决方案

### 方法一：使用修复脚本（推荐）

运行修复脚本自动清理失败的迁移状态：

```bash
cd backend
python fix_charge_items_migration.py
```

然后重新运行迁移：

```bash
alembic upgrade head
```

### 方法二：使用批处理脚本

直接运行批处理脚本，它会自动执行修复和迁移：

```bash
migrate-charge-items.bat
```

### 方法三：手动修复（如果脚本失败）

如果自动修复脚本失败，可以手动执行以下 SQL：

```sql
-- 1. 删除可能存在的约束和索引
ALTER TABLE charge_items DROP CONSTRAINT IF EXISTS fk_charge_items_hospital_id;
DROP INDEX IF EXISTS ix_charge_items_hospital_id;
ALTER TABLE charge_items DROP CONSTRAINT IF EXISTS uq_hospital_item_code;

-- 2. 删除 hospital_id 列（如果存在）
ALTER TABLE charge_items DROP COLUMN IF EXISTS hospital_id;

-- 3. 回滚 alembic 版本
UPDATE alembic_version SET version_num = '20251103_hospital';
```

然后重新运行迁移：

```bash
cd backend
alembic upgrade head
```

## 验证修复

修复完成后，运行测试脚本验证：

```bash
cd backend
python test_charge_item_hospital.py
```

## 常见问题

### Q: 为什么会出现这个错误？

A: 这通常是因为：
1. 之前的迁移操作部分完成但失败了
2. 数据库事务没有正确提交或回滚
3. 约束或索引创建失败

### Q: 修复脚本会删除数据吗？

A: 不会。修复脚本只是清理失败的迁移状态，不会删除 charge_items 表中的数据。

### Q: 如果修复后还是失败怎么办？

A: 请检查：
1. 数据库连接是否正常
2. 是否有足够的权限执行 DDL 操作
3. 查看详细的错误日志
4. 确认 hospitals 表是否存在且有数据

如果问题持续，可以联系技术支持。
