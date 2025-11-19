# 离线部署问题修复说明

## 修复的问题

### 问题1: 前端循环依赖错误
**现象**: 前端部署后浏览器控制台报错
```
Uncaught ReferenceError: Cannot access 'Hl' before initialization
```

**原因**: Element Plus 在 Vite 构建时的循环依赖问题，手动分包配置不当

**修复**: 
- 修改 `frontend/vite.config.ts`
- 使用动态分包函数代替静态配置，避免循环依赖

### 问题2: 缺少 pydantic[email] 库
**现象**: 后端启动时报错，提示缺少email验证相关的依赖

**原因**: requirements.txt中只安装了基础的pydantic包，没有包含email扩展

**修复**: 
- 修改 `backend/requirements.txt`
- 增加 `pydantic[email]==2.5.0`（保留原有的 `pydantic==2.5.0`）

### 问题3: /bin/sh: 0: cannot open uvicorn: No such file
**现象**: 容器启动时报错，找不到uvicorn命令

**原因**: 
1. Dockerfile中使用了 `--only-binary=:all:` 参数，可能导致某些包安装不完整
2. 直接使用 `uvicorn` 命令，在某些环境下可能找不到可执行文件路径

**修复**:
1. **Dockerfile改进**:
   - 移除 `--only-binary=:all:` 参数，使用标准安装方式
   - 添加curl工具（用于健康检查）
   - 使用 `python -m uvicorn` 方式启动，确保使用Python模块方式运行

2. **docker-compose.offline.yml改进**:
   - 将启动命令从 `uvicorn app.main:app ...` 改为 `python -m uvicorn app.main:app ...`

## 修改的文件

### 1. frontend/vite.config.ts
```typescript
build: {
  rollupOptions: {
    output: {
      manualChunks(id) {
        // 动态分包，避免循环依赖
        if (id.includes('node_modules')) {
          if (id.includes('element-plus')) {
            return 'element-plus'
          }
          if (id.includes('vue') || id.includes('pinia') || id.includes('@vue')) {
            return 'vue-vendor'
          }
          return 'vendor'
        }
      }
    }
  }
}
```

### 2. backend/requirements.txt
```diff
  pydantic==2.5.0
+ pydantic[email]==2.5.0
  pydantic-settings==2.1.0
```

### 3. backend/Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p /app/logs

# 暴露端口
EXPOSE 8000

# 启动命令（使用python -m方式确保uvicorn可执行）
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4. docker-compose.offline.yml
```yaml
backend:
  # ... 其他配置 ...
  command: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. backend/alembic/env.py
```python
import os
from logging.config import fileConfig

# ... 其他导入 ...

# this is the Alembic Config object
config = context.config

# Override sqlalchemy.url with environment variable if available
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# ... 其余代码 ...
```

**说明**: 让 Alembic 从环境变量读取数据库连接，而不是使用 alembic.ini 中的硬编码值。

### 6. scripts/init-database.sh
在导入数据前先执行数据库迁移创建表结构：
```bash
# 先执行数据库迁移创建表结构
echo ""
echo ">>> 执行数据库迁移（创建表结构）..."
docker exec hospital_backend_offline alembic upgrade head
```

### 7. backend/alembic/versions/20251106_add_charge_item_id_to_mappings.py (新增)
添加 `charge_item_id` 字段到 `dimension_item_mappings` 表的迁移文件。

### 8. backend/import_database.py
增加了按依赖顺序导入数据的逻辑，避免外键约束错误。
导入完成后自动重置所有表的序列。

### 9. backend/reset_sequences.py (新增)
独立的序列重置脚本，用于修复已部署的数据库。

### 10. scripts/fix-sequences.sh (新增)
便捷的序列修复脚本，可以快速修复主键冲突问题。

## 重新构建部署包

修复后需要重新构建Docker镜像和部署包：

### Windows上重新构建

```powershell
# 1. 清理旧镜像（可选）
docker rmi hospital-backend:latest hospital-frontend:latest

# 2. 重新构建
.\scripts\build-offline-package.ps1
```

### 或手动构建

```powershell
# 构建前端镜像（修复了循环依赖问题）
cd frontend
docker build -t hospital-frontend:latest .

# 构建后端镜像（修复了依赖和Alembic配置）
cd ../backend
docker build -t hospital-backend:latest .

# 导出镜像
cd ..
docker save hospital-backend:latest | gzip > hospital-backend.tar.gz
docker save hospital-frontend:latest | gzip > hospital-frontend.tar.gz
docker pull redis:7-alpine
docker save redis:7-alpine | gzip > redis.tar.gz
```

**注意**: 前端和后端都需要重新构建！

## 验证修复

### 1. 本地测试
```powershell
# 使用离线配置启动
docker-compose -f docker-compose.offline.yml up -d

# 查看后端日志
docker logs hospital_backend_offline

# 应该看到类似输出：
# INFO:     Started server process [1]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. 检查依赖
```powershell
# 进入容器检查
docker exec -it hospital_backend_offline bash

# 验证pydantic[email]已安装
python -c "from pydantic import EmailStr; print('OK')"

# 验证uvicorn可用
python -m uvicorn --version

# 退出容器
exit
```

### 3. 测试API
```powershell
# 测试健康检查
curl http://localhost:8000/health

# 测试API文档
# 浏览器访问: http://localhost:8000/docs
```

## 部署到生产环境

修复验证通过后：

1. **传输新的部署包**到目标服务器

2. **停止旧服务**（如果正在运行）:
   ```bash
   docker-compose -f config/docker-compose.offline.yml down
   ```

3. **加载新镜像**:
   ```bash
   docker load < images/hospital-backend.tar.gz
   docker load < images/hospital-frontend.tar.gz
   ```

4. **配置环境变量**（如果还没配置）:
   ```bash
   cp config/.env.offline.template .env
   vi .env
   # 修改 DATABASE_URL 等配置
   ```

5. **启动服务**:
   ```bash
   docker-compose -f config/docker-compose.offline.yml up -d
   ```

6. **初始化数据库**:
   ```bash
   bash scripts/init-database.sh
   ```
   这个脚本会：
   - 检查数据库连接
   - 执行 Alembic 迁移创建表结构
   - 导入数据（如果有数据文件）

7. **验证服务**:
   ```bash
   docker-compose -f config/docker-compose.offline.yml ps
   docker logs hospital_backend_offline
   ```

## 常见问题

### 问题6: 数据库字段缺失错误

**现象**: 
```
column dimension_item_mappings.charge_item_id does not exist
```

**原因**: 数据库迁移不完整，缺少 `charge_item_id` 字段

**解决方案**:
```bash
# 运行数据库迁移
docker exec hospital_backend_offline alembic upgrade head
```

这会应用最新的迁移，添加缺失的字段。

**说明**: 
- 新增了迁移文件 `20251106_add_charge_item_id_to_mappings.py`
- 该迁移会自动关联现有的维度映射数据到收费项目

### 问题7: 导入数据后创建记录时主键冲突

**现象**: 
```
duplicate key value violates unique constraint "xxx_pkey"
DETAIL: Key (id)=(3) already exists.
```

**原因**: 导入数据后，PostgreSQL 的自增序列没有更新，仍然从初始值开始

**解决方案**:
```bash
# 运行序列修复脚本
bash scripts/fix-sequences.sh

# 或手动执行
docker exec hospital_backend_offline python reset_sequences.py
```

这个脚本会自动检测所有表的最大 ID 值，并将序列重置到正确的位置。

**预防措施**: 
- 新版本的 `import_database.py` 已经在导入完成后自动重置序列
- 如果使用旧版本导入的数据，需要手动运行修复脚本

### 问题8: 数据导入时外键约束错误

**现象**: 
```
insert or update on table "xxx" violates foreign key constraint
```

**原因**: 数据导入顺序不正确，依赖表的数据在被依赖表之前导入

**修复**: 
- 修改 `backend/import_database.py`
- 定义正确的表导入顺序（按外键依赖关系）
- 实现智能跳过已存在记录的逻辑

### 问题9: Alembic 连接到 localhost:5432 而不是配置的数据库

**现象**: 
```
connection to server at "localhost" (127.0.0.1), port 5432 failed
```

**原因**: 容器启动时没有加载环境变量，或者容器启动后修改了 .env 文件

**解决方案**:
```bash
# 重启后端容器以加载新的环境变量
docker-compose -f config/docker-compose.offline.yml restart backend

# 或者完全重启所有服务
docker-compose -f config/docker-compose.offline.yml down
docker-compose -f config/docker-compose.offline.yml up -d
```

## 注意事项

1. **Python模块方式启动的优势**:
   - 不依赖PATH环境变量
   - 确保使用正确的Python环境
   - 更可靠的跨平台兼容性

2. **curl工具的作用**:
   - 用于Docker健康检查
   - 便于容器内调试

3. **依赖安装方式**:
   - 移除了 `--only-binary` 限制，允许从源码编译
   - 确保所有依赖完整安装
   - 虽然构建时间稍长，但更稳定

## 相关文档

- [离线部署指南](OFFLINE_DEPLOYMENT_GUIDE.md)
- [离线部署方案](离线部署方案.md)
- [部署文档](部署文档.md)
