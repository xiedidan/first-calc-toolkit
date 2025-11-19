# 医院科室业务价值评估工具 - 完整离线部署指南

## 目录
1. [部署包构建](#部署包构建)
2. [离线部署步骤](#离线部署步骤)
3. [数据库初始化](#数据库初始化)
4. [表恢复顺序说明](#表恢复顺序说明)
5. [角色和用户初始化](#角色和用户初始化)
6. [验证部署](#验证部署)
7. [常见问题](#常见问题)

---

## 部署包构建

### 前置条件
- Docker Desktop 已安装并运行
- 有网络连接（用于拉取基础镜像）
- 至少 10GB 可用磁盘空间

### 构建步骤

```bash
# 1. 进入项目根目录
cd /path/to/project

# 2. 运行构建脚本
bash scripts/build-offline-package.sh
```

构建脚本会自动完成：
1. 拉取基础镜像（Python、Node、Nginx、Redis）
2. 构建应用镜像（后端、前端）
3. 导出所有镜像为 tar.gz 文件
4. 导出数据库数据（如果配置了 .env）
5. 打包配置文件和脚本
6. 生成最终部署包

### 构建产物

```
hospital-value-toolkit-offline-v1.0.0.tar.gz  (约 500MB-1GB)
├── images/
│   ├── backend.tar.gz      # 后端镜像
│   ├── frontend.tar.gz     # 前端镜像
│   └── redis.tar.gz        # Redis镜像
├── database/
│   └── database_export.json.gz  # 数据库数据（可选）
├── config/
│   ├── docker-compose.offline.yml
│   └── .env.offline.template
├── scripts/
│   ├── deploy-offline.sh
│   ├── load-images.sh
│   ├── init-database.sh
│   └── check-prerequisites.sh
├── docs/
│   └── OFFLINE_DEPLOYMENT_GUIDE.md
└── README.md
```

---

## 离线部署步骤

### 1. 传输部署包

将构建好的部署包传输到目标服务器：

```bash
# 使用 scp
scp hospital-value-toolkit-offline-v1.0.0.tar.gz user@server:/path/to/deploy/

# 或使用 U盘/移动硬盘物理传输
```

### 2. 解压部署包

```bash
# 在目标服务器上
cd /path/to/deploy
tar -xzf hospital-value-toolkit-offline-v1.0.0.tar.gz
cd offline-package
```

### 3. 检查前置条件

```bash
bash scripts/check-prerequisites.sh
```

检查项目：
- Docker 是否安装（版本 >= 20.10）
- Docker Compose 是否安装（版本 >= 2.0）
- PostgreSQL 客户端工具（psql）
- 磁盘空间（至少 50GB）
- 内存（至少 8GB）

### 4. 导入 Docker 镜像

```bash
bash scripts/load-images.sh
```

这会导入：
- hospital-backend:latest
- hospital-frontend:latest
- redis:7-alpine

### 5. 配置环境

```bash
# 复制配置模板
cp config/.env.offline.template .env

# 编辑配置文件
vi .env
```

**必须配置的项目：**

```bash
# 数据库连接（使用已有的 PostgreSQL 实例）
DATABASE_URL=postgresql://username:password@host:5432/database_name

# JWT 密钥（生成方法见下）
SECRET_KEY=your-secret-key-here

# 加密密钥（生成方法见下）
ENCRYPTION_KEY=your-encryption-key-here

# 服务端口
BACKEND_PORT=8000
FRONTEND_PORT=80
```

**生成密钥：**

```bash
# 生成 SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 生成 ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 6. 启动服务

```bash
# 使用 docker-compose 启动
docker-compose -f config/docker-compose.offline.yml up -d

# 查看服务状态
docker-compose -f config/docker-compose.offline.yml ps

# 查看日志
docker-compose -f config/docker-compose.offline.yml logs -f
```

---

## 数据库初始化

### 方式一：使用初始化脚本（推荐）

```bash
bash scripts/init-database.sh
```

这个脚本会自动：
1. 检查数据库连接
2. 执行数据库迁移（创建表结构）
3. 插入默认角色（admin 和 user）
4. 创建默认管理员用户
5. 导入数据（如果有 database_export.json.gz）

### 方式二：手动初始化

#### 步骤 1：执行数据库迁移

```bash
# 进入后端容器
docker exec -it hospital_backend_offline bash

# 执行迁移
alembic upgrade head

# 退出容器
exit
```

#### 步骤 2：初始化角色和管理员

```bash
# 在后端容器中执行
docker exec hospital_backend_offline python scripts/init_admin.py
```

#### 步骤 3：导入数据（可选）

如果有数据导出文件：

```bash
# 解压数据文件
gunzip -c database/database_export.json.gz > database/database_export.json

# 复制到容器
docker cp database/database_export.json hospital_backend_offline:/app/

# 导入数据
docker exec hospital_backend_offline python import_database.py

# 清理临时文件
rm database/database_export.json
```

---

## 表恢复顺序说明

数据库表的导入必须按照外键依赖关系的顺序进行，`import_database.py` 已经定义了正确的顺序：

### 第一层：基础表（无外键依赖）
```
1. alembic_version      # 迁移版本记录
2. permissions          # 权限表
3. roles                # 角色表 ⭐
4. hospitals            # 医疗机构表 ⭐
5. data_sources         # 数据源表
6. system_settings      # 系统设置表
```

### 第二层：依赖基础表
```
7. users                # 用户表（依赖 roles 和 hospitals）⭐
8. role_permissions     # 角色权限关联表
9. departments          # 科室表（依赖 hospitals）
10. model_versions      # 模型版本表（依赖 hospitals）
11. data_templates      # 数据模板表（依赖 hospitals）⭐
```

### 第三层：用户角色关联
```
12. user_roles          # 用户角色关联表（依赖 users 和 roles）⭐
```

### 第四层：业务数据
```
13. charge_items        # 收费项目表
14. model_nodes         # 模型节点表
15. calculation_workflows  # 计算工作流表
16. model_version_imports  # 模型导入记录表
```

### 第五层：计算相关
```
17. calculation_steps   # 计算步骤表
18. calculation_tasks   # 计算任务表
19. dimension_item_mappings  # 维度项映射表
```

### 第六层：结果数据
```
20. calculation_step_logs    # 计算步骤日志表
21. calculation_results      # 计算结果表
22. calculation_summaries    # 计算汇总表
```

**⭐ 标记的表是本次更新新增或修改的表**

### 关键依赖关系

```
roles (角色表)
  ↓
users (用户表) ← hospitals (医疗机构表)
  ↓
user_roles (用户角色关联表)
```

**重要提示：**
- `roles` 表必须在 `users` 表之前导入
- `hospitals` 表必须在 `users` 表之前导入
- `user_roles` 表必须在 `users` 和 `roles` 表之后导入
- 导入脚本会自动跳过已存在的记录，避免主键冲突

---

## 角色和用户初始化

### 默认角色

系统会自动创建两个角色：

| 角色代码 | 角色名称 | 说明 |
|---------|---------|------|
| admin   | 管理员   | 可访问所有医疗机构和功能 |
| user    | 普通用户 | 只能访问所属医疗机构的数据 |

### 默认管理员账号

初始化脚本会自动创建默认管理员：

- **用户名**: `admin`
- **密码**: `admin123`
- **角色**: 管理员
- **医疗机构**: 无（管理员不属于任何医疗机构）

**⚠️ 安全提示：首次登录后请立即修改密码！**

### 手动创建管理员

如果需要手动创建管理员：

```bash
docker exec -it hospital_backend_offline python scripts/init_admin.py
```

### 验证角色和用户

```bash
# 运行测试脚本
docker exec hospital_backend_offline python scripts/test_user_roles.py
```

测试脚本会检查：
- admin 和 user 角色是否存在
- 默认管理员用户是否创建
- 医疗机构数据是否存在
- 普通用户数据是否正确

---

## 验证部署

### 1. 检查服务状态

```bash
# 查看容器状态
docker-compose -f config/docker-compose.offline.yml ps

# 应该看到所有服务都是 Up 状态
```

### 2. 检查后端 API

```bash
# 测试健康检查接口
curl http://localhost:8000/health

# 应该返回: {"status":"healthy"}
```

### 3. 访问前端

打开浏览器访问：`http://localhost:80`

### 4. 登录测试

使用默认管理员账号登录：
- 用户名：`admin`
- 密码：`admin123`

### 5. 功能测试

登录后测试以下功能：
- [ ] 用户管理界面
- [ ] 创建普通用户并指定医疗机构
- [ ] 编辑用户角色
- [ ] 查看角色和医疗机构信息
- [ ] 医疗机构切换（管理员）
- [ ] 数据访问权限（普通用户）

---

## 常见问题

### Q1: 数据库迁移失败

**问题**: `alembic upgrade head` 报错

**解决方案**:
```bash
# 检查数据库连接
docker exec hospital_backend_offline python -c "from app.database import engine; print(engine.url)"

# 查看当前迁移版本
docker exec hospital_backend_offline alembic current

# 查看迁移历史
docker exec hospital_backend_offline alembic history

# 如果版本混乱，可以重置到特定版本
docker exec hospital_backend_offline alembic downgrade <revision>
docker exec hospital_backend_offline alembic upgrade head
```

### Q2: 角色创建失败

**问题**: 提示角色已存在或创建失败

**解决方案**:
```bash
# 检查角色表
docker exec hospital_backend_offline python -c "
from app.database import SessionLocal
from app.models.role import Role
db = SessionLocal()
roles = db.query(Role).all()
for r in roles:
    print(f'{r.code}: {r.name}')
db.close()
"

# 如果角色不存在，手动插入
docker exec -it hospital_backend_offline psql $DATABASE_URL -c "
INSERT INTO roles (name, code, description, created_at, updated_at)
VALUES 
  ('管理员', 'admin', '系统管理员', NOW(), NOW()),
  ('普通用户', 'user', '普通用户', NOW(), NOW())
ON CONFLICT (code) DO NOTHING;
"
```

### Q3: 管理员用户创建失败

**问题**: 提示用户已存在或创建失败

**解决方案**:
```bash
# 检查用户是否存在
docker exec hospital_backend_offline python -c "
from app.database import SessionLocal
from app.models.user import User
db = SessionLocal()
admin = db.query(User).filter(User.username == 'admin').first()
if admin:
    print(f'管理员已存在: {admin.name}')
    print(f'角色: {[r.code for r in admin.roles]}')
else:
    print('管理员不存在')
db.close()
"

# 如果需要重置管理员密码
docker exec hospital_backend_offline python -c "
from app.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash
db = SessionLocal()
admin = db.query(User).filter(User.username == 'admin').first()
if admin:
    admin.hashed_password = get_password_hash('admin123')
    db.commit()
    print('密码已重置为: admin123')
db.close()
"
```

### Q4: 数据导入时主键冲突

**问题**: 导入数据时提示主键冲突

**解决方案**:
导入脚本默认会跳过已存在的记录。如果需要强制覆盖：

```bash
# 修改 import_database.py 中的 skip_existing 参数
# 或者先清空表再导入（⚠️ 注意数据丢失风险）

# 清空特定表
docker exec -it hospital_backend_offline psql $DATABASE_URL -c "
TRUNCATE TABLE table_name CASCADE;
"
```

### Q5: 序列号不同步

**问题**: 插入新记录时提示主键冲突

**解决方案**:
```bash
# 运行序列重置脚本
docker exec hospital_backend_offline python reset_sequences.py

# 或手动重置特定表的序列
docker exec -it hospital_backend_offline psql $DATABASE_URL -c "
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('roles_id_seq', (SELECT MAX(id) FROM roles));
"
```

### Q6: 容器无法启动

**问题**: Docker 容器启动失败

**解决方案**:
```bash
# 查看容器日志
docker-compose -f config/docker-compose.offline.yml logs backend
docker-compose -f config/docker-compose.offline.yml logs frontend

# 检查端口占用
netstat -tulpn | grep 8000
netstat -tulpn | grep 80

# 重新构建并启动
docker-compose -f config/docker-compose.offline.yml down
docker-compose -f config/docker-compose.offline.yml up -d --force-recreate
```

### Q7: 前端无法连接后端

**问题**: 前端页面显示网络错误

**解决方案**:
```bash
# 检查后端是否正常运行
curl http://localhost:8000/health

# 检查前端配置
docker exec hospital_frontend_offline cat /etc/nginx/conf.d/default.conf

# 检查网络连接
docker network ls
docker network inspect offline-package_default
```

---

## 维护命令

### 查看服务状态
```bash
docker-compose -f config/docker-compose.offline.yml ps
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose -f config/docker-compose.offline.yml logs -f

# 查看特定服务日志
docker-compose -f config/docker-compose.offline.yml logs -f backend
docker-compose -f config/docker-compose.offline.yml logs -f frontend
```

### 重启服务
```bash
# 重启所有服务
docker-compose -f config/docker-compose.offline.yml restart

# 重启特定服务
docker-compose -f config/docker-compose.offline.yml restart backend
```

### 停止服务
```bash
docker-compose -f config/docker-compose.offline.yml stop
```

### 启动服务
```bash
docker-compose -f config/docker-compose.offline.yml start
```

### 完全清理
```bash
# 停止并删除容器
docker-compose -f config/docker-compose.offline.yml down

# 删除镜像（如需重新导入）
docker rmi hospital-backend:latest hospital-frontend:latest redis:7-alpine
```

---

## 技术支持

如遇到其他问题，请：
1. 查看日志文件
2. 检查配置文件
3. 参考本文档的常见问题部分
4. 联系技术支持团队

---

**文档版本**: 1.0.0  
**最后更新**: 2025-11-06  
**适用版本**: hospital-value-toolkit v1.0.0
