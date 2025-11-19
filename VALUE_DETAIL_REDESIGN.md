# 业务价值明细表重新设计

## 概述

业务价值明细表已重新实现，按照模型结构展示数据，支持多级维度的完整展示。

## 设计要求

### 1. 展示结构

- **每个序列一个Tab**：医生序列、护理序列、医技序列各自独立展示
- **维度结构与模型一致**：直接参考模型版本管理中的模型结构，从对应序列的一级维度开始
- **支持多级维度**：自动适配2-4级维度结构

### 2. 数据列定义

#### 末级维度（叶子节点）
显示以下列：
- **工作量**：维度的总收入
- **全院业务价值**：权重/单价
- **业务导向**：业务导向说明
- **科室业务价值**：暂时与全院业务价值一致
- **金额**：该维度业务价值的金额
- **占比**：该维度业务价值金额在上一级维度总和的占比

#### 非末级维度（父节点）
显示以下列：
- **工作量**：该维度下所有子维度工作量之和
- **金额**：该维度下所有子维度金额之和
- **占比**：该维度业务价值金额在上一级总和的占比
- **其他列**：用"-"表示无效值

## 实现细节

### 后端API改动

**文件**: `backend/app/api/calculation_tasks.py`

主要改动：
1. 修改 `get_results_detail` 函数
2. 重写 `flatten_tree_to_rows` 函数，支持所有节点（末级和非末级）的展示
3. 根据节点是否为叶子节点，决定显示的数据内容

关键逻辑：
```python
def flatten_tree_to_rows(dimensions):
    """将树形结构扁平化为表格行格式 - 包含所有节点"""
    
    def collect_all_nodes(node, level_names):
        # 判断是否为末级维度
        is_leaf = not node.children or len(node.children) == 0
        
        if is_leaf:
            # 末级维度：显示完整信息
            row = {
                "workload": node.workload,
                "hospital_value": node.weight,
                "business_guide": node.business_guide or "-",
                "dept_value": node.weight,
                "amount": node.value,
                "ratio": node.ratio,
            }
        else:
            # 非末级维度：只显示汇总信息
            row = {
                "workload": node.workload,
                "hospital_value": "-",
                "business_guide": "-",
                "dept_value": "-",
                "amount": node.value,
                "ratio": node.ratio,
            }
```

### Schema改动

**文件**: `backend/app/schemas/calculation_task.py`

简化了 `StructureRow` 模型：
```python
class StructureRow(BaseModel):
    """结构表行数据（按模型结构展示）"""
    level1: Optional[str] = None  # 一级维度
    level2: Optional[str] = None  # 二级维度
    level3: Optional[str] = None  # 三级维度
    level4: Optional[str] = None  # 四级维度（如果有）
    workload: Optional[Decimal] = None  # 工作量（总收入）
    hospital_value: Optional[str] = None  # 全院业务价值（权重/单价），非末级用"-"
    business_guide: Optional[str] = None  # 业务导向，非末级用"-"
    dept_value: Optional[str] = None  # 科室业务价值，非末级用"-"
    amount: Optional[Decimal] = None  # 金额
    ratio: Optional[Decimal] = None  # 占比
```

### 前端改动

**文件**: `frontend/src/views/Results.vue`

主要改动：
1. 移除了复杂的合并单元格逻辑
2. 简化表格列定义，直接展示维度层级
3. 添加辅助函数判断是否有三级、四级维度
4. 添加 `formatValueOrDash` 函数处理"-"值的显示

表格结构：
```vue
<el-table :data="detailData.doctor" border>
  <el-table-column prop="level1" label="一级维度" />
  <el-table-column prop="level2" label="二级维度" />
  <el-table-column prop="level3" label="三级维度" />
  <el-table-column prop="level4" label="四级维度" v-if="hasLevel4(...)" />
  <el-table-column prop="workload" label="工作量" />
  <el-table-column prop="hospital_value" label="全院业务价值" />
  <el-table-column prop="business_guide" label="业务导向" />
  <el-table-column prop="dept_value" label="科室业务价值" />
  <el-table-column prop="amount" label="金额" />
  <el-table-column prop="ratio" label="占比" />
</el-table>
```

## 测试

运行测试脚本验证数据结构：
```bash
python backend/test_new_detail_structure.py
```

测试结果示例：
- 医生序列（3级结构）：18行数据，包含所有节点
- 医技序列（2级结构）：7行数据，包含所有节点
- 末级维度显示完整信息
- 非末级维度只显示汇总信息，其他列显示"-"

## 优势

1. **结构清晰**：完全按照模型结构展示，易于理解
2. **灵活适配**：自动适配不同层级的维度结构（2-4级）
3. **信息完整**：同时展示末级和非末级维度，便于查看汇总
4. **代码简洁**：移除了复杂的合并单元格逻辑，代码更易维护

## 后续优化

1. 可以考虑添加树形表格展示（使用 Element Plus 的 tree-table 功能）
2. 支持展开/折叠功能，方便查看不同层级
3. 添加导出功能，支持导出为Excel格式
