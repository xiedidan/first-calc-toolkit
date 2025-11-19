# 计算流程管理模块 - 快速开始

## 已完成的工作

### 后端开发 ✅

1. **数据库迁移脚本**
   - ✅ `backend/alembic/versions/add_calculation_workflow_tables.py`
   - 创建3个新表：calculation_workflows、calculation_steps、calculation_step_logs

2. **数据库模型**
   - ✅ `backend/app/models/calculation_workflow.py` - 计算流程模型
   - ✅ `backend/app/models/calculation_step.py` - 计算步骤模型
   - ✅ `backend/app/models/calculation_step_log.py` - 计算步骤日志模型
   - ✅ 更新 `backend/app/models/model_version.py` - 添加workflows关系

3. **Schema定义**
   - ✅ `backend/app/schemas/calculation_workflow.py` - 计算流程Schema
   - ✅ `backend/app/schemas/calculation_step.py` - 计算步骤Schema

4. **API路由**
   - ✅ `backend/app/api/calculation_workflows.py` - 计算流程API（6个接口）
   - ✅ `backend/app/api/calculation_steps.py` - 计算步骤API（8个接口）
   - ✅ 更新 `backend/app/main.py` - 注册新路由

5. **测试文件**
   - ✅ `backend/test_calculation_workflow_api.py` - API测试脚本

---

## 快速启动步骤

### 1. 执行数据库迁移

```bash
# 进入backend目录
cd backend

# 执行迁移
alembic upgrade head
```

### 2. 启动后端服务

```bash
# 方式1: 使用脚本（推荐）
..\scripts\dev-start-backend.ps1

# 方式2: 直接运行
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 测试API

```bash
# 运行测试脚本
python test_calculation_workflow_api.py
```

### 4. 查看API文档

打开浏览器访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## API接口列表

### 计算流程管理 (6个接口)

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/calculation-workflows` | 获取计算流程列表 |
| POST | `/api/v1/calculation-workflows` | 创建计算流程 |
| GET | `/api/v1/calculation-workflows/{id}` | 获取计算流程详情 |
| PUT | `/api/v1/calculation-workflows/{id}` | 更新计算流程 |
| DELETE | `/api/v1/calculation-workflows/{id}` | 删除计算流程 |
| POST | `/api/v1/calculation-workflows/{id}/copy` | 复制计算流程 |

### 计算步骤管理 (8个接口)

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/calculation-steps` | 获取计算步骤列表 |
| POST | `/api/v1/calculation-steps` | 创建计算步骤 |
| GET | `/api/v1/calculation-steps/{id}` | 获取计算步骤详情 |
| PUT | `/api/v1/calculation-steps/{id}` | 更新计算步骤 |
| DELETE | `/api/v1/calculation-steps/{id}` | 删除计算步骤 |
| POST | `/api/v1/calculation-steps/{id}/move-up` | 上移计算步骤 |
| POST | `/api/v1/calculation-steps/{id}/move-down` | 下移计算步骤 |
| POST | `/api/v1/calculation-steps/{id}/test` | 测试计算步骤代码 |

---

## 使用示例

### 1. 创建计算流程

```bash
curl -X POST "http://localhost:8000/api/v1/calculation-workflows" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "version_id": 1,
    "name": "2025年Q1计算流程",
    "description": "针对2025年第一季度的计算流程",
    "is_active": true
  }'
```

### 2. 创建计算步骤

```bash
curl -X POST "http://localhost:8000/api/v1/calculation-steps" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": 1,
    "name": "计算门诊工作量",
    "description": "统计门诊的工作量数据",
    "code_type": "sql",
    "code_content": "SELECT department_id, COUNT(*) as count FROM outpatient WHERE date = '\''{current_year_month}'\'' GROUP BY department_id",
    "is_enabled": true
  }'
```

### 3. 测试步骤代码

```bash
curl -X POST "http://localhost:8000/api/v1/calculation-steps/1/test" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "test_params": {
      "current_year_month": "2025-10",
      "department_id": 1
    }
  }'
```

---

## 数据库表结构

### calculation_workflows (计算流程表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| version_id | INTEGER | 模型版本ID |
| name | VARCHAR(200) | 流程名称 |
| description | TEXT | 流程描述 |
| is_active | BOOLEAN | 是否启用 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### calculation_steps (计算步骤表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| workflow_id | INTEGER | 计算流程ID |
| name | VARCHAR(200) | 步骤名称 |
| description | TEXT | 步骤描述 |
| code_type | VARCHAR(20) | 代码类型(python/sql) |
| code_content | TEXT | 代码内容 |
| sort_order | NUMERIC(10,2) | 执行顺序 |
| is_enabled | BOOLEAN | 是否启用 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### calculation_step_logs (计算步骤日志表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| task_id | VARCHAR(100) | 计算任务ID |
| step_id | INTEGER | 计算步骤ID |
| department_id | INTEGER | 科室ID |
| status | VARCHAR(20) | 执行状态 |
| start_time | TIMESTAMP | 开始时间 |
| end_time | TIMESTAMP | 结束时间 |
| duration_ms | INTEGER | 执行耗时(毫秒) |
| result_data | JSONB | 执行结果数据 |
| error_message | TEXT | 错误信息 |
| created_at | TIMESTAMP | 创建时间 |

---

## 下一步工作

### 前端开发 (待完成)

1. **创建前端页面**
   - [ ] 计算流程管理页面 (`frontend/src/views/CalculationWorkflows.vue`)
   - [ ] 计算步骤管理页面 (`frontend/src/views/CalculationSteps.vue`)

2. **创建前端组件**
   - [ ] 计算步骤编辑对话框 (`frontend/src/components/CalculationStepDialog.vue`)
   - [ ] 代码编辑器组件 (`frontend/src/components/CodeEditor.vue`)

3. **创建API客户端**
   - [ ] 计算流程API (`frontend/src/api/calculation-workflow.ts`)

4. **更新路由配置**
   - [ ] 添加新页面路由 (`frontend/src/router/index.ts`)

5. **更新菜单配置**
   - [ ] 添加菜单项

### 数据迁移工具 (待完成)

- [ ] 创建数据迁移脚本 (`backend/app/scripts/migrate_workflows.py`)
- [ ] 实现从model_nodes迁移代码到calculation_steps

### 代码测试功能 (待完成)

- [ ] 实现SQL代码测试执行
- [ ] 实现Python代码测试执行
- [ ] 添加代码安全检查

---

## 常见问题

### Q1: 数据库迁移失败怎么办？

```bash
# 查看当前迁移状态
alembic current

# 回滚到上一个版本
alembic downgrade -1

# 重新执行迁移
alembic upgrade head
```

### Q2: 如何查看API日志？

后端服务运行时会在控制台输出日志，包括所有API请求和响应。

### Q3: 如何清理测试数据？

```sql
-- 删除所有计算流程（会级联删除步骤）
DELETE FROM calculation_workflows WHERE name LIKE '%测试%';
```

---

## 相关文档

- [需求文档](./需求文档.md) - 查看完整需求说明
- [系统设计文档](./系统设计文档.md) - 查看系统设计
- [API设计文档](./API设计文档.md) - 查看API详细设计
- [架构变更说明](./CALCULATION_WORKFLOW_CHANGES.md) - 查看详细变更说明
