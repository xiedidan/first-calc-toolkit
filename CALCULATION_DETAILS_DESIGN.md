# calculation_details 核算明细表设计方案

## 1. 背景与目标

### 当前问题
- 下钻功能与维度统计逻辑强绑定，需要在API层重复实现统计逻辑
- 下钻查询需要动态判断使用哪个科室字段（开单科室/执行科室）
- 下钻查询需要动态判断业务类型（门诊/住院）
- 统计逻辑分散在多个地方，维护困难

### 目标
- 将统计逻辑统一到计算流程中
- 下钻直接查询 `calculation_details` 表，无需重复统计逻辑
- `calculation_results` 由 `calculation_details` 聚合生成

## 2. 数据流设计

```
charge_details (源数据)
       ↓
   Step 1: 数据准备（从HIS源表生成charge_details）
       ↓
   Step 2: 生成 calculation_details（核算明细表）
       ↓
   Step 3: 聚合生成 calculation_results（维度汇总）
       ↓
   Step 4: 导向调整（更新weight）
       ↓
   Step 5: 价值汇总
```

## 3. calculation_details 表结构

```sql
CREATE TABLE calculation_details (
    id SERIAL PRIMARY KEY,
    hospital_id INTEGER NOT NULL,            -- 医疗机构ID
    task_id VARCHAR(100) NOT NULL,           -- 任务ID
    department_id INTEGER NOT NULL,          -- 科室ID
    department_code VARCHAR(50) NOT NULL,    -- 科室代码
    
    -- 维度信息
    node_id INTEGER NOT NULL,                -- 维度节点ID
    node_code VARCHAR(100) NOT NULL,         -- 维度编码
    node_name VARCHAR(255) NOT NULL,         -- 维度名称
    parent_id INTEGER,                       -- 父节点ID
    
    -- 收费项目信息
    item_code VARCHAR(100) NOT NULL,         -- 收费项目编码
    item_name VARCHAR(200),                  -- 收费项目名称
    item_category VARCHAR(100),              -- 项目类别
    
    -- 业务属性
    business_type VARCHAR(20),               -- 业务类型（门诊/住院）
    
    -- 数值
    amount DECIMAL(20, 4) NOT NULL DEFAULT 0,    -- 金额
    quantity DECIMAL(20, 4) NOT NULL DEFAULT 0,  -- 数量
    
    -- 时间
    period VARCHAR(7) NOT NULL,              -- 统计月份 (YYYY-MM)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 唯一约束
CREATE UNIQUE INDEX uq_calc_details_key 
ON calculation_details(hospital_id, task_id, department_id, node_id, item_code, COALESCE(business_type, ''));
```

## 4. 聚合粒度

按 `(hospital_id, task_id, department_id, node_id, item_code, business_type)` 聚合

## 5. 支持下钻的维度

| 序列 | 维度类型 | 科室字段 | 业务类型 | 支持下钻 |
|------|----------|----------|----------|----------|
| 医生 | 诊断维度 (dim-doc-*-eval-*) | prescribing_dept_code | 门诊/住院 | ✓ |
| 医生 | 手术维度 (dim-doc-sur-*) | executing_dept_code | 门诊/住院 | ✓ |
| 医生 | 其他维度 (dim-doc-*) | executing_dept_code | 门诊/住院 | ✓ |
| 医技 | 所有维度 (dim-tech-*) | executing_dept_code | 不区分 | ✓ |
| 护理 | 收费类维度 (dim-nur-base/collab/tr-*/other) | executing_dept_code | 不区分 | ✓ |
| 护理 | 工作量维度 (dim-nur-bed/trans/op/or/mon) | - | - | ✗ |
| 成本 | 所有维度 | - | - | ✗ |

## 6. 实施状态

- [x] 数据库迁移文件 (`backend/alembic/versions/20251230_add_calculation_details.py`)
- [x] SQLAlchemy 模型 (`backend/app/models/calculation_detail.py`)
- [x] 计算流程 Step 生成 calculation_details (步骤ID: 162, 工作流31)
- [x] 修改下钻 API 使用 calculation_details (`backend/app/api/analysis_reports.py`)
- [x] 测试验证 (`test_calculation_details.py`)

## 7. API 变更说明

下钻 API 现在采用双层查询策略：
1. **优先查询 calculation_details 表**：如果任务执行了"生成核算明细"步骤，直接从预计算的数据中查询
2. **回退到 charge_details 表**：兼容旧任务，使用原有的动态查询逻辑

这种设计确保了：
- 新任务：下钻查询更快，逻辑统一在计算流程中
- 旧任务：仍然可以正常下钻，无需重新计算
