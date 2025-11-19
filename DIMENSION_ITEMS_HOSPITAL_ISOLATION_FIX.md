# 维度目录医院隔离修复

## 问题描述

用户报告：新医院导入模型版本后，能够看到其他医院的维度目录数据。

## 问题分析

经过代码审查，发现了以下问题：

### 1. 模型版本导入逻辑 ✅ 正确

查看 `backend/app/services/model_version_import_service.py`：
- 导入模型版本时**只复制模型节点（ModelNode）和计算流程（CalculationWorkflow）**
- **不会复制维度目录（DimensionItemMapping）**
- 这个逻辑是正确的，符合设计要求

### 2. 维度目录API缺少医院隔离 ❌ 问题根源

查看 `backend/app/api/dimension_items.py`：
- 虽然 `DimensionItemMapping` 模型有 `hospital_id` 字段
- 但所有API接口都**没有应用医院隔离过滤**
- 导致所有医院都能看到和操作其他医院的维度目录数据

## 修复内容

在 `backend/app/api/dimension_items.py` 中添加了完整的医院隔离：

### 1. 导入医院过滤工具函数

```python
from app.utils.hospital_filter import (
    apply_hospital_filter,
    get_current_hospital_id_or_raise,
)
```

### 2. 修复所有API接口

#### `get_dimension_items()` - 查询维度项
- ✅ 添加 `DimensionItemMapping.hospital_id == hospital_id` 过滤
- ✅ 在JOIN ChargeItem时也添加医院隔离

#### `create_dimension_items()` - 创建维度项
- ✅ 查询收费项目时添加医院过滤
- ✅ 检查已存在映射时添加医院过滤
- ✅ 创建新映射时设置 `hospital_id`

#### `update_dimension_item()` - 更新维度项
- ✅ 查询映射关系时添加医院过滤
- ✅ 检查重复映射时添加医院过滤

#### `delete_dimension_item()` - 删除维度项
- ✅ 查询映射关系时添加医院过滤

#### `clear_all_dimension_items()` - 清空维度所有项目
- ✅ 删除时添加医院过滤

#### `clear_all_orphan_items()` - 清除孤儿记录
- ✅ 查询和删除时都添加医院过滤

#### `search_charge_items()` - 搜索收费项目
- ✅ 查询收费项目时添加医院过滤
- ✅ 查询已关联项目时添加医院过滤

## 验证要点

修复后需要验证：

1. **新医院导入模型版本后**
   - ✅ 能看到模型节点结构
   - ✅ 能看到计算流程（如果选择导入）
   - ✅ **看不到任何维度目录数据**（因为是空的）

2. **医院A的维度目录**
   - ✅ 只能看到自己医院的维度项
   - ✅ 只能添加自己医院的收费项目
   - ✅ 只能修改/删除自己医院的映射

3. **医院B的维度目录**
   - ✅ 完全独立，看不到医院A的数据
   - ✅ 所有操作都在自己医院范围内

## 数据库结构确认

```sql
-- DimensionItemMapping 表结构
CREATE TABLE dimension_item_mappings (
    id INTEGER PRIMARY KEY,
    hospital_id INTEGER NOT NULL,  -- 医院隔离字段
    dimension_code VARCHAR(100) NOT NULL,
    item_code VARCHAR(100) NOT NULL,
    charge_item_id INTEGER,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE
);

-- ChargeItem 表结构
CREATE TABLE charge_items (
    id INTEGER PRIMARY KEY,
    hospital_id INTEGER NOT NULL,  -- 医院隔离字段
    item_code VARCHAR(100) NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    item_category VARCHAR(100),
    unit_price VARCHAR(50),
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    UNIQUE (hospital_id, item_code)
);
```

## 额外改进：全部清除功能优化

### 问题
原来的"全部清除"按钮要求必须选择一个维度，但用户希望不选维度时就清除当前医院的所有维度目录数据。

### 修改内容

#### 后端 API
在 `backend/app/api/dimension_items.py` 中添加新接口：

```python
@router.delete("/clear-all")
def clear_all_dimension_items_for_hospital(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """清空当前医院的所有维度目录数据"""
    hospital_id = get_current_hospital_id_or_raise()
    deleted_count = db.query(DimensionItemMapping).filter(
        DimensionItemMapping.hospital_id == hospital_id
    ).delete()
    db.commit()
    return {
        "message": f"已清空当前医院的所有维度目录数据",
        "deleted_count": deleted_count
    }
```

#### 前端逻辑
在 `frontend/src/views/DimensionItems.vue` 中修改 `handleClearAll()` 函数：

- **不选维度**：清空当前医院的所有维度目录数据（调用 `/dimension-items/clear-all`）
- **选择1个维度**：清空该维度的数据（调用 `/dimension-items/dimension/{code}/clear-all`）
- **选择多个维度**：提示错误，要求只能选择一个或不选

### 使用场景

1. **清空全部数据**：不选择任何维度，点击"全部清除"
2. **清空单个维度**：选择一个维度，点击"全部清除"

## 总结

问题已完全修复：
1. ✅ 模型版本导入不包括维度目录（本来就是正确的）
2. ✅ 维度目录API已添加完整的医院隔离
3. ✅ 每个医院的维度目录数据完全独立
4. ✅ 新医院导入模型版本后，维度目录为空（符合预期）
5. ✅ "全部清除"按钮支持清空所有维度或单个维度
