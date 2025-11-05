# 快速修复指南

## 如果看到迁移错误

运行以下命令修复：

```bash
cd backend
python fix_charge_items_migration.py
alembic upgrade head
```

或者直接运行：

```bash
migrate-charge-items.bat
```

## 如果 Python 脚本失败

在 PostgreSQL 中执行 `backend/fix_migration.sql` 文件：

```bash
psql -U your_username -d your_database -f backend/fix_migration.sql
```

然后重新运行迁移：

```bash
cd backend
alembic upgrade head
```

## 验证

```bash
cd backend
python test_charge_item_hospital.py
```

完成！
