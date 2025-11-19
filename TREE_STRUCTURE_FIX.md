# 业务价值明细树形结构修复

## 问题描述

业务价值明细表需要改为类似模型结构编辑的树形结构展示，后端已实现但前端未正常显示。

## 问题原因

Schema 定义中 `DepartmentDetailResponse` 的 `doctor`、`nurse`、`tech` 字段类型为 `List[StructureRow]`（扁平格式），与后端 API 返回的树形结构数据不匹配。

## 解决方案

### 1. 修改 Schema 定义

**文件**: `backend/app/schemas/calculation_task.py`

新增 `TreeNode` 类：

```python
class TreeNode(BaseModel):
    """树形表格节点数据"""
    id: int  # 节点ID
    dimension_name: str  # 维度名称
    workload: Optional[Decimal] = None  # 工作量
    hospital_value: str = "-"  # 全院业务价值
    business_guide: str = "-"  # 业务导向
    dept_value: str = "-"  # 科室业务价值
    amount: Optional[Decimal] = None  # 金额
    ratio: Optional[Decimal] = None  # 占比
    children: Optional[List['TreeNode']] = None  # 子节点
```

更新 `DepartmentDetailResponse`：

```python
class DepartmentDetailResponse(BaseModel):
    """科室详细业务价值数据"""
    department_id: int
    department_name: str
    period: str
    sequences: List[SequenceDetail]
    doctor: Optional[List[TreeNode]] = None  # 医生序列
    nurse: Optional[List[TreeNode]] = None  # 护理序列
    tech: Optional[List[TreeNode]] = None  # 医技序列
```

### 2. 数据结构说明

**叶子节点**（末级维度）：
- 不包含 `children` 字段
- `hospital_value`、`business_guide`、`dept_value` 显示实际值

**非叶子节点**（父级维度）：
- 包含 `children` 数组
- `hospital_value`、`business_guide`、`dept_value` 显示 "-"
- `workload` 和 `amount` 为子节点汇总值

### 3. 前端配置

前端 `Results.vue` 已配置树形表格：

```vue
<el-table 
  :data="detailData.doctor" 
  border 
  row-key="id"
  :tree-props="{ children: 'children' }"
  :default-expand-all="true"
>
  <el-table-column prop="dimension_name" label="维度名称" />
  <!-- 其他列 -->
</el-table>
```

## 验证

运行测试脚本：
```bash
python backend/test_tree_structure.py
```

## 效果

- ✅ 树形结构展示维度层级关系
- ✅ 支持展开/收缩功能
- ✅ 自动缩进显示层级
- ✅ 与模型结构编辑界面一致

## 相关文件

- `backend/app/schemas/calculation_task.py` - Schema 定义（已修改）
- `backend/app/api/calculation_tasks.py` - API 实现（无需修改）
- `frontend/src/views/Results.vue` - 前端页面（无需修改）
- `backend/test_tree_structure.py` - 测试脚本（新增）
