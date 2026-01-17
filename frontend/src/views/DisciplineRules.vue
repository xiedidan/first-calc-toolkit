<template>
  <div class="discipline-rules-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>学科规则管理</span>
          <div>
            <el-button type="danger" @click="handleBatchDelete" :loading="batchDeleting" :disabled="pagination.total === 0">删除筛选结果</el-button>
            <el-button @click="handleExport" :loading="exporting">导出</el-button>
            <el-button type="primary" @click="handleAdd">添加学科规则</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="模型版本">
          <el-select
            v-model="searchForm.version_id"
            placeholder="全部"
            clearable
            filterable
            @change="handleSearch"
            @clear="handleSearch"
            style="width: 200px"
          >
            <el-option
              v-for="version in versions"
              :key="version.id"
              :label="version.name"
              :value="version.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="科室">
          <el-select
            v-model="searchForm.department_code"
            placeholder="全部"
            clearable
            filterable
            @change="handleSearch"
            @clear="handleSearch"
            style="width: 200px"
          >
            <el-option
              v-for="dept in filteredDepartments"
              :key="dept.accounting_unit_code"
              :label="dept.accounting_unit_name || dept.his_name"
              :value="dept.accounting_unit_code"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="维度">
          <el-select
            v-model="searchForm.dimension_code"
            placeholder="全部"
            clearable
            filterable
            @change="handleSearch"
            @clear="handleSearch"
            style="width: 320px"
          >
            <el-option
              v-for="dim in dimensions"
              :key="dim.code"
              :label="dim.name"
              :value="dim.code"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="科室名称/维度名称/规则描述"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
            @input="handleKeywordInput"
            style="width: 220px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="tableData" border stripe v-loading="loading">
        <template #empty>
          <el-empty :description="loading ? '加载中...' : getEmptyDescription()" :image-size="100" />
        </template>
        <el-table-column prop="version_name" label="模型版本" width="160" show-overflow-tooltip />
        <el-table-column prop="department_name" label="科室名称" width="150" show-overflow-tooltip />
        <el-table-column prop="dimension_name" label="维度名称" min-width="280" show-overflow-tooltip />
        <el-table-column prop="rule_description" label="规则描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="rule_coefficient" label="规则参数" width="120" align="right">
          <template #default="{ row }">
            {{ formatCoefficient(row.rule_coefficient) }}
          </template>
        </el-table-column>
        <el-table-column label="业务分析" min-width="300" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="hasAnalysis(row)" class="analysis-content">
              {{ getAnalysisContent(row) }}
            </span>
            <span v-else class="no-analysis">暂无分析</span>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="fetchDisciplineRules"
        class="pagination"
      />
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      append-to-body
      @close="handleDialogClose"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="模型版本" prop="version_id">
          <el-select
            v-model="form.version_id"
            placeholder="请选择模型版本"
            filterable
            style="width: 100%"
            @change="handleVersionChange"
            :disabled="isEdit"
          >
            <el-option
              v-for="version in versions"
              :key="version.id"
              :label="version.name"
              :value="version.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="科室" prop="department_code">
          <el-select
            v-model="form.department_code"
            placeholder="请选择科室"
            filterable
            style="width: 100%"
            @change="handleDepartmentChange"
          >
            <el-option
              v-for="dept in filteredDepartments"
              :key="dept.accounting_unit_code"
              :label="dept.accounting_unit_name || dept.his_name"
              :value="dept.accounting_unit_code"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="维度" prop="dimension_code">
          <el-select
            v-model="form.dimension_code"
            placeholder="请选择维度（序列 - 一级维度 - 二级维度...）"
            filterable
            :loading="dimensionsLoading"
            style="width: 100%"
            @change="handleDimensionChange"
          >
            <el-option
              v-for="dim in dimensions"
              :key="dim.code"
              :label="dim.name"
              :value="dim.code"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="规则参数" prop="rule_coefficient">
          <el-input-number
            v-model="form.rule_coefficient"
            :min="0"
            :max="100"
            :precision="4"
            :step="0.1"
            placeholder="请输入规则参数"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="规则描述" prop="rule_description">
          <el-input
            v-model="form.rule_description"
            type="textarea"
            :rows="3"
            placeholder="请输入规则描述"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import request from '@/utils/request'
import {
  getDisciplineRules,
  createDisciplineRule,
  updateDisciplineRule,
  deleteDisciplineRule,
  exportDisciplineRules,
  batchDeleteDisciplineRules,
  type DisciplineRule
} from '@/api/discipline-rules'
import { batchQueryByDeptAndDimCodes, type DimensionAnalysisByCodesItem } from '@/api/dimension-analyses'
import type { ModelVersion } from '@/api/model'


// ==================== 工具函数 ====================

function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null
  return function (this: any, ...args: Parameters<T>) {
    const context = this
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => {
      func.apply(context, args)
    }, wait)
  }
}

// ==================== 接口定义 ====================

interface Department {
  id: number
  his_code: string
  his_name: string
  accounting_unit_code: string | null
  accounting_unit_name: string | null
}

interface Dimension {
  id: number
  code: string
  name: string
}

// ==================== 响应式数据 ====================

const loading = ref(false)
const submitting = ref(false)
const exporting = ref(false)
const batchDeleting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const dialogTitle = ref('添加学科规则')
const formRef = ref<FormInstance>()

// 下拉选项数据
const versions = ref<ModelVersion[]>([])
const departments = ref<Department[]>([])
const dimensions = ref<Dimension[]>([])
const dimensionsLoading = ref(false)
const loadedDimensionVersionId = ref<number | undefined>(undefined)  // 缓存已加载的版本ID

// 过滤有核算单元代码的科室（学科规则使用核算单元代码）
const filteredDepartments = computed(() => {
  return departments.value.filter(d => d.accounting_unit_code)
})

// 搜索表单
const searchForm = reactive({
  version_id: undefined as number | undefined,
  department_code: '',
  dimension_code: '',
  keyword: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 表格数据
const tableData = ref<DisciplineRule[]>([])

// 业务分析数据
const analysisMap = ref<Record<string, DimensionAnalysisByCodesItem>>({})

// 表单数据
const form = reactive({
  id: 0,
  department_code: '',
  department_name: '',
  version_id: undefined as number | undefined,
  dimension_code: '',
  dimension_name: '',
  rule_description: '',
  rule_coefficient: 1.0
})

// 表单验证规则
const rules = {
  version_id: [
    { required: true, message: '请选择模型版本', trigger: 'change' }
  ],
  department_code: [
    { required: true, message: '请选择科室', trigger: 'change' }
  ],
  dimension_code: [
    { required: true, message: '请选择维度', trigger: 'change' }
  ],
  rule_coefficient: [
    { required: true, message: '请输入规则参数', trigger: 'blur' },
    { type: 'number', min: 0, max: 100, message: '规则参数必须在0-100之间', trigger: ['blur', 'change'] }
  ]
}

// ==================== 数据加载 ====================

const fetchDisciplineRules = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      size: pagination.size
    }
    if (searchForm.version_id) params.version_id = searchForm.version_id
    if (searchForm.department_code) params.department_code = searchForm.department_code
    if (searchForm.dimension_code) params.dimension_code = searchForm.dimension_code
    if (searchForm.keyword) params.keyword = searchForm.keyword

    const res = await getDisciplineRules(params)
    tableData.value = res.items || []
    pagination.total = res.total || 0
    
    // 加载业务分析数据
    await fetchAnalysisData()
  } catch (error: any) {
    console.error('获取学科规则列表失败:', error)
    tableData.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

// 加载业务分析数据
const fetchAnalysisData = async () => {
  if (tableData.value.length === 0) {
    analysisMap.value = {}
    return
  }
  
  try {
    const deptCodes = [...new Set(tableData.value.map(r => r.department_code))]
    const dimCodes = [...new Set(tableData.value.map(r => r.dimension_code))]
    
    const res = await batchQueryByDeptAndDimCodes(deptCodes, dimCodes)
    analysisMap.value = res || {}
  } catch (error: any) {
    console.error('获取业务分析数据失败:', error)
    analysisMap.value = {}
  }
}

// 获取某行的业务分析内容
const getAnalysisContent = (row: DisciplineRule): string => {
  const key = `${row.department_code}|${row.dimension_code}`
  const analysis = analysisMap.value[key]
  
  if (!analysis) return ''
  
  // 优先显示长期分析，其次显示最新的当期分析
  if (analysis.long_term_content) {
    return analysis.long_term_content
  }
  
  if (analysis.current_analyses && analysis.current_analyses.length > 0) {
    // 按月份倒序排列，取最新的
    const sorted = [...analysis.current_analyses].sort((a, b) => b.period.localeCompare(a.period))
    return `[${sorted[0].period}] ${sorted[0].content}`
  }
  
  return ''
}

// 判断是否有业务分析
const hasAnalysis = (row: DisciplineRule): boolean => {
  const key = `${row.department_code}|${row.dimension_code}`
  const analysis = analysisMap.value[key]
  return !!(analysis && (analysis.long_term_content || (analysis.current_analyses && analysis.current_analyses.length > 0)))
}

const fetchVersions = async () => {
  try {
    const res = await request.get('/model-versions', { params: { limit: 1000 } })
    versions.value = res.items || []
    
    // 默认选中激活的版本
    const activeVersion = versions.value.find((v: any) => v.is_active)
    if (activeVersion && !searchForm.version_id) {
      searchForm.version_id = activeVersion.id
    }
  } catch (error: any) {
    console.error('获取模型版本列表失败:', error)
    versions.value = []
  }
}

const fetchDepartments = async () => {
  try {
    const res = await request.get('/departments', { params: { size: 1000 } })
    departments.value = res.items || []
  } catch (error: any) {
    console.error('获取科室列表失败:', error)
    departments.value = []
  }
}

const fetchDimensions = async (versionId?: number, force = false) => {
  try {
    let targetVersionId = versionId
    if (!targetVersionId) {
      const activeVersion = versions.value.find((v: any) => v.is_active)
      targetVersionId = activeVersion?.id
    }
    
    if (!targetVersionId) {
      dimensions.value = []
      return
    }
    
    // 如果已经加载过相同版本的维度，且不强制刷新，则跳过
    if (!force && loadedDimensionVersionId.value === targetVersionId && dimensions.value.length > 0) {
      return
    }
    
    dimensionsLoading.value = true
    // 获取该版本的所有叶子维度
    const res = await request.get(`/model-nodes/version/${targetVersionId}/leaf-dimensions`)
    dimensions.value = res.items || []
    loadedDimensionVersionId.value = targetVersionId
  } catch (error: any) {
    console.error('获取维度列表失败:', error)
    dimensions.value = []
  } finally {
    dimensionsLoading.value = false
  }
}

// ==================== 事件处理 ====================

const handleSearch = () => {
  pagination.page = 1
  fetchDisciplineRules()
}

const debouncedSearch = debounce(() => {
  handleSearch()
}, 500)

const handleKeywordInput = () => {
  debouncedSearch()
}

const handleReset = () => {
  // 重置时保留激活版本
  const activeVersion = versions.value.find((v: any) => v.is_active)
  searchForm.version_id = activeVersion?.id
  searchForm.department_code = ''
  searchForm.dimension_code = ''
  searchForm.keyword = ''
  handleSearch()
}

const handleExport = async () => {
  exporting.value = true
  try {
    const response = await exportDisciplineRules({
      version_id: searchForm.version_id,
      department_code: searchForm.department_code || undefined,
      dimension_code: searchForm.dimension_code || undefined,
      keyword: searchForm.keyword || undefined
    }) as any
    
    // axios 拦截器对 blob 响应返回完整 response 对象
    const blob = response.data || response
    
    // 从响应头获取文件名，如果没有则使用默认名称
    let filename = '学科规则.xlsx'
    const contentDisposition = response.headers?.['content-disposition']
    if (contentDisposition) {
      const match = contentDisposition.match(/filename\*=UTF-8''(.+)/)
      if (match) {
        filename = decodeURIComponent(match[1])
      }
    }
    
    // 创建下载链接
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error: any) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

const handleBatchDelete = async () => {
  // 构建筛选条件描述
  const conditions: string[] = []
  if (searchForm.version_id) {
    const version = versions.value.find(v => v.id === searchForm.version_id)
    if (version) conditions.push(`版本: ${version.name}`)
  }
  if (searchForm.department_code) {
    const dept = departments.value.find(d => d.accounting_unit_code === searchForm.department_code)
    if (dept) conditions.push(`科室: ${dept.accounting_unit_name || dept.his_name}`)
  }
  if (searchForm.dimension_code) {
    const dim = dimensions.value.find(d => d.code === searchForm.dimension_code)
    if (dim) conditions.push(`维度: ${dim.name}`)
  }
  if (searchForm.keyword) {
    conditions.push(`关键词: ${searchForm.keyword}`)
  }
  
  const conditionText = conditions.length > 0 
    ? `\n筛选条件：${conditions.join('，')}`
    : '（无筛选条件，将删除全部数据）'
  
  try {
    await ElMessageBox.confirm(
      `确定要删除筛选出的 ${pagination.total} 条学科规则吗？${conditionText}\n\n此操作不可恢复！`,
      '批量删除确认',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    batchDeleting.value = true
    const res = await batchDeleteDisciplineRules({
      version_id: searchForm.version_id,
      department_code: searchForm.department_code || undefined,
      dimension_code: searchForm.dimension_code || undefined,
      keyword: searchForm.keyword || undefined
    })
    
    ElMessage.success(`成功删除 ${res.deleted_count} 条学科规则`)
    pagination.page = 1
    fetchDisciplineRules()
  } catch (error: any) {
    if (error === 'cancel') return
    console.error('批量删除失败:', error)
  } finally {
    batchDeleting.value = false
  }
}

const handleSizeChange = () => {
  pagination.page = 1
  fetchDisciplineRules()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '添加学科规则'
  // 默认选中激活版本
  const activeVersion = versions.value.find((v: any) => v.is_active)
  Object.assign(form, {
    id: 0,
    department_code: '',
    department_name: '',
    version_id: activeVersion?.id,
    dimension_code: '',
    dimension_name: '',
    rule_description: '',
    rule_coefficient: 1.0
  })
  if (activeVersion) {
    fetchDimensions(activeVersion.id)
  }
  dialogVisible.value = true
}

const handleEdit = (row: DisciplineRule) => {
  isEdit.value = true
  dialogTitle.value = '编辑学科规则'
  Object.assign(form, {
    id: row.id,
    department_code: row.department_code,
    department_name: row.department_name,
    version_id: row.version_id,
    dimension_code: row.dimension_code,
    dimension_name: row.dimension_name,
    rule_description: row.rule_description || '',
    rule_coefficient: Number(row.rule_coefficient)
  })
  fetchDimensions(row.version_id)
  dialogVisible.value = true
}

const handleDelete = async (row: DisciplineRule) => {
  try {
    await ElMessageBox.confirm('确定要删除该学科规则吗？', '提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    
    await deleteDisciplineRule(row.id)
    ElMessage.success('删除成功')
    
    if (tableData.value.length === 1 && pagination.page > 1) {
      pagination.page--
    }
    fetchDisciplineRules()
  } catch (error: any) {
    if (error === 'cancel') return
    console.error('删除学科规则失败:', error)
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    const valid = await formRef.value.validate()
    if (!valid) {
      ElMessage.warning('请填写完整的表单信息')
      return
    }

    submitting.value = true
    
    const submitData = {
      department_code: form.department_code,
      department_name: form.department_name,
      version_id: form.version_id!,
      dimension_code: form.dimension_code,
      dimension_name: form.dimension_name,
      rule_description: form.rule_description || undefined,
      rule_coefficient: form.rule_coefficient
    }

    if (isEdit.value) {
      await updateDisciplineRule(form.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await createDisciplineRule(submitData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchDisciplineRules()
  } catch (error: any) {
    console.error('提交表单失败:', error)
  } finally {
    submitting.value = false
  }
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
  Object.assign(form, {
    id: 0,
    department_code: '',
    department_name: '',
    version_id: undefined,
    dimension_code: '',
    dimension_name: '',
    rule_description: '',
    rule_coefficient: 1.0
  })
}

const handleVersionChange = (id: number) => {
  // 重新加载该版本的维度
  fetchDimensions(id)
  // 清空已选择的维度
  form.dimension_code = ''
  form.dimension_name = ''
}

const handleDepartmentChange = (code: string) => {
  const dept = departments.value.find(d => d.accounting_unit_code === code)
  if (dept) {
    form.department_name = dept.accounting_unit_name || dept.his_name
  }
}

const handleDimensionChange = (code: string) => {
  const dim = dimensions.value.find(d => d.code === code)
  if (dim) {
    form.dimension_name = dim.name
  }
}

const formatCoefficient = (value: number) => {
  return Number(value).toFixed(4)
}

const getEmptyDescription = () => {
  const hasFilters = searchForm.version_id || 
                     searchForm.department_code || 
                     searchForm.dimension_code || 
                     searchForm.keyword
  
  if (hasFilters) {
    return '未找到符合条件的数据，请尝试调整筛选条件'
  }
  
  return '暂无学科规则数据，点击"添加学科规则"按钮创建'
}

// ==================== 生命周期 ====================

onMounted(async () => {
  try {
    // 并行加载所有初始数据，不等待维度（维度只在对话框中需要）
    const [versionsResult] = await Promise.all([
      fetchVersions(),
      fetchDepartments(),
      fetchDisciplineRules()  // 先不带版本筛选，快速显示数据
    ])
    
    // 版本加载完成后，如果有激活版本，重新加载带筛选的列表
    if (searchForm.version_id) {
      fetchDisciplineRules()
    }
  } catch (error: any) {
    console.error('页面初始化失败:', error)
    ElMessage.error('页面初始化失败，请刷新页面重试')
  }
})
</script>

<style scoped>
.discipline-rules-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}

.analysis-content {
  color: #606266;
  font-size: 13px;
}

.no-analysis {
  color: #c0c4cc;
  font-size: 13px;
}
</style>
