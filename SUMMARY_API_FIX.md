# 科室汇总表API修复

## 问题根源

之前一直在修改数据生成脚本 `populate_report_data.py`，但忽略了一个关键点：
**前端显示的数据是通过API读取的，而不是直接读数据库！**

## 修复方案

### 方案选择

有两种方案：
1. ❌ 修复数据生成脚本，让 `calculation_summaries` 表存储正确的汇总数据
2. ✅ **修改API，实时从 `calculation_results` 表计算汇总数据**

选择方案2的原因：
- 更灵活：不依赖预先存储的汇总表
- 更准确：直接从序列数据计算，确保数据一致性
- 更简单：逻辑清晰，易于维护

### API修改

修改 `backend/app/api/calculation_tasks.py` 中的 `get_results_summary` 函数：

#### 原逻辑（错误）
```python
# 从 calculation_summaries 表读取预先计算的汇总数据
summaries = db.query(CalculationSummary, Department.his_name).join(...).all()
```

#### 新逻辑（正确）
```python
# 从 calculation_results 表读取序列数据，实时计算汇总
sequence_results = db.query(
    CalculationResult.department_id,
    Department.his_name,
    CalculationResult.node_name,
    CalculationResult.value
).filter(
    CalculationResult.node_type == "sequence"  # 只查询序列
).all()

# 按科室分组，根据序列名称分类汇总
for result in sequence_results:
    if "医生" in node_name:
        doctor_value += value
    elif "护理" in node_name:
        nurse_value += value
    elif "医技" in node_name:
        tech_value += value

# 计算占比
total_value = doctor_value + nurse_value + tech_value
doctor_ratio = doctor_value / total_value * 100
...
```

## 计算逻辑

### 1. 数据来源
- 直接从 `calculation_results` 表读取 `node_type='sequence'` 的记录
- 每个序列的 `value` 已经是该序列下所有维度的汇总值

### 2. 序列分类
根据序列名称判断类型：
- **医生序列**：包含"医生"、"医疗"、"医师"、"doctor"、"physician"
- **护理序列**：包含"护理"、"护士"、"nurse"、"nursing"
- **医技序列**：包含"医技"、"技师"、"tech"、"technician"

### 3. 汇总计算
```
科室医生价值 = Σ(该科室所有医生序列的价值)
科室护理价值 = Σ(该科室所有护理序列的价值)
科室医技价值 = Σ(该科室所有医技序列的价值)
科室总价值 = 医生价值 + 护理价值 + 医技价值

医生占比 = 医生价值 / 科室总价值 × 100%
护理占比 = 护理价值 / 科室总价值 × 100%
医技占比 = 医技价值 / 科室总价值 × 100%
```

### 4. 全院汇总
```
全院医生价值 = Σ(所有科室的医生价值)
全院护理价值 = Σ(所有科室的护理价值)
全院医技价值 = Σ(所有科室的医技价值)
全院总价值 = 全院医生价值 + 全院护理价值 + 全院医技价值

全院医生占比 = 全院医生价值 / 全院总价值 × 100%
...
```

## 数据流程

```
1. 数据生成（populate_report_data.py）
   ├─ 为每个维度生成：工作量、权重、价值
   ├─ 计算维度占比（同序列下维度间的占比）
   └─ 计算序列价值（逐级汇总该序列下所有维度的价值）
        └─ 使用 calculate_sum_from_children 递归汇总

2. API读取（get_results_summary）
   ├─ 读取所有序列的价值
   ├─ 按科室分组
   ├─ 根据序列名称分类（医生/护理/医技）
   ├─ 计算科室总价值和占比
   └─ 计算全院汇总

3. 前端显示
   └─ 显示汇总表数据
```

## 关键改进

1. **数据源改变**：从 `calculation_summaries` 改为 `calculation_results`
2. **实时计算**：不依赖预先存储的汇总数据
3. **逻辑清晰**：序列价值 → 科室汇总 → 全院汇总
4. **易于维护**：计算逻辑集中在API中

## 测试验证

### 1. 测试API
```bash
python backend/test_summary_api.py
```

### 2. 测试数据生成
```bash
python backend/populate_report_data.py --period 2025-10 --random
```

### 3. 调试工具
```bash
# 快速检查
python backend/quick_check_summary.py

# 详细调试
python backend/debug_summary_detail.py
```

## 注意事项

### 1. 序列价值的正确性
序列价值必须正确计算（在数据生成时），API只是读取和分类汇总。

确保 `populate_report_data.py` 中的序列价值计算正确：
```python
# 使用逐级汇总算法
def calculate_sum_from_children(node_id: int) -> Decimal:
    # 叶子节点：返回自己的价值
    # 非叶子节点：返回所有子节点价值之和
```

### 2. 序列名称识别
序列分类依赖名称关键词，确保：
- 序列名称包含明确的关键词（医生/护理/医技）
- 支持中英文关键词
- 不区分大小写

### 3. calculation_summaries 表
虽然API不再使用这个表，但可以保留用于：
- 数据备份
- 历史记录
- 性能优化（如果需要）

## 相关文件

- `backend/app/api/calculation_tasks.py` - API实现（已修改）
- `backend/populate_report_data.py` - 数据生成脚本
- `backend/test_summary_api.py` - API测试脚本（新增）
- `backend/quick_check_summary.py` - 快速检查脚本（新增）
- `backend/debug_summary_detail.py` - 详细调试脚本（新增）

## 后续优化

1. **性能优化**：如果数据量大，考虑缓存或使用汇总表
2. **错误处理**：增加更详细的错误提示
3. **日志记录**：记录计算过程，便于调试
4. **单元测试**：添加完整的单元测试覆盖

## 总结

这次修复的关键是：
- ✅ 找到了问题根源：API读取逻辑
- ✅ 采用了更好的方案：实时计算而非预存储
- ✅ 确保了数据一致性：直接从序列数据计算
- ✅ 简化了维护：逻辑清晰，易于理解
