# 工作流31核算序列过滤升级

## 升级概述

为工作流31的医生、护理、医技业务价值计算步骤添加科室核算序列过滤功能。只有在科室的`accounting_sequences`字段中包含对应序列的科室，才会被纳入该序列的业务价值统计。

## 升级内容

### 涉及步骤

| 步骤ID | 步骤名称 | 序列名称 | 说明 |
|--------|----------|----------|------|
| 117 | 医生业务价值计算 | 医生 | 统计医生序列各维度的工作量和业务价值 |
| 118 | 护理业务价值计算 | 护理 | 统计护理序列各维度的工作量和业务价值 |
| 119 | 医技业务价值计算 | 医技 | 统计医技序列各维度的工作量和业务价值 |

### SQL变更

**原SQL**:
```sql
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id}
```

**新SQL**:
```sql
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医生' = ANY(d.accounting_sequences)
```

### 过滤逻辑

使用PostgreSQL的数组操作符 `= ANY()` 检查科室的核算序列数组：

- **医生步骤**: `'医生' = ANY(d.accounting_sequences)`
- **护理步骤**: `'护理' = ANY(d.accounting_sequences)`
- **医技步骤**: `'医技' = ANY(d.accounting_sequences)`

## 业务影响

### 1. 数据统计范围变化

**升级前**:
- 所有科室的收费数据都会被统计到对应序列
- 无法区分科室是否应该参与某个序列的统计

**升级后**:
- 只统计`accounting_sequences`包含对应序列的科室
- 可以精确控制每个科室参与哪些序列的统计

### 2. 使用场景

#### 场景1: 专科科室
```json
{
  "his_name": "内科",
  "accounting_sequences": ["医生", "护理"]
}
```
- ✓ 参与医生序列统计
- ✓ 参与护理序列统计
- ✗ 不参与医技序列统计

#### 场景2: 医技科室
```json
{
  "his_name": "检验科",
  "accounting_sequences": ["医技"]
}
```
- ✗ 不参与医生序列统计
- ✗ 不参与护理序列统计
- ✓ 参与医技序列统计

#### 场景3: 综合科室
```json
{
  "his_name": "急诊科",
  "accounting_sequences": ["医生", "护理", "医技"]
}
```
- ✓ 参与所有序列统计

#### 场景4: 未设置核算序列
```json
{
  "his_name": "行政科",
  "accounting_sequences": null
}
```
- ✗ 不参与任何序列统计

### 3. 数据完整性

**重要**: 升级后需要为所有科室设置合适的核算序列，否则可能导致：
- 统计数据为0或偏少
- 某些科室的业务价值未被统计
- 报表数据不完整

## 执行步骤

### 1. 数据库字段添加
```bash
python add_accounting_sequences_field.py
```

### 2. 更新工作流步骤SQL
```bash
python update_workflow31_accounting_sequences.py
```

### 3. 配置科室核算序列

在科室管理页面为每个科室设置核算序列：

```sql
-- 示例：批量设置临床科室
UPDATE departments 
SET accounting_sequences = ARRAY['医生', '护理']
WHERE his_name LIKE '%科' 
  AND his_name NOT LIKE '%检验%'
  AND his_name NOT LIKE '%影像%'
  AND his_name NOT LIKE '%药剂%';

-- 示例：设置医技科室
UPDATE departments 
SET accounting_sequences = ARRAY['医技']
WHERE his_name IN ('检验科', '影像科', '超声科', '病理科');

-- 示例：设置综合科室
UPDATE departments 
SET accounting_sequences = ARRAY['医生', '护理', '医技']
WHERE his_name IN ('急诊科', 'ICU');
```

### 4. 验证配置

```sql
-- 查看各序列的科室数量
SELECT 
  unnest(accounting_sequences) as sequence,
  COUNT(*) as dept_count
FROM departments
WHERE accounting_sequences IS NOT NULL
  AND hospital_id = 1
GROUP BY sequence;

-- 查看未配置核算序列的科室
SELECT his_code, his_name 
FROM departments 
WHERE (accounting_sequences IS NULL OR array_length(accounting_sequences, 1) = 0)
  AND is_active = TRUE
  AND hospital_id = 1;
```

## 测试验证

### 1. 创建测试任务

```python
# 使用工作流31创建计算任务
# 确保有科室配置了不同的核算序列
```

### 2. 检查计算结果

```sql
-- 查看医生序列的统计结果
SELECT 
  d.his_name,
  d.accounting_sequences,
  COUNT(*) as record_count,
  SUM(cr.value) as total_value
FROM calculation_results cr
JOIN departments d ON cr.department_id = d.id
JOIN model_nodes mn ON cr.node_id = mn.id
WHERE cr.task_id = 'your-task-id'
  AND mn.code LIKE 'dim-doc-%'
GROUP BY d.id, d.his_name, d.accounting_sequences;

-- 验证过滤是否生效
-- 应该只看到accounting_sequences包含'医生'的科室
```

### 3. 对比测试

**测试步骤**:
1. 记录升级前某个任务的统计结果
2. 为科室配置核算序列
3. 使用相同参数重新计算
4. 对比两次结果的差异

**预期结果**:
- 未配置对应序列的科室不再出现在结果中
- 总体业务价值可能减少（因为过滤掉了不相关的科室）
- 数据更加精确和合理

## 回滚方案

如果需要回滚到升级前的行为：

### 方案1: 为所有科室设置全部序列
```sql
UPDATE departments 
SET accounting_sequences = ARRAY['医生', '护理', '医技']
WHERE is_active = TRUE;
```

### 方案2: 修改SQL移除过滤条件
```sql
-- 恢复原始SQL（移除 AND '医生' = ANY(d.accounting_sequences)）
-- 需要重新执行update_workflow31_accounting_sequences.py
-- 并手动修改替换逻辑
```

## 注意事项

### 1. 数据迁移
- 现有科室的`accounting_sequences`字段默认为NULL
- 需要根据业务规则批量设置初始值
- 建议先在测试环境验证配置的合理性

### 2. 性能影响
- 添加了GIN索引支持数组查询
- 过滤条件可能略微影响查询性能
- 但由于减少了统计的数据量，整体性能可能提升

### 3. 业务规则
- 需要明确定义哪些科室应该参与哪些序列
- 建议制定科室核算序列配置规范
- 定期审查和更新科室配置

### 4. 报表影响
- 升级后的统计结果可能与历史数据不一致
- 需要向用户说明变更原因
- 建议保留历史任务结果用于对比

## 相关文件

- `add_accounting_sequences_field.py` - 添加数据库字段
- `update_workflow31_accounting_sequences.py` - 更新工作流SQL
- `get_workflow31_steps.py` - 导出原始SQL
- `workflow31_step117_医生业务价值计算_updated.sql` - 更新后的医生步骤SQL
- `workflow31_step118_护理业务价值计算_updated.sql` - 更新后的护理步骤SQL
- `workflow31_step119_医技业务价值计算_updated.sql` - 更新后的医技步骤SQL
- `ACCOUNTING_SEQUENCES_FEATURE.md` - 核算序列功能文档
- `ACCOUNTING_SEQUENCES_SUMMARY.md` - 功能实现总结

## 后续优化建议

1. **配置界面**: 在科室管理页面添加批量设置核算序列的功能
2. **配置模板**: 提供常见科室类型的核算序列配置模板
3. **验证规则**: 添加配置合理性检查（如检验科不应该有医生序列）
4. **统计报表**: 提供核算序列配置统计和覆盖率报表
5. **审计日志**: 记录核算序列配置的变更历史
