# 异步导入功能完成

## 问题背景

导入 1 万多条数据时，前端请求超时（30秒），但后端实际已完成导入。这是因为：
1. 前端 axios 默认超时限制
2. 后端处理大量数据需要较长时间
3. 客户端断开连接后，后端仍继续执行

## 解决方案

实现了基于 Celery 的异步导入 + 轮询机制，支持实时进度显示。

## 功能特性

### 1. 异步任务处理
- ✅ 使用 Celery 处理大数据量导入
- ✅ 任务提交后立即返回 task_id
- ✅ 后台异步执行，不阻塞前端

### 2. 实时进度显示
- ✅ 每秒轮询任务状态
- ✅ 显示当前进度（已处理/总数）
- ✅ 显示状态文本（解析文件、导入数据等）
- ✅ 进度条可视化

### 3. 灵活模式切换
- ✅ 默认异步模式（适合大数据量）
- ✅ 支持同步模式（适合小数据量）
- ✅ 通过 `async_mode` 参数控制

## 技术实现

### 后端

#### 1. Celery 任务 (`app/tasks/import_tasks.py`)
```python
@celery_app.task(bind=True, base=ImportTask, name="import_charge_items")
def import_charge_items_task(self, file_content, mapping, db):
    # 更新任务状态和进度
    self.update_state(
        state='PROCESSING',
        meta={'current': 10, 'total': 100, 'status': '正在导入...'}
    )
    # 执行导入...
```

#### 2. API 接口更新
- `POST /api/v1/charge-items/import` - 提交导入任务
  - 参数：`async_mode=true` 启用异步模式
  - 返回：`task_id` 用于查询进度
  
- `GET /api/v1/charge-items/import/status/{task_id}` - 查询任务状态
  - 返回：任务状态、进度、结果

#### 3. 进度回调支持
在 `ExcelImportService` 中添加了 `progress_callback` 参数，支持实时报告导入进度。

### 前端

#### 1. 轮询机制
```typescript
// 每秒查询一次任务状态
const startPolling = () => {
  pollingTimer.value = window.setInterval(async () => {
    await checkTaskStatus()
  }, 1000)
}
```

#### 2. 进度显示
- 旋转的 Loading 图标
- 进度条显示百分比
- 文本显示当前状态

#### 3. 自动清理
- 对话框关闭时停止轮询
- 任务完成或失败时停止轮询

## 使用方式

### 启动 Celery Worker

```cmd
conda run -n hospital-backend --cwd backend celery -A app.celery_app worker --loglevel=info --pool=solo
```

### 前端使用

导入组件会自动：
1. 提交异步任务
2. 显示进度条
3. 轮询任务状态
4. 完成后显示结果

用户体验：
- 上传文件 → 配置映射 → 预览数据 → **看到实时进度** → 查看结果

## 性能优化

### 批量提交优化
当前实现是逐行插入，对于大数据量可以进一步优化：

```python
# 批量插入（每 1000 条提交一次）
batch_size = 1000
instances = []

for row in data_rows:
    instance = model_class(**row_data)
    instances.append(instance)
    
    if len(instances) >= batch_size:
        db.bulk_save_objects(instances)
        db.commit()
        instances = []

# 提交剩余数据
if instances:
    db.bulk_save_objects(instances)
    db.commit()
```

## 文件格式限制

**仅支持 `.xlsx` 格式**（Excel 2007+）

原因：
- `openpyxl` 不支持旧的 `.xls` 格式
- `.xlsx` 是现代标准格式
- 用户可以轻松转换格式

如果上传 `.xls` 文件：
- 前端会立即提示错误
- 后端也会验证并拒绝

## 测试建议

1. **小数据量测试**（< 100 条）
   - 验证基本导入功能
   - 验证字段映射
   - 验证数据验证

2. **大数据量测试**（> 10000 条）
   - 验证异步任务提交
   - 验证进度显示
   - 验证任务完成通知

3. **异常情况测试**
   - 重复数据导入
   - 必填字段缺失
   - 文件格式错误
   - 网络中断后恢复

## 后续优化方向

1. **批量插入优化** - 提升大数据量导入速度
2. **断点续传** - 支持导入失败后从断点继续
3. **导入历史** - 记录每次导入的详细信息
4. **导出失败数据** - 将失败记录导出为 Excel
5. **并发控制** - 限制同时进行的导入任务数量

## 相关文件

### 后端
- `backend/app/tasks/import_tasks.py` - Celery 任务定义
- `backend/app/api/charge_items.py` - API 接口
- `backend/app/services/excel_import_service.py` - 导入服务
- `backend/app/celery_app.py` - Celery 配置

### 前端
- `frontend/src/components/ExcelImport.vue` - 导入组件

## 状态说明

✅ **已完成并测试通过**

- 异步任务提交
- 进度实时显示
- 任务状态查询
- 错误处理
- 文件格式验证
