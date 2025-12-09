# 成本基准管理 - 错误处理实现总结

## 实现概述

本文档总结了成本基准管理功能的错误处理实现，包括前端和后端的错误处理机制。

## 后端错误处理

### 1. API错误拦截器

所有API端点都包含了完整的错误处理：

```python
try:
    # 业务逻辑
    ...
except HTTPException:
    raise  # 重新抛出HTTP异常
except Exception as e:
    db.rollback()  # 回滚事务
    raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")
```

### 2. 数据验证错误

#### 必填字段验证
- 科室代码、科室名称
- 模型版本ID、模型版本名称
- 维度代码、维度名称
- 基准值

错误消息示例：
```json
{
  "detail": "科室代码不能为空"
}
```

#### 数值范围验证
- 基准值必须大于0
- 基准值不能超过999999999.99

错误消息示例：
```json
{
  "detail": "基准值必须大于0"
}
```

### 3. 业务逻辑错误

#### 唯一性约束冲突
当创建或更新导致重复记录时：

```json
{
  "detail": "该科室（内科）在模型版本（V1.0）下的维度（业务量）成本基准已存在"
}
```

#### 外键引用验证
当引用的模型版本不存在时：

```json
{
  "detail": "模型版本不存在或不属于当前医疗机构"
}
```

### 4. 资源不存在错误

当访问不存在的资源时：

```json
{
  "detail": "成本基准不存在或不属于当前医疗机构"
}
```

### 5. 多租户访问控制

当尝试访问其他医疗机构的数据时：

```json
{
  "detail": "成本基准不存在或不属于当前医疗机构"
}
```

### 6. 导出错误处理

当没有可导出的数据时：

```json
{
  "detail": "没有可导出的数据，请先添加成本基准或调整筛选条件"
}
```

## 前端错误处理

### 1. 全局错误拦截器

在 `frontend/src/utils/request.ts` 中实现：

```typescript
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) {
      const status = error.response.status
      const data = error.response.data
      
      switch (status) {
        case 400:
          ElMessage.error(data.detail || '请求参数错误')
          break
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          // 清除token并跳转到登录页
          break
        case 403:
          ElMessage.error(data.detail || '没有权限访问')
          break
        case 404:
          ElMessage.error(data.detail || '请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误，请稍后重试')
          break
        default:
          ElMessage.error(data.detail || '请求失败')
      }
    } else if (error.request) {
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      ElMessage.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)
```

### 2. 网络超时处理

Axios配置了30秒超时：

```typescript
const request = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,  // 30秒超时
  headers: {
    'Content-Type': 'application/json'
  }
})
```

超时后会触发网络错误处理，显示"网络错误，请检查网络连接"。

### 3. 表单验证错误

#### Element Plus表单验证

```typescript
const rules = {
  department_code: [
    { required: true, message: '请选择科室', trigger: 'change' }
  ],
  version_id: [
    { required: true, message: '请选择模型版本', trigger: 'change' }
  ],
  dimension_code: [
    { required: true, message: '请选择维度', trigger: 'change' }
  ],
  benchmark_value: [
    { required: true, message: '请输入基准值', trigger: 'blur' },
    { 
      type: 'number', 
      min: 0.01, 
      message: '基准值必须大于0', 
      trigger: ['blur', 'change'] 
    },
    {
      validator: (rule, value, callback) => {
        if (value !== undefined && value !== null) {
          if (isNaN(value)) {
            callback(new Error('基准值必须是有效的数字'))
          } else if (value <= 0) {
            callback(new Error('基准值必须大于0'))
          } else if (value > 999999999.99) {
            callback(new Error('基准值不能超过999999999.99'))
          } else {
            callback()
          }
        } else {
          callback()
        }
      },
      trigger: ['blur', 'change']
    }
  ]
}
```

#### 提交前额外验证

```typescript
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    // 验证表单
    const valid = await formRef.value.validate()
    if (!valid) {
      ElMessage.warning('请填写完整的表单信息')
      return
    }

    // 额外验证：确保所有必填字段都有值
    if (!form.department_code || !form.version_id || 
        !form.dimension_code || !form.benchmark_value) {
      ElMessage.warning('请填写完整的表单信息')
      return
    }

    // 验证基准值必须大于0
    if (form.benchmark_value <= 0) {
      ElMessage.warning('基准值必须大于0')
      return
    }

    // 提交数据
    ...
  } catch (error) {
    console.error('提交表单失败:', error)
    // 错误消息已由拦截器处理
  } finally {
    submitting.value = false
  }
}
```

### 4. 数据加载错误处理

#### 列表加载

```typescript
const fetchCostBenchmarks = async () => {
  loading.value = true
  try {
    const res = await getCostBenchmarks(params)
    tableData.value = res.items || []
    pagination.total = res.total || 0
  } catch (error) {
    console.error('获取成本基准列表失败:', error)
    tableData.value = []
    pagination.total = 0
    // 错误消息已由拦截器处理
  } finally {
    loading.value = false
  }
}
```

#### 下拉选项加载

```typescript
const fetchVersions = async () => {
  try {
    const res = await request.get('/model-versions', {
      params: { limit: 1000 }
    })
    versions.value = res.items || []
  } catch (error) {
    console.error('获取模型版本列表失败:', error)
    versions.value = []
    // 错误消息已由拦截器处理
  }
}
```

### 5. 删除操作错误处理

```typescript
const handleDelete = async (row: CostBenchmark) => {
  try {
    await ElMessageBox.confirm('确定要删除该成本基准吗？', '提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    
    await deleteCostBenchmark(row.id)
    ElMessage.success('删除成功')
    
    // 如果删除后当前页没有数据，返回上一页
    if (tableData.value.length === 1 && pagination.page > 1) {
      pagination.page--
    }
    
    fetchCostBenchmarks()
  } catch (error) {
    // 用户取消操作
    if (error === 'cancel') {
      return
    }
    
    console.error('删除成本基准失败:', error)
    // 错误消息已由拦截器处理
  }
}
```

### 6. 导出操作错误处理

```typescript
const handleExport = async () => {
  // 检查是否有数据
  if (pagination.total === 0) {
    ElMessage.warning('没有可导出的数据')
    return
  }
  
  exporting.value = true
  try {
    const blob = await exportCostBenchmarks(params)
    
    // 验证返回的是Blob对象
    if (!(blob instanceof Blob)) {
      throw new Error('导出数据格式错误')
    }
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `成本基准_${timestamp}.xlsx`
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出成本基准失败:', error)
    // 错误消息已由拦截器处理
  } finally {
    exporting.value = false
  }
}
```

### 7. 页面初始化错误处理

```typescript
onMounted(async () => {
  try {
    // 并行加载所有初始数据
    await Promise.all([
      fetchCostBenchmarks(),
      fetchVersions(),
      fetchDepartments(),
      fetchDimensions()
    ])
  } catch (error) {
    console.error('页面初始化失败:', error)
    ElMessage.error('页面初始化失败，请刷新页面重试')
  }
})
```

### 8. 空状态处理

表格空状态：

```vue
<el-table
  :data="tableData"
  border
  stripe
  v-loading="loading"
  :empty-text="loading ? '加载中...' : '暂无数据'"
>
```

## 错误处理覆盖范围

### 后端（需求8.1-8.4）

✅ **8.1 必填字段验证**
- 所有必填字段都有验证
- 提供清晰的字段级别错误消息

✅ **8.2 数值验证**
- 基准值必须大于0
- 基准值不能超过最大值
- 非数字值会被拒绝

✅ **8.3 API错误处理**
- 所有API端点都有try-catch
- 提供用户友好的错误消息
- 区分不同类型的错误（400/404/500）

✅ **8.4 网络超时处理**
- 配置30秒超时
- 超时后显示网络错误提示

### 前端

✅ **API错误拦截器**
- 统一处理所有HTTP错误
- 根据状态码显示不同消息

✅ **表单验证**
- Element Plus表单验证
- 自定义验证器
- 实时验证和提交时验证

✅ **网络错误处理**
- 超时处理
- 网络断开处理
- 请求配置错误处理

✅ **用户体验优化**
- 加载状态显示
- 空状态提示
- 操作成功反馈
- 错误日志记录

## 测试验证

创建了测试文件 `test_cost_benchmark_error_handling.py`，包含：

1. **数据验证测试**
   - 缺少必填字段
   - 无效的基准值
   - 重复记录

2. **资源访问测试**
   - 不存在的资源
   - 跨租户访问

3. **业务逻辑测试**
   - 无效的版本ID
   - 导出空数据

4. **参数验证测试**
   - 分页参数验证

## 使用示例

### 后端错误响应

```json
// 400 Bad Request
{
  "detail": "基准值必须大于0"
}

// 404 Not Found
{
  "detail": "成本基准不存在或不属于当前医疗机构"
}

// 500 Internal Server Error
{
  "detail": "创建成本基准失败: Database connection error"
}
```

### 前端错误处理

```typescript
// 自动显示错误消息
try {
  await createCostBenchmark(data)
  ElMessage.success('创建成功')
} catch (error) {
  // 错误消息已由拦截器自动显示
  console.error('创建失败:', error)
}
```

## 最佳实践

1. **后端**
   - 所有API端点都包含try-catch
   - 区分HTTPException和其他异常
   - 提供详细的错误消息
   - 失败时回滚事务

2. **前端**
   - 使用全局错误拦截器
   - 提供用户友好的错误消息
   - 记录详细的错误日志
   - 优雅降级（显示空状态）

3. **用户体验**
   - 加载状态指示
   - 操作反馈（成功/失败）
   - 防止重复提交
   - 智能分页处理

## 总结

成本基准管理功能的错误处理实现完整覆盖了需求8.1-8.4的所有要求：

- ✅ API错误拦截器
- ✅ 用户友好的错误消息
- ✅ 网络超时处理
- ✅ 表单验证错误

所有错误场景都有适当的处理和用户反馈，确保了良好的用户体验和系统稳定性。
