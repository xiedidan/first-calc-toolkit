# 医疗机构管理功能 - 数据库迁移总结

## 已完成的工作

### 1. 数据模型创建

#### 新增模型
- **Hospital** (`backend/app/models/hospital.py`)
  - 医疗机构基础信息表
  - 字段：id, code, name, is_active, created_at, updated_at
  - code 字段唯一约束

#### 修改模型
- **User** (`backend/app/models/user.py`)
  - 添加 `hospital_id` 字段（可为空，支持超级用户）
  - 添加与 Hospital 的关系

- **Department** (`backend/app/models/department.py`)
  - 添加 `hospital_id` 字段（非空）
  - 添加与 Hospital 的关系
  - his_code 唯一约束改为 (hospital_id, his_code) 组合唯一

- **ModelVersion** (`backend/app/models/model_version.py`)
  - 添加 `hospital_id` 字段（非空）
  - 添加与 Hospital 的关系
  - version 唯一约束改为 (hospital_id, version) 组合唯一

- **DimensionItemMapping** (`backend/app/models/dimension_item_mapping.py`)
  - 添加 `hospital_id` 字段（非空）
  - 支持不同医疗机构有不同的维度-收费项目映射

### 2. 数据库迁移脚本

**文件**: `backend/alembic/versions/20251103_add_hospital_management.py`

**迁移内容**:
1. 创建 `hospitals` 表
2. 插入默认医疗机构"宁波市眼科医院"（编码：nbeye）
3. 在 `users` 表添加 `hospital_id` 字段（可为空）
4. 在 `departments` 表添加 `hospital_id` 字段并更新现有数据
5. 在 `model_versions` 表添加 `hospital_id` 字段并更新现有数据
6. 在 `dimension_item_mappings` 表添加 `hospital_id` 字段并更新现有数据
7. 添加所有必要的外键约束和索引
8. 修改唯一约束以支持多租户

**回滚支持**: 完整的 downgrade 函数，可安全回滚所有变更

### 3. 验证脚本

**文件**: `backend/verify_hospital_migration.py`

**验证内容**:
- ✓ hospitals 表结构完整性
- ✓ 默认医疗机构数据存在
- ✓ 所有表的 hospital_id 字段正确添加
- ✓ 外键约束正确创建
- ✓ 索引正确创建
- ✓ 现有数据正确迁移到默认医疗机构

### 4. 执行脚本

**文件**: `backend/run_hospital_migration.py`

**功能**:
- 自动检查当前迁移状态
- 执行数据库迁移
- 自动运行验证脚本
- 提供清晰的执行结果反馈

### 5. 迁移指南

**文件**: `backend/HOSPITAL_MIGRATION_GUIDE.md`

**内容**:
- 详细的迁移步骤说明
- 前置条件检查清单
- 备份和回滚方案
- 常见问题解答
- 下一步开发指引

## 数据隔离策略

### 需要隔离的表
- ✓ `departments` - 科室数据按医疗机构隔离
- ✓ `model_versions` - 模型版本按医疗机构隔离
- ✓ `model_nodes` - 通过 model_versions 间接隔离
- ✓ `dimension_item_mappings` - 维度映射按医疗机构隔离
- ✓ `calculation_workflows` - 通过 model_versions 间接隔离
- ✓ `calculation_steps` - 通过 calculation_workflows 间接隔离
- ✓ `calculation_tasks` - 通过 model_versions 间接隔离
- ✓ `calculation_results` - 通过 calculation_tasks 间接隔离

### 全局共享的表
- `users` - 用户可以属于某个医疗机构或为超级用户
- `roles` - 角色全局共享
- `permissions` - 权限全局共享
- `charge_items` - 收费项目全局共享
- `data_sources` - 数据源全局共享
- `system_settings` - 系统设置全局共享

## 执行迁移

### 快速开始

```bash
cd backend

# 方式一：使用自动化脚本（推荐）
python run_hospital_migration.py

# 方式二：手动执行
alembic upgrade head
python verify_hospital_migration.py
```

### 验证结果

成功的迁移应该显示：

```
✓ 所有检查通过！数据迁移成功。
```

## 下一步工作

数据库迁移完成后，需要继续开发：

### 后端开发
- [ ] 2.1 创建医疗机构数据模型 ✓ (已完成)
- [ ] 2.2 创建医疗机构Schema
- [ ] 2.3 实现医疗机构CRUD服务
- [ ] 2.4 实现医疗机构API路由
- [ ] 2.5 实现医疗机构激活API
- [ ] 2.6 实现用户可访问机构列表API
- [ ] 2.7 修改用户管理API
- [ ] 2.8 实现会话管理中间件
- [ ] 2.9 实现数据隔离过滤器
- [ ] 2.10 修改现有业务API

### 前端开发
- [ ] 3.1 创建医疗机构管理页面
- [ ] 3.2-3.4 实现医疗机构CRUD对话框
- [ ] 3.5 添加医疗机构管理菜单项
- [ ] 3.6 实现顶部医疗机构选择器
- [ ] 3.7 实现页面标题动态更新
- [ ] 3.8 实现菜单权限控制
- [ ] 3.9 修改用户管理页面

## 注意事项

1. **备份**: 执行迁移前务必备份数据库
2. **测试**: 在测试环境充分测试后再在生产环境执行
3. **回滚**: 如遇问题，可使用 `alembic downgrade` 或从备份恢复
4. **验证**: 迁移后务必运行验证脚本确认数据完整性
5. **兼容性**: 现有功能应保持正常运行，所有数据已关联到默认医疗机构

## 技术细节

### 外键约束
- `users.hospital_id` → `hospitals.id` (ON DELETE SET NULL)
- `departments.hospital_id` → `hospitals.id` (ON DELETE CASCADE)
- `model_versions.hospital_id` → `hospitals.id` (ON DELETE CASCADE)
- `dimension_item_mappings.hospital_id` → `hospitals.id` (ON DELETE CASCADE)

### 索引
所有 `hospital_id` 字段都添加了索引以提升查询性能。

### 唯一约束
- `hospitals.code` - 全局唯一
- `departments.(hospital_id, his_code)` - 组合唯一
- `model_versions.(hospital_id, version)` - 组合唯一

## 文件清单

- `backend/app/models/hospital.py` - Hospital 模型
- `backend/app/models/user.py` - 更新的 User 模型
- `backend/app/models/department.py` - 更新的 Department 模型
- `backend/app/models/model_version.py` - 更新的 ModelVersion 模型
- `backend/app/models/dimension_item_mapping.py` - 更新的 DimensionItemMapping 模型
- `backend/alembic/versions/20251103_add_hospital_management.py` - 迁移脚本
- `backend/verify_hospital_migration.py` - 验证脚本
- `backend/run_hospital_migration.py` - 执行脚本
- `backend/HOSPITAL_MIGRATION_GUIDE.md` - 迁移指南
- `backend/HOSPITAL_MIGRATION_SUMMARY.md` - 本文档
