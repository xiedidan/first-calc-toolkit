<template>
  <el-dialog
    v-model="visible"
    title="批量导入"
    width="900px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <!-- 步骤条 -->
    <el-steps :active="currentStep" align-center style="margin-bottom: 30px">
      <el-step title="上传文件" />
      <el-step title="字段映射" />
      <el-step title="数据预览" />
      <el-step title="导入结果" />
    </el-steps>

    <!-- 步骤1: 上传文件 -->
    <div v-if="currentStep === 0" class="step-content">
      <el-upload
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        :file-list="fileList"
        accept=".xlsx"
        :limit="1"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          点击或拖拽文件到此处上传
        </div>
        <template #tip>
          <div class="el-upload__tip">
            仅支持 .xlsx 格式（Excel 2007及以上版本），文件大小不超过10MB
          </div>
        </template>
      </el-upload>
      <div style="margin-top: 20px; text-align: center">
        <el-button @click="downloadTemplate">
          <el-icon><Download /></el-icon>
          下载导入模板
        </el-button>
      </div>
    </div>

    <!-- 步骤2: 字段映射 -->
    <div v-if="currentStep === 1" class="step-content">
      <el-alert
        title="请配置Excel列与系统字段的对应关系"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      />
      <el-table :data="mappingData" border max-height="400">
        <el-table-column label="Excel列名" prop="excelColumn" width="200" />
        <el-table-column label="系统字段" width="250">
          <template #default="{ row }">
            <el-select v-model="row.systemField" placeholder="请选择" style="width: 100%">
              <el-option label="不导入" value="" />
              <el-option
                v-for="field in systemFields"
                :key="field.value"
                :label="field.label + (field.required ? ' *' : '')"
                :value="field.value"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="必填" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="isRequired(row.systemField)" type="danger" size="small">
              必填
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="示例数据">
          <template #default="{ row }">
            <span class="sample-data">{{ row.sampleData }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 步骤3: 数据预览 -->
    <div v-if="currentStep === 2" class="step-content">
      <el-alert
        :title="`共 ${totalRows} 条数据，预览前 ${previewData.length} 条`"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      />
      <el-table :data="previewData" border max-height="400">
        <el-table-column type="index" label="#" width="50" />
        <el-table-column
          v-for="field in mappedFields"
          :key="field.value"
          :label="field.label"
          :prop="field.value"
          min-width="120"
        />
      </el-table>
    </div>

    <!-- 步骤4: 导入结果 -->
    <div v-if="currentStep === 3" class="step-content">
      <!-- 导入中：显示进度 -->
      <div v-if="importing" style="text-align: center; padding: 40px 0">
        <el-icon class="rotating" style="font-size: 48px; color: #409eff; margin-bottom: 20px">
          <Loading />
        </el-icon>
        <div style="font-size: 16px; margin-bottom: 20px">{{ importProgress.status }}</div>
        <el-progress 
          v-if="importProgress.total > 0"
          :percentage="Math.round((importProgress.current / importProgress.total) * 100)"
          :format="() => `${importProgress.current} / ${importProgress.total}`"
          style="width: 60%; margin: 0 auto"
        />
      </div>

      <!-- 导入完成：显示结果 -->
      <el-result
        v-else
        :icon="importResult.failed_count === 0 ? 'success' : 'warning'"
        :title="importResult.failed_count === 0 ? '导入成功' : '导入完成'"
      >
        <template #sub-title>
          <div style="font-size: 16px">
            <div>成功: <span style="color: #67c23a; font-weight: bold">{{ importResult.success_count }}</span> 条</div>
            <div v-if="importResult.failed_count > 0">
              失败: <span style="color: #f56c6c; font-weight: bold">{{ importResult.failed_count }}</span> 条
            </div>
          </div>
        </template>
      </el-result>

      <!-- 失败记录 -->
      <div v-if="importResult.failed_count > 0" style="margin-top: 20px">
        <el-divider />
        <h4>失败记录</h4>
        <el-table :data="importResult.failed_items" border max-height="300">
          <el-table-column label="行号" prop="row" width="80" />
          <el-table-column label="数据" min-width="200">
            <template #default="{ row }">
              {{ JSON.stringify(row.data) }}
            </template>
          </el-table-column>
          <el-table-column label="失败原因" prop="reason" min-width="200" />
        </el-table>
      </div>
    </div>

    <!-- 底部按钮 -->
    <template #footer>
      <el-button v-if="currentStep > 0 && currentStep < 3" @click="prevStep">
        上一步
      </el-button>
      <el-button @click="handleClose">
        {{ currentStep === 3 ? '关闭' : '取消' }}
      </el-button>
      <el-button
        v-if="currentStep < 2"
        type="primary"
        @click="nextStep"
        :disabled="!canNext"
      >
        下一步
      </el-button>
      <el-button
        v-if="currentStep === 2"
        type="primary"
        @click="executeImport"
        :loading="importing"
      >
        开始导入
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Download, Loading } from '@element-plus/icons-vue'
import type { UploadFile, UploadUserFile } from 'element-plus'
import request from '@/utils/request'

interface Props {
  modelValue: boolean
  importConfig: {
    fields: Array<{
      value: string
      label: string
      required: boolean
    }>
    parseUrl: string
    importUrl: string
    templateUrl: string
  }
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const currentStep = ref(0)
const fileList = ref<UploadUserFile[]>([])
const currentFile = ref<File | null>(null)
const importing = ref(false)

// 解析结果
const parseResult = ref<any>(null)
const mappingData = ref<any[]>([])
const systemFields = computed(() => props.importConfig.fields)

// 预览数据
const previewData = ref<any[]>([])
const totalRows = ref(0)
const mappedFields = computed(() => {
  return systemFields.value.filter(f => 
    mappingData.value.some(m => m.systemField === f.value)
  )
})

// 导入结果
const importResult = ref({
  success_count: 0,
  failed_count: 0,
  failed_items: []
})

// 异步导入相关
const taskId = ref<string>('')
const importProgress = ref({
  current: 0,
  total: 0,
  status: ''
})
const pollingTimer = ref<number | null>(null)

// 是否可以进入下一步
const canNext = computed(() => {
  if (currentStep.value === 0) {
    return currentFile.value !== null
  }
  if (currentStep.value === 1) {
    // 检查必填字段是否都已映射
    const requiredFields = systemFields.value.filter(f => f.required)
    const mappedSystemFields = mappingData.value
      .filter(m => m.systemField)
      .map(m => m.systemField)
    return requiredFields.every(f => mappedSystemFields.includes(f.value))
  }
  return true
})

// 文件选择
const handleFileChange = (file: UploadFile) => {
  if (file.raw) {
    // 验证文件格式
    const fileName = file.name.toLowerCase()
    if (!fileName.endsWith('.xlsx')) {
      ElMessage.error('仅支持 .xlsx 格式文件，请使用 Excel 2007 及以上版本保存')
      fileList.value = []
      currentFile.value = null
      return
    }
    currentFile.value = file.raw
    fileList.value = [file]
  }
}

// 下载模板
const downloadTemplate = async () => {
  try {
    const response = await request.get(props.importConfig.templateUrl, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'import_template.xlsx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('下载模板失败')
  }
}

// 下一步
const nextStep = async () => {
  if (currentStep.value === 0) {
    // 解析Excel
    await parseExcel()
  } else if (currentStep.value === 1) {
    // 生成预览数据
    generatePreview()
  }
  currentStep.value++
}

// 上一步
const prevStep = () => {
  currentStep.value--
}

// 解析Excel
const parseExcel = async () => {
  if (!currentFile.value) return

  const formData = new FormData()
  formData.append('file', currentFile.value)

  try {
    const result = await request.post(props.importConfig.parseUrl, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    parseResult.value = result
    totalRows.value = result.total_rows

    // 初始化映射数据
    mappingData.value = result.headers.map((header: string, index: number) => ({
      excelColumn: header,
      systemField: result.suggested_mapping[header] || '',
      sampleData: result.preview_data[0]?.[index] || ''
    }))
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '解析Excel失败')
    throw error
  }
}

// 生成预览数据
const generatePreview = () => {
  if (!parseResult.value) return

  const mapping: any = {}
  mappingData.value.forEach(m => {
    if (m.systemField) {
      mapping[m.excelColumn] = m.systemField
    }
  })

  // 转换预览数据
  previewData.value = parseResult.value.preview_data.map((row: any[]) => {
    const obj: any = {}
    parseResult.value.headers.forEach((header: string, index: number) => {
      const systemField = mapping[header]
      if (systemField) {
        obj[systemField] = row[index] || ''
      }
    })
    return obj
  })
}

// 执行导入
const executeImport = async () => {
  if (!currentFile.value) return

  importing.value = true

  try {
    // 构建映射关系
    const mapping: any = {}
    mappingData.value.forEach(m => {
      if (m.systemField) {
        mapping[m.excelColumn] = m.systemField
      }
    })

    const formData = new FormData()
    formData.append('file', currentFile.value)
    formData.append('mapping', JSON.stringify(mapping))
    formData.append('async_mode', 'true')

    const result = await request.post(props.importConfig.importUrl, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    // 异步模式：开始轮询任务状态
    if (result.task_id) {
      taskId.value = result.task_id
      currentStep.value = 3
      startPolling()
    } 
    // 同步模式：直接显示结果
    else {
      importResult.value = result
      currentStep.value = 3
      importing.value = false

      if (result.failed_count === 0) {
        ElMessage.success(`成功导入 ${result.success_count} 条数据`)
        emit('success')
      } else {
        ElMessage.warning(`导入完成：成功 ${result.success_count} 条，失败 ${result.failed_count} 条`)
      }
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '导入失败')
    importing.value = false
  }
}

// 开始轮询任务状态
const startPolling = () => {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value)
  }

  pollingTimer.value = window.setInterval(async () => {
    await checkTaskStatus()
  }, 1000) // 每秒查询一次
}

// 停止轮询
const stopPolling = () => {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value)
    pollingTimer.value = null
  }
}

// 查询任务状态
const checkTaskStatus = async () => {
  if (!taskId.value) return

  try {
    const statusUrl = props.importConfig.importUrl.replace('/import', `/import/status/${taskId.value}`)
    const status = await request.get(statusUrl)

    if (status.state === 'PROCESSING') {
      // 更新进度
      importProgress.value = {
        current: status.current || 0,
        total: status.total || 0,
        status: status.status || '处理中...'
      }
    } else if (status.state === 'SUCCESS') {
      // 导入完成
      stopPolling()
      importing.value = false
      importResult.value = status.result

      if (status.result.failed_count === 0) {
        ElMessage.success(`成功导入 ${status.result.success_count} 条数据`)
      } else {
        ElMessage.warning(`导入完成：成功 ${status.result.success_count} 条，失败 ${status.result.failed_count} 条`)
      }
      
      // 触发成功事件，通知父组件刷新列表
      emit('success')
    } else if (status.state === 'FAILURE') {
      // 导入失败
      stopPolling()
      importing.value = false
      ElMessage.error(`导入失败: ${status.error}`)
      
      // 即使失败也触发成功事件，因为可能有部分数据导入成功
      emit('success')
    }
  } catch (error: any) {
    console.error('查询任务状态失败:', error)
  }
}

// 判断字段是否必填
const isRequired = (fieldValue: string) => {
  return systemFields.value.find(f => f.value === fieldValue)?.required || false
}

// 关闭对话框
const handleClose = () => {
  // 停止轮询
  stopPolling()
  
  // 如果有导入结果（成功或失败），触发刷新
  const hasImportResult = importResult.value.success_count > 0 || importResult.value.failed_count > 0
  
  visible.value = false
  
  // 如果有导入结果，通知父组件刷新
  if (hasImportResult) {
    emit('success')
  }
  
  // 重置状态
  setTimeout(() => {
    currentStep.value = 0
    fileList.value = []
    currentFile.value = null
    parseResult.value = null
    mappingData.value = []
    previewData.value = []
    importResult.value = {
      success_count: 0,
      failed_count: 0,
      failed_items: []
    }
    taskId.value = ''
    importProgress.value = {
      current: 0,
      total: 0,
      status: ''
    }
    importing.value = false
  }, 300)
}
</script>

<style scoped>
.step-content {
  min-height: 400px;
}

.sample-data {
  color: #909399;
  font-size: 12px;
}

.el-icon--upload {
  font-size: 67px;
  color: #409eff;
  margin: 40px 0 16px;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.rotating {
  animation: rotate 2s linear infinite;
}
</style>
