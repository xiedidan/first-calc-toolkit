# Step 5权重问题修复完成

## 修复时间
2025-11-28

## 问题描述
Step 5（业务价值汇总）在计算时使用了`model_nodes.weight`（原始权重），而不是`calculation_results.weight`（经Step 3a调整后的权重），导致导向调整功能完全失效。

## 修复内容

### 1. SQL模板修改
**文件**: `backend/standard_workflow_templates/step5_value_aggregation.sql`

#### 修改1: dimension_results CTE（第62-73行）
```sql
# 修复前
SELECT 
    cr.node_id as dimension_id,
    cr.department_id,
    cr.workload,
    ms.weight,  -- ❌ 使用model_nodes的原始权重
    ms.node_name
FROM calculation_results cr

# 修复后
SELECT 
    cr.node_id as dimension_id,
    cr.department_id,
    cr.workload,
    cr.weight,  -- ✓ 使用calculation_results的调整后权重
    cr.original_weight,
    ms.node_name
FROM calculation_results cr
```

#### 修改2: 非叶子节点插入（第180-186行）
```sql
# 修复前
    0 as workload,
    ms.weight,
    ms.weight as original_weight,  -- ❌ 非叶子节点不应有original_weight
    agg.score as value,

# 修复后
    0 as workload,
    ms.weight,
    NULL as original_weight,  -- ✓ 非叶子节点的值是汇总来的
    agg.score as value,
```

### 2. 数据库更新
已更新以下4个工作流步骤：
- 步骤ID 67: 标准计算流程 / 业务价值汇总
- 步骤ID 75: 标准计算流程-含数据准备-2025-11-21 / 业务价值汇总
- 步骤ID 80: 标准计算流程-含业务导向 / 业务价值汇总
- 步骤ID 85: 标准计算流程-含业务导向_从业务明细开始 / 业务价值汇总

### 3. API层修复
**文件**: `backend/app/api/calculation_tasks.py`

#### 科室明细API（第553-556行）
```python
# 修复前
"hospital_value": str(node.weight),
"dept_value": str(node.weight),

# 修复后
"hospital_value": str(node.hospital_value),
"dept_value": str(node.dept_value),
```

#### 全院汇总API（第730行 + 第797-799行）
- DimensionDetail构建：添加`hospital_value`和`dept_value`字段
- 树形节点构建：使用`node.hospital_value`和`node.dept_value`

## 数据流修复

### 修复前（错误）
```
Step 2: 插入叶子节点
  └─> weight = mn.weight
  └─> original_weight = mn.weight

Step 3a: 调整叶子节点
  └─> UPDATE weight = adjusted_weight
  └─> original_weight 保持不变

Step 5: 汇总非叶子节点
  └─> 读取 ms.weight (model_nodes)  ❌ 使用原始权重！
  └─> 调整失效
```

### 修复后（正确）
```
Step 2: 插入叶子节点
  └─> weight = mn.weight
  └─> original_weight = mn.weight

Step 3a: 调整叶子节点
  └─> UPDATE weight = adjusted_weight
  └─> original_weight 保持不变

Step 5: 汇总非叶子节点
  └─> 读取 cr.weight (calculation_results)  ✓ 使用调整后权重！
  └─> 调整生效
```

## 下一步操作

### 1. 重启后端服务
```bash
# 应用API层的修复
cd backend
conda activate hospital-backend
python -m uvicorn app.main:app --reload
```

### 2. 删除旧的计算结果
```sql
-- 替换为实际的任务ID
DELETE FROM calculation_results WHERE task_id = 'your-task-id';
DELETE FROM orientation_adjustment_details WHERE task_id = 'your-task-id';
```

### 3. 重新运行计算任务
通过前端或API重新创建计算任务。

### 4. 验证修复
```bash
python verify_weight_adjustment.py your-task-id
```

## 预期效果

### 数据库层
```sql
-- 叶子节点
SELECT node_name, weight, original_weight
FROM calculation_results
WHERE task_id = 'xxx' AND workload > 0;

-- 预期: weight ≠ original_weight（有调整的维度）
```

### 前端显示
- 业务明细页面："全院业务价值" ≠ "科室业务价值"
- 体现导向调整的效果

## 相关文件
- `backend/standard_workflow_templates/step5_value_aggregation.sql` - 修复的SQL模板
- `backend/app/api/calculation_tasks.py` - API修复
- `update_step5_direct.py` - 数据库更新脚本
- `verify_weight_adjustment.py` - 验证脚本
- `DETAIL_VALUES_FIX.md` - 详细技术文档
- `QUICK_FIX_WEIGHT_ISSUE.md` - 快速修复指南

## 影响范围
- 所有使用导向调整功能的计算任务
- 业务明细报表显示
- 科室价值计算结果

## 测试建议
1. 创建新的计算任务（使用含业务导向的工作流）
2. 检查`calculation_results`表中的`weight`和`original_weight`字段
3. 验证业务明细页面显示两个不同的价值列
4. 对比调整前后的科室价值变化
