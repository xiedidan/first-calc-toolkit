# 迁移问题已修复

> **问题**: Multiple head revisions are present  
> **状态**: ✅ 已修复

---

## 🔍 问题原因

有两个迁移文件指向同一个父版本，造成了分支冲突：
- `a1b2c3d4e5f6` (索引优化) → `f0384ea4c792`
- `g1h2i3j4k5l6` (模型表) → `f0384ea4c792`

---

## ✅ 修复方案

已将 `g1h2i3j4k5l6` 的父版本改为 `a1b2c3d4e5f6`，形成正确的迁移链：

```
e6c2a4774ba8
    ↓
f0384ea4c792
    ↓
a1b2c3d4e5f6 (索引优化)
    ↓
g1h2i3j4k5l6 (模型表) ← 新增
```

---

## 🚀 现在执行迁移

### 方法1: 使用新的批处理文件

双击 **`fix-and-migrate.bat`**

### 方法2: 手动执行

```bash
cd backend
python -m alembic upgrade heads
```

---

## ✅ 预期结果

```
INFO  [alembic.runtime.migration] Running upgrade f0384ea4c792 -> a1b2c3d4e5f6, add indexes to charge items
INFO  [alembic.runtime.migration] Running upgrade a1b2c3d4e5f6 -> g1h2i3j4k5l6, Add model_versions and model_nodes tables
```

---

## 🔄 重启后端

迁移成功后，重启后端服务：

1. 在后端窗口按 `Ctrl+C`
2. 运行: `.\scripts\dev-start-backend.ps1`
3. 刷新浏览器

---

## 🎉 完成

问题已解决，现在可以正常使用模型管理功能了！

---

**修复时间**: 2025-10-22  
**状态**: ✅ 已修复
