# 离线打包脚本升级总结

## 升级内容

### 从"白名单"改为"黑名单"模式

**升级前**：
- 需要手动列出所有要导出数据的表（16个）
- 新增表需要修改脚本添加到列表
- 维护成本高，容易遗漏

**升级后**：
- 只需列出不导出数据的表（7个大数据表）
- 新增表自动导出数据
- 维护成本低，不会遗漏

## 技术实现

### 配置文件

创建 `.offline-package-exclude-tables.txt` 文件：

```txt
# 离线打包排除列表
# 这些表只导出结构，不导出数据（大数据表）
# 以 # 开头的行为注释

charge_details
calculation_results
calculation_tasks
orientation_adjustment_details
orientation_values
cost_values
department_revenues
```

### PowerShell 脚本

```powershell
# 从配置文件读取排除列表
$tablesSchemaOnly = Get-Content ".offline-package-exclude-tables.txt" | 
    Where-Object { $_ -notmatch '^\s*#' -and $_ -notmatch '^\s*$' } |
    ForEach-Object { $_.Trim() }

# 使用 --exclude-table-data 参数
$excludeArgs = $tablesSchemaOnly | ForEach-Object { "--exclude-table-data=$_" }
pg_dump ... --data-only @excludeArgs
```

### Bash 脚本

```bash
# 从配置文件读取排除列表
TABLES_SCHEMA_ONLY=()
while IFS= read -r line; do
    if [[ ! "$line" =~ ^[[:space:]]*# ]] && [[ -n "${line// }" ]]; then
        table=$(echo "$line" | xargs)
        TABLES_SCHEMA_ONLY+=("$table")
    fi
done < ".offline-package-exclude-tables.txt"

# 使用 --exclude-table-data 参数
EXCLUDE_ARGS=""
for table in "${TABLES_SCHEMA_ONLY[@]}"; do
    EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude-table-data=$table"
done
pg_dump ... --data-only $EXCLUDE_ARGS
```

## 排除的表（7个）

| 表名 | 说明 | 原因 |
|------|------|------|
| charge_details | 收费明细表 | 数十万~数百万行 |
| calculation_results | 计算结果表 | 数万~数十万行 |
| calculation_tasks | 计算任务表 | 数百~数千行 |
| orientation_adjustment_details | 导向调整明细表 | 数万~数十万行 |
| orientation_values | 导向实际值表 | 数千~数万行 |
| cost_values | 成本值表 | 数千~数万行 |
| department_revenues | 科室收入表 | 数千~数万行 |

## 自动包含的表

所有其他表都会自动导出数据，包括：

### 基础配置表
- users, hospitals, departments
- charge_items, charge_item_mappings
- data_sources

### 模型配置表
- model_versions, model_nodes
- calculation_workflows, workflow_steps

### 导向配置表
- orientation_rules, orientation_ladders
- orientation_benchmarks

### 基准数据表
- cost_benchmarks, revenue_benchmarks

### AI 配置表
- ai_configs

### 未来新增的表
- **任何新增的表都会自动导出数据**
- **除非手动添加到排除列表**

## 优势对比

| 特性 | 升级前（白名单） | 升级后（黑名单） |
|------|----------------|----------------|
| 维护表列表 | 16个 | 7个 |
| 新增表处理 | 需要修改脚本 | 自动包含 |
| 遗漏风险 | 高 | 低 |
| 维护成本 | 高 | 低 |
| 灵活性 | 低 | 高 |

## 使用示例

### 添加新表到排除列表

如果新增了一个大数据表 `new_large_table`，只需编辑配置文件：

**编辑 `.offline-package-exclude-tables.txt`**:
```txt
charge_details
calculation_results
calculation_tasks
orientation_adjustment_details
orientation_values
cost_values
department_revenues
new_large_table  # 添加这一行
```

**无需修改任何脚本代码！**

### 新增配置表

如果新增了配置表 `new_config_table`：
- **无需任何修改**
- 脚本会自动导出该表的数据

## 验证方法

```powershell
# 测试配置
.\test-selective-export.ps1

# 执行打包
.\scripts\build-offline-package.ps1
```

## 导出过程输出

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

>>> 步骤 1/3: 导出完整表结构...
✓ 表结构导出完成

>>> 步骤 2/3: 导出数据（排除大数据表）...
✓ 数据导出完成

>>> 步骤 3/3: 合并 SQL 文件...
✓ SQL 文件合并完成

>>> 压缩 SQL 文件...
✓ 数据库导出完成 (XX MB)
```

## 部署后数据导入

部署到目标环境后，需要导入业务数据到排除的表：

```sql
-- 示例：导入收费明细
COPY charge_details FROM '/path/to/charge_details.csv' WITH CSV HEADER;

-- 或使用应用的数据导入功能
```

## 相关文件

- ✅ `.offline-package-exclude-tables.txt` - 排除列表配置文件（新增）
- ✅ `scripts/build-offline-package.ps1` - PowerShell 打包脚本（已升级）
- ✅ `scripts/build-offline-package.sh` - Bash 打包脚本（已升级）
- ✅ `test-selective-export.ps1` - 测试脚本（已更新）
- ✅ `OFFLINE_PACKAGE_ENV_FIX.md` - 详细文档（已更新）
- ✅ `OFFLINE_PACKAGE_OPTIMIZATION_SUMMARY.md` - 优化总结（已更新）
- ✅ `OFFLINE_PACKAGE_UPGRADE_SUMMARY.md` - 本文档

## 配置文件优势

| 特性 | 硬编码方式 | 配置文件方式 |
|------|-----------|------------|
| 修改排除列表 | 需要修改脚本代码 | 只需编辑文本文件 |
| 可读性 | 代码中查找 | 独立文件，一目了然 |
| 注释说明 | 代码注释 | 支持详细注释 |
| 版本控制 | 混在代码中 | 独立跟踪 |
| 维护难度 | 需要懂脚本语法 | 任何人都能编辑 |

## 总结

这次升级实现了两个重要改进：

1. **从"白名单"改为"黑名单"模式**：只需维护排除列表，其他表自动导出
2. **使用配置文件管理排除列表**：无需修改脚本代码，降低维护门槛

这使得打包脚本更加灵活、易维护，新增表会自动包含在导出中，不会遗漏配置数据。
