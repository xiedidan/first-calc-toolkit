# 计算步骤与数据源集成测试指南

## 功能概述

本次更新实现了计算流程管理中步骤与数据源的对接功能：

1. **SQL 步骤**：可以选择数据源，并支持测试执行
2. **Python 步骤**：预留了虚拟环境选择 UI（暂未实现功能）

## 数据库变更

### 新增字段

在 `calculation_steps` 表中新增了两个字段：

- `data_source_id` (INTEGER): 数据源ID，用于 SQL 步骤
- `python_env` (VARCHAR(200)): Python 虚拟环境路径，用于 Python 步骤

### 外键关系

- `calculation_steps.data_source_id` → `data_sources.id` (SET NULL on delete)

## 后端变更

### 1. 模型更新 (`backend/app/models/calculation_step.py`)

```python
# 新增字段
data_source_id = Column(Integer, ForeignKey("data_sources.id", ondelete="SET NULL"), ...)
python_env = Column(String(200), ...)

# 新增关系
data_source = relationship("DataSource", foreign_keys=[data_source_id])
```

### 2. Schema 更新 (`backend/app/schemas/calculation_step.py`)

- `CalculationStepBase`: 新增 `data_source_id` 和 `python_env` 字段
- `CalculationStepResponse`: 新增 `data_source_name` 字段用于显示

### 3. API 更新 (`backend/app/api/calculation_steps.py`)

#### 创建/更新步骤验证

- SQL 步骤必须指定 `data_source_id`
- 验证数据源是否存在

#### 测试步骤功能 (`POST /calculation-steps/{step_id}/test`)

**SQL 步骤测试**：
- 连接指定的数据源
- 执行 SQL 查询（自动添加 LIMIT 100）
- 返回列名和数据行

**Python 步骤测试**：
- 暂未实现，返回错误提示

## 前端变更

### 1. 类型定义更新 (`frontend/src/api/calculation-workflow.ts`)

```typescript
export interface CalculationStep {
  // ... 其他字段
  data_source_id?: number
  data_source_name?: string
  python_env?: string
}
```

### 2. UI 更新 (`frontend/src/views/CalculationWorkflows.vue`)

#### 步骤列表

- 新增"数据源"列，显示 SQL 步骤关联的数据源名称

#### 步骤编辑对话框

- **SQL 步骤**：显示数据源下拉选择框（必填）
- **Python 步骤**：显示虚拟环境输入框（禁用状态，预留）
- 切换代码类型时自动清空相关字段

#### 测试结果显示

- 显示执行时间
- SQL 查询结果：显示列名和数据预览（最多 10 行）
- 错误信息：格式化显示错误详情

## 测试步骤

### 前置条件

1. 确保后端服务运行：`uvicorn app.main:app --reload`
2. 确保前端服务运行：`npm run dev`
3. 至少创建一个数据源（在系统设置 → 数据源管理）
4. 至少创建一个计算流程

### 手动测试

#### 1. 创建 SQL 步骤

1. 进入"计算流程管理"页面
2. 点击某个流程的"查看步骤"
3. 点击"新建步骤"
4. 填写信息：
   - 步骤名称：测试 SQL 步骤
   - 代码类型：选择 SQL
   - 数据源：选择一个可用的数据源
   - 代码内容：
     ```sql
     SELECT 1 as id, 'test' as name, NOW() as created_at
     ```
5. 点击"确定"创建

#### 2. 测试 SQL 步骤

1. 在步骤列表中找到刚创建的步骤
2. 点击"测试"按钮
3. 查看测试结果对话框：
   - 应显示执行时间
   - 应显示返回的列名
   - 应显示查询结果数据

#### 3. 创建 Python 步骤（UI 预览）

1. 点击"新建步骤"
2. 选择代码类型为 Python
3. 观察"虚拟环境"输入框（应为禁用状态）
4. 填写其他信息并创建

#### 4. 编辑步骤

1. 点击某个步骤的"编辑"按钮
2. 修改数据源（SQL 步骤）
3. 保存并验证更新成功

### 自动化测试脚本

运行集成测试脚本：

```bash
cd backend
python test_step_integration.py
```

该脚本会自动：
1. 登录系统
2. 获取数据源列表
3. 获取计算流程列表
4. 创建测试 SQL 步骤
5. 执行步骤测试
6. 显示测试结果

## API 测试示例

### 创建 SQL 步骤

```bash
curl -X POST "http://localhost:8000/api/v1/calculation-steps" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": 1,
    "name": "测试SQL步骤",
    "code_type": "sql",
    "code_content": "SELECT * FROM users LIMIT 10",
    "data_source_id": 1,
    "is_enabled": true
  }'
```

### 测试步骤

```bash
curl -X POST "http://localhost:8000/api/v1/calculation-steps/1/test" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## 预期结果

### 成功的 SQL 测试响应

```json
{
  "success": true,
  "duration_ms": 45,
  "result": {
    "message": "SQL执行成功，返回 3 行数据",
    "columns": ["id", "name", "created_at"],
    "rows": [
      {"id": 1, "name": "test", "created_at": "2025-10-28T10:00:00"},
      {"id": 2, "name": "test2", "created_at": "2025-10-28T10:01:00"},
      {"id": 3, "name": "test3", "created_at": "2025-10-28T10:02:00"}
    ],
    "row_count": 3
  }
}
```

### 失败的测试响应

```json
{
  "success": false,
  "duration_ms": 120,
  "error": "relation \"non_existent_table\" does not exist"
}
```

## 注意事项

1. **SQL 步骤必须选择数据源**：创建或更新 SQL 步骤时，如果未选择数据源，会返回 400 错误
2. **自动限制查询结果**：测试 SQL 时，如果查询中没有 LIMIT 子句，系统会自动添加 `LIMIT 100`
3. **Python 步骤暂未实现**：虚拟环境选择仅为 UI 预留，实际执行功能待后续开发
4. **数据源连接**：测试时会使用数据源服务建立实际的数据库连接

## 下一步开发

1. 实现 Python 步骤的虚拟环境管理
2. 实现 Python 代码的执行和测试
3. 添加步骤执行日志记录
4. 支持步骤间的数据传递
5. 添加步骤执行的参数化支持

## 故障排查

### 问题：创建 SQL 步骤时提示"SQL步骤必须指定数据源"

**解决方案**：确保在创建步骤时选择了数据源

### 问题：测试步骤时提示"数据源不存在"

**解决方案**：
1. 检查数据源是否已被删除
2. 重新编辑步骤，选择有效的数据源

### 问题：SQL 测试失败

**解决方案**：
1. 检查 SQL 语法是否正确
2. 检查数据源连接是否正常
3. 检查数据库权限是否足够
4. 查看错误信息中的具体原因

## 文件清单

### 后端文件

- `backend/alembic/versions/add_datasource_to_steps.py` - 数据库迁移文件
- `backend/app/models/calculation_step.py` - 步骤模型（已更新）
- `backend/app/schemas/calculation_step.py` - 步骤 Schema（已更新）
- `backend/app/api/calculation_steps.py` - 步骤 API（已更新）
- `backend/test_step_integration.py` - 集成测试脚本（新增）

### 前端文件

- `frontend/src/api/calculation-workflow.ts` - API 类型定义（已更新）
- `frontend/src/views/CalculationWorkflows.vue` - 计算流程管理页面（已更新）

## 总结

本次更新成功实现了计算步骤与数据源的集成，SQL 步骤现在可以：
- 选择数据源
- 执行 SQL 查询测试
- 查看查询结果

Python 步骤的 UI 已预留，等待后续功能实现。
