<template>
  <div class="cost-benchmarks-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>成本基准管理</span>
          <div>
            <el-button type="success" @click="handleExport" :loading="exporting">
              <el-icon><Download /></el-icon>
              导出Excel
            </el-button>
            <el-button type="primary" @click="handleAdd">添加成本基准</el-button>
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
              v-for="dept in departments"
              :key="dept.his_code"
              :label="dept.his_name"
              :value="dept.his_code"
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
            style="width: 200px"
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
            placeholder="科室名称/维度名称"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
            @input="handleKeywordInput"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table
        :data="tableData"
        border
        stripe
        v-loading="loading"
      >
        <template #empty>
          <el-empty 
            :description="loading ? '加载中...' : getEmptyDescription()" 
            :image-size="100"
          />
        </template>
        <el-table-column prop="department_name" label="科室名称" width="180" show-overflow-tooltip />
        <el-table-column prop="version_name" label="模型版本" width="160" show-overflow-tooltip />
        <el-table-column prop="dimension_name" label="维度名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="benchmark_value" label="基准值" width="140" align="right">
          <template #default="{ row }">
            {{ formatNumber(row.benchmark_value) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
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
        @current-change="fetchCostBenchmarks"
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
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="科室" prop="department_code">
          <el-select
            v-model="form.department_code"
            placeholder="请选择科室"
            filterable
            style="width: 100%"
            @change="handleDepartmentChange"
          >
            <el-option
              v-for="dept in departments"
              :key="dept.his_code"
              :label="dept.his_name"
              :value="dept.his_code"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="模型版本" prop="version_id">
          <el-select
            v-model="form.version_id"
            placeholder="请选择模型版本"
            filterable
            style="width: 100%"
            @change="handleVersionChange"
          >
            <el-option
              v-for="version in versions"
              :key="version.id"
              :label="version.name"
              :value="version.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="维度" prop="dimension_code">
          <el-select
            v-model="form.dimension_code"
            placeholder="请选择维度"
            filterable
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
        <el-form-item label="基准值" prop="benchmark_value">
          <el-input-number
            v-model="form.benchmark_value"
            :min="0.01"
            :precision="2"
            :step="1"
            placeholder="请输入基准值"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import request from '@/utils/request'
import {
  getCostBenchmarks,
  createCostBenchmark,
  updateCostBenchmark,
  deleteCostBenchmark,
  exportCostBenchmarks,
  type CostBenchmark
} from '@/api/cost-benchmarks'
import type { ModelVersion } from '@/api/model'

// ==================== 工具函数 ====================

/**
 * 防抖函数
 */
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
const dialogVisible = ref(false)
const isEdit = ref(false)
const dialogTitle = ref('添加成本基准')
const formRef = ref<FormInstance>()

// 下拉选项数据
const versions = ref<ModelVersion[]>([])
const departments = ref<Department[]>([])
const dimensions = ref<Dimension[]>([])

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
const tableData = ref<CostBenchmark[]>([])

// 表单数据
const form = reactive({
  id: 0,
  department_code: '',
  department_name: '',
  version_id: undefined as number | undefined,
  version_name: '',
  dimension_code: '',
  dimension_name: '',
  benchmark_value: undefined as number | undefined
})

// 表单验证规则
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
      validator: (rule: any, value: any, callback: any) => {
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

// ==================== 数据加载 ====================

/**
 * 获取成本基准列表
 */
const fetchCostBenchmarks = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      size: pagination.size
    }
    if (searchForm.version_id) {
      params.version_id = searchForm.version_id
    }
    if (searchForm.department_code) {
      params.department_code = searchForm.department_code
    }
    if (searchForm.dimension_code) {
      params.dimension_code = searchForm.dimension_code
    }
    if (searchForm.keyword) {
      params.keyword = searchForm.keyword
    }

    const res = await getCostBenchmarks(params)
    tableData.value = res.items || []
    pagination.total = res.total || 0
  } catch (error: any) {
    console.error('获取成本基准列表失败:', error)
    tableData.value = []
    pagination.total = 0
    // 错误消息已由拦截器处理，这里只记录日志
  } finally {
    loading.value = false
  }
}

/**
 * 获取模型版本列表
 */
const fetchVersions = async () => {
  try {
    const res = await request.get('/model-versions', {
      params: { limit: 1000 }
    })
    versions.value = res.items || []
  } catch (error: any) {
    console.error('获取模型版本列表失败:', error)
    versions.value = []
    // 错误消息已由拦截器处理
  }
}

/**
 * 获取科室列表
 */
const fetchDepartments = async () => {
  try {
    const res = await request.get('/departments', {
      params: { size: 1000 }
    })
    departments.value = res.items || []
  } catch (error: any) {
    console.error('获取科室列表失败:', error)
    departments.value = []
    // 错误消息已由拦截器处理
  }
}

/**
 * 获取成本维度列表（医护技序列下成本一级维度的末级维度）
 */
const fetchDimensions = async (versionId?: number) => {
  try {
    // 如果没有指定版本ID，获取激活的模型版本
    let targetVersionId = versionId
    if (!targetVersionId) {
      const versionsRes = await request.get('/model-versions', {
        params: { limit: 1 }
      })
      
      if (!versionsRes.items || versionsRes.items.length === 0) {
        console.warn('没有可用的模型版本')
        dimensions.value = []
        return
      }
      
      targetVersionId = versionsRes.items[0].id
    }
    
    // 获取该版本中医护技序列下成本维度的末级维度
    const res = await request.get(`/model-nodes/version/${targetVersionId}/cost-dimensions`)
    
    dimensions.value = res.items || []
    
    console.log(`获取到 ${dimensions.value.length} 个成本维度`)
  } catch (error: any) {
    console.error('获取维度列表失败:', error)
    dimensions.value = []
    // 错误消息已由拦截器处理
  }
}

// ==================== 事件处理 ====================

/**
 * 搜索
 */
const handleSearch = () => {
  pagination.page = 1
  fetchCostBenchmarks()
}

/**
 * 防抖搜索 - 用于关键词输入
 */
const debouncedSearch = debounce(() => {
  handleSearch()
}, 500)

/**
 * 处理关键词输入
 */
const handleKeywordInput = () => {
  debouncedSearch()
}

/**
 * 重置
 */
const handleReset = () => {
  searchForm.version_id = undefined
  searchForm.department_code = ''
  searchForm.dimension_code = ''
  searchForm.keyword = ''
  handleSearch()
}

/**
 * 处理每页数量变化
 */
const handleSizeChange = () => {
  pagination.page = 1
  fetchCostBenchmarks()
}

/**
 * 新增
 */
const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '添加成本基准'
  dialogVisible.value = true
}

/**
 * 编辑
 */
const handleEdit = (row: CostBenchmark) => {
  isEdit.value = true
  dialogTitle.value = '编辑成本基准'
  Object.assign(form, row)
  dialogVisible.value = true
}

/**
 * 删除
 */
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
  } catch (error: any) {
    // 用户取消操作
    if (error === 'cancel') {
      return
    }
    
    console.error('删除成本基准失败:', error)
    // 错误消息已由拦截器处理
  }
}

/**
 * 导出Excel
 */
const handleExport = async () => {
  // 检查是否有数据
  if (pagination.total === 0) {
    ElMessage.warning('没有可导出的数据')
    return
  }
  
  exporting.value = true
  try {
    const params: any = {}
    if (searchForm.version_id) {
      params.version_id = searchForm.version_id
    }
    if (searchForm.department_code) {
      params.department_code = searchForm.department_code
    }
    if (searchForm.dimension_code) {
      params.dimension_code = searchForm.dimension_code
    }
    if (searchForm.keyword) {
      params.keyword = searchForm.keyword
    }

    const response = await exportCostBenchmarks(params)
    
    // 验证返回的是Blob对象
    const blob = response.data || response
    if (!(blob instanceof Blob)) {
      throw new Error('导出数据格式错误')
    }
    
    // 从响应头获取文件名
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
    let filename = `成本基准_${timestamp}.xlsx`
    const contentDisposition = response.headers?.['content-disposition']
    if (contentDisposition && contentDisposition.includes("filename*=UTF-8''")) {
      const filenameMatch = contentDisposition.split("filename*=UTF-8''")[1]
      if (filenameMatch) {
        filename = decodeURIComponent(filenameMatch)
      }
    }
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error: any) {
    console.error('导出成本基准失败:', error)
    // 错误消息已由拦截器处理
  } finally {
    exporting.value = false
  }
}

/**
 * 提交表单
 */
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
    if (!form.department_code || !form.version_id || !form.dimension_code || !form.benchmark_value) {
      ElMessage.warning('请填写完整的表单信息')
      return
    }

    // 验证基准值必须大于0
    if (form.benchmark_value <= 0) {
      ElMessage.warning('基准值必须大于0')
      return
    }

    submitting.value = true
    
    const submitData = {
      department_code: form.department_code,
      department_name: form.department_name,
      version_id: form.version_id,
      version_name: form.version_name,
      dimension_code: form.dimension_code,
      dimension_name: form.dimension_name,
      benchmark_value: form.benchmark_value
    }

    if (isEdit.value) {
      await updateCostBenchmark(form.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await createCostBenchmark(submitData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchCostBenchmarks()
  } catch (error: any) {
    console.error('提交表单失败:', error)
    // 错误消息已由拦截器处理
  } finally {
    submitting.value = false
  }
}

/**
 * 关闭对话框
 */
const handleDialogClose = () => {
  formRef.value?.resetFields()
  Object.assign(form, {
    id: 0,
    department_code: '',
    department_name: '',
    version_id: undefined,
    version_name: '',
    dimension_code: '',
    dimension_name: '',
    benchmark_value: undefined
  })
}

/**
 * 科室选择变化
 */
const handleDepartmentChange = (code: string) => {
  const dept = departments.value.find(d => d.his_code === code)
  if (dept) {
    form.department_name = dept.his_name
  }
}

/**
 * 版本选择变化
 */
const handleVersionChange = (id: number) => {
  const version = versions.value.find(v => v.id === id)
  if (version) {
    form.version_name = version.name
  }
  
  // 重新加载该版本的成本维度
  fetchDimensions(id)
  
  // 清空已选择的维度
  form.dimension_code = ''
  form.dimension_name = ''
}

/**
 * 维度选择变化
 */
const handleDimensionChange = (code: string) => {
  const dim = dimensions.value.find(d => d.code === code)
  if (dim) {
    form.dimension_name = dim.name
  }
}

/**
 * 格式化数字
 */
const formatNumber = (value: number) => {
  return value.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

/**
 * 获取空数据提示文本
 */
const getEmptyDescription = () => {
  // 检查是否有筛选条件
  const hasFilters = searchForm.version_id || 
                     searchForm.department_code || 
                     searchForm.dimension_code || 
                     searchForm.keyword
  
  if (hasFilters) {
    return '未找到符合条件的数据，请尝试调整筛选条件'
  }
  
  return '暂无成本基准数据，点击"添加成本基准"按钮创建'
}

// ==================== 生命周期 ====================

onMounted(async () => {
  try {
    // 并行加载所有初始数据
    await Promise.all([
      fetchCostBenchmarks(),
      fetchVersions(),
      fetchDepartments(),
      fetchDimensions()
    ])
  } catch (error: any) {
    console.error('页面初始化失败:', error)
    ElMessage.error('页面初始化失败，请刷新页面重试')
  }
})
</script>

<style scoped>
.cost-benchmarks-container {
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
</style>
