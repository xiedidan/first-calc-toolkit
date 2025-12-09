# PostgreSQL 工具配置说明

## 问题场景

在离线部署环境中，服务器可能没有安装 PostgreSQL 客户端工具（`pg_dump` 和 `pg_restore`），但需要这些工具来导出和恢复数据库。

## 解决方案

脚本提供了三种方式来使用 PostgreSQL 工具：

### 方式 1：使用本地安装的工具（推荐）

如果服务器上已安装 PostgreSQL 客户端：

```bash
# 检查是否已安装
which pg_restore

# 如果已安装，脚本会自动使用
bash scripts/init-database.sh
```

### 方式 2：指定 Docker 容器

如果服务器上有运行中的 PostgreSQL 容器，可以使用容器内的工具：

```bash
# 方法 A: 通过环境变量指定
export PG_DOCKER_CONTAINER=postgres_container_name
bash scripts/init-database.sh

# 方法 B: 在 .env 文件中配置
echo "PG_DOCKER_CONTAINER=postgres_container_name" >> .env
bash scripts/init-database.sh
```

**查找容器名称：**
```bash
# 列出所有运行中的容器
docker ps

# 或只列出 PostgreSQL 容器
docker ps --format '{{.Names}}' | grep postgres
```

### 方式 3：使用本地 Docker 镜像

如果本地有 PostgreSQL Docker 镜像（不会尝试 pull）：

```bash
# 检查本地镜像
docker images | grep postgres

# 指定镜像（默认是 postgres:16）
export PG_DOCKER_IMAGE=postgres:16
bash scripts/init-database.sh
```

### 方式 4：自动检测（默认）

如果不指定任何配置，脚本会自动：

1. 检查本地是否有 `pg_restore`
2. 如果没有，查找运行中的 PostgreSQL 容器
3. 如果找到，使用该容器
4. 如果没找到容器，检查是否有 `postgres:16` 镜像
5. 如果都没有，给出手动操作指南

## 配置示例

### 示例 1：使用现有的 PostgreSQL 容器

假设你的 PostgreSQL 运行在名为 `my_postgres` 的容器中：

```bash
# .env 文件
DATABASE_URL=postgresql://admin:password@localhost:5432/hospital_value
PG_DOCKER_CONTAINER=my_postgres
```

### 示例 2：使用不同版本的 PostgreSQL 镜像

如果你有 `postgres:15` 镜像：

```bash
# .env 文件
PG_DOCKER_IMAGE=postgres:15
```

### 示例 3：完全离线环境

如果完全离线且没有 Docker：

```bash
# 1. 在有网络的机器上安装 PostgreSQL 客户端
# Ubuntu/Debian
apt-get install postgresql-client

# CentOS/RHEL
yum install postgresql

# 2. 或者提前准备好 PostgreSQL Docker 镜像
docker pull postgres:16
docker save postgres:16 -o postgres-16.tar

# 3. 在离线服务器上加载镜像
docker load -i postgres-16.tar
```

## 工作原理

### 使用容器中的工具

当使用 Docker 容器时，脚本会：

1. 将 `database.dump` 文件复制到容器内
2. 在容器中执行 `pg_restore` 命令
3. 恢复完成后删除临时文件

```bash
# 实际执行的命令
docker cp database/database.dump $PG_CONTAINER:/tmp/database.dump
docker exec -e PGPASSWORD=$DB_PASSWORD $PG_CONTAINER \
    pg_restore -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
    --no-owner --no-acl /tmp/database.dump
docker exec $PG_CONTAINER rm -f /tmp/database.dump
```

### 使用镜像运行临时容器

当使用 Docker 镜像时，脚本会：

1. 启动一个临时容器
2. 挂载 `database` 目录
3. 执行 `pg_restore` 命令
4. 容器自动删除（`--rm`）

```bash
# 实际执行的命令
docker run --rm \
    --network host \
    -v "$(pwd)/database:/backup" \
    -e PGPASSWORD=$DB_PASSWORD \
    postgres:16 \
    pg_restore -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
    --no-owner --no-acl /backup/database.dump
```

## 常见问题

### Q: 如何知道应该使用哪个容器？

A: 运行以下命令查看：
```bash
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
```

找到运行 PostgreSQL 的容器名称。

### Q: 容器和镜像有什么区别？

A: 
- **容器**：正在运行的 PostgreSQL 实例，可以直接使用其中的工具
- **镜像**：PostgreSQL 的模板，需要启动临时容器来使用工具

使用容器更快，因为不需要启动新容器。

### Q: 为什么不自动 pull 镜像？

A: 离线部署环境通常没有网络连接，自动 pull 会失败。脚本只使用本地已有的资源。

### Q: 如果都没有怎么办？

A: 脚本会给出手动恢复的命令：
```bash
PGPASSWORD=your_password pg_restore \
    -h localhost -p 5432 -U admin -d hospital_value \
    --no-owner --no-acl database/database.dump
```

你可以：
1. 安装 PostgreSQL 客户端工具
2. 或在另一台有工具的机器上执行恢复
3. 或准备好 PostgreSQL Docker 镜像

### Q: 可以使用其他版本的 PostgreSQL 吗？

A: 可以，只要版本兼容：
- ✅ 使用相同或更高版本恢复（如 PG 14 → PG 16）
- ⚠️ 使用更低版本可能失败（如 PG 16 → PG 14）

### Q: 容器需要访问数据库吗？

A: 是的，容器需要能够连接到目标数据库。确保：
- 使用 `--network host` 让容器访问宿主机网络
- 或数据库允许容器网络访问

## 调试技巧

### 测试容器连接

```bash
# 测试容器是否能连接数据库
docker exec $PG_CONTAINER psql -h localhost -p 5432 -U admin -d hospital_value -c '\l'
```

### 手动恢复

如果脚本失败，可以手动执行：

```bash
# 1. 复制文件到容器
docker cp database/database.dump my_postgres:/tmp/

# 2. 进入容器
docker exec -it my_postgres bash

# 3. 在容器内执行恢复
export PGPASSWORD=your_password
pg_restore -h localhost -p 5432 -U admin -d hospital_value \
    --no-owner --no-acl /tmp/database.dump

# 4. 退出并清理
exit
docker exec my_postgres rm /tmp/database.dump
```

### 查看详细日志

```bash
# 添加 -v 参数查看详细输出
bash -x scripts/init-database.sh
```

## 最佳实践

1. **提前准备**：在打包前确认目标环境有以下之一：
   - PostgreSQL 客户端工具
   - PostgreSQL Docker 容器
   - PostgreSQL Docker 镜像

2. **测试环境**：在测试环境先验证配置是否正确

3. **文档记录**：记录目标环境的容器名称和配置

4. **备份验证**：恢复后验证数据完整性

## 总结

脚本提供了灵活的配置方式，适应不同的部署环境：

| 环境 | 推荐方式 | 配置 |
|------|---------|------|
| 有 PostgreSQL 客户端 | 使用本地工具 | 无需配置 |
| 有运行中的 PG 容器 | 指定容器 | `PG_DOCKER_CONTAINER=容器名` |
| 有 PG 镜像 | 使用镜像 | `PG_DOCKER_IMAGE=镜像名` |
| 完全离线 | 提前准备 | 安装工具或准备镜像 |

无论哪种方式，脚本都不会尝试从网络下载资源，确保离线部署的可靠性。
