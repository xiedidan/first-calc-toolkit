# 成本基准管理 - 维度列表加载修复

## 问题描述

在成本基准管理页面加载时，前端尝试获取维度列表失败，控制台显示错误：

```
CostBenchmarks.vue:431 获取维度列表失败: AxiosError
```

## 问题原因

前端代码在调用 `/model-nodes` API 时缺少必需的 `version_id` 参数。

### 原始代码

```typescript
const fetchDimensions = async () => {
  try {
    // 获取激活版本的维度节点
    const res = await request.get('/model-nodes', {
      params: { limit: 1000 }  // ❌ 缺少 version_id 参数
    })
    dimensions.value = res.items || []
  } catch (error: any) {
    console.error('获取维度列表失败:', error)
    dimensions.value = []
  }
}
```

### API 要求

`/model-nodes` API 的定义要求必须传递 `version_id` 参数：

```python
@router.get("", response_model=ModelNodeListResponse)
def get_model_nodes(
    version_id: int,  # ← 必需参数
    parent_id: Optional[int] = None,
    ...
)
```

## 解决方案

修改 `fetchDimensions` 函数，先获取激活的模型版本，然后使用该版本ID获取维度列表。

### 修复后的代码

```typescript
const fetchDimensions = async () => {
  try {
    // 先获取激活的模型版本
    const versionsRes = await request.get('/model-versions', {
      params: { limit: 1 }
    })
    
    if (!versionsRes.items || versionsRes.items.length === 0) {
      console.warn('没有可用的模型版本')
      dimensions.value = []
      return
    }
    
    const activeVersion = versionsRes.items[0]
    
    // 获取该版本的所有维度节点
    const res = await request.get('/model-nodes', {
      params: { 
        version_id: activeVersion.id,  // ✅ 传递必需的 version_id
        limit: 1000 
      }
    })
    dimensions.value = res.items || []
  } catch (error: any) {
    console.error('获取维度列表失败:', error)
    dimensions.value = []
  }
}
```

## 修复步骤

1. **修改文件**: `frontend/src/views/CostBenchmarks.vue`
2. **修改位置**: `fetchDimensions` 函数（约第420-435行）
3. **修改内容**: 
   - 先调用 `/model-versions` 获取激活版本
   - 使用版本ID调用 `/model-nodes` 获取维度列表
   - 添加空版本检查

## 验证步骤

1. **重新构建前端**:
   ```bash
   cd frontend
   npm run build
   ```

2. **刷新页面**:
   - 清除浏览器缓存
   - 刷新成本基准管理页面

3. **检查结果**:
   - 打开浏览器开发者工具（F12）
   - 查看 Console 标签，应该没有错误
   - 查看 Network 标签，确认以下请求成功：
     - `GET /api/v1/model-versions?limit=1`
     - `GET /api/v1/model-nodes?version_id=X&limit=1000`
   - 在页面上，"维度"下拉框应该能正常显示选项

## 影响范围

- **影响功能**: 成本基准管理页面的维度筛选和维度选择
- **影响用户**: 所有使用成本基准管理功能的用户
- **严重程度**: 中等（功能可用但体验受影响）

## 相关问题

这个问题也可能影响其他使用 `/model-nodes` API 的页面。建议检查以下页面：

1. 模型节点管理页面
2. 维度目录管理页面
3. 其他需要选择维度的页面

## 预防措施

为避免类似问题，建议：

1. **API 文档**: 在 API 文档中明确标注必需参数
2. **TypeScript 类型**: 为 API 调用定义严格的类型
3. **代码审查**: 在代码审查时检查 API 调用参数
4. **集成测试**: 添加前后端集成测试，验证 API 调用

## 测试建议

### 单元测试

```typescript
describe('fetchDimensions', () => {
  it('should fetch dimensions with version_id', async () => {
    // Mock API responses
    const mockVersions = { items: [{ id: 1, name: 'v1' }] }
    const mockDimensions = { items: [{ id: 1, code: 'D001', name: '维度1' }] }
    
    // Test implementation
    // ...
  })
  
  it('should handle empty versions gracefully', async () => {
    // Mock empty versions response
    const mockVersions = { items: [] }
    
    // Test implementation
    // ...
  })
})
```

### 集成测试

```python
def test_cost_benchmarks_page_loads_dimensions():
    """测试成本基准页面能正确加载维度列表"""
    # 1. 创建测试数据（版本、维度）
    # 2. 访问成本基准管理页面
    # 3. 验证维度下拉框有选项
    # 4. 验证没有控制台错误
```

## 更新日志

- **2024-11-27**: 发现并修复维度列表加载失败问题
- **修复人员**: AI Assistant
- **影响版本**: v1.0.0
- **修复版本**: v1.0.1

## 相关文件

- `frontend/src/views/CostBenchmarks.vue` - 修复的主文件
- `backend/app/api/model_nodes.py` - API 定义文件
- `COST_BENCHMARK_API_DOCUMENTATION.md` - API 文档

---

**状态**: ✅ 已修复  
**优先级**: 高  
**类型**: Bug修复
