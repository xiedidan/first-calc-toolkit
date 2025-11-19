# SQL数据源配置功能设计总结

## 概述

本次设计在系统配置中添加了SQL数据源配置管理功能，用于建立与外部数据库的连接，并在计算流程中执行SQL代码。

## 修改的文档

### 1. 需求文档.md

**修改位置**: 第3.1章节 - 系统全局设置

**新增内容**:
- **3.1.2. SQL数据源配置 (FR-GLOBAL-02)**
  - 功能概述
  - 核心需求（支持多数据源、多数据库类型、连接测试等）
  - 数据源配置项（12个配置字段）
  - 连接测试功能
  - 安全性要求（密码加密、权限控制）
  - 连接池管理
  - 与计算流程集成
  - 数据源管理界面

### 2. 系统设计文档.md

**修改位置**: 多处

**新增/修改内容**:

#### 2.1 数据库设计（第4章）
- 在系统配置表列表中新增 `data_sources` 表
- 新增 `data_sources` 表的详细字段设计（18个字段）
- 在 `calculation_steps` 表中新增 `data_source_id` 字段

#### 2.2 服务设计（第3章）
- **新增 3.4.5. 数据源管理服务 (Data Source Service)**
  - 功能设计
  - 核心实体定义
  - 连接池管理策略
  - 安全机制（密码加密、权限控制）
  - 接口说明引用

### 3. API设计文档.md

**修改位置**: 多处

**新增/修改内容**:

#### 3.1 新增第9章 - 数据源管理服务 API
包含9个API接口：
1. `GET /data-sources` - 获取数据源列表
2. `POST /data-sources` - 创建新数据源
3. `GET /data-sources/{id}` - 获取数据源详情
4. `PUT /data-sources/{id}` - 更新数据源信息
5. `DELETE /data-sources/{id}` - 删除数据源
6. `POST /data-sources/{id}/test` - 测试数据源连接
7. `PUT /data-sources/{id}/toggle` - 切换数据源启用状态
8. `PUT /data-sources/{id}/set-default` - 设置为默认数据源
9. `GET /data-sources/{id}/pool-status` - 获取连接池状态

#### 3.2 修改计算步骤相关API
- 在创建计算步骤API中新增 `data_source_id` 参数
- 在获取计算步骤列表API响应中新增 `data_source_id` 和 `data_source_name` 字段
- 在获取计算步骤详情API响应中新增 `data_source_id` 和 `data_source_name` 字段
- 在更新计算步骤API中新增 `data_source_id` 参数

#### 3.3 新增数据字典
- 9.1.5. 数据库类型 (db_type)
- 9.1.6. 数据源连接状态 (connection_status)

## 核心功能特性

### 1. 多数据源支持
- 支持配置多个数据源连接
- 支持PostgreSQL、MySQL、SQL Server、Oracle等主流数据库
- 每个数据源独立配置和管理

### 2. 连接池管理
- 为每个启用的数据源维护独立的连接池
- 支持配置连接池参数（最小/最大连接数、超时时间）
- 自动回收空闲连接
- 提供连接池状态监控

### 3. 安全性
- 数据库密码使用AES-256加密存储
- 密码字段在前端显示时脱敏
- 数据源配置需要系统管理员权限
- 连接字符串不在日志中明文记录

### 4. 连接测试
- 保存前可测试连接
- 验证网络连通性、认证信息、访问权限
- 显示详细的错误信息

### 5. 默认数据源
- 支持设置默认数据源
- 计算步骤未指定数据源时使用默认数据源
- 只能有一个数据源标记为默认

### 6. 与计算流程集成
- 计算步骤创建时可选择目标数据源
- SQL类型步骤执行时使用指定的数据源
- 支持在SQL代码中使用占位符

## 数据库表设计

### data_sources 表

| 字段名 | 类型 | 描述 |
|---|---|---|
| id | SERIAL | 主键 |
| name | VARCHAR(100) | 数据源名称（唯一） |
| db_type | VARCHAR(20) | 数据库类型 |
| host | VARCHAR(255) | 主机地址 |
| port | INTEGER | 端口号 |
| database_name | VARCHAR(100) | 数据库名称 |
| username | VARCHAR(100) | 用户名 |
| password | TEXT | 密码（加密存储） |
| schema_name | VARCHAR(100) | Schema名称 |
| connection_params | JSONB | 额外连接参数 |
| is_default | BOOLEAN | 是否默认数据源 |
| is_enabled | BOOLEAN | 是否启用 |
| description | TEXT | 描述 |
| pool_size_min | INTEGER | 连接池最小连接数 |
| pool_size_max | INTEGER | 连接池最大连接数 |
| pool_timeout | INTEGER | 连接超时时间(秒) |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### calculation_steps 表（新增字段）

| 字段名 | 类型 | 描述 |
|---|---|---|
| data_source_id | INT | 数据源ID（外键，可选） |

## 技术实现要点

### 1. 密码加密
```python
from cryptography.fernet import Fernet

# 使用环境变量中的密钥
key = os.getenv('ENCRYPTION_KEY')
cipher = Fernet(key)

# 加密
encrypted_password = cipher.encrypt(password.encode())

# 解密
decrypted_password = cipher.decrypt(encrypted_password).decode()
```

### 2. 连接池配置
```python
from sqlalchemy import create_engine

engine = create_engine(
    connection_string,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True
)
```

### 3. 数据源管理器
```python
class DataSourceManager:
    def __init__(self):
        self.pools = {}  # 存储所有数据源的连接池
    
    def get_pool(self, data_source_id):
        """获取指定数据源的连接池"""
        pass
    
    def create_pool(self, data_source):
        """为数据源创建连接池"""
        pass
    
    def close_pool(self, data_source_id):
        """关闭并清理连接池"""
        pass
    
    def test_connection(self, data_source):
        """测试数据源连接"""
        pass
```

## 使用场景

### 场景1：配置HIS业务数据库
1. 系统管理员登录系统
2. 进入"数据源管理"页面
3. 点击"新建数据源"
4. 填写配置信息（名称、类型、主机、端口、数据库名、用户名、密码等）
5. 点击"测试连接"验证配置
6. 保存并设置为默认数据源

### 场景2：创建计算步骤并指定数据源
1. 进入"计算流程管理"页面
2. 选择一个计算流程，进入步骤管理
3. 点击"新建步骤"
4. 填写步骤信息，代码类型选择"SQL"
5. 在"数据源"下拉框中选择目标数据源
6. 编写SQL代码
7. 点击"测试运行"验证代码
8. 保存步骤

### 场景3：监控连接池状态
1. 进入"数据源管理"页面
2. 点击某个数据源的"连接池状态"按钮
3. 查看活跃连接数、空闲连接数、等待请求数等信息
4. 根据需要调整连接池配置

## 后续开发建议

### 1. 数据库迁移脚本
需要创建Alembic迁移脚本：
- 创建 `data_sources` 表
- 在 `calculation_steps` 表中添加 `data_source_id` 字段

### 2. 后端实现
- 实现数据源管理服务
- 实现密码加密/解密工具
- 实现连接池管理器
- 修改计算引擎，支持从指定数据源执行SQL

### 3. 前端实现
- 实现数据源管理页面
- 在计算步骤编辑页面添加数据源选择
- 实现连接测试功能
- 实现连接池状态监控页面

### 4. 测试
- 单元测试：密码加密/解密、连接池管理
- 集成测试：数据源CRUD、连接测试、SQL执行
- 性能测试：连接池性能、并发连接测试

## 注意事项

1. **安全性**：
   - 加密密钥必须存储在环境变量中，不能写入代码
   - 密码在日志中必须脱敏
   - 数据源配置需要严格的权限控制

2. **性能**：
   - 合理配置连接池大小，避免资源浪费
   - 定期回收空闲连接
   - 监控连接池使用情况

3. **可靠性**：
   - 连接前进行pre-ping测试
   - 处理连接超时和断开的情况
   - 提供详细的错误日志

4. **兼容性**：
   - 支持多种数据库类型
   - 处理不同数据库的连接字符串格式差异
   - 考虑不同数据库的SQL方言差异

## 总结

本次设计完整地添加了SQL数据源配置管理功能，包括：
- 完善的需求定义
- 详细的系统设计
- 完整的API接口设计
- 安全的密码管理机制
- 高效的连接池管理
- 与现有计算流程的无缝集成

该功能将大大提升系统的灵活性，支持从多个数据源提取数据进行计算，满足复杂的业务场景需求。
