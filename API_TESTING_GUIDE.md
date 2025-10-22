# API测试指南

## 🚀 启动后端服务

```powershell
.\scripts\dev-start-backend.ps1
```

服务启动后访问：
- **API文档**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 测试认证API

### 1. 用户登录

**请求**:
```http
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**使用Swagger UI测试**:
1. 访问 http://localhost:8000/docs
2. 找到 `POST /api/v1/auth/login`
3. 点击 "Try it out"
4. 输入用户名和密码
5. 点击 "Execute"
6. 复制返回的 `access_token`

### 2. 获取当前用户信息

**请求**:
```http
GET http://localhost:8000/api/v1/auth/me
Authorization: Bearer <your_access_token>
```

**响应**:
```json
{
  "id": 1,
  "username": "admin",
  "name": "System Administrator",
  "email": "admin@hospital.com",
  "status": "active",
  "created_at": "2025-10-21T10:00:00",
  "updated_at": "2025-10-21T10:00:00",
  "roles": ["admin"]
}
```

**使用Swagger UI测试**:
1. 在Swagger UI页面顶部，点击 "Authorize" 按钮
2. 输入: `Bearer <your_access_token>`
3. 点击 "Authorize"
4. 现在可以测试需要认证的API了

## 👥 测试用户管理API

### 1. 获取用户列表

**请求**:
```http
GET http://localhost:8000/api/v1/users?page=1&size=10
Authorization: Bearer <your_access_token>
```

**响应**:
```json
{
  "total": 1,
  "items": [
    {
      "id": 1,
      "username": "admin",
      "name": "System Administrator",
      "email": "admin@hospital.com",
      "status": "active",
      "created_at": "2025-10-21T10:00:00",
      "updated_at": "2025-10-21T10:00:00",
      "roles": ["admin"]
    }
  ]
}
```

### 2. 创建用户

**请求**:
```http
POST http://localhost:8000/api/v1/users
Authorization: Bearer <your_access_token>
Content-Type: application/json

{
  "username": "testuser",
  "name": "Test User",
  "email": "test@hospital.com",
  "password": "test123",
  "role_ids": [2]
}
```

### 3. 获取用户详情

**请求**:
```http
GET http://localhost:8000/api/v1/users/1
Authorization: Bearer <your_access_token>
```

### 4. 更新用户

**请求**:
```http
PUT http://localhost:8000/api/v1/users/1
Authorization: Bearer <your_access_token>
Content-Type: application/json

{
  "name": "Updated Name",
  "email": "updated@hospital.com"
}
```

### 5. 删除用户

**请求**:
```http
DELETE http://localhost:8000/api/v1/users/2
Authorization: Bearer <your_access_token>
```

## 🧪 使用curl测试

### 登录并获取Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 使用Token访问API

```bash
# 保存token到变量
TOKEN="your_access_token_here"

# 获取当前用户信息
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"

# 获取用户列表
curl -X GET "http://localhost:8000/api/v1/users?page=1&size=10" \
  -H "Authorization: Bearer $TOKEN"
```

## 🧪 使用PowerShell测试

### 登录

```powershell
$loginData = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method Post `
    -Body $loginData `
    -ContentType "application/json"

$token = $response.access_token
Write-Host "Token: $token"
```

### 获取用户信息

```powershell
$headers = @{
    Authorization = "Bearer $token"
}

$user = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" `
    -Method Get `
    -Headers $headers

$user | ConvertTo-Json
```

### 获取用户列表

```powershell
$users = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/users?page=1&size=10" `
    -Method Get `
    -Headers $headers

$users | ConvertTo-Json -Depth 3
```

## 📝 测试场景

### 场景1：完整的用户管理流程

1. **登录获取Token**
2. **创建新用户**
3. **获取用户列表** - 验证新用户已创建
4. **更新用户信息**
5. **获取用户详情** - 验证更新成功
6. **删除用户**
7. **获取用户列表** - 验证用户已删除

### 场景2：权限测试

1. **使用admin登录** - 应该成功
2. **尝试错误密码** - 应该返回401
3. **使用过期Token** - 应该返回401
4. **不带Token访问受保护API** - 应该返回401

## 🐛 常见问题

### Q: 401 Unauthorized

**原因**: Token无效或已过期

**解决**: 重新登录获取新Token

### Q: 403 Forbidden

**原因**: 用户账户未激活

**解决**: 检查用户状态

### Q: 400 Bad Request

**原因**: 请求数据格式错误或违反约束

**解决**: 检查请求体格式和字段值

## 🎯 下一步

API测试通过后，可以：

1. 实现角色管理API
2. 实现权限管理API
3. 开始前端登录页面开发

查看 `AUTH_MODULE_PROGRESS.md` 了解完整的开发进度。
