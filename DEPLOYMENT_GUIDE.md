# 数据源功能部署指南

## 前置条件

- Python 3.8+
- PostgreSQL 数据库
- Redis（用于Celery）

## 部署步骤

### 1. 生成加密密钥

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

将输出的密钥保存，例如：
```
xYz123ABC456def789GHI012jkl345MNO678pqr901STU234vwx567YZA890bcd=
```

### 2. 配置环境变量

编辑 `backend/.env` 文件，添加加密密钥：

```bash
# 数据源密码加密密钥
ENCRYPTION_KEY=xYz123ABC456def789GHI012jkl345MNO678pqr901STU234vwx567YZA890bcd=
```

⚠️ **重要提示**：
- 密钥一旦设置不应更改
- 生产环境应使用密钥管理服务（AWS KMS、Azure Key Vault等）
- 密钥应妥善保管，不要提交到版本控制系统

### 3. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

新增的依赖包括：
- `cryptography==41.0.7` - 加密库
- `pymysql==1.1.0` - MySQL驱动
- `pyodbc==5.0.1` - SQL Server驱动
- `cx-oracle==8.3.0` - Oracle驱动

### 4. 测试加密功能

```bash
python test_encryption.py
```

预期输出：
```
=== 测试密码加密功能 ===

原始密码: simple_password
加密后: gAAAAABl...
解密后: simple_password
✅ 加密解密成功

所有测试通过！
```

### 5. 执行数据库迁移

```bash
alembic upgrade head
```

预期输出：
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade calc_workflow_001 -> l6m7n8o9p0q1, add data sources table
```

迁移将创建：
- `data_sources` 表（18个字段）
- `calculation_steps.data_source_id` 外键字段

### 6. 验证数据库表

连接到PostgreSQL数据库，检查表是否创建成功：

```sql
-- 检查data_sources表
\d data_sources

-- 检查calculation_steps表的data_source_id字段
\d calculation_steps
```

### 7. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. 验证API

访问API文档：http://localhost:8000/docs

应该能看到新增的"数据源管理"标签，包含9个API接口。

### 9. 测试API功能

```bash
python test_data_source_api.py
```

## 数据库驱动安装

### SQL Server (Windows)

1. 下载并安装 ODBC Driver 17 for SQL Server：
   https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

2. 验证安装：
   ```bash
   odbcinst -q -d
   ```

### Oracle

1. 下载并安装 Oracle Instant Client：
   https://www.oracle.com/database/technologies/instant-client/downloads.html

2. 配置环境变量：
   ```bash
   # Windows
   set PATH=%PATH%;C:\oracle\instantclient_19_8
   
   # Linux
   export LD_LIBRARY_PATH=/opt/oracle/instantclient_19_8:$LD_LIBRARY_PATH
   ```

## 故障排查

### 问题1：加密密钥未设置

**错误信息**：
```
警告: 未设置ENCRYPTION_KEY环境变量，使用临时密钥
```

**解决方案**：
在 `.env` 文件中添加 `ENCRYPTION_KEY`

### 问题2：迁移失败

**错误信息**：
```
KeyError: 'add_calculation_workflow_tables'
```

**解决方案**：
检查迁移文件的 `down_revision` 是否正确

### 问题3：数据库连接失败

**错误信息**：
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**解决方案**：
1. 检查数据库服务是否启动
2. 检查 `.env` 中的 `DATABASE_URL` 是否正确
3. 检查网络连通性

### 问题4：导入错误

**错误信息**：
```
ModuleNotFoundError: No module named 'cryptography'
```

**解决方案**：
```bash
pip install cryptography==41.0.7
```

## 安全检查清单

- [ ] 已设置 `ENCRYPTION_KEY` 环境变量
- [ ] 加密密钥已妥善保管
- [ ] 加密密钥未提交到版本控制
- [ ] 数据库密码已加密存储
- [ ] API响应中密码已脱敏
- [ ] 限制了数据源管理权限
- [ ] 配置了防火墙规则
- [ ] 使用了安全的数据库连接（SSL/TLS）

## 性能优化建议

1. **连接池配置**
   - 根据实际负载调整 `pool_size_min` 和 `pool_size_max`
   - 监控连接池使用情况
   - 避免创建过多数据源

2. **数据库优化**
   - 为常用查询字段添加索引
   - 定期清理无用数据
   - 监控数据库性能

3. **网络优化**
   - 使用专线或VPN连接远程数据库
   - 配置合适的连接超时时间
   - 启用数据库连接压缩

## 监控建议

1. **连接池监控**
   - 定期检查连接池状态
   - 监控活跃连接数和空闲连接数
   - 设置告警阈值

2. **性能监控**
   - 监控API响应时间
   - 监控数据库查询性能
   - 记录慢查询日志

3. **安全监控**
   - 审计数据源配置变更
   - 监控异常连接尝试
   - 定期检查权限配置

## 回滚方案

如果需要回滚数据源功能：

```bash
# 回滚数据库迁移
alembic downgrade -1

# 或回滚到特定版本
alembic downgrade calc_workflow_001
```

⚠️ **注意**：回滚将删除 `data_sources` 表和所有数据，请谨慎操作！

## 备份建议

1. **数据库备份**
   ```bash
   pg_dump -h localhost -U postgres -d hospital_db > backup.sql
   ```

2. **配置备份**
   - 备份 `.env` 文件（不包含敏感信息）
   - 备份加密密钥（单独存储）
   - 备份数据源配置（导出为JSON）

3. **定期备份**
   - 每日自动备份数据库
   - 每周备份配置文件
   - 每月验证备份可用性

## 升级计划

### 短期（1-2周）
- [ ] 完成前端管理界面
- [ ] 与计算流程集成
- [ ] 编写单元测试

### 中期（1-2月）
- [ ] 性能优化
- [ ] 安全加固
- [ ] 完善文档

### 长期（3-6月）
- [ ] 支持更多数据库类型
- [ ] 实现连接池自动调优
- [ ] 集成监控告警系统

## 技术支持

如遇问题，请：
1. 查看日志文件
2. 检查API文档：http://localhost:8000/docs
3. 运行测试脚本：`python test_data_source_api.py`
4. 查看相关文档：
   - [实现总结](DATA_SOURCE_IMPLEMENTATION.md)
   - [快速启动](DATA_SOURCE_QUICKSTART.md)
   - [README](DATA_SOURCE_README.md)

## 附录

### A. 环境变量完整列表

```bash
# 应用配置
APP_NAME=医院科室业务价值评估工具
APP_VERSION=1.0.0
DEBUG=True

# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/hospital_db

# Redis配置
REDIS_URL=redis://localhost:6379/0

# JWT配置
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# 加密配置（新增）
ENCRYPTION_KEY=your-encryption-key

# 日志配置
LOG_LEVEL=INFO
```

### B. 数据库表结构

```sql
CREATE TABLE data_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    db_type VARCHAR(20) NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    database_name VARCHAR(100) NOT NULL,
    username VARCHAR(100) NOT NULL,
    password TEXT NOT NULL,
    schema_name VARCHAR(100),
    connection_params JSON,
    is_default BOOLEAN DEFAULT FALSE,
    is_enabled BOOLEAN DEFAULT TRUE,
    description TEXT,
    pool_size_min INTEGER DEFAULT 2,
    pool_size_max INTEGER DEFAULT 10,
    pool_timeout INTEGER DEFAULT 30,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE calculation_steps 
ADD COLUMN data_source_id INTEGER REFERENCES data_sources(id) ON DELETE SET NULL;
```

### C. API端点完整列表

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/data-sources` | 获取数据源列表 |
| POST | `/api/v1/data-sources` | 创建数据源 |
| GET | `/api/v1/data-sources/{id}` | 获取详情 |
| PUT | `/api/v1/data-sources/{id}` | 更新数据源 |
| DELETE | `/api/v1/data-sources/{id}` | 删除数据源 |
| POST | `/api/v1/data-sources/{id}/test` | 测试连接 |
| PUT | `/api/v1/data-sources/{id}/toggle` | 切换状态 |
| PUT | `/api/v1/data-sources/{id}/set-default` | 设置默认 |
| GET | `/api/v1/data-sources/{id}/pool-status` | 连接池状态 |
