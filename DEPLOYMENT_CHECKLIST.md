# 离线部署检查清单

## 📋 部署前检查

### 环境准备
- [ ] Docker 已安装（版本 >= 20.10）
- [ ] Docker Compose 已安装（版本 >= 2.0）
- [ ] PostgreSQL 数据库已准备好
- [ ] 服务器内存 >= 8GB
- [ ] 服务器磁盘空间 >= 50GB
- [ ] 网络连接正常（用于拉取基础镜像）

### 文件准备
- [ ] 离线部署包已下载
- [ ] 部署包完整性已验证
- [ ] 解压目录有足够空间

---

## 🔨 构建离线包检查

### 构建前
- [ ] 项目代码最新
- [ ] Docker Desktop 运行正常
- [ ] 有网络连接
- [ ] 磁盘空间 >= 10GB

### 构建过程
- [ ] 基础镜像拉取成功
  - [ ] python:3.12
  - [ ] node:18-alpine
  - [ ] nginx:alpine
  - [ ] redis:7-alpine
- [ ] 后端镜像构建成功
- [ ] 前端镜像构建成功
- [ ] 镜像导出成功
  - [ ] backend.tar.gz
  - [ ] frontend.tar.gz
  - [ ] redis.tar.gz
- [ ] 数据库数据导出成功（可选）
- [ ] 配置文件复制完成
- [ ] 脚本文件复制完成
- [ ] 文档复制完成
- [ ] 最终打包成功

### 构建后验证
- [ ] 部署包文件存在
- [ ] 部署包大小合理（约 500MB-1GB）
- [ ] 可以解压部署包
- [ ] 目录结构完整

---

## 📦 部署过程检查

### 1. 解压部署包
- [ ] 部署包已传输到目标服务器
- [ ] 解压成功
- [ ] 目录结构完整
  - [ ] images/
  - [ ] database/
  - [ ] config/
  - [ ] scripts/
  - [ ] docs/
  - [ ] README.md

### 2. 检查前置条件
```bash
bash scripts/check-prerequisites.sh
```
- [ ] Docker 版本检查通过
- [ ] Docker Compose 版本检查通过
- [ ] PostgreSQL 客户端工具可用
- [ ] 磁盘空间充足
- [ ] 内存充足

### 3. 导入 Docker 镜像
```bash
bash scripts/load-images.sh
```
- [ ] backend 镜像导入成功
- [ ] frontend 镜像导入成功
- [ ] redis 镜像导入成功
- [ ] 镜像列表验证
  ```bash
  docker images | grep hospital
  ```

### 4. 配置环境
```bash
cp config/.env.offline.template .env
vi .env
```
- [ ] .env 文件已创建
- [ ] DATABASE_URL 已配置
- [ ] SECRET_KEY 已生成
- [ ] ENCRYPTION_KEY 已生成
- [ ] 端口配置正确
  - [ ] BACKEND_PORT（默认 8000）
  - [ ] FRONTEND_PORT（默认 80）

### 5. 启动服务
```bash
docker-compose -f config/docker-compose.offline.yml up -d
```
- [ ] 容器启动成功
- [ ] 所有容器状态为 Up
  ```bash
  docker-compose -f config/docker-compose.offline.yml ps
  ```
- [ ] 容器列表
  - [ ] hospital_backend_offline
  - [ ] hospital_frontend_offline
  - [ ] hospital_redis_offline

### 6. 初始化数据库
```bash
bash scripts/init-database.sh
```
- [ ] 数据库连接成功
- [ ] 数据库迁移执行成功
  ```bash
  docker exec hospital_backend_offline alembic current
  ```
- [ ] 角色创建成功
  - [ ] admin 角色存在
  - [ ] user 角色存在
- [ ] 管理员用户创建成功
  - [ ] 用户名: admin
  - [ ] 密码: admin123
- [ ] 数据导入成功（如果有数据文件）

---

## ✅ 部署后验证

### 服务状态检查
```bash
# 查看容器状态
docker-compose -f config/docker-compose.offline.yml ps
```
- [ ] 所有容器运行正常
- [ ] 没有容器重启

### 日志检查
```bash
# 查看后端日志
docker-compose -f config/docker-compose.offline.yml logs backend
```
- [ ] 没有严重错误
- [ ] 应用启动成功
- [ ] 数据库连接正常

### 健康检查
```bash
# 后端健康检查
curl http://localhost:8000/health
```
- [ ] 返回 `{"status":"healthy"}`

```bash
# 前端访问
curl http://localhost:80
```
- [ ] 返回 HTML 页面

### 数据库验证
```bash
# 测试角色功能
docker exec hospital_backend_offline python scripts/test_user_roles.py
```
- [ ] 角色检查通过
  - [ ] admin 角色存在
  - [ ] user 角色存在
- [ ] 管理员用户检查通过
- [ ] 医疗机构数据检查通过（如果有）

### 数据完整性检查
```sql
-- 检查角色表
SELECT * FROM roles ORDER BY code;
```
- [ ] 有 2 条记录（admin, user）

```sql
-- 检查管理员用户
SELECT u.username, u.name, r.code as role, u.hospital_id
FROM users u
LEFT JOIN user_roles ur ON u.id = ur.user_id
LEFT JOIN roles r ON ur.role_id = r.id
WHERE u.username = 'admin';
```
- [ ] 管理员用户存在
- [ ] 角色为 admin
- [ ] hospital_id 为 NULL

```sql
-- 检查用户角色关联
SELECT COUNT(*) FROM user_roles;
```
- [ ] 至少有 1 条记录（管理员的角色关联）

### 功能测试

#### 1. 前端访问
- [ ] 打开浏览器访问 `http://localhost:80`
- [ ] 页面正常加载
- [ ] 没有 JavaScript 错误

#### 2. 登录测试
- [ ] 使用 admin/admin123 登录
- [ ] 登录成功
- [ ] 跳转到主页面

#### 3. 用户管理测试
- [ ] 访问用户管理页面
- [ ] 可以看到用户列表
- [ ] 可以看到角色列和医疗机构列
- [ ] 管理员用户显示正确
  - [ ] 角色显示为"管理员"
  - [ ] 医疗机构显示为"-"

#### 4. 创建用户测试
- [ ] 点击"新增用户"
- [ ] 可以选择角色（管理员/普通用户）
- [ ] 选择普通用户时显示医疗机构下拉框
- [ ] 选择管理员时不显示医疗机构下拉框
- [ ] 可以成功创建用户

#### 5. 编辑用户测试
- [ ] 可以编辑用户信息
- [ ] 可以切换用户角色
- [ ] 切换为管理员时自动清空医疗机构
- [ ] 切换为普通用户时必须选择医疗机构

#### 6. 医疗机构测试（如果有数据）
- [ ] 管理员可以看到所有医疗机构
- [ ] 可以激活不同的医疗机构
- [ ] 普通用户只能看到所属医疗机构

---

## 🔒 安全检查

### 密码安全
- [ ] 已修改默认管理员密码
- [ ] SECRET_KEY 使用强随机值
- [ ] ENCRYPTION_KEY 使用强随机值
- [ ] 数据库密码足够强

### 访问控制
- [ ] 数据库只允许必要的 IP 访问
- [ ] 防火墙规则配置正确
- [ ] 只开放必要的端口

### 数据安全
- [ ] 已备份原始数据
- [ ] 已备份配置文件
- [ ] 设置了定期备份计划

---

## 📊 性能检查

### 资源使用
```bash
docker stats
```
- [ ] CPU 使用率正常（< 80%）
- [ ] 内存使用率正常（< 80%）
- [ ] 没有内存泄漏

### 响应时间
- [ ] 前端页面加载时间 < 3秒
- [ ] API 响应时间 < 1秒
- [ ] 数据库查询时间正常

### 数据库性能
```sql
-- 检查表大小
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```
- [ ] 表大小合理
- [ ] 索引正常

---

## 📝 文档检查

### 部署文档
- [ ] README.md 存在
- [ ] OFFLINE_DEPLOYMENT_COMPLETE_GUIDE.md 存在
- [ ] DATABASE_TABLE_DEPENDENCIES.md 存在
- [ ] DEPLOYMENT_QUICK_REFERENCE.md 存在
- [ ] USER_ROLE_MANAGEMENT.md 存在

### 运维文档
- [ ] 记录了部署日期
- [ ] 记录了部署版本
- [ ] 记录了配置信息
- [ ] 记录了管理员账号信息
- [ ] 记录了常见问题解决方案

---

## 🎯 最终确认

### 功能完整性
- [ ] 所有核心功能正常
- [ ] 用户管理功能正常
- [ ] 角色管理功能正常
- [ ] 医疗机构管理功能正常
- [ ] 数据访问权限正常

### 稳定性
- [ ] 服务运行稳定
- [ ] 没有频繁重启
- [ ] 日志没有异常错误
- [ ] 资源使用正常

### 可维护性
- [ ] 文档完整
- [ ] 脚本可用
- [ ] 备份策略明确
- [ ] 监控方案清晰

---

## 📞 问题记录

如果遇到问题，请记录：

| 问题 | 现象 | 解决方案 | 备注 |
|------|------|----------|------|
|      |      |          |      |
|      |      |          |      |
|      |      |          |      |

---

## ✍️ 签字确认

| 角色 | 姓名 | 签字 | 日期 |
|------|------|------|------|
| 部署人员 |  |  |  |
| 测试人员 |  |  |  |
| 项目负责人 |  |  |  |

---

**检查清单版本**: 1.0.0  
**最后更新**: 2025-11-06  
**适用版本**: hospital-value-toolkit v1.0.0
