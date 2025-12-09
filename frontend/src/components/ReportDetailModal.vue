<template>
  <el-dialog
    :model-value="props.visible"
    :title="dialogTitle"
    width="900px"
    top="5vh"
    append-to-body
    destroy-on-close
    @update:model-value="(val) => emit('update:visible', val)"
  >
    <div v-loading="loading" class="report-detail-content">
      <!-- 科室主业价值分布 -->
      <div class="section">
        <h3 class="section-title">科室主业价值分布</h3>
        <el-table
          :data="valueDistribution"
          border
          stripe
          size="small"
        >
          <el-table-column prop="rank" label="排名" width="60" align="center" />
          <el-table-column prop="dimension_name" label="维度名称" min-width="200" />
          <el-table-column prop="workload" label="工作量金额" width="150" align="right">
            <template #default="{ row }">
              {{ formatNumber(row.workload) }}
            </template>
          </el-table-column>
          <el-table-column prop="value" label="业务价值" width="150" align="right">
            <template #default="{ row }">
              {{ formatNumber(row.value) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="center">
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
        </el-table>
        <div v-if="valueDistributionMessage" class="data-message">
          {{ valueDistributionMessage }}
        </div>
      </div>

      <!-- 科室业务内涵展示 -->
      <div class="section">
        <h3 class="section-title">科室业务内涵展示</h3>
        
        <!-- 按维度分组显示 -->
        <template v-if="businessContentDimensions.length > 0">
          <div v-for="(dim, index) in businessContentDimensions" :key="index" class="dimension-section">
            <h4 class="dimension-title">{{ dim.dimension_name }}</h4>
            <el-table
              :data="dim.items"
              border
              stripe
              size="small"
            >
              <el-table-column prop="item_code" label="项目编码" width="120" />
              <el-table-column prop="item_name" label="项目名称" min-width="200" show-overflow-tooltip />
              <el-table-column prop="item_category" label="项目类别" width="100">
                <template #default="{ row }">
                  {{ row.item_category || '-' }}
                </template>
              </el-table-column>
              <el-table-column prop="unit_price" label="单价" width="80" align="right">
                <template #default="{ row }">
                  {{ row.unit_price || '-' }}
                </template>
              </el-table-column>
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
          </div>
        </template>
        
        <div v-if="businessContentMessage" class="data-message">
          {{ businessContentMessage }}
        </div>
      </div>

      <!-- 当前存在问题 -->
      <div class="section">
        <h3 class="section-title">当前存在问题</h3>
        <div v-if="props.report?.current_issues" class="markdown-content" v-html="renderedCurrentIssues"></div>
        <div v-else class="empty-content">暂无内容</div>
      </div>

      <!-- 未来发展计划 -->
      <div class="section">
        <h3 class="section-title">未来发展计划</h3>
        <div v-if="props.report?.future_plans" class="markdown-content" v-html="renderedFuturePlans"></div>
        <div v-else class="empty-content">暂无内容</div>
      </div>
    </div>

    <template #footer>
      <el-button @click="emit('update:visible', false)">关闭</el-button>
    </template>
  </el-dialog>

  <!-- 维度下钻对话框 -->
  <el-dialog
    v-model="drillDownVisible"
    :title="`${drillDownData?.dimension_name || '维度'} - 收费项目明细`"
    width="1000px"
    append-to-body
    destroy-on-close
    @open="resetDrillDownPagination"
  >
    <div v-loading="drillDownLoading" class="drilldown-content">
      <el-table
        :data="paginatedDrillDownItems"
        border
        stripe
        size="small"
      >
        <el-table-column prop="period" label="年月" width="80" />
        <el-table-column prop="department_code" label="科室代码" width="80" />
        <el-table-column prop="department_name" label="科室名称" width="120" />
        <el-table-column prop="item_code" label="项目编码" width="100" />
        <el-table-column prop="item_name" label="项目名称" min-width="160" />
        <el-table-column prop="item_category" label="项目类别" width="80">
          <template #default="{ row }">
            {{ row.item_category || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="unit_price" label="单价" width="70" align="right">
          <template #default="{ row }">
            {{ row.unit_price || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="100" align="right">
          <template #default="{ row }">
            {{ formatNumber(row.amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="80" align="right">
          <template #default="{ row }">
            {{ formatNumber(row.quantity) }}
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div v-if="drillDownData && drillDownData.items.length > 0" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="drillDownCurrentPage"
          v-model:page-size="drillDownPageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="drillDownData.items.length"
          layout="total, sizes, prev, pager, next"
          small
        />
      </div>
      
      <!-- 汇总信息 -->
      <div v-if="drillDownData && drillDownData.items.length > 0" class="summary-info">
        <span>总金额: <strong>{{ formatNumber(drillDownData.total_amount) }}</strong></span>
        <span style="margin-left: 30px;">共 <strong>{{ drillDownData.items.length }}</strong> 条记录</span>
      </div>
      
      <div v-if="drillDownData?.message" class="data-message">
        {{ drillDownData.message }}
      </div>
      
      <el-empty v-if="!drillDownLoading && (!drillDownData?.items || drillDownData.items.length === 0)" description="暂无数据" />
    </div>

    <template #footer>
      <el-button @click="drillDownVisible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import {
  getValueDistribution,
  getBusinessContent,
  getDimensionDrillDown,
  type AnalysisReport,
  type ValueDistributionItem,
  type DimensionBusinessContent,
  type DimensionDrillDownItem
} from '@/api/analysis-reports'

const props = defineProps<{
  visible: boolean
  report: AnalysisReport | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
}>()

const dialogTitle = computed(() => {
  if (!props.report) return '报告详情'
  return `${props.report.department_name} - ${props.report.period} 分析报告`
})

// 数据
const loading = ref(false)
const valueDistribution = ref<ValueDistributionItem[]>([])
const valueDistributionMessage = ref<string | null>(null)
const businessContentDimensions = ref<DimensionBusinessContent[]>([])
const businessContentMessage = ref<string | null>(null)

// 下钻相关
const drillDownVisible = ref(false)
const drillDownLoading = ref(false)
const drillDownData = ref<{
  dimension_name: string
  items: DimensionDrillDownItem[]
  total_amount: number
  total_quantity: number
  message: string | null
} | null>(null)
const drillDownCurrentPage = ref(1)
const drillDownPageSize = ref(10)

// 分页后的下钻数据
const paginatedDrillDownItems = computed(() => {
  if (!drillDownData.value?.items) return []
  const start = (drillDownCurrentPage.value - 1) * drillDownPageSize.value
  const end = start + drillDownPageSize.value
  return drillDownData.value.items.slice(start, end)
})

// 重置下钻分页
const resetDrillDownPagination = () => {
  drillDownCurrentPage.value = 1
  drillDownPageSize.value = 10
}

// Markdown 渲染
const renderedCurrentIssues = computed(() => {
  if (!props.report?.current_issues) return ''
  return marked(props.report.current_issues)
})

const renderedFuturePlans = computed(() => {
  if (!props.report?.future_plans) return ''
  return marked(props.report.future_plans)
})

// 加载数据
const loadData = async () => {
  if (!props.report) return
  
  loading.value = true
  try {
    const [valueRes, contentRes] = await Promise.all([
      getValueDistribution(props.report.id),
      getBusinessContent(props.report.id)
    ])
    
    console.log('报告ID:', props.report.id)
    console.log('价值分布响应:', valueRes)
    
    valueDistribution.value = valueRes.items || []
    valueDistributionMessage.value = valueRes.message
    
    businessContentDimensions.value = contentRes.dimensions || []
    businessContentMessage.value = contentRes.message
  } catch (error: any) {
    console.error('加载报告数据失败:', error)
    ElMessage.error(error.response?.data?.detail || '加载报告数据失败')
  } finally {
    loading.value = false
  }
}

// 格式化数字（处理字符串或数字类型）
const formatNumber = (value: number | string | null | undefined) => {
  if (value === null || value === undefined) return '-'
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return '-'
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// 格式化百分比（处理字符串或数字类型）
const formatPercent = (value: number | string | null | undefined) => {
  if (value === null || value === undefined) return '-'
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return '-'
  return `${num.toFixed(2)}%`
}

// 判断是否可以下钻
const canDrillDown = (row: any) => {
  return row.node_id && row.dimension_name
}

// 处理下钻
const handleDrillDown = async (row: any) => {
  if (!props.report) return
  
  drillDownVisible.value = true
  drillDownLoading.value = true
  drillDownData.value = null
  
  try {
    const res = await getDimensionDrillDown(props.report.id, row.node_id || 0)
    drillDownData.value = res
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载下钻数据失败')
    drillDownVisible.value = false
  } finally {
    drillDownLoading.value = false
  }
}

// 监听 visible 变化，打开时加载数据
watch(() => props.visible, (newVal) => {
  if (newVal && props.report) {
    loadData()
  } else if (!newVal) {
    // 关闭时重置数据
    valueDistribution.value = []
    valueDistributionMessage.value = null
    businessContentDimensions.value = []
    businessContentMessage.value = null
    drillDownVisible.value = false
    drillDownData.value = null
  }
})
</script>


<style scoped>
.report-detail-content {
  /* 不设置 max-height 和 overflow，让 el-dialog 自己处理滚动 */
}

.section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.data-message {
  margin-top: 8px;
  color: #909399;
  font-size: 13px;
}

.markdown-content {
  padding: 12px;
  background-color: #fafafa;
  border-radius: 4px;
  min-height: 60px;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4) {
  margin-top: 16px;
  margin-bottom: 8px;
}

.markdown-content :deep(p) {
  margin-bottom: 8px;
  line-height: 1.6;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  padding-left: 20px;
  margin-bottom: 8px;
}

.markdown-content :deep(li) {
  margin-bottom: 4px;
}

.markdown-content :deep(code) {
  background-color: #f0f0f0;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
}

.markdown-content :deep(pre) {
  background-color: #f0f0f0;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
}

.empty-content {
  padding: 12px;
  background-color: #fafafa;
  border-radius: 4px;
  color: #909399;
  text-align: center;
}

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

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.dimension-section {
  margin-bottom: 20px;
}

.dimension-section:last-child {
  margin-bottom: 0;
}

.dimension-title {
  font-size: 14px;
  font-weight: 500;
  color: #409eff;
  margin-bottom: 8px;
  padding-left: 8px;
  border-left: 3px solid #409eff;
}
</style>
