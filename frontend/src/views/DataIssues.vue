<template>
  <div class="data-issues-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据问题记录</span>
          <div class="header-actions">
            <el-button type="success" @click="handleExport" :loading="exporting">
              <el-icon><Download /></el-icon>
              导出问题
            </el-button>
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              新建问题
            </el-button>
          </div>
        </div>
      </template>

      <!-- Search bar -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="标题/描述"
            clearable
            @clear="handleSearch"
          />
        </el-form-item>
        <el-form-item label="处理阶段">
          <el-select
            v-model="searchForm.processing_stage"
            placeholder="全部"
            clearable
            @clear="handleSearch"
            style="width: 150px"
          >
            <el-option label="待开始" value="not_started" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已解决" value="resolved" />
            <el-option label="已确认" value="confirmed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>

      <!-- Table -->
      <el-table
        :data="tableData"
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="150" />
        <el-table-column prop="description" label="问题描述" min-width="200">
          <template #default="{ row }">
            <el-tooltip
              :content="row.description"
              placement="top"
              :disabled="row.description.length <= 50"
            >
              <span>{{ row.description.length > 50 ? row.description.substring(0, 50) + '...' : row.description }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="reporter" label="记录人" width="120" />
        <el-table-column prop="assignee" label="负责人" width="120">
          <template #default="{ row }">
            <span :style="{ color: row.assignee ? '' : '#909399' }">
              {{ row.assignee || '待定' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="processing_stage" label="处理阶段" width="120">
          <template #default="{ row }">
            <el-tag :type="getStageTagType(row.processing_stage)" size="small">
              {{ getStageLabel(row.processing_stage) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="记录时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              link
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              link
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchData"
        @current-change="fetchData"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- Add/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      append-to-body
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="formData.title" placeholder="请输入问题标题" />
        </el-form-item>
        <el-form-item label="问题描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入问题描述"
          />
        </el-form-item>
        <el-form-item label="记录人" prop="reporter">
          <UserSelector
            v-model="formData.reporter"
            v-model:user-id="formData.reporter_user_id"
            placeholder="请输入或选择记录人"
          />
        </el-form-item>
        <el-form-item label="负责人" prop="assignee">
          <UserSelector
            v-model="formData.assignee"
            v-model:user-id="formData.assignee_user_id"
            placeholder="请输入或选择负责人（可选）"
          />
        </el-form-item>
        <el-form-item label="处理阶段" prop="processing_stage">
          <el-select v-model="formData.processing_stage" style="width: 100%">
            <el-option label="待开始" value="not_started" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已解决" value="resolved" />
            <el-option label="已确认" value="confirmed" />
          </el-select>
          <el-alert
            type="info"
            :closable="false"
            style="margin-top: 10px"
          >
            <template #default>
              <div style="font-size: 12px; line-height: 1.5">
                问题的处理结果包括但不限于：技术修复、流程优化、数据更正等。<br />
                若经评估后决定不予处理或撤回问题，也应将处理阶段更新为"已解决"，<br />
                并在解决方案中详细说明不处理的原因和依据。
              </div>
            </template>
          </el-alert>
        </el-form-item>
        <el-form-item label="解决方案" prop="resolution">
          <el-input
            v-model="formData.resolution"
            type="textarea"
            :rows="4"
            placeholder="请输入解决方案（处理阶段为已解决时必填）"
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Search, Refresh, Download } from '@element-plus/icons-vue'
import {
  getDataIssueList,
  createDataIssue,
  updateDataIssue,
  deleteDataIssue,
  type DataIssue,
  type ProcessingStage
} from '@/api/dataIssue'
import UserSelector from '@/components/UserSelector.vue'
import request from '@/utils/request'

// Search form
const searchForm = reactive({
  keyword: '',
  processing_stage: ''
})

// Table data
const tableData = ref<DataIssue[]>([])
const loading = ref(false)
const exporting = ref(false)

// Pagination
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// Fetch data
const fetchData = async () => {
  loading.value = true
  try {
    const response = await getDataIssueList({
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword || undefined,
      processing_stage: searchForm.processing_stage as ProcessingStage || undefined
    })
    tableData.value = response.items
    pagination.total = response.total
  } catch (error) {
    console.error('Failed to fetch data issues:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// Search
const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

// Reset
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.processing_stage = ''
  pagination.page = 1
  fetchData()
}

// Dialog
const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

// Form data
const formData = reactive({
  id: 0,
  title: '',
  description: '',
  reporter: '',
  reporter_user_id: undefined as number | undefined,
  assignee: '',
  assignee_user_id: undefined as number | undefined,
  processing_stage: 'not_started' as ProcessingStage,
  resolution: ''
})

// Form rules
const formRules: FormRules = {
  title: [
    { required: true, message: '请输入问题标题', trigger: 'blur' },
    { min: 1, max: 200, message: '长度在 1 到 200 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入问题描述', trigger: 'blur' }
  ],
  reporter: [
    { required: true, message: '请输入记录人', trigger: 'blur' }
  ],
  resolution: [
    {
      validator: (rule, value, callback) => {
        if (formData.processing_stage === 'resolved' && !value) {
          callback(new Error('处理阶段为"已解决"时，必须填写解决方案'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// Add
const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增问题'
  resetForm()
  dialogVisible.value = true
}

// Edit
const handleEdit = (row: DataIssue) => {
  isEdit.value = true
  dialogTitle.value = '编辑问题'
  formData.id = row.id
  formData.title = row.title
  formData.description = row.description
  formData.reporter = row.reporter
  formData.reporter_user_id = row.reporter_user_id
  formData.assignee = row.assignee || ''
  formData.assignee_user_id = row.assignee_user_id
  formData.processing_stage = row.processing_stage
  formData.resolution = row.resolution || ''
  dialogVisible.value = true
}

// Submit
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value) {
          // Update
          await updateDataIssue(formData.id, {
            title: formData.title,
            description: formData.description,
            reporter: formData.reporter,
            reporter_user_id: formData.reporter_user_id,
            assignee: formData.assignee || undefined,
            assignee_user_id: formData.assignee_user_id,
            processing_stage: formData.processing_stage,
            resolution: formData.resolution || undefined
          })
          ElMessage.success('更新成功')
        } else {
          // Create
          await createDataIssue({
            title: formData.title,
            description: formData.description,
            reporter: formData.reporter,
            reporter_user_id: formData.reporter_user_id,
            assignee: formData.assignee || undefined,
            assignee_user_id: formData.assignee_user_id,
            processing_stage: formData.processing_stage,
            resolution: formData.resolution || undefined
          })
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        console.error('Failed to submit:', error)
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

// Dialog close
const handleDialogClose = () => {
  formRef.value?.resetFields()
  resetForm()
}

// Reset form
const resetForm = () => {
  formData.id = 0
  formData.title = ''
  formData.description = ''
  formData.reporter = ''
  formData.reporter_user_id = undefined
  formData.assignee = ''
  formData.assignee_user_id = undefined
  formData.processing_stage = 'not_started'
  formData.resolution = ''
}

// Delete
const handleDelete = (row: DataIssue) => {
  ElMessageBox.confirm(
    `确定要删除问题 "${row.title}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteDataIssue(row.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      console.error('Failed to delete data issue:', error)
      ElMessage.error('删除失败')
    }
  })
}

// Get stage tag type
const getStageTagType = (stage: ProcessingStage): string => {
  const typeMap: Record<ProcessingStage, string> = {
    not_started: 'info',
    in_progress: 'primary',
    resolved: 'success',
    confirmed: 'success'
  }
  return typeMap[stage] || 'info'
}

// Get stage label
const getStageLabel = (stage: ProcessingStage): string => {
  const labelMap: Record<ProcessingStage, string> = {
    not_started: '待开始',
    in_progress: '进行中',
    resolved: '已解决',
    confirmed: '已确认'
  }
  return labelMap[stage] || stage
}

// Format datetime
const formatDateTime = (dateStr: string): string => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// Export to Excel
const handleExport = async () => {
  exporting.value = true
  try {
    const response = await request({
      url: '/data-issues/export',
      method: 'get',
      params: {
        keyword: searchForm.keyword || undefined,
        processing_stage: searchForm.processing_stage || undefined
      },
      responseType: 'blob'
    })
    
    // 从响应头获取文件名
    let filename = `数据问题记录_${new Date().toISOString().slice(0, 10)}.xlsx`
    const contentDisposition = response.headers?.['content-disposition']
    if (contentDisposition && contentDisposition.includes("filename*=UTF-8''")) {
      const filenameMatch = contentDisposition.split("filename*=UTF-8''")[1]
      if (filenameMatch) {
        filename = decodeURIComponent(filenameMatch)
      }
    }
    
    // 创建下载链接
    const blob = response.data || response
    const url = window.URL.createObjectURL(new Blob([blob]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error: any) {
    console.error('Failed to export data:', error)
    ElMessage.error(error.response?.data?.detail || '导出失败')
  } finally {
    exporting.value = false
  }
}

// Initialize
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.data-issues-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.search-form {
  margin-bottom: 20px;
}
</style>
