# 模型版本管理模块 - 实现完成

> **完成日期**: 2025-10-22
> **状态**: ✅ 已完成

---

## 1. 实现概述

模型版本管理模块是医院科室业务价值评估工具的核心功能之一，用于管理评估模型的版本和结构。本模块实现了以下功能：

- ✅ 模型版本的创建、查询、更新、删除
- ✅ 模型版本的激活/切换
- ✅ 基于现有版本复制创建新版本
- ✅ 模型节点的树状结构管理
- ✅ 模型节点的CRUD操作
- ✅ 节点代码测试接口（框架已实现，具体执行逻辑待完善）

---

## 2. 数据库设计

### 2.1. model_versions 表

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | INTEGER | 主键 |
| version | VARCHAR(50) | 版本号（唯一） |
| name | VARCHAR(100) | 版本名称 |
| description | TEXT | 版本描述 |
| is_active | BOOLEAN | 是否激活 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

**索引**:
- `ix_model_versions_id`: 主键索引
- `ix_model_versions_version`: 版本号唯一索引

### 2.2. model_nodes 表

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | INTEGER | 主键 |
| version_id | INTEGER | 模型版本ID（外键） |
| parent_id | INTEGER | 父节点ID（外键，自关联） |
| name | VARCHAR(100) | 节点名称 |
| code | VARCHAR(50) | 节点编码 |
| node_type | VARCHAR(20) | 节点类型(sequence/dimension) |
| calc_type | VARCHAR(20) | 计算类型(statistical/calculational) |
| weight | NUMERIC(10,4) | 权重/单价 |
| business_guide | TEXT | 业务导向 |
| script | TEXT | SQL/Python脚本 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

**索引**:
- `ix_model_nodes_id`: 主键索引
- `ix_model_nodes_version_id`: 版本ID索引
- `ix_model_nodes_parent_id`: 父节点ID索引

**外键约束**:
- `version_id` → `model_versions.id` (CASCADE DELETE)
- `parent_id` → `model_nodes.id` (CASCADE DELETE)

---

## 3. API接口

### 3.1. 模型版本管理 API

#### 3.1.1. 获取模型版本列表
```
GET /api/v1/model-versions
```

**查询参数**:
- `skip`: 跳过记录数（默认0）
- `limit`: 返回记录数（默认100）

**响应示例**:
```json
{
  "total": 5,
  "items": [
    {
      "id": 1,
      "version": "v1.0",
      "name": "2025年标准版",
      "description": "2025年度评估标准",
      "is_active": true,
      "created_at": "2025-10-22T10:00:00",
      "updated_at": "2025-10-22T10:00:00"
    }
  ]
}
```

#### 3.1.2. 创建模型版本
```
POST /api/v1/model-versions
```

**请求体**:
```json
{
  "version": "v1.1",
  "name": "2025年标准版-修订",
  "description": "基于v1.0的修订版本",
  "base_version_id": 1
}
```

**说明**:
- 如果提供 `base_version_id`，将复制该版本的所有节点结构
- 版本号必须唯一

#### 3.1.3. 获取模型版本详情
```
GET /api/v1/model-versions/{version_id}
```

#### 3.1.4. 更新模型版本
```
PUT /api/v1/model-versions/{version_id}
```

**请求体**:
```json
{
  "name": "2025年标准版-最终版",
  "description": "更新后的描述"
}
```

#### 3.1.5. 删除模型版本
```
DELETE /api/v1/model-versions/{version_id}
```

**注意**: 不能删除激活状态的版本

#### 3.1.6. 激活模型版本
```
PUT /api/v1/model-versions/{version_id}/activate
```

**说明**: 激活指定版本，同时取消其他版本的激活状态

### 3.2. 模型节点管理 API

#### 3.2.1. 获取模型节点列表
```
GET /api/v1/model-nodes?version_id={version_id}
```

**查询参数**:
- `version_id`: 模型版本ID（必填）
- `parent_id`: 父节点ID（可选，不提供则返回根节点）

**响应示例**:
```json
{
  "total": 3,
  "items": [
    {
      "id": 1,
      "version_id": 1,
      "parent_id": null,
      "name": "医生序列",
      "code": "DOCTOR",
      "node_type": "sequence",
      "calc_type": null,
      "weight": null,
      "business_guide": "医生工作量评估",
      "script": null,
      "created_at": "2025-10-22T10:00:00",
      "updated_at": "2025-10-22T10:00:00",
      "children": [
        {
          "id": 2,
          "version_id": 1,
          "parent_id": 1,
          "name": "门诊诊察",
          "code": "OUTPATIENT",
          "node_type": "dimension",
          "calc_type": "statistical",
          "weight": 0.3000,
          "business_guide": "门诊工作量",
          "script": "SELECT ...",
          "created_at": "2025-10-22T10:00:00",
          "updated_at": "2025-10-22T10:00:00",
          "children": []
        }
      ]
    }
  ]
}
```

#### 3.2.2. 创建模型节点
```
POST /api/v1/model-nodes
```

**请求体**:
```json
{
  "version_id": 1,
  "parent_id": 1,
  "name": "住院手术",
  "code": "SURGERY",
  "node_type": "dimension",
  "calc_type": "calculational",
  "weight": 0.4000,
  "business_guide": "手术工作量评估",
  "script": "SELECT department_id, COUNT(*) as count FROM surgeries WHERE ..."
}
```

#### 3.2.3. 获取模型节点详情
```
GET /api/v1/model-nodes/{node_id}
```

#### 3.2.4. 更新模型节点
```
PUT /api/v1/model-nodes/{node_id}
```

**请求体**:
```json
{
  "name": "住院手术（更新）",
  "weight": 0.4500,
  "script": "SELECT ..."
}
```

#### 3.2.5. 删除模型节点
```
DELETE /api/v1/model-nodes/{node_id}
```

**注意**: 删除节点会级联删除其所有子节点

#### 3.2.6. 测试节点代码
```
POST /api/v1/model-nodes/{node_id}/test-code
```

**请求体**:
```json
{
  "script": "SELECT department_id, COUNT(*) FROM ...",
  "test_params": {
    "current_year_month": "2025-10"
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "result": {
    "message": "代码测试功能待实现",
    "script": "SELECT department_id, COUNT(*) FROM ..."
  }
}
```

**说明**: 当前返回模拟结果，实际执行逻辑需要后续实现

---

## 4. 代码结构

### 4.1. 文件清单

```
backend/
├── app/
│   ├── models/
│   │   ├── model_version.py          # 模型版本数据模型
│   │   └── model_node.py             # 模型节点数据模型
│   ├── schemas/
│   │   ├── model_version.py          # 模型版本Schema
│   │   └── model_node.py             # 模型节点Schema
│   └── api/
│       ├── model_versions.py         # 模型版本API路由
│       └── model_nodes.py            # 模型节点API路由
└── alembic/
    └── versions/
        └── g1h2i3j4k5l6_add_model_version_and_node_tables.py  # 数据库迁移
```

### 4.2. 核心功能实现

#### 4.2.1. 版本复制功能

在创建新版本时，如果提供了 `base_version_id`，系统会：
1. 创建新的版本记录
2. 递归复制源版本的所有节点
3. 保持节点的层级关系和属性

```python
def _copy_nodes(db: Session, source_version_id: int, target_version_id: int):
    """复制节点结构"""
    source_nodes = db.query(ModelNode).filter(
        ModelNode.version_id == source_version_id,
        ModelNode.parent_id.is_(None)
    ).all()
    
    for node in source_nodes:
        _copy_node_recursive(db, node, target_version_id, None)
    
    db.commit()
```

#### 4.2.2. 树状结构加载

查询节点时，系统会递归加载所有子节点：

```python
def _load_children(db: Session, node: ModelNode):
    """递归加载子节点"""
    children = db.query(ModelNode).filter(ModelNode.parent_id == node.id).all()
    node.children = children
    for child in children:
        _load_children(db, child)
```

#### 4.2.3. 级联删除

通过数据库外键约束实现：
- 删除版本时，自动删除该版本的所有节点
- 删除节点时，自动删除该节点的所有子节点

---

## 5. 使用示例

### 5.1. 创建第一个模型版本

```bash
# 1. 创建版本
curl -X POST http://localhost:8000/api/v1/model-versions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "v1.0",
    "name": "2025年标准版",
    "description": "初始版本"
  }'

# 2. 创建根节点（序列）
curl -X POST http://localhost:8000/api/v1/model-nodes \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "version_id": 1,
    "name": "医生序列",
    "code": "DOCTOR",
    "node_type": "sequence",
    "business_guide": "医生工作量评估"
  }'

# 3. 创建子节点（维度）
curl -X POST http://localhost:8000/api/v1/model-nodes \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "version_id": 1,
    "parent_id": 1,
    "name": "门诊诊察",
    "code": "OUTPATIENT",
    "node_type": "dimension",
    "calc_type": "statistical",
    "weight": 0.3000,
    "business_guide": "门诊工作量",
    "script": "SELECT department_id, COUNT(*) as count FROM outpatient_visits WHERE visit_date >= {current_year_month}"
  }'
```

### 5.2. 基于现有版本创建新版本

```bash
curl -X POST http://localhost:8000/api/v1/model-versions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "v1.1",
    "name": "2025年标准版-修订",
    "description": "基于v1.0的修订版本",
    "base_version_id": 1
  }'
```

### 5.3. 激活版本

```bash
curl -X PUT http://localhost:8000/api/v1/model-versions/2/activate \
  -H "Authorization: Bearer <token>"
```

---

## 6. 数据库迁移

### 6.1. 执行迁移

```bash
# 进入backend目录
cd backend

# 执行迁移
conda run -n hospital_value alembic upgrade head
```

### 6.2. 回滚迁移

```bash
# 回滚到上一个版本
conda run -n hospital_value alembic downgrade -1

# 回滚到指定版本
conda run -n hospital_value alembic downgrade f0384ea4c792
```

---

## 7. 待完善功能

### 7.1. 代码测试功能

当前 `/model-nodes/{node_id}/test-code` 接口返回模拟结果，需要实现：

1. **SQL执行器**
   - 解析SQL脚本
   - 替换占位符（如 `{current_year_month}`）
   - 执行SQL并返回结果
   - 错误处理和超时控制

2. **Python执行器**
   - 沙箱环境执行Python代码
   - 提供预定义的上下文变量
   - 结果格式化
   - 安全性控制

### 7.2. 权限控制

需要在API层面添加权限检查：
- 模型设计师/管理员：完整的CRUD权限
- 业务专家：查看和调整权重，但不能修改代码
- 其他角色：只读权限

### 7.3. 数据验证

增强数据验证逻辑：
- 节点类型的有效性检查
- 权重值的范围验证
- 脚本语法的基本检查
- 节点编码的命名规范

---

## 8. 测试建议

### 8.1. 单元测试

```python
# tests/test_model_versions.py
def test_create_model_version():
    """测试创建模型版本"""
    pass

def test_copy_model_version():
    """测试复制模型版本"""
    pass

def test_activate_model_version():
    """测试激活模型版本"""
    pass

# tests/test_model_nodes.py
def test_create_model_node():
    """测试创建模型节点"""
    pass

def test_delete_node_cascade():
    """测试级联删除"""
    pass

def test_load_tree_structure():
    """测试树状结构加载"""
    pass
```

### 8.2. 集成测试

1. 创建完整的模型结构（3层）
2. 复制版本并验证结构完整性
3. 更新节点并验证变更
4. 删除节点并验证级联删除
5. 激活版本并验证状态切换

---

## 9. 性能优化建议

### 9.1. 查询优化

- 使用 `joinedload` 预加载关联数据
- 添加适当的数据库索引
- 对大型树结构使用分页加载

### 9.2. 缓存策略

- 缓存激活版本的信息
- 缓存常用的节点树结构
- 使用Redis存储热点数据

---

## 10. 下一步工作

1. ✅ 模型版本管理 - 已完成
2. 🔄 维度目录管理 - 进行中
3. ⏳ 代码测试功能 - 待开始
4. ⏳ 前端界面开发 - 待开始
5. ⏳ 计算引擎集成 - 待开始

---

## 11. 相关文档

- [系统设计文档](./系统设计文档.md)
- [API设计文档](./API设计文档.md)
- [需求文档](./需求文档.md)
- [数据库设计](./系统设计文档.md#4-数据库设计)

---

**文档维护**: 请在功能更新时同步更新本文档
