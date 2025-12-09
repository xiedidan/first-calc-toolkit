<template>
  <el-dialog
    v-model="dialogVisible"
    title="新建分析报告"
    width="1000px"
    top="5vh"
    append-to-body
    destroy-on-close
    @open="loadDepartments"
  >
    <div v-loading="loading" class="report-create-content">
      <!-- 基本信息 -->
      <div class="section">
        <h3 class="section-title">基本信息</h3>
        <el-form
          ref="formRef"
          :model="formData"
          :rules="rules"
          label-width="100px"
        >
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="科室" prop="department_id">
                <el-select
                  v-model="formData.department_id"
                  placeholder="请选择科室"
                  filterable
                  style="width: 100%"
                  @change="handleSelectionChange"
                >
                  <el-option
                    v-for="dept in departments"
                    :key="dept.id"
                    :label="`${dept.his_code} - ${dept.his_name}`"
                    :value="dept.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="年月" prop="period">
                <el-date-picker
                  v-model="formData.period"
                  type="month"
                  placeholder="选择月份"
                  format="YYYY-MM"
                  value-format="YYYY-MM"
                  style="width: 100%"
                  @change="handleSelectionChange"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>

      <!-- 科室主业价值分布（只读） -->
      <div class="section">
        <h3 class="section-title">科室主业价值分布（只读）</h3>
        <div v-if="!formData.department_id || !formData.period" class="data-placeholder">
          请先选择科室和年月
        </div>
        <template v-else>
          <el-table
            v-loading="previewLoading"
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
        </template>
      </div>

      <!-- 科室业务内涵展示（只读） -->
      <div class="section">
        <h3 class="section-title">科室业务内涵展示（只读）</h3>
        <div v-if="!formData.department_id || !formData.period" class="data-placeholder">
          请先选择科室和年月
        </div>
        <template v-else>
          <div v-loading="previewLoading">
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
        </template>
      </div>

      <!-- 当前存在问题（可编辑） -->
      <div class="section">
        <h3 class="section-title">
          当前存在问题
          <span class="char-count" :class="{ 'over-limit': currentIssuesLength > 2000 }">
            {{ currentIssuesLength }}/2000
          </span>
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
          未来发展计划
          <span class="char-count" :class="{ 'over-limit': futurePlansLength > 2000 }">
            {{ futurePlansLength }}/2000
          </span>
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
      <el-button type="primary" :loading="saving" @click="handleCreate">
        创建
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
import { ref, reactive, computed } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import request from '@/utils/request'
import {
  createAnalysisReport,
  previewValueDistribution,
  previewBusinessContent,
  previewDimensionDrillDown,
  type ValueDistributionItem,
  type DimensionBusinessContent,
  type DimensionDrillDownItem
} from '@/api/analysis-reports'

interface Department {
  id: number
  his_code: string
  his_name: string
}

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'created'): void
}>()

const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
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

const formRef = ref<FormInstance>()
const loading = ref(false)
const saving = ref(false)
const previewLoading = ref(false)
const departments = ref<Department[]>([])

// 预览数据
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
  if (!formData.department_id || !formData.period) return
  
  drillDownVisible.value = true
  drillDownLoading.value = true
  drillDownData.value = null
  
  try {
    const res = await previewDimensionDrillDown(formData.department_id, formData.period, row.node_id || 0)
    drillDownData.value = res
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载下钻数据失败')
    drillDownVisible.value = false
  } finally {
    drillDownLoading.value = false
  }
}

const formData = reactive({
  department_id: null as number | null,
  period: '',
  current_issues: '',
  future_plans: ''
})

const rules: FormRules = {
  department_id: [
    { required: true, message: '请选择科室', trigger: 'change' }
  ],
  period: [
    { required: true, message: '请选择年月', trigger: 'change' }
  ]
}

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

// 加载科室列表
const loadDepartments = async () => {
  // 重置表单
  formData.department_id = null
  formData.period = ''
  formData.current_issues = ''
  formData.future_plans = ''
  currentIssuesError.value = ''
  futurePlansError.value = ''
  
  // 重置预览数据
  valueDistribution.value = []
  valueDistributionMessage.value = null
  businessContentDimensions.value = []
  businessContentMessage.value = null
  
  loading.value = true
  try {
    // 获取所有参与评估的科室
    const res = await request.get('/departments', {
      params: {
        page: 1,
        size: 1000,
        is_active: true,
        sort_by: 'sort_order',
        sort_order: 'asc'
      }
    })
    departments.value = res.items
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载科室列表失败')
  } finally {
    loading.value = false
  }
}

// 当科室或年月变化时加载预览数据
const handleSelectionChange = async () => {
  // 清空之前的预览数据
  valueDistribution.value = []
  valueDistributionMessage.value = null
  businessContentDimensions.value = []
  businessContentMessage.value = null
  
  // 如果科室和年月都已选择，加载预览数据
  if (formData.department_id && formData.period) {
    await loadPreviewData()
  }
}

// 加载预览数据
const loadPreviewData = async () => {
  if (!formData.department_id || !formData.period) return
  
  previewLoading.value = true
  try {
    // 并行加载价值分布和业务内涵
    const [valueRes, contentRes] = await Promise.all([
      previewValueDistribution(formData.department_id, formData.period),
      previewBusinessContent(formData.department_id, formData.period)
    ])
    
    valueDistribution.value = valueRes.items || []
    valueDistributionMessage.value = valueRes.message
    
    businessContentDimensions.value = contentRes.dimensions || []
    businessContentMessage.value = contentRes.message
  } catch (error: any) {
    console.error('加载预览数据失败:', error)
    valueDistributionMessage.value = '加载价值分布数据失败'
    businessContentMessage.value = '加载业务内涵数据失败'
  } finally {
    previewLoading.value = false
  }
}

// 格式化数字（处理字符串或数字类型）
const formatNumber = (value: number | string | null | undefined) => {
  if (value === null || value === undefined) return '-'
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return '-'
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// 创建报告
const handleCreate = async () => {
  if (!formRef.value) return
  
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  // 验证 Markdown 内容长度
  validateCurrentIssues()
  validateFuturePlans()
  
  if (currentIssuesError.value || futurePlansError.value) {
    ElMessage.warning('请修正表单错误后再创建')
    return
  }
  
  saving.value = true
  try {
    await createAnalysisReport({
      department_id: formData.department_id!,
      period: formData.period,
      current_issues: formData.current_issues || null,
      future_plans: formData.future_plans || null
    })
    
    ElMessage.success('创建成功')
    emit('created')
    dialogVisible.value = false
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '创建失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.report-create-content {
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

.char-count {
  font-size: 12px;
  font-weight: normal;
  color: #909399;
}

.char-count.over-limit {
  color: #f56c6c;
}

.data-placeholder {
  padding: 20px;
  text-align: center;
  color: #909399;
  background-color: #f5f7fa;
  border-radius: 4px;
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
