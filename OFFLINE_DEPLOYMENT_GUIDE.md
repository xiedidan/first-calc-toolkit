# 离线部署快速指南

## 一、在Windows 11上构建部署包

### 1. 前置条件
- ✅ 已安装Docker Desktop
- ✅ Docker Desktop正在运行
- ✅ 项目代码完整

### 2. 构建部署包

在项目根目录打开PowerShell，执行：

```powershell
.\scripts\build-offline-package.ps1
```

脚本会自动：
1. 构建Docker镜像（后端、前端）
2. 拉取Redis镜像
3. 导出所有镜像为tar.gz文件
4. 导出数据库数据（如果配置了.env）
5. 打包配置文件和脚本
6. 生成最终部署包

### 3. 输出文件

构建完成后会生成：
- `hospital-value-toolkit-offline-v1.0.tar.gz` - 完整部署包（约500MB）

---

## 二、在Linux服务器上部署

### 1. 传输部署包

将部署包传输到目标Linux服务器：

```bash
# 使用scp
scp hospital-value-toolkit-offline-v1.0.tar.gz user@server:/path/to/deploy/

# 或使用其他方式（U盘、内网文件共享等）
```

### 2. 解压部署包

```bash
tar -xzf hospital-value-toolkit-offline-v1.0.tar.gz
cd offline-package
```

### 3. 一键部署

```bash
bash scripts/deploy-offline.sh
```

首次运行会提示配置环境变量，按提示操作即可。

### 4. 配置环境变量

编辑 `.env` 文件：

```bash
vi .env
```

**必须修改的配置**：

```bash
# 数据库连接（修改为实际的连接信息）
DATABASE_URL=postgresql://admin:password@host.docker.internal:5432/hospital_value

# JWT密钥（生成随机密钥）
SECRET_KEY=your-secret-key-change-this

# 加密密钥（生成随机密钥）
ENCRYPTION_KEY=your-encryption-key-change-this
```

**生成密钥**：

```bash
# 生成SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 生成ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 5. 再次运行部署脚本

配置完成后，再次运行：

```bash
bash scripts/deploy-offline.sh
```

这次会完整执行所有部署步骤。

---

## 三、验证部署

### 1. 检查容器状态

```bash
docker-compose -f config/docker-compose.offline.yml ps
```

所有容器应该显示为 `Up` 状态。

### 2. 访问系统

- **前端**: http://服务器IP:80
- **后端API文档**: http://服务器IP:8000/docs

### 3. 测试登录

使用默认账号登录（如果已导入数据）。

---

## 四、常用操作

### 查看日志

```bash
# 查看所有服务日志
docker-compose -f config/docker-compose.offline.yml logs -f

# 查看特定服务日志
docker logs hospital_backend_offline
docker logs hospital_frontend_offline
docker logs hospital_celery_offline
```

### 停止服务

```bash
docker-compose -f config/docker-compose.offline.yml stop
```

### 启动服务

```bash
docker-compose -f config/docker-compose.offline.yml start
```

### 重启服务

```bash
docker-compose -f config/docker-compose.offline.yml restart
```

### 完全停止并删除容器

```bash
docker-compose -f config/docker-compose.offline.yml down
```

---

## 五、故障排查

### 问题1: 容器无法启动

**检查**：
```bash
docker logs hospital_backend_offline
```

**常见原因**：
- 数据库连接失败
- 端口被占用
- 配置文件错误

### 问题2: 无法连接数据库

**检查数据库连接**：
```bash
# 在宿主机测试
psql -h localhost -p 5432 -U admin -d hospital_value

# 在容器内测试
docker exec hospital_backend_offline ping host.docker.internal
```

**解决方案**：
- 确认PostgreSQL正在运行
- 确认DATABASE_URL配置正确
- 确认防火墙允许连接

### 问题3: 前端无法访问后端

**检查网络**：
```bash
docker exec hospital_frontend_offline ping backend
```

**检查Nginx配置**：
```bash
docker exec hospital_frontend_offline cat /etc/nginx/conf.d/default.conf
```

---

## 六、数据库说明

### 使用现有PostgreSQL

系统默认连接宿主机的PostgreSQL数据库，通过 `host.docker.internal` 访问。

### 数据导入

部署脚本会自动导入 `database/hospital_value.sql.gz` 中的数据。

如果需要手动导入：

```bash
gunzip -c database/hospital_value.sql.gz | \
  psql -h localhost -p 5432 -U admin -d hospital_value
```

---

## 七、系统要求

### 硬件要求

**最低配置**：
- CPU: 4核心
- 内存: 8GB
- 磁盘: 50GB

**推荐配置**：
- CPU: 8核心或更多
- 内存: 16GB或更多
- 磁盘: 100GB SSD

### 软件要求

- Linux操作系统（CentOS 7+, Ubuntu 18.04+）
- Docker 20.10+
- Docker Compose 2.0+
- PostgreSQL数据库（已有实例）

---

## 八、技术支持

如遇问题，请：
1. 查看日志文件
2. 检查配置文件
3. 参考详细文档：`docs/离线部署方案.md`

---

**部署完成后，即可开始使用系统！**
