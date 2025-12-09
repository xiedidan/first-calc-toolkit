# 计算结果字段缺失修复

## 问题描述

计算任务执行后，`calculation_results` 表中的记录缺少关键字段：
- `node_code` - 节点编码（空）
- `parent_id` - 父节点ID（空）
- `ratio` - 占比（空）

这导致报表无法正确显示树形结构和占比信息。

## 示例问题数据

```
id: 31406
task_id: f6240cd4-64cb-4dda-bbb6-b0ba1e4a7a6a
department_id: 25
node_id: 22
node_name: 会诊
node_code: (空) ❌
node_type: dimension
parent_id: (空) ❌
workload: 71.0000
weight: 100.0000
value: 7100.0000
ratio: (空) ❌
created_at: 2025-11-20 08:11:25.231033
```

## 根本原因

标准工作流模板的SQL语句中，INSERT语句没有包含这些字段：

**原始SQL（step1）：**
```sql
INSERT INTO calculation_results (
    task_id,
    node_id,
    department_id,
    node_type,
    node_name,
    workload,
    weight,
    value,
    created_at
)
SELECT 
    '{task_id}' as task_id,
    dm.dimension_id as node_id,
    d.id as department_id,
    'dimension' as node_type,
    mn.name as node_name,
    -- ❌ 缺少 node_code
    -- ❌ 缺少 parent_id
    COALESCE(SUM(cd.total_amount), 0) as workload,
    mn.weight,
    COALESCE(SUM(cd.total_amount), 0) * mn.weight as value,
    NOW() as created_at
FROM ...
```

## 修复方案

### 1. 添加缺失字段到INSERT语句

**修复后的SQL：**
```sql
INSERT INTO calculation_results (
    task_id,
    node_id,
    department_id,
    node_type,
    node_name,
    node_code,      -- ✓ 添加
    parent_id,      -- ✓ 添加
    workload,
    weight,
    value,
    created_at
)
SELECT 
    '{task_id}' as task_id,
    dm.dimension_id as node_id,
    d.id as department_id,
    'dimension' as node_type,
    mn.name as node_name,
    mn.code as node_code,           -- ✓ 添加
    mn.parent_id as parent_id,      -- ✓ 添加
    COALESCE(SUM(cd.total_amount), 0) as workload,
    mn.weight,
    COALESCE(SUM(cd.total_amount), 0) * mn.weight as value,
    NOW() as created_at
FROM ...
GROUP BY dm.dimension_id, d.id, mn.name, mn.code, mn.parent_id, mn.weight  -- ✓ 更新GROUP BY
```

### 2. 关于 `ratio` 字段

`ratio` 字段（占比）不在SQL中计算，而是在后端API中动态计算的。这是正确的设计，因为：
- 占比需要知道同级节点的总和
- 不同层级的占比计算方式不同
- 前端展示时才需要计算占比

## 修复的文件

### 1. step1_dimension_catalog.sql
- 添加 `node_code` 和 `parent_id` 字段
- 更新 GROUP BY 子句

### 2. step2_indicator_calculation.sql
- 护理床日数INSERT：添加 `node_code` 和 `parent_id`
- 会诊INSERT：添加 `node_code` 和 `parent_id`
- 更新两个INSERT的GROUP BY子句

### 3. step3_value_aggregation.sql
- 不需要修改（插入到summaries表）

## 验证步骤

### 1. 清空旧数据

```sql
-- 删除旧的测试数据
DELETE FROM calculation_results WHERE task_id LIKE 'test-%';
DELETE FROM calculation_tasks WHERE task_id LIKE 'test-%';
```

### 2. 重新导入工作流模板

```bash
cd backend/standard_workflow_templates
bash import_standard_workflow.sh
```

或者在前端：
1. 进入"计算流程管理"
2. 找到标准工作流
3. 点击"重新导入"按钮

### 3. 创建新的计算任务

在前端创建一个新的计算任务，使用更新后的工作流。

### 4. 检查结果

```sql
-- 查看最新任务的结果
SELECT 
    id,
    task_id,
    node_name,
    node_code,      -- 应该有值
    parent_id,      -- 应该有值（除了顶级节点）
    node_type,
    workload,
    value
FROM calculation_results 
WHERE task_id = (
    SELECT task_id 
    FROM calculation_tasks 
    ORDER BY created_at DESC 
    LIMIT 1
)
ORDER BY node_id
LIMIT 20;
```

**预期结果：**
- `node_code` 应该有值（如果模型节点定义了code）
- `parent_id` 应该有值（除了序列节点）
- 数据应该能构建完整的树形结构

### 5. 检查报表显示

在前端查看：
1. 业务价值汇总表 - 应该正常显示
2. 业务价值明细表 - 应该显示完整的树形结构
3. 全院汇总明细 - 应该正确汇总

## 字段说明

### node_code
- **用途**：节点编码，用于唯一标识维度
- **来源**：`model_nodes.code`
- **可为空**：是（如果模型节点没有定义code）
- **影响**：不影响树形结构，但影响数据追溯

### parent_id
- **用途**：父节点ID，用于构建树形结构
- **来源**：`model_nodes.parent_id`
- **可为空**：是（顶级节点/序列节点）
- **影响**：**关键字段**，缺失会导致无法构建树形结构

### ratio
- **用途**：占比百分比
- **来源**：后端API动态计算
- **可为空**：是（在数据库中）
- **影响**：仅影响显示，不影响数据结构

## 注意事项

### 1. 现有数据处理

如果已经有旧数据，有两个选择：

**选项A：删除重新计算**
```sql
DELETE FROM calculation_results WHERE parent_id IS NULL AND node_type = 'dimension';
DELETE FROM calculation_summaries WHERE task_id IN (
    SELECT DISTINCT task_id FROM calculation_results WHERE parent_id IS NULL
);
```
然后重新运行计算任务。

**选项B：更新现有数据**
```sql
-- 从model_nodes补充缺失的字段
UPDATE calculation_results cr
SET 
    node_code = mn.code,
    parent_id = mn.parent_id
FROM model_nodes mn
WHERE cr.node_id = mn.id
  AND cr.parent_id IS NULL
  AND cr.node_type = 'dimension';
```

### 2. 自定义工作流

如果你创建了自定义的计算步骤，也需要确保INSERT语句包含这些字段：
- `node_code`
- `parent_id`

### 3. 测试建议

在生产环境使用前，建议：
1. 使用测试数据验证
2. 检查树形结构是否完整
3. 验证占比计算是否正确
4. 确认导出功能正常

## 总结

这个修复确保了 `calculation_results` 表中的数据包含构建树形结构所需的所有字段。`parent_id` 是最关键的字段，它使得前端能够正确展示维度的层级关系。

修复后，报表应该能够：
- 正确显示树形结构
- 准确计算各级占比
- 完整展示维度层级
- 支持数据追溯和分析
