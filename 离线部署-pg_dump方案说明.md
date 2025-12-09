# 离线部署 - pg_dump/pg_restore 方案说明

## 方案优势

相比之前的 Alembic 迁移 + JSON 导入方案，新方案使用 PostgreSQL 原生的 `pg_dump` 和 `pg_restore`：

### ✅ 优点

1. **简单可靠**
   - 一条命令完成导出/恢复
   - PostgreSQL 官方工具，久经考验
   - 不依赖应用代码和 Python 环境

2. **完整性**
   - 包含所有表结构、数据、索引、约束、序列
   - 自动处理外键依赖关系
   - 保留所有数据库对象

3. **性能**
   - 比逐表导入快得多
   - 支持并行恢复（使用 `-j` 参数）
   - 自定义格式已压缩

4. **无迁移冲突**
   - 不需要处理 Alembic 迁移文件
   - 不会出现多个 heads 的问题
   - 版本一致性由数据库保证

### ❌ 注意事项

1. **需要 PostgreSQL 客户端工具**
   - 如果本地没有，脚本会自动使用 Docker
   - 需要拉取 `postgres:16` 镜像（约 150MB）

2. **数据库版本兼容性**
   - 建议源和目标数据库版本一致
   - 或目标版本高于源版本

## 使用方法

### 打包（Windows）

```powershell
# 使用 PowerShell 脚本
.\scripts\build-offline-package.ps1

# 或使用 WSL2 + bash
bash scripts/build-offline-package.sh
```

脚本会自动：
1. 检测本地是否有 `pg_dump`
2. 如果没有，使用 Docker 运行 `pg_dump`
3. 导出为 PostgreSQL 自定义格式（`.dump`）

### 部署（Linux）

```bash
# 1. 解压部署包
tar -xzf hospital-value-toolkit-offline-v1.0.0.tar.gz
cd offline-package

# 2. 配置环境
cp config/.env.offline.template .env
vi .env  # 修改数据库连接信息

# 3. 初始化数据库
bash scripts/init-database.sh
```

初始化脚本会自动：
1. 检测是否有 `database.dump` 文件
2. 如果有，使用 `pg_restore` 恢复
3. 如果本地没有 `pg_restore`，使用 Docker
4. 如果没有 dump 文件，回退到 Alembic 迁移

## 工具检测逻辑

### 打包时（build-offline-package）

```
检查本地 pg_dump
  ├─ 找到 → 使用本地工具
  └─ 未找到 → 使用 Docker postgres:16
```

Windows 会检查这些路径：
- `C:\Program Files\PostgreSQL\*\bin\pg_dump.exe`
- `C:\Program Files (x86)\PostgreSQL\*\bin\pg_dump.exe`
- `C:\software\PostgreSQL\*\bin\pg_dump.exe`
- PATH 环境变量

### 部署时（init-database）

```
检查 database.dump 文件
  ├─ 存在
  │   ├─ 检查本地 pg_restore
  │   │   ├─ 找到 → 使用本地工具
  │   │   └─ 未找到 → 使用 Docker postgres:16
  │   └─ 恢复数据库
  └─ 不存在
      └─ 回退到 Alembic 迁移（兼容旧版本）
```

## 导出格式说明

### 自定义格式（-F c）

```bash
pg_dump -F c -f database.dump
```

特点：
- 二进制格式，已压缩
- 支持选择性恢复（可以只恢复部分表）
- 支持并行恢复（`pg_restore -j 4`）
- 文件扩展名：`.dump`

### 其他格式（不推荐）

- **纯文本格式（-F p）**：SQL 脚本，体积大，不支持并行
- **目录格式（-F d）**：多个文件，适合大数据库
- **tar 格式（-F t）**：tar 归档，不支持并行

## 恢复选项说明

```bash
pg_restore \
    -h $DB_HOST \
    -p $DB_PORT \
    -U $DB_USER \
    -d $DB_NAME \
    --verbose \          # 显示详细信息
    --no-owner \         # 不恢复对象所有者
    --no-acl \           # 不恢复访问权限
    database.dump
```

### 为什么使用 --no-owner 和 --no-acl？

- **--no-owner**：避免因用户不存在导致的错误
- **--no-acl**：避免权限设置冲突

这些选项让恢复更加灵活，适合不同的部署环境。

## 常见问题

### Q: 如果本地没有 PostgreSQL 客户端怎么办？

A: 脚本会自动使用 Docker 运行 PostgreSQL 客户端工具。只需要：
- 确保 Docker 正在运行
- 脚本会自动拉取 `postgres:16` 镜像

### Q: 可以跨版本恢复吗？

A: 可以，但有限制：
- ✅ 从低版本恢复到高版本（如 PG 14 → PG 16）
- ⚠️ 从高版本恢复到低版本可能失败
- 建议保持版本一致

### Q: 恢复时出现警告怎么办？

A: 大多数警告可以忽略，常见的包括：
- 角色不存在（使用了 --no-owner）
- 权限设置失败（使用了 --no-acl）
- 扩展已存在

只要最后验证表数量正确即可。

### Q: 如何验证恢复是否成功？

A: 脚本会自动验证：
```bash
# 检查表数量
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public';
```

也可以手动检查：
```bash
# 连接数据库
psql -h localhost -p 15433 -U admin -d hospital_value

# 查看所有表
\dt

# 查看表记录数
SELECT 
    schemaname,
    tablename,
    n_live_tup as row_count
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;
```

### Q: 可以只恢复部分表吗？

A: 可以，使用 `-t` 参数：
```bash
pg_restore -t users -t hospitals database.dump
```

但通常不需要，完整恢复更简单可靠。

## 性能优化

### 并行恢复

如果数据库很大，可以使用并行恢复：
```bash
pg_restore -j 4 database.dump  # 使用 4 个并行任务
```

注意：
- 只有自定义格式（-F c）和目录格式（-F d）支持并行
- 并行数不要超过 CPU 核心数

### 禁用触发器

如果有大量触发器，可以临时禁用：
```bash
pg_restore --disable-triggers database.dump
```

## 回退方案

如果 `pg_restore` 失败，脚本会自动回退到 Alembic 迁移：

1. 使用 Docker 容器内的 Alembic
2. 执行 `alembic upgrade head`
3. 运行 `init_admin.py` 创建管理员

这确保了即使没有 dump 文件，也能正常部署。

## 最佳实践

1. **打包前测试**
   ```bash
   # 测试导出
   bash scripts/build-offline-package.sh
   
   # 检查 dump 文件
   ls -lh offline-package/database/database.dump
   ```

2. **部署前备份**
   ```bash
   # 备份目标数据库
   pg_dump -F c -f backup_$(date +%Y%m%d).dump hospital_value
   ```

3. **分步部署**
   ```bash
   # 先只初始化数据库
   bash scripts/init-database.sh
   
   # 验证成功后再启动服务
   docker-compose up -d
   ```

4. **保留日志**
   ```bash
   # 保存部署日志
   bash scripts/init-database.sh 2>&1 | tee deploy.log
   ```

## 技术细节

### 为什么不用 SQL 脚本？

SQL 脚本（`pg_dump -F p`）的问题：
- 体积大（未压缩）
- 不支持并行恢复
- 恢复时需要处理事务
- 错误处理复杂

自定义格式更适合生产环境。

### 为什么不用 pg_dumpall？

`pg_dumpall` 会导出整个 PostgreSQL 实例（所有数据库），而我们只需要一个数据库。使用 `pg_dump` 更精确。

### Docker 网络模式

使用 `--network host` 让容器直接访问宿主机网络，简化数据库连接。

## 总结

新方案使用 PostgreSQL 原生工具，更简单、更可靠、更快速。脚本会自动处理各种情况，无需手动干预。
