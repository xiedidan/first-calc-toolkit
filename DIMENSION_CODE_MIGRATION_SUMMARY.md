# 维度Code迁移 - 执行总结

## 已完成

✅ 1. 创建数据库迁移脚本
✅ 2. 修改模型定义（dimension_id → dimension_code）
✅ 3. 修改Schema定义

## 进行中

🔄 4. 修改API层

由于API文件较大且改动较多，建议：
1. 先执行数据库迁移
2. 然后重启后端服务
3. 测试API是否正常工作

## 关键变更点

### API层需要修改的地方

1. **查询接口** (`get_dimension_items`)
   - 参数从 `dimension_id/dimension_ids` 改为 `dimension_code/dimension_codes`
   - JOIN条件从 `dimension_id == ModelNode.id` 改为 `dimension_code == ModelNode.code`

2. **创建接口** (`create_dimension_items`)
   - 参数从 `dimension_id` 改为 `dimension_code`
   - 创建映射时使用 `dimension_code`

3. **更新接口** (`update_dimension_item`)
   - 参数从 `new_dimension_id` 改为 `new_dimension_code`
   - 更新时使用 `dimension_code`

4. **删除接口** (`clear_all_dimension_items`)
   - 参数从 `dimension_id` 改为 `dimension_code`
   - 查询条件使用 `dimension_code`

5. **智能导入服务**
   - 所有使用 `dimension_id` 的地方改为 `dimension_code`

## 执行步骤

### 1. 数据库迁移

```bash
cd backend
conda activate performance_system
alembic upgrade head
```

### 2. 验证迁移

检查表结构：
```sql
DESC dimension_item_mappings;
```

应该看到 `dimension_code` 字段，而不是 `dimension_id`。

### 3. 重启服务

```bash
# 停止当前服务
# 重新启动
python -m uvicorn app.main:app --reload
```

### 4. 测试

- 测试查询接口
- 测试创建接口
- 测试更新接口
- 测试删除接口
- 测试智能导入

## 注意事项

1. **备份数据**：迁移前务必备份数据库
2. **停机维护**：建议在维护窗口执行
3. **回滚准备**：如果出现问题，可以执行 `alembic downgrade -1`
4. **前端更新**：前端代码也需要同步更新

## 风险评估

- **高风险**：这是破坏性变更，会影响所有相关功能
- **影响范围**：维度目录管理、智能导入、所有相关API
- **恢复时间**：如果出现问题，需要回滚数据库和代码

## 建议

由于这是一个大的变更，建议：
1. 在开发环境充分测试
2. 准备详细的测试用例
3. 准备回滚方案
4. 通知所有相关人员

## 后续工作

完成API层修改后，还需要：
1. 修改前端代码
2. 更新文档
3. 进行全面测试
