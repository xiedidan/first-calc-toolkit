# 医疗机构管理功能 - 数据迁移指南

## 概述

本指南说明如何将现有系统升级到支持多医疗机构管理的新架构。迁移过程将：

1. 创建 `hospitals` 表存储医疗机构信息
2. 在 `users` 表添加 `hospital_id` 字段（可为空，支持超级用户）
3. 在业务表（`departments`, `model_versions` 等）添加 `hospital_id` 字段
4. 创建默认医疗机构"宁波市眼科医院"（编码：nbeye）
5. 将所有现有数据关联到默认医疗机构

## 前置条件

- 已安装 Python 3.12+
- 已安装项目依赖（`pip install -r requirements.txt`）
- 数据库连接配置正确（`.env` 文件）
- 有数据库的完整备份

## 迁移步骤

### 1. 备份数据库

**重要：在执行迁移前，务必备份数据库！**

```bash
# PostgreSQL 备份命令示例
pg_dump -h localhost -U your_user -d hospital_value > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. 检查当前迁移状态

```bash
cd backend
alembic current
```

确认当前迁移版本为 `l6m7n8o9p0q1` (add data sources table)。

### 3. 执行迁移

#### 方式一：使用自动化脚本（推荐）

```bash
cd backend
python run_hospital_migration.py
```

此脚本将自动执行迁移并验证结果。

#### 方式二：手动执行

```bash
cd backend

# 执行迁移
alembic upgrade head

# 验证迁移
python verify_hospital_migration.py
```

### 4. 验证迁移结果

迁移完成后，验证脚本会检查：

- ✓ `hospitals` 表已创建
- ✓ 默认医疗机构"宁波市眼科医院"已插入
- ✓ `users` 表的 `hospital_id` 字段已添加
- ✓ `departments` 表的 `hospital_id` 字段已添加并关联到默认机构
- ✓ `model_versions` 表的 `hospital_id` 字段已添加并关联到默认机构
- ✓ 所有外键约束和索引已创建

### 5. 测试功能

迁移完成后，测试以下功能：

1. 用户登录功能正常
2. 可以查看和管理科室数据
3. 可以查看和管理模型版本
4. 计算任务功能正常
5. 结果查询功能正常

## 迁移影响

### 数据库变更

#### 新增表

- `hospitals` - 医疗机构表

#### 修改表

- `users` - 添加 `hospital_id` 字段（可为空）
- `departments` - 添加 `hospital_id` 字段（非空）
- `model_versions` - 添加 `hospital_id` 字段（非空）

#### 唯一约束变更

- `departments.his_code` - 从全局唯一改为 `(hospital_id, his_code)` 组合唯一
- `model_versions.version` - 从全局唯一改为 `(hospital_id, version)` 组合唯一

### 应用程序变更

- 所有用户默认为超级用户（`hospital_id` 为 NULL）
- 所有现有数据关联到默认医疗机构"宁波市眼科医院"
- 后续需要更新应用代码以支持医疗机构管理功能

## 回滚方案

如果迁移失败或需要回滚：

### 方式一：使用 Alembic 回滚

```bash
cd backend
alembic downgrade l6m7n8o9p0q1
```

### 方式二：从备份恢复

```bash
# PostgreSQL 恢复命令示例
psql -h localhost -U your_user -d hospital_value < backup_YYYYMMDD_HHMMSS.sql
```

## 常见问题

### Q1: 迁移失败，提示外键约束错误

**A:** 检查是否有孤立数据（引用不存在的记录）。清理孤立数据后重试。

### Q2: 验证脚本报告有数据的 hospital_id 为空

**A:** 迁移脚本可能未正确执行。检查迁移日志，手动执行更新语句：

```sql
UPDATE departments
SET hospital_id = (SELECT id FROM hospitals WHERE code = 'nbeye')
WHERE hospital_id IS NULL;

UPDATE model_versions
SET hospital_id = (SELECT id FROM hospitals WHERE code = 'nbeye')
WHERE hospital_id IS NULL;
```

### Q3: 如何添加新的医疗机构？

**A:** 迁移完成后，可以通过以下方式添加：

```sql
INSERT INTO hospitals (code, name, is_active, created_at, updated_at)
VALUES ('new_code', '新医疗机构名称', true, now(), now());
```

或者等待医疗机构管理API开发完成后，通过界面添加。

## 下一步

迁移完成后，继续开发：

1. 医疗机构管理API（CRUD、激活等）
2. 前端医疗机构管理界面
3. 数据隔离中间件
4. 菜单权限控制

## 技术支持

如遇到问题，请查看：

- 迁移日志：`alembic.log`
- 验证脚本输出
- 数据库错误日志

或联系开发团队获取支持。
