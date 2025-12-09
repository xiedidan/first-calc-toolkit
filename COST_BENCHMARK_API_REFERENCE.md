# 成本基准管理API参考文档

## 基础信息

- **基础路径**: `/api/v1/cost-benchmarks`
- **认证**: 需要Bearer Token
- **多租户**: 需要 `X-Hospital-ID` 请求头

## API端点

### 1. 获取成本基准列表

```http
GET /api/v1/cost-benchmarks
```

**查询参数**:
- `page` (int, 可选): 页码，默认1
- `size` (int, 可选): 每页数量，默认20，最大1000
- `version_id` (int, 可选): 按模型版本ID筛选
- `department_code` (string, 可选): 按科室代码筛选
- `dimension_code` (string, 可选): 按维度代码筛选
- `keyword` (string, 可选): 搜索关键词（科室名称或维度名称）

**响应示例**:
```json
{
  "total": 10,
  "items": [
    {
      "id": 1,
      "hospital_id": 1,
      "department_code": "DEPT001",
      "department_name": "内科",
      "version_id": 12,
      "version_name": "2025年迭代版",
      "dimension_code": "DIM001",
      "dimension_name": "医疗服务",
      "benchmark_value": 1000.50,
      "created_at": "2025-11-27T10:00:00",
      "updated_at": "2025-11-27T10:00:00"
    }
  ]
}
```

### 2. 创建成本基准

```http
POST /api/v1/cost-benchmarks
```

**请求体**:
```json
{
  "department_code": "DEPT001",
  "department_name": "内科",
  "version_id": 12,
  "version_name": "2025年迭代版",
  "dimension_code": "DIM001",
  "dimension_name": "医疗服务",
  "benchmark_value": 1000.50
}
```

**验证规则**:
- 所有字段必填
- `benchmark_value` 必须大于0
- 科室+版本+维度组合在同一医疗机构内必须唯一
- `version_id` 必须引用存在的模型版本

**响应**: 创建的成本基准对象（同列表项格式）

**错误响应**:
- `404`: 模型版本不存在
- `400`: 基准值无效或唯一性冲突
- `422`: 数据验证失败

### 3. 获取成本基准详情

```http
GET /api/v1/cost-benchmarks/{benchmark_id}
```

**路径参数**:
- `benchmark_id` (int): 成本基准ID

**响应**: 成本基准对象（同列表项格式）

**错误响应**:
- `404`: 成本基准不存在或不属于当前医疗机构

### 4. 更新成本基准

```http
PUT /api/v1/cost-benchmarks/{benchmark_id}
```

**路径参数**:
- `benchmark_id` (int): 成本基准ID

**请求体** (所有字段可选):
```json
{
  "department_code": "DEPT002",
  "department_name": "外科",
  "version_id": 13,
  "version_name": "2025年迭代版V2",
  "dimension_code": "DIM002",
  "dimension_name": "护理服务",
  "benchmark_value": 2000.75
}
```

**验证规则**:
- 如果更新 `benchmark_value`，必须大于0
- 如果更新 `version_id`，新版本必须存在且属于当前医疗机构
- 更新后不能违反唯一性约束

**响应**: 更新后的成本基准对象

**错误响应**:
- `404`: 成本基准不存在、模型版本不存在，或不属于当前医疗机构
- `400`: 基准值无效或唯一性冲突
- `403`: 无权访问该数据

### 5. 删除成本基准

```http
DELETE /api/v1/cost-benchmarks/{benchmark_id}
```

**路径参数**:
- `benchmark_id` (int): 成本基准ID

**响应**:
```json
{
  "message": "成本基准删除成功"
}
```

**错误响应**:
- `404`: 成本基准不存在或不属于当前医疗机构
- `403`: 无权访问该数据

### 6. 导出成本基准到Excel

```http
GET /api/v1/cost-benchmarks/export
```

**查询参数** (与列表接口相同):
- `version_id` (int, 可选): 按模型版本ID筛选
- `department_code` (string, 可选): 按科室代码筛选
- `dimension_code` (string, 可选): 按维度代码筛选
- `keyword` (string, 可选): 搜索关键词

**响应**: Excel文件流

**文件格式**:
- 文件名: `成本基准_YYYYMMDD_HHMMSS.xlsx`
- 包含列: 科室代码、科室名称、模型版本名称、维度代码、维度名称、基准值、创建时间、更新时间

**错误响应**:
- `400`: 没有可导出的数据

## 使用示例

### Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your_access_token"
HOSPITAL_ID = 1

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-Hospital-ID": str(HOSPITAL_ID),
    "Content-Type": "application/json"
}

# 获取列表
response = requests.get(
    f"{BASE_URL}/cost-benchmarks",
    headers=headers,
    params={"page": 1, "size": 20, "keyword": "内科"}
)
print(response.json())

# 创建成本基准
data = {
    "department_code": "DEPT001",
    "department_name": "内科",
    "version_id": 12,
    "version_name": "2025年迭代版",
    "dimension_code": "DIM001",
    "dimension_name": "医疗服务",
    "benchmark_value": 1000.50
}
response = requests.post(
    f"{BASE_URL}/cost-benchmarks",
    headers=headers,
    json=data
)
print(response.json())

# 导出Excel
response = requests.get(
    f"{BASE_URL}/cost-benchmarks/export",
    headers=headers
)
with open("cost_benchmarks.xlsx", "wb") as f:
    f.write(response.content)
```

### JavaScript (fetch)

```javascript
const BASE_URL = "http://localhost:8000/api/v1";
const TOKEN = "your_access_token";
const HOSPITAL_ID = 1;

const headers = {
    "Authorization": `Bearer ${TOKEN}`,
    "X-Hospital-ID": HOSPITAL_ID.toString(),
    "Content-Type": "application/json"
};

// 获取列表
fetch(`${BASE_URL}/cost-benchmarks?page=1&size=20`, {
    headers: headers
})
.then(response => response.json())
.then(data => console.log(data));

// 创建成本基准
const data = {
    department_code: "DEPT001",
    department_name: "内科",
    version_id: 12,
    version_name: "2025年迭代版",
    dimension_code: "DIM001",
    dimension_name: "医疗服务",
    benchmark_value: 1000.50
};

fetch(`${BASE_URL}/cost-benchmarks`, {
    method: "POST",
    headers: headers,
    body: JSON.stringify(data)
})
.then(response => response.json())
.then(data => console.log(data));

// 导出Excel
fetch(`${BASE_URL}/cost-benchmarks/export`, {
    headers: headers
})
.then(response => response.blob())
.then(blob => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cost_benchmarks.xlsx';
    a.click();
});
```

## 多租户隔离说明

所有API端点都实现了严格的多租户数据隔离：

1. **查询隔离**: 只返回当前医疗机构的数据
2. **创建隔离**: 自动关联当前医疗机构ID
3. **更新隔离**: 只能更新当前医疗机构的数据
4. **删除隔离**: 只能删除当前医疗机构的数据
5. **跨租户访问**: 尝试访问其他医疗机构的数据会返回404（不暴露数据存在性）

## 数据验证规则

### 字段验证
- `department_code`: 1-50字符，不能为空
- `department_name`: 1-100字符，不能为空
- `version_id`: 必须大于0，必须引用存在的模型版本
- `version_name`: 1-100字符，不能为空
- `dimension_code`: 1-100字符，不能为空
- `dimension_name`: 1-200字符，不能为空
- `benchmark_value`: 必须大于0，自动格式化为2位小数

### 业务规则
- 唯一性约束: 同一医疗机构内，科室代码+版本ID+维度代码组合必须唯一
- 外键约束: version_id必须引用存在的模型版本
- 多租户约束: 所有操作都限制在当前医疗机构范围内

## 错误码说明

- `200 OK`: 请求成功
- `400 Bad Request`: 业务逻辑错误（唯一性冲突、基准值无效、没有可导出数据等）
- `403 Forbidden`: 无权访问该资源（跨租户访问）
- `404 Not Found`: 资源不存在或不属于当前医疗机构
- `422 Unprocessable Entity`: 数据验证失败（字段格式错误、缺少必填字段等）
- `500 Internal Server Error`: 服务器内部错误

## 性能建议

1. **分页查询**: 使用合理的 `size` 参数，避免一次加载过多数据
2. **筛选优化**: 使用具体的筛选条件（version_id、department_code等）而不是仅依赖关键词搜索
3. **导出限制**: 导出大量数据时可能需要较长时间，建议使用筛选条件限制导出范围
