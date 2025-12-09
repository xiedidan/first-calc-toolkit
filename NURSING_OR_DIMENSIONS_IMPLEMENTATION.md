# 手术室护理维度实现

## 概述

为计算流程31的步骤2（护理业务价值计算）添加了手术室护理维度的计算逻辑。

## 问题描述

在护理序列的模型结构中，存在手术室护理相关的维度，但在步骤2的SQL中没有实现这些维度的计算：

- `dim-nur-proc-or` (手术室) - 父维度
  - `dim-nur-proc-or-large` (大手术护理) - 权重 1200
  - `dim-nur-proc-or-mid` (中手术护理) - 权重 400
  - `dim-nur-proc-or-tiny` (小手术护理) - 权重 20

## 解决方案

### 数据来源

手术室护理维度的数据来自 `workload_statistics` 表，使用以下统计类型：

| model_nodes 代码 | workload_statistics 代码 | 维度名称 | 权重 |
|-----------------|------------------------|---------|------|
| dim-nur-proc-or-large | dim-nur-or-large | 大手术护理 | 1200 |
| dim-nur-proc-or-mid | dim-nur-or-mid | 中手术护理 | 400 |
| dim-nur-proc-or-tiny | dim-nur-or-tiny | 小手术护理 | 20 |

**注意**：`workload_statistics` 表中使用的是简化代码（`dim-nur-or-*`），需要在SQL中映射到 `model_nodes` 的完整代码（`dim-nur-proc-or-*`）。

### SQL实现

为每个手术室护理子维度添加了独立的INSERT语句：

```sql
-- 12. 大手术护理 (dim-nur-proc-or-large)
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
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-proc-or-large' AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-or-large'
  AND d.is_active = TRUE;
```

类似的SQL也添加了中手术护理和小手术护理。

### 关键设计

1. **代码映射**：
   - `model_nodes.code` 使用完整代码：`dim-nur-proc-or-large`
   - `workload_statistics.stat_type` 使用简化代码：`dim-nur-or-large`
   - 在SQL中通过硬编码映射关系

2. **科室关联**：
   - 通过 `departments.accounting_unit_code` 关联
   - 只统计 `is_active = TRUE` 的科室

3. **数据完整性**：
   - 包含所有必需字段：`node_id`, `node_code`, `parent_id` 等
   - 设置 `original_weight = weight`，用于后续导向调整

## 修改文件

- **脚本**：`add_nursing_or_dimensions.py`
- **数据库表**：`calculation_steps` (步骤ID: 118)
- **修改内容**：在步骤2的SQL末尾追加手术室护理维度的计算逻辑

## 验证方法

### 1. 检查SQL是否更新

```sql
SELECT LENGTH(code_content) as sql_length
FROM calculation_steps 
WHERE workflow_id = 31 AND sort_order = 2.00;
```

预期结果：SQL长度约为 16741 字符（原来是 13631 字符）

### 2. 检查是否包含新维度

```sql
SELECT code_content 
FROM calculation_steps 
WHERE workflow_id = 31 AND sort_order = 2.00;
```

搜索关键字：`dim-nur-proc-or-large`, `dim-nur-proc-or-mid`, `dim-nur-proc-or-tiny`

### 3. 运行计算任务

创建新的计算任务，检查 `calculation_results` 表中是否有手术室护理维度的数据：

```sql
SELECT node_code, node_name, COUNT(*) as dept_count, SUM(workload) as total_workload
FROM calculation_results
WHERE task_id = 'your-task-id'
  AND node_code IN ('dim-nur-proc-or-large', 'dim-nur-proc-or-mid', 'dim-nur-proc-or-tiny')
GROUP BY node_code, node_name;
```

## 注意事项

1. **数据依赖**：
   - 需要 `workload_statistics` 表中有对应的手术统计数据
   - 统计类型必须是 `dim-nur-or-large/mid/tiny`

2. **科室配置**：
   - 科室的 `accounting_unit_code` 必须与 `workload_statistics.department_code` 匹配
   - 科室必须是激活状态（`is_active = TRUE`）

3. **模型版本**：
   - 确保激活的模型版本中包含这些维度节点
   - 维度的 `parent_id` 必须正确指向 `dim-nur-proc-or` (手术室)

## 影响范围

- ✅ 步骤2：护理业务价值计算 - 新增3个维度的计算
- ✅ 步骤5：业务价值汇总 - 自动包含新维度（通过树形结构汇总）
- ✅ 前端报表：自动显示新维度数据

## 日期

2025-12-08
