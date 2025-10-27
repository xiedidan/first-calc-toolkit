# 维度智能导入 - 按名称匹配功能

## 功能概述

在维度智能导入功能中，新增"按收费名称匹配"选项，用户可以选择使用收费编码或收费名称来进行匹配。无论选择哪种匹配方式，最终保存到数据库的都是收费编码。

## 使用场景

### 场景1：Excel中只有收费名称
有些Excel文件中只包含收费项目的名称，没有编码。例如：
```
收费项目名称    | 维度预案 | 专家意见
CT检查         | 4D      | 4D
核磁共振       | 4D      | 4D
血常规         | 3D      | 3D
```

使用"按收费名称匹配"功能，系统会自动将名称转换为对应的编码。

### 场景2：Excel中有编码
如果Excel中已经有收费编码，可以使用"按收费编码匹配"（默认方式）：
```
收费项目编码    | 维度预案 | 专家意见
CT001         | 4D      | 4D
MRI002        | 4D      | 4D
LAB003        | 3D      | 3D
```

## 使用方法

### 步骤1：选择匹配方式

在智能导入的第一步"字段映射"中，选择匹配方式：

- **按收费编码匹配**（默认）：Excel中的列包含收费项目编码
- **按收费名称匹配**：Excel中的列包含收费项目名称

### 步骤2：选择对应的列

根据选择的匹配方式，选择Excel中对应的列：

- 如果选择"按收费编码匹配"，选择包含编码的列
- 如果选择"按收费名称匹配"，选择包含名称的列

### 步骤3：继续后续步骤

后续的维度值映射、预览与确认步骤与之前相同。

## 技术实现

### 后端实现

#### 1. Schema修改

在 `SmartImportFieldMapping` 中添加 `match_by` 字段：

```python
class SmartImportFieldMapping(BaseModel):
    session_id: str
    field_mapping: dict[str, str]
    model_version_id: int
    match_by: str = Field("code", description="匹配方式：code(按编码) 或 name(按名称)")
```

#### 2. 服务层修改

在 `DimensionImportService.extract_unique_values()` 中添加 `match_by` 参数：

```python
@classmethod
def extract_unique_values(
    cls,
    session_id: str,
    field_mapping: Dict[str, str],
    model_version_id: int,
    db: Session,
    match_by: str = "code"  # 新增参数
) -> Dict[str, Any]:
    # 保存匹配方式到会话
    cls._sessions[session_id]["match_by"] = match_by
    ...
```

#### 3. 预览生成时的转换

在 `generate_preview()` 方法中，根据匹配方式处理数据：

```python
# 获取匹配方式
match_by = session_data.get("match_by", "code")

# 创建两个索引
all_charge_items_by_code = {item.item_code: item for item in db.query(ChargeItem).all()}
all_charge_items_by_name = {item.item_name: item for item in db.query(ChargeItem).all()}

# 根据匹配方式获取收费项目编码
if match_by == "name":
    # 按名称匹配，需要转换为编码
    charge_item = all_charge_items_by_name.get(item_value)
    if charge_item:
        item_code = charge_item.item_code
        item_name = charge_item.item_name
    else:
        # 名称不存在，标记为warning
        item_code = item_value
        item_name = ""
else:
    # 按编码匹配
    item_code = item_value
    charge_item = all_charge_items_by_code.get(item_code)
    item_name = charge_item.item_name if charge_item else ""
```

### 前端实现

#### 1. 添加匹配方式选择

```vue
<el-form-item label="匹配方式" required>
  <el-radio-group v-model="matchBy">
    <el-radio value="code">按收费编码匹配</el-radio>
    <el-radio value="name">按收费名称匹配</el-radio>
  </el-radio-group>
  <div style="margin-top: 8px; color: #909399; font-size: 12px">
    <span v-if="matchBy === 'code'">使用Excel中的收费编码直接匹配</span>
    <span v-else>使用Excel中的收费名称匹配，系统会自动转换为对应的收费编码</span>
  </div>
</el-form-item>
```

#### 2. 动态标签

根据匹配方式动态显示标签：

```vue
<el-form-item :label="matchBy === 'code' ? '收费编码' : '收费名称'" required>
  <el-select v-model="fieldMapping.item_code" placeholder="请选择">
    ...
  </el-select>
</el-form-item>
```

#### 3. API调用

在调用API时传递 `match_by` 参数：

```typescript
const result = await extractValues({
  session_id: parseResult.value.session_id,
  field_mapping: fieldMapping.value,
  model_version_id: props.modelVersionId,
  match_by: matchBy.value  // 传递匹配方式
})
```

## 数据流程

### 按编码匹配（默认）

```
Excel: CT001 → 验证编码存在 → 保存: CT001
```

### 按名称匹配

```
Excel: CT检查 → 查找名称对应的编码 → 找到: CT001 → 保存: CT001
Excel: 不存在的项目 → 查找失败 → 标记为warning → 保存: 不存在的项目（孤儿记录）
```

## 预览状态说明

在预览步骤中，会显示不同的状态：

### 状态1：OK（绿色）
- 收费项目存在
- 未重复
- 可以正常导入

### 状态2：Warning（黄色）
- **按编码匹配**：收费项目编码在系统中不存在
- **按名称匹配**：收费项目名称在系统中不存在
- 或者：该收费项目已存在于此维度中

### 状态3：Error（红色）
- 目标维度不存在
- 其他系统错误

## 注意事项

### 1. 名称必须完全匹配

按名称匹配时，Excel中的名称必须与系统中的名称完全一致（包括空格、标点符号）。

**正确示例**：
- Excel: `CT检查` → 系统: `CT检查` ✅

**错误示例**：
- Excel: `CT 检查`（多了空格） → 系统: `CT检查` ❌
- Excel: `ct检查`（大小写不同） → 系统: `CT检查` ❌

### 2. 名称重复问题

如果系统中有多个收费项目使用相同的名称，会匹配到第一个找到的项目。建议：
- 确保收费项目名称唯一
- 或者使用"按编码匹配"方式

### 3. 孤儿记录

如果名称不存在，系统仍然会创建映射记录（使用原名称作为编码），这会产生孤儿记录。可以使用"查看孤儿记录"功能清理。

### 4. 性能考虑

按名称匹配需要额外的查询和转换，对于大量数据可能会稍慢一些。如果Excel中已有编码，建议使用"按编码匹配"。

## 示例

### 示例1：按名称匹配成功

**Excel数据**：
```
收费项目名称    | 维度预案
CT检查         | 4D
核磁共振       | 4D
```

**系统中的收费项目**：
```
编码: CT001, 名称: CT检查
编码: MRI002, 名称: 核磁共振
```

**导入结果**：
```
维度4D → CT001 (CT检查) ✅
维度4D → MRI002 (核磁共振) ✅
```

### 示例2：按名称匹配失败

**Excel数据**：
```
收费项目名称    | 维度预案
不存在的项目    | 4D
```

**导入结果**：
```
维度4D → 不存在的项目 ⚠️ (收费项目名称'不存在的项目'在系统中不存在)
```

这条记录会被标记为warning，但仍然可以导入（成为孤儿记录）。

## 常见问题

### Q: 为什么选择"按名称匹配"后，预览中还是显示编码？
A: 这是正常的。系统会将名称转换为编码后再显示，因为最终保存的是编码。

### Q: 如果名称匹配不到，会怎样？
A: 会标记为warning状态，提示"收费项目名称'xxx'在系统中不存在"。你可以选择跳过这些记录，或者导入后再清理。

### Q: 可以混合使用编码和名称吗？
A: 不可以。每次导入只能选择一种匹配方式。如果Excel中既有编码又有名称，建议分两次导入。

### Q: 按名称匹配会更慢吗？
A: 会稍微慢一些，但对于几千条数据来说，差异不明显。

## 相关文档

- [维度智能导入完整文档](DIMENSION_SMART_IMPORT_COMPLETED.md)
- [孤儿记录清理指南](ORPHAN_RECORDS_QUICK_GUIDE.md)

## 更新日期

2025-10-24
