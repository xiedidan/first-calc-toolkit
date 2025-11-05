# 收费项目医疗机构隔离修复总结

## 问题

收费项目管理模块没有与医疗机构对接，用户可以查看到其他医疗机构的收费项目数据。

## 解决方案

### 1. 数据模型更新

#### ChargeItem 模型
```python
# 添加字段
hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)

# 修改唯一约束
__table_args__ = (
    UniqueConstraint('hospital_id', 'item_code', name='uq_hospital_item_code'),
)

# 添加关系
hospital = relationship("Hospital", back_populates="charge_items")
```

#### Hospital 模型
```python
# 添加关系
charge_items = relationship("ChargeItem", back_populates="hospital")
```

#### DimensionItemMapping 模型
```python
# 添加字段
charge_item_id = Column(Integer, ForeignKey("charge_items.id", ondelete="CASCADE"))

# 添加关系
charge_item = relationship("ChargeItem", backref="dimension_mappings")
```

### 2. API 更新

所有收费项目 API 端点已更新，自动应用医疗机构过滤：

- **列表查询** - 使用 `apply_hospital_filter` 自动过滤
- **详情查询** - 验证 `hospital_id` 匹配
- **创建** - 自动添加 `hospital_id`
- **更新** - 验证 `hospital_id` 匹配
- **删除** - 验证 `hospital_id` 匹配
- **清空** - 仅清空当前医疗机构的数据
- **分类列表** - 仅返回当前医疗机构的分类

### 3. 导入功能更新

#### 同步导入
```python
def preprocess_row(row_data: dict) -> dict:
    row_data['hospital_id'] = hospital_id
    return row_data
```

#### 异步导入
```python
# 传递 hospital_id 到 Celery 任务
task = import_charge_items_task.delay(content, mapping_dict, hospital_id)
```

### 4. 数据库迁移

**迁移文件：** `backend/alembic/versions/20251104_add_hospital_to_charge_items.py`

**迁移步骤：**
1. 添加 `hospital_id` 列（允许为空）
2. 将现有数据关联到默认医疗机构
3. 设置 `hospital_id` 为非空
4. 删除旧的唯一约束
5. 创建新的复合唯一约束
6. 创建外键约束和索引

## 执行步骤

### 1. 运行迁移

```bash
# 使用批处理脚本（推荐）
migrate-charge-items.bat

# 或手动执行
cd backend
conda activate hospital-backend
alembic upgrade head
```

### 2. 测试验证

```bash
cd backend
conda activate hospital-backend
python test_charge_item_hospital.py
```

## 文件清单

### 修改的文件
- `backend/app/models/charge_item.py` - 添加 hospital_id 字段和关系
- `backend/app/models/hospital.py` - 添加 charge_items 关系
- `backend/app/models/dimension_item_mapping.py` - 添加 charge_item_id 关系
- `backend/app/api/charge_items.py` - 所有 API 端点添加医疗机构过滤
- `backend/app/tasks/import_tasks.py` - 导入任务添加 hospital_id 参数
- `backend/app/services/excel_import_service.py` - 添加 preprocess_func 支持

### 新增的文件
- `backend/alembic/versions/20251104_add_hospital_to_charge_items.py` - 数据库迁移脚本
- `backend/test_charge_item_hospital.py` - 测试脚本
- `migrate-charge-items.bat` - 迁移执行脚本
- `CHARGE_ITEMS_HOSPITAL_ISOLATION.md` - 详细文档
- `CHARGE_ITEMS_HOSPITAL_FIX_SUMMARY.md` - 本文档

## 验证要点

1. ✓ 不同医疗机构的用户只能看到自己机构的收费项目
2. ✓ 创建收费项目时自动关联到当前医疗机构
3. ✓ 导入收费项目时自动关联到当前医疗机构
4. ✓ 同一医疗机构内收费项目编码唯一
5. ✓ 不同医疗机构可以有相同的收费项目编码
6. ✓ 删除医疗机构时级联删除其收费项目

## 影响范围

### 数据库
- `charge_items` 表结构变更
- 添加外键约束和索引

### 后端 API
- 所有收费项目相关 API 自动应用医疗机构过滤
- API 接口保持兼容，无需前端修改

### 前端
- 无需修改，API 自动处理医疗机构隔离

## 注意事项

1. **现有数据**：迁移时会将所有现有收费项目关联到第一个医疗机构
2. **唯一性**：同一医疗机构内收费项目编码必须唯一
3. **级联删除**：删除医疗机构会自动删除其收费项目
4. **导入数据**：导入时自动关联到当前用户的医疗机构

## 下一步

收费项目的医疗机构隔离已完成。建议检查其他业务模块是否也需要类似的隔离处理。
