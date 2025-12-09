# 业务导向调整步骤更新总结

## 更新时间
2025-11-28

## 更新内容

### 1. 新增数据表
- ✅ `orientation_adjustment_details` - 业务导向调整明细表
- ✅ `cost_values` - 成本值表（额外创建）

### 2. 更新的 SQL 文件
- **旧文件**: `step3a_orientation_adjustment.sql`
- **新文件**: `step3a_orientation_adjustment_with_details.sql`

### 3. 数据库更新
- ✅ 执行迁移：`20251128_orientation_details`
- ✅ 更新工作流步骤：ID 78, Workflow 25

### 4. 主要改进

#### 旧版本（仅更新权重）
```sql
-- 只更新 calculation_results.weight
UPDATE calculation_results
SET weight = adjusted_weight
WHERE ...
```

#### 新版本（记录完整过程）
```sql
-- 1. 插入调整明细
INSERT INTO orientation_adjustment_details (...)
SELECT 
    实际值, 基准值, 导向比例,
    阶梯下限, 阶梯上限, 调整力度,
    原始权重, 调整后权重,
    是否调整, 未调整原因
FROM ...

-- 2. 更新权重
UPDATE calculation_results
SET weight = adjusted_weight
WHERE is_adjusted = TRUE
```

## 新表字段说明

### orientation_adjustment_details 核心字段

| 分类 | 字段 | 说明 |
|------|------|------|
| **输入值** | actual_value | 导向实际值 |
| | benchmark_value | 导向基准值 |
| **中间计算** | orientation_ratio | 导向比例 = 实际值/基准值 |
| **阶梯匹配** | ladder_lower_limit | 阶梯下限 |
| | ladder_upper_limit | 阶梯上限 |
| | adjustment_intensity | 调整力度 |
| **权重调整** | original_weight | 原始权重 |
| | adjusted_weight | 调整后权重 |
| **状态** | is_adjusted | 是否调整 |
| | adjustment_reason | 未调整原因 |

## 使用方式

### 1. 查看调整明细

```sql
SELECT 
    department_name,
    node_name,
    actual_value,
    benchmark_value,
    orientation_ratio,
    adjustment_intensity,
    original_weight,
    adjusted_weight,
    is_adjusted,
    adjustment_reason
FROM orientation_adjustment_details
WHERE task_id = 'your-task-id'
ORDER BY department_name, node_name;
```

### 2. 统计调整效果

```sql
SELECT 
    COUNT(*) as total_records,
    SUM(CASE WHEN is_adjusted THEN 1 ELSE 0 END) as adjusted_count,
    SUM(CASE WHEN NOT is_adjusted THEN 1 ELSE 0 END) as not_adjusted_count
FROM orientation_adjustment_details
WHERE task_id = 'your-task-id';
```

### 3. 查看未调整原因

```sql
SELECT 
    adjustment_reason,
    COUNT(*) as count
FROM orientation_adjustment_details
WHERE task_id = 'your-task-id' 
  AND is_adjusted = FALSE
GROUP BY adjustment_reason;
```

## 前端展示建议

### 调整明细页面
- 表格展示所有调整记录
- 筛选：科室、维度、导向规则、调整状态
- 详情对话框：展示完整计算过程

### 统计图表
- 饼图：调整成功率
- 柱状图：各科室平均调整力度
- 散点图：导向比例 vs 调整力度

## 相关文件

- 📄 `ORIENTATION_ADJUSTMENT_DETAILS_GUIDE.md` - 详细设计文档
- 📄 `backend/standard_workflow_templates/step3a_orientation_adjustment_with_details.sql` - 新 SQL
- 📄 `backend/app/models/orientation_adjustment_detail.py` - 模型定义
- 📄 `backend/alembic/versions/20251128_orientation_details.py` - 迁移文件
- 📄 `update_orientation_adjustment_step.py` - 更新脚本

## 后续工作

### 必需
- [ ] 前端：创建调整明细查询 API
- [ ] 前端：创建调整明细展示页面
- [ ] 测试：验证新流程的计算结果

### 可选
- [ ] 导出：支持导出调整明细到 Excel
- [ ] 分析：添加调整效果分析报表
- [ ] 优化：添加调整明细的数据清理策略

## 注意事项

1. **向后兼容**：旧的 `step3a_orientation_adjustment.sql` 文件保留，可随时回退
2. **数据量**：每次计算会生成大量明细记录，建议定期清理历史数据
3. **性能**：task_id 字段已建立索引，查询性能良好
4. **多租户**：所有查询必须包含 hospital_id 过滤

## 回退方案

如需回退到旧版本：

```python
# 运行更新脚本，但使用旧的 SQL 文件
python update_orientation_adjustment_step.py  # 修改脚本指向旧文件
```

或直接在数据库中更新：

```sql
UPDATE calculation_steps
SET code_content = (SELECT pg_read_file('旧SQL文件路径'))
WHERE id = 78;
```
