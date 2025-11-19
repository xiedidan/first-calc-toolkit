# 计算流程模型导入问题修复

## 问题描述

后端启动时出现 SQLAlchemy 错误：
```
sqlalchemy.exc.InvalidRequestError: One or more mappers failed to initialize - can't proceed with initialization of other mappers. 
Triggering mapper: 'Mapper[CalculationStep(calculation_steps)]'. 
Original exception was: When initializing mapper Mapper[CalculationStep(calculation_steps)], 
expression 'CalculationStepLog' failed to locate a name ('CalculationStepLog').
```

## 根本原因

新增的计算流程相关模型（`CalculationWorkflow`、`CalculationStep`、`CalculationStepLog`）没有被正确导入到：
1. `backend/app/models/__init__.py` - 模型包初始化文件
2. `backend/alembic/env.py` - Alembic 迁移环境文件

导致 SQLAlchemy 无法正确解析模型之间的关系引用。

## 修复内容

### 1. 更新 `backend/app/models/__init__.py`

添加了新模型的导入：
```python
from .calculation_step_log import CalculationStepLog
from .calculation_step import CalculationStep
from .calculation_workflow import CalculationWorkflow
```

注意导入顺序：先导入 `CalculationStepLog`，再导入 `CalculationStep`，最后导入 `CalculationWorkflow`。

### 2. 更新 `backend/alembic/env.py`

添加了所有模型的导入，确保 Alembic 能够识别所有表：
```python
from app.models import (
    user,
    role,
    permission,
    department,
    charge_item,
    dimension_item_mapping,
    model_version,
    model_node,
    calculation_workflow,
    calculation_step,
    calculation_step_log,
)
```

## 验证步骤

1. **重启后端服务**
   ```bash
   # 停止当前运行的后端服务（Ctrl+C）
   # 重新启动
   cd backend
   uvicorn app.main:app --reload
   ```

2. **检查服务启动**
   - 确认没有 SQLAlchemy 错误
   - 访问 http://localhost:8000/docs 查看 API 文档
   - 确认计算流程相关的 API 端点已正确注册

3. **运行集成测试**
   ```bash
   cd backend
   python test_calculation_workflow_integration.py
   ```

## 相关文件

- `backend/app/models/__init__.py` - 模型包初始化
- `backend/alembic/env.py` - Alembic 环境配置
- `backend/app/models/calculation_workflow.py` - 计算流程模型
- `backend/app/models/calculation_step.py` - 计算步骤模型
- `backend/app/models/calculation_step_log.py` - 计算步骤日志模型

## 注意事项

在 SQLAlchemy 中使用关系引用时：
- 使用字符串引用（如 `"CalculationStepLog"`）可以避免循环导入
- 但必须确保被引用的模型在应用启动时被导入
- 在 `models/__init__.py` 中导入所有模型是最佳实践
- 在 `alembic/env.py` 中也需要导入所有模型，以便迁移工具能识别

## 状态

✅ 已修复 - 2025-10-27
