# 占比计算修复说明

## 问题描述

明细表中的占比显示不正确。

## 占比定义

**占比 = 该维度的金额 / 同一父节点下所有兄弟节点的金额总和 × 100%**

### 示例

```
医生序列
├── 门诊 (金额=5000)
│   ├── 门诊诊察 (金额=2000, 占比=2000/5000=40%)
│   ├── 门诊诊断 (金额=1500, 占比=1500/5000=30%)
│   └── 门诊治疗 (金额=1500, 占比=1500/5000=30%)
└── 住院 (金额=5000)
    └── 住院诊察 (金额=2000, 占比=2000/5000=40%)
```

## 修复内容

### 1. 数据生成脚本修复

**文件**: `backend/populate_report_data.py`

**问题**: 原来的 `calculate_dimension_ratios` 函数只计算某个序列下直接子维度的占比，对于多层嵌套结构不适用。

**修复**: 重写为 `calculate_all_dimension_ratios` 函数，按父节点分组计算所有维度的占比。

```python
def calculate_all_dimension_ratios(db: Session, task_id: str, dept_id: int):
    """计算所有维度的占比
    
    占比 = 该维度的价值 / 同一父节点下所有兄弟节点的价值总和 × 100%
    """
    # 获取该科室的所有维度结果
    all_dimensions = db.query(CalculationResult).filter(
        CalculationResult.task_id == task_id,
        CalculationResult.department_id == dept_id,
        CalculationResult.node_type == "dimension"
    ).all()
    
    # 按父节点分组
    from collections import defaultdict
    parent_groups = defaultdict(list)
    for dim in all_dimensions:
        parent_groups[dim.parent_id].append(dim)
    
    # 为每个分组计算占比
    for parent_id, siblings in parent_groups.items():
        # 计算该父节点下所有子节点的价值总和
        total_value = sum((d.value or Decimal("0")) for d in siblings)
        
        # 更新每个子节点的占比
        if total_value > 0:
            for dim in siblings:
                dim_value = dim.value or Decimal("0")
                dim.ratio = (dim_value / total_value * 100).quantize(Decimal("0.01"))
        else:
            for dim in siblings:
                dim.ratio = Decimal("0")
    
    db.commit()
```

### 2. API接口修复

**文件**: `backend/app/api/calculation_tasks.py`

**问题**: 
1. 非末级维度的金额是在API中重新计算的（子维度之和），但占比还是用的数据库中的旧值
2. 没有根据实际的金额重新计算占比

**修复**: 在 `flatten_tree_to_rows` 函数中，根据实际金额重新计算占比。

```python
def collect_all_nodes(node, level_names, siblings_total=None):
    """递归收集所有节点（末级和非末级）
    
    siblings_total: 同级节点的金额总和（用于计算占比）
    """
    # 计算当前节点的金额
    if is_leaf:
        current_amount = node.value or 0
    else:
        _, current_amount = calculate_sum_from_children(node)
    
    # 计算占比
    if siblings_total and siblings_total > 0:
        ratio = (current_amount / siblings_total * 100)
        ratio = Decimal(str(ratio)).quantize(Decimal("0.01"))
    else:
        ratio = node.ratio or 0
    
    # 递归处理子节点时，传入子节点的金额总和
    if node.children:
        children_total = sum(
            (calculate_sum_from_children(child)[1] if child.children else (child.value or 0))
            for child in node.children
        )
        
        for child in node.children:
            collect_all_nodes(child, new_level_names, children_total)
```

## 计算逻辑

### 数据生成阶段

1. 生成所有维度的数据（工作量、权重、金额）
2. 按父节点分组
3. 计算每组的金额总和
4. 计算每个维度的占比 = 该维度金额 / 同组金额总和 × 100%
5. 保存到数据库

### API展示阶段

1. 从数据库读取数据
2. 对于非末级维度，重新计算金额（子维度之和）
3. 根据实际金额重新计算占比
4. 返回给前端

## 验证方法

### 1. 重新生成数据

```bash
python backend/populate_report_data.py --period 2025-10 --random
```

### 2. 检查数据库中的占比

```sql
-- 查看某个父节点下的子节点占比
SELECT 
    node_name,
    value,
    ratio,
    ROUND(value / SUM(value) OVER (PARTITION BY parent_id) * 100, 2) AS calculated_ratio
FROM calculation_results
WHERE task_id = 'YOUR_TASK_ID'
    AND department_id = 3
    AND parent_id = 某个父节点ID
ORDER BY node_id;
```

### 3. 前端验证

1. 访问业务价值报表页面
2. 点击"查看明细"
3. 检查每一级维度的占比
4. 验证同一父节点下的所有子节点占比之和 ≈ 100%

**预期结果**:
- 同一父节点下的所有子节点占比之和应该接近100%（可能有小数点误差）
- 每个维度的占比 = 该维度金额 / 同级所有维度金额总和 × 100%

## 示例验证

### 医生序列 - 门诊

假设数据如下：

| 维度 | 金额 | 占比 |
|------|------|------|
| 门诊诊察 | 2000 | 40% |
| 门诊诊断 | 1500 | 30% |
| 门诊治疗 | 1500 | 30% |
| **总计** | **5000** | **100%** |

验证：
- 门诊诊察占比 = 2000 / 5000 × 100% = 40% ✓
- 门诊诊断占比 = 1500 / 5000 × 100% = 30% ✓
- 门诊治疗占比 = 1500 / 5000 × 100% = 30% ✓
- 总和 = 40% + 30% + 30% = 100% ✓

## 注意事项

1. **精度问题**: 使用 `Decimal` 类型确保计算精度，保留2位小数
2. **总和验证**: 同一父节点下的所有子节点占比之和应该接近100%
3. **零值处理**: 如果父节点下所有子节点金额都为0，占比也为0
4. **递归计算**: 对于多层嵌套结构，需要递归计算每一层的占比

## 相关文件

- `backend/populate_report_data.py` - 数据生成脚本（已修复）
- `backend/app/api/calculation_tasks.py` - API接口（已修复）
- `RATIO_CALCULATION_FIX.md` - 本文档

## 总结

修复后，占比计算逻辑正确：
- ✅ 数据生成时按父节点分组计算占比
- ✅ API展示时根据实际金额重新计算占比
- ✅ 同一父节点下的所有子节点占比之和 = 100%
