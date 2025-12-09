# 核算单元字段清理

## 问题描述

`calculation_results` 表中存在冗余字段：
- `accounting_unit_code`
- `accounting_unit_name`

这些字段是冗余的，因为 `department_id` 本身就是核算单元的ID，可以通过关联 `departments` 表获取相关信息。

## 解决方案

### 1. 数据库迁移

创建迁移文件删除冗余字段：
- 文件：`backend/alembic/versions/20251208_remove_redundant_accounting_unit_fields.py`
- Revision ID: `20251208_remove_accounting_unit`
- 删除索引：`ix_calculation_results_accounting_unit`
- 删除字段：`accounting_unit_code`, `accounting_unit_name`

### 2. 执行结果

```sql
-- 删除前的表结构
calculation_results (
    id, task_id, department_id, node_id, node_name, node_code, node_type,
    parent_id, workload, weight, value, ratio, created_at, original_weight,
    accounting_unit_code, accounting_unit_name  -- 冗余字段
)

-- 删除后的表结构
calculation_results (
    id, task_id, department_id, node_id, node_name, node_code, node_type,
    parent_id, workload, weight, value, ratio, created_at, original_weight
)
```

### 3. 数据验证

验证任务 `ae546d7b-5de8-40ec-b4a7-9e80502bd3ed` 的数据：
- 13个序列节点
- 每个科室（核算单元）的每个序列只出现一次
- 数据完整性正常

## 影响范围

### 后端
- `calculation_results` 表结构变更
- 通过 `department_id` 关联 `departments` 表获取核算单元信息

### 前端
- 无影响（前端通过 API 获取数据，API 层会处理关联查询）

## 注意事项

1. **数据查询**：需要核算单元信息时，通过 JOIN `departments` 表获取
2. **API 响应**：如需返回核算单元信息，在 API 层预加载
3. **向后兼容**：旧的 SQL 模板如果引用了这些字段需要更新

## 迁移执行

```bash
cd backend
alembic upgrade head
```

## 日期

2025-12-08
