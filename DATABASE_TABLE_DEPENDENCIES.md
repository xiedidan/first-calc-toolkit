# 数据库表依赖关系图

## 表导入顺序总览

```
层级 1: 基础表（无外键依赖）
├── alembic_version
├── permissions
├── roles ⭐
├── hospitals ⭐
├── data_sources
└── system_settings

层级 2: 依赖基础表
├── users ⭐ (依赖: roles, hospitals)
├── role_permissions (依赖: roles, permissions)
├── departments (依赖: hospitals)
├── model_versions (依赖: hospitals)
└── data_templates ⭐ (依赖: hospitals)

层级 3: 用户角色关联
└── user_roles ⭐ (依赖: users, roles)

层级 4: 业务数据
├── charge_items (依赖: hospitals, departments)
├── model_nodes (依赖: model_versions)
├── calculation_workflows (依赖: model_versions)
└── model_version_imports (依赖: model_versions)

层级 5: 计算相关
├── calculation_steps (依赖: calculation_workflows)
├── calculation_tasks (依赖: calculation_steps, model_versions)
└── dimension_item_mappings (依赖: charge_items)

层级 6: 结果数据
├── calculation_step_logs (依赖: calculation_tasks)
├── calculation_results (依赖: calculation_tasks)
└── calculation_summaries (依赖: calculation_tasks)
```

⭐ = 本次更新涉及的表

---

## 详细依赖关系

### 1. 角色和用户体系

```
┌─────────────┐
│   roles     │  角色表（基础表）
│  - id (PK)  │  - admin: 管理员
│  - code     │  - user: 普通用户
│  - name     │
└──────┬──────┘
       │
       │ 被引用
       ↓
┌─────────────────────┐
│   user_roles        │  用户角色关联表
│  - id (PK)          │
│  - user_id (FK) ────┼──→ users.id
│  - role_id (FK) ────┼──→ roles.id
└─────────────────────┘
       ↑
       │ 引用
       │
┌──────┴──────┐
│   users     │  用户表
│  - id (PK)  │
│  - username │
│  - hospital_id (FK) ──→ hospitals.id
└─────────────┘
```

**关键点：**
- `roles` 必须先于 `users` 导入
- `users` 必须先于 `user_roles` 导入
- 管理员用户的 `hospital_id` 为 NULL
- 普通用户的 `hospital_id` 必须有值

### 2. 医疗机构体系

```
┌─────────────┐
│  hospitals  │  医疗机构表（基础表）
│  - id (PK)  │
│  - code     │
│  - name     │
└──────┬──────┘
       │
       │ 被引用
       ├────────────────────────────┐
       │                            │
       ↓                            ↓
┌─────────────┐              ┌─────────────┐
│   users     │              │ departments │
│  - hospital_id (FK)        │  - hospital_id (FK)
└─────────────┘              └──────┬──────┘
                                    │
                                    │ 被引用
                                    ↓
                             ┌─────────────┐
                             │charge_items │
                             │  - hospital_id (FK)
                             │  - department_id (FK)
                             └─────────────┘
```

**关键点：**
- `hospitals` 必须先于所有依赖它的表导入
- 包括：users, departments, charge_items, model_versions, data_templates

### 3. 模型版本体系

```
┌─────────────┐
│  hospitals  │
└──────┬──────┘
       │
       │ 被引用
       ↓
┌─────────────────┐
│ model_versions  │  模型版本表
│  - id (PK)      │
│  - hospital_id (FK)
└────────┬────────┘
         │
         │ 被引用
         ├──────────────────────────┐
         │                          │
         ↓                          ↓
┌─────────────────┐      ┌──────────────────────┐
│  model_nodes    │      │calculation_workflows │
│  - version_id (FK)     │  - version_id (FK)   │
└─────────────────┘      └──────────┬───────────┘
                                    │
                                    │ 被引用
                                    ↓
                         ┌──────────────────────┐
                         │ calculation_steps    │
                         │  - workflow_id (FK)  │
                         └──────────┬───────────┘
                                    │
                                    │ 被引用
                                    ↓
                         ┌──────────────────────┐
                         │ calculation_tasks    │
                         │  - step_id (FK)      │
                         │  - version_id (FK)   │
                         └──────────────────────┘
```

### 4. 数据模板体系（新增）

```
┌─────────────┐
│  hospitals  │
└──────┬──────┘
       │
       │ 被引用
       ↓
┌─────────────────┐
│ data_templates  │  数据模板表（新增）
│  - id (PK)      │
│  - hospital_id (FK)
│  - name         │
│  - template_type│
└─────────────────┘
```

**关键点：**
- `data_templates` 依赖 `hospitals`
- 必须在 `hospitals` 之后导入

---

## 导入脚本配置

在 `backend/import_database.py` 中定义的导入顺序：

```python
TABLE_IMPORT_ORDER = [
    # 层级 1: 基础表
    "alembic_version",
    "permissions",
    "roles",                    # ⭐ 必须在 users 之前
    "hospitals",                # ⭐ 必须在 users 之前
    "data_sources",
    "system_settings",
    
    # 层级 2: 依赖基础表
    "users",                    # ⭐ 依赖 roles 和 hospitals
    "role_permissions",
    "departments",
    "model_versions",
    "data_templates",           # ⭐ 新增，依赖 hospitals
    
    # 层级 3: 用户角色关联
    "user_roles",               # ⭐ 依赖 users 和 roles
    
    # 层级 4-6: 其他业务表
    # ...
]
```

---

## 外键约束说明

### users 表
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hospital_id INTEGER REFERENCES hospitals(id) ON DELETE SET NULL,
    -- 其他字段...
);
```
- `hospital_id` 可以为 NULL（管理员）
- 外键约束：`ON DELETE SET NULL`

### user_roles 表
```sql
CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    -- 其他字段...
);
```
- 两个外键都不能为 NULL
- 外键约束：`ON DELETE CASCADE`

### data_templates 表
```sql
CREATE TABLE data_templates (
    id SERIAL PRIMARY KEY,
    hospital_id INTEGER NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    -- 其他字段...
);
```
- `hospital_id` 不能为 NULL
- 外键约束：`ON DELETE CASCADE`

---

## 数据完整性检查

### 检查角色数据
```sql
-- 应该有 2 条记录
SELECT * FROM roles ORDER BY code;
```

预期结果：
```
 id |   name   | code  |           description
----+----------+-------+--------------------------------
  1 | 管理员   | admin | 系统管理员，可访问所有医疗机构
  2 | 普通用户 | user  | 普通用户，只能访问所属医疗机构
```

### 检查用户角色关联
```sql
-- 检查所有用户都有角色
SELECT u.username, u.name, r.code as role, h.name as hospital
FROM users u
LEFT JOIN user_roles ur ON u.id = ur.user_id
LEFT JOIN roles r ON ur.role_id = r.id
LEFT JOIN hospitals h ON u.hospital_id = h.id
ORDER BY u.id;
```

### 检查孤立记录
```sql
-- 检查没有角色的用户
SELECT * FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM user_roles ur WHERE ur.user_id = u.id
);

-- 检查引用不存在医疗机构的用户
SELECT * FROM users u
WHERE u.hospital_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM hospitals h WHERE h.id = u.hospital_id
);
```

---

## 迁移版本依赖

```
33b1cc715d32 (初始迁移: users, roles, permissions)
    ↓
b1cd20417f09 (用户表更新)
    ↓
... (其他迁移)
    ↓
20251106_data_templates (数据模板表)
    ↓
20251106_add_default_roles (插入默认角色) ⭐
```

**关键迁移：**
- `20251106_add_default_roles`: 插入 admin 和 user 角色
- 必须在创建用户之前执行

---

## 故障排查

### 问题 1: 角色表为空
```bash
# 检查迁移是否执行
docker exec hospital_backend_offline alembic current

# 手动插入角色
docker exec -it hospital_backend_offline psql $DATABASE_URL -c "
INSERT INTO roles (name, code, description, created_at, updated_at)
VALUES 
  ('管理员', 'admin', '系统管理员', NOW(), NOW()),
  ('普通用户', 'user', '普通用户', NOW(), NOW())
ON CONFLICT (code) DO NOTHING;
"
```

### 问题 2: 用户没有角色
```bash
# 为所有用户分配默认角色
docker exec -it hospital_backend_offline psql $DATABASE_URL -c "
INSERT INTO user_roles (user_id, role_id, created_at)
SELECT u.id, r.id, NOW()
FROM users u
CROSS JOIN roles r
WHERE r.code = 'user'
AND NOT EXISTS (
    SELECT 1 FROM user_roles ur WHERE ur.user_id = u.id
);
"
```

### 问题 3: 外键约束冲突
```bash
# 检查外键约束
docker exec -it hospital_backend_offline psql $DATABASE_URL -c "
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name;
"
```

---

## 最佳实践

1. **始终按顺序导入**
   - 使用 `import_database.py` 脚本
   - 不要手动调整导入顺序

2. **验证基础数据**
   - 导入后检查 roles 表
   - 确保 admin 和 user 角色存在

3. **检查外键完整性**
   - 导入完成后运行完整性检查
   - 修复孤立记录

4. **备份重要数据**
   - 导入前备份现有数据
   - 保留导出文件

5. **测试导入结果**
   - 运行 `test_user_roles.py`
   - 验证用户登录功能

---

**文档版本**: 1.0.0  
**最后更新**: 2025-11-06
