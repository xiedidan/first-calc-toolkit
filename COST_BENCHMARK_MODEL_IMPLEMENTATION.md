# 成本基准管理 - 数据库模型实施完成

## 任务概述

已完成任务 1：创建数据库模型和迁移

## 实施内容

### 1. 创建 CostBenchmark 模型

**文件**: `backend/app/models/cost_benchmark.py`

创建了完整的成本基准模型，包含以下特性：

- **字段定义**：
  - `id`: 主键
  - `hospital_id`: 医疗机构ID（外键，支持多租户隔离）
  - `department_code`, `department_name`: 科室信息
  - `version_id`, `version_name`: 模型版本信息（外键）
  - `dimension_code`, `dimension_name`: 维度信息
  - `benchmark_value`: 基准值（Numeric(15,2)）
  - `created_at`, `updated_at`: 时间戳

- **约束**：
  - 唯一约束：`(hospital_id, department_code, version_id, dimension_code)` 确保同一医疗机构内不会有重复的科室-版本-维度组合

- **索引**：
  - `hospital_id`: 支持多租户查询
  - `department_code`: 支持科室筛选
  - `version_id`: 支持版本筛选
  - `dimension_code`: 支持维度筛选

- **关系**：
  - `hospital`: 关联到 Hospital 模型
  - `version`: 关联到 ModelVersion 模型

### 2. 更新关联模型

**文件**: `backend/app/models/hospital.py`
- 添加了 `cost_benchmarks` 反向关系

**文件**: `backend/app/models/model_version.py`
- 添加了 `cost_benchmarks` 反向关系

**文件**: `backend/app/models/__init__.py`
- 导入并导出 `CostBenchmark` 模型

### 3. 创建 Alembic 迁移

**文件**: `backend/alembic/versions/20251127_add_cost_benchmarks.py`

- **Revision ID**: `20251127_add_cost_benchmarks`
- **Down Revision**: `20251127_add_orientation_values`

迁移脚本包含：
- 创建 `cost_benchmarks` 表
- 创建所有必需的索引
- 创建外键约束（CASCADE 删除）
- 创建唯一约束
- 完整的 downgrade 支持

### 4. 执行迁移

成功执行了数据库迁移：
```bash
alembic upgrade head
```

## 验证测试

### 测试 1: 模型结构验证
✅ 模型导入成功
✅ 表名正确
✅ 所有字段存在
✅ 关系定义正确
✅ 唯一约束存在
✅ 反向关系定义正确

### 测试 2: CRUD 操作验证
✅ 创建记录成功
✅ 查询记录成功
✅ 多租户过滤成功
✅ 唯一约束生效（正确阻止重复记录）
✅ 更新记录成功
✅ 关系查询成功
✅ 删除记录成功

### 测试 3: 迁移回滚验证
✅ 降级迁移成功（表被删除）
✅ 升级迁移成功（表被重新创建）

## 数据库表结构

```sql
Table "public.cost_benchmarks"
     Column      |            Type             | Nullable | Default
-----------------+-----------------------------+----------+---------------------------
 id              | integer                     | not null | nextval(...)
 hospital_id     | integer                     | not null |
 department_code | character varying(50)       | not null |
 department_name | character varying(100)      | not null |
 version_id      | integer                     | not null |
 version_name    | character varying(100)      | not null |
 dimension_code  | character varying(100)      | not null |
 dimension_name  | character varying(200)      | not null |
 benchmark_value | numeric(15,2)               | not null |
 created_at      | timestamp without time zone | not null | now()
 updated_at      | timestamp without time zone | not null | now()

Indexes:
    "cost_benchmarks_pkey" PRIMARY KEY, btree (id)
    "ix_cost_benchmarks_department_code" btree (department_code)
    "ix_cost_benchmarks_dimension_code" btree (dimension_code)
    "ix_cost_benchmarks_hospital_id" btree (hospital_id)
    "ix_cost_benchmarks_id" btree (id)
    "ix_cost_benchmarks_version_id" btree (version_id)
    "uq_cost_benchmark_dept_version_dimension" UNIQUE, btree (hospital_id, department_code, version_id, dimension_code)

Foreign-key constraints:
    "fk_cost_benchmarks_hospital_id" FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE
    "fk_cost_benchmarks_version_id" FOREIGN KEY (version_id) REFERENCES model_versions(id) ON DELETE CASCADE
```

## 符合的需求

- ✅ **需求 1.1**: 支持成本基准数据管理
- ✅ **需求 2.4**: 创建时自动关联医疗机构
- ✅ **需求 6.1**: 多租户数据隔离（通过 hospital_id）
- ✅ **需求 6.2**: 创建时自动关联当前医疗机构

## 下一步

模型和迁移已完成，可以继续实施：
- 任务 2: 创建 Pydantic Schemas
- 任务 3: 实现后端 API 端点

## 技术细节

### 多租户隔离设计
- 所有查询必须包含 `hospital_id` 过滤
- 唯一约束包含 `hospital_id`，确保不同医疗机构可以有相同的科室-版本-维度组合
- 外键使用 CASCADE 删除，确保医疗机构删除时相关数据也被清理

### 数据完整性
- 使用 Numeric 类型存储基准值，避免浮点数精度问题
- 外键约束确保引用的医疗机构和模型版本存在
- 唯一约束防止重复数据

### 性能优化
- 为常用查询字段创建索引
- 复合唯一约束同时作为索引使用
