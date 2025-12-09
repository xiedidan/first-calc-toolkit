<template>
  <div class="model-versions-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>评估模型管理</span>
          <div class="header-buttons">
            <el-button type="success" @click="handleImport">
              <el-icon><Download /></el-icon>
              导入版本
            </el-button>
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              新建版本
            </el-button>
          </div>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索版本号、名称或描述"
          clearable
          style="width: 300px"
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </div>

      <!-- 表格 -->
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="version" label="版本号" width="120" />
        <el-table-column prop="name" label="版本名称" min-width="200" />
        <el-table-column prop="description" label="版本描述" min-width="250" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_active" type="success">激活</el-tag>
            <el-tag v-else type="info">未激活</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="500" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEditStructure(row)">
              <el-icon><Edit /></el-icon>
              编辑结构
            </el-button>
            <el-button link type="info" @click="handleViewRules(row)">
              <el-icon><Document /></el-icon>
              查看规则
            </el-button>
            <el-button 
              link 
              type="success" 
              @click="handleActivate(row)"
              :disabled="row.is_active"
            >
              <el-icon><Check /></el-icon>
              激活
            </el-button>
            <el-button link type="warning" @click="handleCopy(row)">
              <el-icon><CopyDocument /></el-icon>
              复制
            </el-button>
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button 
              link 
              type="danger" 
              @click="handleDelete(row)"
              :disabled="row.is_active"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      append-to-body
      @close="handleDialogClose"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="版本号" prop="version">
          <el-input 
            v-model="form.version" 
            placeholder="如: v1.0"
            :disabled="isEdit"
          />
        </el-form-item>
        <el-form-item label="版本名称" prop="name">
          <el-input v-model="form.name" placeholder="如: 2025年标准版" />
        </el-form-item>
        <el-form-item label="版本描述" prop="description">
          <el-input 
            v-model="form.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入版本描述"
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

    <!-- 复制版本对话框 -->
    <el-dialog
      v-model="copyDialogVisible"
      title="复制版本"
      width="600px"
      append-to-body
      @close="handleCopyDialogClose"
    >
      <el-alert
        title="提示"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        将复制版本 <strong>{{ copySource?.name }}</strong> 的完整结构
      </el-alert>
      <el-form :model="copyForm" :rules="copyRules" ref="copyFormRef" label-width="100px">
        <el-form-item label="版本号" prop="version">
          <el-input v-model="copyForm.version" placeholder="如: v1.1" />
        </el-form-item>
        <el-form-item label="版本名称" prop="name">
          <el-input v-model="copyForm.name" placeholder="如: 2025年标准版-修订" />
        </el-form-item>
        <el-form-item label="版本描述" prop="description">
          <el-input 
            v-model="copyForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入版本描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="copyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCopySubmit" :loading="submitting">
          确定复制
        </el-button>
      </template>
    </el-dialog>

    <!-- 导入版本对话框 -->
    <ModelVersionImportDialog
      v-model:visible="importDialogVisible"
      @success="handleImportSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Edit, Check, CopyDocument, Document, Search, Download } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import {
  getModelVersions,
  createModelVersion,
  updateModelVersion,
  deleteModelVersion,
  activateModelVersion,
  type ModelVersion
} from '@/api/model'
import ModelVersionImportDialog from '@/components/ModelVersionImportDialog.vue'

const router = useRouter()

// 表格数据
const tableData = ref<ModelVersion[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchText = ref('')

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('新建版本')
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

// 表单
const form = reactive({
  id: 0,
  version: '',
  name: '',
  description: ''
})

const rules: FormRules = {
  version: [{ required: true, message: '请输入版本号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入版本名称', trigger: 'blur' }]
}

// 复制对话框
const copyDialogVisible = ref(false)
const copySource = ref<ModelVersion>()
const copyFormRef = ref<FormInstance>()
const copyForm = reactive({
  version: '',
  name: '',
  description: ''
})

const copyRules: FormRules = {
  version: [{ required: true, message: '请输入版本号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入版本名称', trigger: 'blur' }]
}

// 导入对话框
const importDialogVisible = ref(false)

// 获取列表
const fetchData = async () => {
  loading.value = true
  try {
    const res = await getModelVersions({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      search: searchText.value || undefined
    })
    tableData.value = res.items
    total.value = res.total
  } catch (error) {
    ElMessage.error('获取版本列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

// 分页变化
const handlePageChange = () => {
  fetchData()
}

const handleSizeChange = () => {
  currentPage.value = 1
  fetchData()
}

// 新增
const handleAdd = () => {
  dialogTitle.value = '新建版本'
  isEdit.value = false
  Object.assign(form, {
    id: 0,
    version: '',
    name: '',
    description: ''
  })
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: ModelVersion) => {
  dialogTitle.value = '编辑版本'
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    version: row.version,
    name: row.name,
    description: row.description || ''
  })
  dialogVisible.value = true
}

// 编辑结构
const handleEditStructure = (row: ModelVersion) => {
  router.push({
    name: 'ModelNodes',
    params: { versionId: row.id }
  })
}

// 查看规则
const handleViewRules = (row: ModelVersion) => {
  router.push({
    name: 'ModelRules',
    params: { versionId: row.id }
  })
}

// 激活
const handleActivate = async (row: ModelVersion) => {
  try {
    await ElMessageBox.confirm(
      `确定要激活版本 "${row.name}" 吗？激活后其他版本将自动取消激活。`,
      '确认激活',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await activateModelVersion(row.id)
    ElMessage.success('激活成功')
    fetchData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '激活失败')
    }
  }
}

// 复制
const handleCopy = (row: ModelVersion) => {
  copySource.value = row
  Object.assign(copyForm, {
    version: '',
    name: `${row.name}-副本`,
    description: row.description || ''
  })
  copyDialogVisible.value = true
}

// 导入
const handleImport = () => {
  importDialogVisible.value = true
}

// 导入成功
const handleImportSuccess = (versionId: number) => {
  fetchData()
  // 可选：跳转到新版本的编辑页面
  // router.push({ name: 'ModelNodes', params: { versionId } })
}

// 删除
const handleDelete = async (row: ModelVersion) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除版本 "${row.name}" 吗？删除后将无法恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteModelVersion(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (isEdit.value) {
        await updateModelVersion(form.id, {
          name: form.name,
          description: form.description
        })
        ElMessage.success('更新成功')
      } else {
        await createModelVersion({
          version: form.version,
          name: form.name,
          description: form.description
        })
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchData()
    } catch (error: any) {
      ElMessage.error(error.message || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

// 提交复制
const handleCopySubmit = async () => {
  if (!copyFormRef.value || !copySource.value) return
  
  await copyFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      await createModelVersion({
        version: copyForm.version,
        name: copyForm.name,
        description: copyForm.description,
        base_version_id: copySource.value!.id
      })
      ElMessage.success('复制成功')
      copyDialogVisible.value = false
      fetchData()
    } catch (error: any) {
      ElMessage.error(error.message || '复制失败')
    } finally {
      submitting.value = false
    }
  })
}

// 关闭对话框
const handleDialogClose = () => {
  formRef.value?.resetFields()
}

const handleCopyDialogClose = () => {
  copyFormRef.value?.resetFields()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.model-versions-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-buttons {
  display: flex;
  gap: 10px;
}

.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
