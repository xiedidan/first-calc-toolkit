<template>
  <el-dialog
    v-model="visible"
    :title="dialogTitle"
    width="800px"
    append-to-body
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div v-loading="loading">
      <el-tabs v-model="activeTab">
        <!-- 业务属性 -->
        <el-tab-pane label="业务属性" name="business">
          <el-form
            ref="businessFormRef"
            :model="form"
            :rules="rules"
            label-width="100px"
            class="edit-form"
          >
            <el-form-item label="所属项目">
              <span class="readonly-value">{{ projectName || '-' }}</span>
            </el-form-item>
            <el-form-item label="所属主题" prop="topic_id">
              <el-select
                v-model="form.topic_id"
                placeholder="请选择主题"
                style="width: 100%"
                filterable
              >
                <el-option-group
                  v-for="project in projectsWithTopics"
                  :key="project.id"
                  :label="project.name"
                >
                  <el-option
                    v-for="topic in project.topics"
                    :key="topic.id"
                    :label="topic.name"
                    :value="topic.id"
                  />
                </el-option-group>
              </el-select>
            </el-form-item>
            <el-form-item label="业务口径">
              <el-input
                v-model="form.business_caliber"
                type="textarea"
                :rows="6"
                placeholder="请输入业务口径，描述指标的业务含义和计算规则"
              />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 技术属性 -->
        <el-tab-pane label="技术属性" name="technical">
          <el-form
            ref="technicalFormRef"
            :model="form"
            :rules="rules"
            label-width="100px"
            class="edit-form"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="中文名称" prop="name_cn">
                  <el-input
                    v-model="form.name_cn"
                    placeholder="请输入中文名称"
                    maxlength="200"
                    show-word-limit
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="英文名称">
                  <el-input
                    v-model="form.name_en"
                    placeholder="请输入英文名称"
                    maxlength="200"
                    show-word-limit
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="指标类型" prop="metric_type">
                  <el-select
                    v-model="form.metric_type"
                    placeholder="请选择指标类型"
                    style="width: 100%"
                  >
                    <el-option label="原子指标" value="atomic">
                      <span>原子指标</span>
                      <span class="option-desc">不可再分解的基础指标</span>
                    </el-option>
                    <el-option label="复合指标" value="composite">
                      <span>复合指标</span>
                      <span class="option-desc">由多个原子指标组合计算</span>
                    </el-option>
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="指标层级">
                  <el-input
                    v-model="form.metric_level"
                    placeholder="请输入指标层级"
                    maxlength="100"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="技术口径">
              <el-input
                v-model="form.technical_caliber"
                type="textarea"
                :rows="4"
                placeholder="请输入技术口径，描述指标的技术实现细节"
              />
            </el-form-item>
            <el-form-item label="数据源">
              <el-select
                v-model="form.data_source_id"
                placeholder="请选择数据源"
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="ds in dataSources"
                  :key="ds.id"
                  :label="ds.name"
                  :value="ds.id"
                />
              </el-select>
              <div class="form-item-tip">选择数据源后可从中加载表列表</div>
            </el-form-item>
            <el-form-item label="指标源表">
              <el-select
                v-model="form.source_tables"
                multiple
                filterable
                allow-create
                default-first-option
                :placeholder="form.data_source_id ? '请选择事实表' : '请先选择数据源'"
                style="width: 100%"
                :loading="loadingTables"
              >
                <el-option
                  v-for="table in factTables"
                  :key="table"
                  :label="table"
                  :value="table"
                />
              </el-select>
              <div class="form-item-tip">事实表（非 mb_/dim_ 开头），可手动输入</div>
            </el-form-item>
            <el-form-item label="关联维表">
              <el-select
                v-model="form.dimension_tables"
                multiple
                filterable
                allow-create
                default-first-option
                :placeholder="form.data_source_id ? '请选择维表' : '请先选择数据源'"
                style="width: 100%"
                :loading="loadingTables"
              >
                <el-option
                  v-for="table in dimensionTables"
                  :key="table"
                  :label="table"
                  :value="table"
                />
              </el-select>
              <div class="form-item-tip">维表（mb_/dim_ 开头），可手动输入</div>
            </el-form-item>
            <el-form-item label="指标维度">
              <el-select
                v-model="form.dimensions"
                multiple
                filterable
                allow-create
                default-first-option
                placeholder="请输入或选择指标维度"
                style="width: 100%"
              >
                <el-option
                  v-for="dim in commonDimensions"
                  :key="dim"
                  :label="dim"
                  :value="dim"
                />
              </el-select>
              <div class="form-item-tip">可手动输入新的维度名称，按回车确认</div>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button @click="resetForm">重置</el-button>
      <el-button type="primary" @click="handleSave" :loading="saving">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import {
  getMetric,
  updateMetric,
  type Metric,
  type MetricUpdate,
  type MetricType
} from '@/api/metrics'
import { getMetricProjects, type MetricProject } from '@/api/metric-projects'
import { getMetricTopics, type MetricTopic } from '@/api/metric-topics'
import request from '@/utils/request'

// Props
const props = defineProps<{
  modelValue: boolean
  metricId: number | null
}>()

// Emits
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'saved', metric: Metric): void
}>()

// 状态
const visible = ref(false)
const loading = ref(false)
const saving = ref(false)
const activeTab = ref('business')
const businessFormRef = ref<FormInstance>()
const technicalFormRef = ref<FormInstance>()

// 数据
const metric = ref<Metric | null>(null)
const allProjects = ref<MetricProject[]>([])
const allTopics = ref<MetricTopic[]>([])
const dataSources = ref<{ id: number; name: string }[]>([])
const loadingTables = ref(false)
const factTables = ref<string[]>([])
const dimensionTables = ref<string[]>([])

// 表单数据
const form = reactive<MetricUpdate & { topic_id: number }>({
  topic_id: 0,
  name_cn: '',
  name_en: '',
  metric_type: 'atomic',
  metric_level: '',
  business_caliber: '',
  technical_caliber: '',
  source_tables: [],
  dimension_tables: [],
  dimensions: [],
  data_source_id: undefined
})

// 原始数据，用于重置
const originalForm = ref<MetricUpdate & { topic_id: number }>({
  topic_id: 0,
  name_cn: '',
  name_en: '',
  metric_type: 'atomic',
  metric_level: '',
  business_caliber: '',
  technical_caliber: '',
  source_tables: [],
  dimension_tables: [],
  dimensions: [],
  data_source_id: undefined
})

// 表单验证规则
const rules: FormRules = {
  name_cn: [
    { required: true, message: '请输入中文名称', trigger: 'blur' },
    { max: 200, message: '中文名称不能超过200个字符', trigger: 'blur' }
  ],
  topic_id: [
    { required: true, message: '请选择所属主题', trigger: 'change' }
  ],
  metric_type: [
    { required: true, message: '请选择指标类型', trigger: 'change' }
  ]
}

// 常用维度（可扩展）
const commonDimensions = [
  '科室',
  '医生',
  '时间',
  '病种',
  '收费项目',
  '患者类型',
  '就诊类型'
]

// 计算属性
const dialogTitle = computed(() => {
  return metric.value ? `编辑指标 - ${metric.value.name_cn}` : '编辑指标'
})

const projectName = computed(() => {
  if (!form.topic_id) return ''
  const topic = allTopics.value.find(t => t.id === form.topic_id)
  return topic?.project_name || ''
})

// 按项目分组的主题列表
const projectsWithTopics = computed(() => {
  const projectMap = new Map<number, { id: number; name: string; topics: MetricTopic[] }>()
  
  for (const project of allProjects.value) {
    projectMap.set(project.id, {
      id: project.id,
      name: project.name,
      topics: []
    })
  }
  
  for (const topic of allTopics.value) {
    const project = projectMap.get(topic.project_id)
    if (project) {
      project.topics.push(topic)
    }
  }
  
  return Array.from(projectMap.values()).filter(p => p.topics.length > 0)
})

// 加载数据源的表列表
const loadDataSourceTables = async (dataSourceId: number) => {
  if (!dataSourceId) {
    factTables.value = []
    dimensionTables.value = []
    return
  }
  
  loadingTables.value = true
  try {
    const res = await request.get(`/data-sources/${dataSourceId}/tables`)
    factTables.value = res.data?.fact_tables || []
    dimensionTables.value = res.data?.dimension_tables || []
  } catch (error: any) {
    console.error('加载表列表失败:', error)
    factTables.value = []
    dimensionTables.value = []
    // 不显示错误提示，允许手动输入
  } finally {
    loadingTables.value = false
  }
}

// 监听数据源变化
watch(() => form.data_source_id, (newVal) => {
  if (newVal) {
    loadDataSourceTables(newVal)
  } else {
    factTables.value = []
    dimensionTables.value = []
  }
})

// 监听visible状态
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.metricId) {
    loadData()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 加载数据
const loadData = async () => {
  if (!props.metricId) return
  
  loading.value = true
  try {
    // 并行加载所有数据
    const [metricData, projectsRes, topicsRes, dsRes] = await Promise.all([
      getMetric(props.metricId),
      getMetricProjects(),
      getMetricTopics(),
      request.get('/data-sources')
    ])
    
    metric.value = metricData
    allProjects.value = projectsRes.items
    allTopics.value = topicsRes.items
    // 数据源API返回格式: { code, message, data: { items, total } }
    dataSources.value = dsRes.data?.items || []
    
    // 填充表单
    fillForm(metricData)
  } catch (error) {
    console.error('加载指标数据失败:', error)
    ElMessage.error('加载指标数据失败')
  } finally {
    loading.value = false
  }
}

// 填充表单数据
const fillForm = (data: Metric) => {
  const formData = {
    topic_id: data.topic_id,
    name_cn: data.name_cn || '',
    name_en: data.name_en || '',
    metric_type: data.metric_type || 'atomic',
    metric_level: data.metric_level || '',
    business_caliber: data.business_caliber || '',
    technical_caliber: data.technical_caliber || '',
    source_tables: data.source_tables || [],
    dimension_tables: data.dimension_tables || [],
    dimensions: data.dimensions || [],
    data_source_id: data.data_source_id || undefined
  }
  
  Object.assign(form, formData)
  originalForm.value = { ...formData }
  
  // 如果有数据源，加载表列表
  if (data.data_source_id) {
    loadDataSourceTables(data.data_source_id)
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(form, { ...originalForm.value })
  ElMessage.info('已重置为保存的配置')
}

// 保存
const handleSave = async () => {
  if (!props.metricId) return
  
  // 验证表单
  let valid = true
  
  if (businessFormRef.value) {
    await businessFormRef.value.validate((isValid) => {
      if (!isValid) valid = false
    }).catch(() => { valid = false })
  }
  
  if (technicalFormRef.value) {
    await technicalFormRef.value.validate((isValid) => {
      if (!isValid) valid = false
    }).catch(() => { valid = false })
  }
  
  if (!valid) {
    ElMessage.warning('请检查表单填写是否正确')
    return
  }

  saving.value = true
  try {
    const updateData: MetricUpdate = {
      topic_id: form.topic_id,
      name_cn: form.name_cn,
      name_en: form.name_en || undefined,
      metric_type: form.metric_type as MetricType,
      metric_level: form.metric_level || undefined,
      business_caliber: form.business_caliber || undefined,
      technical_caliber: form.technical_caliber || undefined,
      source_tables: form.source_tables?.length ? form.source_tables : undefined,
      dimension_tables: form.dimension_tables?.length ? form.dimension_tables : undefined,
      dimensions: form.dimensions?.length ? form.dimensions : undefined,
      data_source_id: form.data_source_id || undefined
    }
    
    const updatedMetric = await updateMetric(props.metricId, updateData)
    ElMessage.success('保存成功')
    emit('saved', updatedMetric)
    handleClose()
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || '保存失败'
    ElMessage.error(errorMsg)
  } finally {
    saving.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
  activeTab.value = 'business'
  metric.value = null
  factTables.value = []
  dimensionTables.value = []
  // 重置表单
  Object.assign(form, {
    topic_id: 0,
    name_cn: '',
    name_en: '',
    metric_type: 'atomic',
    metric_level: '',
    business_caliber: '',
    technical_caliber: '',
    source_tables: [],
    dimension_tables: [],
    dimensions: [],
    data_source_id: undefined
  })
}
</script>

<style scoped>
.edit-form {
  max-width: 100%;
}

.readonly-value {
  color: #606266;
}

.form-item-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.option-desc {
  float: right;
  color: #909399;
  font-size: 12px;
}

:deep(.el-tabs__content) {
  padding: 16px 0;
}

:deep(.el-form-item) {
  margin-bottom: 18px;
}

:deep(.el-textarea__inner) {
  font-family: inherit;
}

:deep(.el-select-dropdown__item) {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
