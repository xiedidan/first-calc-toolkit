# 维度目录清单重复数据修复

## 问题描述

在维度目录清单中，一个项目在一个维度里面会重复出现3次。

## 问题原因

**笛卡尔积问题**：在 `get_dimension_items` API 中，查询时 JOIN 了 `ModelNode` 表来获取维度名称。但是 `ModelNode` 表中同一个 `dimension_code` 可能对应多条记录（因为存在多个模型版本，每个版本都有自己的节点记录）。

当 JOIN 条件只使用 `dimension_code` 时：
```python
.outerjoin(
    ModelNode,
    DimensionItemMapping.dimension_code == ModelNode.code
)
```

如果数据库中有3个模型版本，每个版本都有相同的 `dimension_code`，那么一条 `DimensionItemMapping` 记录就会匹配到3条 `ModelNode` 记录，导致结果集中出现3条重复数据。

## 解决方案

在 JOIN `ModelNode` 时，增加 `version_id` 的限定条件，只关联当前激活的模型版本：

```python
# 获取当前激活的模型版本ID
from app.models.model_version import ModelVersion
active_version = db.query(ModelVersion).filter(
    ModelVersion.hospital_id == hospital_id,
    ModelVersion.is_active == True
).first()

# JOIN时限定版本
.outerjoin(
    ModelNode,
    and_(
        DimensionItemMapping.dimension_code == ModelNode.code,
        ModelNode.version_id == active_version.id if active_version else None
    )
)
```

## 修改文件

- `backend/app/api/dimension_items.py` - `get_dimension_items` 函数

## 测试建议

1. 确保数据库中存在多个模型版本
2. 查询维度目录清单，验证每个项目只出现一次
3. 切换激活的模型版本，验证显示的维度名称正确更新

## 影响范围

- 修复了维度目录清单的重复数据问题
- 确保显示的维度名称来自当前激活的模型版本
- 不影响其他功能
