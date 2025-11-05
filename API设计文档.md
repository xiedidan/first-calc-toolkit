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
| `/model-versions/importable` | GET | 获取可导入的模型版本列表 | 模型设计师/管理员 |
| `/model-versions/{id}/preview` | GET | 预览模型版本详情（用于导入） | 模型设计师/管理员 |
| `/model-versions/import` | POST | 导入模型版本 | 模型设计师/管理员 |
| `/model-versions/{id}/import-info` | GET | 获取模型版本导入信息 | 模型设计师/管理员 |
| `/model-nodes` | GET | 获取指定版本的模型结构 | 模型设计师/管理员 |
| `/model-nodes` | POST | 创建模型节点 | 模型设计师/管理员 |
| `/model-nodes/{id}` | PUT | 更新模型节点 | 模型设计师/管理员 |
| `/model-nodes/{id}` | DELETE | 删除模型节点 | 模型设计师/管理员 |
| `/model-nodes/{id}/test-code` | POST | 测试节点代码 | 模型设计师/管理员 |
| `/dimension-items` | GET | 获取维度的收费项目目录 | 模型设计师/管理员 |
| `/dimension-items` | POST | 为维度添加收费项目 | 模型设计师/管理员 |
| `/dimension-items/{id}` | DELETE | 删除维度关联的收费项目 | 模型设计师/管理员 |
| `/dimension-items/import` | POST | 批量导入维度目录 | 模型设计师/管理员 |
| `/dimension-items/smart-import/parse` | POST | 解析Excel文件（智能导入第一步） | 模型设计师/管理员 |
| `/dimension-items/smart-import/extract-values` | POST | 提取维度值（智能导入第二步） | 模型设计师/管理员 |
| `/dimension-items/smart-import/preview` | POST | 生成导入预览（智能导入第三步） | 模型设计师/管理员 |
| `/dimension-items/smart-import/execute` | POST | 执行导入 | 模型设计师/管理员 |

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

#### 3.1.4. 获取可导入的模型版本列表
- **接口**: `GET /model-versions/importable`
- **描述**: 获取可导入的模型版本列表（其他医疗机构的版本）

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| skip | integer | 否 | 跳过数量，默认0 |
| limit | integer | 否 | 每页数量，默认20 |
| search | string | 否 | 搜索关键词（版本号、名称、医疗机构名称） |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| total | integer | 总数量 |
| items | array | 版本列表 |
| items[].id | integer | 版本ID |
| items[].version | string | 版本号 |
| items[].name | string | 版本名称 |
| items[].description | string | 版本描述 |
| items[].hospital_id | integer | 所属医疗机构ID |
| items[].hospital_name | string | 所属医疗机构名称 |
| items[].created_at | string | 创建时间 |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 5,
    "items": [
      {
        "id": 10,
        "version": "v1.0",
        "name": "2025年标准版",
        "description": "2025年业务价值评估标准版本",
        "hospital_id": 2,
        "hospital_name": "某某医院",
        "created_at": "2025-10-20T10:00:00"
      }
    ]
  }
}
```

#### 3.1.5. 预览模型版本详情
- **接口**: `GET /model-versions/{id}/preview`
- **描述**: 预览模型版本详情（用于导入前查看）

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| id | integer | 是 | 版本ID |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| id | integer | 版本ID |
| version | string | 版本号 |
| name | string | 版本名称 |
| description | string | 版本描述 |
| hospital_name | string | 所属医疗机构名称 |
| node_count | integer | 模型节点数量 |
| workflow_count | integer | 计算流程数量 |
| step_count | integer | 计算步骤数量 |
| created_at | string | 创建时间 |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 10,
    "version": "v1.0",
    "name": "2025年标准版",
    "description": "2025年业务价值评估标准版本",
    "hospital_name": "某某医院",
    "node_count": 45,
    "workflow_count": 3,
    "step_count": 15,
    "created_at": "2025-10-20T10:00:00"
  }
}
```

#### 3.1.6. 导入模型版本
- **接口**: `POST /model-versions/import`
- **描述**: 导入模型版本

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| source_version_id | integer | 是 | 源版本ID |
| import_type | string | 是 | 导入类型（structure_only/with_workflows） |
| version | string | 是 | 新版本号 |
| name | string | 是 | 新版本名称 |
| description | string | 否 | 新版本描述 |

**请求示例**:
```json
{
  "source_version_id": 10,
  "import_type": "with_workflows",
  "version": "v1.0-imported",
  "name": "2025年标准版（导入）",
  "description": "从某某医院导入"
}
```

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| id | integer | 新版本ID |
| version | string | 新版本号 |
| name | string | 新版本名称 |
| statistics | object | 导入统计信息 |
| statistics.node_count | integer | 导入的节点数量 |
| statistics.workflow_count | integer | 导入的流程数量 |
| statistics.step_count | integer | 导入的步骤数量 |
| warnings | array | 警告信息列表 |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 15,
    "version": "v1.0-imported",
    "name": "2025年标准版（导入）",
    "statistics": {
      "node_count": 45,
      "workflow_count": 3,
      "step_count": 15
    },
    "warnings": [
      "计算步骤 '门诊工作量统计' 引用的数据源在目标医疗机构不存在，已设置为使用默认数据源"
    ]
  }
}
```

#### 3.1.7. 获取模型版本导入信息
- **接口**: `GET /model-versions/{id}/import-info`
- **描述**: 获取模型版本的导入信息

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| id | integer | 是 | 版本ID |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| is_imported | boolean | 是否为导入版本 |
| source_version | string | 源版本号（如果是导入版本） |
| source_hospital_name | string | 源医疗机构名称（如果是导入版本） |
| import_type | string | 导入类型（如果是导入版本） |
| import_time | string | 导入时间（如果是导入版本） |
| importer_name | string | 导入用户名（如果是导入版本） |

**响应示例（导入版本）**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "is_imported": true,
    "source_version": "v1.0",
    "source_hospital_name": "某某医院",
    "import_type": "with_workflows",
    "import_time": "2025-11-05T14:30:00",
    "importer_name": "admin"
  }
}
```

**响应示例（本地创建）**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "is_imported": false
  }
}
```

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

### 3.4. 维度目录智能导入

#### 3.4.1. 解析Excel文件（第一步：字段映射）
- **接口**: `POST /dimension-items/smart-import/parse`
- **描述**: 解析上传的Excel文件，返回列名和预览数据，用于字段映射

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| file | file | 是 | Excel文件 |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| session_id | string | 导入会话ID，用于后续步骤 |
| headers | array | Excel表头列表 |
| preview_data | array | 预览数据（前10行） |
| total_rows | integer | 总行数 |
| suggested_mapping | object | 建议的字段映射 |

**响应示例**:
```json
{
  "session_id": "import_session_123456",
  "headers": ["收费编码", "收费名称", "维度预案", "专家意见"],
  "preview_data": [
    ["CK001", "血常规", "检验项目", "4D"],
    ["SS002", "阑尾切除术", "甲级手术D", "4D"]
  ],
  "total_rows": 500,
  "suggested_mapping": {
    "item_code": "收费编码",
    "dimension_plan": "维度预案",
    "expert_opinion": "专家意见"
  }
}
```

#### 3.4.2. 提取维度值（第二步：维度值映射）
- **接口**: `POST /dimension-items/smart-import/extract-values`
- **描述**: 根据字段映射提取维度预案和专家意见的唯一值，并提供智能匹配建议

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| session_id | string | 是 | 导入会话ID |
| field_mapping | object | 是 | 字段映射关系 |
| field_mapping.item_code | string | 是 | 收费编码列名 |
| field_mapping.dimension_plan | string | 否 | 维度预案列名 |
| field_mapping.expert_opinion | string | 否 | 专家意见列名 |
| model_version_id | integer | 是 | 模型版本ID，用于获取系统维度列表 |

**请求示例**:
```json
{
  "session_id": "import_session_123456",
  "field_mapping": {
    "item_code": "收费编码",
    "dimension_plan": "维度预案",
    "expert_opinion": "专家意见"
  },
  "model_version_id": 1
}
```

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| unique_values | array | 唯一值列表 |
| unique_values[].value | string | 唯一值 |
| unique_values[].source | string | 来源（dimension_plan/expert_opinion） |
| unique_values[].count | integer | 出现次数 |
| unique_values[].suggested_dimensions | array | 建议的系统维度列表 |
| system_dimensions | array | 系统维度列表 |
| system_dimensions[].id | integer | 维度ID |
| system_dimensions[].name | string | 维度名称 |
| system_dimensions[].code | string | 维度编码 |
| system_dimensions[].full_path | string | 维度完整路径 |

**响应示例**:
```json
{
  "unique_values": [
    {
      "value": "4D",
      "source": "expert_opinion",
      "count": 120,
      "suggested_dimensions": [
        {"id": 10, "name": "甲级手术D", "code": "JJSSD", "full_path": "医生序列 > 门诊 > 甲级手术D"},
        {"id": 25, "name": "甲级手术D", "code": "JJSSD", "full_path": "医生序列 > 住院 > 甲级手术D"}
      ]
    },
    {
      "value": "检验项目",
      "source": "dimension_plan",
      "count": 80,
      "suggested_dimensions": [
        {"id": 45, "name": "检验", "code": "JY", "full_path": "医技序列 > 检验"}
      ]
    }
  ],
  "system_dimensions": [
    {"id": 10, "name": "甲级手术D", "code": "JJSSD", "full_path": "医生序列 > 门诊 > 甲级手术D"},
    {"id": 25, "name": "甲级手术D", "code": "JJSSD", "full_path": "医生序列 > 住院 > 甲级手术D"},
    {"id": 45, "name": "检验", "code": "JY", "full_path": "医技序列 > 检验"}
  ]
}
```

#### 3.4.3. 生成导入预览（第三步：预览与确认）
- **接口**: `POST /dimension-items/smart-import/preview`
- **描述**: 根据维度值映射生成导入预览数据

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| session_id | string | 是 | 导入会话ID |
| value_mapping | array | 是 | 维度值映射关系 |
| value_mapping[].value | string | 是 | 唯一值 |
| value_mapping[].source | string | 是 | 来源 |
| value_mapping[].dimension_ids | array | 是 | 目标维度ID列表 |

**请求示例**:
```json
{
  "session_id": "import_session_123456",
  "value_mapping": [
    {
      "value": "4D",
      "source": "expert_opinion",
      "dimension_ids": [10, 25]
    },
    {
      "value": "检验项目",
      "source": "dimension_plan",
      "dimension_ids": [45]
    }
  ]
}
```

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| preview_items | array | 预览数据列表 |
| preview_items[].item_code | string | 收费项目编码 |
| preview_items[].item_name | string | 收费项目名称 |
| preview_items[].dimension_id | integer | 目标维度ID |
| preview_items[].dimension_name | string | 目标维度名称 |
| preview_items[].dimension_path | string | 维度完整路径 |
| preview_items[].source | string | 来源（dimension_plan/expert_opinion） |
| preview_items[].source_value | string | 来源值 |
| preview_items[].status | string | 状态（ok/warning/error） |
| preview_items[].message | string | 提示信息 |
| statistics | object | 统计信息 |
| statistics.total | integer | 总数 |
| statistics.ok | integer | 正常数量 |
| statistics.warning | integer | 警告数量 |
| statistics.error | integer | 错误数量 |

**响应示例**:
```json
{
  "preview_items": [
    {
      "item_code": "SS002",
      "item_name": "阑尾切除术",
      "dimension_id": 10,
      "dimension_name": "甲级手术D",
      "dimension_path": "医生序列 > 门诊 > 甲级手术D",
      "source": "expert_opinion",
      "source_value": "4D",
      "status": "ok",
      "message": ""
    },
    {
      "item_code": "SS002",
      "item_name": "阑尾切除术",
      "dimension_id": 25,
      "dimension_name": "甲级手术D",
      "dimension_path": "医生序列 > 住院 > 甲级手术D",
      "source": "expert_opinion",
      "source_value": "4D",
      "status": "warning",
      "message": "该收费项目已存在于此维度中"
    },
    {
      "item_code": "CK999",
      "item_name": "",
      "dimension_id": 45,
      "dimension_name": "检验",
      "dimension_path": "医技序列 > 检验",
      "source": "dimension_plan",
      "source_value": "检验项目",
      "status": "warning",
      "message": "收费项目编码在系统中不存在"
    }
  ],
  "statistics": {
    "total": 500,
    "ok": 450,
    "warning": 48,
    "error": 2
  }
}
```

#### 3.4.4. 执行导入
- **接口**: `POST /dimension-items/smart-import/execute`
- **描述**: 执行批量导入操作

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| session_id | string | 是 | 导入会话ID |
| confirmed_items | array | 否 | 用户确认的导入项（如果为空则导入所有预览项） |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| success | boolean | 是否成功 |
| report | object | 导入报告 |
| report.success_count | integer | 成功导入数量 |
| report.skipped_count | integer | 跳过数量 |
| report.error_count | integer | 错误数量 |
| report.errors | array | 错误详情列表 |

**响应示例**:
```json
{
  "success": true,
  "report": {
    "success_count": 450,
    "skipped_count": 48,
    "error_count": 2,
    "errors": [
      {
        "item_code": "CK999",
        "dimension_id": 45,
        "reason": "收费项目编码在系统中不存在"
      }
    ]
  }
}
```

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

## 9. 数据源管理服务 API - 新增

### API汇总表

| 接口路径 | 方法 | 描述 | 权限要求 |
|---|---|---|---|
| `/data-sources` | GET | 获取数据源列表 | 系统管理员 |
| `/data-sources` | POST | 创建新数据源 | 系统管理员 |
| `/data-sources/{id}` | GET | 获取数据源详情 | 系统管理员 |
| `/data-sources/{id}` | PUT | 更新数据源信息 | 系统管理员 |
| `/data-sources/{id}` | DELETE | 删除数据源 | 系统管理员 |
| `/data-sources/{id}/test` | POST | 测试数据源连接 | 系统管理员 |
| `/data-sources/{id}/toggle` | PUT | 切换数据源启用状态 | 系统管理员 |
| `/data-sources/{id}/set-default` | PUT | 设置为默认数据源 | 系统管理员 |
| `/data-sources/{id}/pool-status` | GET | 获取连接池状态 | 系统管理员 |

### 9.1. 数据源管理

#### 9.1.1. 获取数据源列表
- **接口**: `GET /data-sources`
- **描述**: 获取数据源列表

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页数量，默认10 |
| keyword | string | 否 | 搜索关键词（数据源名称） |
| db_type | string | 否 | 数据库类型筛选 |
| is_enabled | boolean | 否 | 启用状态筛选 |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| total | integer | 总数量 |
| items | array | 数据源列表 |
| items[].id | integer | 数据源ID |
| items[].name | string | 数据源名称 |
| items[].db_type | string | 数据库类型 |
| items[].host | string | 主机地址 |
| items[].port | integer | 端口号 |
| items[].database_name | string | 数据库名称 |
| items[].username | string | 用户名 |
| items[].is_default | boolean | 是否默认 |
| items[].is_enabled | boolean | 是否启用 |
| items[].connection_status | string | 连接状态(online/offline/error) |
| items[].description | string | 描述 |
| items[].created_at | string | 创建时间 |
| items[].updated_at | string | 更新时间 |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 3,
    "items": [
      {
        "id": 1,
        "name": "HIS业务数据库",
        "db_type": "postgresql",
        "host": "192.168.1.100",
        "port": 5432,
        "database_name": "his_db",
        "username": "his_user",
        "is_default": true,
        "is_enabled": true,
        "connection_status": "online",
        "description": "医院HIS系统业务数据库",
        "created_at": "2025-10-27T10:00:00",
        "updated_at": "2025-10-27T10:00:00"
      }
    ]
  }
}
```

**注意**: 密码字段不在列表中返回

#### 9.1.2. 创建数据源
- **接口**: `POST /data-sources`
- **描述**: 创建新数据源

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| name | string | 是 | 数据源名称 |
| db_type | string | 是 | 数据库类型(postgresql/mysql/sqlserver/oracle) |
| host | string | 是 | 主机地址 |
| port | integer | 是 | 端口号 |
| database_name | string | 是 | 数据库名称 |
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |
| schema_name | string | 否 | Schema名称 |
| connection_params | object | 否 | 额外连接参数 |
| is_default | boolean | 否 | 是否默认，默认false |
| is_enabled | boolean | 否 | 是否启用，默认true |
| description | string | 否 | 描述 |
| pool_size_min | integer | 否 | 最小连接数，默认2 |
| pool_size_max | integer | 否 | 最大连接数，默认10 |
| pool_timeout | integer | 否 | 连接超时(秒)，默认30 |

**请求示例**:
```json
{
  "name": "HIS业务数据库",
  "db_type": "postgresql",
  "host": "192.168.1.100",
  "port": 5432,
  "database_name": "his_db",
  "username": "his_user",
  "password": "his_password_123",
  "schema_name": "public",
  "is_default": true,
  "is_enabled": true,
  "description": "医院HIS系统业务数据库",
  "pool_size_min": 2,
  "pool_size_max": 10,
  "pool_timeout": 30
}
```

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| id | integer | 数据源ID |
| name | string | 数据源名称 |
| db_type | string | 数据库类型 |
| created_at | string | 创建时间 |

#### 9.1.3. 获取数据源详情
- **接口**: `GET /data-sources/{id}`
- **描述**: 获取数据源详情

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| id | integer | 数据源ID |
| name | string | 数据源名称 |
| db_type | string | 数据库类型 |
| host | string | 主机地址 |
| port | integer | 端口号 |
| database_name | string | 数据库名称 |
| username | string | 用户名 |
| password | string | 密码（脱敏显示为***） |
| schema_name | string | Schema名称 |
| connection_params | object | 连接参数 |
| is_default | boolean | 是否默认 |
| is_enabled | boolean | 是否启用 |
| description | string | 描述 |
| pool_size_min | integer | 最小连接数 |
| pool_size_max | integer | 最大连接数 |
| pool_timeout | integer | 连接超时 |
| connection_status | string | 连接状态 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

#### 9.1.4. 更新数据源
- **接口**: `PUT /data-sources/{id}`
- **描述**: 更新数据源信息

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| name | string | 否 | 数据源名称 |
| host | string | 否 | 主机地址 |
| port | integer | 否 | 端口号 |
| database_name | string | 否 | 数据库名称 |
| username | string | 否 | 用户名 |
| password | string | 否 | 密码（如果不修改则不传） |
| schema_name | string | 否 | Schema名称 |
| connection_params | object | 否 | 连接参数 |
| description | string | 否 | 描述 |
| pool_size_min | integer | 否 | 最小连接数 |
| pool_size_max | integer | 否 | 最大连接数 |
| pool_timeout | integer | 否 | 连接超时 |

**注意**: 
- 数据库类型（db_type）创建后不可修改
- 更新配置后，系统会重新创建连接池

#### 9.1.5. 删除数据源
- **接口**: `DELETE /data-sources/{id}`
- **描述**: 删除数据源

**注意**: 
- 如果数据源被计算步骤引用，将无法删除
- 删除操作会关闭并清理该数据源的连接池

#### 9.1.6. 测试数据源连接
- **接口**: `POST /data-sources/{id}/test`
- **描述**: 测试数据源连接

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| success | boolean | 是否成功 |
| message | string | 测试结果消息 |
| duration_ms | integer | 连接耗时(毫秒) |
| error | string | 错误信息（失败时） |

**响应示例（成功）**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "success": true,
    "message": "连接成功",
    "duration_ms": 125
  }
}
```

**响应示例（失败）**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "success": false,
    "message": "连接失败",
    "duration_ms": 5000,
    "error": "连接超时: could not connect to server"
  }
}
```

#### 9.1.7. 切换数据源启用状态
- **接口**: `PUT /data-sources/{id}/toggle`
- **描述**: 切换数据源启用状态

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| is_enabled | boolean | 更新后的启用状态 |

**注意**: 
- 禁用数据源会关闭其连接池
- 启用数据源会重新创建连接池

#### 9.1.8. 设置为默认数据源
- **接口**: `PUT /data-sources/{id}/set-default`
- **描述**: 设置为默认数据源

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| success | boolean | 是否成功 |
| message | string | 消息 |

**注意**: 
- 设置新的默认数据源会自动取消原默认数据源的默认标记
- 只能有一个数据源标记为默认

#### 9.1.9. 获取连接池状态
- **接口**: `GET /data-sources/{id}/pool-status`
- **描述**: 获取数据源连接池状态

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| pool_size | integer | 连接池大小 |
| active_connections | integer | 活跃连接数 |
| idle_connections | integer | 空闲连接数 |
| waiting_requests | integer | 等待连接的请求数 |
| total_connections_created | integer | 累计创建的连接数 |
| total_connections_closed | integer | 累计关闭的连接数 |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "pool_size": 10,
    "active_connections": 3,
    "idle_connections": 7,
    "waiting_requests": 0,
    "total_connections_created": 15,
    "total_connections_closed": 5
  }
}
```

---

## 10. 附录

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

#### 9.1.5. 数据库类型 (db_type) - 新增
| 值 | 说明 |
|---|---|
| postgresql | PostgreSQL数据库 |
| mysql | MySQL数据库 |
| sqlserver | SQL Server数据库 |
| oracle | Oracle数据库 |

#### 9.1.6. 数据源连接状态 (connection_status) - 新增
| 值 | 说明 |
|---|---|
| online | 在线（连接正常） |
| offline | 离线（未启用或连接池未创建） |
| error | 错误（连接失败） |

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

-
--

## 8. 计算流程管理服务 API - 新增

### API汇总表

| 接口路径 | 方法 | 描述 | 权限要求 |
|---|---|---|---|
| `/calculation-workflows` | GET | 获取计算流程列表 | 模型设计师/管理员 |
| `/calculation-workflows` | POST | 创建新计算流程 | 模型设计师/管理员 |
| `/calculation-workflows/{id}` | GET | 获取计算流程详情 | 模型设计师/管理员 |
| `/calculation-workflows/{id}` | PUT | 更新计算流程信息 | 模型设计师/管理员 |
| `/calculation-workflows/{id}` | DELETE | 删除计算流程 | 模型设计师/管理员 |
| `/calculation-workflows/{id}/copy` | POST | 复制计算流程 | 模型设计师/管理员 |
| `/calculation-steps` | GET | 获取计算步骤列表 | 模型设计师/管理员 |
| `/calculation-steps` | POST | 创建新计算步骤 | 模型设计师/管理员 |
| `/calculation-steps/{id}` | GET | 获取计算步骤详情 | 模型设计师/管理员 |
| `/calculation-steps/{id}` | PUT | 更新计算步骤信息 | 模型设计师/管理员 |
| `/calculation-steps/{id}` | DELETE | 删除计算步骤 | 模型设计师/管理员 |
| `/calculation-steps/{id}/move-up` | POST | 上移计算步骤 | 模型设计师/管理员 |
| `/calculation-steps/{id}/move-down` | POST | 下移计算步骤 | 模型设计师/管理员 |
| `/calculation-steps/{id}/test` | POST | 测试计算步骤代码 | 模型设计师/管理员 |
| `/calculation-workflows/migrate` | POST | 执行数据迁移 | 系统管理员 |

### 8.1. 计算流程管理

#### 8.1.1. 获取计算流程列表
- **接口**: `GET /calculation-workflows`
- **描述**: 获取计算流程列表

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| version_id | integer | 否 | 模型版本ID筛选 |
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页数量，默认10 |
| keyword | string | 否 | 搜索关键词（流程名称） |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| total | integer | 总数量 |
| items | array | 计算流程列表 |
| items[].id | integer | 流程ID |
| items[].version_id | integer | 模型版本ID |
| items[].version_name | string | 模型版本名称 |
| items[].name | string | 流程名称 |
| items[].description | string | 流程描述 |
| items[].step_count | integer | 步骤数量 |
| items[].is_active | boolean | 是否启用 |
| items[].created_at | string | 创建时间 |
| items[].updated_at | string | 更新时间 |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 5,
    "items": [
      {
        "id": 1,
        "version_id": 1,
        "version_name": "2025年标准版-v1",
        "name": "默认计算流程",
        "description": "从模型节点迁移的默认计算流程",
        "step_count": 15,
        "is_active": true,
        "created_at": "2025-10-27T10:00:00",
        "updated_at": "2025-10-27T10:00:00"
      }
    ]
  }
}
```

#### 8.1.2. 创建计算流程
- **接口**: `POST /calculation-workflows`
- **描述**: 创建新计算流程

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| version_id | integer | 是 | 模型版本ID |
| name | string | 是 | 流程名称 |
| description | string | 否 | 流程描述 |
| is_active | boolean | 否 | 是否启用，默认true |

**请求示例**:
```json
{
  "version_id": 1,
  "name": "2025年Q1计算流程",
  "description": "针对2025年第一季度的计算流程",
  "is_active": true
}
```

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| id | integer | 流程ID |
| version_id | integer | 模型版本ID |
| name | string | 流程名称 |
| description | string | 流程描述 |
| is_active | boolean | 是否启用 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

#### 8.1.3. 获取计算流程详情
- **接口**: `GET /calculation-workflows/{id}`
- **描述**: 获取计算流程详情

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| id | integer | 流程ID |
| version_id | integer | 模型版本ID |
| version_name | string | 模型版本名称 |
| name | string | 流程名称 |
| description | string | 流程描述 |
| is_active | boolean | 是否启用 |
| step_count | integer | 步骤数量 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

#### 8.1.4. 更新计算流程
- **接口**: `PUT /calculation-workflows/{id}`
- **描述**: 更新计算流程信息

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| name | string | 否 | 流程名称 |
| description | string | 否 | 流程描述 |
| is_active | boolean | 否 | 是否启用 |

#### 8.1.5. 删除计算流程
- **接口**: `DELETE /calculation-workflows/{id}`
- **描述**: 删除计算流程（级联删除所有步骤）

**注意**: 删除操作不可恢复，请谨慎操作

#### 8.1.6. 复制计算流程
- **接口**: `POST /calculation-workflows/{id}/copy`
- **描述**: 复制计算流程（包括所有步骤）

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| name | string | 是 | 新流程名称 |
| description | string | 否 | 新流程描述 |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| id | integer | 新流程ID |
| name | string | 新流程名称 |
| step_count | integer | 复制的步骤数量 |

### 8.2. 计算步骤管理

#### 8.2.1. 获取计算步骤列表
- **接口**: `GET /calculation-steps?workflow_id={id}`
- **描述**: 获取指定流程的计算步骤列表

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| workflow_id | integer | 是 | 计算流程ID |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| total | integer | 总数量 |
| items | array | 计算步骤列表 |
| items[].id | integer | 步骤ID |
| items[].workflow_id | integer | 计算流程ID |
| items[].name | string | 步骤名称 |
| items[].description | string | 步骤描述 |
| items[].code_type | string | 代码类型(python/sql) |
| items[].code_content | string | 代码内容 |
| items[].data_source_id | integer | 数据源ID |
| items[].data_source_name | string | 数据源名称 |
| items[].sort_order | number | 执行顺序 |
| items[].is_enabled | boolean | 是否启用 |
| items[].created_at | string | 创建时间 |
| items[].updated_at | string | 更新时间 |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 3,
    "items": [
      {
        "id": 1,
        "workflow_id": 1,
        "name": "医生序列 > 门诊 > 甲级手术D",
        "description": "计算门诊甲级手术D的工作量",
        "code_type": "sql",
        "code_content": "SELECT department_id, SUM(amount) as total FROM ...",
        "data_source_id": 1,
        "data_source_name": "HIS业务数据库",
        "sort_order": 1.0,
        "is_enabled": true,
        "created_at": "2025-10-27T10:00:00",
        "updated_at": "2025-10-27T10:00:00"
      }
    ]
  }
}
```

#### 8.2.2. 创建计算步骤
- **接口**: `POST /calculation-steps`
- **描述**: 创建新计算步骤

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| workflow_id | integer | 是 | 计算流程ID |
| name | string | 是 | 步骤名称 |
| description | string | 否 | 步骤描述 |
| code_type | string | 是 | 代码类型(python/sql) |
| code_content | string | 是 | 代码内容 |
| data_source_id | integer | 否 | 数据源ID（SQL类型时使用，为空则使用默认数据源） |
| sort_order | number | 否 | 执行顺序，默认为最大值+1 |
| is_enabled | boolean | 否 | 是否启用，默认true |

**请求示例**:
```json
{
  "workflow_id": 1,
  "name": "计算门诊工作量",
  "description": "统计门诊的工作量数据",
  "code_type": "sql",
  "code_content": "SELECT department_id, COUNT(*) as count FROM outpatient WHERE date = '{current_year_month}' GROUP BY department_id",
  "data_source_id": 1,
  "is_enabled": true
}
```

**注意**: 
- 当 `code_type='sql'` 时，建议指定 `data_source_id`
- 如果未指定 `data_source_id`，系统将使用标记为默认的数据源
- 当 `code_type='python'` 时，`data_source_id` 可以为空

#### 8.2.3. 获取计算步骤详情
- **接口**: `GET /calculation-steps/{id}`
- **描述**: 获取计算步骤详情

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| id | integer | 步骤ID |
| workflow_id | integer | 计算流程ID |
| workflow_name | string | 计算流程名称 |
| name | string | 步骤名称 |
| description | string | 步骤描述 |
| code_type | string | 代码类型 |
| code_content | string | 代码内容 |
| data_source_id | integer | 数据源ID |
| data_source_name | string | 数据源名称 |
| sort_order | number | 执行顺序 |
| is_enabled | boolean | 是否启用 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

#### 8.2.4. 更新计算步骤
- **接口**: `PUT /calculation-steps/{id}`
- **描述**: 更新计算步骤信息

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| name | string | 否 | 步骤名称 |
| description | string | 否 | 步骤描述 |
| code_type | string | 否 | 代码类型 |
| data_source_id | integer | 否 | 数据源ID |
| code_content | string | 否 | 代码内容 |
| is_enabled | boolean | 否 | 是否启用 |

#### 8.2.5. 删除计算步骤
- **接口**: `DELETE /calculation-steps/{id}`
- **描述**: 删除计算步骤

#### 8.2.6. 上移计算步骤
- **接口**: `POST /calculation-steps/{id}/move-up`
- **描述**: 将计算步骤向上移动一位

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| success | boolean | 是否成功 |
| message | string | 消息 |

#### 8.2.7. 下移计算步骤
- **接口**: `POST /calculation-steps/{id}/move-down`
- **描述**: 将计算步骤向下移动一位

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| success | boolean | 是否成功 |
| message | string | 消息 |

#### 8.2.8. 测试计算步骤代码
- **接口**: `POST /calculation-steps/{id}/test`
- **描述**: 测试计算步骤代码

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| test_params | object | 否 | 测试参数 |
| test_params.current_year_month | string | 否 | 当期年月 |
| test_params.department_id | integer | 否 | 科室ID |
| test_params.department_code | string | 否 | 科室代码 |

**请求示例**:
```json
{
  "test_params": {
    "current_year_month": "2025-10",
    "department_id": 1,
    "department_code": "KS001"
  }
}
```

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| success | boolean | 是否成功 |
| duration_ms | integer | 执行耗时(毫秒) |
| result | object | 执行结果 |
| error | string | 错误信息 |

**响应示例（成功）**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "success": true,
    "duration_ms": 125,
    "result": {
      "rows": [
        {"department_id": 1, "count": 150},
        {"department_id": 2, "count": 200}
      ],
      "row_count": 2
    }
  }
}
```

**响应示例（失败）**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "success": false,
    "duration_ms": 50,
    "error": "SQL语法错误: near 'FORM': syntax error"
  }
}
```

### 8.3. 数据迁移

#### 8.3.1. 执行数据迁移
- **接口**: `POST /calculation-workflows/migrate`
- **描述**: 将模型节点中的代码迁移到计算流程

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| version_ids | array | 否 | 要迁移的模型版本ID列表，为空则迁移所有版本 |
| preview_only | boolean | 否 | 是否仅预览，不实际执行，默认false |

**请求示例**:
```json
{
  "version_ids": [1, 2],
  "preview_only": false
}
```

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| success | boolean | 是否成功 |
| report | object | 迁移报告 |
| report.total_versions | integer | 总版本数 |
| report.migrated_versions | integer | 已迁移版本数 |
| report.total_nodes | integer | 总节点数 |
| report.migrated_steps | integer | 已迁移步骤数 |
| report.skipped_nodes | integer | 跳过的节点数（无代码） |
| report.failed_nodes | integer | 失败的节点数 |
| report.details | array | 详细信息 |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "success": true,
    "report": {
      "total_versions": 2,
      "migrated_versions": 2,
      "total_nodes": 50,
      "migrated_steps": 30,
      "skipped_nodes": 20,
      "failed_nodes": 0,
      "details": [
        {
          "version_id": 1,
          "version_name": "2025年标准版-v1",
          "workflow_id": 1,
          "workflow_name": "2025年标准版-v1 - 默认计算流程",
          "migrated_steps": 15,
          "skipped_nodes": 10
        }
      ]
    }
  }
}
```

---

## 9. API变更说明 (V1.1)

### 9.1. 已弃用的API

#### 9.1.1. 模型节点代码相关
- **接口**: `POST /model-nodes/{id}/test-code`
- **状态**: 已弃用（Deprecated）
- **替代方案**: 使用 `POST /calculation-steps/{id}/test` 测试计算步骤代码
- **说明**: 模型节点不再包含代码字段，代码测试功能已迁移到计算步骤

### 9.2. 修改的API

#### 9.2.1. 创建计算任务
- **接口**: `POST /calculation/tasks`
- **变更**: 新增 `workflow_id` 参数（可选）
- **说明**: 
  - 如果指定 `workflow_id`，系统将执行该计算流程中的步骤
  - 如果未指定 `workflow_id`，系统将尝试使用模型节点中的代码（兼容模式）
  - 建议始终指定 `workflow_id`，兼容模式将在未来版本中移除

**新的请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| model_version_id | integer | 是 | 模型版本ID |
| workflow_id | integer | 否 | 计算流程ID（推荐） |
| department_ids | array | 否 | 科室ID列表 |
| period | string | 是 | 计算周期(YYYY-MM) |
| description | string | 否 | 任务描述 |

#### 9.2.2. 获取模型节点
- **接口**: `GET /model-nodes`
- **变更**: `script` 字段标记为已弃用
- **说明**: 
  - API继续返回 `script` 字段，但前端不应再使用
  - 未来版本可能移除该字段

### 9.3. 新增的API

#### 9.3.1. 计算流程管理
- `GET /calculation-workflows` - 获取计算流程列表
- `POST /calculation-workflows` - 创建计算流程
- `GET /calculation-workflows/{id}` - 获取计算流程详情
- `PUT /calculation-workflows/{id}` - 更新计算流程
- `DELETE /calculation-workflows/{id}` - 删除计算流程
- `POST /calculation-workflows/{id}/copy` - 复制计算流程

#### 9.3.2. 计算步骤管理
- `GET /calculation-steps` - 获取计算步骤列表
- `POST /calculation-steps` - 创建计算步骤
- `GET /calculation-steps/{id}` - 获取计算步骤详情
- `PUT /calculation-steps/{id}` - 更新计算步骤
- `DELETE /calculation-steps/{id}` - 删除计算步骤
- `POST /calculation-steps/{id}/move-up` - 上移计算步骤
- `POST /calculation-steps/{id}/move-down` - 下移计算步骤
- `POST /calculation-steps/{id}/test` - 测试计算步骤代码

#### 9.3.3. 数据迁移
- `POST /calculation-workflows/migrate` - 执行数据迁移

### 9.4. 兼容性说明

#### 9.4.1. 过渡期
- 过渡期为6个月（2025-10-27 至 2026-04-27）
- 过渡期内，系统同时支持新旧两种方式
- 建议客户端尽快迁移到新API

#### 9.4.2. 兼容模式
- 兼容模式可通过系统配置启用/禁用
- 默认启用兼容模式
- 完成数据迁移后，建议禁用兼容模式

#### 9.4.3. 移除计划
- 2026-04-27 之后的版本将移除兼容模式
- 2026-04-27 之后的版本将移除 `model_nodes.script` 字段
- 2026-04-27 之后的版本将移除已弃用的API
