<template>
  <el-dialog
    v-model="dialogVisible"
    title="导入模型版本"
    width="900px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-steps :active="currentStep" finish-status="success" align-center>
      <el-step title="选择版本" />
      <el-step title="预览详情" />
      <el-step title="配置导入" />
      <el-step title="完成" />
    </el-steps>

    <div class="step-content">
      <!-- 步骤1: 选择版本 -->
      <div v-if="currentStep === 0" class="step-select">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索版本号、名称或医疗机构"
          clearable
          style="margin-bottom: 16px"
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-table
          :data="versionList"
          highlight-current-row
          @current-change="handleVersionSelect"
          style="width: 100%"
          max-height="400px"
        >
          <el-table-column type="index" width="50" />
          <el-table-column prop="version" label="版本号" width="120" />
          <el-table-column prop="name" label="版本名称" min-width="150" />
          <el-table-column prop="hospital_name" label="所属医疗机构" width="150" />
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          style="margin-top: 16px; justify-content: center"
          @current-change="loadVersions"
          @size-change="loadVersions"
        />
      </div>

      <!-- 步骤2: 预览详情 -->
      <div v-if="currentStep === 1" class="step-preview">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="版本号">{{ preview?.version }}</el-descriptions-item>
          <el-descriptions-item label="版本名称">{{ preview?.name }}</el-descriptions-item>
          <el-descriptions-item label="所属医疗机构" :span="2">
            {{ preview?.hospital_name }}
          </el-descriptions-item>
          <el-descriptions-item label="版本描述" :span="2">
            {{ preview?.description || '无' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <div class="statistics">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-statistic title="模型节点数量" :value="preview?.node_count || 0" />
            </el-col>
            <el-col :span="8">
              <el-statistic title="计算流程数量" :value="preview?.workflow_count || 0" />
            </el-col>
            <el-col :span="8">
              <el-statistic title="计算步骤数量" :value="preview?.step_count || 0" />
            </el-col>
          </el-row>
        </div>
      </div>

      <!-- 步骤3: 配置导入 -->
      <div v-if="currentStep === 2" class="step-config">
        <el-form :model="importForm" :rules="importRules" ref="importFormRef" label-width="120px">
          <el-form-item label="导入内容" prop="import_type">
            <el-radio-group v-model="importForm.import_type">
              <el-radio value="structure_only">仅导入模型结构</el-radio>
              <el-radio value="with_workflows">导入模型结构和计算流程</el-radio>
            </el-radio-group>
            <div v-if="importForm.import_type === 'with_workflows'" class="warning-tip">
              <el-alert
                title="注意：计算流程中的SQL代码可能需要根据您的数据库结构进行调整"
                type="warning"
                :closable="false"
                show-icon
              />
            </div>
          </el-form-item>

          <el-divider />

          <el-form-item label="新版本号" prop="version">
            <el-input
              v-model="importForm.version"
              placeholder="请输入版本号"
              @blur="checkVersionUnique"
            />
          </el-form-item>

          <el-form-item label="新版本名称" prop="name">
            <el-input v-model="importForm.name" placeholder="请输入版本名称" />
          </el-form-item>

          <el-form-item label="版本描述">
            <el-input
              v-model="importForm.description"
              type="textarea"
              :rows="3"
              placeholder="请输入版本描述（可选）"
            />
          </el-form-item>
        </el-form>
      </div>

      <!-- 步骤4: 完成 -->
      <div v-if="currentStep === 3" class="step-result">
        <el-result icon="success" title="导入成功">
          <template #sub-title>
            <div class="result-info">
              <p>新版本：{{ importResult?.version }} - {{ importResult?.name }}</p>
              <el-descriptions :column="3" border style="margin-top: 16px">
                <el-descriptions-item label="导入节点数">
                  {{ importResult?.statistics.node_count || 0 }}
                </el-descriptions-item>
                <el-descriptions-item label="导入流程数">
                  {{ importResult?.statistics.workflow_count || 0 }}
                </el-descriptions-item>
                <el-descriptions-item label="导入步骤数">
                  {{ importResult?.statistics.step_count || 0 }}
                </el-descriptions-item>
              </el-descriptions>

              <div v-if="importResult?.warnings && importResult.warnings.length > 0" style="margin-top: 16px">
                <el-alert title="警告信息" type="warning" :closable="false">
                  <ul>
                    <li v-for="(warning, index) in importResult.warnings" :key="index">
                      {{ warning }}
                    </li>
                  </ul>
                </el-alert>
              </div>
            </div>
          </template>
          <template #extra>
            <el-button type="primary" @click="handleViewNewVersion">查看新版本</el-button>
          </template>
        </el-result>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button v-if="currentStep > 0 && currentStep < 3" @click="handlePrevious">上一步</el-button>
        <el-button
          v-if="currentStep < 2"
          type="primary"
          :disabled="!canNext"
          @click="handleNext"
        >
          下一步
        </el-button>
        <el-button
          v-if="currentStep === 2"
          type="primary"
          :loading="importing"
          @click="handleImport"
        >
          确认导入
        </el-button>
        <el-button v-if="currentStep === 3" type="primary" @click="handleClose">完成</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import {
  getImportableVersions,
  previewVersion,
  importVersion,
  getModelVersions,
  type ImportableVersion,
  type VersionPreview,
  type ModelVersionImportRequest,
  type ModelVersionImportResponse
} from '@/api/model'

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'success', versionId: number): void
}>()

const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

// 当前步骤
const currentStep = ref(0)

// 搜索关键词
const searchKeyword = ref('')

// 版本列表
const versionList = ref<ImportableVersion[]>([])
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

// 选中的版本
const selectedVersion = ref<ImportableVersion | null>(null)

// 预览数据
const preview = ref<VersionPreview | null>(null)

// 导入表单
const importFormRef = ref<FormInstance>()
const importForm = reactive<ModelVersionImportRequest>({
  source_version_id: 0,
  import_type: 'structure_only',
  version: '',
  name: '',
  description: ''
})

const importRules: FormRules = {
  import_type: [{ required: true, message: '请选择导入内容', trigger: 'change' }],
  version: [
    { required: true, message: '请输入版本号', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9._-]+$/, message: '版本号只能包含字母、数字、点、下划线和连字符', trigger: 'blur' }
  ],
  name: [{ required: true, message: '请输入版本名称', trigger: 'blur' }]
}

// 导入状态
const importing = ref(false)
const importResult = ref<ModelVersionImportResponse | null>(null)

// 是否可以进入下一步
const canNext = computed(() => {
  if (currentStep.value === 0) {
    return selectedVersion.value !== null
  }
  if (currentStep.value === 1) {
    return preview.value !== null
  }
  return false
})

// 加载可导入版本列表
const loadVersions = async () => {
  try {
    const res = await getImportableVersions({
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size,
      search: searchKeyword.value || undefined
    })
    versionList.value = res.items
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('加载版本列表失败')
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadVersions()
}

// 选择版本
const handleVersionSelect = (row: ImportableVersion | null) => {
  selectedVersion.value = row
}

// 加载预览数据
const loadPreview = async () => {
  if (!selectedVersion.value) return

  try {
    const res = await previewVersion(selectedVersion.value.id)
    preview.value = res
  } catch (error) {
    ElMessage.error('加载预览数据失败')
  }
}

// 检查版本号唯一性
const checkVersionUnique = async () => {
  if (!importForm.version) return

  try {
    const res = await getModelVersions({ search: importForm.version })
    const exists = res.items.some(v => v.version === importForm.version)
    if (exists) {
      ElMessage.warning('版本号已存在，请使用其他版本号')
      return false
    }
    return true
  } catch (error) {
    return true
  }
}

// 下一步
const handleNext = async () => {
  if (currentStep.value === 0) {
    await loadPreview()
    currentStep.value++
  } else if (currentStep.value === 1) {
    // 预填充表单
    if (selectedVersion.value) {
      importForm.source_version_id = selectedVersion.value.id
      importForm.version = selectedVersion.value.version + '-copy'
      importForm.name = selectedVersion.value.name + ' (导入)'
      importForm.description = `从 ${selectedVersion.value.hospital_name} 导入`
    }
    currentStep.value++
  }
}

// 上一步
const handlePrevious = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 执行导入
const handleImport = async () => {
  if (!importFormRef.value) return

  await importFormRef.value.validate(async (valid) => {
    if (!valid) return

    // 再次检查版本号唯一性
    const isUnique = await checkVersionUnique()
    if (!isUnique) return

    try {
      importing.value = true
      const res = await importVersion(importForm)
      importResult.value = res
      currentStep.value = 3
      ElMessage.success('导入成功')
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '导入失败')
    } finally {
      importing.value = false
    }
  })
}

// 查看新版本
const handleViewNewVersion = () => {
  if (importResult.value) {
    emit('success', importResult.value.id)
    handleClose()
  }
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
  // 重置状态
  setTimeout(() => {
    currentStep.value = 0
    selectedVersion.value = null
    preview.value = null
    importResult.value = null
    searchKeyword.value = ''
    pagination.page = 1
    importFormRef.value?.resetFields()
  }, 300)
}

// 格式化日期
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 监听对话框打开
watch(dialogVisible, (visible) => {
  if (visible) {
    loadVersions()
  }
})
</script>

<style scoped>
.step-content {
  margin: 24px 0;
  min-height: 400px;
}

.step-select {
  padding: 0 16px;
}

.step-preview {
  padding: 0 16px;
}

.step-preview .statistics {
  margin-top: 24px;
}

.step-config {
  padding: 0 16px;
}

.step-config .warning-tip {
  margin-top: 8px;
}

.step-result {
  padding: 0 16px;
}

.step-result .result-info {
  text-align: left;
}

.step-result .result-info ul {
  margin: 0;
  padding-left: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
