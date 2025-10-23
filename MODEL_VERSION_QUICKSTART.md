# 模型版本管理 - 快速开始

## 1. 数据库迁移

首先需要执行数据库迁移来创建新表：

```bash
# Windows (使用Anaconda Prompt)
cd backend
conda activate hospital_value
alembic upgrade head
```

## 2. 启动后端服务

```bash
# 确保在backend目录
cd backend

# 激活conda环境
conda activate hospital_value

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 3. 测试API

### 方式1: 使用测试脚本

```bash
# 在backend目录下
python test_model_api.py
```

### 方式2: 使用Swagger UI

访问 http://localhost:8000/docs 查看和测试API

### 方式3: 使用curl

```bash
# 1. 登录获取token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 2. 创建模型版本（替换<token>为实际token）
curl -X POST http://localhost:8000/api/v1/model-versions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "v1.0",
    "name": "2025年标准版",
    "description": "初始版本"
  }'

# 3. 获取版本列表
curl -X GET http://localhost:8000/api/v1/model-versions \
  -H "Authorization: Bearer <token>"

# 4. 创建模型节点
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

# 5. 获取节点列表
curl -X GET "http://localhost:8000/api/v1/model-nodes?version_id=1" \
  -H "Authorization: Bearer <token>"

# 6. 激活版本
curl -X PUT http://localhost:8000/api/v1/model-versions/1/activate \
  -H "Authorization: Bearer <token>"
```

## 4. API端点总览

### 模型版本管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/model-versions` | 获取版本列表 |
| POST | `/api/v1/model-versions` | 创建版本 |
| GET | `/api/v1/model-versions/{id}` | 获取版本详情 |
| PUT | `/api/v1/model-versions/{id}` | 更新版本 |
| DELETE | `/api/v1/model-versions/{id}` | 删除版本 |
| PUT | `/api/v1/model-versions/{id}/activate` | 激活版本 |

### 模型节点管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/model-nodes` | 获取节点列表 |
| POST | `/api/v1/model-nodes` | 创建节点 |
| GET | `/api/v1/model-nodes/{id}` | 获取节点详情 |
| PUT | `/api/v1/model-nodes/{id}` | 更新节点 |
| DELETE | `/api/v1/model-nodes/{id}` | 删除节点 |
| POST | `/api/v1/model-nodes/{id}/test-code` | 测试节点代码 |

## 5. 数据模型说明

### 节点类型 (node_type)

- `sequence`: 序列节点（如：医生序列、护理序列）
- `dimension`: 维度节点（如：门诊诊察、住院手术）

### 计算类型 (calc_type)

- `statistical`: 统计型（基于收费项目目录统计）
- `calculational`: 计算型（基于自定义SQL/Python计算）

## 6. 常见问题

### Q1: 数据库迁移失败

**A**: 确保数据库连接正常，检查 `.env` 文件中的数据库配置

### Q2: 无法创建节点

**A**: 检查：
1. 版本ID是否存在
2. 父节点ID是否有效
3. 节点编码是否重复

### Q3: 删除版本失败

**A**: 不能删除激活状态的版本，需要先激活其他版本

## 7. 下一步

- [ ] 实现代码测试功能（SQL/Python执行器）
- [ ] 开发前端界面
- [ ] 集成维度目录管理
- [ ] 实现权限控制

## 8. 相关文档

- [完整实现文档](./MODEL_VERSION_COMPLETED.md)
- [API设计文档](./API设计文档.md)
- [系统设计文档](./系统设计文档.md)
