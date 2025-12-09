# 权重调整问题快速修复指南

## 问题症状
- 业务明细中"全院业务价值"和"科室业务价值"完全相同
- 配置了导向规则但没有效果
- 数据库中`weight`和`original_weight`字段值相同

## 快速修复（5分钟）

### 1. 更新Step 5的SQL模板
```bash
python fix_step5_weight_issue.py
```

输入`y`确认更新。

### 2. 重启后端服务
```bash
cd backend
conda activate hospital-backend
python -m uvicorn app.main:app --reload
```

### 3. 删除旧的计算结果
在数据库中执行：
```sql
-- 替换为你的任务ID
DELETE FROM calculation_results WHERE task_id = 'your-task-id';
DELETE FROM orientation_adjustment_details WHERE task_id = 'your-task-id';
```

### 4. 重新运行计算任务
通过前端或API重新创建计算任务。

### 5. 验证修复
```bash
python verify_weight_adjustment.py your-task-id
```

## 预期结果

### 修复前
```
维度A | weight=100 | original=100 | ⚠️  未调整
维度B | weight=200 | original=200 | ⚠️  未调整
```

### 修复后
```
维度A | weight=120 | original=100 | ✓ 已调整 +20%
维度B | weight=180 | original=200 | ✓ 已调整 -10%
```

## 如果仍然没有调整

检查以下配置：

### 1. 导向规则配置
```sql
SELECT * FROM orientation_rules WHERE hospital_id = 1;
```
确保有规则配置。

### 2. 导向基准值
```sql
SELECT * FROM orientation_benchmarks WHERE hospital_id = 1;
```
确保科室有基准值。

### 3. 导向实际值
```sql
SELECT * FROM orientation_values 
WHERE hospital_id = 1 
  AND year_month = '2025-11';
```
确保有当月的实际值数据。

### 4. 导向阶梯
```sql
SELECT * FROM orientation_ladders WHERE hospital_id = 1;
```
确保有阶梯配置。

### 5. 模型节点配置
```sql
SELECT 
    name,
    orientation_rule_ids,
    array_length(orientation_rule_ids, 1) as rule_count
FROM model_nodes
WHERE version_id = 1
  AND orientation_rule_ids IS NOT NULL;
```
确保维度节点关联了导向规则。

## 常见问题

### Q: 更新后仍然显示相同？
A: 确保删除了旧的计算结果并重新运行任务。

### Q: 部分维度调整，部分没有？
A: 正常现象。只有配置了导向规则且有数据的维度才会调整。

### Q: 非叶子节点的original_weight是什么？
A: 应该是NULL。非叶子节点的值是汇总来的，不需要original_weight。

### Q: 全院汇总页面两列相同？
A: 正常。全院汇总是所有科室的汇总，没有科室级别的调整。

## 技术细节

### 修复内容
1. **Step 5 dimension_results CTE**: 使用`cr.weight`而不是`ms.weight`
2. **Step 5 非叶子节点插入**: `original_weight`设为NULL
3. **API层**: 使用`node.hospital_value`和`node.dept_value`

### 数据流
```
model_nodes.weight (全院业务价值)
    ↓
Step 2: calculation_results.original_weight = mn.weight
Step 2: calculation_results.weight = mn.weight
    ↓
Step 3a: calculation_results.weight = adjusted_weight (调整)
Step 3a: calculation_results.original_weight 保持不变
    ↓
Step 5: 使用 cr.weight (调整后) 汇总
    ↓
API: hospital_value = original_weight
API: dept_value = weight
```

## 相关文件
- `backend/standard_workflow_templates/step5_value_aggregation.sql` - 修复的SQL
- `backend/app/api/calculation_tasks.py` - API修复
- `fix_step5_weight_issue.py` - 更新脚本
- `verify_weight_adjustment.py` - 验证脚本
- `DETAIL_VALUES_FIX.md` - 详细文档
