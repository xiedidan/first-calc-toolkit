# 业务明细价值显示修复

## 问题描述

在业务明细页面中，全院业务价值和科室业务价值显示完全一样，没有体现导向调整的效果。

## 根本原因（双重问题）

### 问题1: API层错误使用字段
API返回的树形表格数据中，`hospital_value`和`dept_value`两个字段都错误地使用了`node.weight`：

```python
# 错误代码
"hospital_value": str(node.weight) if node.weight is not None else "-",
"dept_value": str(node.weight) if node.weight is not None else "-",
```

### 问题2: 计算流程使用原始权重（更严重）
**Step 5（价值汇总）在计算时使用了`model_nodes.weight`（原始权重），而不是`calculation_results.weight`（调整后权重）！**

这导致即使Step 3a正确调整了权重，Step 5在汇总时仍然使用原始权重计算，使得调整失效。

## 数据流分析

### 1. 数据库层（calculation_results表）
- `weight`: 科室业务价值（经过导向调整）
- `original_weight`: 全院业务价值（未调整）

### 2. Schema层（DimensionDetail）
正确构建：
```python
hospital_value=result.original_weight or result.weight,
dept_value=result.weight,
```

### 3. API响应层（树形表格数据）
**错误**：两个字段都使用了`node.weight`
**正确**：应该使用`node.hospital_value`和`node.dept_value`

## 修复方案

### 修复位置1：Step 5计算流程（最关键）

**文件**: `backend/standard_workflow_templates/step5_value_aggregation.sql`

#### 1.1 dimension_results CTE（第68行）
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

#### 1.2 非叶子节点插入（第186行）
```sql
# 修复前
ms.weight,
ms.weight as original_weight,  -- ❌ 非叶子节点不应有original_weight

# 修复后
ms.weight,
NULL as original_weight,  -- ✓ 非叶子节点的值是汇总来的
```

### 修复位置2：科室明细API（/results/detail）

**文件**: `backend/app/api/calculation_tasks.py` 第553-556行

```python
# 修复前
"hospital_value": str(node.weight) if node.weight is not None else "-",
"dept_value": str(node.weight) if node.weight is not None else "-",

# 修复后
"hospital_value": str(node.hospital_value) if node.hospital_value is not None else "-",
"dept_value": str(node.dept_value) if node.dept_value is not None else "-",
```

### 修复位置3：全院汇总API（/results/hospital-detail）

**文件**: `backend/app/api/calculation_tasks.py`

#### 2.1 DimensionDetail构建（第730行左右）
```python
# 添加缺失字段
dim = DimensionDetail(
    ...
    hospital_value=result.weight,  # 全院汇总时，两个值相同
    dept_value=result.weight,
    ...
)
```

#### 2.2 树形节点构建（第797-799行）
```python
# 修复前
"hospital_value": str(node.weight) if node.weight is not None else "-",
"dept_value": str(node.weight) if node.weight is not None else "-",

# 修复后
"hospital_value": str(node.hospital_value) if node.hospital_value is not None else "-",
"dept_value": str(node.dept_value) if node.dept_value is not None else "-",
```

## 修复步骤

### 1. 更新Step 5的SQL模板
```bash
python fix_step5_weight_issue.py
```

### 2. 重新运行计算任务
```sql
-- 删除旧的计算结果
DELETE FROM calculation_results WHERE task_id = 'your-task-id';
DELETE FROM orientation_adjustment_details WHERE task_id = 'your-task-id';

-- 通过API重新创建计算任务
```

### 3. 重启后端服务
```bash
# 应用API层的修复
cd backend
conda activate hospital-backend
python -m uvicorn app.main:app --reload
```

## 验证方法

### 1. 验证计算结果
```bash
python verify_weight_adjustment.py <task_id>
```

这个脚本会检查：
- 叶子节点是否有`original_weight`
- 非叶子节点的`original_weight`是否为NULL
- 有多少维度被调整
- 导向调整明细记录

### 2. 数据库验证
```sql
-- 检查叶子节点
SELECT 
    node_name,
    weight as 科室价值,
    original_weight as 全院价值,
    CASE 
        WHEN original_weight IS NULL THEN '❌ 缺失'
        WHEN original_weight = weight THEN '⚠️  未调整'
        ELSE '✓ 已调整'
    END as 状态
FROM calculation_results
WHERE task_id = 'your-task-id'
    AND node_type = 'dimension'
    AND workload > 0  -- 叶子节点
ORDER BY node_name;

-- 检查非叶子节点
SELECT 
    node_type,
    node_name,
    original_weight,
    CASE 
        WHEN original_weight IS NULL THEN '✓ 正确'
        ELSE '❌ 不应有值'
    END as 状态
FROM calculation_results
WHERE task_id = 'your-task-id'
    AND workload = 0  -- 非叶子节点
ORDER BY node_type, node_name;
```

### 3. 前端验证
1. 打开业务明细页面
2. 选择一个有导向调整的科室
3. 检查表格中的"全院业务价值"和"科室业务价值"列
4. 确认两列数值不同（有导向调整的维度）

## 预期效果

修复后：
- **有导向调整的维度**：全院业务价值 ≠ 科室业务价值
- **无导向调整的维度**：全院业务价值 = 科室业务价值
- **全院汇总页面**：两列数值相同（因为是汇总数据）

## 相关文件

- `backend/app/api/calculation_tasks.py` - API实现
- `backend/app/schemas/calculation_task.py` - Schema定义
- `frontend/src/views/Results.vue` - 前端展示
- `test_detail_values.py` - 测试脚本

## 问题影响范围

### 严重程度：高
- **计算流程问题**导致所有导向调整失效
- 即使配置了导向规则，最终计算结果仍使用原始权重
- 影响所有使用导向调整功能的计算任务

### 受影响的功能
1. 业务明细报表（显示错误）
2. 科室价值计算（计算错误）
3. 导向调整功能（完全失效）

## 根本原因分析

### 数据流
```
Step 2: 插入叶子节点
  └─> weight = mn.weight
  └─> original_weight = mn.weight  ✓

Step 3a: 调整叶子节点
  └─> UPDATE weight = adjusted_weight  ✓
  └─> original_weight 保持不变  ✓

Step 5: 汇总非叶子节点
  └─> 读取 ms.weight (model_nodes)  ❌ 错误！
  └─> 应该读取 cr.weight (calculation_results)  ✓
```

### 为什么会出现这个问题
1. Step 5的CTE从`calculation_results`读取数据
2. 但JOIN了`model_structure`（来自`model_nodes`）
3. 错误地使用了`ms.weight`而不是`cr.weight`
4. 导致汇总时使用的是原始权重，调整失效

## 注意事项

1. **必须先修复Step 5，再重新运行计算任务**
2. 旧的计算结果需要删除并重新计算
3. 前端代码和Schema定义是正确的
4. API层的修复是次要的（显示层问题）
5. 全院汇总时，两个值应该相同（因为是所有科室的汇总）

## 相关工作流步骤

需要检查的步骤顺序：
1. Step 1: 数据准备（生成charge_details）
2. Step 2: 维度统计（插入叶子节点，设置original_weight）
3. **Step 3a: 导向调整（更新weight，保持original_weight）** ← 关键
4. Step 3b: 指标计算（可选）
5. **Step 5: 价值汇总（使用调整后的weight）** ← 修复点
