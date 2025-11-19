# 异步导入功能快速启动指南

## 前置条件

异步导入功能需要以下服务正常运行：
1. ✅ PostgreSQL 数据库
2. ✅ FastAPI 后端服务
3. ⚠️ **Redis 服务**（必需）
4. ⚠️ **Celery Worker**（必需）

## 快速启动步骤

### 1. 启动 Redis

#### Windows 推荐方案：使用 Memurai

1. **下载并安装 Memurai**
   - 访问：https://www.memurai.com/get-memurai
   - 下载免费开发者版本
   - 运行安装程序（默认端口 6379）

2. **验证 Redis 连接**
   ```cmd
   conda run -n hospital-backend python -c "import redis; r = redis.Redis(); print('✅ Redis 连接成功' if r.ping() else '❌ Redis 连接失败')"
   ```

#### 其他方案

- **Docker**: `docker run -d -p 6379:6379 --name redis redis:latest`
- **WSL**: `sudo service redis-server start`

详细安装指南请参考 `REDIS_SETUP.md`

### 2. 启动 Celery Worker

打开新的命令行窗口：

```cmd
conda run -n hospital-backend --cwd backend celery -A app.celery_app worker --loglevel=info --pool=solo
```

**成功标志**：看到以下输出
```
[2024-10-22 10:00:00,000: INFO/MainProcess] Connected to redis://localhost:6379/0
[tasks]
  . import_charge_items
[2024-10-22 10:00:00,000: INFO/MainProcess] celery@hostname ready.
```

**重要**：必须看到 `[tasks] . import_charge_items` 这一行，表示任务已成功注册。

如果看到 "Received unregistered task" 错误，请参考 `CELERY_TASK_FIX.md` 进行排查。

### 3. 启动后端服务

如果还没启动，打开另一个命令行窗口：

```cmd
conda run -n hospital-backend --cwd backend uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 启动前端服务

如果还没启动，打开另一个命令行窗口：

```cmd
cd frontend
npm run dev
```

## 测试异步导入

### 1. 准备测试数据

创建一个包含大量数据的 Excel 文件（.xlsx 格式）：
- 至少 1000 条数据以测试异步功能
- 包含列：项目编码、项目名称、项目分类、单价

或使用系统提供的模板：
1. 访问收费项目管理页面
2. 点击"批量导入"
3. 点击"下载导入模板"
4. 复制示例数据多次，创建大量测试数据

### 2. 执行导入

1. 访问 http://localhost:5173
2. 登录系统
3. 进入"收费项目管理"页面
4. 点击"批量导入"按钮
5. 上传准备好的 Excel 文件
6. 配置字段映射（系统会自动建议）
7. 预览数据
8. 点击"开始导入"

### 3. 观察进度

导入开始后，你会看到：
- 🔄 旋转的加载图标
- 📊 实时进度条
- 📝 状态文本："正在导入数据... (5000/10000)"

### 4. 查看结果

导入完成后，系统会显示：
- ✅ 成功导入数量
- ❌ 失败数量（如果有）
- 📋 失败记录详情（行号、数据、原因）

## 故障排查

### 问题 1: Redis 连接失败

**错误信息**：
```
Celery backend 配置错误: 'DisabledBackend' object has no attribute '_get_task_meta_for'
```

**解决方案**：
1. 检查 Redis 是否运行：
   ```cmd
   # Memurai
   sc query Memurai
   
   # Docker
   docker ps | findstr redis
   ```

2. 测试 Redis 连接：
   ```cmd
   conda run -n hospital-backend python -c "import redis; redis.Redis().ping()"
   ```

3. 检查 `.env` 配置：
   ```env
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   ```

### 问题 2: Celery Worker 未启动

**症状**：任务一直显示"等待中..."

**解决方案**：
1. 检查 Celery Worker 是否运行
2. 查看 Celery 日志是否有错误
3. 重启 Celery Worker

### 问题 3: 文件格式错误

**错误信息**：
```
仅支持 .xlsx 格式文件，请使用 Excel 2007 及以上版本保存
```

**解决方案**：
1. 在 Excel 中打开文件
2. 另存为 → 选择"Excel 工作簿 (*.xlsx)"
3. 重新上传

### 问题 4: 导入超时（同步模式）

**症状**：前端显示超时错误，但数据已导入

**解决方案**：
- 这是正常现象，说明异步模式未启用
- 确保 Redis 和 Celery Worker 正常运行
- 前端会自动使用异步模式

## 性能参考

基于测试环境（本地开发机器）：

| 数据量 | 导入时间 | 建议模式 |
|--------|----------|----------|
| < 100 条 | < 1 秒 | 同步 |
| 100-1000 条 | 1-10 秒 | 同步/异步 |
| 1000-10000 条 | 10-100 秒 | 异步 |
| > 10000 条 | > 100 秒 | 异步 |

## 开发模式 vs 生产模式

### 开发模式（当前）
- Celery pool: `solo`（单进程，Windows 兼容）
- 适合开发和测试
- 不支持并发任务

### 生产模式（推荐）
- Celery pool: `prefork`（多进程）
- 支持并发任务
- 更高性能
- 需要 Linux 环境或 Docker

生产部署配置请参考 `docker-compose.prod.yml`

## 下一步

- ✅ 测试小数据量导入（< 100 条）
- ✅ 测试大数据量导入（> 1000 条）
- ✅ 测试异常情况（重复数据、格式错误等）
- ✅ 查看 Celery 日志了解任务执行情况
- ✅ 监控 Redis 内存使用情况

## 相关文档

- `REDIS_SETUP.md` - Redis 详细安装指南
- `ASYNC_IMPORT_COMPLETED.md` - 异步导入功能说明
- `API设计文档.md` - API 接口详细说明
- `系统设计文档.md` - 系统架构设计
