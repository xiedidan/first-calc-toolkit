# 成本基准管理 - 末级维度过滤实现

## 需求背景

用户反馈:添加成本基准时,维度下拉选项应该只显示末级维度(叶子节点),包括医疗、护理、技术等所有业务类别的末级维度。

## 业务逻辑

成本基准应该设置在最细粒度的维度上,即末级维度。中间层级的维度(如"医疗"、"护理"、"技术"等分类节点)不应该出现在选择列表中,因为:

1. **精确性**: 成本基准需要设置在具体的工作项目上,而不是大类
2. **可操作性**: 末级维度才是实际产生成本的单元
3. **数据一致性**: 避免在不同层级设置基准值导致的混乱

## 实现方案

### 修改前的问题

原代码获取所有维度节点,包括:
- 一级分类节点(如"医疗"、"护理"、"技术")
- 二级分类节点(如"门诊工作量"、"住院工作量")
- 末级节点(如具体的工作项目)

这导致用户在选择时看到大量不应该选择的中间节点。

### 修改后的逻辑

```typescript
/**
 * 获取维度列表（只获取末级维度）
 */
const fetchDimensions = async () => {
  try {
    // 1. 获取激活的模型版本
    const versionsRes = await request.get('/model-versions', {
      params: { limit: 1 }
    })
    
    if (!versionsRes.items || versionsRes.items.length === 0) {
      console.warn('没有可用的模型版本')
      dimensions.value = []
      return
    }
    
    const activeVersion = versionsRes.items[0]
    
    // 2. 获取该版本的所有维度节点
    const res = await request.get('/model-nodes', {
      params: { 
        version_id: activeVersion.id,
        limit: 1000 
      }
    })
    
    const allNodes = res.items || []
    
    // 3. 过滤出末级维度（没有子节点的节点）
    // 通过检查是否有其他节点的parent_id指向当前节点来判断
    const parentIds = new Set(allNodes.map(node => node.parent_id).filter(id => id !== null))
    const leafNodes = allNodes.filter(node => !parentIds.has(node.id))
    
    dimensions.value = leafNodes
    
    console.log(`获取到 ${allNodes.length} 个维度节点，其中 ${leafNodes.length} 个末级维度`)
  } catch (error: any) {
    console.error('获取维度列表失败:', error)
    dimensions.value = []
  }
}
```

### 过滤算法说明

1. **收集所有父节点ID**: 遍历所有节点,收集所有 `parent_id` 值到一个 Set 中
2. **识别末级节点**: 如果一个节点的 `id` 不在父节点ID集合中,说明没有其他节点指向它,即它是末级节点
3. **返回末级节点**: 只返回末级节点供用户选择

### 示例

假设有以下节点结构:

```
医疗 (id: 1, parent_id: null)
  ├─ 门诊工作量 (id: 2, parent_id: 1)
  │   ├─ 普通门诊 (id: 3, parent_id: 2)  ← 末级
  │   └─ 专家门诊 (id: 4, parent_id: 2)  ← 末级
  └─ 住院工作量 (id: 5, parent_id: 1)
      └─ 住院床日 (id: 6, parent_id: 5)  ← 末级

护理 (id: 7, parent_id: null)
  └─ 护理工作量 (id: 8, parent_id: 7)
      ├─ 一级护理 (id: 9, parent_id: 8)  ← 末级
      └─ 二级护理 (id: 10, parent_id: 8) ← 末级
```

**过滤过程**:
1. 收集父节点ID: `{null, 1, 2, 1, 5, 7, 8, 8}` → `{1, 2, 5, 7, 8}`
2. 过滤末级节点: 
   - id=3 不在父节点集合中 ✓
   - id=4 不在父节点集合中 ✓
   - id=6 不在父节点集合中 ✓
   - id=9 不在父节点集合中 ✓
   - id=10 不在父节点集合中 ✓
3. 结果: 只显示 `[普通门诊, 专家门诊, 住院床日, 一级护理, 二级护理]`

## 修改的文件

- `frontend/src/views/CostBenchmarks.vue` - 修改了 `fetchDimensions` 函数

## 验证步骤

1. **重新构建前端**:
   ```bash
   cd frontend
   npm run build
   ```

2. **刷新页面并测试**:
   - 打开成本基准管理页面
   - 点击"添加成本基准"按钮
   - 查看"维度"下拉框

3. **预期结果**:
   - 只显示末级维度(叶子节点)
   - 不显示"医疗"、"护理"、"技术"等分类节点
   - 不显示"门诊工作量"、"住院工作量"等中间层级节点
   - 只显示具体的工作项目

4. **检查控制台日志**:
   ```
   获取到 50 个维度节点，其中 30 个末级维度
   ```
   (数字会根据实际数据变化)

## 性能考虑

### 时间复杂度
- 收集父节点ID: O(n)
- 过滤末级节点: O(n)
- 总体: O(n),其中 n 是节点总数

### 空间复杂度
- 父节点ID集合: O(n)
- 总体: O(n)

对于通常的维度节点数量(几十到几百个),这个性能开销完全可以接受。

## 替代方案

如果后端支持,也可以在后端API中添加一个参数来直接返回末级节点:

```typescript
// 后端API支持 leaf_only 参数
const res = await request.get('/model-nodes', {
  params: { 
    version_id: activeVersion.id,
    leaf_only: true,  // 只返回末级节点
    limit: 1000 
  }
})
```

这样可以:
1. 减少网络传输的数据量
2. 将过滤逻辑移到后端,更易于维护
3. 提高前端性能

但当前的前端过滤方案已经足够高效,且不需要修改后端API。

## 影响范围

- **影响功能**: 成本基准管理的维度选择
- **影响用户**: 所有使用成本基准管理功能的用户
- **用户体验**: 改善 - 减少了不必要的选项,使选择更加清晰

## 相关问题

这个过滤逻辑也可能适用于其他需要选择维度的页面,建议检查:

1. 维度目录管理页面
2. 定向规则管理页面
3. 其他需要选择具体维度的功能

## 测试建议

### 单元测试

```typescript
describe('fetchDimensions', () => {
  it('should filter leaf nodes correctly', () => {
    const allNodes = [
      { id: 1, parent_id: null, name: '医疗' },
      { id: 2, parent_id: 1, name: '门诊工作量' },
      { id: 3, parent_id: 2, name: '普通门诊' },
      { id: 4, parent_id: 2, name: '专家门诊' }
    ]
    
    const parentIds = new Set(allNodes.map(n => n.parent_id).filter(id => id !== null))
    const leafNodes = allNodes.filter(n => !parentIds.has(n.id))
    
    expect(leafNodes).toHaveLength(2)
    expect(leafNodes.map(n => n.name)).toEqual(['普通门诊', '专家门诊'])
  })
  
  it('should handle nodes with no children', () => {
    const allNodes = [
      { id: 1, parent_id: null, name: '单独节点' }
    ]
    
    const parentIds = new Set(allNodes.map(n => n.parent_id).filter(id => id !== null))
    const leafNodes = allNodes.filter(n => !parentIds.has(n.id))
    
    expect(leafNodes).toHaveLength(1)
    expect(leafNodes[0].name).toBe('单独节点')
  })
})
```

### 集成测试

```python
def test_cost_benchmark_shows_only_leaf_dimensions():
    """测试成本基准页面只显示末级维度"""
    # 1. 创建测试数据（多层级维度）
    # 2. 访问成本基准管理页面
    # 3. 打开添加对话框
    # 4. 验证维度下拉框只包含末级维度
    # 5. 验证不包含中间层级节点
```

## 更新日志

- **2024-11-27**: 实现末级维度过滤功能
- **修复人员**: AI Assistant
- **影响版本**: v1.0.0
- **修复版本**: v1.0.2

## 相关文件

- `frontend/src/views/CostBenchmarks.vue` - 实现末级维度过滤
- `COST_BENCHMARK_DIMENSION_FIX.md` - 之前的维度加载修复文档

---

**状态**: ✅ 已实现  
**优先级**: 中  
**类型**: 功能优化
