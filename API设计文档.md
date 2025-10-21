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

## 4. 科室管理服务 API

### API汇总表

| 接口路径 | 方法 | 描述 | 权限要求 |
|---|---|---|---|
| `/departments` | GET | 获取科室列表 | 系统管理员 |
| `/departments` | POST | 创建新科室 | 系统管理员 |
| `/departments/{id}` | GET | 获取科室详情 | 系统管理员 |
| `/departments/{id}` | PUT | 更新科室信息 | 系统管理员 |
| `/departments/{id}` | DELETE | 删除科室 | 系统管理员 |
| `/departments/{id}/toggle-evaluation` | PUT | 切换科室评估状态 | 系统管理员 |

### 4.1. 科室管理

#### 4.1.1. 获取科室列表
- **接口**: `GET /departments`
- **描述**: 获取科室列表

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页数量，默认10 |
| keyword | string | 否 | 搜索关键词 |
| is_active | boolean | 否 | 是否激活 |

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| total | integer | 总数量 |
| items | array | 科室列表 |
| items[].id | integer | 科室ID |
| items[].his_code | string | HIS科室代码 |
| items[].his_name | string | HIS科室名称 |
| items[].cost_center_code | string | 成本中心代码 |
| items[].cost_center_name | string | 成本中心名称 |
| items[].accounting_unit_code | string | 核算单元代码 |
| items[].accounting_unit_name | string | 核算单元名称 |
| items[].is_active | boolean | 是否参与评估 |
| items[].created_at | string | 创建时间 |

#### 4.1.2. 创建科室
- **接口**: `POST /departments`
- **描述**: 创建新科室

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| his_code | string | 是 | HIS科室代码 |
| his_name | string | 是 | HIS科室名称 |
| cost_center_code | string | 否 | 成本中心代码 |
| cost_center_name | string | 否 | 成本中心名称 |
| accounting_unit_code | string | 否 | 核算单元代码 |
| accounting_unit_name | string | 否 | 核算单元名称 |
| is_active | boolean | 否 | 是否参与评估，默认true |

#### 4.1.3. 获取科室详情
- **接口**: `GET /departments/{id}`
- **描述**: 获取科室详情

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| id | integer | 科室ID |
| his_code | string | HIS科室代码 |
| his_name | string | HIS科室名称 |
| cost_center_code | string | 成本中心代码 |
| cost_center_name | string | 成本中心名称 |
| accounting_unit_code | string | 核算单元代码 |
| accounting_unit_name | string | 核算单元名称 |
| is_active | boolean | 是否参与评估 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

#### 4.1.4. 更新科室信息
- **接口**: `PUT /departments/{id}`
- **描述**: 更新科室信息

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| his_name | string | 否 | HIS科室名称 |
| cost_center_code | string | 否 | 成本中心代码 |
| cost_center_name | string | 否 | 成本中心名称 |
| accounting_unit_code | string | 否 | 核算单元代码 |
| accounting_unit_name | string | 否 | 核算单元名称 |

#### 4.1.5. 删除科室
- **接口**: `DELETE /departments/{id}`
- **描述**: 删除科室

#### 4.1.6. 切换科室评估状态
- **接口**: `PUT /departments/{id}/toggle-evaluation`
- **描述**: 切换科室评估状态

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| is_active | boolean | 更新后的评估状态 |

---

## 5. 计算引擎服务 API

### API汇总表

| 接口路径 | 方法 | 描述 | 权限要求 |
|---|---|---|---|
| `/calculation/tasks` | POST | 创建并启动计算任务 | 数据分析师/操作员 |
| `/calculation/tasks` | GET | 获取计算任务列表 | 数据分析师/操作员 |
| `/calculation/tasks/{id}/log` | GET | 获取任务日志 | 数据分析师/操作员 |
| `/calculation/tasks/{id}/cancel` | POST | 取消计算任务 | 数据分析师/操作员 |

### 5.1. 计算任务管理

#### 5.1.1. 创建计算任务
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

#### 5.1.2. 获取计算任务列表
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

#### 5.1.3. 获取任务日志
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

#### 5.1.4. 取消计算任务
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

## 6. 结果与报表服务 API

### API汇总表

| 接口路径 | 方法 | 描述 | 权限要求 |
|---|---|---|---|
| `/results/summary` | GET | 获取科室汇总数据 | 所有用户 |
| `/results/detail` | GET | 获取科室详细业务价值数据 | 所有用户 |
| `/results/export/summary` | POST | 导出汇总表 | 数据分析师/操作员 |
| `/results/export/detail` | POST | 导出明细表 | 数据分析师/操作员 |
| `/results/export/{task_id}/download` | GET | 下载报表文件 | 数据分析师/操作员 |

### 6.1. 结果查询

#### 6.1.1. 获取科室汇总数据
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

#### 6.1.2. 获取科室详细业务价值数据
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

### 6.2. 报表导出

#### 6.2.1. 导出汇总表
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

#### 6.2.2. 导出明细表
- **接口**: `POST /results/export/detail`
- **描述**: 导出明细表

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| task_id | string | 是 | 计算任务ID |
| department_ids | array | 否 | 科室ID列表 |

#### 6.2.3. 下载报表文件
- **接口**: `GET /results/export/{task_id}/download`
- **描述**: 下载报表文件

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| task_id | string | 是 | 导出任务ID |

**响应**: 文件流

---

## 7. 系统配置 API

### API汇总表

| 接口路径 | 方法 | 描述 | 权限要求 |
|---|---|---|---|
| `/system/settings` | GET | 获取系统设置 | 所有用户 |
| `/system/settings` | PUT | 更新系统设置 | 系统管理员 |

### 7.1. 系统设置

#### 7.1.1. 获取系统设置
- **接口**: `GET /system/settings`
- **描述**: 获取系统设置

**响应数据**:
| 参数名 | 类型 | 说明 |
|---|---|---|
| current_period | string | 当期年月 |
| system_name | string | 系统名称 |
| version | string | 系统版本 |

#### 7.1.2. 更新系统设置
- **接口**: `PUT /system/settings`
- **描述**: 更新系统设置

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| current_period | string | 否 | 当期年月 |
| system_name | string | 否 | 系统名称 |

---

## 8. 附录

### 8.1. 数据字典

#### 8.1.1. 节点类型 (node_type)
| 值 | 说明 |
|---|---|
| sequence | 序列 |
| dimension | 维度 |

#### 8.1.2. 计算类型 (calc_type)
| 值 | 说明 |
|---|---|
| statistical | 统计型 |
| calculational | 计算型 |

#### 8.1.3. 任务状态 (task_status)
| 值 | 说明 |
|---|---|
| pending | 排队中 |
| running | 运行中 |
| completed | 已完成 |
| failed | 失败 |
| cancelled | 已取消 |

#### 8.1.4. 用户状态 (user_status)
| 值 | 说明 |
|---|---|
| active | 激活 |
| inactive | 未激活 |
| locked | 锁定 |

### 8.2. 认证说明

所有需要认证的API都需要在请求头中携带JWT Token：

```
Authorization: Bearer <token>
```

Token有效期为24小时，过期后需要重新登录获取。

### 8.3. 分页说明

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