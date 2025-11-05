# 汇总表数据修复说明

## 问题描述

汇总表（`calculation_summaries`）中的医生/护理/医技价值与明细表（`calculation_results`）的总额对不上。

## 问题原因

### 原代码问题

```python
# 6.3 计算序列汇总值（基于维度值求和）
for seq_node in sequence_nodes:
    # ❌ 问题：只统计直接子维度
    dimensions = db.query(CalculationResult).filter(
        CalculationResult.parent_id == seq_node.id,  # 只查询直接子节点
        CalculationResult.node_type == "dimension"
    ).all()
    
    sequence_value = sum((d.value or Decimal("0")) for d in dimensions)
```

**问题**：
- 只统计了序列的**直接子维度**（一级维度）
- 如果维度有多层嵌套（二级、三级维度），这些维度的价值会被遗漏
- 导致序列汇总值远小于实际值

### 数据结构示例

```
医生序列 (sequence)
├── 门诊 (dimension, level 1)
│   ├── 门诊诊察 (dimension, level 2)
│   │   ├── 普通诊察 (dimension, level 3, 叶子节点, value=1000)
│   │   ├── 会诊 (dimension, level 3, 叶子节点, value=600)
│   │   └── MDT (dimension, level 3, 叶子节点, value=400)
│   └── 门诊治疗 (dimension, level 2)
│       ├── 甲级 (dimension, level 3, 叶子节点, value=600)
│       └── 乙级 (dimension, level 3, 叶子节点, value=500)
└── 住院 (dimension, level 1)
    └── ...
```

**原逻辑**：
- 只统计"门诊"和"住院"（一级维度）
- 但"门诊"和"住院"本身没有价值（非叶子节点）
- 真正的价值在三级维度（叶子节点）

**正确逻辑**：
- 应该统计所有叶子节点的价值：1000 + 600 + 400 + 600 + 500 + ... = 总价值

## 解决方案

### 修复后的代码

```python
# 6.3 计算序列汇总值（基于维度值求和）
for seq_node in sequence_nodes:
    # ✅ 查询所有维度
    all_dimensions = db.query(CalculationResult).filter(
        CalculationResult.task_id == task_id,
        CalculationResult.department_id == dept.id,
        CalculationResult.node_type == "dimension"
    ).all()
    
    # 构建父子关系映射
    dimension_map = {d.node_id: d for d in all_dimensions}
    
    # 找出属于该序列的所有维度
    def belongs_to_sequence(dim_result, seq_id):
        """判断维度是否属于某个序列"""
        current = dim_result
        while current:
            if current.parent_id == seq_id:
                return True
            # 查找父节点
            current = dimension_map.get(current.parent_id)
        return False
    
    # 筛选出属于该序列的维度
    sequence_dimensions = [
        d for d in all_dimensions 
        if belongs_to_sequence(d, seq_node.id)
    ]
    
    # 找出末级维度（叶子节点）
    parent_ids = {d.parent_id for d in all_dimensions}
    leaf_dimensions = [
        d for d in sequence_dimensions
        if d.node_id not in parent_ids
    ]
    
    # ✅ 汇总末级维度的价值
    sequence_value = sum((d.value or Decimal("0")) for d in leaf_dimensions)
```

### 关键改进

1. **查询所有维度**：不限制 `parent_id`，查询所有维度
2. **递归判断归属**：通过 `belongs_to_sequence` 函数递归向上查找，判断维度是否属于某个序列
3. **只统计叶子节点**：找出没有子节点的维度（叶子节点），只统计它们的价值
4. **避免重复计算**：非叶子节点的价值不计入汇总（它们的价值应该等于子节点之和）

## 验证方法

### 1. 重新生成数据

```bash
python backend/populate_report_data.py --period 2025-10 --random
```

### 2. 检查汇总表

查询汇总表数据：

```sql
SELECT 
    department_id,
    doctor_value,
    nurse_value,
    tech_value,
    total_value
FROM calculation_summaries
WHERE task_id = 'YOUR_TASK_ID'
ORDER BY department_id;
```

### 3. 验证明细表总和

对比明细表中各序列的叶子节点价值总和：

```sql
-- 医生序列的叶子节点价值总和
WITH leaf_nodes AS (
    SELECT cr.node_id, cr.value
    FROM calculation_results cr
    WHERE cr.task_id = 'YOUR_TASK_ID'
        AND cr.department_id = 3
        AND cr.node_type = 'dimension'
        AND cr.node_id NOT IN (
            SELECT DISTINCT parent_id 
            FROM calculation_results 
            WHERE task_id = 'YOUR_TASK_ID' 
                AND department_id = 3
                AND parent_id IS NOT NULL
        )
)
SELECT 
    '医生序列' AS sequence_name,
    SUM(ln.value) AS total_value
FROM leaf_nodes ln
INNER JOIN model_nodes mn ON ln.node_id = mn.id
WHERE mn.parent_id IN (
    SELECT id FROM model_nodes 
    WHERE node_type = 'sequence' 
        AND name LIKE '%医生%'
);
```

### 4. 前端验证

1. 访问业务价值报表页面
2. 查看汇总表的医生/护理/医技价值
3. 点击"查看明细"，查看明细表
4. 手动计算明细表中各序列的总和
5. 对比汇总表和明细表的数值是否一致

**预期结果**：
- 汇总表的医生价值 = 明细表中医生序列所有叶子节点的价值之和
- 汇总表的护理价值 = 明细表中护理序列所有叶子节点的价值之和
- 汇总表的医技价值 = 明细表中医技序列所有叶子节点的价值之和
- 汇总表的总价值 = 医生价值 + 护理价值 + 医技价值

## 数据流程

```
维度数据生成
    ↓
calculation_results (所有维度)
    ├── 一级维度 (非叶子节点，value = 子节点之和)
    ├── 二级维度 (非叶子节点，value = 子节点之和)
    └── 三级维度 (叶子节点，value = workload × weight)
    ↓
序列汇总计算
    ↓
    1. 找出属于该序列的所有维度
    2. 筛选出叶子节点
    3. 汇总叶子节点的价值
    ↓
calculation_results (序列)
    ├── 医生序列 (value = 医生序列叶子节点之和)
    ├── 护理序列 (value = 护理序列叶子节点之和)
    └── 医技序列 (value = 医技序列叶子节点之和)
    ↓
汇总表生成
    ↓
calculation_summaries
    ├── doctor_value (从序列结果读取)
    ├── nurse_value (从序列结果读取)
    ├── tech_value (从序列结果读取)
    └── total_value (三者之和)
```

## 注意事项

1. **叶子节点判断**：叶子节点是指没有子节点的维度，它们的 `node_id` 不会出现在其他节点的 `parent_id` 中
2. **递归查找**：通过递归向上查找父节点，判断维度是否属于某个序列
3. **避免重复**：非叶子节点的价值不应该计入汇总，因为它们的价值已经包含在子节点中
4. **性能考虑**：对于大量数据，可以考虑使用数据库的递归查询（CTE）来优化性能

## 相关文件

- `backend/populate_report_data.py` - 数据生成脚本（已修复）
- `backend/app/models/calculation_task.py` - 数据模型
- `SUMMARY_TABLE_FIX.md` - 本文档

## 总结

修复后，汇总表的数据将正确反映明细表中各序列叶子节点的价值总和，确保数据的一致性和准确性。
