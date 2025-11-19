# Celery Backend 配置问题修复

## 问题描述

前端查询任务状态时报错：
```
Celery backend 配置错误: 'DisabledBackend' object has no attribute '_get_task_meta_for'
```

但 Celery Worker 日志显示任务执行成功：
```
Task import_charge_items[xxx] succeeded in 112.6s
```

## 问题原因

FastAPI 服务在查询任务状态时使用了错误的 Celery 实例：
- ❌ 使用 `from celery.result import AsyncResult` 创建新实例
- ✅ 应该使用 `celery_app.AsyncResult()` 使用配置好的实例

## 已修复

在 `backend/app/api/charge_items.py` 中：

```python
# 修复前
from celery.result import AsyncResult
task = AsyncResult(task_id)  # 使用默认配置，backend 被禁用

# 修复后
from app.celery_app import celery_app
task = celery_app.AsyncResult(task_id)  # 使用配置好的实例
```

## 验证修复

### 1. 运行测试脚本

```cmd
conda run -n hospital-backend --cwd backend python test_redis_celery.py
```

**期望输出：**
```
✅ 环境变量配置: 通过
✅ Redis 连接: 通过
✅ Celery 配置: 通过
✅ 任务结果查询: 通过

🎉 所有测试通过！异步导入功能应该可以正常工作。
```

### 2. 重启 FastAPI 服务

**重要：** 修改代码后必须重启 FastAPI 服务！

停止当前服务（Ctrl+C），然后重新启动：

```cmd
conda run -n hospital-backend --cwd backend uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 测试异步导入

1. 访问前端收费项目管理页面
2. 点击"批量导入"
3. 上传 Excel 文件
4. 观察是否显示实时进度

## 故障排查

### 问题 1: 测试脚本报 Redis 连接失败

**解决方案：**
1. 检查 Redis/Memurai 是否运行：
   ```cmd
   # Memurai
   sc query Memurai
   
   # 或手动测试
   conda run -n hospital-backend python -c "import redis; redis.Redis().ping(); print('OK')"
   ```

2. 如果未运行，启动 Redis/Memurai

### 问题 2: Backend 类型显示 DisabledBackend

**原因：** `.env` 配置未正确加载或 Redis 连接失败

**解决方案：**
1. 检查 `backend/.env` 文件：
   ```env
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   ```

2. 确保 Redis 在 6379 端口运行

3. 重启 FastAPI 服务

### 问题 3: 仍然报错

**可能原因：**
- FastAPI 服务未重启
- 使用了缓存的旧代码
- 虚拟环境不正确

**解决方案：**
1. 完全停止 FastAPI 服务
2. 清除 Python 缓存：
   ```cmd
   cd backend
   del /s /q __pycache__
   del /s /q *.pyc
   ```
3. 重新启动服务

## 完整重启流程

如果问题持续存在，按以下顺序完全重启所有服务：

### 1. 停止所有服务
- 停止 FastAPI（Ctrl+C）
- 停止 Celery Worker（Ctrl+C）
- 停止前端（Ctrl+C）

### 2. 验证 Redis
```cmd
conda run -n hospital-backend python backend/test_redis_celery.py
```

### 3. 启动 Celery Worker
```cmd
conda run -n hospital-backend --cwd backend celery -A app.celery_app worker --loglevel=info --pool=solo
```

验证输出：
```
✅ Connected to redis://localhost:6379/0
✅ [tasks] . import_charge_items
✅ celery@hostname ready.
```

### 4. 启动 FastAPI
```cmd
conda run -n hospital-backend --cwd backend uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 启动前端
```cmd
cd frontend
npm run dev
```

### 6. 测试导入功能

## 技术细节

### 为什么会出现这个问题？

Celery 支持多种 backend：
- `redis://` - Redis backend（需要 Redis 运行）
- `rpc://` - RPC backend（基于消息队列）
- `db+postgresql://` - 数据库 backend
- `disabled://` - 禁用 backend（默认）

当创建 `AsyncResult` 时：
```python
# 方式 1: 使用默认配置（错误）
from celery.result import AsyncResult
result = AsyncResult(task_id)  # 使用 Celery() 默认实例，backend=disabled

# 方式 2: 使用配置好的实例（正确）
from app.celery_app import celery_app
result = celery_app.AsyncResult(task_id)  # 使用我们配置的实例，backend=redis
```

### 为什么 Celery Worker 能工作？

Celery Worker 启动时直接使用 `app.celery_app`：
```cmd
celery -A app.celery_app worker
```

所以它使用的是正确配置的实例，能够连接 Redis 并存储结果。

### 为什么 FastAPI 查询失败？

FastAPI 服务如果使用 `AsyncResult(task_id)` 而不是 `celery_app.AsyncResult(task_id)`，会创建一个新的 Celery 实例，这个实例使用默认配置（backend=disabled），无法从 Redis 读取结果。

## 相关文件

- ✅ `backend/app/api/charge_items.py` - 已修复查询逻辑
- ✅ `backend/test_redis_celery.py` - 测试脚本
- ✅ `backend/.env` - 配置文件

## 下一步

1. ✅ 运行测试脚本验证配置
2. ✅ 重启 FastAPI 服务
3. ✅ 测试异步导入功能
4. ✅ 观察实时进度显示
