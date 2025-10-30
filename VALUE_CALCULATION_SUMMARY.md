# 业务价值计算公式说明

## 核心公式

```
业务价值 = 工作量（收入）× 权重
```

## 字段说明

### 1. 工作量 (workload)
- **定义**：该维度的总收入
- **来源**：
  - 测试环境：随机生成（`populate_report_data.py`）
  - 生产环境：从HIS系统或数据仓库读取实际收入数据
- **单位**：元（人民币）

### 2. 权重 (weight)
- **定义**：权重/单价，用于将收入转换为业务价值
- **来源**：从模型节点配置中读取（`model_nodes.weight`）
- **配置位置**：模型版本管理 → 模型结构 → 各维度节点
- **单位**：无量纲或根据业务定义

### 3. 业务价值 (value)
- **定义**：该维度对医院业务的贡献价值
- **计算**：`value = workload × weight`
- **用途**：
  - 评估各维度的业务贡献
  - 计算科室绩效
  - 分配资源和奖金

## 数据流程

```
模型配置
    ↓
model_nodes.weight (权重配置)
    ↓
数据生成/计算
    ↓
calculation_results.workload (工作量/收入)
calculation_results.weight (权重，从模型读取)
calculation_results.value (业务价值 = workload × weight)
    ↓
API接口
    ↓
前端展示
```

## 代码实现

### 数据生成脚本 (`populate_report_data.py`)

```python
def generate_workload_value(node: ModelNode, use_random: bool) -> tuple:
    """生成工作量和业务价值"""
    # 1. 权重从模型节点读取
    weight = node.weight if node.weight is not None else Decimal("0")
    
    if use_random:
        # 2. 随机生成工作量（测试用）
        workload = Decimal(str(random.randint(100, 2000)))
        
        # 3. 计算业务价值 = 工作量 × 权重
        value = workload * weight
    else:
        workload = Decimal("0")
        value = Decimal("0")
    
    return workload, weight, value
```

### 数据库存储 (`calculation_results`)

```sql
CREATE TABLE calculation_results (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(100) NOT NULL,
    department_id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    node_name VARCHAR(255) NOT NULL,
    workload DECIMAL(20, 4),      -- 工作量（收入）
    weight DECIMAL(10, 4),        -- 权重（从模型读取）
    value DECIMAL(20, 4),         -- 业务价值 = workload × weight
    ratio DECIMAL(10, 4),         -- 占比
    ...
);
```

### API接口 (`calculation_tasks.py`)

```python
# 末级维度显示
row = {
    "workload": node.workload,              # 工作量
    "hospital_value": str(node.weight),     # 全院业务价值（权重）
    "dept_value": str(node.weight),         # 科室业务价值（权重）
    "amount": node.value,                   # 金额（业务价值）
    "ratio": node.ratio,                    # 占比
}
```

## 示例计算

### 示例1：门诊诊察

```
工作量（收入）: 1,000 元
权重/单价: 55
业务价值 = 1,000 × 55 = 55,000
```

### 示例2：检查化验

```
工作量（收入）: 500 元
权重/单价: 3.49
业务价值 = 500 × 3.49 = 1,745
```

### 示例3：普通治疗甲级

```
工作量（收入）: 600 元
权重/单价: 18
业务价值 = 600 × 18 = 10,800
```

## 前端展示

在业务价值明细表中：

| 维度名称 | 工作量 | 全院业务价值 | 业务导向 | 科室业务价值 | 金额 | 占比 |
|---------|--------|-------------|---------|-------------|------|------|
| 门诊诊察 | 1,000 | 55 | 基础诊疗 | 55 | 55,000 | 10% |
| 会诊 | 600 | 60 | 疑难病例 | 60 | 36,000 | 6% |
| 检查化验 | 500 | 3.49 | 辅助诊断 | 3.49 | 1,745 | 5% |

**说明**：
- **工作量**：该维度的总收入
- **全院业务价值**：权重/单价（从模型配置读取）
- **科室业务价值**：权重/单价（暂时与全院一致）
- **金额**：业务价值 = 工作量 × 权重

## 汇总计算

### 非末级维度

非末级维度的工作量和金额由子维度汇总：

```python
def calculate_sum_from_children(node):
    """计算节点的工作量和金额（从子节点汇总）"""
    if not node.children:
        return node.workload, node.value
    
    total_workload = 0
    total_amount = 0
    for child in node.children:
        child_workload, child_amount = calculate_sum_from_children(child)
        total_workload += child_workload
        total_amount += child_amount
    
    return total_workload, total_amount
```

### 序列汇总

序列的业务价值 = 该序列下所有维度的业务价值之和：

```python
sequence_value = sum(dimension.value for dimension in dimensions)
```

## 验证方法

运行验证脚本：

```bash
python backend/verify_value_calculation.py
```

预期输出：
```
✓ 所有测试通过！
计算公式正确：业务价值 = 工作量（收入）× 权重
```

## 注意事项

1. **权重配置**：确保在模型版本管理中正确配置各维度的权重
2. **数据一致性**：权重应该从模型节点读取，不应该随机生成
3. **精度处理**：使用 `Decimal` 类型确保计算精度
4. **单位统一**：工作量和业务价值的单位应该统一（通常为元）
5. **历史数据**：修改计算公式后，需要重新生成历史数据

## 相关文件

- `backend/populate_report_data.py` - 数据生成脚本
- `backend/app/api/calculation_tasks.py` - API接口
- `backend/verify_value_calculation.py` - 验证脚本
- `WEIGHT_VALUE_FIX.md` - 权重值修复说明
