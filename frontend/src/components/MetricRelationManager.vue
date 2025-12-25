<template>
  <div class="metric-relation-manager">
    <!-- 头部操作栏 -->
    <div class="relation-header">
      <div class="header-title">
        <span>关联指标管理</span>
        <el-tag size="small" type="info" v-if="relationStats">
          共 {{ relationStats.total }} 个关联
        </el-tag>
      </div>
      <el-button type="primary" size="small" @click="handleAddRelation" :disabled="!metricId">
        <el-icon><Plus /></el-icon>
        添加关联
      </el-button>
    </div>

    <!-- 关联统计 -->
    <div class="relation-stats" v-if="relationStats">
      <el-tag type="success" size="small">
        <el-icon><Right /></el-icon>
        引用其他指标: {{ relationStats.as_source_count }}
      </el-tag>
      <el-tag type="warning" size="small">
        <el-icon><Back /></el-icon>
        被其他指标引用: {{ relationStats.as_target_count }}
      </el-tag>
    </div>

    <!-- 关联列表 -->
    <el-table
      :data="relations"
      border
      stripe
      v-loading="loading"
      max-height="400"
      empty-text="暂无关联指标"
    >
      <el-table-column label="关联方向" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.source_metric_id === metricId" type="success" size="small">
            引用
          </el-tag>
          <el-tag v-else type="warning" size="small">
            被引用
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="关联指标" min-width="180">
        <template #default="{ row }">
          <span v-if="row.source_metric_id === metricId">
            {{ row.target_metric_name }}
          </span>
          <span v-else>
            {{ row.source_metric_name }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="relation_type_display" label="关联类型" width="100">
        <template #default="{ row }">
          <el-tag :type="getRelationTypeTag(row.relation_type)" size="small">
            {{ row.relation_type_display }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="170">
        <template #default="{ row }">
          {{ formatDateTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button link type="danger" @click="handleDeleteRelation(row)">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加关联对话框 -->
    <el-dialog
      v-model="addDialogVisible"
      title="添加关联指标"
      width="550px"
      append-to-body
      :close-on-click-modal="false"
    >
      <el-form :model="addForm" label-width="100px" ref="addFormRef" :rules="addFormRules">
        <el-form-item label="当前指标">
          <span class="current-metric-name">{{ currentMetricName }}</span>
        </el-form-item>
        <el-form-item label="关联指标" prop="target_metric_id">
          <el-select
            v-model="addForm.target_metric_id"
            placeholder="请选择要关联的指标"
            filterable
            style="width: 100%"
            :loading="metricsLoading"
          >
            <el-option-group
              v-for="group in groupedMetrics"
              :key="group.project_name"
              :label="group.project_name"
            >
              <el-option
                v-for="metric in group.metrics"
                :key="metric.id"
                :label="metric.name_cn"
                :value="metric.id"
                :disabled="metric.id === metricId || isAlreadyRelated(metric.id)"
              >
                <div class="metric-option">
                  <span>{{ metric.name_cn }}</span>
                  <span class="metric-option-topic">{{ metric.topic_name || '未分类' }}</span>
                </div>
              </el-option>
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item label="关联类型" prop="relation_type">
          <el-select v-model="addForm.relation_type" placeholder="请选择关联类型" style="width: 100%">
            <el-option label="组成关系" value="component">
              <div class="relation-type-option">
                <span>组成关系</span>
                <span class="relation-type-desc">当前指标由目标指标组成</span>
              </div>
            </el-option>
            <el-option label="派生关系" value="derived">
              <div class="relation-type-option">
                <span>派生关系</span>
                <span class="relation-type-desc">当前指标从目标指标派生</span>
              </div>
            </el-option>
            <el-option label="相关关系" value="related">
              <div class="relation-type-option">
                <span>相关关系</span>
                <span class="relation-type-desc">两个指标存在业务关联</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveRelation" :loading="saving">确定</el-button>
      </template>
    </el-dialog>

    <!-- 删除确认对话框（显示受影响指标） -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="确认删除关联"
      width="500px"
      append-to-body
    >
      <div class="delete-confirm-content">
        <el-alert
          type="warning"
          :closable="false"
          show-icon
        >
          <template #title>
            确定要删除与"{{ deleteTargetName }}"的关联关系吗？
          </template>
          <template #default>
            删除关联关系不会影响指标本身，只会移除两个指标之间的关联。
          </template>
        </el-alert>
      </div>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmDeleteRelation" :loading="deleting">确认删除</el-button>
      </template>
    </el-dialog>

    <!-- 受影响指标列表对话框（删除指标前检查） -->
    <el-dialog
      v-model="affectedDialogVisible"
      title="受影响的指标"
      width="600px"
      append-to-body
    >
      <div class="affected-content">
        <el-alert
          v-if="affectedMetrics.length > 0"
          type="warning"
          :closable="false"
          show-icon
          style="margin-bottom: 16px"
        >
          <template #title>
            以下 {{ affectedMetrics.length }} 个指标引用了当前指标
          </template>
          <template #default>
            删除当前指标将会影响这些指标的关联关系。请确认是否继续删除？
          </template>
        </el-alert>
        <el-alert
          v-else
          type="success"
          :closable="false"
          show-icon
          style="margin-bottom: 16px"
        >
          <template #title>
            当前指标没有被其他指标引用
          </template>
          <template #default>
            可以安全删除此指标。
          </template>
        </el-alert>
        
        <el-table
          v-if="affectedMetrics.length > 0"
          :data="affectedMetrics"
          border
          stripe
          max-height="300"
        >
          <el-table-column prop="name_cn" label="指标名称" min-width="150" />
          <el-table-column prop="topic_name" label="所属主题" width="120">
            <template #default="{ row }">
              {{ row.topic_name || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="project_name" label="所属项目" width="120">
            <template #default="{ row }">
              {{ row.project_name || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="关联类型" width="100">
            <template #default="{ row }">
              <el-tag :type="getRelationTypeTag(row.relation_type)" size="small">
                {{ getRelationTypeDisplay(row.relation_type) }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="affectedDialogVisible = false">关闭</el-button>
        <el-button
          v-if="affectedMetrics.length > 0"
          type="danger"
          @click="handleForceDelete"
          :loading="deleting"
        >
          强制删除指标
        </el-button>
        <el-button
          v-else
          type="danger"
          @click="handleConfirmDelete"
          :loading="deleting"
        >
          确认删除
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Delete, Right, Back } from '@element-plus/icons-vue'
import {
  getMetricRelations,
  createMetricRelation,
  deleteMetricRelation,
  getAffectedMetrics,
  getMetrics,
  deleteMetric,
  type MetricRelation,
  type Metric,
  type AffectedMetric,
  type RelationType
} from '@/api/metrics'

// Props
const props = defineProps<{
  metricId: number | null
  metricName?: string
}>()

// Emits
const emit = defineEmits<{
  (e: 'updated'): void
  (e: 'deleted'): void
}>()

// 状态
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const metricsLoading = ref(false)

// 关联数据
const relations = ref<MetricRelation[]>([])
const relationStats = ref<{
  total: number
  as_source_count: number
  as_target_count: number
} | null>(null)

// 所有可选指标
const allMetrics = ref<Metric[]>([])

// 添加关联对话框
const addDialogVisible = ref(false)
const addFormRef = ref<FormInstance>()
const addForm = reactive({
  target_metric_id: null as number | null,
  relation_type: 'related' as RelationType
})
const addFormRules: FormRules = {
  target_metric_id: [
    { required: true, message: '请选择要关联的指标', trigger: 'change' }
  ],
  relation_type: [
    { required: true, message: '请选择关联类型', trigger: 'change' }
  ]
}

// 删除关联对话框
const deleteDialogVisible = ref(false)
const deleteTargetName = ref('')
const deleteTargetId = ref<number | null>(null)

// 受影响指标对话框
const affectedDialogVisible = ref(false)
const affectedMetrics = ref<AffectedMetric[]>([])

// 计算属性
const currentMetricName = computed(() => props.metricName || '当前指标')

// 按项目分组的指标列表
const groupedMetrics = computed(() => {
  const groups: { project_name: string; metrics: Metric[] }[] = []
  const projectMap = new Map<string, Metric[]>()
  
  for (const metric of allMetrics.value) {
    const projectName = metric.project_name || '未分类'
    if (!projectMap.has(projectName)) {
      projectMap.set(projectName, [])
    }
    projectMap.get(projectName)!.push(metric)
  }
  
  for (const [project_name, metrics] of projectMap) {
    groups.push({ project_name, metrics })
  }
  
  return groups.sort((a, b) => a.project_name.localeCompare(b.project_name))
})

// 检查指标是否已关联
const isAlreadyRelated = (targetId: number): boolean => {
  return relations.value.some(r => 
    r.source_metric_id === targetId || r.target_metric_id === targetId
  )
}

// 获取关联类型标签样式
const getRelationTypeTag = (type: string): string => {
  switch (type) {
    case 'component': return 'primary'
    case 'derived': return 'success'
    case 'related': return 'info'
    default: return 'info'
  }
}

// 获取关联类型显示名称
const getRelationTypeDisplay = (type: string): string => {
  switch (type) {
    case 'component': return '组成关系'
    case 'derived': return '派生关系'
    case 'related': return '相关关系'
    default: return type
  }
}

// 格式化日期时间
const formatDateTime = (dateStr: string): string => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 加载关联列表
const loadRelations = async () => {
  if (!props.metricId) {
    relations.value = []
    relationStats.value = null
    return
  }
  
  loading.value = true
  try {
    const res = await getMetricRelations(props.metricId)
    relations.value = res.items
    relationStats.value = {
      total: res.total,
      as_source_count: res.as_source_count,
      as_target_count: res.as_target_count
    }
  } catch (error) {
    console.error('加载关联列表失败:', error)
    ElMessage.error('加载关联列表失败')
  } finally {
    loading.value = false
  }
}

// 加载所有可选指标
const loadAllMetrics = async () => {
  metricsLoading.value = true
  try {
    const res = await getMetrics({ size: 1000 })
    allMetrics.value = res.items
  } catch (error) {
    console.error('加载指标列表失败:', error)
  } finally {
    metricsLoading.value = false
  }
}

// 添加关联
const handleAddRelation = async () => {
  if (!props.metricId) return
  
  // 加载可选指标
  await loadAllMetrics()
  
  // 重置表单
  addForm.target_metric_id = null
  addForm.relation_type = 'related'
  addDialogVisible.value = true
}

// 保存关联
const handleSaveRelation = async () => {
  if (!props.metricId || !addForm.target_metric_id) {
    ElMessage.warning('请选择要关联的指标')
    return
  }
  
  // 表单验证
  if (addFormRef.value) {
    const valid = await addFormRef.value.validate().catch(() => false)
    if (!valid) return
  }
  
  saving.value = true
  try {
    await createMetricRelation(props.metricId, {
      target_metric_id: addForm.target_metric_id,
      relation_type: addForm.relation_type
    })
    ElMessage.success('添加关联成功')
    addDialogVisible.value = false
    await loadRelations()
    emit('updated')
  } catch (error: any) {
    const msg = error.response?.data?.detail || '添加关联失败'
    ElMessage.error(msg)
  } finally {
    saving.value = false
  }
}

// 删除关联
const handleDeleteRelation = (row: MetricRelation) => {
  // 确定要删除的目标指标
  if (row.source_metric_id === props.metricId) {
    deleteTargetName.value = row.target_metric_name || '未知指标'
    deleteTargetId.value = row.target_metric_id
  } else {
    deleteTargetName.value = row.source_metric_name || '未知指标'
    deleteTargetId.value = row.source_metric_id
  }
  deleteDialogVisible.value = true
}

// 确认删除关联
const confirmDeleteRelation = async () => {
  if (!props.metricId || !deleteTargetId.value) return
  
  deleting.value = true
  try {
    await deleteMetricRelation(props.metricId, deleteTargetId.value)
    ElMessage.success('删除关联成功')
    deleteDialogVisible.value = false
    await loadRelations()
    emit('updated')
  } catch (error: any) {
    const msg = error.response?.data?.detail || '删除关联失败'
    ElMessage.error(msg)
  } finally {
    deleting.value = false
  }
}

// 检查受影响的指标（删除指标前调用）
const checkAffectedMetrics = async (): Promise<boolean> => {
  if (!props.metricId) return false
  
  try {
    const res = await getAffectedMetrics(props.metricId)
    affectedMetrics.value = res.items
    affectedDialogVisible.value = true
    return res.can_delete
  } catch (error) {
    console.error('检查受影响指标失败:', error)
    ElMessage.error('检查受影响指标失败')
    return false
  }
}

// 强制删除指标
const handleForceDelete = async () => {
  if (!props.metricId) return
  
  deleting.value = true
  try {
    await deleteMetric(props.metricId, true)
    ElMessage.success('删除指标成功')
    affectedDialogVisible.value = false
    emit('deleted')
  } catch (error: any) {
    const msg = error.response?.data?.detail || '删除指标失败'
    ElMessage.error(msg)
  } finally {
    deleting.value = false
  }
}

// 确认删除指标（无关联时）
const handleConfirmDelete = async () => {
  if (!props.metricId) return
  
  deleting.value = true
  try {
    await deleteMetric(props.metricId, false)
    ElMessage.success('删除指标成功')
    affectedDialogVisible.value = false
    emit('deleted')
  } catch (error: any) {
    const msg = error.response?.data?.detail || '删除指标失败'
    ElMessage.error(msg)
  } finally {
    deleting.value = false
  }
}

// 暴露方法给父组件
defineExpose({
  loadRelations,
  checkAffectedMetrics
})

// 监听 metricId 变化
watch(() => props.metricId, (newId) => {
  if (newId) {
    loadRelations()
  } else {
    relations.value = []
    relationStats.value = null
  }
}, { immediate: true })
</script>

<style scoped>
.metric-relation-manager {
  width: 100%;
}

.relation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 14px;
}

.relation-stats {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.relation-stats .el-tag {
  display: flex;
  align-items: center;
  gap: 4px;
}

.current-metric-name {
  color: #409eff;
  font-weight: 500;
}

.metric-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.metric-option-topic {
  font-size: 12px;
  color: #909399;
}

.relation-type-option {
  display: flex;
  flex-direction: column;
}

.relation-type-desc {
  font-size: 12px;
  color: #909399;
}

.delete-confirm-content {
  padding: 8px 0;
}

.affected-content {
  padding: 8px 0;
}

:deep(.el-table) {
  margin-top: 0;
}

:deep(.el-dialog__body) {
  padding-top: 16px;
  padding-bottom: 16px;
}
</style>
