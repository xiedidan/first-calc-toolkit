# 离线部署快速参考卡片

## 🚀 快速部署（5步）

```bash
# 1. 解压部署包
tar -xzf hospital-value-toolkit-offline-v1.0.0.tar.gz
cd offline-package

# 2. 导入镜像
bash scripts/load-images.sh

# 3. 配置环境
cp config/.env.offline.template .env
vi .env  # 配置数据库连接

# 4. 启动服务
docker-compose -f config/docker-compose.offline.yml up -d

# 5. 初始化数据库
bash scripts/init-database.sh
```

## 📋 必须配置项

```bash
# .env 文件
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
```

## 🔑 默认账号

| 项目 | 值 |
|------|-----|
| 用户名 | admin |
| 密码 | admin123 |
| 角色 | 管理员 |

⚠️ **首次登录后立即修改密码！**

## 📊 表导入顺序（关键）

```
1. roles ⭐          # 必须第一
2. hospitals ⭐      # 必须第二
3. users ⭐          # 依赖 1,2
4. user_roles ⭐     # 依赖 3
5. data_templates ⭐ # 依赖 2
6. 其他业务表...
```

## 🔧 常用命令

### 服务管理
```bash
# 查看状态
docker-compose -f config/docker-compose.offline.yml ps

# 查看日志
docker-compose -f config/docker-compose.offline.yml logs -f

# 重启服务
docker-compose -f config/docker-compose.offline.yml restart

# 停止服务
docker-compose -f config/docker-compose.offline.yml stop
```

### 数据库操作
```bash
# 执行迁移
docker exec hospital_backend_offline alembic upgrade head

# 初始化管理员
docker exec hospital_backend_offline python scripts/init_admin.py

# 测试角色
docker exec hospital_backend_offline python scripts/test_user_roles.py

# 重置序列
docker exec hospital_backend_offline python reset_sequences.py
```

### 数据导入
```bash
# 导入数据
docker cp database/database_export.json hospital_backend_offline:/app/
docker exec hospital_backend_offline python import_database.py
```

## 🩺 健康检查

```bash
# 后端健康检查
curl http://localhost:8000/health
# 预期: {"status":"healthy"}

# 前端访问
curl http://localhost:80
# 预期: HTML 页面

# 数据库连接
docker exec hospital_backend_offline python -c "from app.database import engine; print('OK')"
```

## ❌ 常见错误

### 错误 1: 数据库连接失败
```bash
# 检查数据库是否运行
psql -h localhost -U user -d dbname

# 检查 .env 配置
cat .env | grep DATABASE_URL
```

### 错误 2: 角色不存在
```bash
# 手动插入角色
docker exec -it hospital_backend_offline psql $DATABASE_URL -c "
INSERT INTO roles (name, code, description, created_at, updated_at)
VALUES 
  ('管理员', 'admin', '系统管理员', NOW(), NOW()),
  ('普通用户', 'user', '普通用户', NOW(), NOW())
ON CONFLICT (code) DO NOTHING;
"
```

### 错误 3: 管理员创建失败
```bash
# 重新创建管理员
docker exec hospital_backend_offline python scripts/init_admin.py

# 或重置密码
docker exec hospital_backend_offline python -c "
from app.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash
db = SessionLocal()
admin = db.query(User).filter(User.username == 'admin').first()
if admin:
    admin.hashed_password = get_password_hash('admin123')
    db.commit()
    print('密码已重置')
db.close()
"
```

### 错误 4: 端口被占用
```bash
# 检查端口占用
netstat -tulpn | grep 8000
netstat -tulpn | grep 80

# 修改 .env 中的端口
BACKEND_PORT=8001
FRONTEND_PORT=8080
```

### 错误 5: 容器无法启动
```bash
# 查看详细日志
docker-compose -f config/docker-compose.offline.yml logs backend

# 强制重建
docker-compose -f config/docker-compose.offline.yml down
docker-compose -f config/docker-compose.offline.yml up -d --force-recreate
```

## 📁 目录结构

```
offline-package/
├── images/              # Docker 镜像
│   ├── backend.tar.gz
│   ├── frontend.tar.gz
│   └── redis.tar.gz
├── database/            # 数据库数据
│   └── database_export.json.gz
├── config/              # 配置文件
│   ├── docker-compose.offline.yml
│   └── .env.offline.template
├── scripts/             # 部署脚本
│   ├── deploy-offline.sh
│   ├── load-images.sh
│   ├── init-database.sh
│   └── check-prerequisites.sh
├── docs/                # 文档
│   ├── OFFLINE_DEPLOYMENT_COMPLETE_GUIDE.md
│   └── DATABASE_TABLE_DEPENDENCIES.md
└── README.md
```

## 🔍 验证清单

- [ ] Docker 镜像已导入
- [ ] 配置文件已创建（.env）
- [ ] 数据库连接正常
- [ ] 容器全部运行
- [ ] 数据库迁移完成
- [ ] 角色表有数据（admin, user）
- [ ] 管理员用户已创建
- [ ] 前端可以访问
- [ ] 后端 API 正常
- [ ] 可以登录系统

## 📞 获取帮助

1. 查看完整文档：`docs/OFFLINE_DEPLOYMENT_COMPLETE_GUIDE.md`
2. 查看表依赖关系：`docs/DATABASE_TABLE_DEPENDENCIES.md`
3. 查看用户角色说明：`USER_ROLE_MANAGEMENT.md`
4. 查看日志：`docker-compose logs -f`

## 🎯 关键文件

| 文件 | 说明 |
|------|------|
| `.env` | 环境配置（必须） |
| `docker-compose.offline.yml` | 服务编排 |
| `import_database.py` | 数据导入脚本 |
| `init_admin.py` | 管理员初始化 |
| `test_user_roles.py` | 角色测试 |

## 🔐 安全提示

1. ✅ 首次登录后修改管理员密码
2. ✅ 使用强密码生成 SECRET_KEY
3. ✅ 使用强密码生成 ENCRYPTION_KEY
4. ✅ 限制数据库访问权限
5. ✅ 定期备份数据库
6. ✅ 监控系统日志

## 📈 性能优化

```bash
# 查看容器资源使用
docker stats

# 优化数据库
docker exec -it hospital_backend_offline psql $DATABASE_URL -c "VACUUM ANALYZE;"

# 清理 Docker 缓存
docker system prune -a
```

## 🔄 更新流程

```bash
# 1. 备份数据
docker exec hospital_backend_offline python export_database.py

# 2. 停止服务
docker-compose -f config/docker-compose.offline.yml down

# 3. 导入新镜像
bash scripts/load-images.sh

# 4. 启动服务
docker-compose -f config/docker-compose.offline.yml up -d

# 5. 执行迁移
docker exec hospital_backend_offline alembic upgrade head
```

---

**版本**: 1.0.0  
**更新**: 2025-11-06  
**打印**: 建议打印此卡片作为快速参考
