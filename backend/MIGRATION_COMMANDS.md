# Alembic 迁移命令

## 1. 查看当前迁移状态

```bash
cd backend
alembic current
```

## 2. 查看所有 head 版本

```bash
alembic heads
```

## 3. 查看迁移历史

```bash
alembic history
```

## 4. 执行迁移到最新版本

由于我们之前用 stamp 标记了迁移，但实际列没有添加，需要先回退再重新执行：

### 方案 A：回退一个版本再升级（推荐）

```bash
# 回退到 add_system_settings
alembic downgrade add_system_settings

# 再升级到最新
alembic upgrade head
```

### 方案 B：直接升级（如果方案 A 失败）

```bash
# 直接尝试升级
alembic upgrade head
```

### 方案 C：强制重新执行当前版本

```bash
# 先标记回退
alembic stamp add_system_settings

# 再升级
alembic upgrade add_datasource_steps
```

## 5. 如果遇到错误

如果提示列已存在（data_source_id），说明之前手动添加过，但 python_env 没有添加。

可以使用以下命令查看具体错误：

```bash
alembic upgrade head --sql
```

这会显示将要执行的 SQL，但不会真正执行。

## 6. 验证迁移结果

迁移完成后，验证列是否存在：

```bash
python -c "from sqlalchemy import create_engine, inspect; from app.core.config import settings; engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI)); inspector = inspect(engine); cols = [c['name'] for c in inspector.get_columns('calculation_steps')]; print('Columns:', cols); print('Has python_env:', 'python_env' in cols); print('Has data_source_id:', 'data_source_id' in cols)"
```

## 推荐执行顺序

```bash
cd backend

# 1. 查看当前状态
alembic current

# 2. 尝试回退并重新升级
alembic downgrade add_system_settings
alembic upgrade head

# 3. 如果步骤2失败，使用强制方式
alembic stamp add_system_settings
alembic upgrade add_datasource_steps
```

## 注意事项

- 迁移文件中已经添加了检查逻辑，如果列已存在会跳过
- 如果 data_source_id 已存在但 python_env 不存在，迁移会只添加 python_env
- 执行前确保数据库连接正常
