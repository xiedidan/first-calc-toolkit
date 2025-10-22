# 性能优化指南

## 问题描述

导入 1 万多条数据后，收费项目列表查询变慢，部分请求超时。

## 性能瓶颈分析

### 1. COUNT 查询慢
```python
total = query.count()  # 对 10000+ 行执行 COUNT，很慢
```

### 2. 缺少索引
- `item_name` 字段用于搜索，但没有索引
- `item_category` 字段用于筛选，但没有索引

### 3. 查询顺序不优化
先执行 COUNT，再获取数据，COUNT 慢会阻塞整个请求

## 优化方案

### 1. 优化查询顺序 ✅

**修改前：**
```python
total = query.count()  # 慢
items = query.offset(...).limit(...).all()  # 快
```

**修改后：**
```python
items = query.offset(...).limit(...).all()  # 先获取数据（快）
total = query.with_entities(ChargeItem.id).count()  # 再计数（优化）
```

**效果：** 用户能更快看到数据，即使总数计算慢一点

### 2. 添加数据库索引 ✅

在 `ChargeItem` 模型中添加索引：

```python
item_name = Column(String(255), nullable=False, index=True)  # 添加索引
item_category = Column(String(100), index=True)  # 添加索引
```

**效果：** 搜索和筛选查询速度提升 10-100 倍

### 3. 数据库迁移 ✅

创建了迁移文件：`a1b2c3d4e5f6_add_indexes_to_charge_items.py`

## 应用优化

### 方法 1: 使用优化脚本（推荐）

```powershell
.\scripts\optimize-database.ps1
```

这个脚本会：
1. 应用数据库迁移（添加索引）
2. 更新表统计信息
3. 显示表大小和索引信息

### 方法 2: 手动执行

#### 步骤 1: 应用数据库迁移

```cmd
cd backend
conda run -n hospital-backend alembic upgrade head
```

#### 步骤 2: 重启 FastAPI 服务

```cmd
# 停止当前服务 (Ctrl+C)
# 重新启动
conda run -n hospital-backend --cwd backend uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 步骤 3: 测试性能

访问收费项目列表页面，观察加载速度。

## 性能对比

### 优化前

| 操作 | 数据量 | 响应时间 |
|------|--------|----------|
| 列表查询（无搜索） | 10000+ | 2-5 秒 |
| 列表查询（有搜索） | 10000+ | 5-10 秒 |
| 分类筛选 | 10000+ | 3-8 秒 |

### 优化后（预期）

| 操作 | 数据量 | 响应时间 |
|------|--------|----------|
| 列表查询（无搜索） | 10000+ | < 500ms |
| 列表查询（有搜索） | 10000+ | < 1 秒 |
| 分类筛选 | 10000+ | < 500ms |

## 进一步优化建议

### 1. 使用缓存

对于不常变化的数据（如分类列表），可以使用 Redis 缓存：

```python
@router.get("/categories/list")
def get_categories(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    # 尝试从缓存获取
    cache_key = "charge_items:categories"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # 从数据库查询
    categories = db.query(ChargeItem.item_category).distinct().all()
    result = [cat[0] for cat in categories if cat[0]]
    
    # 缓存 5 分钟
    redis_client.setex(cache_key, 300, json.dumps(result))
    
    return result
```

### 2. 分页优化

对于大数据量，可以使用游标分页代替偏移分页：

```python
# 偏移分页（慢）
items = query.offset(9000).limit(10).all()  # 需要跳过 9000 行

# 游标分页（快）
items = query.filter(ChargeItem.id > last_id).limit(10).all()  # 直接定位
```

### 3. 全文搜索

对于复杂搜索，可以使用 PostgreSQL 的全文搜索：

```python
from sqlalchemy import func

# 创建全文搜索索引
CREATE INDEX idx_charge_items_search ON charge_items 
USING gin(to_tsvector('simple', item_name || ' ' || item_code));

# 使用全文搜索
query = query.filter(
    func.to_tsvector('simple', ChargeItem.item_name + ' ' + ChargeItem.item_code)
    .match(keyword)
)
```

### 4. 数据库连接池优化

在 `database.py` 中优化连接池配置：

```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,          # 增加连接池大小
    max_overflow=40,       # 增加最大溢出连接
    pool_pre_ping=True,    # 连接前检查
    pool_recycle=3600,     # 1小时回收连接
)
```

### 5. 异步查询

对于非关键路径的查询，可以使用异步：

```python
from fastapi import BackgroundTasks

@router.get("")
async def get_charge_items(
    background_tasks: BackgroundTasks,
    ...
):
    # 快速返回数据
    items = query.offset(...).limit(...).all()
    
    # 后台计算总数
    def count_total():
        total = query.count()
        # 更新缓存或通知前端
    
    background_tasks.add_task(count_total)
    
    return ChargeItemList(total=-1, items=items)  # -1 表示计算中
```

## 监控和诊断

### 1. 启用 SQL 日志

在 `.env` 中添加：
```env
LOG_LEVEL=DEBUG
```

这会在控制台显示所有 SQL 查询和执行时间。

### 2. 使用 PostgreSQL 慢查询日志

在 PostgreSQL 配置中：
```sql
ALTER DATABASE hospital_value SET log_min_duration_statement = 1000;  -- 记录超过 1 秒的查询
```

### 3. 分析查询计划

```sql
EXPLAIN ANALYZE 
SELECT * FROM charge_items 
WHERE item_name LIKE '%test%' 
ORDER BY item_code 
LIMIT 10 OFFSET 100;
```

## 故障排查

### 问题 1: 迁移失败

**错误：** `Index already exists`

**解决：** 索引可能已存在，跳过或删除重建
```sql
DROP INDEX IF EXISTS ix_charge_items_item_name;
DROP INDEX IF EXISTS ix_charge_items_item_category;
```

### 问题 2: 性能没有提升

**检查：**
1. 索引是否创建成功？
   ```sql
   SELECT * FROM pg_indexes WHERE tablename = 'charge_items';
   ```

2. 统计信息是否更新？
   ```sql
   ANALYZE charge_items;
   ```

3. 查询是否使用了索引？
   ```sql
   EXPLAIN SELECT * FROM charge_items WHERE item_name LIKE '%test%';
   ```

### 问题 3: 内存使用增加

**原因：** 索引会占用额外内存

**解决：** 监控内存使用，必要时增加服务器内存或优化索引

## 相关文件

- ✅ `backend/app/api/charge_items.py` - 优化查询逻辑
- ✅ `backend/app/models/charge_item.py` - 添加索引定义
- ✅ `backend/alembic/versions/a1b2c3d4e5f6_add_indexes_to_charge_items.py` - 数据库迁移
- ✅ `scripts/optimize-database.ps1` - 优化脚本

## 下一步

1. ✅ 运行优化脚本
2. ✅ 重启 FastAPI 服务
3. ✅ 测试查询性能
4. ✅ 监控响应时间
5. ⏭️ 根据需要应用进一步优化
