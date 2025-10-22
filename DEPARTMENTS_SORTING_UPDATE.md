# 科室管理排序功能更新

## 更新时间
2025-10-22

## 更新内容

### 1. 新增排序序号字段

#### 后端更新
- **模型**: 在 `Department` 模型中添加 `sort_order` 字段
  - 类型: `Numeric(10, 2)` - 支持小数，方便插入排序
  - 默认值: 创建时自动设置为最大序号+1
  - 索引: 已添加索引以优化排序查询

#### 数据库迁移
- 迁移文件: `e6c2a4774ba8_add_sort_order_to_departments.py`
- 处理现有数据: 为已存在的科室按ID顺序分配序号
- 状态: ✅ 已执行

### 2. 列表排序功能

#### 后端API更新
**GET /departments** 接口新增参数:
- `sort_by`: 排序字段（默认: sort_order）
  - 可选值: sort_order, his_code, his_name, cost_center_code, cost_center_name, accounting_unit_code, accounting_unit_name, created_at
- `sort_order`: 排序方向（默认: asc）
  - 可选值: asc（升序）, desc（降序）

#### 前端更新
- 表格列添加 `sortable="custom"` 属性，支持点击表头排序
- 新增 `handleSortChange` 方法处理排序事件
- 排序参数自动传递给后端API
- 默认按 `sort_order` 升序排列

### 3. 表单更新

#### 创建科室
- 新增"排序序号"输入框（数字输入框）
- 支持小数输入（精度2位）
- 可留空，后端自动分配为最大序号+1

#### 编辑科室
- 可修改排序序号
- 支持手动调整科室顺序

### 4. UI优化

#### 状态选择框宽度修复
- 原问题: 选择框宽度太窄，无法显示完整内容
- 解决方案: 设置固定宽度 `style="width: 140px"`
- 效果: 可以完整显示"参与评估"和"不参与评估"选项

#### 其他UI改进
- 关键词搜索框设置宽度 `style="width: 200px"`
- 表格新增"序号"列，显示 sort_order 值
- 表格新增"创建时间"列，支持排序

## 功能特性

### 灵活的排序系统
1. **默认排序**: 按序号升序排列
2. **多字段排序**: 支持按任意字段排序
3. **双向排序**: 支持升序和降序
4. **小数序号**: 使用小数类型，方便在两个科室之间插入
   - 例如: 1.0 和 2.0 之间可以插入 1.5

### 自动序号分配
- 创建科室时不指定序号，系统自动分配
- 自动分配规则: 当前最大序号 + 1
- 避免序号冲突

### 表格交互
- 点击表头可切换排序方向
- 排序状态实时反馈
- 支持取消排序（恢复默认排序）

## 使用示例

### 创建科室
```json
POST /api/v1/departments
{
  "his_code": "001",
  "his_name": "内科",
  "sort_order": 1.5,  // 可选，不传则自动分配
  "is_active": true
}
```

### 获取排序列表
```bash
# 按序号升序（默认）
GET /api/v1/departments?sort_by=sort_order&sort_order=asc

# 按科室名称降序
GET /api/v1/departments?sort_by=his_name&sort_order=desc

# 按创建时间降序
GET /api/v1/departments?sort_by=created_at&sort_order=desc
```

### 更新序号
```json
PUT /api/v1/departments/1
{
  "sort_order": 2.5
}
```

## 测试建议

### 功能测试
1. ✅ 创建科室不指定序号，验证自动分配
2. ✅ 创建科室指定序号，验证正确保存
3. ✅ 点击表头排序，验证排序功能
4. ✅ 修改科室序号，验证顺序变化
5. ✅ 使用小数序号插入，验证排序正确

### UI测试
1. ✅ 状态选择框宽度是否足够
2. ✅ 表格列宽是否合适
3. ✅ 排序图标是否正确显示
4. ✅ 数字输入框是否支持小数

## 相关文件

### 后端
- `backend/app/models/department.py` - 添加 sort_order 字段
- `backend/app/schemas/department.py` - 更新 Schema
- `backend/app/api/departments.py` - 添加排序逻辑
- `backend/alembic/versions/e6c2a4774ba8_add_sort_order_to_departments.py` - 数据库迁移

### 前端
- `frontend/src/views/Departments.vue` - 添加排序功能和UI优化

### 文档
- `API设计文档.md` - 更新API文档
- `DEPARTMENTS_SORTING_UPDATE.md` - 本更新文档

## 注意事项

1. **序号唯一性**: 系统不强制序号唯一，允许多个科室使用相同序号
2. **小数精度**: 序号支持2位小数，如 1.00, 1.50, 2.00
3. **排序稳定性**: 相同序号的科室按ID排序
4. **性能优化**: sort_order 字段已添加索引

## 后续优化建议

1. 添加批量调整序号功能
2. 添加拖拽排序功能
3. 添加序号冲突检测和自动调整
4. 添加序号重新编号功能（1, 2, 3...）
