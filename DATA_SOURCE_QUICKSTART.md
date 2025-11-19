# 数据源功能快速启动指南

## 快速开始

### 1. 生成加密密钥

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

将生成的密钥添加到 `.env` 文件：

```bash
ENCRYPTION_KEY=生成的密钥
```

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 执行数据库迁移

```bash
alembic upgrade head
```

### 4. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问API文档

打开浏览器访问：http://localhost:8000/docs

### 6. 测试API

```bash
python test_data_source_api.py
```

## API端点

所有数据源API的前缀为：`/api/v1/data-sources`

### 基本操作

1. **获取数据源列表**
   - `GET /api/v1/data-sources`
   - 参数：page, size, keyword, db_type, is_enabled

2. **创建数据源**
   - `POST /api/v1/data-sources`
   - Body: DataSourceCreate

3. **获取数据源详情**
   - `GET /api/v1/data-sources/{id}`

4. **更新数据源**
   - `PUT /api/v1/data-sources/{id}`
   - Body: DataSourceUpdate

5. **删除数据源**
   - `DELETE /api/v1/data-sources/{id}`

### 高级操作

6. **测试连接**
   - `POST /api/v1/data-sources/{id}/test`

7. **切换启用状态**
   - `PUT /api/v1/data-sources/{id}/toggle`

8. **设置为默认**
   - `PUT /api/v1/data-sources/{id}/set-default`

9. **获取连接池状态**
   - `GET /api/v1/data-sources/{id}/pool-status`

## 创建数据源示例

### PostgreSQL

```json
{
  "name": "HIS业务数据库",
  "db_type": "postgresql",
  "host": "192.168.1.100",
  "port": 5432,
  "database_name": "his_db",
  "username": "his_user",
  "password": "his_password",
  "schema_name": "public",
  "is_default": true,
  "is_enabled": true,
  "description": "医院HIS系统业务数据库",
  "pool_size_min": 2,
  "pool_size_max": 10,
  "pool_timeout": 30
}
```

### MySQL

```json
{
  "name": "MySQL数据源",
  "db_type": "mysql",
  "host": "192.168.1.101",
  "port": 3306,
  "database_name": "test_db",
  "username": "root",
  "password": "mysql_password",
  "is_default": false,
  "is_enabled": true,
  "description": "MySQL测试数据库"
}
```

### SQL Server

```json
{
  "name": "SQL Server数据源",
  "db_type": "sqlserver",
  "host": "192.168.1.102",
  "port": 1433,
  "database_name": "TestDB",
  "username": "sa",
  "password": "sqlserver_password",
  "is_default": false,
  "is_enabled": true,
  "description": "SQL Server测试数据库"
}
```

### Oracle

```json
{
  "name": "Oracle数据源",
  "db_type": "oracle",
  "host": "192.168.1.103",
  "port": 1521,
  "database_name": "ORCL",
  "username": "system",
  "password": "oracle_password",
  "schema_name": "HR",
  "is_default": false,
  "is_enabled": true,
  "description": "Oracle测试数据库"
}
```

## 常见问题

### 1. 加密密钥未设置

**错误**: `警告: 未设置ENCRYPTION_KEY环境变量`

**解决**: 在 `.env` 文件中添加 `ENCRYPTION_KEY`

### 2. 数据库驱动未安装

**错误**: `ModuleNotFoundError: No module named 'pymysql'`

**解决**: `pip install pymysql`

### 3. SQL Server连接失败

**错误**: `ODBC Driver not found`

**解决**: 安装 ODBC Driver 17 for SQL Server

### 4. Oracle连接失败

**错误**: `Oracle Client not found`

**解决**: 安装 Oracle Instant Client

### 5. 连接池创建失败

**错误**: `创建连接池失败`

**解决**: 
- 检查数据库连接信息是否正确
- 检查网络连通性
- 检查数据库服务是否启动

## 下一步

1. 开发前端数据源管理页面
2. 在计算步骤中集成数据源选择
3. 修改计算引擎支持多数据源
4. 编写单元测试和集成测试

## 相关文档

- [数据源功能实现总结](DATA_SOURCE_IMPLEMENTATION.md)
- [需求文档](需求文档.md)
- [API设计文档](API设计文档.md)
- [SQL数据源配置功能设计总结](SQL数据源配置功能设计总结.md)
