# 🚀 数据源功能 - 开始使用

## ⚡ 快速开始（3步）

### 1️⃣ 生成加密密钥

```bash
cd backend
python generate_encryption_key.py
```

按 `y` 确认，工具会自动配置。

### 2️⃣ 执行数据库迁移

```bash
alembic upgrade head
```

### 3️⃣ 启动服务

```bash
uvicorn app.main:app --reload
```

✅ 完成！访问 http://localhost:8000/docs 查看API文档

## 📚 文档导航

### 🆘 遇到问题？
→ [快速修复指南](QUICK_FIX_GUIDE.md)

### 📖 详细文档
- [功能说明](DATA_SOURCE_README.md) - 了解功能
- [快速启动](DATA_SOURCE_QUICKSTART.md) - 详细步骤
- [部署指南](DEPLOYMENT_GUIDE.md) - 生产部署
- [文档索引](DATA_SOURCE_DOCS_INDEX.md) - 所有文档

### 🧪 测试
```bash
# 测试加密
python test_encryption.py

# 测试API
python test_data_source_api.py
```

## 🎯 核心功能

✅ 多数据源管理（PostgreSQL/MySQL/SQL Server/Oracle）  
✅ 密码加密存储（AES-256）  
✅ 连接测试  
✅ 连接池管理  
✅ 9个API接口  

## 💡 提示

- 密钥生成后请妥善保管
- 生产环境使用密钥管理服务
- 查看 [交付清单](DATA_SOURCE_DELIVERY_CHECKLIST.md) 了解完整功能

## 🐛 常见问题

**Q: 提示 "Extra inputs are not permitted"**  
A: 运行 `python generate_encryption_key.py` 配置密钥

**Q: 迁移失败**  
A: 检查数据库连接，查看 [快速修复指南](QUICK_FIX_GUIDE.md)

**Q: 密钥格式错误**  
A: 使用工具生成，不要手动编辑

## 📞 获取帮助

1. 查看 [快速修复指南](QUICK_FIX_GUIDE.md)
2. 查看 [部署指南](DEPLOYMENT_GUIDE.md) 的故障排查章节
3. 运行测试脚本检查问题

---

**版本**: 1.0.1  
**更新**: 2025-10-28  
**状态**: ✅ 生产就绪
