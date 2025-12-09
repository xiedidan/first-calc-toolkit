# AI分类任务实现文档

## 概述

本文档描述了医技智能分类分级模块的Celery异步任务实现，包括AI分类处理和断点续传功能。

## 实现的功能

### 1. classify_items_task - AI分类异步任务

**功能描述：**
- 异步执行医技项目的AI分类
- 逐个调用AI接口处理项目
- 记录处理进度和结果
- 支持错误处理和日志记录
- 实现调用延迟控制

**任务配置：**
- 超时限制：2小时（硬超时）/ 116分钟（软超时）
- 不自动重试（max_retries=0）
- 绑定模式（bind=True），支持状态更新

**处理流程：**

1. **加载任务和配置**
   - 查询ClassificationTask记录
   - 更新任务状态为processing
   - 加载AI配置（AIConfig）
   - 解密API密钥

2. **创建或获取预案**
   - 查询或创建ClassificationPlan
   - 如果是首次执行，创建PlanItem列表

3. **查询待处理项目**
   - 查询状态为pending或failed的PlanItem
   - 支持断点续传（跳过已完成项目）

4. **加载目标维度**
   - 查询模型版本的所有末级维度（is_leaf=True）
   - 构建维度列表（包含id、name、path）
   - 递归构建完整路径

5. **逐个处理项目**
   - 更新项目状态为processing
   - 调用AI接口（call_ai_classification）
   - 保存AI建议结果（dimension_id和confidence）
   - 记录API使用日志（APIUsageLog）
   - 更新任务进度
   - 实现调用延迟控制

6. **错误处理**
   - 捕获AI接口错误（AIClassificationError）
   - 记录错误信息到PlanItem
   - 记录失败日志到APIUsageLog
   - 继续处理下一个项目（不中断整个任务）

7. **完成任务**
   - 更新任务状态为completed
   - 记录完成时间
   - 更新处理统计（processed_items、failed_items）

**错误处理策略：**
- 单个项目失败不影响其他项目
- 记录详细错误信息
- 支持后续重试失败项目
- 超时时任务状态设为paused

### 2. continue_classification_task - 断点续传任务

**功能描述：**
- 继续执行中断的分类任务
- 复用classify_items_task的逻辑
- 自动跳过已完成项目

**实现方式：**
- 直接调用classify_items_task
- classify_items_task会自动查询pending和failed状态的项目
- 实现真正的断点续传

## 数据流

```
创建任务 → 启动Celery任务 → 加载配置 → 解密密钥
    ↓
创建预案 → 创建项目列表 → 加载维度列表
    ↓
逐个处理项目:
  - 更新状态为processing
  - 调用AI接口
  - 保存结果
  - 记录日志
  - 更新进度
  - 延迟控制
    ↓
完成任务 → 更新状态为completed
```

## 关键实现细节

### 1. 维度路径构建

```python
# 递归构建完整路径
path_parts = [dim.name]
current = dim
while current.parent_id:
    parent = db.query(ModelNode).filter(ModelNode.id == current.parent_id).first()
    if parent:
        path_parts.insert(0, parent.name)
        current = parent
    else:
        break

path = " / ".join(path_parts)
```

### 2. 项目列表创建

```python
def _create_plan_items(db, task, plan):
    # 查询符合收费类别的项目
    charge_items = db.query(ChargeItem).filter(
        ChargeItem.hospital_id == task.hospital_id,
        ChargeItem.item_category.in_(task.charge_categories)
    ).all()
    
    # 创建预案项目
    for charge_item in charge_items:
        plan_item = PlanItem(
            hospital_id=task.hospital_id,
            plan_id=plan.id,
            charge_item_id=charge_item.id,
            charge_item_name=charge_item.item_name,
            processing_status=ProcessingStatus.pending
        )
        db.add(plan_item)
    
    db.commit()
```

### 3. 错误处理和继续执行

```python
try:
    # 处理项目
    result = call_ai_classification(...)
    item.processing_status = ProcessingStatus.completed
    processed_count += 1
except AIClassificationError as e:
    # 记录错误但继续
    item.processing_status = ProcessingStatus.failed
    item.error_message = str(e)
    failed_count += 1
    continue  # 继续处理下一个项目
```

### 4. 进度更新

```python
# 更新任务进度
task.processed_items = processed_count
db.commit()

# 更新Celery任务状态
self.update_state(
    state='PROGRESS',
    meta={
        'current': processed_count,
        'total': total_items,
        'failed': failed_count
    }
)
```

### 5. 调用延迟控制

```python
# 在每个项目处理后延迟
if idx < total_items - 1:  # 最后一个项目不需要延迟
    delay = float(ai_config.call_delay or 1.0)
    time.sleep(delay)
```

## 依赖关系

### 模型依赖
- ClassificationTask - 分类任务
- ClassificationPlan - 分类预案
- PlanItem - 预案项目
- AIConfig - AI配置
- ModelNode - 模型节点（维度）
- ChargeItem - 收费项目
- APIUsageLog - API使用日志

### 工具依赖
- encryption.decrypt_api_key - 密钥解密
- ai_interface.call_ai_classification - AI接口调用

### Celery配置
- 任务已注册到celery_app
- 需要Redis作为消息队列
- 需要启动Celery worker

## 使用方式

### 1. 通过API创建任务

```python
# API会自动启动Celery任务
from app.tasks.classification_tasks import classify_items_task

result = classify_items_task.delay(
    task_id=1,
    hospital_id=1
)
```

### 2. 继续中断的任务

```python
from app.tasks.classification_tasks import continue_classification_task

result = continue_classification_task.delay(
    task_id=1,
    hospital_id=1
)
```

### 3. 查询任务状态

```python
from celery.result import AsyncResult

result = AsyncResult(celery_task_id)
print(result.state)  # PENDING, PROGRESS, SUCCESS, FAILURE
print(result.info)   # 进度信息
```

## 测试

### 运行测试脚本

```bash
python test_classification_tasks.py
```

### 测试内容
1. 任务模块导入
2. Celery任务注册
3. 数据库结构检查
4. 数据完整性验证

## 配置要求

### 环境变量
```bash
ENCRYPTION_KEY=<Fernet加密密钥>
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 数据库要求
- AI配置已创建（AIConfig）
- 模型版本已创建（ModelVersion）
- 收费项目已导入（ChargeItem）
- 维度结构已建立（ModelNode）

### 服务要求
- Redis服务运行中
- Celery worker运行中
- 数据库连接正常

## 启动Celery Worker

### Windows (PowerShell)
```powershell
cd backend
celery -A app.celery_app worker --loglevel=info --pool=solo
```

### Linux/Mac
```bash
cd backend
celery -A app.celery_app worker --loglevel=info --concurrency=4
```

## 监控和调试

### 查看Celery日志
```bash
# Worker会输出详细日志
[AI分类任务] 开始执行任务 1, 医疗机构 1
[AI分类任务] 加载AI配置: endpoint=https://api.deepseek.com
[AI分类任务] 找到 10 个待处理项目
[AI分类任务] 处理项目 1/10: 血常规检查
[AI分类任务] 项目处理成功: 血常规检查, 维度ID=5, 确信度=0.95
```

### 查看任务状态
```python
# 通过API查询任务进度
GET /api/v1/classification-tasks/{id}/progress
```

### 查看处理日志
```python
# 通过API查询处理日志
GET /api/v1/classification-tasks/{id}/logs
```

## 性能优化

### 1. 批量加载维度
- 一次性加载所有末级维度
- 避免在循环中查询数据库

### 2. 调用延迟控制
- 通过call_delay配置控制调用频率
- 避免触发API限流

### 3. 错误隔离
- 单个项目失败不影响其他项目
- 支持后续重试失败项目

### 4. 进度实时更新
- 每处理一个项目更新进度
- 支持前端实时显示

## 注意事项

1. **API密钥安全**
   - 密钥加密存储
   - 使用时解密
   - 不记录到日志

2. **错误处理**
   - 记录详细错误信息
   - 不中断整个任务
   - 支持断点续传

3. **性能考虑**
   - 控制调用频率
   - 避免超出API限额
   - 合理设置超时时间

4. **数据一致性**
   - 使用数据库事务
   - 及时提交更改
   - 错误时回滚

## 下一步

1. 实现分类任务管理服务和API（任务7）
2. 实现分类预案管理服务和API（任务8）
3. 实现提交预览和批量提交功能（任务9）
4. 实现限流和统计功能（任务10）

## 相关文件

- `backend/app/tasks/classification_tasks.py` - 任务实现
- `backend/app/celery_app.py` - Celery配置
- `backend/app/utils/ai_interface.py` - AI接口
- `backend/app/utils/encryption.py` - 加密工具
- `test_classification_tasks.py` - 测试脚本
