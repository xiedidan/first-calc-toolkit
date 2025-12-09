# 手术管理维度实现

## 概述

为计算流程31的步骤2（护理业务价值计算）添加了手术管理维度的计算逻辑。

## 背景

在护理序列的模型结构中，存在手术管理相关的维度，但在步骤2的SQL中没有实现这些维度的计算：

- `dim-nur-op` (手术管理) - 父维度
  - `dim-nur-op-3` (乙级手术管理) - 权重 0.05
  - `dim-nur-op-4` (甲级手术管理) - 权重 0.08
  - `dim-nur-op-acad` (学科手术管理) - 权重 0.10
  - `dim-nur-op-other` (其他级别手术管理) - 权重 0.03

## 数据来源

手术管理维度的数据来自 `workload_statistics` 表：

| model_nodes 代码 | workload_statistics 代码 | 维度名称 | 权重 |
|-----------------|------------------------|---------|------|
| dim-nur-op-3 | dim-nur-op-3 | 乙级手术管理 | 0.05 |
| dim-nur-op-4 | dim-nur-op-4 | 甲级手术管理 | 0.08 |
| dim-nur-op-acad | dim-nur-op-acad | 学科手术管理 | 0.10 |
| dim-nur-op-other | dim-nur-op-other | 其他级别手术管理 | 0.03 |

**注意**：手术管理维度的代码在 `model_nodes` 和 `workload_statistics` 中是一致的。

## 实际数据情况 (2025-10)

### workload_statistics 中的数据

| stat_type | department_code | stat_value | 说明 |
|-----------|----------------|------------|------|
| dim-nur-op-3 | BHL01 | 21 | 眼科一病区，乙级手术管理 |
| dim-nur-op-other | BHL01 | 611 | 眼科一病区，其他级别手术管理 |
| dim-nur-op-other | BHL02 | 682 | 眼科二病区，其他级别手术管理 |

**说明**：
- 没有 `dim-nur-op-4` (甲级手术管理) 的数据
- 没有 `dim-nur-op-acad` (学科手术管理) 的数据
- 这是正常的，因为不是所有科室都有所有级别的手术

## SQL实现

为每个手术管理子维度添加了独立的INSERT语句：

```sql
-- 15. 乙级手术管理 (dim-nur-op-3)
INSERT INTO calculation_results (...)
SELECT
    '{task_id}' as task_id,
    mn.id as node_id,
    d.id as department_id,
    'dimension' as node_type,
    mn.name as node_name,
    mn.code as node_code,
    mn.parent_id as parent_id,
    ws.stat_value as workload,
    mn.weight,
    mn.weight as original_weight,
    ws.stat_value * mn.weight as value,
    NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-op-3' AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-op-3'
  AND d.is_active = TRUE;
```

类似的SQL也添加了其他3个手术管理维度。

## 关键设计

1. **代码一致性**：
   - `model_nodes.code` 和 `workload_statistics.stat_type` 使用相同的代码
   - 例如：都是 `dim-nur-op-3`，不需要映射

2. **科室关联**：
   - 通过 `departments.accounting_unit_code` 关联
   - 只统计 `is_active = TRUE` 的科室

3. **数据完整性**：
   - 包含所有必需字段：`node_id`, `node_code`, `parent_id` 等
   - 设置 `original_weight = weight`，用于后续导向调整

## 修改文件

- **脚本**：`add_nursing_op_dimensions.py`
- **数据库表**：`calculation_steps` (步骤ID: 118)
- **修改内容**：在步骤2的SQL末尾追加手术管理维度的计算逻辑

## 验证方法

### 1. 检查SQL是否更新

```sql
SELECT LENGTH(code_content) as sql_length
FROM calculation_steps 
WHERE workflow_id = 31 AND sort_order = 2.00;
```

预期结果：SQL长度约为 20606 字符（原来是 16726 字符）

### 2. 检查是否包含新维度

```sql
SELECT code_content 
FROM calculation_steps 
WHERE workflow_id = 31 AND sort_order = 2.00;
```

搜索关键字：`dim-nur-op-3`, `dim-nur-op-4`, `dim-nur-op-acad`, `dim-nur-op-other`

### 3. 测试SQL匹配

```sql
-- 测试乙级手术管理
SELECT 
    mn.id as node_id,
    mn.code,
    mn.name,
    d.id as dept_id,
    d.his_name,
    ws.stat_value,
    ws.stat_value * mn.weight as value
FROM workload_statistics ws
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-op-3' AND mn.version_id = 26
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = 1
WHERE ws.stat_month = '2025-10'
  AND ws.stat_type = 'dim-nur-op-3'
  AND d.is_active = TRUE;
```

预期结果：返回1行数据（眼科一病区，工作量=21，价值=1.05）

### 4. 运行计算任务

创建新的计算任务，检查 `calculation_results` 表中是否有手术管理维度的数据：

```sql
SELECT 
    node_code,
    node_name,
    COUNT(*) as dept_count,
    SUM(workload) as total_workload,
    SUM(value) as total_value
FROM calculation_results
WHERE task_id = 'your-task-id'
  AND node_code IN ('dim-nur-op-3', 'dim-nur-op-4', 'dim-nur-op-acad', 'dim-nur-op-other')
GROUP BY node_code, node_name;
```

预期结果（基于2025-10数据）：
- `dim-nur-op-3`: 1个科室，工作量=21，价值=1.05
- `dim-nur-op-other`: 2个科室，工作量=1293，价值=38.79

## 注意事项

1. **数据依赖**：
   - 需要 `workload_statistics` 表中有对应的手术管理统计数据
   - 统计类型必须是 `dim-nur-op-3/4/acad/other`

2. **科室配置**：
   - 科室的 `accounting_unit_code` 必须与 `workload_statistics.department_code` 匹配
   - 科室必须是激活状态（`is_active = TRUE`）

3. **模型版本**：
   - 确保激活的模型版本中包含这些维度节点
   - 维度的 `parent_id` 必须正确指向 `dim-nur-op` (手术管理)

4. **数据可选性**：
   - 不是所有科室都有所有级别的手术管理数据
   - 没有数据的维度不会插入记录，这是正常的

## 影响范围

- ✅ 步骤2：护理业务价值计算 - 新增4个维度的计算
- ✅ 步骤5：业务价值汇总 - 自动包含新维度（通过树形结构汇总）
- ✅ 前端报表：自动显示新维度数据

## 与手术室护理的区别

| 维度类型 | 父维度 | 数据来源 | 说明 |
|---------|--------|---------|------|
| 手术室护理 | dim-nur-or | workload_statistics | 手术室的护理工作（大/中/小手术） |
| 手术管理 | dim-nur-op | workload_statistics | 手术的管理工作（甲/乙/学科/其他级别） |

两者是不同的维度，分别统计不同的工作内容。

## 日期

2025-12-08

## 状态

✅ 已实现，等待用户重新运行计算任务验证
