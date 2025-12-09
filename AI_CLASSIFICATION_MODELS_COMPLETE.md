# AI医技智能分类分级 - SQLAlchemy模型实现完成

## 任务概述

已完成任务 1.2：定义SQLAlchemy模型，实现了AI医技智能分类分级功能所需的全部6个数据模型。

## 实现的模型

### 1. AIConfig（AI接口配置）
- **文件**: `backend/app/models/ai_config.py`
- **功能**: 存储AI接口配置信息
- **关键字段**:
  - `api_endpoint`: API访问端点
  - `api_key_encrypted`: 加密的API密钥
  - `prompt_template`: 提示词模板
  - `call_delay`: 调用延迟（秒）
  - `daily_limit`: 每日调用限额
  - `batch_size`: 批次大小
- **约束**: 每个医疗机构只能有一个AI配置（`uq_ai_config_hospital`）
- **关系**: 
  - `hospital`: 关联到Hospital模型

### 2. ClassificationTask（分类任务）
- **文件**: `backend/app/models/classification_task.py`
- **功能**: 管理AI分类任务
- **关键字段**:
  - `task_name`: 任务名称
  - `model_version_id`: 模型版本ID
  - `charge_categories`: 收费类别列表（JSON）
  - `status`: 任务状态（pending/processing/completed/failed/paused）
  - `total_items`: 总项目数
  - `processed_items`: 已处理项目数
  - `failed_items`: 失败项目数
  - `celery_task_id`: Celery任务ID
- **关系**:
  - `hospital`: 关联到Hospital模型
  - `model_version`: 关联到ModelVersion模型
  - `creator`: 关联到User模型
  - `plan`: 一对一关联到ClassificationPlan模型
  - `progress_records`: 一对多关联到TaskProgress模型

### 3. ClassificationPlan（分类预案）
- **文件**: `backend/app/models/classification_plan.py`
- **功能**: 存储AI分类结果预案
- **关键字段**:
  - `task_id`: 关联的分类任务ID（唯一）
  - `plan_name`: 预案名称
  - `status`: 预案状态（draft/submitted）
  - `submitted_at`: 提交时间
- **约束**: 每个任务只能有一个预案（`task_id` unique）
- **关系**:
  - `hospital`: 关联到Hospital模型
  - `task`: 一对一关联到ClassificationTask模型
  - `items`: 一对多关联到PlanItem模型

### 4. PlanItem（预案项目）
- **文件**: `backend/app/models/plan_item.py`
- **功能**: 存储预案中的每个收费项目及其分类结果
- **关键字段**:
  - `charge_item_id`: 收费项目ID
  - `charge_item_name`: 收费项目名称
  - `ai_suggested_dimension_id`: AI建议的维度ID
  - `ai_confidence`: AI确信度（0-1）
  - `user_set_dimension_id`: 用户设置的维度ID
  - `is_adjusted`: 是否已调整
  - `processing_status`: 处理状态（pending/processing/completed/failed）
- **约束**: 同一预案中每个收费项目只能出现一次（`uq_plan_item`）
- **关系**:
  - `hospital`: 关联到Hospital模型
  - `plan`: 关联到ClassificationPlan模型
  - `charge_item`: 关联到ChargeItem模型
  - `ai_suggested_dimension`: 关联到ModelNode模型（AI建议）
  - `user_set_dimension`: 关联到ModelNode模型（用户设置）

### 5. TaskProgress（任务进度记录）
- **文件**: `backend/app/models/task_progress.py`
- **功能**: 记录每个项目的处理进度，支持断点续传
- **关键字段**:
  - `task_id`: 分类任务ID
  - `charge_item_id`: 收费项目ID
  - `status`: 处理状态（pending/processing/completed/failed）
  - `error_message`: 错误信息
  - `processed_at`: 处理时间
- **约束**: 同一任务中每个项目只记录一次（`uq_task_progress`）
- **关系**:
  - `task`: 关联到ClassificationTask模型
  - `charge_item`: 关联到ChargeItem模型

### 6. APIUsageLog（API使用日志）
- **文件**: `backend/app/models/api_usage_log.py`
- **功能**: 记录所有AI接口调用日志
- **关键字段**:
  - `hospital_id`: 医疗机构ID
  - `task_id`: 分类任务ID
  - `charge_item_id`: 收费项目ID
  - `request_data`: 请求数据（JSON）
  - `response_data`: 响应数据（JSON）
  - `status_code`: HTTP状态码
  - `error_message`: 错误信息
  - `call_duration`: 调用耗时（秒）
- **关系**:
  - `hospital`: 关联到Hospital模型
  - `task`: 关联到ClassificationTask模型
  - `charge_item`: 关联到ChargeItem模型

## 关联模型更新

已更新以下模型以支持双向关系：

### Hospital模型
添加了以下关系：
- `ai_configs`: 一对多关联到AIConfig
- `classification_tasks`: 一对多关联到ClassificationTask
- `classification_plans`: 一对多关联到ClassificationPlan

### ModelVersion模型
添加了以下关系：
- `classification_tasks`: 一对多关联到ClassificationTask

## 数据库迁移

迁移文件：`backend/alembic/versions/20251126_add_ai_classification_tables.py`

### 创建的枚举类型
1. `task_status`: pending, processing, completed, failed, paused
2. `plan_status`: draft, submitted
3. `processing_status`: pending, processing, completed, failed
4. `progress_status`: pending, processing, completed, failed

### 创建的表
1. `ai_configs`: AI接口配置表
2. `classification_tasks`: 分类任务表
3. `classification_plans`: 分类预案表
4. `plan_items`: 预案项目表
5. `task_progress`: 任务进度记录表
6. `api_usage_logs`: API使用日志表

### 索引
所有表都创建了必要的索引：
- 主键索引
- 外键索引
- hospital_id索引（多租户查询优化）
- created_at索引（日志查询优化）

## 测试验证

运行测试文件 `test_ai_classification_models.py`，验证结果：

✅ 所有6个模型创建成功
✅ 所有关系配置正确
✅ 级联删除工作正常
✅ 唯一约束生效
✅ 多租户隔离正常

## 模型导入顺序

已在 `backend/app/models/__init__.py` 中按正确的依赖顺序导入：

```python
# AI智能分类模型 - 注意导入顺序
from .ai_config import AIConfig
from .classification_task import ClassificationTask, TaskStatus
from .classification_plan import ClassificationPlan, PlanStatus
from .plan_item import PlanItem, ProcessingStatus
from .task_progress import TaskProgress, ProgressStatus
from .api_usage_log import APIUsageLog
```

## 设计特点

### 1. 多租户隔离
所有表都包含 `hospital_id` 字段，确保数据按医疗机构隔离。

### 2. 级联删除
使用 `ondelete="CASCADE"` 确保删除医疗机构、任务或预案时，相关数据自动清理。

### 3. 断点续传支持
通过 `TaskProgress` 表记录每个项目的处理状态，支持任务中断后继续处理。

### 4. 审计日志
`APIUsageLog` 表记录所有AI接口调用，支持成本统计和问题排查。

### 5. 灵活的维度设置
`PlanItem` 支持AI建议维度和用户设置维度，用户可以调整AI的分类结果。

## 下一步

模型定义已完成，可以继续实现：
- 任务 2.1: 实现API密钥加密解密功能
- 任务 3.1-3.3: 创建Pydantic Schema定义
- 任务 4.1: 实现AI接口调用功能

## 相关文件

- 模型文件: `backend/app/models/ai_*.py`, `backend/app/models/classification_*.py`, `backend/app/models/plan_*.py`, `backend/app/models/task_*.py`, `backend/app/models/api_*.py`
- 迁移文件: `backend/alembic/versions/20251126_add_ai_classification_tables.py`
- 测试文件: `test_ai_classification_models.py`
- 模型导入: `backend/app/models/__init__.py`
