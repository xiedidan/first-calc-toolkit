<template>
  <el-dialog
    v-model="visible"
    :title="dialogTitle"
    width="750px"
    append-to-body
    destroy-on-close
    @close="handleClose"
  >
    <!-- 基本信息 -->
    <div class="analysis-info">
      <el-descriptions :column="3" size="small" border>
        <el-descriptions-item label="科室">{{ departmentName }}</el-descriptions-item>
        <el-descriptions-item label="月份">{{ period }}</el-descriptions-item>
        <el-descriptions-item label="维度">{{ nodeName }}</el-descriptions-item>
      </el-descriptions>
    </div>
    
    <div class="analysis-sections">
      <!-- 当期分析 -->
      <div class="analysis-section">
        <div class="section-header">
          <span class="section-title">当期分析</span>
          <el-button 
            v-if="currentAnalysis" 
            type="danger" 
            text 
            size="small"
            @click="handleDelete('current')"
            :loading="deleting"
          >
            删除
          </el-button>
        </div>
        <el-input
          v-model="currentContent"
          type="textarea"
          :rows="3"
          placeholder="请输入当期分析内容..."
          maxlength="2000"
          show-word-limit
        />
        <div v-if="currentAnalysis" class="analysis-meta">
          <span>最后更新: {{ formatTime(currentAnalysis.updated_at) }}</span>
          <span v-if="currentAnalysis.updated_by_name"> 由 {{ currentAnalysis.updated_by_name }}</span>
        </div>
      </div>
      
      <!-- 长期分析 -->
      <div class="analysis-section">
        <div class="section-header">
          <span class="section-title">长期分析</span>
          <el-tag type="info" size="small">不限月份</el-tag>
          <el-button 
            v-if="longTermAnalysis" 
            type="danger" 
            text 
            size="small"
            @click="handleDelete('longTerm')"
            :loading="deleting"
            style="margin-left: auto;"
          >
            删除
          </el-button>
        </div>
        <el-input
          v-model="longTermContent"
          type="textarea"
          :rows="3"
          placeholder="请输入长期分析内容（适用于整体性、持续性分析）..."
          maxlength="2000"
          show-word-limit
        />
        <div v-if="longTermAnalysis" class="analysis-meta">
          <span>最后更新: {{ formatTime(longTermAnalysis.updated_at) }}</span>
          <span v-if="longTermAnalysis.updated_by_name"> 由 {{ longTermAnalysis.updated_by_name }}</span>
        </div>
      </div>
      
      <!-- 学科规则 -->
      <div class="analysis-section rule-section">
        <div class="section-header">
          <el-checkbox v-model="ruleEnabled" @change="handleRuleEnabledChange">
            <span class="section-title">学科规则</span>
          </el-checkbox>
          <el-tag type="warning" size="small">权重系数</el-tag>
        </div>
        
        <div v-if="ruleEnabled" class="rule-form">
          <div class="rule-row">
            <span class="rule-label">系数:</span>
            <el-input-number
              v-model="ruleCoefficient"
              :min="0"
              :max="100"
              :precision="4"
              :step="0.1"
              size="small"
              style="width: 140px"
            />
            <span class="rule-hint">（默认1.0，用于调整该科室在此维度上的业务价值权重）</span>
          </div>
          <el-input
            v-model="ruleDescription"
            type="textarea"
            :rows="2"
            placeholder="规则描述（可选）..."
            maxlength="500"
            show-word-limit
            style="margin-top: 8px;"
          />
          <div v-if="disciplineRule" class="analysis-meta">
            <span>更新时间: {{ formatTime(disciplineRule.updated_at) }}</span>
          </div>
        </div>
        <div v-else class="rule-disabled-hint">
          勾选启用后可设置该科室在此维度上的权重调整系数
        </div>
      </div>
    </div>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSaveAll" :loading="saving">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  getDimensionAnalysis, 
  createOrUpdateDimensionAnalysis, 
  deleteDimensionAnalysis,
  type DimensionAnalysis 
} from '@/api/dimension-analyses'
import {
  getDisciplineRules,
  createDisciplineRule,
  updateDisciplineRule,
  deleteDisciplineRule,
  type DisciplineRule
} from '@/api/discipline-rules'

const props = defineProps<{
  modelValue: boolean
  departmentId: number
  departmentCode: string
  departmentName: string
  nodeId: number
  nodeCode: string
  nodeName: string
  period: string
  versionId?: number
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'saved'): void
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const dialogTitle = computed(() => `维度分析 - ${props.nodeName}`)

const currentContent = ref('')
const longTermContent = ref('')
const currentAnalysis = ref<DimensionAnalysis | null>(null)
const longTermAnalysis = ref<DimensionAnalysis | null>(null)
const disciplineRule = ref<DisciplineRule | null>(null)
const ruleEnabled = ref(false)
const ruleCoefficient = ref(1.0)
const ruleDescription = ref('')
const saving = ref(false)
const deleting = ref(false)

// 处理规则启用状态变化
const handleRuleEnabledChange = (enabled: boolean | string | number) => {
  if (!enabled) {
    // 取消勾选时重置为默认值
    ruleCoefficient.value = 1.0
    ruleDescription.value = ''
  }
}

// 加载分析数据
const loadAnalyses = async () => {
  if (!props.departmentId || !props.nodeId) return
  
  // 加载当期分析
  try {
    const res = await getDimensionAnalysis({
      department_id: props.departmentId,
      node_id: props.nodeId,
      period: props.period
    })
    currentAnalysis.value = res
    currentContent.value = res.content
  } catch (e: unknown) {
    const err = e as { response?: { status?: number } }
    if (err.response?.status !== 404) {
      console.error('加载当期分析失败', e)
    }
    currentAnalysis.value = null
    currentContent.value = ''
  }
  
  // 加载长期分析
  try {
    const res = await getDimensionAnalysis({
      department_id: props.departmentId,
      node_id: props.nodeId,
      period: null
    })
    longTermAnalysis.value = res
    longTermContent.value = res.content
  } catch (e: unknown) {
    const err = e as { response?: { status?: number } }
    if (err.response?.status !== 404) {
      console.error('加载长期分析失败', e)
    }
    longTermAnalysis.value = null
    longTermContent.value = ''
  }
}

// 加载学科规则
const loadDisciplineRule = async () => {
  console.log('loadDisciplineRule called with:', {
    departmentCode: props.departmentCode,
    nodeCode: props.nodeCode,
    nodeId: props.nodeId,
    versionId: props.versionId
  })
  
  // 使用 nodeId 或 nodeCode 查询，只要有一个即可
  if (!props.departmentCode || !props.versionId || (!props.nodeCode && !props.nodeId)) {
    console.log('loadDisciplineRule skipped - missing params:', {
      hasDepartmentCode: !!props.departmentCode,
      hasNodeCode: !!props.nodeCode,
      hasNodeId: !!props.nodeId,
      hasVersionId: !!props.versionId
    })
    disciplineRule.value = null
    ruleEnabled.value = false
    ruleCoefficient.value = 1.0
    ruleDescription.value = ''
    return
  }
  
  try {
    const params: Record<string, unknown> = {
      version_id: props.versionId,
      department_code: props.departmentCode,
      size: 1
    }
    
    // 优先使用 nodeCode，如果没有则使用 nodeId
    if (props.nodeCode) {
      params.dimension_code = props.nodeCode
    } else if (props.nodeId) {
      params.node_id = props.nodeId
    }
    
    const res = await getDisciplineRules(params as any)
    
    if (res.items && res.items.length > 0) {
      disciplineRule.value = res.items[0]
      ruleEnabled.value = true
      ruleCoefficient.value = Number(res.items[0].rule_coefficient)
      ruleDescription.value = res.items[0].rule_description || ''
    } else {
      disciplineRule.value = null
      ruleEnabled.value = false
      ruleCoefficient.value = 1.0
      ruleDescription.value = ''
    }
  } catch (e: unknown) {
    console.error('加载学科规则失败', e)
    disciplineRule.value = null
    ruleEnabled.value = false
    ruleCoefficient.value = 1.0
    ruleDescription.value = ''
  }
}

// 监听对话框打开
watch(() => props.modelValue, (val) => {
  if (val) {
    loadAnalyses()
    loadDisciplineRule()
  }
})

// 保存所有内容
const handleSaveAll = async () => {
  const hasCurrent = currentContent.value.trim()
  const hasLongTerm = longTermContent.value.trim()
  
  saving.value = true
  try {
    const promises: Array<Promise<unknown>> = []
    
    // 保存当期分析
    if (hasCurrent) {
      promises.push(
        createOrUpdateDimensionAnalysis({
          department_id: props.departmentId,
          node_id: props.nodeId,
          period: props.period,
          content: currentContent.value.trim()
        }).then(res => { currentAnalysis.value = res })
      )
    }
    
    // 保存长期分析
    if (hasLongTerm) {
      promises.push(
        createOrUpdateDimensionAnalysis({
          department_id: props.departmentId,
          node_id: props.nodeId,
          period: null,
          content: longTermContent.value.trim()
        }).then(res => { longTermAnalysis.value = res })
      )
    }
    
    // 处理学科规则
    if (props.versionId) {
      if (ruleEnabled.value) {
        // 启用状态：创建或更新规则
        if (disciplineRule.value) {
          promises.push(
            updateDisciplineRule(disciplineRule.value.id, {
              rule_coefficient: ruleCoefficient.value,
              rule_description: ruleDescription.value || undefined
            })
          )
        } else {
          promises.push(
            createDisciplineRule({
              version_id: props.versionId,
              department_code: props.departmentCode,
              department_name: props.departmentName,
              dimension_code: props.nodeCode,
              dimension_name: props.nodeName,
              rule_coefficient: ruleCoefficient.value,
              rule_description: ruleDescription.value || undefined
            })
          )
        }
      } else if (disciplineRule.value) {
        // 未启用但存在规则：删除规则
        promises.push(
          deleteDisciplineRule(disciplineRule.value.id).then(() => {
            disciplineRule.value = null
          })
        )
      }
    }
    
    await Promise.all(promises)
    
    // 刷新规则状态
    if (ruleEnabled.value) {
      await loadDisciplineRule()
    }
    
    ElMessage.success('保存成功')
    emit('saved')
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    ElMessage.error(err.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

// 删除分析
const handleDelete = async (type: 'current' | 'longTerm') => {
  const analysis = type === 'current' ? currentAnalysis.value : longTermAnalysis.value
  if (!analysis) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除${type === 'current' ? '当期' : '长期'}分析吗？`,
      '确认删除',
      { type: 'warning' }
    )
  } catch {
    return
  }
  
  deleting.value = true
  try {
    await deleteDimensionAnalysis(analysis.id)
    
    if (type === 'current') {
      currentAnalysis.value = null
      currentContent.value = ''
    } else {
      longTermAnalysis.value = null
      longTermContent.value = ''
    }
    
    ElMessage.success('删除成功')
    emit('saved')
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    ElMessage.error(err.response?.data?.detail || '删除失败')
  } finally {
    deleting.value = false
  }
}

const handleClose = () => {
  visible.value = false
}

const formatTime = (time: string) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}
</script>

<style scoped>
.analysis-info {
  margin-bottom: 16px;
}

.analysis-sections {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.analysis-section {
  background: #fafafa;
  border-radius: 6px;
  padding: 14px;
}

.rule-section {
  background: #fffbe6;
  border: 1px solid #ffe58f;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.section-title {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
}

.rule-form {
  margin-top: 4px;
}

.rule-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rule-label {
  font-size: 13px;
  color: #606266;
}

.rule-hint {
  font-size: 12px;
  color: #909399;
}

.rule-disabled-hint {
  font-size: 13px;
  color: #909399;
  padding: 8px 0;
}

.analysis-meta {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}
</style>
