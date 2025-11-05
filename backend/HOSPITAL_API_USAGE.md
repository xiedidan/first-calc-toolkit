# 医疗机构管理API使用指南

## 快速开始

### 1. 获取可访问的医疗机构列表

```bash
GET /api/v1/hospitals/accessible
Authorization: Bearer <token>
```

响应：
```json
[
  {
    "id": 1,
    "code": "nbeye",
    "name": "宁波市眼科医院",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

### 2. 激活医疗机构

```bash
POST /api/v1/hospitals/1/activate
Authorization: Bearer <token>
```

响应：
```json
{
  "hospital_id": 1,
  "hospital_name": "宁波市眼科医院",
  "message": "医疗机构激活成功，请在后续请求中通过 X-Hospital-ID 请求头传递医疗机构ID"
}
```

### 3. 访问业务API

激活医疗机构后，所有业务API请求必须包含 `X-Hospital-ID` 请求头：

```bash
GET /api/v1/departments
Authorization: Bearer <token>
X-Hospital-ID: 1
```

## API端点

### 医疗机构管理

#### 获取医疗机构列表（管理员）
```
GET /api/v1/hospitals?page=1&size=10&search=<关键词>&is_active=<true|false>
```

#### 创建医疗机构（管理员）
```
POST /api/v1/hospitals
Content-Type: application/json

{
  "code": "hospital_code",
  "name": "医院名称",
  "is_active": true
}
```

#### 获取医疗机构详情（管理员）
```
GET /api/v1/hospitals/{id}
```

#### 更新医疗机构（管理员）
```
PUT /api/v1/hospitals/{id}
Content-Type: application/json

{
  "name": "新的医院名称",
  "is_active": true
}
```

注意：不允许修改医疗机构编码（code）

#### 删除医疗机构（管理员）
```
DELETE /api/v1/hospitals/{id}
```

注意：如果医疗机构有关联数据（用户、模型、科室等），将拒绝删除

### 用户管理

#### 创建用户（绑定医疗机构）
```
POST /api/v1/users
Content-Type: application/json

{
  "username": "user123",
  "name": "张三",
  "email": "user@example.com",
  "password": "password123",
  "role_ids": [1, 2],
  "hospital_id": 1  // 可选，为空表示超级用户
}
```

#### 更新用户（修改医疗机构绑定）
```
PUT /api/v1/users/{id}
Content-Type: application/json

{
  "name": "李四",
  "hospital_id": 2  // 可选
}
```

## 数据隔离说明

### 自动过滤

所有业务数据查询都会自动添加医疗机构过滤条件：

- **科室管理**：只返回当前医疗机构的科室
- **模型版本**：只返回当前医疗机构的模型版本
- **模型节点**：只返回当前医疗机构模型版本的节点
- **计算任务**：只返回当前医疗机构的计算任务
- **计算流程**：只返回当前医疗机构的计算流程
- **计算步骤**：只返回当前医疗机构的计算步骤

### 自动关联

创建业务数据时会自动关联到当前激活的医疗机构：

```bash
POST /api/v1/departments
Authorization: Bearer <token>
X-Hospital-ID: 1
Content-Type: application/json

{
  "his_code": "001",
  "his_name": "内科"
}
```

系统会自动将 `hospital_id=1` 关联到新创建的科室。

### 权限验证

更新或删除数据时，系统会验证数据是否属于当前医疗机构：

```bash
DELETE /api/v1/departments/123
Authorization: Bearer <token>
X-Hospital-ID: 1
```

如果科室123不属于医疗机构1，将返回403错误。

## 用户类型

### 超级用户（hospital_id = NULL）
- 可以访问所有医疗机构的数据
- 可以在不同医疗机构之间切换
- 通常是系统管理员

### 普通用户（hospital_id = 具体ID）
- 只能访问绑定的医疗机构数据
- 无法切换到其他医疗机构
- 尝试访问其他医疗机构数据将返回403错误

## 错误处理

### 400 Bad Request - 未激活医疗机构
```json
{
  "detail": "请先激活医疗机构"
}
```

解决方法：调用激活API并在请求头中传递 `X-Hospital-ID`

### 403 Forbidden - 无权访问
```json
{
  "detail": "您没有权限访问该医疗机构"
}
```

解决方法：确认用户有权访问该医疗机构

### 404 Not Found - 数据不存在
```json
{
  "detail": "医疗机构不存在"
}
```

可能原因：
1. 医疗机构ID不存在
2. 数据不属于当前医疗机构（被过滤掉）

## 前端集成示例

### Axios拦截器配置

```javascript
import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 添加认证token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 添加医疗机构ID
    const hospitalId = localStorage.getItem('currentHospitalId');
    if (hospitalId) {
      config.headers['X-Hospital-ID'] = hospitalId;
    }
    
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 400 && 
        error.response?.data?.detail === '请先激活医疗机构') {
      // 跳转到医疗机构选择页面
      router.push('/select-hospital');
    }
    return Promise.reject(error);
  }
);

export default api;
```

### Vue组件示例

```vue
<template>
  <div>
    <el-select v-model="currentHospitalId" @change="switchHospital">
      <el-option
        v-for="hospital in accessibleHospitals"
        :key="hospital.id"
        :label="hospital.name"
        :value="hospital.id"
      />
    </el-select>
  </div>
</template>

<script>
export default {
  data() {
    return {
      currentHospitalId: null,
      accessibleHospitals: [],
    };
  },
  
  async mounted() {
    await this.loadAccessibleHospitals();
    this.currentHospitalId = parseInt(localStorage.getItem('currentHospitalId'));
  },
  
  methods: {
    async loadAccessibleHospitals() {
      const response = await this.$api.get('/hospitals/accessible');
      this.accessibleHospitals = response.data;
    },
    
    async switchHospital(hospitalId) {
      try {
        await this.$api.post(`/hospitals/${hospitalId}/activate`);
        localStorage.setItem('currentHospitalId', hospitalId);
        // 刷新页面数据
        this.$router.go(0);
      } catch (error) {
        this.$message.error('切换医疗机构失败');
      }
    },
  },
};
</script>
```

## 测试建议

### 1. 测试数据隔离

创建两个医疗机构和两个用户，分别绑定到不同医疗机构：

```bash
# 创建医疗机构A
POST /api/v1/hospitals
{"code": "hospital_a", "name": "医院A"}

# 创建医疗机构B
POST /api/v1/hospitals
{"code": "hospital_b", "name": "医院B"}

# 创建用户A（绑定医院A）
POST /api/v1/users
{"username": "user_a", "hospital_id": 1, ...}

# 创建用户B（绑定医院B）
POST /api/v1/users
{"username": "user_b", "hospital_id": 2, ...}
```

然后测试：
- 用户A只能看到医院A的数据
- 用户B只能看到医院B的数据
- 用户A无法访问医院B的数据

### 2. 测试超级用户

创建一个超级用户（不绑定医疗机构）：

```bash
POST /api/v1/users
{"username": "admin", "hospital_id": null, ...}
```

测试：
- 超级用户可以切换到任意医疗机构
- 超级用户可以看到所有医疗机构的数据

### 3. 测试权限控制

测试未激活医疗机构时的菜单权限：
- 只能访问系统设置和数据源管理
- 其他菜单应该被禁用

## 常见问题

### Q: 如何判断用户是否是超级用户？
A: 查看用户的 `hospital_id` 字段，如果为 `null` 则是超级用户。

### Q: 可以修改医疗机构编码吗？
A: 不可以。医疗机构编码创建后不允许修改，只能修改名称和启用状态。

### Q: 如何删除有数据的医疗机构？
A: 必须先删除或迁移该医疗机构的所有关联数据（用户、模型、科室等），然后才能删除医疗机构。

### Q: 未激活医疗机构时可以访问哪些API？
A: 可以访问：
- 认证相关API（登录、登出）
- 医疗机构列表和激活API
- 系统设置API
- 数据源管理API

### Q: 如何在开发环境中测试？
A: 使用提供的测试脚本 `backend/test_hospital_api.py`，或使用Postman/curl手动测试。

## 相关文档

- [数据隔离实施总结](./HOSPITAL_DATA_ISOLATION_SUMMARY.md)
- [数据库迁移指南](./HOSPITAL_MIGRATION_GUIDE.md)
- [数据库迁移总结](./HOSPITAL_MIGRATION_SUMMARY.md)
