# 手术室护理维度代码修复

## 问题描述

任务 `0a0ab1a0-f202-48e2-9666-40674e129887` (2025-10) 中没有手术室护理数据，尽管：
1. 步骤118的SQL已经包含手术室护理维度计算
2. `workload_statistics` 表中有手术数据
3. 任务创建时间在SQL更新之后

## 根本原因

**模型版本代码不一致**：

- **版本1**（旧版本）：使用完整代码
  - `dim-nur-proc-or-large` (大手术护理)
  - `dim-nur-proc-or-mid` (中手术护理)
  - `dim-nur-proc-or-tiny` (小手术护理)

- **版本26**（当前激活版本）：使用简化代码
  - `dim-nur-or-large` (大手术护理)
  - `dim-nur-or-mid` (中手术护理)
  - `dim-nur-or-tiny` (小手术护理)

- **SQL中的代码**：使用完整代码 `dim-nur-proc-or-*`
  - 导致无法匹配版本26的节点
  - JOIN条件失败，没有数据插入

## 解决方案

### 1. 代码替换

修改步骤118的SQL，将完整代码替换为简化代码：

```sql
-- 修改前
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-proc-or-large' AND mn.version_id = {version_id}

-- 修改后
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-or-large' AND mn.version_id = {version_id}
```

同样的替换应用于：
- `dim-nur-proc-or-mid` → `dim-nur-or-mid`
- `dim-nur-proc-or-tiny` → `dim-nur-or-tiny`

### 2. 执行脚本

```bash
python update_nursing_or_sql_codes.py
```

### 3. 验证

执行测试查询验证SQL能够匹配数据：

```sql
SELECT 
    mn.id as node_id,
    mn.code,
    mn.name,
    d.id as dept_id,
    d.his_name,
    ws.stat_value
FROM workload_statistics ws
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-or-large' AND mn.version_id = 26
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = 1
WHERE ws.stat_month = '2025-10'
  AND ws.stat_type = 'dim-nur-or-large'
  AND d.is_active = TRUE;
```

预期结果：返回1行数据（手术窒科室，工作量=1）

## 数据对比

### workload_statistics 中的手术数据 (2025-10)

| stat_type | department_code | stat_value |
|-----------|----------------|------------|
| dim-nur-or-large | FHL01 | 1.0000 |
| dim-nur-or-mid | FHL01 | 21.0000 |
| dim-nur-or-tiny | FHL01 | 1293.0000 |

### 版本26中的手术室护理维度

| 代码 | 名称 | 权重 |
|------|------|------|
| dim-nur-or-large | 大手术护理 | 350.0000 |
| dim-nur-or-mid | 中手术护理 | 180.0000 |
| dim-nur-or-tiny | 小手术护理 | 15.0000 |

### 科室配置

| ID | HIS代码 | HIS名称 | 核算单元代码 | 核算单元名称 |
|----|---------|---------|--------------|--------------|
| 21 | 111 | 手术窒 | FHL01 | 手术窒 |

## 影响范围

### 已修复
- ✅ 步骤118的SQL代码已更新
- ✅ SQL能够正确匹配版本26的节点
- ✅ 测试查询返回正确数据

### 需要操作
- ⚠️ **重新运行计算任务**：旧任务（如 `0a0ab1a0-f202-48e2-9666-40674e129887`）不会自动更新
- ⚠️ 创建新的计算任务以验证手术室护理数据

## 预期结果

重新运行计算任务后，`calculation_results` 表中应包含：

```sql
SELECT 
    node_code,
    node_name,
    COUNT(*) as dept_count,
    SUM(workload) as total_workload,
    SUM(value) as total_value
FROM calculation_results
WHERE task_id = 'new-task-id'
  AND node_code IN ('dim-nur-or-large', 'dim-nur-or-mid', 'dim-nur-or-tiny')
GROUP BY node_code, node_name;
```

预期：
- `dim-nur-or-large`: 1个科室，工作量=1，价值=350
- `dim-nur-or-mid`: 1个科室，工作量=21，价值=3780
- `dim-nur-or-tiny`: 1个科室，工作量=1293，价值=19395

## 相关文件

- **修复脚本**：`update_nursing_or_sql_codes.py`
- **原始实现**：`add_nursing_or_dimensions.py`
- **数据库表**：`calculation_steps` (步骤ID: 118)

## 经验教训

1. **模型版本一致性**：不同版本的模型可能使用不同的代码规范
2. **SQL模板灵活性**：SQL模板应该能够适配不同版本的代码规范
3. **测试覆盖**：应该测试SQL在不同模型版本下的执行情况
4. **代码规范统一**：建议统一使用简化代码或完整代码，避免混用

## 日期

2025-12-08

## 状态

✅ 已修复，等待用户重新运行计算任务验证
