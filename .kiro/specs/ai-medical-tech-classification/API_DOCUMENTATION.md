# 医技智能分类分级 - API文档

## AI配置API

### 获取AI配置
```http
GET /api/v1/ai-config
```

**响应示例**
```json
{
  "id": 1,
  "hospital_id": 1,
  "api_endpoint": "https://api.deepseek.com/v1",
  "api_key_masked": "****abcd",
  "prompt_template": "请分类：{item_name}\n维度：{dimensions}",
  "call_delay": 1.0,
  "daily_limit": 10000,
  "batch_size": 100
}
```

### 创建/更新AI配置
```http
POST /api/v1/ai-config
```

**请求体**
```json
{
  "api_endpoint": "https://api.deepseek.com/v1",
  "api_key": "sk-xxxxxxxxxxxxx",
  "prompt_template": "请分类：{item_name}\n维度：{dimensions}",
  "call_delay": 1.0,
  "daily_limit": 10000,
  "batch_size": 100
}
```

### 测试AI配置
```http
POST /api/v1/ai-config/test
```

**请求体**
```json
{
  "api_endpoint": "https://api.deepseek.com/v1",
  "api_key": "sk-xxxxxxxxxxxxx",
  "prompt_template": "测试提示词"
}
```

### 获取使用统计
```http
GET /api/v1/ai-config/usage-stats
```

**响应示例**
```json
{
  "today_calls": 150,
  "today_limit": 10000,
  "estimated_cost": 0.75
}
```

## 分类任务API

### 获取任务列表
```http
GET /api/v1/classification-tasks?page=1&size=10
```

**响应示例**
```json
{
  "items": [
    {
      "id": 1,
      "task_name": "2024年医技分类",
      "model_version_id": 1,
      "charge_categories": ["检查费", "化验费"],
      "status": "completed",
      "total_items": 100,
      "processed_items": 100,
      "failed_items": 0,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10
}
```

### 创建分类任务
```http
POST /api/v1/classification-tasks
```

**请求体**
```json
{
  "task_name": "2024年医技分类",
  "model_version_id": 1,
  "charge_categories": ["检查费", "化验费"]
}
```

### 获取任务详情
```http
GET /api/v1/classification-tasks/{id}
```

### 删除任务
```http
DELETE /api/v1/classification-tasks/{id}
```

### 继续处理任务
```http
POST /api/v1/classification-tasks/{id}/continue
```

### 获取实时进度
```http
GET /api/v1/classification-tasks/{id}/progress
```

**响应示例**
```json
{
  "total_items": 100,
  "processed_items": 50,
  "failed_items": 2,
  "status": "processing"
}
```

### 获取处理日志
```http
GET /api/v1/classification-tasks/{id}/logs?page=1&size=20
```

## 分类预案API

### 获取预案列表
```http
GET /api/v1/classification-plans?page=1&size=10
```

**响应示例**
```json
{
  "items": [
    {
      "id": 1,
      "task_id": 1,
      "plan_name": "医技分类预案V1",
      "status": "draft",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

### 获取预案详情
```http
GET /api/v1/classification-plans/{id}
```

### 更新预案
```http
PUT /api/v1/classification-plans/{id}
```

**请求体**
```json
{
  "plan_name": "医技分类预案V2",
  "status": "draft"
}
```

### 删除预案
```http
DELETE /api/v1/classification-plans/{id}
```

### 获取预案项目列表
```http
GET /api/v1/classification-plans/{id}/items?sort_by=confidence&order=asc&min_confidence=0.5
```

**响应示例**
```json
{
  "items": [
    {
      "id": 1,
      "charge_item_name": "血常规",
      "ai_suggested_dimension_id": 10,
      "ai_confidence": 0.95,
      "user_set_dimension_id": null,
      "is_adjusted": false
    }
  ]
}
```

### 调整项目维度
```http
PUT /api/v1/classification-plans/{id}/items/{item_id}
```

**请求体**
```json
{
  "user_set_dimension_id": 15
}
```

### 生成提交预览
```http
POST /api/v1/classification-plans/{id}/preview
```

**响应示例**
```json
{
  "new_items": [
    {
      "charge_item_name": "血常规",
      "dimension_name": "检验科"
    }
  ],
  "overwrite_items": [
    {
      "charge_item_name": "心电图",
      "new_dimension_name": "心电图室",
      "old_dimension_name": "功能科"
    }
  ],
  "new_count": 50,
  "overwrite_count": 10
}
```

### 提交预案
```http
POST /api/v1/classification-plans/{id}/submit
```

**响应示例**
```json
{
  "success": true,
  "message": "预案提交成功",
  "new_count": 50,
  "overwrite_count": 10
}
```

## 错误响应

### 400 Bad Request
```json
{
  "detail": "任务名称不能为空"
}
```

### 403 Forbidden
```json
{
  "detail": "无权访问该资源"
}
```

### 404 Not Found
```json
{
  "detail": "任务不存在"
}
```

### 429 Too Many Requests
```json
{
  "detail": "已达到每日调用限额",
  "retry_after": 3600
}
```

### 500 Internal Server Error
```json
{
  "detail": "服务器内部错误"
}
```
