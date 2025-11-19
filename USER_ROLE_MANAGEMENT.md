# 用户角色和医疗机构管理功能

## 功能概述

本次更新为用户管理界面添加了角色和医疗机构配置功能，简化了权限管理模型。

## 角色说明

系统现在支持两种角色：

### 1. 管理员（admin）
- **权限**：可以访问系统所有医疗机构和功能
- **医疗机构**：不属于任何医疗机构
- **登录行为**：登录后需要自己选择激活医疗机构

### 2. 普通用户（user）
- **权限**：只能访问所属医疗机构的数据和非管理员功能
- **医疗机构**：必须属于某个医疗机构
- **登录行为**：登录后自动激活所属医疗机构

## 数据库变更

### 1. 新增迁移文件
- `backend/alembic/versions/20251106_add_default_roles.py`
  - 自动插入 `admin` 和 `user` 两个默认角色

### 2. Schema 变更
- `backend/app/schemas/user.py`
  - `UserCreate.role`: 从 `role_ids` 改为 `role`（字符串类型：'admin' 或 'user'）
  - `UserUpdate.role`: 从 `role_ids` 改为 `role`
  - `User.role`: 从 `roles` 改为 `role`（单个角色字符串）

## API 变更

### 后端 API

#### 用户创建 (POST /users)
```json
{
  "username": "testuser",
  "name": "测试用户",
  "email": "test@example.com",
  "password": "password123",
  "role": "user",  // "admin" 或 "user"
  "hospital_id": 1  // 普通用户必填，管理员必须为空
}
```

#### 用户更新 (PUT /users/{user_id})
```json
{
  "name": "新名称",
  "email": "newemail@example.com",
  "role": "admin",  // 可选，切换角色
  "hospital_id": 1,  // 可选，仅普通用户可设置
  "status": "active"
}
```

#### 用户响应
```json
{
  "id": 1,
  "username": "testuser",
  "name": "测试用户",
  "email": "test@example.com",
  "status": "active",
  "role": "user",  // "admin" 或 "user"
  "hospital_id": 1,
  "hospital_name": "测试医院",
  "created_at": "2025-11-06T10:00:00",
  "updated_at": "2025-11-06T10:00:00"
}
```

### 前端变更

#### 用户列表界面
- 新增"角色"列：显示管理员或普通用户标签
- 新增"所属医疗机构"列：显示用户所属医疗机构名称

#### 用户编辑对话框
- 新增"角色"选择：管理员/普通用户
- 新增"所属医疗机构"下拉框：仅普通用户显示
- 自动验证：
  - 普通用户必须选择医疗机构
  - 管理员不能选择医疗机构
  - 切换为管理员时自动清空医疗机构

## 初始化脚本

### 创建默认管理员
运行以下脚本创建默认管理员用户：

```bash
# 在容器内运行
docker exec hospital_backend_offline python scripts/init_admin.py
```

默认管理员账号：
- 用户名：`admin`
- 密码：`admin123`
- **重要**：首次登录后请立即修改密码！

### 数据库初始化
运行 `scripts/init-database.sh` 会自动：
1. 执行数据库迁移
2. 创建默认角色（admin 和 user）
3. 创建默认管理员用户

## 业务规则

### 创建用户
1. 必须指定角色（admin 或 user）
2. 普通用户必须指定所属医疗机构
3. 管理员不能指定所属医疗机构

### 更新用户
1. 可以切换用户角色
2. 切换为管理员时，自动清空医疗机构
3. 切换为普通用户时，必须指定医疗机构
4. 管理员不能设置医疗机构

### 登录行为
1. **管理员登录**：
   - 登录成功后，需要调用 `/hospitals/{hospital_id}/activate` 激活医疗机构
   - 可以随时切换激活的医疗机构
   
2. **普通用户登录**：
   - 登录成功后，自动激活所属医疗机构
   - 不能切换医疗机构

## 迁移指南

### 从旧版本升级

如果你的系统已有用户数据，需要：

1. **运行数据库迁移**
```bash
docker exec hospital_backend_offline alembic upgrade head
```

2. **为现有用户分配角色**
```sql
-- 为所有用户分配默认角色（普通用户）
INSERT INTO user_roles (user_id, role_id, created_at)
SELECT u.id, r.id, NOW()
FROM users u
CROSS JOIN roles r
WHERE r.code = 'user'
AND NOT EXISTS (
    SELECT 1 FROM user_roles ur WHERE ur.user_id = u.id
);
```

3. **创建管理员用户**
```bash
docker exec hospital_backend_offline python scripts/init_admin.py
```

## 测试建议

1. **测试管理员功能**
   - 创建管理员用户
   - 验证不能设置医疗机构
   - 登录后测试激活不同医疗机构

2. **测试普通用户功能**
   - 创建普通用户并指定医疗机构
   - 验证必须设置医疗机构
   - 登录后验证只能访问所属医疗机构数据

3. **测试角色切换**
   - 将普通用户改为管理员
   - 验证医疗机构被清空
   - 将管理员改为普通用户
   - 验证必须设置医疗机构

## 注意事项

1. **安全性**：默认管理员密码为 `admin123`，生产环境必须立即修改
2. **数据完整性**：普通用户必须关联医疗机构，否则无法创建
3. **权限控制**：后续需要在各个API中添加基于角色的权限检查
4. **医疗机构激活**：前端需要实现医疗机构激活和切换功能

## 后续优化建议

1. 在各个API中添加基于角色的权限检查
2. 实现前端医疗机构激活和切换界面
3. 添加用户操作日志记录
4. 实现更细粒度的权限控制（如果需要）
