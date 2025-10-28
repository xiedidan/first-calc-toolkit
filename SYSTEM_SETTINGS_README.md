# 系统设置功能说明

## 功能概述

系统设置模块提供了全局配置管理功能，包括：
1. **当期年月设置**：用于计算任务的默认计算周期
2. **系统名称设置**：自定义系统显示名称
3. **系统版本信息**：显示当前系统版本

## 已实现功能

### 1. 当期年月设置 (FR-GLOBAL-01)

#### 功能描述
- 系统提供全局"当期年月"设置项
- 格式：YYYY-MM（例如：2025-10）
- 作为所有计算任务的默认计算周期
- 在界面中多处显示以保持上下文一致

#### API接口

**获取系统设置**
```http
GET /api/v1/system/settings
```

响应示例：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "current_period": "2025-10",
    "system_name": "医院科室业务价值评估工具",
    "version": "1.0.0"
  }
}
```

**更新系统设置**
```http
PUT /api/v1/system/settings
```

请求示例：
```json
{
  "current_period": "2025-11",
  "system_name": "医院科室业务价值评估工具 v2"
}
```

响应示例：
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "current_period": "2025-11",
    "system_name": "医院科室业务价值评估工具 v2",
    "version": "1.0.0"
  }
}
```

#### 数据验证
- 当期年月格式必须为 YYYY-MM
- 月份范围：01-12
- 示例：2025-10 ✓，2025-13 ✗

### 2. SQL数据源配置 (FR-GLOBAL-02)

数据源配置功能已完整实现，详见 [DATA_SOURCE_README.md](DATA_SOURCE_README.md)

## 数据库设计

### system_settings 表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键 |
| key | VARCHAR(100) | 设置键（唯一） |
| value | TEXT | 设置值 |
| description | TEXT | 设置描述 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 预定义设置键

| 键名 | 说明 | 示例值 |
|------|------|--------|
| current_period | 当期年月 | 2025-10 |
| system_name | 系统名称 | 医院科室业务价值评估工具 |
| system_version | 系统版本 | 1.0.0 |

## 部署步骤

### 1. 运行数据库迁移

```bash
cd backend
alembic upgrade head
```

这将创建 `system_settings` 表并插入默认设置。

### 2. 启动后端服务

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 测试API

```bash
cd backend
python test_system_settings_api.py
```

### 4. 访问API文档

打开浏览器访问：http://localhost:8000/docs

在 "系统设置" 标签下可以看到相关API接口。

## 使用示例

### Python示例

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 获取系统设置
response = requests.get(f"{BASE_URL}/system/settings")
settings = response.json()["data"]
print(f"当期年月: {settings['current_period']}")

# 更新当期年月
response = requests.put(
    f"{BASE_URL}/system/settings",
    json={"current_period": "2025-11"}
)
print(response.json())
```

### JavaScript示例

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// 获取系统设置
fetch(`${BASE_URL}/system/settings`)
  .then(response => response.json())
  .then(data => {
    console.log("当期年月:", data.data.current_period);
  });

// 更新当期年月
fetch(`${BASE_URL}/system/settings`, {
  method: "PUT",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    current_period: "2025-11"
  })
})
  .then(response => response.json())
  .then(data => {
    console.log("更新成功:", data);
  });
```

## 前端集成建议

### 1. 创建系统设置页面

```vue
<template>
  <div class="system-settings">
    <el-card>
      <template #header>
        <span>系统设置</span>
      </template>
      
      <el-form :model="form" label-width="120px">
        <el-form-item label="当期年月">
          <el-date-picker
            v-model="form.current_period"
            type="month"
            format="YYYY-MM"
            value-format="YYYY-MM"
            placeholder="选择年月"
          />
        </el-form-item>
        
        <el-form-item label="系统名称">
          <el-input v-model="form.system_name" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="saveSettings">保存</el-button>
          <el-button @click="loadSettings">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import axios from 'axios';

const form = ref({
  current_period: '',
  system_name: ''
});

const loadSettings = async () => {
  try {
    const response = await axios.get('/api/v1/system/settings');
    const data = response.data.data;
    form.value.current_period = data.current_period || '';
    form.value.system_name = data.system_name || '';
  } catch (error) {
    ElMessage.error('加载设置失败');
  }
};

const saveSettings = async () => {
  try {
    await axios.put('/api/v1/system/settings', form.value);
    ElMessage.success('保存成功');
  } catch (error) {
    ElMessage.error('保存失败');
  }
};

onMounted(() => {
  loadSettings();
});
</script>
```

### 2. 在全局状态中使用当期年月

```javascript
// store/system.js
import { defineStore } from 'pinia';
import axios from 'axios';

export const useSystemStore = defineStore('system', {
  state: () => ({
    currentPeriod: null,
    systemName: '',
  }),
  
  actions: {
    async loadSettings() {
      const response = await axios.get('/api/v1/system/settings');
      const data = response.data.data;
      this.currentPeriod = data.current_period;
      this.systemName = data.system_name;
    },
    
    async updateCurrentPeriod(period) {
      await axios.put('/api/v1/system/settings', {
        current_period: period
      });
      this.currentPeriod = period;
    }
  }
});
```

## 权限控制

### 当前状态
- 获取系统设置：所有用户可访问
- 更新系统设置：**待实现权限控制**

### 建议实现
在 `backend/app/api/system_settings.py` 中添加权限依赖：

```python
from app.api.deps import get_current_user, require_admin

@router.put("", response_model=dict)
def update_system_settings(
    settings_update: SystemSettingsUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin),  # 需要管理员权限
):
    """更新系统设置（需要管理员权限）"""
    # ...
```

## 扩展建议

### 1. 添加更多系统设置

可以通过添加新的设置键来扩展功能：

```python
# 在 SystemSettingService 中添加新的键
KEY_CALCULATION_TIMEOUT = "calculation_timeout"
KEY_MAX_UPLOAD_SIZE = "max_upload_size"
KEY_EMAIL_NOTIFICATION = "email_notification"
```

### 2. 设置分组

可以将设置按功能分组：

```python
class SystemSettingsResponse(BaseModel):
    # 基础设置
    current_period: Optional[str]
    system_name: Optional[str]
    version: Optional[str]
    
    # 计算设置
    calculation_timeout: Optional[int]
    max_concurrent_tasks: Optional[int]
    
    # 通知设置
    email_notification: Optional[bool]
    notification_email: Optional[str]
```

### 3. 设置历史记录

可以添加设置变更历史表：

```sql
CREATE TABLE system_setting_history (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_by INTEGER,  -- 用户ID
    changed_at TIMESTAMP DEFAULT NOW()
);
```

## 故障排查

### 问题1：无法连接到API
- 检查后端服务是否启动
- 检查端口是否正确（默认8000）
- 检查防火墙设置

### 问题2：数据库表不存在
- 运行数据库迁移：`alembic upgrade head`
- 检查数据库连接配置

### 问题3：当期年月格式验证失败
- 确保格式为 YYYY-MM
- 月份范围：01-12
- 示例：2025-10 ✓，2025-13 ✗

## 相关文档

- [API设计文档](API设计文档.md) - 第8章：系统配置API
- [系统设计文档](系统设计文档.md) - 3.4.5节：系统配置
- [数据源功能文档](DATA_SOURCE_README.md) - SQL数据源配置功能
