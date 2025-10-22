# 医院科室业务价值评估工具 - API设计文档 V1.0

> **文档状态**: 草稿
> **创建日期**: 2025-10-21
> **版本**: 1.0

---

## 1. API概述

### 1.1. 基本信息
- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

### 1.2. 通用响应格式
所有API响应都遵循统一的格式：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

- `code`: 状态码，200表示成功，其他表示错误
- `message`: 响应消息
- `data`: 响应数据，具体结构根据API而定

### 1.3. 错误码说明
| 错误码 | 说明 |
|---|---|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 2. 用户与权限服务 API

### API汇总表

| 接口路径 | 方法 | 描述 | 权限要求 |
|---|---|---|---|
| `/auth/login` | POST | 用户登录获取访问令牌 | 无 |
| `/users` | GET | 获取用户列表 | 系统管理员 |
| `/users` | POST | 创建新用户 | 系统管理员 |
| `/users/{id}` | PUT | 更新用户信息 | 系统管理员 |
| `/roles` | GET | 获取角色列表 | 系统管理员 |
| `/roles` | POST | 创建新角色 | 系统管理员 |
| `/roles/{id}` | PUT | 更新角色信息 | 系统管理员 |

### 2.1. 用户认证

#### 2.1.1. 用户登录
- **接口**: `POST /auth/login`
- **描述**: 用户登录获取访问令牌

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**请求示例**:
```json
{
  "username": "admin",
  "password": "123456"
}
```

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| token | string | JWT访问令牌 |
| user | object | 用户信息 |
| user.id | integer | 用户ID |
| user.username | string | 用户名 |
| user.name | string | 用户姓名 |
| user.roles | array | 用户角色列表 |

**响应示例**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "name": "管理员",
      "roles": ["admin"]
    }
  }
}
```

### 2.2. 用户管理

#### 2.2.1. 获取用户列表
- **接口**: `GET /users`
- **描述**: 获取用户列表

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页数量，默认10 |
| keyword | string | 否 | 搜索关键词 |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| total | integer | 总数量 |
| items | array | 用户列表 |
| items[].id | integer | 用户ID |
| items[].username | string | 用户名 |
| items[].name | string | 用户姓名 |
| items[].email | string | 邮箱 |
| items[].status | string | 状态 |
| items[].created_at | string | 创建时间 |

#### 2.2.2. 创建用户
- **接口**: `POST /users`
- **描述**: 创建新用户

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| username | string | 是 | 用户名 |
| name | string | 是 | 用户姓名 |
| password | string | 是 | 密码 |
| email | string | 否 | 邮箱 |
| role_ids | array | 是 | 角色ID列表 |

#### 2.2.3. 更新用户
- **接口**: `PUT /users/{id}`
- **描述**: 更新用户信息

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| name | string | 否 | 用户姓名 |
| email | string | 否 | 邮箱 |
| password | string | 否 | 密码 |
| role_ids | array | 否 | 角色ID列表 |
| status | string | 否 | 状态 |

### 2.3. 角色管理

#### 2.3.1. 获取角色列表
- **接口**: `GET /roles`
- **描述**: 获取角色列表

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| id | integer | 角色ID |
| name | string | 角色名称 |
| code | string | 角色编码 |
| description | string | 角色描述 |
| permissions | array | 权限列表 |

#### 2.3.2. 创建角色
- **接口**: `POST /roles`
- **描述**: 创建新角色

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| name | string | 是 | 角色名称 |
| code | string | 是 | 角色编码 |
| description | string | 否 | 角色描述 |
| permission_ids | array | 是 | 权限ID列表 |

#### 2.3.3. 更新角色
- **接口**: `PUT /roles/{id}`
- **描述**: 更新角色信息

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| name | string | 否 | 角色名称 |
| description | string | 否 | 角色描述 |
| permission_ids | array | 否 | 权限ID列表 |

---

## 3. 模型管理服务 API

### API汇总表

| 接口路径 | 方法 | 描述 | 权限要求 |
|---|---|---|---|
| `/model-versions` | GET | 获取模型版本列表 | 模型设计师/管理员 |
| `/model-versions` | POST | 创建新模型版本 | 模型设计师/管理员 |
| `/model-versions/{id}/activate` | PUT | 激活指定模型版本 | 模型设计师/管理员 |
| `/model-nodes` | GET | 获取指定版本的模型结构 | 模型设计师/管理员 |
| `/model-nodes` | POST | 创建模型节点 | 模型设计师/管理员 |
| `/model-nodes/{id}` | PUT | 更新模型节点 | 模型设计师/管理员 |
| `/model-nodes/{id}` | DELETE | 删除模型节点 | 模型设计师/管理员 |
| `/model-nodes/{id}/test-code` | POST | 测试节点代码 | 模型设计师/管理员 |
| `/dimension-items` | GET | 获取维度的收费项目目录 | 模型设计师/管理员 |
| `/dimension-items` | POST | 为维度添加收费项目 | 模型设计师/管理员 |
| `/dimension-items/{id}` | DELETE | 删除维度关联的收费项目 | 模型设计师/管理员 |
| `/dimension-items/import` | POST | 批量导入维度目录 | 模型设计师/管理员 |

### 3.1. 模型版本管理

#### 3.1.1. 获取模型版本列表
- **接口**: `GET /model-versions`
- **描述**: 获取模型版本列表

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| id | integer | 版本ID |
| version | string | 版本号 |
| name | string | 版本名称 |
| description | string | 版本描述 |
| is_active | boolean | 是否激活 |
| created_at | string | 创建时间 |

#### 3.1.2. 创建模型版本
- **接口**: `POST /model-versions`
- **描述**: 创建新模型版本

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| version | string | 是 | 版本号 |
| name | string | 是 | 版本名称 |
| description | string | 否 | 版本描述 |
| base_version_id | integer | 否 | 基础版本ID（用于复制） |

#### 3.1.3. 激活模型版本
- **接口**: `PUT /model-versions/{id}/activate`
- **描述**: 激活指定模型版本

### 3.2. 模型结构管理

#### 3.2.1. 获取模型结构
- **接口**: `GET /model-nodes?version_id={id}`
- **描述**: 获取指定版本的模型结构

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| version_id | integer | 是 | 模型版本ID |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| id | integer | 节点ID |
| parent_id | integer | 父节点ID |
| name | string | 节点名称 |
| code | string | 节点编码 |
| node_type | string | 节点类型(sequence/dimension) |
| calc_type | string | 计算类型(statistical/calculational) |
| weight | number | 权重/单价 |
| business_guide | string | 业务导向 |
| script | string | SQL/Python脚本 |
| children | array | 子节点列表 |

#### 3.2.2. 创建模型节点
- **接口**: `POST /model-nodes`
- **描述**: 创建模型节点

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| version_id | integer | 是 | 模型版本ID |
| parent_id | integer | 否 | 父节点ID |
| name | string | 是 | 节点名称 |
| code | string | 是 | 节点编码 |
| node_type | string | 是 | 节点类型 |
| calc_type | string | 是 | 计算类型 |
| weight | number | 否 | 权重/单价 |
| business_guide | string | 否 | 业务导向 |
| script | string | 否 | SQL/Python脚本 |

#### 3.2.3. 更新模型节点
- **接口**: `PUT /model-nodes/{id}`
- **描述**: 更新模型节点

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| name | string | 否 | 节点名称 |
| code | string | 否 | 节点编码 |
| node_type | string | 否 | 节点类型 |
| calc_type | string | 否 | 计算类型 |
| weight | number | 否 | 权重/单价 |
| business_guide | string | 否 | 业务导向 |
| script | string | 否 | SQL/Python脚本 |

#### 3.2.4. 删除模型节点
- **接口**: `DELETE /model-nodes/{id}`
- **描述**: 删除模型节点

#### 3.2.5. 测试节点代码
- **接口**: `POST /model-nodes/{id}/test-code`
- **描述**: 测试节点代码

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| script | string | 是 | SQL/Python脚本 |
| test_params | object | 否 | 测试参数 |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| success | boolean | 是否成功 |
| result | object | 执行结果 |
| error | string | 错误信息 |

### 3.3. 维度目录管理

#### 3.3.1. 获取维度目录
- **接口**: `GET /dimension-items?dimension_id={id}`
- **描述**: 获取维度的收费项目目录

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| dimension_id | integer | 是 | 维度节点ID |
| keyword | string | 否 | 搜索关键词 |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| id | integer | 映射ID |
| dimension_id | integer | 维度节点ID |
| item_code | string | 收费项目编码 |
| item_name | string | 收费项目名称 |
| item_category | string | 收费项目分类 |

#### 3.3.2. 添加维度目录
- **接口**: `POST /dimension-items`
- **描述**: 为维度添加收费项目

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| dimension_id | integer | 是 | 维度节点ID |
| item_codes | array | 是 | 收费项目编码列表 |

#### 3.3.3. 删除维度目录
- **接口**: `DELETE /dimension-items/{id}`
- **描述**: 删除维度关联的收费项目

#### 3.3.4. 批量导入维度目录
- **接口**: `POST /dimension-items/import`
- **描述**: 批量导入维度目录

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| dimension_id | integer | 是 | 维度节点ID |
| file | file | 是 | Excel文件 |

---

## 4. 收费项目管理服务 API

### API汇总表

| 接口路径 | 方法 | 描述 | 权限要求 |
|---|---|---|---|
| `/charge-items` | GET | 获取收费项目列表 | 系统管理员/模型设计师 |
| `/charge-items` | POST | 创建新收费项目 | 系统管理员 |
| `/charge-items/{id}` | GET | 获取收费项目详情 | 系统管理员/模型设计师 |
| `/charge-items/{id}` | PUT | 更新收费项目信息 | 系统管理员 |
| `/charge-items/{id}` | DELETE | 删除收费项目 | 系统管理员 |
| `/charge-items/import` | POST | 批量导入收费项目 | 系统管理员 |
| `/charge-items/export` | POST | 导出收费项目 | 系统管理员/模型设计师 |

### 4.1. 收费项目管理

#### 4.1.1. 获取收费项目列表
- **接口**: `GET /charge-items`
- **描述**: 获取收费项目列表

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页数量，默认10 |
| keyword | string | 否 | 搜索关键词（项目编码/名称/分类） |
| item_category | string | 否 | 项目分类筛选 |
| sort_by | string | 否 | 排序字段，可选值：item_code(默认)、item_name、item_category、created_at |
| sort_order | string | 否 | 排序方向，可选值：asc(升序，默认)、desc(降序) |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| total | integer | 总数量 |
| items | array | 收费项目列表 |
| items[].id | integer | 项目ID |
| items[].item_code | string | 收费项目编码 |
| items[].item_name | string | 收费项目名称 |
| items[].item_category | string | 收费项目分类 |
| items[].unit_price | string | 单价 |
| items[].created_at | string | 创建时间 |
| items[].updated_at | string | 更新时间 |

#### 4.1.2. 创建收费项目
- **接口**: `POST /charge-items`
- **描述**: 创建新收费项目

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| item_code | string | 是 | 收费项目编码 |
| item_name | string | 是 | 收费项目名称 |
| item_category | string | 否 | 收费项目分类 |
| unit_price | string | 否 | 单价 |

**请求示例**:
```json
{
  "item_code": "CK001",
  "item_name": "血常规",
  "item_category": "检验",
  "unit_price": "25.00"
}
```

#### 4.1.3. 获取收费项目详情
- **接口**: `GET /charge-items/{id}`
- **描述**: 获取收费项目详情

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| id | integer | 项目ID |
| item_code | string | 收费项目编码 |
| item_name | string | 收费项目名称 |
| item_category | string | 收费项目分类 |
| unit_price | string | 单价 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

#### 4.1.4. 更新收费项目信息
- **接口**: `PUT /charge-items/{id}`
- **描述**: 更新收费项目信息

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| item_name | string | 否 | 收费项目名称 |
| item_category | string | 否 | 收费项目分类 |
| unit_price | string | 否 | 单价 |

**注意**: 收费项目编码（item_code）创建后不可修改

#### 4.1.5. 删除收费项目
- **接口**: `DELETE /charge-items/{id}`
- **描述**: 删除收费项目

**注意**: 如果收费项目已被维度目录引用，将无法删除

#### 4.1.6. 批量导入收费项目（异步）
- **接口**: `POST /charge-items/import`
- **描述**: 批量导入收费项目（支持异步模式和字段映射）

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| file | file | 是 | Excel文件（仅支持 .xlsx 格式） |
| mapping | string | 是 | 字段映射JSON字符串 |
| async_mode | boolean | 否 | 是否使用异步模式（默认 true） |

**字段映射格式**:
```json
{
  "项目编码": "item_code",
  "项目名称": "item_name",
  "分类": "item_category",
  "单价": "unit_price"
}
```

**响应数据（异步模式）**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| task_id | string | 任务ID，用于查询进度 |
| status | string | 任务状态（pending） |
| message | string | 提示信息 |

**响应示例（异步模式）**:
```json
{
  "task_id": "57764026-9db6-4b83-b65a-017ad6091275",
  "status": "pending",
  "message": "导入任务已提交，请使用 task_id 查询进度"
}
```

**响应数据（同步模式）**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| success_count | integer | 成功导入数量 |
| failed_count | integer | 失败数量 |
| failed_items | array | 失败的项目列表 |
| failed_items[].row | integer | 行号 |
| failed_items[].data | object | 原始数据 |
| failed_items[].reason | string | 失败原因 |

**响应示例（同步模式）**:
```json
{
  "success_count": 80,
  "failed_count": 2,
  "failed_items": [
    {
      "row": 5,
      "data": {"项目编码": "CK005", "项目名称": ""},
      "reason": "项目名称不能为空"
    },
    {
      "row": 10,
      "data": {"项目编码": "CK001", "项目名称": "重复项目"},
      "reason": "项目编码已存在"
    }
  ]
}
```

**注意事项**:
- 大数据量（> 1000 条）建议使用异步模式
- 异步模式需要 Redis 和 Celery Worker 正常运行
- 仅支持 `.xlsx` 格式，不支持旧的 `.xls` 格式

#### 4.1.6.1. 查询导入任务状态
- **接口**: `GET /charge-items/import/status/{task_id}`
- **描述**: 查询异步导入任务的状态和进度

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| task_id | string | 是 | 任务ID |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| state | string | 任务状态（PENDING/PROCESSING/SUCCESS/FAILURE） |
| status | string | 状态描述 |
| current | integer | 已处理数量（仅 PROCESSING 状态） |
| total | integer | 总数量（仅 PROCESSING 状态） |
| result | object | 导入结果（仅 SUCCESS 状态） |
| error | string | 错误信息（仅 FAILURE 状态） |

**响应示例（处理中）**:
```json
{
  "state": "PROCESSING",
  "status": "正在导入数据... (5000/10000)",
  "current": 5000,
  "total": 10000
}
```

**响应示例（完成）**:
```json
{
  "state": "SUCCESS",
  "status": "导入完成",
  "result": {
    "success_count": 9998,
    "failed_count": 2,
    "failed_items": [...]
  }
}
```

**响应示例（失败）**:
```json
{
  "state": "FAILURE",
  "status": "导入失败",
  "error": "数据库连接失败"
}
```

#### 4.1.7. 解析Excel文件
- **接口**: `POST /charge-items/parse`
- **描述**: 解析Excel文件，返回表头和预览数据

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| file | file | 是 | Excel文件 |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| headers | array | Excel表头列表 |
| preview_data | array | 预览数据（前10行） |
| total_rows | integer | 总行数 |
| suggested_mapping | object | 建议的字段映射 |

**响应示例**:
```json
{
  "headers": ["项目编码", "项目名称", "分类", "单价"],
  "preview_data": [
    ["CK001", "血常规", "检验", "25.00"],
    ["CK002", "尿常规", "检验", "15.00"]
  ],
  "total_rows": 100,
  "suggested_mapping": {
    "项目编码": "item_code",
    "项目名称": "item_name",
    "分类": "item_category",
    "单价": "unit_price"
  }
}
```

#### 4.1.8. 下载导入模板
- **接口**: `GET /charge-items/template`
- **描述**: 下载收费项目导入模板

**响应**: Excel文件流

#### 4.1.9. 导出收费项目
- **接口**: `POST /charge-items/export`
- **描述**: 导出收费项目为Excel文件

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| keyword | string | 否 | 搜索关键词 |
| item_category | string | 否 | 项目分类筛选 |

**响应**: Excel文件流

---

## 5. 科室管理服务 API

### API汇总表

| 接口路径 | 方法 | 描述 | 权限要求 |
|---|---|---|---|
| `/departments` | GET | 获取科室列表 | 系统管理员 |
| `/departments` | POST | 创建新科室 | 系统管理员 |
| `/departments/{id}` | GET | 获取科室详情 | 系统管理员 |
| `/departments/{id}` | PUT | 更新科室信息 | 系统管理员 |
| `/departments/{id}` | DELETE | 删除科室 | 系统管理员 |
| `/departments/{id}/toggle-evaluation` | PUT | 切换科室评估状态 | 系统管理员 |

### 5.1. 科室管理

#### 5.1.1. 获取科室列表
- **接口**: `GET /departments`
- **描述**: 获取科室列表

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页数量，默认10 |
| keyword | string | 否 | 搜索关键词 |
| is_active | boolean | 否 | 是否激活 |
| sort_by | string | 否 | 排序字段，可选值：sort_order(默认)、his_code、his_name、cost_center_code、cost_center_name、accounting_unit_code、accounting_unit_name、created_at |
| sort_order | string | 否 | 排序方向，可选值：asc(升序，默认)、desc(降序) |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| total | integer | 总数量 |
| items | array | 科室列表 |
| items[].id | integer | 科室ID |
| items[].sort_order | number | 排序序号（小数类型） |
| items[].his_code | string | HIS科室代码 |
| items[].his_name | string | HIS科室名称 |
| items[].cost_center_code | string | 成本中心代码 |
| items[].cost_center_name | string | 成本中心名称 |
| items[].accounting_unit_code | string | 核算单元代码 |
| items[].accounting_unit_name | string | 核算单元名称 |
| items[].is_active | boolean | 是否参与评估 |
| items[].created_at | string | 创建时间 |

#### 5.1.2. 创建科室
- **接口**: `POST /departments`
- **描述**: 创建新科室

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| his_code | string | 是 | HIS科室代码 |
| his_name | string | 是 | HIS科室名称 |
| sort_order | number | 否 | 排序序号，默认为当前最大序号+1 |
| cost_center_code | string | 否 | 成本中心代码 |
| cost_center_name | string | 否 | 成本中心名称 |
| accounting_unit_code | string | 否 | 核算单元代码 |
| accounting_unit_name | string | 否 | 核算单元名称 |
| is_active | boolean | 否 | 是否参与评估，默认true |

#### 5.1.3. 获取科室详情
- **接口**: `GET /departments/{id}`
- **描述**: 获取科室详情

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| id | integer | 科室ID |
| sort_order | number | 排序序号 |
| his_code | string | HIS科室代码 |
| his_name | string | HIS科室名称 |
| cost_center_code | string | 成本中心代码 |
| cost_center_name | string | 成本中心名称 |
| accounting_unit_code | string | 核算单元代码 |
| accounting_unit_name | string | 核算单元名称 |
| is_active | boolean | 是否参与评估 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

#### 5.1.4. 更新科室信息
- **接口**: `PUT /departments/{id}`
- **描述**: 更新科室信息

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| his_name | string | 否 | HIS科室名称 |
| sort_order | number | 否 | 排序序号 |
| cost_center_code | string | 否 | 成本中心代码 |
| cost_center_name | string | 否 | 成本中心名称 |
| accounting_unit_code | string | 否 | 核算单元代码 |
| accounting_unit_name | string | 否 | 核算单元名称 |

#### 5.1.5. 删除科室
- **接口**: `DELETE /departments/{id}`
- **描述**: 删除科室

#### 5.1.6. 切换科室评估状态
- **接口**: `PUT /departments/{id}/toggle-evaluation`
- **描述**: 切换科室评估状态

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| is_active | boolean | 更新后的评估状态 |

---

## 6. 计算引擎服务 API

### API汇总表

| 接口路径 | 方法 | 描述 | 权限要求 |
|---|---|---|---|
| `/calculation/tasks` | POST | 创建并启动计算任务 | 数据分析师/操作员 |
| `/calculation/tasks` | GET | 获取计算任务列表 | 数据分析师/操作员 |
| `/calculation/tasks/{id}/log` | GET | 获取任务日志 | 数据分析师/操作员 |
| `/calculation/tasks/{id}/cancel` | POST | 取消计算任务 | 数据分析师/操作员 |

### 6.1. 计算任务管理

#### 6.1.1. 创建计算任务
- **接口**: `POST /calculation/tasks`
- **描述**: 创建并启动计算任务

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| model_version_id | integer | 是 | 模型版本ID |
| department_ids | array | 否 | 科室ID列表，为空则计算所有科室 |
| period | string | 是 | 计算周期(YYYY-MM) |
| description | string | 否 | 任务描述 |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| task_id | string | 任务ID |
| status | string | 任务状态 |
| created_at | string | 创建时间 |

#### 6.1.2. 获取计算任务列表
- **接口**: `GET /calculation/tasks`
- **描述**: 获取计算任务列表

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页数量，默认10 |
| status | string | 否 | 任务状态筛选 |
| model_version_id | integer | 否 | 模型版本ID筛选 |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| total | integer | 总数量 |
| items | array | 任务列表 |
| items[].task_id | string | 任务ID |
| items[].model_version_name | string | 模型版本名称 |
| items[].period | string | 计算周期 |
| items[].status | string | 任务状态 |
| items[].progress | number | 进度百分比 |
| items[].created_at | string | 创建时间 |
| items[].started_at | string | 开始时间 |
| items[].completed_at | string | 完成时间 |
| items[].error_message | string | 错误信息 |

#### 6.1.3. 获取任务日志
- **接口**: `GET /calculation/tasks/{id}/log`
- **描述**: 获取任务日志

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| id | string | 是 | 任务ID |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| logs | array | 日志列表 |
| logs[].timestamp | string | 时间戳 |
| logs[].level | string | 日志级别 |
| logs[].message | string | 日志消息 |

#### 6.1.4. 取消计算任务
- **接口**: `POST /calculation/tasks/{id}/cancel`
- **描述**: 取消计算任务

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| id | string | 是 | 任务ID |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| success | boolean | 是否成功取消 |
| message | string | 消息 |

---

## 7. 结果与报表服务 API

### API汇总表

| 接口路径 | 方法 | 描述 | 权限要求 |
|---|---|---|---|
| `/results/summary` | GET | 获取科室汇总数据 | 所有用户 |
| `/results/detail` | GET | 获取科室详细业务价值数据 | 所有用户 |
| `/results/export/summary` | POST | 导出汇总表 | 数据分析师/操作员 |
| `/results/export/detail` | POST | 导出明细表 | 数据分析师/操作员 |
| `/results/export/{task_id}/download` | GET | 下载报表文件 | 数据分析师/操作员 |

### 7.1. 结果查询

#### 7.1.1. 获取科室汇总数据
- **接口**: `GET /results/summary`
- **描述**: 获取科室汇总数据

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| period | string | 是 | 评估月份(YYYY-MM) |
| model_version_id | integer | 否 | 模型版本ID，默认使用激活版本 |
| department_id | integer | 否 | 科室ID，为空则查询所有科室 |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| summary | object | 全院汇总数据 |
| summary.doctor_value | number | 医生价值 |
| summary.doctor_ratio | number | 医生占比 |
| summary.nurse_value | number | 护理价值 |
| summary.nurse_ratio | number | 护理占比 |
| summary.tech_value | number | 医技价值 |
| summary.tech_ratio | number | 医技占比 |
| summary.total_value | number | 科室总价值 |
| departments | array | 科室数据列表 |
| departments[].department_id | integer | 科室ID |
| departments[].department_name | string | 科室名称 |
| departments[].doctor_value | number | 医生价值 |
| departments[].doctor_ratio | number | 医生占比 |
| departments[].nurse_value | number | 护理价值 |
| departments[].nurse_ratio | number | 护理占比 |
| departments[].tech_value | number | 医技价值 |
| departments[].tech_ratio | number | 医技占比 |
| departments[].total_value | number | 科室总价值 |

#### 7.1.2. 获取科室详细业务价值数据
- **接口**: `GET /results/detail?dept_id={id}&task_id={id}`
- **描述**: 获取科室详细业务价值数据

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| dept_id | integer | 是 | 科室ID |
| task_id | string | 是 | 任务ID |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| department_info | object | 科室基本信息 |
| sequences | array | 序列数据列表 |
| sequences[].sequence_type | string | 序列类型(医生/护理/医技) |
| sequences[].total_value | number | 序列总价值 |
| sequences[].dimensions | array | 维度数据列表 |
| sequences[].dimensions[].dimension_name | string | 维度名称 |
| sequences[].dimensions[].dimension_code | string | 维度编码 |
| sequences[].dimensions[].value | number | 维度价值 |
| sequences[].dimensions[].ratio | number | 维度占比 |
| sequences[].dimensions[].items | array | 明细项目列表 |
| sequences[].dimensions[].items[].item_name | string | 项目名称 |
| sequences[].dimensions[].items[].item_code | string | 项目编码 |
| sequences[].dimensions[].items[].value | number | 项目价值 |
| sequences[].dimensions[].items[].quantity | number | 项目数量 |
| sequences[].dimensions[].items[].unit_price | number | 单价 |

### 7.2. 报表导出

#### 7.2.1. 导出汇总表
- **接口**: `POST /results/export/summary`
- **描述**: 导出汇总表

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| period | string | 是 | 评估月份(YYYY-MM) |
| model_version_id | integer | 否 | 模型版本ID |
| department_ids | array | 否 | 科室ID列表 |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| task_id | string | 导出任务ID |
| download_url | string | 下载链接（完成后） |

#### 7.2.2. 导出明细表
- **接口**: `POST /results/export/detail`
- **描述**: 导出明细表

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| task_id | string | 是 | 计算任务ID |
| department_ids | array | 否 | 科室ID列表 |

#### 7.2.3. 下载报表文件
- **接口**: `GET /results/export/{task_id}/download`
- **描述**: 下载报表文件

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| task_id | string | 是 | 导出任务ID |

**响应**: 文件流

---

## 8. 系统配置 API

### API汇总表

| 接口路径 | 方法 | 描述 | 权限要求 |
|---|---|---|---|
| `/system/settings` | GET | 获取系统设置 | 所有用户 |
| `/system/settings` | PUT | 更新系统设置 | 系统管理员 |

### 8.1. 系统设置

#### 8.1.1. 获取系统设置
- **接口**: `GET /system/settings`
- **描述**: 获取系统设置

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| current_period | string | 当期年月 |
| system_name | string | 系统名称 |
| version | string | 系统版本 |

#### 8.1.2. 更新系统设置
- **接口**: `PUT /system/settings`
- **描述**: 更新系统设置

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| current_period | string | 否 | 当期年月 |
| system_name | string | 否 | 系统名称 |

---

## 9. 附录

### 9.1. 数据字典

#### 9.1.1. 节点类型 (node_type)
| 值 | 说明 |
|---|---|
| sequence | 序列 |
| dimension | 维度 |

#### 9.1.2. 计算类型 (calc_type)
| 值 | 说明 |
|---|---|
| statistical | 统计型 |
| calculational | 计算型 |

#### 9.1.3. 任务状态 (task_status)
| 值 | 说明 |
|---|---|
| pending | 排队中 |
| running | 运行中 |
| completed | 已完成 |
| failed | 失败 |
| cancelled | 已取消 |

#### 9.1.4. 用户状态 (user_status)
| 值 | 说明 |
|---|---|
| active | 激活 |
| inactive | 未激活 |
| locked | 锁定 |

### 9.2. 认证说明

所有需要认证的API都需要在请求头中携带JWT Token：

```
Authorization: Bearer <token>
```

Token有效期为24小时，过期后需要重新登录获取。

### 9.3. 分页说明

列表接口支持分页，分页参数为：
- `page`: 页码，从1开始
- `size`: 每页数量，默认10，最大100

分页响应格式：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "items": []
  }
}