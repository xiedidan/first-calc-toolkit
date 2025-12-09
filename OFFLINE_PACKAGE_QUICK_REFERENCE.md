# 离线打包快速参考

## 一键打包

```powershell
# Windows
.\scripts\build-offline-package.ps1

# Linux/WSL
bash scripts/build-offline-package.sh
```

## 配置排除列表

编辑 `.offline-package-exclude-tables.txt`：

```txt
# 添加不需要导出数据的表（每行一个）
new_large_table
```

## 验证配置

```powershell
.\test-selective-export.ps1
```

## 工作原理

```
┌─────────────────────────────────────┐
│  .offline-package-exclude-tables.txt│
│  ├─ charge_details                  │
│  ├─ calculation_results             │
│  └─ ...                             │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  build-offline-package.ps1/sh       │
│  ├─ 读取排除列表                     │
│  ├─ 导出所有表结构                   │
│  ├─ 导出数据（排除列表中的表除外）    │
│  └─ 压缩打包                        │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  offline-package/database.sql.gz    │
│  ├─ 所有表结构                       │
│  ├─ 配置表数据                       │
│  └─ 大数据表仅结构                   │
└─────────────────────────────────────┘
```

## 当前排除的表（7个）

| 表名 | 数据量 |
|------|--------|
| charge_details | 数十万~数百万行 |
| calculation_results | 数万~数十万行 |
| calculation_tasks | 数百~数千行 |
| orientation_adjustment_details | 数万~数十万行 |
| orientation_values | 数千~数万行 |
| cost_values | 数千~数万行 |
| department_revenues | 数千~数万行 |

## 常见操作

### 添加新表到排除列表

```txt
# 编辑 .offline-package-exclude-tables.txt
new_table_name
```

### 临时导出某个表的数据

```txt
# 注释该表
# charge_details
```

### 导出所有表的数据

```txt
# 注释所有表或清空文件
```

## 文件大小对比

| 模式 | 文件大小 | 说明 |
|------|---------|------|
| 完整导出 | 500-1000 MB | 包含所有数据 |
| 选择性导出 | 5-50 MB | 排除大数据表 |
| 减少比例 | 80-95% | 大幅节省空间 |

## 故障排除

### 找不到配置文件

```powershell
# 检查文件是否存在
Test-Path .offline-package-exclude-tables.txt

# 如果不存在，从模板创建
Copy-Item .offline-package-exclude-tables.txt.example .offline-package-exclude-tables.txt
```

### 连接错误的数据库

检查 `backend/.env` 中的 `DATABASE_URL` 配置

### 文件仍然很大

检查排除列表是否包含所有大数据表

## 相关文档

- `.offline-package-exclude-tables.README.md` - 配置文件详细说明
- `OFFLINE_PACKAGE_UPGRADE_SUMMARY.md` - 升级说明
- `OFFLINE_PACKAGE_OPTIMIZATION_SUMMARY.md` - 优化总结
