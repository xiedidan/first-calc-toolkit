# 快速开始 - SQL 步骤测试

## 5 分钟快速体验

### 前置条件
- ✅ 后端服务运行中
- ✅ 前端服务运行中  
- ✅ 已创建至少一个数据源
- ✅ 已创建至少一个计算流程

### 步骤 1：创建 SQL 步骤（2 分钟）

1. 打开浏览器访问前端页面
2. 导航到 **计算流程管理**
3. 选择任意流程，点击 **查看步骤**
4. 点击 **新建步骤** 按钮
5. 填写表单：
   ```
   步骤名称: 测试查询
   步骤描述: 测试 SQL 步骤功能
   代码类型: SQL
   数据源: [选择你的数据源]
   代码内容: SELECT 1 as id, 'Hello' as message, NOW() as time
   是否启用: 开启
   ```
6. 点击 **确定**

### 步骤 2：测试 SQL 步骤（1 分钟）

1. 在步骤列表中找到刚创建的步骤
2. 点击 **测试** 按钮
3. 查看测试结果弹窗：
   - ✅ 执行时间
   - ✅ 返回列名：id, message, time
   - ✅ 数据结果

### 步骤 3：尝试真实查询（2 分钟）

编辑步骤，修改 SQL 为：

```sql
-- PostgreSQL 示例
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables
WHERE schemaname = 'public'
LIMIT 5
```

或

```sql
-- MySQL 示例
SELECT 
    table_schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = DATABASE()
LIMIT 5
```

点击测试，查看你的数据库表信息！

## 自动化测试（可选）

如果你想用脚本测试：

```bash
cd backend
python test_step_integration.py
```

脚本会自动完成所有测试步骤。

## 常见问题

**Q: 提示"SQL步骤必须指定数据源"？**  
A: 确保在创建步骤时选择了数据源。

**Q: 测试失败显示连接错误？**  
A: 检查数据源配置是否正确，可以在"系统设置 → 数据源管理"中测试连接。

**Q: 查询返回空结果？**  
A: 检查 SQL 语法和表是否存在。

**Q: Python 步骤的虚拟环境为什么是禁用的？**  
A: Python 步骤执行功能暂未实现，目前仅为 UI 预留。

## 下一步

- 📖 阅读完整文档：`STEP_DATASOURCE_INTEGRATION_TEST.md`
- 🔧 查看实现细节：`STEP_DATASOURCE_SUMMARY.md`
- 🎯 开始构建你的计算流程！

---

**提示**: 测试 SQL 时会自动添加 `LIMIT 100`，确保不会返回过多数据。
