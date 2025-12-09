<template>
  <el-dialog
    v-model="dialogVisible"
    :title="dialogTitle"
    width="1000px"
    top="5vh"
    append-to-body
    destroy-on-close
    @open="loadData"
  >
    <div v-loading="loading" class="report-edit-content">
      <!-- 科室主业价值分布（只读） -->
      <div class="section">
        <h3 class="section-title">科室主业价值分布（只读）</h3>
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

      <!-- 科室业务内涵展示（只读） -->
      <div class="section">
        <h3 class="section-title">科室业务内涵展示（只读）</h3>
        
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

      <!-- 当前存在问题（可编辑） -->
      <div class="section">
        <h3 class="section-title">
          <span>当前存在问题</span>
          <div class="title-actions">
            <el-button
              type="primary"
              size="small"
              :loading="generatingIssues"
              @click="generateIssues"
            >
              <el-icon><MagicStick /></el-icon>
              智能分析
            </el-button>
            <span class="char-count" :class="{ 'over-limit': currentIssuesLength > 2000 }">
              {{ currentIssuesLength }}/2000
            </span>
          </div>
        </h3>
        <MdEditor
          v-model="formData.current_issues"
          language="zh-CN"
          :toolbars="toolbars"
          :preview="true"
          previewTheme="default"
          style="height: 300px"
          @onChange="validateCurrentIssues"
        />
        <div v-if="currentIssuesError" class="error-message">
          {{ currentIssuesError }}
        </div>
      </div>

      <!-- 未来发展计划（可编辑） -->
      <div class="section">
        <h3 class="section-title">
          <span>未来发展计划</span>
          <div class="title-actions">
            <el-button
              type="primary"
              size="small"
              :loading="generatingPlans"
              @click="generatePlans"
            >
              <el-icon><MagicStick /></el-icon>
              智能分析
            </el-button>
            <span class="char-count" :class="{ 'over-limit': futurePlansLength > 2000 }">
              {{ futurePlansLength }}/2000
            </span>
          </div>
        </h3>
        <MdEditor
          v-model="formData.future_plans"
          language="zh-CN"
          :toolbars="toolbars"
          :preview="true"
          previewTheme="default"
          style="height: 300px"
          @onChange="validateFuturePlans"
        />
        <div v-if="futurePlansError" class="error-message">
          {{ futurePlansError }}
        </div>
      </div>
    </div>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSave">
        保存
      </el-button>
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
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MagicStick } from '@element-plus/icons-vue'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import {
  getValueDistribution,
  getBusinessContent,
  updateAnalysisReport,
  getDimensionDrillDown,
  type AnalysisReport,
  type ValueDistributionItem,
  type DimensionBusinessContent,
  type DimensionDrillDownItem
} from '@/api/analysis-reports'
import { generateReportContent } from '@/api/ai-prompt-config'

const props = defineProps<{
  visible: boolean
  report: AnalysisReport | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'saved'): void
}>()

const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const dialogTitle = computed(() => {
  if (!props.report) return '编辑报告'
  return `编辑 ${props.report.department_name} - ${props.report.period} 分析报告`
})

// 工具栏配置
const toolbars = [
  'bold',
  'underline',
  'italic',
  '-',
  'strikeThrough',
  'title',
  'sub',
  'sup',
  'quote',
  'unorderedList',
  'orderedList',
  '-',
  'codeRow',
  'code',
  'link',
  'table',
  '-',
  'revoke',
  'next',
  'preview'
]

// 数据
const loading = ref(false)
const saving = ref(false)
const generatingIssues = ref(false)
const generatingPlans = ref(false)
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

// 表单数据
const formData = reactive({
  current_issues: '',
  future_plans: ''
})

// 验证错误
const currentIssuesError = ref('')
const futurePlansError = ref('')

// 字符数计算
const currentIssuesLength = computed(() => formData.current_issues?.length || 0)
const futurePlansLength = computed(() => formData.future_plans?.length || 0)

// 验证当前存在问题
const validateCurrentIssues = () => {
  if (currentIssuesLength.value > 2000) {
    currentIssuesError.value = '内容长度不能超过2000字符'
  } else {
    currentIssuesError.value = ''
  }
}

// 验证未来发展计划
const validateFuturePlans = () => {
  if (futurePlansLength.value > 2000) {
    futurePlansError.value = '内容长度不能超过2000字符'
  } else {
    futurePlansError.value = ''
  }
}

// 加载数据
const loadData = async () => {
  if (!props.report) return
  
  // 初始化表单数据
  formData.current_issues = props.report.current_issues || ''
  formData.future_plans = props.report.future_plans || ''
  currentIssuesError.value = ''
  futurePlansError.value = ''
  
  loading.value = true
  try {
    // 并行加载价值分布和业务内涵
    const [valueRes, contentRes] = await Promise.all([
      getValueDistribution(props.report.id),
      getBusinessContent(props.report.id)
    ])
    
    valueDistribution.value = valueRes.items || []
    valueDistributionMessage.value = valueRes.message
    
    businessContentDimensions.value = contentRes.dimensions || []
    businessContentMessage.value = contentRes.message
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载报告数据失败')
  } finally {
    loading.value = false
  }
}

// 智能生成当前存在问题
const generateIssues = async () => {
  if (!props.report) return
  
  // 如果已有内容，提示确认
  if (formData.current_issues) {
    try {
      await ElMessageBox.confirm(
        '当前已有内容，智能分析将覆盖现有内容，是否继续？',
        '提示',
        {
          confirmButtonText: '继续',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
    } catch {
      return
    }
  }
  
  generatingIssues.value = true
  try {
    const result = await generateReportContent({
      report_id: props.report.id,
      category: 'report_issues'
    })
    
    if (result.success && result.content) {
      formData.current_issues = result.content
      ElMessage.success(`智能分析完成，耗时 ${result.duration?.toFixed(1) || 0} 秒`)
    } else {
      ElMessage.error(result.error || '智能分析失败')
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '智能分析失败')
  } finally {
    generatingIssues.value = false
  }
}

// 智能生成未来发展计划
const generatePlans = async () => {
  if (!props.report) return
  
  // 如果已有内容，提示确认
  if (formData.future_plans) {
    try {
      await ElMessageBox.confirm(
        '当前已有内容，智能分析将覆盖现有内容，是否继续？',
        '提示',
        {
          confirmButtonText: '继续',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
    } catch {
      return
    }
  }
  
  generatingPlans.value = true
  try {
    const result = await generateReportContent({
      report_id: props.report.id,
      category: 'report_plans'
    })
    
    if (result.success && result.content) {
      formData.future_plans = result.content
      ElMessage.success(`智能分析完成，耗时 ${result.duration?.toFixed(1) || 0} 秒`)
    } else {
      ElMessage.error(result.error || '智能分析失败')
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '智能分析失败')
  } finally {
    generatingPlans.value = false
  }
}

// 保存
const handleSave = async () => {
  if (!props.report) return
  
  // 验证
  validateCurrentIssues()
  validateFuturePlans()
  
  if (currentIssuesError.value || futurePlansError.value) {
    ElMessage.warning('请修正表单错误后再保存')
    return
  }
  
  saving.value = true
  try {
    await updateAnalysisReport(props.report.id, {
      current_issues: formData.current_issues || null,
      future_plans: formData.future_plans || null
    })
    
    ElMessage.success('保存成功')
    emit('saved')
    dialogVisible.value = false
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

// 格式化数字（处理字符串或数字类型）
const formatNumber = (value: number | string | null | undefined) => {
  if (value === null || value === undefined) return '-'
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return '-'
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// 监听 report 变化，重置数据
watch(() => props.report, () => {
  valueDistribution.value = []
  valueDistributionMessage.value = null
  businessContentDimensions.value = []
  businessContentMessage.value = null
  formData.current_issues = ''
  formData.future_plans = ''
})
</script>

<style scoped>
.report-edit-content {
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
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.char-count {
  font-size: 12px;
  font-weight: normal;
  color: #909399;
}

.char-count.over-limit {
  color: #f56c6c;
}

.data-message {
  margin-top: 8px;
  color: #909399;
  font-size: 13px;
}

.error-message {
  margin-top: 4px;
  color: #f56c6c;
  font-size: 12px;
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
</style>
