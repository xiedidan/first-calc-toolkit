# Results.vue 下钻功能补丁说明

## 需要修改的内容

### 1. 在 script 部分导入下钻 API

在文件顶部的 import 语句中添加：

```typescript
import { getDimensionDrillDownByTask, type DimensionDrillDownItem, type DimensionDrillDownResponse } from '@/api/analysis-reports'
```

### 2. 添加下钻相关的响应式变量

在现有的 ref 变量后添加：

```typescript
// 下钻相关
const drillDownVisible = ref(false)
const drillDownLoading = ref(false)
const drillDownData = ref<DimensionDrillDownResponse | null>(null)
```

### 3. 添加下钻相关的函数

在现有函数后添加：

```typescript
// 判断是否可以下钻
const canDrillDown = (row: any) => {
  // 只有叶子节点（没有children）才能下钻
  return row.node_id && !row.children
}

// 处理下钻
const handleDrillDown = async (row: any) => {
  if (!selectedTaskId.value || !currentDepartment.value) return
  
  drillDownVisible.value = true
  drillDownLoading.value = true
  drillDownData.value = null
  
  try {
    const res = await getDimensionDrillDownByTask(
      selectedTaskId.value,
      currentDepartment.value.department_id,
      row.node_id
    )
    drillDownData.value = res
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载下钻数据失败')
    drillDownVisible.value = false
  } finally {
    drillDownLoading.value = false
  }
}
```

### 4. 在医生序列表格中添加操作列

在医生序列的 `el-table` 中，在最后一个 `el-table-column` 后添加：

```vue
<el-table-column label="操作" width="100" align="center" fixed="right">
  <template #default="{ row }">
    <el-button
      v-if="canDrillDown(row)"
      link
      type="primary"
      size="small"
      @click="handleDrillDown(row)"
    >
      下钻
    </el-button>
  </template>
</el-table-column>
```

### 5. 在护理序列和医技序列表格中也添加相同的操作列

复制上面的操作列代码，分别添加到护理序列和医技序列的表格中。

### 6. 在明细对话框后添加下钻对话框

在现有的明细对话框 `</el-dialog>` 标签后添加：

```vue
<!-- 下钻对话框 -->
<el-dialog
  v-model="drillDownVisible"
  :title="`${drillDownData?.dimension_name || '维度'} - 收费项目明细`"
  width="1000px"
  append-to-body
  destroy-on-close
>
  <div v-loading="drillDownLoading" class="drilldown-content">
    <el-table
      :data="drillDownData?.items || []"
      border
      stripe
      size="small"
      max-height="500"
    >
      <el-table-column prop="period" label="年月" width="100" />
      <el-table-column prop="department_code" label="科室代码" width="100" />
      <el-table-column prop="department_name" label="科室名称" width="150" />
      <el-table-column prop="item_code" label="项目编码" width="120" />
      <el-table-column prop="item_name" label="项目名称" min-width="200" />
      <el-table-column prop="amount" label="金额" width="120" align="right">
        <template #default="{ row }">
          {{ formatNumber(row.amount) }}
        </template>
      </el-table-column>
      <el-table-column prop="quantity" label="数量" width="100" align="right">
        <template #default="{ row }">
          {{ formatNumber(row.quantity) }}
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 汇总信息 -->
    <div v-if="drillDownData && drillDownData.items.length > 0" class="summary-info">
      <span>总金额: <strong>{{ formatNumber(drillDownData.total_amount) }}</strong></span>
      <span style="margin-left: 30px;">总数量: <strong>{{ formatNumber(drillDownData.total_quantity) }}</strong></span>
    </div>
    
    <div v-if="drillDownData?.message" class="data-message">
      {{ drillDownData.message }}
    </div>
  </div>

  <template #footer>
    <el-button @click="drillDownVisible = false">关闭</el-button>
  </template>
</el-dialog>
```

### 7. 在 style 部分添加下钻对话框样式

在现有样式后添加：

```css
.drilldown-content {
  min-height: 200px;
}

.summary-info {
  margin-top: 16px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-size: 14px;
}

.summary-info strong {
  color: #409eff;
  font-size: 16px;
}

.data-message {
  margin-top: 8px;
  color: #909399;
  font-size: 13px;
}
```

## 修改位置说明

### 医生序列表格位置
找到这段代码：
```vue
<el-tab-pane label="医生序列" name="doctor" v-if="detailData?.doctor && detailData.doctor.length > 0">
  <div class="table-title">{{ currentDepartment?.department_name }} - 医生序列业务价值明细（{{ filterForm.period }}）</div>
  <el-table ...>
    <!-- 现有的列 -->
    <el-table-column prop="amount" label="业务价值金额" min-width="110" align="right">
      <template #default="{ row }">{{ formatNumber(row.amount) }}</template>
    </el-table-column>
    <!-- 在这里添加操作列 -->
  </el-table>
</el-tab-pane>
```

### 护理序列和医技序列
找到类似的结构，在对应位置添加操作列。

## 测试步骤

1. 重启前端开发服务器
2. 登录系统
3. 进入"业务价值报表"页面
4. 点击某个科室的"查看明细"
5. 在医生序列标签页中，应该看到末级维度有"下钻"按钮
6. 点击"下钻"按钮，应该弹出收费项目明细对话框
7. 验证数据显示正确

## 注意事项

1. 只有叶子节点（没有 children 的节点）才显示下钻按钮
2. 目前只支持医生序列的维度下钻
3. 病例价值维度不支持下钻
4. 如果没有映射关系或收费明细数据，会显示相应的提示信息
