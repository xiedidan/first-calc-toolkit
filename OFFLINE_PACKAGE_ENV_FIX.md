# 离线打包脚本优化

## 1. .env 读取修复

### 问题描述

离线打包脚本在读取 `backend/.env` 文件时，会错误地读取到被注释掉的配置行，导致连接到错误的数据库。

## 2. 选择性数据导出优化

### 问题描述

完整导出数据库会导致打包文件过大，因为包含了大量的业务数据表（如 `charge_details`、`calculation_results` 等）。

### 问题示例

```properties
# backend/.env 文件内容
# DATABASE_URL=postgresql://admin:admin123@localhost:5432/hospital_value
DATABASE_URL=postgresql://root:root@47.108.227.254:50016/hospital_value
```

**修复前**：脚本会读取到第一行（注释行），连接到 `localhost:5432`
**修复后**：脚本只读取未注释的行，连接到 `47.108.227.254:50016`

## 修复内容

### 1. PowerShell 脚本 (`scripts/build-offline-package.ps1`)

**修复前：**
```powershell
$envContent = Get-Content "backend\.env" -Raw
if ($envContent -match 'DATABASE_URL=postgresql://...') {
```

**修复后：**
```powershell
$envContent = Get-Content "backend\.env" | Where-Object { $_ -notmatch '^\s*#' -and $_ -match 'DATABASE_URL=' } | Select-Object -First 1
if ($envContent -match 'DATABASE_URL=postgresql://...') {
```

### 2. Bash 脚本 (`scripts/build-offline-package.sh`)

**修复前：**
```bash
source backend/.env
```

**修复后：**
```bash
DATABASE_URL=$(grep -v '^\s*#' backend/.env | grep 'DATABASE_URL=' | tail -1 | cut -d'=' -f2-)
```

## 验证方法

运行测试脚本验证修复：

```powershell
.\test-env-parsing.ps1
```

预期输出：
```
✓ 匹配成功!
  DB_USER: root
  DB_PASSWORD: root
  DB_HOST: 47.108.227.254
  DB_PORT: 50016
  DB_NAME: hospital_value
```

## 影响范围

- ✅ 离线打包时的数据库导出
- ✅ 确保导出的是最新的生产数据库
- ✅ 避免导出本地开发数据库

## 注意事项

1. 打包前确认 `backend/.env` 中的 `DATABASE_URL` 配置正确
2. 确保未注释的 `DATABASE_URL` 是实际要使用的配置
3. 如果有多个未注释的 `DATABASE_URL`，脚本会使用最后一个

### 优化方案

**排除列表策略**：
- 只指定需要排除数据的表（大数据表）
- 其他所有表自动导出数据
- 更灵活，新增表无需修改脚本

### 导出的表分类

**排除数据的表（7个）**：
```
charge_details              - 收费明细表
calculation_results         - 计算结果表
calculation_tasks          - 计算任务表
orientation_adjustment_details - 导向调整明细表
orientation_values         - 导向实际值表
cost_values               - 成本值表
department_revenues       - 科室收入表
```

**自动导出数据的表**：
- 所有其他表（包括新增的表）
- 无需手动维护列表

### 优化效果

- ✅ 大幅减小打包文件大小（从数百MB降至几MB）
- ✅ 保留完整的表结构和约束
- ✅ 保留所有配置和基础数据
- ✅ 部署后可按需导入业务数据

### 使用方法

打包脚本会自动使用选择性导出：

```powershell
# PowerShell
.\scripts\build-offline-package.ps1

# Bash
bash scripts/build-offline-package.sh
```

导出过程会显示：
```
导出策略:
  - 大数据表（仅结构）: 7 个
  - 其他所有表（含数据）: 自动包含

排除数据的表:
  - charge_details
  - calculation_results
  - calculation_tasks
  - orientation_adjustment_details
  - orientation_values
  - cost_values
  - department_revenues
```

### 部署后数据导入

部署到目标环境后，需要导入业务数据到大数据表：

```sql
-- 示例：导入收费明细
COPY charge_details FROM '/path/to/charge_details.csv' WITH CSV HEADER;

-- 或使用 ETL 工具导入
```

## 相关文件

- `scripts/build-offline-package.ps1` - Windows PowerShell 打包脚本
- `scripts/build-offline-package.sh` - Linux/WSL Bash 打包脚本
- `test-env-parsing.ps1` - 测试脚本
- `backend/.env` - 环境配置文件
