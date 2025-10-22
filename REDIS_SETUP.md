# Redis 安装和配置指南

## 问题

Celery 需要 Redis 作为消息代理（broker）和结果后端（result backend），但当前 Redis 可能未启动或未安装。

## 错误信息

```
AttributeError: 'DisabledBackend' object has no attribute '_get_task_meta_for'
```

这表示 Celery 的 result backend 被禁用了，通常是因为无法连接到 Redis。

## 解决方案

### Windows 系统

#### 方案 1: 使用 Memurai（推荐）

Memurai 是 Redis 的 Windows 原生替代品。

1. **下载 Memurai**
   - 访问：https://www.memurai.com/get-memurai
   - 下载免费的开发者版本

2. **安装**
   - 运行安装程序
   - 默认端口：6379（与 Redis 兼容）

3. **启动服务**
   - Memurai 会作为 Windows 服务自动启动
   - 或手动启动：`net start Memurai`

4. **验证连接**
   ```cmd
   memurai-cli ping
   ```
   应该返回 `PONG`

#### 方案 2: 使用 WSL + Redis

1. **安装 WSL**
   ```powershell
   wsl --install
   ```

2. **在 WSL 中安装 Redis**
   ```bash
   sudo apt update
   sudo apt install redis-server
   ```

3. **启动 Redis**
   ```bash
   sudo service redis-server start
   ```

4. **验证连接**
   ```bash
   redis-cli ping
   ```

#### 方案 3: 使用 Docker

1. **安装 Docker Desktop**
   - 下载：https://www.docker.com/products/docker-desktop

2. **启动 Redis 容器**
   ```cmd
   docker run -d -p 6379:6379 --name redis redis:latest
   ```

3. **验证连接**
   ```cmd
   docker exec -it redis redis-cli ping
   ```

### 验证 Redis 连接

使用 Python 测试连接：

```python
import redis

try:
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.ping()
    print("✅ Redis 连接成功")
except Exception as e:
    print(f"❌ Redis 连接失败: {e}")
```

或使用命令行：

```cmd
conda run -n hospital-backend python -c "import redis; r = redis.Redis(); print('✅ Redis OK' if r.ping() else '❌ Redis Failed')"
```

## 重启服务

Redis 启动后，需要重启 Celery worker：

```cmd
# 停止当前的 Celery worker (Ctrl+C)

# 重新启动
conda run -n hospital-backend --cwd backend celery -A app.celery_app worker --loglevel=info --pool=solo
```

## 配置检查

确保 `.env` 文件中的配置正确：

```env
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 临时解决方案：使用同步模式

如果暂时无法配置 Redis，可以使用同步导入模式：

### 前端修改

在 `ExcelImport.vue` 中：

```typescript
formData.append('async_mode', 'false')  // 改为 false
```

这样会直接在 HTTP 请求中完成导入，不使用 Celery。

**注意：** 同步模式适合小数据量（< 1000 条），大数据量仍会超时。

## 推荐配置

对于开发环境，推荐使用 **Memurai**：
- ✅ Windows 原生支持
- ✅ 完全兼容 Redis
- ✅ 作为服务自动启动
- ✅ 免费开发者版本

对于生产环境，推荐使用 **Docker + Redis**：
- ✅ 跨平台
- ✅ 易于部署
- ✅ 资源隔离
- ✅ 易于扩展

## 故障排查

### 1. 检查 Redis 是否运行

**Memurai:**
```cmd
sc query Memurai
```

**WSL:**
```bash
sudo service redis-server status
```

**Docker:**
```cmd
docker ps | findstr redis
```

### 2. 检查端口占用

```cmd
netstat -ano | findstr :6379
```

### 3. 检查防火墙

确保端口 6379 未被防火墙阻止。

### 4. 查看 Celery 日志

启动 Celery 时会显示连接信息：

```
[2024-10-22 10:00:00,000: INFO/MainProcess] Connected to redis://localhost:6379/0
```

如果看到连接错误，说明 Redis 未正确配置。

## 下一步

1. 选择并安装 Redis（推荐 Memurai）
2. 验证 Redis 连接
3. 重启 Celery worker
4. 测试异步导入功能
