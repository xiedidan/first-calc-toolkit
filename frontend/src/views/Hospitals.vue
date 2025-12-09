<template>
  <div class="hospitals-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>医疗机构管理</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建医疗机构
          </el-button>
        </div>
      </template>

      <!-- Search and filters -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="关键词">
          <el-input
            v-model="searchKeyword"
            placeholder="医疗机构编码或名称"
            clearable
            style="width: 240px"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="filterActive"
            placeholder="全部"
            clearable
            style="width: 140px"
            @change="handleSearch"
          >
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- Table -->
      <el-table
        :data="hospitals"
        v-loading="loading"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="code" label="医疗机构编码" width="200" />
        <el-table-column prop="name" label="医疗机构名称" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
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
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 16px; justify-content: flex-end"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </el-card>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      append-to-body
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="医疗机构编码" prop="code">
          <el-input
            v-model="formData.code"
            placeholder="请输入医疗机构编码（拼音或英文）"
            :disabled="isEdit"
          />
          <div class="form-tip" v-if="!isEdit">
            编码创建后不可修改，建议使用拼音或英文缩写
          </div>
        </el-form-item>
        <el-form-item label="医疗机构名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入医疗机构名称"
          />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch
            v-model="formData.is_active"
            active-text="启用"
            inactive-text="禁用"
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
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import {
  getHospitals,
  createHospital,
  updateHospital,
  deleteHospital,
  type Hospital,
  type HospitalCreate,
  type HospitalUpdate
} from '@/api/hospital'
import { useHospitalStore } from '@/stores/hospital'

// Store
const hospitalStore = useHospitalStore()

// Data
const loading = ref(false)
const hospitals = ref<Hospital[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchKeyword = ref('')
const filterActive = ref<boolean | undefined>(undefined)

// Dialog
const dialogVisible = ref(false)
const dialogTitle = computed(() => isEdit.value ? '编辑医疗机构' : '新建医疗机构')
const isEdit = ref(false)
const editingId = ref<number | null>(null)
const submitting = ref(false)

// Form
const formRef = ref<FormInstance>()
const formData = reactive<HospitalCreate & { is_active: boolean }>({
  code: '',
  name: '',
  is_active: true
})

const formRules: FormRules = {
  code: [
    { required: true, message: '请输入医疗机构编码', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_-]+$/, message: '编码只能包含字母、数字、下划线和连字符', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入医疗机构名称', trigger: 'blur' },
    { min: 2, max: 100, message: '名称长度在 2 到 100 个字符', trigger: 'blur' }
  ]
}

// Methods
const fetchHospitals = async () => {
  loading.value = true
  try {
    const response = await getHospitals({
      page: currentPage.value,
      size: pageSize.value,
      search: searchKeyword.value || undefined,
      is_active: filterActive.value
    })
    hospitals.value = response.items
    total.value = response.total
  } catch (error) {
    ElMessage.error('获取医疗机构列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchHospitals()
}

const handleReset = () => {
  searchKeyword.value = ''
  filterActive.value = undefined
  currentPage.value = 1
  fetchHospitals()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchHospitals()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchHospitals()
}

// Refresh hospital list in store (for top navigation)
const refreshHospitalStore = async () => {
  try {
    await hospitalStore.fetchAccessibleHospitals()
  } catch (error) {
    console.error('Failed to refresh hospital store:', error)
  }
}

const handleCreate = () => {
  isEdit.value = false
  editingId.value = null
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row: Hospital) => {
  isEdit.value = true
  editingId.value = row.id
  formData.code = row.code
  formData.name = row.name
  formData.is_active = row.is_active
  dialogVisible.value = true
}

const handleDelete = (row: Hospital) => {
  ElMessageBox.confirm(
    `确定要删除医疗机构"${row.name}"吗？如果该机构有关联数据，将无法删除。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteHospital(row.id)
      ElMessage.success('删除成功')
      fetchHospitals()
      // Refresh hospital list in top navigation
      await refreshHospitalStore()
    } catch (error: any) {
      if (error.response?.data?.detail) {
        ElMessage.error(error.response.data.detail)
      } else {
        ElMessage.error('删除失败')
      }
    }
  })
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (isEdit.value && editingId.value) {
        // Update
        const updateData: HospitalUpdate = {
          name: formData.name,
          is_active: formData.is_active
        }
        await updateHospital(editingId.value, updateData)
        ElMessage.success('更新成功')
      } else {
        // Create
        await createHospital(formData)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchHospitals()
      // Refresh hospital list in top navigation
      await refreshHospitalStore()
    } catch (error: any) {
      if (error.response?.data?.detail) {
        ElMessage.error(error.response.data.detail)
      } else {
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      }
    } finally {
      submitting.value = false
    }
  })
}

const handleDialogClose = () => {
  resetForm()
}

const resetForm = () => {
  formData.code = ''
  formData.name = ''
  formData.is_active = true
  formRef.value?.clearValidate()
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Lifecycle
onMounted(() => {
  fetchHospitals()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 16px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
