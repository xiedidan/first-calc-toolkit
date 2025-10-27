# 维度目录管理 - 界面优化更新

## 更新日期
2025-10-24

## 更新内容

### 1. 维度选择方式优化 ⭐

#### 之前的问题
- 使用维度ID输入框，用户不知道应该输入什么ID
- 需要先查询维度ID，然后再输入
- 用户体验不友好

#### 现在的改进
- **改为维度下拉选择**
- 显示完整的维度路径（例如：一级维度 > 二级维度 > 三级维度）
- 支持搜索过滤
- 只显示末级维度（叶子节点）

#### 界面对比

**之前**：
```
┌─────────────────────────────────────────┐
│ 模型版本: [选择▼]  维度ID: [输入数字]    │
└─────────────────────────────────────────┘
```

**现在**：
```
┌──────────────────────────────────────────────────────┐
│ 模型版本: [选择▼]  维度: [一级 > 二级 > 三级 ▼]      │
└──────────────────────────────────────────────────────┘
```

### 2. 智能导入覆盖功能 ⭐

#### 之前的行为
- 如果记录已存在，会跳过（skipped）
- 无法更新已有的映射关系
- 需要先手动删除，再重新导入

#### 现在的改进
- **自动覆盖已存在的记录**
- 删除旧记录，导入新记录
- 实现类似"更新"的效果

#### 预览状态变化

**之前**：
```
状态: ⚠️ Warning
消息: 该收费项目已存在于此维度中
结果: 跳过导入
```

**现在**：
```
状态: ✅ OK
消息: 该收费项目已存在，将被覆盖
结果: 删除旧记录，导入新记录
```

## 技术实现

### 1. 维度下拉选择

#### 后端API
新增获取末级维度列表的API：

```python
@router.get("/version/{version_id}/leaf")
def get_leaf_nodes(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取指定版本的所有末级维度（叶子节点）"""
    leaf_nodes = db.query(ModelNode).filter(
        ModelNode.version_id == version_id,
        ModelNode.is_leaf == True
    ).order_by(ModelNode.sort_order).all()
    
    # 构建完整路径
    result = []
    for node in leaf_nodes:
        full_path = _build_node_path(node, db)
        result.append({
            "id": node.id,
            "name": node.name,
            "code": node.code,
            "full_path": full_path
        })
    
    return result
```

#### 前端实现
```vue
<!-- 维度下拉选择 -->
<el-select
  v-model="dimensionId"
  placeholder="请选择维度"
  clearable
  filterable
  style="width: 300px"
>
  <el-option
    v-for="dim in leafDimensions"
    :key="dim.id"
    :label="dim.full_path"
    :value="dim.id"
  />
</el-select>
```

```typescript
// 获取末级维度列表
const fetchLeafDimensions = async (versionId: number) => {
  const res = await request.get(`/model-nodes/version/${versionId}/leaf`)
  leafDimensions.value = res.map((node: any) => ({
    id: node.id,
    name: node.name,
    full_path: node.full_path || node.name
  }))
}

// 版本变化时重新加载维度列表
const handleVersionChange = async () => {
  dimensionId.value = null
  await fetchLeafDimensions(modelVersionId.value)
}
```

### 2. 智能导入覆盖

#### 服务层修改
```python
# 检查是否已存在映射
existing = db.query(DimensionItemMapping).filter(
    DimensionItemMapping.dimension_id == item["dimension_id"],
    DimensionItemMapping.item_code == item["item_code"]
).first()

if existing:
    # 删除旧记录，实现覆盖效果
    db.delete(existing)
    db.flush()

# 创建新映射
mapping = DimensionItemMapping(
    dimension_id=item["dimension_id"],
    item_code=item["item_code"]
)
db.add(mapping)
db.flush()
success_count += 1
```

#### 预览状态修改
```python
elif (dim_id, item_code) in existing_mappings:
    status = "ok"  # 改为ok状态，因为会覆盖
    message = "该收费项目已存在，将被覆盖"
    statistics["ok"] += 1
```

## 使用说明

### 1. 使用维度下拉选择

#### 步骤1：选择模型版本
在"模型版本"下拉框中选择要查看的版本

#### 步骤2：选择维度
在"维度"下拉框中：
- 点击下拉框查看所有末级维度
- 可以输入关键词搜索（支持拼音搜索）
- 选择要查看的维度

#### 步骤3：查询
点击"查询"按钮，显示该维度的所有收费项目

#### 提示
- 下拉框显示完整路径，例如："医疗服务 > 检查 > CT检查"
- 只显示末级维度（可以添加收费项目的维度）
- 支持清空选择，查看所有记录

### 2. 使用智能导入覆盖功能

#### 场景：更新已有的维度映射

假设你已经导入过一次数据，现在需要更新：

**步骤1：准备新的Excel文件**
```
收费编码 | 维度预案
CT001   | 4D  (之前是3D，现在改为4D)
MRI002  | 5D  (新增)
```

**步骤2：智能导入**
- 上传Excel文件
- 完成字段映射和维度值映射

**步骤3：查看预览**
```
CT001  → 4D  ✅ OK (该收费项目已存在，将被覆盖)
MRI002 → 5D  ✅ OK
```

**步骤4：确认导入**
- 点击"确认导入"
- CT001的旧映射（3D）会被删除
- CT001的新映射（4D）会被创建
- MRI002的新映射（5D）会被创建

#### 结果
- 旧数据被新数据覆盖
- 不需要手动删除旧记录
- 一次操作完成更新

## 优势对比

### 维度选择优化

| 特性 | 之前 | 现在 |
|------|------|------|
| 输入方式 | 手动输入ID | 下拉选择 |
| 显示内容 | 无提示 | 完整路径 |
| 搜索功能 | 无 | 支持过滤 |
| 用户体验 | ⭐⭐ | ⭐⭐⭐⭐⭐ |

### 智能导入覆盖

| 特性 | 之前 | 现在 |
|------|------|------|
| 已存在记录 | 跳过 | 覆盖 |
| 更新数据 | 需手动删除 | 自动覆盖 |
| 操作步骤 | 3步 | 1步 |
| 用户体验 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 注意事项

### 1. 维度下拉选择
- 只显示末级维度（is_leaf=True）
- 如果没有末级维度，下拉框会是空的
- 切换模型版本时，维度列表会自动更新

### 2. 智能导入覆盖
- **覆盖是不可逆的**，旧记录会被永久删除
- 建议在预览步骤仔细检查
- 如果不想覆盖，可以先手动删除不需要的记录

### 3. 性能考虑
- 维度列表只加载末级维度，性能较好
- 覆盖操作使用事务，确保数据一致性

## 常见问题

### Q: 为什么维度下拉框是空的？
A: 可能的原因：
1. 该模型版本没有末级维度
2. 所有维度都不是末级维度（is_leaf=False）
3. 需要在模型管理中设置末级维度

### Q: 覆盖功能会影响其他维度吗？
A: 不会。覆盖只针对相同的（维度ID + 收费编码）组合。例如：
- 维度A的CT001会被覆盖
- 维度B的CT001不受影响

### Q: 可以关闭覆盖功能吗？
A: 目前不支持关闭。如果不想覆盖，可以：
1. 在预览步骤取消已存在的记录
2. 或者先手动删除不需要更新的记录

### Q: 覆盖后可以恢复吗？
A: 不能。覆盖操作会永久删除旧记录。建议：
1. 导入前备份数据
2. 在预览步骤仔细检查

## 相关文档

- [维度智能导入完整文档](DIMENSION_SMART_IMPORT_COMPLETED.md)
- [按名称匹配功能](DIMENSION_IMPORT_MATCH_BY_NAME.md)
- [孤儿记录清理](ORPHAN_RECORDS_QUICK_GUIDE.md)

## 更新历史

- 2025-10-24: 初始版本
  - 维度ID改为维度下拉选择
  - 智能导入支持覆盖已存在的记录
