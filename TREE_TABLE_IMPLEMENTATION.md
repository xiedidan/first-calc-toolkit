# 树形表格实现说明

## 概述

将业务价值明细表的维度列合并为树形结构，支持展开/收缩功能。

## 实现方式

### 后端改动

**文件**: `backend/app/api/calculation_tasks.py`

#### 1. 修改数据结构

将扁平的行数据改为树形结构：

```python
def build_tree_rows(sequence_name, dimensions):
    """将维度树转换为表格树形数据"""
    
    def build_tree_node(node, siblings_total=None):
        """构建树形节点数据"""
        is_leaf = not node.children or len(node.children) == 0
        
        # 计算金额和工作量
        if is_leaf:
            current_amount = node.value or 0
            current_workload = node.workload or 0
        else:
            current_workload, current_amount = calculate_sum_from_children(node)
        
        # 计算占比
        ratio = calculate_ratio(current_amount, siblings_total)
        
        # 创建节点数据
        if is_leaf:
            # 叶子节点：不包含children属性
            tree_node = {
                "id": node.node_id,
                "dimension_name": node.dimension_name,
                "workload": current_workload,
                "hospital_value": str(node.weight) if node.weight else "-",
                "business_guide": node.business_guide or "-",
                "dept_value": str(node.weight) if node.weight else "-",
                "amount": current_amount,
                "ratio": ratio
            }
        else:
            # 非叶子节点：包含children数组
            tree_node = {
                "id": node.node_id,
                "dimension_name": node.dimension_name,
                "workload": current_workload,
                "hospital_value": "-",
                "business_guide": "-",
                "dept_value": "-",
                "amount": current_amount,
                "ratio": ratio,
                "children": []  # 子节点数组
            }
        
        # 递归处理子节点
        if node.children:
            children_total = sum(...)
            for child in node.children:
                child_node = build_tree_node(child, children_total)
                tree_node["children"].append(child_node)
        
        return tree_node
```

#### 2. 数据结构示例

```json
[
  {
    "id": 10,
    "dimension_name": "门诊",
    "workload": 5000,
    "hospital_value": "-",
    "business_guide": "-",
    "dept_value": "-",
    "amount": 5000,
    "ratio": 50,
    "children": [
      {
        "id": 20,
        "dimension_name": "门诊诊察",
        "workload": 2000,
        "hospital_value": "-",
        "business_guide": "-",
        "dept_value": "-",
        "amount": 2000,
        "ratio": 40,
        "children": [
          {
            "id": 30,
            "dimension_name": "普通诊察",
            "workload": 1000,
            "hospital_value": "55",
            "business_guide": "基础诊疗",
            "dept_value": "55",
            "amount": 1000,
            "ratio": 50
          }
        ]
      }
    ]
  }
]
```

### 前端改动

**文件**: `frontend/src/views/Results.vue`

#### 1. 使用树形表格

```vue
<el-table 
  :data="detailData.doctor" 
  border 
  class="structure-table"
  row-key="id"
  :tree-props="{ children: 'children' }"
  :default-expand-all="true"
>
  <el-table-column prop="dimension_name" label="维度名称" min-width="200" align="left" />
  <el-table-column prop="workload" label="工作量" min-width="110" align="right">
    <template #default="{ row }">{{ formatNumber(row.workload) }}</template>
  </el-table-column>
  <!-- 其他列 -->
</el-table>
```

#### 2. 关键属性说明

- `row-key="id"`: 指定行的唯一标识符
- `:tree-props="{ children: 'children' }"`: 指定子节点的属性名
- `:default-expand-all="true"`: 默认展开所有节点
- `prop="dimension_name"`: 维度名称列会自动显示树形结构（缩进和展开/收缩图标）

#### 3. 移除的内容

- 移除了 `level1`、`level2`、`level3`、`level4` 列
- 移除了 `hasLevel3`、`hasLevel4` 辅助函数
- 简化了表格结构

## 特性

### 1. 自动缩进

Element Plus会根据节点层级自动添加缩进，无需手动处理。

### 2. 展开/收缩

- 点击维度名称前的箭头图标可以展开/收缩子节点
- 默认全部展开（`default-expand-all="true"`）
- 可以手动控制展开状态

### 3. 层级显示

- 一级维度：无缩进
- 二级维度：一级缩进
- 三级维度：二级缩进
- 四级维度：三级缩进

## 优势

1. **更清晰的层级关系**：树形结构直观展示维度的父子关系
2. **节省空间**：不需要多个维度列，只需一个维度名称列
3. **交互友好**：支持展开/收缩，用户可以按需查看详细信息
4. **与模型结构一致**：展示方式与模型版本管理中的结构编辑一致

## 注意事项

### 1. 叶子节点识别

- 叶子节点：不包含 `children` 属性
- 非叶子节点：包含 `children` 数组（即使为空也要包含）

```python
# ✓ 正确
leaf_node = {"id": 1, "name": "叶子"}  # 没有children属性

# ✓ 正确
parent_node = {"id": 2, "name": "父节点", "children": []}  # 有children数组

# ✗ 错误
leaf_node = {"id": 1, "name": "叶子", "children": []}  # 会被识别为父节点
```

### 2. row-key必须唯一

确保每个节点的 `id` 是唯一的，否则树形结构会出现问题。

### 3. 数据一致性

确保后端返回的树形结构与实际的维度层级关系一致。

## 调试

### 1. 检查数据结构

在浏览器控制台查看返回的数据：

```javascript
console.log('detailData.doctor:', detailData.doctor)
```

### 2. 检查节点ID

确保每个节点都有唯一的 `id`：

```javascript
detailData.doctor.forEach(node => {
  console.log('Node ID:', node.id, 'Name:', node.dimension_name)
})
```

### 3. 检查children属性

确保非叶子节点有 `children` 数组：

```javascript
detailData.doctor.forEach(node => {
  if (node.children) {
    console.log('Parent:', node.dimension_name, 'Children:', node.children.length)
  }
})
```

## 相关文件

- `backend/app/api/calculation_tasks.py` - 后端API（已修改）
- `frontend/src/views/Results.vue` - 前端页面（已修改）
- `TREE_TABLE_IMPLEMENTATION.md` - 本文档

## 总结

树形表格实现完成，提供了更清晰、更友好的维度层级展示方式，与模型结构编辑界面保持一致。
