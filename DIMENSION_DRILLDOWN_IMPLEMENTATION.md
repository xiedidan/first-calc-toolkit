# 维度下钻功能实现总结

## 功能概述

为业务价值明细报表增加末级维度下钻功能，用户可以点击维度查看组成该维度的收费项目明细。

**当前实现范围**：医生序列中按维度目录计算的末级维度（排除病例价值维度）

## 实现内容

### 1. 后端实现

#### 1.1 Schema 更新 (`backend/app/schemas/analysis_report.py`)

新增两个 Schema：

```python
class DimensionDrillDownItem(BaseModel):
    """维度下钻明细项"""
    period: str  # 年月
    department_code: str  # 科室代码
    department_name: str  # 科室名称
    item_code: str  # 项目编码
    item_name: str  # 项目名称
    amount: Decimal  # 金额
    quantity: Decimal  # 数量

class DimensionDrillDownResponse(BaseModel):
    """维度下钻响应"""
    dimension_name: str  # 维度名称
    items: List[DimensionDrillDownItem]  # 明细列表
    total_amount: Decimal  # 总金额
    total_quantity: Decimal  # 总数量
    message: Optional[str]  # 提示信息
```

同时为 `ValueDistributionItem` 添加 `node_id` 字段，用于前端调用下钻接口。

#### 1.2 API 接口 (`backend/app/api/analysis_reports.py`)

新增路由：
```
GET /api/v1/analysis-reports/{report_id}/dimension-drilldown/{node_id}
```

**功能逻辑**：
1. 验证报告存在且用户有权限访问
2. 查找激活版本的最新完成任务
3. 查询该维度节点信息（从 `calculation_results` 表）
4. 验证维度类型：
   - 必须是医生序列维度（`dim-doc-*`）
   - 排除病例价值维度（`dim-doc-case`）
   - 必须是叶子节点（无子节点）
5. 查询维度与收费项目的映射关系（`dimension_item_mappings` 表）
6. 从 `charge_details` 表查询该科室该月份该维度的收费明细
7. 按项目编码分组汇总金额和数量
8. 返回明细列表和汇总信息

**SQL 查询**：
```sql
SELECT 
    item_code,
    item_name,
    SUM(amount) as total_amount,
    SUM(quantity) as total_quantity
FROM charge_details
WHERE prescribing_dept_code = :dept_code
AND TO_CHAR(charge_time, 'YYYY-MM') = :period
AND item_code = ANY(:item_codes)
GROUP BY item_code, item_name
ORDER BY total_amount DESC
```

### 2. 前端实现

#### 2.1 API 类型定义 (`frontend/src/api/analysis-reports.ts`)

新增接口类型：
```typescript
export interface DimensionDrillDownItem {
  period: string
  department_code: string
  department_name: string
  item_code: string
  item_name: string
  amount: number
  quantity: number
}

export interface DimensionDrillDownResponse {
  dimension_name: string
  items: DimensionDrillDownItem[]
  total_amount: number
  total_quantity: number
  message: string | null
}
```

新增 API 方法：
```typescript
export function getDimensionDrillDown(reportId: number, nodeId: number)
```

#### 2.2 详情模态框更新 (`frontend/src/components/ReportDetailModal.vue`)

**价值分布表格增强**：
- 添加"操作"列
- 显示"下钻"按钮（仅对可下钻的维度显示）
- 判断逻辑：维度名称不是"病例价值"

**下钻对话框**：
- 宽度：1000px
- 显示收费项目明细表格（7列）：
  - 年月
  - 科室代码
  - 科室名称
  - 项目编码
  - 项目名称
  - 金额（右对齐，千分位格式）
  - 数量（右对齐，千分位格式）
- 底部显示汇总信息：总金额、总数量
- 最大高度：500px，超出滚动

### 3. 测试脚本

创建 `test_dimension_drilldown.py`：
1. 登录获取 token
2. 获取报告列表
3. 获取价值分布数据
4. 测试下钻前两个维度
5. 显示明细数据和汇总信息

## 使用说明

### 用户操作流程

1. 进入"报告查看"页面
2. 点击某个报告的"查看详情"
3. 在"科室主业价值分布"表格中，找到想要下钻的维度
4. 点击该维度行的"下钻"按钮
5. 弹出对话框显示该维度的收费项目明细
6. 查看明细数据和汇总信息
7. 关闭对话框返回报告详情

### 限制条件

1. **序列限制**：仅支持医生序列的维度
2. **维度类型限制**：排除病例价值维度（因为病例价值不是按收费项目计算的）
3. **层级限制**：仅支持末级维度（叶子节点）
4. **数据依赖**：
   - 需要存在维度与收费项目的映射关系
   - 需要存在该科室该月份的收费明细数据

### 错误处理

- 报告不存在或无权限：404
- 维度不存在：404
- 非医生序列维度：400（提示仅支持医生序列维度）
- 病例价值维度：400（提示不支持该维度）
- 非叶子节点：400（提示该维度不是末级维度）
- 无映射关系：返回空列表，提示"未找到映射关系"
- 无收费明细：返回空列表，提示"未找到收费明细数据"
- 查询失败：500（显示错误信息）

## 数据流

```
用户点击下钻
    ↓
前端调用 getDimensionDrillDown(reportId, nodeId)
    ↓
后端验证权限和参数
    ↓
查询 calculation_results 获取维度信息
    ↓
验证维度类型和层级
    ↓
查询 dimension_item_mappings 获取收费项目映射
    ↓
查询 charge_details 获取收费明细
    ↓
按项目编码分组汇总
    ↓
返回明细列表和汇总信息
    ↓
前端显示下钻对话框
```

## 扩展建议

### 短期扩展

1. **支持更多序列**：
   - 护理序列维度下钻
   - 医技序列维度下钻

2. **导出功能**：
   - 导出下钻明细为 Excel
   - 包含汇总信息

3. **筛选和排序**：
   - 按金额/数量排序
   - 按项目编码/名称搜索

### 长期扩展

1. **多级下钻**：
   - 支持非叶子节点下钻（显示子维度）
   - 支持从子维度继续下钻到收费项目

2. **可视化**：
   - 饼图显示项目占比
   - 柱状图显示 Top 项目

3. **对比分析**：
   - 同一维度不同月份对比
   - 同一维度不同科室对比

## 测试清单

- [ ] 登录并访问报告详情
- [ ] 价值分布表格显示"下钻"按钮
- [ ] 点击下钻按钮打开对话框
- [ ] 对话框显示正确的维度名称
- [ ] 明细表格显示收费项目数据
- [ ] 金额和数量格式正确（千分位）
- [ ] 汇总信息计算正确
- [ ] 测试无映射关系的维度
- [ ] 测试无收费明细的维度
- [ ] 测试病例价值维度（应提示不支持）
- [ ] 测试非叶子节点（应提示不是末级维度）
- [ ] 测试权限控制（科室用户只能看自己科室）

## 相关文件

### 后端
- `backend/app/schemas/analysis_report.py` - Schema 定义
- `backend/app/api/analysis_reports.py` - API 接口
- `backend/app/models/calculation_task.py` - CalculationResult 模型
- `backend/app/models/dimension_item_mapping.py` - 映射关系模型

### 前端
- `frontend/src/api/analysis-reports.ts` - API 调用
- `frontend/src/components/ReportDetailModal.vue` - 详情模态框
- `frontend/src/views/ReportView.vue` - 报告查看页面

### 测试
- `test_dimension_drilldown.py` - 功能测试脚本

## 注意事项

1. **性能考虑**：
   - charge_details 表可能数据量很大，已添加索引优化查询
   - 按科室代码、时间、项目编码建立了索引

2. **数据一致性**：
   - 下钻数据来自 charge_details 表
   - 价值分布数据来自 calculation_results 表
   - 两者的数据源和计算逻辑应保持一致

3. **前端性能**：
   - 下钻对话框使用 `destroy-on-close` 避免内存泄漏
   - 表格设置 `max-height` 避免数据过多时页面卡顿

4. **用户体验**：
   - 加载时显示 loading 状态
   - 错误时显示友好的提示信息
   - 无数据时显示提示信息而非空表格
