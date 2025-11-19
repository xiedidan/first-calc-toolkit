# 模型节点单位字段功能说明

## 功能概述

为模型节点添加了 `unit`（单位）字段，用于标识权重/单价的计量单位。

## 字段详情

- **字段名**: `unit`
- **类型**: 字符串 (最大长度 20)
- **默认值**: `%`
- **是否必填**: 否
- **适用范围**: 末级维度节点

## 使用场景

不同的绩效指标可能使用不同的计量单位：

1. **百分比** (默认): `%`
   - 适用于比率、占比类指标
   - 例如：门诊人次占比、手术成功率等

2. **金额单位**: `元/例`、`元/人天`、`元`
   - 适用于成本、收入类指标
   - 例如：平均住院费用、人均药品费用等

3. **其他单位**: `次`、`人`、`天`、`分`
   - 适用于计数、时间类指标
   - 例如：门诊人次、平均住院天数等

## 数据库结构

### model_nodes 表

```sql
ALTER TABLE model_nodes 
ADD COLUMN unit VARCHAR(20) DEFAULT '%' COMMENT '单位';
```

## API 接口

### 创建节点

```json
POST /api/model-nodes
{
  "version_id": 1,
  "name": "平均住院费用",
  "code": "AVG_HOSPITAL_COST",
  "node_type": "dimension",
  "is_leaf": true,
  "calc_type": "statistical",
  "weight": 5000.00,
  "unit": "元/例",  // 自定义单位
  "business_guide": "控制平均住院费用"
}
```

### 更新节点

```json
PUT /api/model-nodes/{node_id}
{
  "unit": "元/人天"  // 更新单位
}
```

### 响应示例

```json
{
  "id": 1,
  "name": "平均住院费用",
  "code": "AVG_HOSPITAL_COST",
  "weight": 5000.00,
  "unit": "元/例",
  "is_leaf": true,
  "calc_type": "statistical",
  ...
}
```

## 前端界面

### 显示效果

在节点列表的"权重/单价"列中显示：
```
5000.00 元/例
```

### 编辑表单

在编辑/新增节点对话框中：
- 当节点为末级维度时，显示"单位"输入框
- 输入框提供占位符提示：`如: %, 元/例, 元/人天`
- 如果不填写，默认使用 `%`

## 数据迁移

已创建的迁移文件：
- `i3j4k5l6m7n8_add_unit_to_model_nodes.py`

执行迁移：
```bash
# 方式1: 使用脚本
.\migrate-simple.bat

# 方式2: 直接执行
cd backend
alembic upgrade head
```

## 测试

运行测试脚本验证功能：
```bash
cd backend
python test_unit_field.py
```

测试内容：
1. 创建带自定义单位的节点
2. 更新节点单位
3. 验证默认单位
4. 查询节点列表

## 注意事项

1. **单位字段仅对末级维度有效**
   - 序列节点和非末级维度节点不需要设置单位

2. **单位长度限制**
   - 最大 20 个字符
   - 建议使用简洁的单位表示

3. **常用单位建议**
   - 百分比: `%`
   - 金额: `元`、`元/例`、`元/人`、`元/人天`
   - 计数: `次`、`人`、`例`
   - 时间: `天`、`小时`、`分钟`
   - 比率: `‰`（千分比）

4. **向后兼容**
   - 已存在的节点会自动设置默认单位 `%`
   - 不影响现有功能

## 相关文件

### 后端
- 模型: `backend/app/models/model_node.py`
- Schema: `backend/app/schemas/model_node.py`
- API: `backend/app/api/model_nodes.py`
- 迁移: `backend/alembic/versions/i3j4k5l6m7n8_add_unit_to_model_nodes.py`

### 前端
- 页面: `frontend/src/views/ModelNodes.vue`
- API: `frontend/src/api/model.ts`

### 测试
- 测试脚本: `backend/test_unit_field.py`

## 更新日志

**2025-10-23**
- ✓ 添加 unit 字段到数据库模型
- ✓ 更新 Schema 定义
- ✓ 前端界面支持单位显示和编辑
- ✓ 创建数据库迁移文件
- ✓ 编写测试脚本
- ✓ 编写功能文档
