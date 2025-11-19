# 数据源配置功能

## 功能概述

数据源配置功能允许系统管理员配置和管理多个外部数据库连接，用于在计算流程中执行SQL查询。

## 核心功能

✅ **多数据源支持** - 支持PostgreSQL、MySQL、SQL Server、Oracle等主流数据库  
✅ **安全加密** - 数据库密码使用AES-256加密存储  
✅ **连接测试** - 保存前可测试连接是否正常  
✅ **连接池管理** - 自动管理数据库连接池，提高性能  
✅ **默认数据源** - 支持设置默认数据源  
✅ **状态管理** - 支持启用/禁用数据源  
✅ **引用检查** - 删除前检查是否被计算步骤引用  

## 快速开始

### 1. 配置环境

```bash
# 生成加密密钥
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 添加到 .env 文件
echo "ENCRYPTION_KEY=生成的密钥" >> backend/.env
```

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 执行迁移

```bash
alembic upgrade head
```

### 4. 启动服务

```bash
uvicorn app.main:app --reload
```

### 5. 访问API文档

http://localhost:8000/docs

## 使用流程

### 1. 创建数据源

通过API或前端界面创建数据源配置：

```json
{
  "name": "HIS业务数据库",
  "db_type": "postgresql",
  "host": "192.168.1.100",
  "port": 5432,
  "database_name": "his_db",
  "username": "his_user",
  "password": "his_password",
  "is_default": true,
  "is_enabled": true
}
```

### 2. 测试连接

创建后测试连接是否正常：

```bash
POST /api/v1/data-sources/{id}/test
```

### 3. 在计算步骤中使用

创建计算步骤时选择数据源：

```json
{
  "workflow_id": 1,
  "name": "计算门诊工作量",
  "code_type": "sql",
  "code_content": "SELECT ...",
  "data_source_id": 1
}
```

## API接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/data-sources` | GET | 获取数据源列表 |
| `/data-sources` | POST | 创建数据源 |
| `/data-sources/{id}` | GET | 获取详情 |
| `/data-sources/{id}` | PUT | 更新数据源 |
| `/data-sources/{id}` | DELETE | 删除数据源 |
| `/data-sources/{id}/test` | POST | 测试连接 |
| `/data-sources/{id}/toggle` | PUT | 切换状态 |
| `/data-sources/{id}/set-default` | PUT | 设置默认 |
| `/data-sources/{id}/pool-status` | GET | 连接池状态 |

## 支持的数据库

| 数据库 | 类型值 | 默认端口 | 驱动 |
|--------|--------|----------|------|
| PostgreSQL | `postgresql` | 5432 | psycopg2 |
| MySQL | `mysql` | 3306 | pymysql |
| SQL Server | `sqlserver` | 1433 | pyodbc |
| Oracle | `oracle` | 1521 | cx_oracle |

## 安全性

- 🔒 密码使用AES-256加密存储
- 🔒 密码在API响应中自动脱敏（显示为***）
- 🔒 加密密钥从环境变量读取
- 🔒 连接字符串不在日志中明文记录
- 🔒 需要系统管理员权限才能管理数据源

## 连接池配置

每个数据源可以配置独立的连接池参数：

- **pool_size_min**: 最小连接数（默认2）
- **pool_size_max**: 最大连接数（默认10）
- **pool_timeout**: 连接超时时间（默认30秒）

系统会自动：
- 回收空闲连接（1小时）
- 连接前进行健康检查
- 监控连接池使用情况

## 注意事项

### 1. 加密密钥管理

⚠️ **重要**: 加密密钥一旦设置不应更改，否则已加密的密码无法解密

建议：
- 生产环境使用密钥管理服务（AWS KMS、Azure Key Vault）
- 定期备份加密密钥
- 限制密钥访问权限

### 2. 数据库驱动

确保服务器上已安装相应的数据库客户端：

- **SQL Server**: ODBC Driver 17 for SQL Server
- **Oracle**: Oracle Instant Client

### 3. 网络安全

- 使用防火墙限制数据库访问
- 使用VPN或专线连接远程数据库
- 定期审计数据源配置

### 4. 性能优化

- 根据实际负载调整连接池大小
- 监控连接池使用情况
- 避免创建过多数据源

## 故障排查

### 连接失败

1. 检查网络连通性：`ping 数据库主机`
2. 检查端口是否开放：`telnet 主机 端口`
3. 检查用户名密码是否正确
4. 检查数据库服务是否启动

### 加密错误

1. 检查 `ENCRYPTION_KEY` 是否设置
2. 检查密钥格式是否正确
3. 不要更改已设置的密钥

### 驱动错误

1. 检查是否安装了相应的数据库驱动
2. 检查驱动版本是否兼容
3. 重新安装驱动：`pip install --upgrade 驱动名`

## 开发计划

### 已完成 ✅
- [x] 数据库模型设计
- [x] API接口开发
- [x] 密码加密功能
- [x] 连接池管理
- [x] 连接测试功能
- [x] 多数据库支持

### 进行中 🚧
- [ ] 前端管理界面
- [ ] 与计算流程集成

### 待开发 📋
- [ ] 单元测试
- [ ] 集成测试
- [ ] 性能测试
- [ ] 用户文档

## 相关文档

- [实现总结](DATA_SOURCE_IMPLEMENTATION.md) - 详细的实现说明
- [快速启动](DATA_SOURCE_QUICKSTART.md) - 快速开始指南
- [需求文档](需求文档.md) - 功能需求说明
- [API设计](API设计文档.md) - API接口设计
- [设计总结](SQL数据源配置功能设计总结.md) - 设计文档

## 技术支持

如有问题，请查看：
1. API文档：http://localhost:8000/docs
2. 测试脚本：`backend/test_data_source_api.py`
3. 日志文件：检查应用日志

## 许可证

本项目遵循项目主许可证。
