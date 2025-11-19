# 开发计划 - 用户认证与权限模块

## 📋 开发顺序

### 阶段1：数据库和模型层 ✅ 开始
1. 创建数据库表结构（Alembic迁移）
2. 定义SQLAlchemy模型
3. 创建Pydantic schemas

### 阶段2：后端API实现
1. 用户认证API（登录、JWT）
2. 用户管理API
3. 角色管理API
4. 权限管理API

### 阶段3：前端实现
1. 登录页面
2. 路由守卫和权限控制
3. 用户管理页面
4. 角色管理页面

## 🎯 当前任务：阶段1 - 数据库和模型层

### 任务列表

- [ ] 1. 初始化Alembic
- [ ] 2. 创建用户表（users）
- [ ] 3. 创建角色表（roles）
- [ ] 4. 创建权限表（permissions）
- [ ] 5. 创建用户-角色关联表（user_roles）
- [ ] 6. 创建角色-权限关联表（role_permissions）
- [ ] 7. 创建SQLAlchemy模型
- [ ] 8. 创建Pydantic schemas
- [ ] 9. 创建初始数据（管理员用户）

## 📊 数据库表设计

### users（用户表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| username | VARCHAR(50) | 用户名，唯一 |
| name | VARCHAR(100) | 姓名 |
| email | VARCHAR(100) | 邮箱 |
| hashed_password | VARCHAR(255) | 加密密码 |
| status | VARCHAR(20) | 状态（active/inactive/locked） |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### roles（角色表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(50) | 角色名称 |
| code | VARCHAR(50) | 角色编码，唯一 |
| description | TEXT | 角色描述 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### permissions（权限表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(50) | 权限名称 |
| code | VARCHAR(50) | 权限编码，唯一 |
| resource | VARCHAR(50) | 资源类型 |
| action | VARCHAR(50) | 操作类型 |
| created_at | TIMESTAMP | 创建时间 |

### user_roles（用户-角色关联表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户ID |
| role_id | INTEGER | 角色ID |
| created_at | TIMESTAMP | 创建时间 |

### role_permissions（角色-权限关联表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| role_id | INTEGER | 角色ID |
| permission_id | INTEGER | 权限ID |
| created_at | TIMESTAMP | 创建时间 |

## 🔐 初始数据

### 默认角色
1. **admin** - 系统管理员（所有权限）
2. **model_designer** - 模型设计师/管理员
3. **data_analyst** - 数据分析师/操作员
4. **business_expert** - 业务专家
5. **dept_manager** - 科室管理者

### 默认管理员用户
- 用户名：admin
- 密码：admin123（首次登录需修改）
- 角色：admin

## 📝 下一步

完成阶段1后，将开始实现后端API。
