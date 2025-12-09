# 医生业务价值计算流程实现文档

## 概述

为模型版本26创建了"医生业务价值计算流程"，用于统计医生序列各末级维度的工作量和业务价值。

## 流程信息

- **流程ID**: 31
- **流程名称**: 医生业务价值计算流程
- **模型版本**: 26 (2025年迭代版-宁波眼科v1.7)
- **医院ID**: 1
- **步骤数量**: 1

## 步骤详情

### 步骤1: 医生业务价值计算

- **步骤ID**: 117
- **代码类型**: SQL
- **数据源ID**: 3 (系统数据源)
- **执行顺序**: 1.00

## 计算逻辑

该步骤统计医生序列下的所有末级维度，分为9个部分：

### 1. 门诊-诊察类维度
- **维度代码**: `dim-doc-out-diag%`
- **数据来源**: charge_details (业务类型='门诊')
- **关联方式**: 通过 dimension_item_mappings 映射
- **工作量**: 收费金额总和
- **价值计算**: 工作量 × 权重

### 2. 门诊-诊断类维度
- **维度代码**: `dim-doc-out-eval%`
- **包含**: 检查化验、中草药、治疗手术
- **数据来源**: charge_details (业务类型='门诊')
- **关联方式**: 通过 dimension_item_mappings 映射
- **工作量**: 收费金额总和
- **价值计算**: 工作量 × 权重

### 3. 门诊-治疗类维度
- **维度代码**: `dim-doc-out-tr%`
- **包含**: 甲级治疗、乙级治疗、丙级治疗、其他治疗
- **数据来源**: charge_details (业务类型='门诊')
- **关联方式**: 通过 dimension_item_mappings 映射
- **工作量**: 收费金额总和
- **价值计算**: 工作量 × 权重

### 4. 住院-诊察类维度
- **维度代码**: `dim-doc-in-diag%`
- **数据来源**: charge_details (业务类型='住院')
- **关联方式**: 通过 dimension_item_mappings 映射
- **工作量**: 收费金额总和
- **价值计算**: 工作量 × 权重

### 5. 住院-病例价值
- **维度代码**: `dim-doc-in-case`
- **数据来源**: charge_details (业务类型='住院')
- **工作量**: 住院病例数 (按 patient_id 去重计数)
- **权重**: 50元/例
- **价值计算**: 病例数 × 50

### 6. 住院-诊断类维度
- **维度代码**: `dim-doc-in-eval%`
- **包含**: 检查化验、中草药、治疗手术
- **数据来源**: charge_details (业务类型='住院')
- **关联方式**: 通过 dimension_item_mappings 映射
- **工作量**: 收费金额总和
- **价值计算**: 工作量 × 权重

### 7. 住院-治疗类维度
- **维度代码**: `dim-doc-in-tr%`
- **包含**: 甲级治疗、乙级治疗、丙级治疗、其他治疗
- **数据来源**: charge_details (业务类型='住院')
- **关联方式**: 通过 dimension_item_mappings 映射
- **工作量**: 收费金额总和
- **价值计算**: 工作量 × 权重

### 8. 手术-门诊类维度
- **维度代码**: `dim-doc-sur-out%`
- **包含**: 学科手术、甲级手术A/B/C/D、乙级手术、丙级手术、丁级手术、术中加收、其他手术
- **数据来源**: charge_details (业务类型='门诊')
- **关联方式**: 通过 dimension_item_mappings 映射
- **工作量**: 收费金额总和
- **价值计算**: 工作量 × 权重

### 9. 手术-住院类维度
- **维度代码**: `dim-doc-sur-in%`
- **包含**: 学科手术、甲级手术A/B/C/D、乙级手术、丙级手术、丁级手术、术中加收、其他手术
- **数据来源**: charge_details (业务类型='住院')
- **关联方式**: 通过 dimension_item_mappings 映射
- **工作量**: 收费金额总和
- **价值计算**: 工作量 × 权重

## 数据表关系

```
charge_details (收费明细)
    ├─ item_code → dimension_item_mappings.item_code (收费项目映射)
    │                └─ dimension_code → model_nodes.code (维度节点)
    └─ prescribing_dept_code → departments.his_code (开单科室)

workload_statistics (工作量统计)
    └─ 目前不包含医生相关数据
```

## 输出结果

结果写入 `calculation_results` 表，包含以下字段：

- `task_id`: 计算任务ID
- `node_id`: 节点ID
- `department_id`: 科室ID
- `node_type`: 'dimension'
- `node_name`: 节点名称
- `node_code`: 节点编码
- `parent_id`: 父节点ID
- `workload`: 工作量
- `weight`: 权重/单价
- `original_weight`: 原始权重
- `value`: 价值 (workload × weight)
- `created_at`: 创建时间

## 参数占位符

SQL模板支持以下参数占位符：

- `{task_id}`: 计算任务ID
- `{current_year_month}`: 当期年月 (格式: YYYY-MM)
- `{hospital_id}`: 医疗机构ID
- `{version_id}`: 模型版本ID

## 使用方法

### 1. 通过前端界面

1. 进入「计算流程管理」
2. 找到"医生业务价值计算流程"
3. 点击「测试」或「执行」按钮
4. 选择计算周期（如：2023-10）
5. 查看执行结果

### 2. 通过API

```python
# 创建计算任务
POST /api/v1/calculation-tasks
{
    "model_version_id": 26,
    "workflow_id": 31,
    "period": "2023-10",
    "description": "测试医生业务价值计算"
}

# 查询结果
GET /api/v1/calculation-tasks/{task_id}/results
```

### 3. 通过测试脚本

```bash
# 创建测试任务
python test_doctor_workflow.py

# 查询结果
psql -h 47.108.227.254 -p 50016 -U root -d hospital_value \
  -c "SELECT * FROM calculation_results WHERE task_id = 'test-doctor-xxx' LIMIT 10;"
```

## 验证检查

### 1. 检查维度覆盖

```sql
-- 查看医生序列下的所有末级维度
SELECT id, name, code, is_leaf, weight, unit
FROM model_nodes
WHERE version_id = 26
  AND parent_id IN (
    SELECT id FROM model_nodes 
    WHERE version_id = 26 
      AND parent_id = (SELECT id FROM model_nodes WHERE version_id = 26 AND name = '医生')
  )
  AND is_leaf = TRUE
ORDER BY code;
```

### 2. 检查映射数据

```sql
-- 查看医生相关的收费项目映射
SELECT DISTINCT dimension_code, COUNT(*) as item_count
FROM dimension_item_mappings
WHERE dimension_code LIKE 'dim-doc%'
  AND hospital_id = 1
GROUP BY dimension_code
ORDER BY dimension_code;
```

### 3. 检查收费数据

```sql
-- 查看测试周期的收费数据
SELECT business_type, COUNT(*) as record_count, SUM(amount) as total_amount
FROM charge_details
WHERE TO_CHAR(charge_time, 'YYYY-MM') = '2023-10'
GROUP BY business_type;
```

## 注意事项

1. **数据源配置**: 步骤使用数据源ID=3（系统数据源），确保该数据源已正确配置并启用

2. **业务类型字段**: charge_details表必须包含business_type字段（'门诊'/'住院'）

3. **映射完整性**: dimension_item_mappings表必须包含所有医生相关维度的映射关系

4. **科室匹配**: departments表的his_code必须与charge_details的prescribing_dept_code匹配

5. **批量模式**: 该流程设计为批量模式，一次性处理所有科室，不需要指定department_ids

6. **权重来源**: 权重从model_nodes表读取，确保所有末级维度都已配置权重

## 后续扩展

### 建议添加的步骤

1. **步骤2: 医生维度汇总** - 汇总各二级维度（诊察、诊断、治疗）的价值
2. **步骤3: 医生序列汇总** - 汇总医生序列总价值
3. **步骤4: 导向调整** - 根据导向规则调整权重
4. **步骤5: 占比计算** - 计算各维度在科室中的占比

### 性能优化建议

1. 为charge_details表添加复合索引：`(business_type, charge_time, item_code)`
2. 为dimension_item_mappings表添加复合索引：`(item_code, hospital_id, dimension_code)`
3. 考虑按月分区charge_details表

## 相关文件

- `create_doctor_workflow.py` - 流程创建脚本
- `test_doctor_workflow.py` - 测试脚本
- `backend/app/tasks/calculation_tasks.py` - 任务执行逻辑
- `backend/app/models/calculation_workflow.py` - 流程模型
- `backend/app/models/calculation_step.py` - 步骤模型

## 创建时间

2025-12-05

## 创建人

AI Assistant (Kiro)
