# 维度关联字段从ID改为Code的迁移计划

## 背景

当前 `dimension_item_mappings` 表使用 `dimension_id` (Integer) 关联维度节点。
改为使用 `dimension_code` (String) 更符合业务逻辑，因为：
1. Code 是业务上的唯一标识
2. 即使重新导入数据，Code 不变，关联关系不会断
3. 更容易理解和维护

## 需要修改的文件

### 1. 数据库层
- ✅ `backend/app/models/dimension_item_mapping.py` - 模型定义
- ✅ `backend/alembic/versions/change_dimension_id_to_code.py` - 迁移脚本

### 2. Schema层
- `backend/app/schemas/dimension_item.py` - Schema定义

### 3. API层
- `backend/app/api/dimension_items.py` - 所有API方法

### 4. Service层
- `backend/app/services/dimension_import_service.py` - 智能导入服务

### 5. 前端层
- `frontend/src/views/DimensionItems.vue` - 前端页面
- 前端TypeScript接口定义

## 迁移步骤

1. ✅ 创建数据库迁移脚本
2. ✅ 修改模型定义
3. 修改Schema
4. 修改API（需要将ID转换为Code）
5. 修改Service
6. 修改前端
7. 执行数据库迁移
8. 测试验证

## 注意事项

1. 所有通过ID查询维度的地方，需要先通过ID查code，再使用code
2. 所有创建映射的地方，需要传递code而不是ID
3. 前端选择维度时，需要传递code
4. 需要确保所有维度节点都有唯一的code

## 兼容性

这是一个破坏性变更，需要：
1. 数据库迁移
2. API接口变更
3. 前端代码变更

建议在开发环境充分测试后再部署到生产环境。
