# 快速修复 - 数据库表不存在

> **错误**: relation "model_versions" does not exist

---

## 🚀 快速修复（1分钟）

### 步骤1: 双击运行

双击项目根目录的 **`run-migration.bat`** 文件

### 步骤2: 等待完成

看到 "迁移完成！" 提示后，按任意键关闭窗口

### 步骤3: 重启后端

在后端服务窗口按 `Ctrl+C` 停止，然后重新运行：
```bash
.\scripts\dev-start-backend.ps1
```

### 步骤4: 刷新浏览器

刷新前端页面，问题解决！✅

---

## 📝 详细说明

如果上述方法不行，请查看：
- [详细修复指南](./FIX_DATABASE_MIGRATION.md)
- [迁移指南](./MIGRATION_GUIDE.md)

---

## ❓ 为什么会出现这个错误？

因为新增的数据库表还没有创建。运行 `run-migration.bat` 会自动创建这些表：
- `model_versions` - 模型版本表
- `model_nodes` - 模型节点表

---

**解决时间**: 约1分钟
