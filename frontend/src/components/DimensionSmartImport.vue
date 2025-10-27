<template>
  <el-dialog
    v-model="visible"
    title="维度目录智能导入"
    width="90%"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-steps :active="currentStep" finish-status="success" align-center>
      <el-step title="字段映射" />
      <el-step title="维度值映射" />
      <el-step title="预览与确认" />
    </el-steps>

    <div class="step-content">
      <!-- 第一步：字段映射 -->
      <div v-if="currentStep === 0" class="step-1">
        <el-alert
          title="请上传包含收费项目编码、维度预案、专家意见的Excel文件"
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
        />

        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          :on-change="handleFileChange"
          :on-exceed="handleExceed"
          accept=".xlsx"
          drag
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">只能上传 xlsx 文件</div>
          </template>
        </el-upload>

        <div v-if="parseResult" style="margin-top: 20px">
          <el-divider content-position="left">Excel配置</el-divider>
          
          <el-form :model="excelConfig" label-width="120px" style="margin-bottom: 20px">
            <el-form-item label="选择Sheet">
              <el-select v-model="excelConfig.sheetName" placeholder="请选择Sheet" @change="handleSheetChange">
                <el-option
                  v-for="sheet in parseResult.sheet_names"
                  :key="sheet"
                  :label="sheet"
                  :value="sheet"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="跳过前N行">
              <el-input-number
                v-model="excelConfig.skipRows"
                :min="0"
                :max="100"
                placeholder="跳过前N行"
                @change="handleSkipRowsChange"
              />
              <span style="margin-left: 10px; color: #909399; font-size: 12px">
                跳过前N行（包括表头），跳过后的第1行将作为新表头
              </span>
            </el-form-item>
          </el-form>

          <el-divider content-position="left">字段映射配置</el-divider>
          
          <el-form :model="fieldMapping" label-width="120px">
            <el-form-item label="匹配方式" required>
              <el-radio-group v-model="matchBy">
                <el-radio value="code">按收费编码匹配</el-radio>
                <el-radio value="name">按收费名称匹配</el-radio>
              </el-radio-group>
              <div style="margin-top: 8px; color: #909399; font-size: 12px">
                <span v-if="matchBy === 'code'">使用Excel中的收费编码直接匹配</span>
                <span v-else>使用Excel中的收费名称匹配，系统会自动转换为对应的收费编码</span>
              </div>
            </el-form-item>

            <el-form-item :label="matchBy === 'code' ? '收费编码' : '收费名称'" required>
              <el-select v-model="fieldMapping.item_code" placeholder="请选择">
                <el-option
                  v-for="header in parseResult.headers"
                  :key="header"
                  :label="header"
                  :value="header"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="维度预案">
              <el-select v-model="fieldMapping.dimension_plan" placeholder="请选择（可选）" clearable>
                <el-option
                  v-for="header in parseResult.headers"
                  :key="header"
                  :label="header"
                  :value="header"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="专家意见">
              <el-select v-model="fieldMapping.expert_opinion" placeholder="请选择（可选）" clearable>
                <el-option
                  v-for="header in parseResult.headers"
                  :key="header"
                  :label="header"
                  :value="header"
                />
              </el-select>
            </el-form-item>
          </el-form>

          <el-divider content-position="left">数据预览（前10行）</el-divider>
          <el-table :data="parseResult.preview_data" border max-height="300">
            <el-table-column
              label="行号"
              width="80"
              align="center"
              fixed="left"
            >
              <template #default="{ $index }">
                {{ parseResult.skip_rows + $index + 2 }}
              </template>
            </el-table-column>
            <el-table-column
              v-for="(header, index) in parseResult.headers"
              :key="index"
              :label="header"
              :prop="String(index)"
              min-width="120"
            >
              <template #default="{ row }">
                {{ row[index] }}
              </template>
            </el-table-column>
          </el-table>

          <div style="margin-top: 10px; color: #909399">
            <span>表头行号: {{ parseResult.skip_rows + 1 }}</span>
            <span style="margin-left: 20px">数据行 {{ parseResult.skip_rows + 2 }} - {{ parseResult.skip_rows + 1 + parseResult.total_rows }}</span>
            <span style="margin-left: 20px">共{{ parseResult.total_rows }} 行数据</span>
          </div>
        </div>
      </div>

      <!-- 第二步：维度值映射-->
      <div v-if="currentStep === 1" class="step-2">
        <el-alert
          title="请为每个唯一值指定对应的系统维度（支持一对多映射）"
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
        />

        <div v-if="extractResult" class="value-mapping-container">
          <!-- 专家意见组-->
          <template v-if="expertOpinionValues.length > 0">
            <div class="value-group-title">
              <el-tag type="danger" size="large">专家意见</el-tag>
              <span style="margin-left: 10px; color: #606266">共{{ expertOpinionValues.length }} 个唯一值</span>
            </div>
            <div
              v-for="(item, index) in expertOpinionValues"
              :key="`expert-${index}`"
              class="value-mapping-item"
            >
              <div class="value-info">
                <span class="value-text">{{ item.value }}</span>
                <span class="value-count">（出现{{ item.count }} 次）</span>
              </div>

              <el-select
                v-model="valueMapping[item.originalIndex].dimension_codes"
                multiple
                placeholder="请选择对应的系统维度（可多选）"
                filterable
                default-first-option
                style="width: 100%"
              >
                <el-option-group v-if="item.suggested_dimensions.length > 0" label="💡 智能匹配建议（推荐）">
                  <el-option
                    v-for="dim in item.suggested_dimensions"
                    :key="dim.id"
                    :label="`${dim.full_path} (匹配度 ${(dim.score * 100).toFixed(0)}%)`"
                    :value="dim.code"
                  >
                    <span>{{ dim.full_path }}</span>
                    <span style="float: right; color: #8492a6; font-size: 13px">
                      {{ (dim.score * 100).toFixed(0) }}%
                    </span>
                  </el-option>
                </el-option-group>
                <el-option-group label="📋 所有维度">
                  <el-option
                    v-for="dim in extractResult.system_dimensions"
                    :key="dim.id"
                    :label="dim.full_path"
                    :value="dim.code"
                  />
                </el-option-group>
              </el-select>
            </div>
          </template>

          <!-- 维度预案组 -->
          <template v-if="dimensionPlanValues.length > 0">
            <div class="value-group-title" style="margin-top: 30px">
              <el-tag type="primary" size="large">维度预案</el-tag>
              <span style="margin-left: 10px; color: #606266">共{{ dimensionPlanValues.length }} 个唯一值</span>
            </div>
            <div
              v-for="(item, index) in dimensionPlanValues"
              :key="`plan-${index}`"
              class="value-mapping-item"
            >
              <div class="value-info">
                <span class="value-text">{{ item.value }}</span>
                <span class="value-count">（出现{{ item.count }} 次）</span>
              </div>

              <el-select
                v-model="valueMapping[item.originalIndex].dimension_codes"
                multiple
                placeholder="请选择对应的系统维度（可多选）"
                filterable
                default-first-option
                style="width: 100%"
              >
                <el-option-group v-if="item.suggested_dimensions.length > 0" label="💡 智能匹配建议（推荐）">
                  <el-option
                    v-for="dim in item.suggested_dimensions"
                    :key="dim.id"
                    :label="`${dim.full_path} (匹配度 ${(dim.score * 100).toFixed(0)}%)`"
                    :value="dim.code"
                  >
                    <span>{{ dim.full_path }}</span>
                    <span style="float: right; color: #8492a6; font-size: 13px">
                      {{ (dim.score * 100).toFixed(0) }}%
                    </span>
                  </el-option>
                </el-option-group>
                <el-option-group label="📋 所有维度">
                  <el-option
                    v-for="dim in extractResult.system_dimensions"
                    :key="dim.id"
                    :label="dim.full_path"
                    :value="dim.code"
                  />
                </el-option-group>
              </el-select>
            </div>
          </template>
        </div>
      </div>

      <!-- 第三步：预览与确认-->
      <div v-if="currentStep === 2" class="step-3">
        <el-alert
          v-if="previewResult"
          :title="`共${previewResult.statistics.total} 条记录，正常 ${previewResult.statistics.ok} 条，警告 ${previewResult.statistics.warning} 条，错误 ${previewResult.statistics.error} 条`"
          :type="previewResult.statistics.error > 0 ? 'error' : 'success'"
          :closable="false"
          style="margin-bottom: 20px"
        />

        <el-table
          v-if="previewResult"
          :data="previewResult.preview_items"
          border
          max-height="500"
        >
          <el-table-column label="状态" width="80" align="center">
            <template #default="{ row }">
              <el-tag
                :type="row.status === 'ok' ? 'success' : row.status === 'warning' ? 'warning' : 'danger'"
                size="small"
              >
                {{ row.status === 'ok' ? '正常' : row.status === 'warning' ? '警告' : '错误' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="item_code" label="收费编码" width="120" />
          <el-table-column prop="item_name" label="收费名称" width="150" />
          <el-table-column prop="dimension_path" label="目标维度" min-width="200" />
          <el-table-column label="来源" width="100">
            <template #default="{ row }">
              <el-tag size="small" :type="row.source === 'expert_opinion' ? 'danger' : 'primary'">
                {{ row.source === 'expert_opinion' ? '专家意见' : '维度预案' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="source_value" label="来源值" width="120" />
          <el-table-column prop="message" label="提示信息" min-width="150" />
        </el-table>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button v-if="currentStep > 0" @click="handlePrevious">上一步</el-button>
        <el-button
          v-if="currentStep < 2"
          type="primary"
          :disabled="!canNext"
          :loading="loading"
          @click="handleNext"
        >
          下一步
        </el-button>
        <el-button
          v-if="currentStep === 2"
          type="primary"
          :loading="loading"
          @click="handleExecute"
        >
          执行导入
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox, type UploadInstance, type UploadFile } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import {
  parseExcel,
  extractValues,
  generatePreview,
  executeImport,
  type SmartImportParseResponse,
  type SmartImportExtractResponse,
  type SmartImportPreviewResponse,
  type ValueMapping
} from '@/api/dimension-import'

// Props
interface Props {
  modelValue: boolean
  modelVersionId: number
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}>()

// Data
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const currentStep = ref(0)
const loading = ref(false)
const uploadRef = ref<UploadInstance>()
const currentFile = ref<File | null>(null)

// 第一步数据
const parseResult = ref<SmartImportParseResponse | null>(null)
const excelConfig = ref({
  sheetName: '',
  skipRows: 0
})
const fieldMapping = ref<Record<string, string>>({
  item_code: '',
  dimension_plan: '',
  expert_opinion: ''
})
const matchBy = ref<'code' | 'name'>('code') // 匹配方式：code(按编码) 或 name(按名称)

// 第二步数据
const extractResult = ref<SmartImportExtractResponse | null>(null)
const valueMapping = ref<ValueMapping[]>([])

// 第三步数据
const previewResult = ref<SmartImportPreviewResponse | null>(null)

// Computed
const canNext = computed(() => {
  if (currentStep.value === 0) {
    return parseResult.value && fieldMapping.value.item_code
  }
  if (currentStep.value === 1) {
    return valueMapping.value.some(m => m.dimension_codes.length > 0)
  }
  return false
})

// 分组显示：专家意见
const expertOpinionValues = computed(() => {
  if (!extractResult.value) return []
  return extractResult.value.unique_values
    .map((item, index) => ({ ...item, originalIndex: index }))
    .filter(item => item.source === 'expert_opinion')
})

// 分组显示：维度预案
const dimensionPlanValues = computed(() => {
  if (!extractResult.value) return []
  return extractResult.value.unique_values
    .map((item, index) => ({ ...item, originalIndex: index }))
    .filter(item => item.source === 'dimension_plan')
})

// Watch
watch(() => extractResult.value?.unique_values, (newVal) => {
  if (newVal) {
    valueMapping.value = newVal.map(item => ({
      value: item.value,
      source: item.source,
      dimension_codes: item.suggested_dimensions.length > 0 ? [item.suggested_dimensions[0].code] : []
    }))
  }
}, { immediate: true })

// Methods
const handleFileChange = (file: UploadFile) => {
  if (file.raw) {
    currentFile.value = file.raw
    handleParse()
  }
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

const handleParse = async (showMessage = true) => {
  if (!currentFile.value) {
    ElMessage.error('请选择文件')
    return
  }

  loading.value = true
  try {
    const result = await parseExcel(
      currentFile.value,
      excelConfig.value.sheetName || undefined,
      excelConfig.value.skipRows
    )
    parseResult.value = result
    excelConfig.value.sheetName = result.current_sheet
    excelConfig.value.skipRows = result.skip_rows
    
    // 清空字段映射，让用户重新选择
    fieldMapping.value = {
      item_code: result.suggested_mapping.item_code || '',
      dimension_plan: result.suggested_mapping.dimension_plan || '',
      expert_opinion: result.suggested_mapping.expert_opinion || ''
    }
    
    if (showMessage) {
      ElMessage.success('文件解析成功')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '文件解析失败')
  } finally {
    loading.value = false
  }
}

const handleSheetChange = () => {
  // Sheet改变时重新解析
  handleParse(false)
}

const handleSkipRowsChange = () => {
  // 跳过行数改变时重新解析
  handleParse(false)
}

const handleNext = async () => {
  if (currentStep.value === 0) {
    // 第一步 -> 第二步
    if (!parseResult.value) {
      ElMessage.error('请先上传并解析文件')
      return
    }

    if (!fieldMapping.value.item_code) {
      ElMessage.error('请选择收费编码字段')
      return
    }

    if (!fieldMapping.value.dimension_plan && !fieldMapping.value.expert_opinion) {
      ElMessage.error('请至少选择维度预案或专家意见字段')
      return
    }

    loading.value = true
    try {
      const result = await extractValues({
        session_id: parseResult.value.session_id,
        field_mapping: fieldMapping.value,
        model_version_id: props.modelVersionId,
        match_by: matchBy.value
      })
      extractResult.value = result
      currentStep.value = 1
    } catch (error: any) {
      ElMessage.error(error.message || '提取唯一值失败')
    } finally {
      loading.value = false
    }
  } else if (currentStep.value === 1) {
    // 第二步 -> 第三步
    const validMappings = valueMapping.value.filter(m => m.dimension_codes.length > 0)
    if (validMappings.length === 0) {
      ElMessage.error('请至少为一个值指定对应的维度')
      return
    }

    loading.value = true
    try {
      const result = await generatePreview({
        session_id: parseResult.value!.session_id,
        value_mapping: validMappings
      })
      previewResult.value = result
      currentStep.value = 2
    } catch (error: any) {
      ElMessage.error(error.message || '生成预览失败')
    } finally {
      loading.value = false
    }
  }
}

const handlePrevious = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const handleExecute = async () => {
  if (!previewResult.value) {
    return
  }

  if (previewResult.value.statistics.error > 0) {
    try {
      await ElMessageBox.confirm(
        `存在 ${previewResult.value.statistics.error} 条错误记录，这些记录将被跳过。是否继续导入？`,
        '确认导入',
        {
          confirmButtonText: '继续导入',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
    } catch {
      return
    }
  }

  loading.value = true
  try {
    const result = await executeImport({
      session_id: parseResult.value!.session_id
    })

    if (result.success) {
      ElMessage.success(
        `导入完成！成功${result.report.success_count} 条，跳过 ${result.report.skipped_count} 条，失败 ${result.report.error_count} 条`
      )
      emit('success')
      handleClose()
    } else {
      ElMessage.error('导入失败')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '导入失败')
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  currentStep.value = 0
  parseResult.value = null
  extractResult.value = null
  previewResult.value = null
  excelConfig.value = {
    sheetName: '',
    skipRows: 0
  }
  fieldMapping.value = {
    item_code: '',
    dimension_plan: '',
    expert_opinion: ''
  }
  matchBy.value = 'code'  // 重置匹配方式
  valueMapping.value = []
  currentFile.value = null
  uploadRef.value?.clearFiles()
  visible.value = false
}
</script>

<style scoped>
.step-content {
  margin-top: 30px;
  min-height: 400px;
}

.value-mapping-container {
  max-height: 500px;
  overflow-y: auto;
}

.value-group-title {
  margin-bottom: 15px;
  padding: 10px 15px;
  background-color: #f5f7fa;
  border-left: 4px solid #409eff;
  border-radius: 4px;
  display: flex;
  align-items: center;
}

.value-mapping-item {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.value-info {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.value-text {
  font-weight: bold;
  font-size: 14px;
}

.value-count {
  color: #909399;
  font-size: 12px;
}

.el-icon--upload {
  font-size: 67px;
  color: #409eff;
  margin: 40px 0 16px;
}
</style>
