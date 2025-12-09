# 成本基准管理 API 文档

## 概述

成本基准管理功能提供了一套完整的 RESTful API，用于管理医院科室在不同模型版本下各维度的成本基准值。该功能支持多租户隔离，确保不同医疗机构的数据完全独立。

**基础路径**: `/api/v1/cost-benchmarks`

**认证方式**: JWT Token（通过 `Authorization: Bearer <token>` 请求头传递）

**多租户**: 通过 `X-Hospital-ID` 请求头传递当前医疗机构ID

## 数据模型

### CostBenchmark（成本基准）

```typescript
interface CostBenchmark {
  id: number                    // 主键ID
  hospital_id: number           // 所属医疗机构ID
  department_code: string       // 科室代码（最大50字符）
  department_name: string       // 科室名称（最大100字符）
  version_id: number            // 模型版本ID
  version_name: string          // 模型版本名称（最大100字符）
  dimension_code: string        // 维度代码（最大100字符）
  dimension_name: string        // 维度名称（最大200字符）
  benchmark_value: number       // 基准值（Decimal(15,2)，必须>0）
  created_at: string            // 创建时间（ISO 8601格式）
  updated_at: string            // 更新时间（ISO 8601格式）
}
```

### 约束条件

- **唯一性约束**: 同一医疗机构内，`(hospital_id, department_code, version_id, dimension_code)` 组合必须唯一
- **外键约束**: 
  - `hospital_id` 引用 `hospitals.id`（级联删除）
  - `version_id` 引用 `model_versions.id`（级联删除）
- **数值约束**: `benchmark_value` 必须大于 0，最大值为 999999999.99

## API 端点

### 1. 获取成本基准列表

获取当前医疗机构的成本基准列表，支持分页、筛选和搜索。

**请求**

```http
GET /api/v1/cost-benchmarks
```

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认1，最小1 |
| size | integer | 否 | 每页数量，默认20，范围1-1000 |
| version_id | integer | 否 | 按模型版本ID筛选 |
| department_code | string | 否 | 按科室代码筛选 |
| dimension_code | string | 否 | 按维度代码筛选 |
| keyword | string | 否 | 搜索关键词（在科室名称和维度名称中模糊匹配） |

**响应**

```json
{
  "total": 100,
  "items": [
    {
      "id": 1,
      "hospital_id": 1,
      "department_code": "001",
      "department_name": "内科",
      "version_id": 1,
      "version_name": "2024年度模型",
      "dimension_code": "D001",
      "dimension_name": "门诊工作量",
      "benchmark_value": 50000.00,
      "created_at": "2024-01-01T10:00:00",
      "updated_at": "2024-01-01T10:00:00"
    }
  ]
}
```

**状态码**

- `200 OK`: 成功
- `401 Unauthorized`: 未认证
- `403 Forbidden`: 未激活医疗机构
- `500 Internal Server Error`: 服务器错误

---

### 2. 创建成本基准

创建新的成本基准记录。

**请求**

```http
POST /api/v1/cost-benchmarks
Content-Type: application/json
```

**请求体**

```json
{
  "department_code": "001",
  "department_name": "内科",
  "version_id": 1,
  "version_name": "2024年度模型",
  "dimension_code": "D001",
  "dimension_name": "门诊工作量",
  "benchmark_value": 50000.00
}
```

**字段说明**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| department_code | string | 是 | 科室代码，1-50字符 |
| department_name | string | 是 | 科室名称，1-100字符 |
| version_id | integer | 是 | 模型版本ID，必须>0 |
| version_name | string | 是 | 模型版本名称，1-100字符 |
| dimension_code | string | 是 | 维度代码，1-100字符 |
| dimension_name | string | 是 | 维度名称，1-200字符 |
| benchmark_value | number | 是 | 基准值，必须>0，最大999999999.99 |

**响应**

```json
{
  "id": 1,
  "hospital_id": 1,
  "department_code": "001",
  "department_name": "内科",
  "version_id": 1,
  "version_name": "2024年度模型",
  "dimension_code": "D001",
  "dimension_name": "门诊工作量",
  "benchmark_value": 50000.00,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

**状态码**

- `200 OK`: 创建成功
- `400 Bad Request`: 参数错误或违反唯一性约束
- `401 Unauthorized`: 未认证
- `403 Forbidden`: 未激活医疗机构
- `404 Not Found`: 模型版本不存在
- `500 Internal Server Error`: 服务器错误

**错误示例**

```json
{
  "detail": "该科室（内科）在模型版本（2024年度模型）下的维度（门诊工作量）成本基准已存在"
}
```

---

### 3. 获取成本基准详情

获取指定成本基准的详细信息。

**请求**

```http
GET /api/v1/cost-benchmarks/{benchmark_id}
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| benchmark_id | integer | 成本基准ID |

**响应**

```json
{
  "id": 1,
  "hospital_id": 1,
  "department_code": "001",
  "department_name": "内科",
  "version_id": 1,
  "version_name": "2024年度模型",
  "dimension_code": "D001",
  "dimension_name": "门诊工作量",
  "benchmark_value": 50000.00,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

**状态码**

- `200 OK`: 成功
- `401 Unauthorized`: 未认证
- `403 Forbidden`: 未激活医疗机构或无权访问
- `404 Not Found`: 成本基准不存在
- `500 Internal Server Error`: 服务器错误

---

### 4. 更新成本基准

更新指定成本基准的信息。

**请求**

```http
PUT /api/v1/cost-benchmarks/{benchmark_id}
Content-Type: application/json
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| benchmark_id | integer | 成本基准ID |

**请求体**

所有字段均为可选，只需传递需要更新的字段：

```json
{
  "department_code": "002",
  "department_name": "外科",
  "version_id": 2,
  "version_name": "2025年度模型",
  "dimension_code": "D002",
  "dimension_name": "住院工作量",
  "benchmark_value": 60000.00
}
```

**响应**

```json
{
  "id": 1,
  "hospital_id": 1,
  "department_code": "002",
  "department_name": "外科",
  "version_id": 2,
  "version_name": "2025年度模型",
  "dimension_code": "D002",
  "dimension_name": "住院工作量",
  "benchmark_value": 60000.00,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-02T15:30:00"
}
```

**状态码**

- `200 OK`: 更新成功
- `400 Bad Request`: 参数错误或违反唯一性约束
- `401 Unauthorized`: 未认证
- `403 Forbidden`: 未激活医疗机构或无权访问
- `404 Not Found`: 成本基准或模型版本不存在
- `500 Internal Server Error`: 服务器错误

---

### 5. 删除成本基准

删除指定的成本基准记录。

**请求**

```http
DELETE /api/v1/cost-benchmarks/{benchmark_id}
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| benchmark_id | integer | 成本基准ID |

**响应**

```json
{
  "message": "成本基准删除成功"
}
```

**状态码**

- `200 OK`: 删除成功
- `401 Unauthorized`: 未认证
- `403 Forbidden`: 未激活医疗机构或无权访问
- `404 Not Found`: 成本基准不存在
- `500 Internal Server Error`: 服务器错误

---

### 6. 导出成本基准到Excel

导出当前筛选条件下的所有成本基准数据到Excel文件。

**请求**

```http
GET /api/v1/cost-benchmarks/export
```

**查询参数**

与列表接口相同的筛选参数（不包括分页参数）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| version_id | integer | 否 | 按模型版本ID筛选 |
| department_code | string | 否 | 按科室代码筛选 |
| dimension_code | string | 否 | 按维度代码筛选 |
| keyword | string | 否 | 搜索关键词 |

**响应**

返回Excel文件流（`.xlsx`格式）

**响应头**

```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename*=UTF-8''成本基准_20240101_120000.xlsx
```

**Excel文件结构**

| 列名 | 说明 |
|------|------|
| 科室代码 | department_code |
| 科室名称 | department_name |
| 模型版本名称 | version_name |
| 维度代码 | dimension_code |
| 维度名称 | dimension_name |
| 基准值 | benchmark_value（格式化为2位小数） |
| 创建时间 | created_at（格式：YYYY-MM-DD HH:MM:SS） |
| 更新时间 | updated_at（格式：YYYY-MM-DD HH:MM:SS） |

**状态码**

- `200 OK`: 导出成功
- `400 Bad Request`: 没有可导出的数据
- `401 Unauthorized`: 未认证
- `403 Forbidden`: 未激活医疗机构
- `500 Internal Server Error`: 服务器错误

---

## 错误处理

### 错误响应格式

所有错误响应遵循统一格式：

```json
{
  "detail": "错误描述信息"
}
```

### 常见错误码

| 状态码 | 说明 | 示例 |
|--------|------|------|
| 400 | 请求参数错误 | 基准值必须大于0 |
| 401 | 未认证 | 未提供有效的认证令牌 |
| 403 | 无权访问 | 未激活医疗机构或访问其他机构数据 |
| 404 | 资源不存在 | 成本基准不存在或模型版本不存在 |
| 500 | 服务器内部错误 | 数据库连接失败 |

### 唯一性约束错误

当创建或更新操作违反唯一性约束时，返回详细的错误信息：

```json
{
  "detail": "该科室（内科）在模型版本（2024年度模型）下的维度（门诊工作量）成本基准已存在"
}
```

### 数值验证错误

```json
{
  "detail": "基准值必须大于0"
}
```

```json
{
  "detail": "基准值不能超过999999999.99"
}
```

---

## 使用示例

### Python 示例

```python
import requests

# 配置
BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your_jwt_token"
HOSPITAL_ID = 1

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-Hospital-ID": str(HOSPITAL_ID),
    "Content-Type": "application/json"
}

# 1. 获取成本基准列表
response = requests.get(
    f"{BASE_URL}/cost-benchmarks",
    headers=headers,
    params={"page": 1, "size": 20, "keyword": "内科"}
)
print(response.json())

# 2. 创建成本基准
data = {
    "department_code": "001",
    "department_name": "内科",
    "version_id": 1,
    "version_name": "2024年度模型",
    "dimension_code": "D001",
    "dimension_name": "门诊工作量",
    "benchmark_value": 50000.00
}
response = requests.post(
    f"{BASE_URL}/cost-benchmarks",
    headers=headers,
    json=data
)
print(response.json())

# 3. 更新成本基准
benchmark_id = 1
update_data = {"benchmark_value": 60000.00}
response = requests.put(
    f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
    headers=headers,
    json=update_data
)
print(response.json())

# 4. 删除成本基准
response = requests.delete(
    f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
    headers=headers
)
print(response.json())

# 5. 导出Excel
response = requests.get(
    f"{BASE_URL}/cost-benchmarks/export",
    headers=headers,
    params={"version_id": 1}
)
with open("成本基准.xlsx", "wb") as f:
    f.write(response.content)
```

### JavaScript/TypeScript 示例

```typescript
import axios from 'axios';

const BASE_URL = 'http://localhost:8000/api/v1';
const TOKEN = 'your_jwt_token';
const HOSPITAL_ID = 1;

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Authorization': `Bearer ${TOKEN}`,
    'X-Hospital-ID': HOSPITAL_ID.toString()
  }
});

// 1. 获取成本基准列表
const getCostBenchmarks = async () => {
  const response = await api.get('/cost-benchmarks', {
    params: { page: 1, size: 20, keyword: '内科' }
  });
  return response.data;
};

// 2. 创建成本基准
const createCostBenchmark = async () => {
  const data = {
    department_code: '001',
    department_name: '内科',
    version_id: 1,
    version_name: '2024年度模型',
    dimension_code: 'D001',
    dimension_name: '门诊工作量',
    benchmark_value: 50000.00
  };
  const response = await api.post('/cost-benchmarks', data);
  return response.data;
};

// 3. 更新成本基准
const updateCostBenchmark = async (id: number) => {
  const data = { benchmark_value: 60000.00 };
  const response = await api.put(`/cost-benchmarks/${id}`, data);
  return response.data;
};

// 4. 删除成本基准
const deleteCostBenchmark = async (id: number) => {
  const response = await api.delete(`/cost-benchmarks/${id}`);
  return response.data;
};

// 5. 导出Excel
const exportCostBenchmarks = async () => {
  const response = await api.get('/cost-benchmarks/export', {
    params: { version_id: 1 },
    responseType: 'blob'
  });
  
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.download = '成本基准.xlsx';
  link.click();
  window.URL.revokeObjectURL(url);
};
```

---

## 多租户隔离

### 工作原理

1. **请求头验证**: 所有请求必须包含 `X-Hospital-ID` 请求头
2. **自动过滤**: 查询操作自动过滤当前医疗机构的数据
3. **自动关联**: 创建操作自动关联当前医疗机构ID
4. **权限验证**: 更新/删除操作验证数据所属权

### 安全保证

- 用户无法查询其他医疗机构的数据
- 用户无法修改或删除其他医疗机构的数据
- 唯一性约束在医疗机构级别生效
- 外键引用验证确保关联数据属于同一医疗机构

---

## 性能优化

### 数据库索引

以下字段已建立索引以优化查询性能：

- `hospital_id`: 多租户过滤
- `department_code`: 科室筛选
- `version_id`: 版本筛选
- `dimension_code`: 维度筛选
- 复合唯一索引: `(hospital_id, department_code, version_id, dimension_code)`

### 分页建议

- 默认每页20条记录
- 建议每页不超过100条记录
- 大数据量导出使用导出接口而非列表接口

### 缓存策略

- 模型版本、科室、维度等基础数据可在前端缓存
- 成本基准数据建议实时查询以确保数据一致性

---

## 版本历史

### v1.0.0 (2024-11-27)

- 初始版本发布
- 支持成本基准的CRUD操作
- 支持多条件筛选和搜索
- 支持Excel导出
- 实现多租户数据隔离

---

## 技术支持

如有问题或建议，请联系技术支持团队。
