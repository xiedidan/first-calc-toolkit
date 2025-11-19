# 收费项目医疗机构隔离功能

## 问题描述

收费项目管理模块没有与医疗机构对接，导致用户可以查看到其他医疗机构的收费项目数据，存在数据隔离问题。

## 解决方案

### 1. 数据模型更新

**ChargeItem 模型变更：**
- 添加 `hospital_id` 字段，关联到医疗机构
- 修改唯一约束：从 `item_code` 改为 `(hospital_id, item_code)` 复合唯一约束
- 添加外键约束和级联删除
- 添加与 Hospital 的关系映射

**DimensionItemMapping 模型更新：**
- 添加 `charge_item_id` 字段，直接关联到 ChargeItem
- 添加与 ChargeItem 的关系映射

### 2. API 更新

所有收费项目相关的 API 端点都已更新，自动应用医疗机构过滤：

- `GET /api/charge-items` - 列表查询（仅返回当前用户所属医疗机构的数据）
- `GET /api/charge-items/{id}` - 详情查询（验证所属医疗机构）
- `POST /api/charge-items` - 创建（自动关联到当前用户的医疗机构）
- `PUT /api/charge-items/{id}` - 更新（验证所属医疗机构）
- `DELETE /api/charge-items/{id}` - 删除（验证所属医疗机构）
- `DELETE /api/charge-items/clear-all` - 清空（仅清空当前医疗机构的数据）
- `GET /api/charge-items/categories/list` - 分类列表（仅返回当前医疗机构的分类）

### 3. 导入功能更新

**同步导入：**
- 自动为导入的数据添加 `hospital_id`
- 验证项目编码唯一性时限定在当前医疗机构范围内

**异步导入：**
- 传递 `hospital_id` 到 Celery 任务
- 任务执行时自动关联到指定医疗机构

### 4. 数据库迁移

迁移脚本：`backend/alembic/versions/20251104_add_hospital_to_charge_items.py`

**迁移步骤：**
1. 添加 `hospital_id` 列（初始允许为空）
2. 将现有数据关联到默认医疗机构（第一个医疗机构）
3. 设置 `hospital_id` 为非空
4. 删除旧的 `item_code` 唯一约束
5. 创建新的 `(hospital_id, item_code)` 复合唯一约束
6. 创建外键约束和索引

## 执行迁移

### 方法一：使用批处理脚本（推荐）

```bash
migrate-charge-items.bat
```

此脚本会自动：
1. 检查并修复迁移状态
2. 执行数据库迁移
3. 运行测试验证

### 方法二：手动执行

```bash
cd backend
conda activate hospital-backend

# 如果之前迁移失败，先运行修复脚本
python fix_charge_items_migration.py

# 执行迁移
alembic upgrade head

# 测试验证
python test_charge_item_hospital.py
```

### 如果遇到迁移错误

如果看到 "current transaction is aborted" 错误，请参考 `FIX_CHARGE_ITEMS_MIGRATION.md` 文档进行修复。

快速修复方法：

```bash
cd backend
# 在 PostgreSQL 中执行 fix_migration.sql
# 或运行 Python 修复脚本
python fix_charge_items_migration.py

# 然后重新运行迁移
alembic upgrade head
```

## 测试验证

运行测试脚本验证隔离功能：

```bash
cd backend
conda activate hospital-backend
python test_charge_item_hospital.py
```

测试内容：
1. 查看系统中的医疗机构
2. 统计各医疗机构的收费项目数量
3. 验证数据隔离（不同医疗机构的数据互不干扰）
4. 测试用户与收费项目的关联

## 影响范围

### 后端变更
- `backend/app/models/charge_item.py` - 模型定义
- `backend/app/models/hospital.py` - 添加关系
- `backend/app/models/dimension_item_mapping.py` - 添加关联
- `backend/app/api/charge_items.py` - API 逻辑
- `backend/app/tasks/import_tasks.py` - 导入任务
- `backend/app/services/excel_import_service.py` - 导入服务

### 数据库变更
- `charge_items` 表添加 `hospital_id` 字段
- 修改唯一约束
- 添加外键约束和索引

### 前端影响
前端无需修改，API 接口保持兼容，自动应用医疗机构过滤。

## 注意事项

1. **数据迁移**：现有收费项目数据会自动关联到第一个医疗机构
2. **唯一性约束**：同一医疗机构内收费项目编码必须唯一，但不同医疗机构可以有相同编码
3. **级联删除**：删除医疗机构时会自动删除其关联的收费项目
4. **导入数据**：导入时会自动关联到当前用户所属的医疗机构

## 回滚方案

如果需要回滚迁移：

```bash
cd backend
conda activate hospital-backend
alembic downgrade -1
```

⚠️ 警告：回滚会删除 `hospital_id` 字段，可能导致数据丢失。

## 后续优化建议

1. 考虑添加数据迁移工具，支持将收费项目从一个医疗机构迁移到另一个
2. 添加批量导入时的医疗机构选择功能（超级管理员）
3. 优化查询性能，添加必要的复合索引
