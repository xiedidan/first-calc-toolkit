# 权重值修复说明

## 问题描述

在业务价值明细表中，末级维度的"全院业务价值"和"科室业务价值"显示的值与模型结构中设定的权重不一致。

## 问题原因

数据生成脚本 `populate_report_data.py` 中的 `generate_workload_value` 函数在生成随机数据时，**随机生成了权重值**，而不是从模型节点中读取实际配置的权重。

### 原代码问题

```python
def generate_workload_value(node: ModelNode, use_random: bool) -> tuple:
    if use_random:
        # 问题：随机生成权重，而不是使用模型节点的权重
        if "门诊" in node.name or "诊察" in node.name:
            workload = Decimal(str(random.randint(500, 2000)))
            weight = Decimal(str(random.uniform(20, 50)))  # ❌ 随机生成
        # ... 其他情况
        value = workload * weight
```

## 解决方案

修改 `generate_workload_value` 函数，让权重始终从模型节点读取，并确保业务价值计算公式正确：

```python
def generate_workload_value(node: ModelNode, use_random: bool) -> tuple:
    # ✅ 权重始终从模型节点读取
    weight = node.weight if node.weight is not None else Decimal("0")
    
    if use_random:
        # 只随机生成工作量（收入）
        if "门诊" in node.name or "诊察" in node.name:
            workload = Decimal(str(random.randint(500, 2000)))
        # ... 其他情况
        
        # ✅ 业务价值 = 工作量（收入）× 权重
        value = workload * weight
    else:
        workload = Decimal("0")
        value = Decimal("0")
    
    return workload, weight, value
```

### 计算公式

**业务价值 = 工作量（收入）× 权重**

- `workload`：工作量，即该维度的总收入
- `weight`：权重/单价，从模型节点配置中读取
- `value`：业务价值，计算结果

## 修改内容

**文件**: `backend/populate_report_data.py`

**主要改动**:
1. 权重 (`weight`) 始终从 `node.weight` 读取
2. 只有工作量 (`workload`) 使用随机值生成
3. 价值 (`value`) = 工作量 × 权重（使用模型权重）

## 验证步骤

### 1. 重新生成数据

运行数据生成脚本，使用随机工作量但使用模型权重：

```bash
python backend/populate_report_data.py --period 2025-10 --random
```

### 2. 检查权重值

查询数据库验证权重值是否正确：

```sql
-- 检查计算结果中的权重是否与模型节点一致
SELECT 
    cr.node_id,
    cr.node_name,
    cr.weight AS result_weight,
    mn.weight AS model_weight,
    CASE 
        WHEN cr.weight = mn.weight THEN '✓ 一致'
        ELSE '✗ 不一致'
    END AS status
FROM calculation_results cr
LEFT JOIN model_nodes mn ON cr.node_id = mn.id
WHERE cr.task_id = 'YOUR_TASK_ID'
    AND cr.department_id = 3
    AND cr.node_type = 'dimension'
ORDER BY cr.node_id;
```

### 3. 前端验证

1. 访问业务价值报表页面
2. 选择评估月份
3. 点击某个科室的"查看明细"
4. 检查末级维度的"全院业务价值"列
5. 对比模型版本管理中的权重设置

**预期结果**:
- 末级维度的"全院业务价值"应该显示模型中配置的权重值
- 末级维度的"科室业务价值"应该与"全院业务价值"一致
- 非末级维度的这两列应该显示"-"

## 数据流程

```
模型节点 (model_nodes)
    ↓
    weight (权重/单价)
    ↓
数据生成脚本 (populate_report_data.py)
    ↓
    读取 node.weight
    ↓
计算结果表 (calculation_results)
    ↓
    存储 weight 字段
    ↓
API接口 (get_results_detail)
    ↓
    读取 result.weight
    ↓
前端显示
    ↓
    "全院业务价值" 和 "科室业务价值"
```

## 注意事项

1. **历史数据**: 已经生成的历史数据中的权重值可能不正确，需要重新生成
2. **模型版本**: 确保使用正确的模型版本生成数据
3. **权重配置**: 在模型版本管理中正确配置各维度的权重值
4. **数据一致性**: 重新生成数据后，旧的任务数据会被清理

## 相关文件

- `backend/populate_report_data.py` - 数据生成脚本（已修复）
- `backend/app/api/calculation_tasks.py` - API接口
- `backend/app/models/calculation_task.py` - 数据模型
- `backend/app/models/model_node.py` - 模型节点
- `frontend/src/views/Results.vue` - 前端页面

## 总结

修复后，业务价值明细表中的"全院业务价值"和"科室业务价值"将正确显示模型中配置的权重值，确保数据的准确性和一致性。
