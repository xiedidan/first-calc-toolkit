# 报表功能实现说明

## 功能概述

报表功能是医院科室业务价值评估工具的核心功能之一，包括计算任务管理、结果查询展示和报表导出三个主要模块。

## 已实现功能

### 1. 后端实现

#### 1.1 数据模型
- **CalculationTask**: 计算任务表，记录任务的基本信息和执行状态
- **CalculationResult**: 计算结果明细表，存储每个科室、每个节点的详细计算结果
- **CalculationSummary**: 计算结果汇总表，存储科室级别的汇总数据

#### 1.2 API接口
创建了 `backend/app/api/calculation_tasks.py`，实现了以下接口：

- `POST /api/v1/calculation/tasks` - 创建并启动计算任务
- `GET /api/v1/calculation/tasks` - 获取计算任务列表
- `GET /api/v1/calculation/tasks/{task_id}` - 获取计算任务详情
- `POST /api/v1/calculation/tasks/{task_id}/cancel` - 取消计算任务
- `GET /api/v1/calculation/results/summary` - 获取科室汇总数据
- `GET /api/v1/calculation/results/detail` - 获取科室详细业务价值数据
- `POST /api/v1/calculation/results/export/summary` - 导出汇总表（待完善）
- `POST /api/v1/calculation/results/export/detail` - 导出明细表（待完善）
- `GET /api/v1/calculation/results/export/{task_id}/download` - 下载报表文件（待完善）

#### 1.3 异步任务
创建了 `backend/app/tasks/calculation_tasks.py`，实现了：

- `execute_calculation_task`: 执行计算任务的Celery异步任务
- `execute_calculation_step`: 执行单个计算步骤
- `calculate_summaries`: 计算汇总数据

### 2. 前端实现

#### 2.1 计算任务管理页面
创建了 `frontend/src/views/CalculationTasks.vue`，实现了：

- 计算任务列表展示
- 创建计算任务对话框
- 任务状态监控（排队中、运行中、已完成、失败、已取消）
- 任务进度显示
- 任务操作（查看结果、取消、重试）

#### 2.2 结果查看页面
创建了 `frontend/src/views/Results.vue`，实现了：

- 科室业务价值汇总表展示
- 筛选条件（评估月份、模型版本）
- 科室详细业务价值明细对话框
- 按序列（医生、护理、医技）分类展示维度数据
- 导出功能按钮（待完善）

#### 2.3 路由配置
更新了 `frontend/src/router/index.ts`，添加了：

- `/calculation-tasks` - 计算任务管理页面
- `/results` - 评估结果页面

### 3. 数据库迁移
创建了 `backend/alembic/versions/20251029_182429_add_calculation_task_tables.py`，包含：

- 创建 `calculation_tasks` 表
- 创建 `calculation_results` 表
- 创建 `calculation_summaries` 表
- 创建相关索引和外键约束

## 待完善功能

### 1. 计算引擎核心逻辑
当前 `execute_calculation_step` 函数中的代码执行逻辑需要完善：

```python
# TODO: 执行SQL代码
if step.code_type == "sql":
    # 需要实现：
    # 1. 获取数据源连接
    # 2. 执行SQL查询
    # 3. 解析查询结果
    # 4. 存储到 CalculationResult 表
    result_data = {}

# TODO: 执行Python代码
elif step.code_type == "python":
    # 需要实现：
    # 1. 创建安全的Python执行环境
    # 2. 执行Python代码
    # 3. 解析执行结果
    # 4. 存储到 CalculationResult 表
    result_data = {}
```

### 2. 报表导出功能
需要实现Excel报表生成和下载功能：

- 使用 `openpyxl` 或 `xlsxwriter` 库生成Excel文件
- 实现汇总表导出（按照《绩效结构表（模板）-标准版-20251017-v1.xlsx》格式）
- 实现明细表导出
- 实现异步导出任务（使用Celery）
- 实现文件下载接口

### 3. 任务重试功能
前端已有重试按钮，但后端逻辑需要实现：

- 复制失败任务的配置
- 创建新的计算任务
- 重新提交到Celery队列

### 4. 任务取消功能
当前只更新了任务状态，需要实现：

- 实际取消Celery任务
- 清理已生成的中间结果

### 5. 实时进度更新
需要实现前端轮询或WebSocket连接，实时更新任务进度：

- 前端定时轮询任务状态
- 或使用WebSocket推送进度更新

### 6. 数据权限控制
需要实现基于角色的数据权限隔离：

- 科室管理者只能查看本科室数据
- 院领导可以查看所有科室数据
- 在API层面实现数据过滤

## 使用说明

### 1. 运行数据库迁移

```bash
cd backend
alembic upgrade head
```

### 2. 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload
```

### 3. 启动Celery Worker

```bash
cd backend
celery -A app.celery_app worker --loglevel=info
```

### 4. 启动前端服务

```bash
cd frontend
npm run dev
```

### 5. 访问系统

打开浏览器访问 `http://localhost:3000`，登录后：

1. 进入"计算任务管理"页面
2. 点击"创建计算任务"按钮
3. 选择模型版本、计算流程、计算周期和科室范围
4. 提交任务后，可以在列表中查看任务状态和进度
5. 任务完成后，点击"查看结果"按钮进入结果页面
6. 在结果页面可以查看汇总数据和各科室的详细数据

## 技术栈

- **后端**: Python 3.12 + FastAPI + SQLAlchemy + Celery
- **前端**: Vue 3 + TypeScript + Element Plus
- **数据库**: PostgreSQL 16
- **任务队列**: Redis + Celery
- **报表生成**: openpyxl / xlsxwriter（待实现）

## 注意事项

1. 计算任务是异步执行的，创建任务后需要等待Celery Worker处理
2. 确保Redis服务正常运行，否则任务无法提交
3. 确保Celery Worker正常运行，否则任务无法执行
4. 大数据量计算可能需要较长时间，建议设置合理的超时时间
5. 导出功能需要足够的磁盘空间存储临时文件

## 下一步计划

1. 完善计算引擎核心逻辑（SQL和Python代码执行）
2. 实现Excel报表导出功能
3. 实现任务重试和取消功能
4. 实现实时进度更新
5. 实现数据权限控制
6. 添加单元测试和集成测试
7. 优化性能（并行计算、结果缓存等）
8. 完善错误处理和日志记录
