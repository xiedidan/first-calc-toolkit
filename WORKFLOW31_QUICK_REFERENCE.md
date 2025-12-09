# 工作流31核算序列过滤 - 快速参考

## 一句话总结
工作流31的医生、护理、医技步骤现在会根据科室的`accounting_sequences`字段过滤，只统计配置了对应序列的科室。

## 快速配置（3步）

### 1. 运行配置工具
```bash
python configure_department_sequences.py
```

### 2. 选择自动配置
- 选项1: 配置临床科室 → `['医生', '护理']`
- 选项2: 配置医技科室 → `['医技']`
- 选项3: 配置综合科室 → `['医生', '护理', '医技']`

### 3. 验证配置
```sql
-- 查看配置统计
SELECT 
  unnest(accounting_sequences) as sequence,
  COUNT(*) as count
FROM departments
WHERE accounting_sequences IS NOT NULL
GROUP BY sequence;
```

## 配置规则速查

| 科室类型 | 核算序列 | 示例科室 |
|---------|---------|---------|
| 临床科室 | `['医生', '护理']` | 内科、外科、妇产科、儿科 |
| 医技科室 | `['医技']` | 检验科、影像科、超声科、病理科 |
| 综合科室 | `['医生', '护理', '医技']` | 急诊科、ICU、手术室 |
| 行政科室 | `[]` 或 `null` | 院办、财务科、总务科 |

## 常用SQL

### 批量配置临床科室
```sql
UPDATE departments 
SET accounting_sequences = ARRAY['医生', '护理']
WHERE his_name LIKE '%科' 
  AND his_name NOT LIKE '%检验%'
  AND his_name NOT LIKE '%影像%'
  AND is_active = TRUE;
```

### 批量配置医技科室
```sql
UPDATE departments 
SET accounting_sequences = ARRAY['医技']
WHERE (his_name LIKE '%检验%' 
       OR his_name LIKE '%影像%'
       OR his_name LIKE '%超声%'
       OR his_name LIKE '%病理%')
  AND is_active = TRUE;
```

### 查看未配置的科室
```sql
SELECT his_code, his_name 
FROM departments 
WHERE (accounting_sequences IS NULL 
       OR array_length(accounting_sequences, 1) = 0)
  AND is_active = TRUE;
```

### 查看某科室的配置
```sql
SELECT his_name, accounting_sequences
FROM departments
WHERE his_name = '内科';
```

## 验证计算结果

### 检查医生序列
```sql
SELECT DISTINCT d.his_name, d.accounting_sequences
FROM calculation_results cr
JOIN departments d ON cr.department_id = d.id
JOIN model_nodes mn ON cr.node_id = mn.id
WHERE cr.task_id = 'your-task-id'
  AND mn.code LIKE 'dim-doc-%';
-- 应该只看到包含'医生'的科室
```

### 检查护理序列
```sql
-- 将 dim-doc-% 改为 dim-nur-%
-- 应该只看到包含'护理'的科室
```

### 检查医技序列
```sql
-- 将 dim-doc-% 改为 dim-med-%
-- 应该只看到包含'医技'的科室
```

## 故障排查

### 问题1: 统计结果为0
**原因**: 科室未配置核算序列  
**解决**: 运行 `python configure_department_sequences.py`

### 问题2: 某些科室未被统计
**原因**: 科室的`accounting_sequences`不包含对应序列  
**解决**: 在科室管理页面编辑该科室，添加对应序列

### 问题3: 不确定如何配置
**原因**: 不清楚科室应该属于哪个序列  
**解决**: 参考配置规则速查表，或咨询业务人员

## 临时回滚

如果需要临时恢复到升级前的行为（所有科室都参与统计）：

```sql
UPDATE departments 
SET accounting_sequences = ARRAY['医生', '护理', '医技']
WHERE is_active = TRUE;
```

## 相关文档

- 详细文档: `WORKFLOW31_ACCOUNTING_SEQUENCES_UPGRADE.md`
- 功能说明: `ACCOUNTING_SEQUENCES_FEATURE.md`
- 完成总结: `WORKFLOW31_UPGRADE_COMPLETE.md`

## 关键点记忆

1. ✓ 三个步骤已更新：医生(117)、护理(118)、医技(119)
2. ✓ 过滤条件：`'序列名' = ANY(d.accounting_sequences)`
3. ⚠️ 必须配置核算序列，否则不会被统计
4. 💡 使用配置工具快速批量配置
5. 🔍 验证配置后再执行计算任务
