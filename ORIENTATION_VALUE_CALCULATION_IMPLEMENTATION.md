# 业务导向价值计算实施总结

## 概述

本次更新在标准计算流程中增加了业务导向调整步骤，实现了基于导向规则动态调整维度学科业务价值的功能。

## 核心变更

### 1. 新增数据表：orientation_values

**用途**: 存储科室在特定月份的业务导向实际取值

**字段设计**:
- `id`: 主键
- `hospital_id`: 医疗机构ID（外键）
- `year_month`: 年月（格式: YYYY-MM）
- `department_code`: 科室代码
- `department_name`: 科室名称
- `orientation_rule_id`: 导向规则ID（外键）
- `actual_value`: 导向实际取值
- `created_at`: 创建时间
- `updated_at`: 更新时间

**唯一约束**: (hospital_id, year_month, department_code, orientation_rule_id)

**数据来源**: 由ETL工程师负责填充，系统不自动生成

### 2. 新增计算步骤：step3a_orientation_adjustment.sql

**执行时机**: 在Step2（维度统计）之后、Step3b（指标计算）之前

**算法逻辑**（基准阶梯型导向）:

```
1. 计算导向比例
   导向比例 = 当月科室导向取值 / 科室导向基准
   
2. 查找管控力度
   根据导向比例从阶梯表中找到对应区间的管控力度
   
3. 调整权重
   调整后的weight = 全院业务价值(model_nodes.weight) × 管控力度
```

**输入参数**:
- `{task_id}`: 计算任务ID
- `{version_id}`: 模型版本ID
- `{year_month}`: 计算年月（格式: YYYY-MM）

**输出**: 更新 calculation_results 表中维度节点的 weight 字段

### 3. 计算流程步骤调整

原有步骤重新编号：

| 旧编号 | 新编号 | 步骤名称 | 文件名 |
|--------|--------|----------|--------|
| Step1 | Step1 | 数据准备 | step1_data_preparation.sql |
| Step2 | Step2 | 维度目录统计 | step2_dimension_catalog.sql |
| - | **Step3a** | **业务导向调整** | **step3a_orientation_adjustment.sql** |
| Step3 | Step3b | 指标计算-护理床日数 | step3b_indicator_calculation.sql |
| Step4 | Step5 | 业务价值汇总 | step5_value_aggregation.sql |

### 4. 数据库迁移

**迁移文件**: `20251127_add_orientation_values.py`

**操作内容**:
- 创建 orientation_values 表
- 创建索引（hospital_id, orientation_rule_id, year_month, department_code）
- 创建唯一约束
- 添加外键约束（hospitals, orientation_rules）

### 5. 模型关系更新

**OrientationRule 模型**:
```python
orientation_values = relationship("OrientationValue", back_populates="orientation_rule", cascade="all, delete-orphan")
```

**Hospital 模型**:
```python
orientation_values = relationship("OrientationValue", back_populates="hospital")
```

**OrientationValue 模型**:
```python
hospital = relationship("Hospital", back_populates="orientation_values")
orientation_rule = relationship("OrientationRule", back_populates="orientation_values")
```

## 使用流程

### 1. 准备导向数据

ETL工程师需要将科室的导向实际值数据导入到 `orientation_values` 表：

```sql
INSERT INTO orientation_values (
    hospital_id, 
    year_month, 
    department_code, 
    department_name, 
    orientation_rule_id, 
    actual_value,
    created_at,
    updated_at
) VALUES (
    1,                    -- 医疗机构ID
    '2025-11',           -- 年月
    'DEPT001',           -- 科室代码
    '内科',              -- 科室名称
    1,                   -- 导向规则ID
    85.5,                -- 导向实际取值
    NOW(),
    NOW()
);
```

### 2. 配置导向规则

在前端"业务导向管理"模块中：
1. 创建导向规则（基准阶梯型）
2. 配置科室基准值
3. 配置阶梯区间和管控力度
4. 在模型节点中关联导向规则

### 3. 导入标准流程

使用更新后的导入脚本：

**Bash**:
```bash
cd backend/standard_workflow_templates
bash import_standard_workflow.sh --version-id 1 --data-source-id 1
```

**PowerShell**:
```powershell
cd backend/standard_workflow_templates
.\import_standard_workflow.ps1 -VersionId 1 -DataSourceId 1
```

### 4. 创建计算任务

在前端创建计算任务时，系统会自动：
1. 执行Step1-2：准备数据和统计维度工作量
2. 执行Step3a：根据导向规则调整维度权重
3. 执行Step3b：计算指标
4. 执行Step5：汇总业务价值

## 技术细节

### 导向比例计算

```sql
CASE 
    WHEN ob.benchmark_value = 0 THEN NULL
    ELSE ov.actual_value / ob.benchmark_value
END as orientation_ratio
```

**注意**: 基准值为0时，导向比例设为NULL，不进行调整

### 阶梯区间匹配

```sql
WHERE oratio.orientation_ratio IS NOT NULL
  AND (ol.lower_limit IS NULL OR oratio.orientation_ratio >= ol.lower_limit)
  AND (ol.upper_limit IS NULL OR oratio.orientation_ratio < ol.upper_limit)
```

**规则**: 
- 左闭右开区间：[lower_limit, upper_limit)
- NULL表示正负无穷

### 权重调整

```sql
UPDATE calculation_results
SET 
    weight = mn.weight * la.adjustment_intensity,
    updated_at = NOW()
WHERE cr.task_id = '{task_id}'
  AND cr.node_type = 'dimension'
  AND mn.orientation_rule_id IS NOT NULL
```

**影响范围**: 仅调整配置了导向规则的维度节点

## 注意事项

### 1. 数据完整性

- 确保 orientation_values 表中有对应月份的数据
- 确保 orientation_benchmarks 表中有对应科室的基准值
- 确保 orientation_ladders 表中有完整的阶梯配置

### 2. 执行顺序

Step3a 必须在 Step2 之后、Step5 之前执行：
- Step2 生成维度节点的初始 weight（从 model_nodes 复制）
- Step3a 调整 weight（应用导向管控力度）
- Step5 使用调整后的 weight 计算价值

### 3. 可选性

- 未配置导向规则的维度不受影响
- 没有导向实际值数据的科室保持原始权重
- Step3a 可以禁用，系统会使用原始权重

### 4. 扩展性

当前仅实现"基准阶梯"型导向，未来可扩展：
- 直接阶梯型导向
- 其他导向类型

## 验证方法

### 1. 检查导向数据

```sql
SELECT * FROM orientation_values 
WHERE year_month = '2025-11' 
  AND hospital_id = 1;
```

### 2. 检查权重调整

```sql
SELECT 
    cr.node_id,
    mn.name as node_name,
    d.name as department_name,
    mn.weight as original_weight,
    cr.weight as adjusted_weight,
    cr.weight / mn.weight as adjustment_ratio
FROM calculation_results cr
INNER JOIN model_nodes mn ON cr.node_id = mn.id
INNER JOIN departments d ON cr.department_id = d.id
WHERE cr.task_id = 'your-task-id'
  AND cr.node_type = 'dimension'
  AND mn.orientation_rule_id IS NOT NULL;
```

### 3. 检查价值计算

```sql
SELECT 
    node_name,
    department_id,
    workload,
    weight,
    value,
    value / NULLIF(workload, 0) as unit_value
FROM calculation_results
WHERE task_id = 'your-task-id'
  AND node_type = 'dimension'
ORDER BY department_id, node_name;
```

## 文件清单

### 新增文件
- `backend/app/models/orientation_value.py` - 导向实际值模型
- `backend/alembic/versions/20251127_add_orientation_values.py` - 数据库迁移
- `backend/standard_workflow_templates/step3a_orientation_adjustment.sql` - 导向调整步骤

### 重命名文件
- `step3_indicator_calculation.sql` → `step3b_indicator_calculation.sql`
- `step4_value_aggregation.sql` → `step5_value_aggregation.sql`

### 修改文件
- `backend/app/models/__init__.py` - 添加 OrientationValue 导入
- `backend/app/models/orientation_rule.py` - 添加 orientation_values 关系
- `backend/app/models/hospital.py` - 添加 orientation_values 关系
- `backend/standard_workflow_templates/import_standard_workflow.sh` - 更新步骤配置
- `backend/standard_workflow_templates/import_standard_workflow.ps1` - 更新步骤配置

## 下一步工作

1. **执行数据库迁移**:
   ```bash
   cd backend
   alembic upgrade head
   ```

2. **准备测试数据**:
   - 在 orientation_values 表中插入测试数据
   - 确保有对应的基准值和阶梯配置

3. **导入标准流程**:
   - 使用更新后的导入脚本
   - 验证5个步骤都已正确创建

4. **创建测试任务**:
   - 选择配置了导向的模型版本
   - 指定有导向数据的计算月份
   - 执行任务并验证结果

5. **前端集成**（可选）:
   - 创建导向实际值管理页面
   - 支持批量导入导向数据
   - 在报表中显示导向调整信息

## 总结

本次更新实现了业务导向对维度价值的动态调整功能，核心思路是：

1. **数据准备**: ETL工程师提供科室导向实际值
2. **规则配置**: 管理员配置导向规则、基准和阶梯
3. **自动计算**: 系统在计算流程中自动应用导向调整
4. **结果输出**: 调整后的权重影响最终的价值汇总

这种设计保持了系统的灵活性，支持不同类型的导向规则，同时不影响未配置导向的维度节点。
