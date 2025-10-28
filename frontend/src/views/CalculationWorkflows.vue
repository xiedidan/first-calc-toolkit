<template>
  <div class="calculation-workflows-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>计算流程管理</span>
          <el-button type="primary" @click="handleCreate">新建流程</el-button>
        </div>
      </template>

      <!-- 筛选区域 -->
      <el-form :inline="true" :model="queryParams" class="query-form">
        <el-form-item label="模型版本">
          <el-select
            v-model="queryParams.version_id"
            placeholder="请选择版本"
            clearable
            style="width: 200px"
            @change="handleQuery"
          >
            <el-option
              v-for="version in versionList"
              :key="version.id"
              :label="version.name"
              :value="version.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="queryParams.keyword"
            placeholder="请输入流程名称"
            clearable
            style="width: 200px"
            @keyup.enter="handleQuery"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 列表 -->
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="流程名称" min-width="150" />
        <el-table-column prop="version_name" label="所属版本" width="150" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="step_count" label="步骤数" width="100" align="center" />
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleViewSteps(row)">查看步骤</el-button>
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handleCopy(row)">复制</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="queryParams.page"
        v-model:page-size="queryParams.size"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleQuery"
        @current-change="handleQuery"
        class="pagination"
      />
    </el-card>

    <!-- 新建/编辑流程对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="模型版本" prop="version_id">
          <el-select
            v-model="formData.version_id"
            placeholder="请选择版本"
            style="width: 100%"
            :disabled="isEdit"
          >
            <el-option
              v-for="version in versionList"
              :key="version.id"
              :label="version.name"
              :value="version.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="流程名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入流程名称" />
        </el-form-item>
        <el-form-item label="流程描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入流程描述"
          />
        </el-form-item>
        <el-form-item label="是否启用" prop="is_active">
          <el-switch v-model="formData.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 复制流程对话框 -->
    <el-dialog
      v-model="copyDialogVisible"
      title="复制流程"
      width="600px"
      @close="handleCopyDialogClose"
    >
      <el-form
        ref="copyFormRef"
        :model="copyFormData"
        :rules="copyFormRules"
        label-width="100px"
      >
        <el-form-item label="新流程名称" prop="name">
          <el-input v-model="copyFormData.name" placeholder="请输入新流程名称" />
        </el-form-item>
        <el-form-item label="流程描述" prop="description">
          <el-input
            v-model="copyFormData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入流程描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="copyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCopySubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 步骤管理对话框 -->
    <el-dialog
      v-model="stepsDialogVisible"
      :title="`${currentWorkflow?.name} - 步骤管理`"
      width="90%"
      top="5vh"
      @close="handleStepsDialogClose"
    >
      <div class="steps-container">
        <div class="steps-header">
          <el-button type="primary" @click="handleCreateStep">新建步骤</el-button>
        </div>

        <el-table :data="stepsList" border stripe v-loading="stepsLoading">
          <el-table-column prop="sort_order" label="顺序" width="80" align="center" />
          <el-table-column prop="name" label="步骤名称" width="150" />
          <el-table-column prop="description" label="描述" width="200" show-overflow-tooltip />
          <el-table-column prop="code_type" label="代码类型" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.code_type === 'python' ? 'success' : 'primary'">
                {{ row.code_type.toUpperCase() }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="code_content" label="代码内容" min-width="300">
            <template #default="{ row }">
              <pre class="code-preview">{{ row.code_content }}</pre>
            </template>
          </el-table-column>
          <el-table-column prop="is_enabled" label="状态" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_enabled ? 'success' : 'info'">
                {{ row.is_enabled ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="280" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="handleMoveUp(row)">上移</el-button>
              <el-button link type="primary" @click="handleMoveDown(row)">下移</el-button>
              <el-button link type="primary" @click="handleEditStep(row)">编辑</el-button>
              <el-button link type="warning" @click="handleTestStep(row)">测试</el-button>
              <el-button link type="danger" @click="handleDeleteStep(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 新建/编辑步骤对话框 -->
    <el-dialog
      v-model="stepDialogVisible"
      :title="stepDialogTitle"
      width="800px"
      @close="handleStepDialogClose"
    >
      <el-form
        ref="stepFormRef"
        :model="stepFormData"
        :rules="stepFormRules"
        label-width="100px"
      >
        <el-form-item label="步骤名称" prop="name">
          <el-input v-model="stepFormData.name" placeholder="请输入步骤名称" />
        </el-form-item>
        <el-form-item label="步骤描述" prop="description">
          <el-input
            v-model="stepFormData.description"
            type="textarea"
            :rows="2"
            placeholder="请输入步骤描述"
          />
        </el-form-item>
        <el-form-item label="代码类型" prop="code_type">
          <el-radio-group v-model="stepFormData.code_type">
            <el-radio value="python">Python</el-radio>
            <el-radio value="sql">SQL</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="代码内容" prop="code_content">
          <el-input
            v-model="stepFormData.code_content"
            type="textarea"
            :rows="12"
            placeholder="请输入代码内容"
            style="font-family: 'Courier New', monospace;"
          />
        </el-form-item>
        <el-form-item label="是否启用" prop="is_enabled">
          <el-switch v-model="stepFormData.is_enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stepDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleStepSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { calculationWorkflowApi, calculationStepApi } from '@/api/calculation-workflow'
import type {
  CalculationWorkflow,
  CalculationStep,
  WorkflowCreateData,
  WorkflowUpdateData,
  StepCreateData,
  StepUpdateData
} from '@/api/calculation-workflow'
import { getModelVersions } from '@/api/model'

// 版本列表
const versionList = ref<any[]>([])

// 查询参数
const queryParams = reactive({
  version_id: undefined as number | undefined,
  page: 1,
  size: 10,
  keyword: ''
})

// 表格数据
const tableData = ref<CalculationWorkflow[]>([])
const total = ref(0)
const loading = ref(false)

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const formData = reactive<Partial<WorkflowCreateData & { id?: number }>>({
  version_id: undefined,
  name: '',
  description: '',
  is_active: true
})
const formRules: FormRules = {
  version_id: [{ required: true, message: '请选择模型版本', trigger: 'change' }],
  name: [{ required: true, message: '请输入流程名称', trigger: 'blur' }]
}
const submitting = ref(false)

// 复制对话框
const copyDialogVisible = ref(false)
const copyFormRef = ref<FormInstance>()
const copyFormData = reactive({
  id: 0,
  name: '',
  description: ''
})
const copyFormRules: FormRules = {
  name: [{ required: true, message: '请输入新流程名称', trigger: 'blur' }]
}

// 步骤管理
const stepsDialogVisible = ref(false)
const currentWorkflow = ref<CalculationWorkflow | null>(null)
const stepsList = ref<CalculationStep[]>([])
const stepsLoading = ref(false)

// 步骤对话框
const stepDialogVisible = ref(false)
const stepDialogTitle = ref('')
const isEditStep = ref(false)
const stepFormRef = ref<FormInstance>()
const stepFormData = reactive<Partial<StepCreateData & { id?: number }>>({
  workflow_id: undefined,
  name: '',
  description: '',
  code_type: 'python',
  code_content: '',
  is_enabled: true
})
const stepFormRules: FormRules = {
  name: [{ required: true, message: '请输入步骤名称', trigger: 'blur' }],
  code_type: [{ required: true, message: '请选择代码类型', trigger: 'change' }],
  code_content: [{ required: true, message: '请输入代码内容', trigger: 'blur' }]
}

// 加载版本列表
const loadVersions = async () => {
  try {
    const res = await getModelVersions({ skip: 0, limit: 1000 })
    versionList.value = res.items
  } catch (error) {
    console.error('加载版本列表失败:', error)
  }
}

// 加载列表
const loadList = async () => {
  loading.value = true
  try {
    const res = await calculationWorkflowApi.getList(queryParams)
    tableData.value = res.items
    total.value = res.total
  } catch (error) {
    ElMessage.error('加载列表失败')
  } finally {
    loading.value = false
  }
}

// 查询
const handleQuery = () => {
  queryParams.page = 1
  loadList()
}

// 重置
const handleReset = () => {
  queryParams.version_id = undefined
  queryParams.keyword = ''
  handleQuery()
}

// 新建
const handleCreate = () => {
  isEdit.value = false
  dialogTitle.value = '新建流程'
  Object.assign(formData, {
    version_id: queryParams.version_id,
    name: '',
    description: '',
    is_active: true
  })
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: CalculationWorkflow) => {
  isEdit.value = true
  dialogTitle.value = '编辑流程'
  Object.assign(formData, {
    id: row.id,
    version_id: row.version_id,
    name: row.name,
    description: row.description,
    is_active: row.is_active
  })
  dialogVisible.value = true
}

// 提交
const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (isEdit.value && formData.id) {
        const updateData: WorkflowUpdateData = {
          name: formData.name,
          description: formData.description,
          is_active: formData.is_active
        }
        await calculationWorkflowApi.update(formData.id, updateData)
        ElMessage.success('更新成功')
      } else {
        const createData: WorkflowCreateData = {
          version_id: formData.version_id!,
          name: formData.name!,
          description: formData.description,
          is_active: formData.is_active
        }
        await calculationWorkflowApi.create(createData)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      loadList()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

// 复制
const handleCopy = (row: CalculationWorkflow) => {
  Object.assign(copyFormData, {
    id: row.id,
    name: `${row.name}_副本`,
    description: row.description
  })
  copyDialogVisible.value = true
}

// 提交复制
const handleCopySubmit = async () => {
  if (!copyFormRef.value) return
  await copyFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      await calculationWorkflowApi.copy(copyFormData.id, {
        name: copyFormData.name,
        description: copyFormData.description
      })
      ElMessage.success('复制成功')
      copyDialogVisible.value = false
      loadList()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '复制失败')
    } finally {
      submitting.value = false
    }
  })
}

// 删除
const handleDelete = (row: CalculationWorkflow) => {
  ElMessageBox.confirm(`确定要删除流程"${row.name}"吗？此操作将同时删除所有步骤！`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await calculationWorkflowApi.delete(row.id)
      ElMessage.success('删除成功')
      loadList()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  })
}

// 查看步骤
const handleViewSteps = async (row: CalculationWorkflow) => {
  currentWorkflow.value = row
  stepsDialogVisible.value = true
  await loadSteps()
}

// 加载步骤列表
const loadSteps = async () => {
  if (!currentWorkflow.value) return
  stepsLoading.value = true
  try {
    const res = await calculationStepApi.getList(currentWorkflow.value.id)
    stepsList.value = res.items
  } catch (error) {
    ElMessage.error('加载步骤列表失败')
  } finally {
    stepsLoading.value = false
  }
}

// 新建步骤
const handleCreateStep = () => {
  if (!currentWorkflow.value) return
  isEditStep.value = false
  stepDialogTitle.value = '新建步骤'
  Object.assign(stepFormData, {
    workflow_id: currentWorkflow.value.id,
    name: '',
    description: '',
    code_type: 'python',
    code_content: '',
    is_enabled: true
  })
  stepDialogVisible.value = true
}

// 编辑步骤
const handleEditStep = (row: CalculationStep) => {
  isEditStep.value = true
  stepDialogTitle.value = '编辑步骤'
  Object.assign(stepFormData, {
    id: row.id,
    workflow_id: row.workflow_id,
    name: row.name,
    description: row.description,
    code_type: row.code_type,
    code_content: row.code_content,
    is_enabled: row.is_enabled
  })
  stepDialogVisible.value = true
}

// 提交步骤
const handleStepSubmit = async () => {
  if (!stepFormRef.value) return
  await stepFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (isEditStep.value && stepFormData.id) {
        const updateData: StepUpdateData = {
          name: stepFormData.name,
          description: stepFormData.description,
          code_type: stepFormData.code_type,
          code_content: stepFormData.code_content,
          is_enabled: stepFormData.is_enabled
        }
        await calculationStepApi.update(stepFormData.id, updateData)
        ElMessage.success('更新成功')
      } else {
        const createData: StepCreateData = {
          workflow_id: stepFormData.workflow_id!,
          name: stepFormData.name!,
          description: stepFormData.description,
          code_type: stepFormData.code_type!,
          code_content: stepFormData.code_content!,
          is_enabled: stepFormData.is_enabled
        }
        await calculationStepApi.create(createData)
        ElMessage.success('创建成功')
      }
      stepDialogVisible.value = false
      loadSteps()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

// 上移步骤
const handleMoveUp = async (row: CalculationStep) => {
  try {
    const res = await calculationStepApi.moveUp(row.id)
    if (res.success) {
      ElMessage.success(res.message)
      loadSteps()
    } else {
      ElMessage.warning(res.message)
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

// 下移步骤
const handleMoveDown = async (row: CalculationStep) => {
  try {
    const res = await calculationStepApi.moveDown(row.id)
    if (res.success) {
      ElMessage.success(res.message)
      loadSteps()
    } else {
      ElMessage.warning(res.message)
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

// 测试步骤
const handleTestStep = async (row: CalculationStep) => {
  try {
    const res = await calculationStepApi.testCode(row.id)
    if (res.success) {
      ElMessageBox.alert(
        `<pre>${JSON.stringify(res.result, null, 2)}</pre>`,
        '测试结果',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '确定'
        }
      )
    } else {
      ElMessageBox.alert(res.error || '测试失败', '测试结果', {
        type: 'error',
        confirmButtonText: '确定'
      })
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '测试失败')
  }
}

// 删除步骤
const handleDeleteStep = (row: CalculationStep) => {
  ElMessageBox.confirm(`确定要删除步骤"${row.name}"吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await calculationStepApi.delete(row.id)
      ElMessage.success('删除成功')
      loadSteps()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  })
}

// 对话框关闭
const handleDialogClose = () => {
  formRef.value?.resetFields()
}

const handleCopyDialogClose = () => {
  copyFormRef.value?.resetFields()
}

const handleStepsDialogClose = () => {
  currentWorkflow.value = null
  stepsList.value = []
}

const handleStepDialogClose = () => {
  stepFormRef.value?.resetFields()
}

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  if (!dateStr) return ''
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

// 初始化
onMounted(() => {
  loadVersions()
  loadList()
})
</script>

<style scoped>
.calculation-workflows-container {
  padding: 0;
  width: 100%;
  height: 100%;
}

.calculation-workflows-container :deep(.el-card) {
  width: 100%;
  height: 100%;
}

.calculation-workflows-container :deep(.el-card__body) {
  height: calc(100% - 60px);
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.query-form {
  margin-bottom: 20px;
}

.calculation-workflows-container :deep(.el-table) {
  flex: 1;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.steps-container .steps-header {
  margin-bottom: 16px;
}

.steps-container .code-preview {
  max-height: 100px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.4;
  margin: 0;
  padding: 8px;
  background-color: #f5f5f5;
  border-radius: 4px;
}
</style>