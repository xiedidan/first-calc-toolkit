# 科室核算序列功能

## 功能概述

为科室对照表增加"核算序列"字段，支持多选"医生"、"护理"、"医技"三个选项。

## 数据库变更

### 字段定义
- **字段名**: `accounting_sequences`
- **类型**: `VARCHAR(20)[]` (PostgreSQL数组类型)
- **可选值**: `["医生", "护理", "医技"]`
- **允许为空**: 是
- **索引**: GIN索引，支持高效的数组查询

### 添加方式
使用 `add_accounting_sequences_field.py` 脚本直接通过SQL添加字段，避免Alembic迁移依赖问题。

```bash
python add_accounting_sequences_field.py
```

## 后端实现

### 模型 (backend/app/models/department.py)
```python
from sqlalchemy.dialects.postgresql import ARRAY

accounting_sequences = Column(
    ARRAY(String(20)), 
    comment="核算序列（可多选：医生、护理、医技）"
)
```

### Schema (backend/app/schemas/department.py)
```python
from typing import List, Optional

class DepartmentBase(BaseModel):
    # ... 其他字段
    accounting_sequences: Optional[List[str]] = Field(
        None, 
        description="核算序列（可多选：医生、护理、医技）"
    )
```

### API端点
- `GET /api/v1/departments` - 列表中显示核算序列
- `POST /api/v1/departments` - 创建时可设置核算序列
- `PUT /api/v1/departments/{id}` - 更新核算序列

## 前端实现

### 表格显示 (frontend/src/views/Departments.vue)
在科室列表中显示核算序列标签：
```vue
<el-table-column label="核算序列" width="180">
  <template #default="{ row }">
    <el-tag 
      v-for="seq in row.accounting_sequences" 
      :key="seq" 
      size="small" 
      style="margin-right: 5px"
    >
      {{ seq }}
    </el-tag>
    <span v-if="!row.accounting_sequences || row.accounting_sequences.length === 0">-</span>
  </template>
</el-table-column>
```

### 编辑表单
使用多选下拉框：
```vue
<el-form-item label="核算序列">
  <el-select 
    v-model="form.accounting_sequences" 
    multiple 
    placeholder="请选择核算序列"
    style="width: 100%"
  >
    <el-option label="医生" value="医生" />
    <el-option label="护理" value="护理" />
    <el-option label="医技" value="医技" />
  </el-select>
</el-form-item>
```

## 使用场景

1. **科室分类管理**: 标识科室参与哪些核算序列的计算
2. **数据筛选**: 可按核算序列筛选科室
3. **报表生成**: 根据核算序列生成不同维度的报表
4. **权限控制**: 可基于核算序列进行权限划分

## 数据示例

```json
{
  "id": 1,
  "his_code": "001",
  "his_name": "内科",
  "accounting_sequences": ["医生", "护理"],
  "is_active": true
}
```

## 测试

运行测试脚本验证功能：
```bash
python test_accounting_sequences.py
```

测试内容包括：
- 获取科室列表（显示核算序列）
- 创建科室（设置核算序列）
- 更新核算序列
- 清空核算序列
- 删除科室

## 注意事项

1. **数组类型**: PostgreSQL特有的ARRAY类型，其他数据库需调整
2. **空值处理**: 前端需处理null和空数组两种情况
3. **验证**: 前端可添加选项验证，确保只能选择预定义的值
4. **索引**: 使用GIN索引支持数组查询，如 `WHERE '医生' = ANY(accounting_sequences)`

## 后续扩展

1. 可在系统设置中配置可选的核算序列选项
2. 支持按核算序列筛选科室
3. 在计算流程中根据核算序列进行数据分组
4. 导出功能中包含核算序列信息
