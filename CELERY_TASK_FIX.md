# Celery 任务注册问题修复

## 问题描述

Celery Worker 报错：
```
Received unregistered task of type 'import_charge_items'.
The message has been ignored and discarded.
```

## 原因分析

Celery 的 `autodiscover_tasks()` 方法默认只查找名为 `tasks.py` 的文件，但我们的任务定义在 `import_tasks.py` 中，导致任务没有被注册。

## 解决方案

在 `celery_app.py` 中显式导入任务模块：

```python
# 导入任务模块（必须在配置之后）
from app.tasks import import_tasks  # noqa: F401
```

这样 Celery worker 启动时会自动注册 `import_tasks.py` 中定义的所有任务。

## 修复步骤

### 1. 停止当前的 Celery Worker

在运行 Celery 的命令行窗口按 `Ctrl+C` 停止。

### 2. 重新启动 Celery Worker

```cmd
conda run -n hospital-backend --cwd backend celery -A app.celery_app worker --loglevel=info --pool=solo
```

### 3. 验证任务已注册

启动成功后，你应该看到类似输出：

```
[tasks]
  . import_charge_items
```

这表示任务已成功注册。

### 4. 测试异步导入

1. 访问前端页面
2. 进入"收费项目管理"
3. 点击"批量导入"
4. 上传 Excel 文件
5. 观察是否显示实时进度

## 验证清单

- ✅ Redis 正在运行
- ✅ Celery Worker 已启动
- ✅ 看到 `Connected to redis://localhost:6379/0`
- ✅ 看到 `[tasks] . import_charge_items`
- ✅ 没有 "unregistered task" 错误

## 常见问题

### Q: 重启后仍然报 "unregistered task" 错误

**A:** 检查以下几点：
1. 确保完全停止了旧的 Celery Worker（检查任务管理器）
2. 确保在正确的目录启动（`--cwd backend`）
3. 确保使用正确的虚拟环境（`conda run -n hospital-backend`）
4. 检查是否有 Python 语法错误

### Q: 启动时报 ImportError

**A:** 可能是循环导入问题，检查：
1. `app/celery_app.py` 是否正确导入了 `settings`
2. `app/tasks/import_tasks.py` 是否正确导入了 `celery_app`
3. 确保 `app/config/__init__.py` 中有 `settings` 定义

### Q: 任务执行失败

**A:** 查看 Celery Worker 的日志输出，通常会显示详细的错误信息。

## 其他注意事项

### 任务命名

任务名称通过 `name` 参数指定：

```python
@celery_app.task(bind=True, base=ImportTask, name="import_charge_items")
def import_charge_items_task(...):
    ...
```

- `name="import_charge_items"` - 这是任务的唯一标识符
- `import_charge_items_task` - 这是 Python 函数名

调用时使用任务名称：
```python
from app.tasks.import_tasks import import_charge_items_task
task = import_charge_items_task.delay(content, mapping_dict)
```

### 开发模式 vs 生产模式

**开发模式（当前）：**
```cmd
celery -A app.celery_app worker --loglevel=info --pool=solo
```
- `--pool=solo`: 单进程模式，Windows 兼容
- `--loglevel=info`: 显示详细日志

**生产模式（Linux/Docker）：**
```bash
celery -A app.celery_app worker --loglevel=warning --pool=prefork --concurrency=4
```
- `--pool=prefork`: 多进程模式，更高性能
- `--concurrency=4`: 4 个工作进程
- `--loglevel=warning`: 只显示警告和错误

## 相关文件

- `backend/app/celery_app.py` - Celery 应用配置
- `backend/app/tasks/import_tasks.py` - 导入任务定义
- `backend/app/tasks/__init__.py` - 任务模块初始化

## 下一步

任务注册成功后，可以：
1. ✅ 测试小文件导入
2. ✅ 测试大文件导入（> 1000 条）
3. ✅ 观察实时进度显示
4. ✅ 查看任务执行日志
