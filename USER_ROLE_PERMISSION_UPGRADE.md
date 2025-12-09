# 用户角色权限系统升级

## 概述

本次升级实现了三级用户权限体系：
1. **科室用户** (department_user)：必须有所属医疗机构和科室，只能查看本科室报表
2. **全院用户** (hospital_user)：必须有所属医疗机构，可操作本院所有数据
3. **管理员** (admin)：无所属医疗机构，可跨院操作，但不能管理维护者和AI接口
4. **维护者** (maintainer)：最高权限，可管理所有用户和AI接口

## 数据库变更

### Role 表新增字段
- `role_type`: 角色类型枚举 (department_user, hospital_user, admin, maintainer)
- `menu_permissions`: JSON数组，存储允许访问的菜单路径

### User 表新增字段
- `department_id`: 所属科室ID，科室用户必填

## 部署步骤

### 1. 执行数据库迁移
```bash
cd backend
alembic upgrade head
```

### 2. 更新现有角色数据
```bash
cd backend
python -m scripts.migrate_roles
```

## 新增功能

### 后端 API
- `GET /api/v1/roles` - 获取角色列表
- `POST /api/v1/roles` - 创建角色
- `GET /api/v1/roles/{id}` - 获取角色详情
- `PUT /api/v1/roles/{id}` - 更新角色
- `DELETE /api/v1/roles/{id}` - 删除角色
- `GET /api/v1/roles/menus` - 获取系统菜单列表（用于权限配置）

### 前端页面
- 用户角色管理页面 (`/roles`)：角色CRUD + 菜单权限配置
- 用户管理页面更新：支持选择角色、医疗机构、科室

## 权限控制规则

### 数据权限
| 角色类型 | 所属医疗机构 | 所属科室 | 数据范围 |
|---------|------------|---------|---------|
| 科室用户 | 必填 | 必填 | 本院本科室 |
| 全院用户 | 必填 | 空 | 本院全部 |
| 管理员 | 空 | 空 | 所有医疗机构 |
| 维护者 | 空 | 空 | 所有医疗机构 |

### 功能权限
- **用户管理**：仅管理员和维护者可访问
- **角色管理**：仅管理员和维护者可访问
- **AI接口管理**：仅维护者可访问
- **管理维护者用户**：仅维护者可操作

### 跨医疗机构复制
以下功能的跨院复制仅管理员和维护者可用：
- 评估模型管理 - 导入/复制版本
- 计算流程管理 - 复制流程
- 导向规则管理 - 复制规则
- 数据模板管理 - 复制模板

## 文件变更清单

### 后端
- `backend/alembic/versions/20251203_user_role_permission_upgrade.py` - 数据库迁移
- `backend/app/models/role.py` - Role模型增加role_type和menu_permissions
- `backend/app/models/user.py` - User模型增加department_id
- `backend/app/schemas/role.py` - 角色Schema
- `backend/app/schemas/user.py` - 用户Schema更新
- `backend/app/api/roles.py` - 角色管理API
- `backend/app/api/users.py` - 用户管理API更新
- `backend/app/api/auth.py` - 登录返回信息更新
- `backend/scripts/migrate_roles.py` - 角色数据迁移脚本
- `backend/scripts/init_data.py` - 初始化数据更新

### 前端
- `frontend/src/api/roles.ts` - 角色API
- `frontend/src/api/auth.ts` - UserInfo类型更新
- `frontend/src/api/user.ts` - 用户API更新
- `frontend/src/stores/user.ts` - 用户Store更新
- `frontend/src/views/Roles.vue` - 角色管理页面
- `frontend/src/views/Users.vue` - 用户管理页面更新
- `frontend/src/views/Layout.vue` - 菜单权限控制更新
- `frontend/src/router/index.ts` - 路由配置
