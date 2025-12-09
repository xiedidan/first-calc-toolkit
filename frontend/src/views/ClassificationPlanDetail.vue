<template>
  <div class="plan-detail-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <div>
            <span style="font-weight: 600;">预案详情</span>
            <el-tag
              v-if="plan"
              :type="plan.status === 'submitted' ? 'success' : 'info'"
              style="margin-left: 10px;"
            >
              {{ plan.status === 'submitted' ? '已提交' : '草稿' }}
            </el-tag>
          </div>
          <div>
            <el-button @click="handleBack">返回</el-button>
            <el-button
              v-if="plan"
              type="primary"
              @click="handleSaveName"
            >
              保存预案名称
            </el-button>
            <el-button
              v-if="plan && plan.status === 'draft'"
              type="success"
              @click="handleSubmit"
            >
              提交预案
            </el-button>
          </div>
        </div>
      </template>

      <!-- 预案基本信息 -->
      <div v-if="plan" style="margin-bottom: 20px;">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="预案名称">
            <el-input
              v-model="planName"
              placeholder="请输入预案名称"
              style="width: 300px;"
              maxlength="100"
              show-word-limit
            />
          </el-descriptions-item>
          <el-descriptions-item label="关联任务">
            {{ plan.task_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="模型版本ID">
            {{ plan.model_version_id || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="收费类别">
            {{ formatChargeCategories(plan.charge_categories) }}
          </el-descriptions-item>
          <el-descriptions-item label="总项目数">
            {{ plan.total_items }}
          </el-descriptions-item>
          <el-descriptions-item label="已调整项目">
            {{ plan.adjusted_items }}
          </el-descriptions-item>
          <el-descriptions-item label="低确信度项目">
            {{ plan.low_confidence_items }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(plan.created_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 预案项目表格 -->
      <PlanItemTable
        :items="items"
        :loading="itemsLoading"
        :total="itemsTotal"
        :disabled="plan?.status === 'submitted'"
        @filter-change="handleFilterChange"
        @adjust="handleAdjustDimension"
      />
    </el-card>

    <!-- 维度选择对话框 -->
    <el-dialog
      v-model="dimensionDialogVisible"
      title="选择维度"
      width="600px"
      append-to-body
    >
      <el-form label-width="100px">
        <el-form-item label="当前项目">
          <span style="font-weight: 600;">{{ currentItem?.charge_item_name }}</span>
        </el-form-item>
        <el-form-item label="AI建议">
          <div v-if="currentItem?.ai_suggested_dimension_name">
            <div>{{ currentItem.ai_suggested_dimension_name }}</div>
            <div style="font-size: 12px; color: #909399;">
              {{ currentItem.ai_suggested_dimension_path }}
            </div>
            <div style="margin-top: 5px;">
              <el-tag :type="getConfidenceType(currentItem.ai_confidence)">
                确信度: {{ (currentItem.ai_confidence * 100).toFixed(1) }}%
              </el-tag>
            </div>
          </div>
          <span v-else style="color: #909399;">无AI建议</span>
        </el-form-item>
        <el-form-item label="选择维度">
          <el-select
            v-model="selectedDimensionId"
            placeholder="请选择维度"
            filterable
            clearable
            style="width: 100%;"
            @focus="loadDimensions"
          >
            <el-option
              :key="0"
              label="不设维度（提交时跳过该项目）"
              :value="null"
            >
              <div style="color: #909399;">
                <span>不设维度（提交时跳过该项目）</span>
              </div>
            </el-option>
            <el-option
              v-for="dim in dimensions"
              :key="dim.id"
              :label="dim.full_path"
              :value="dim.id"
            >
              <div>
                <div style="font-weight: 600;">{{ dim.name }}</div>
                <div style="font-size: 12px; color: #909399;">
                  {{ dim.full_path }}
                </div>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dimensionDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            @click="handleConfirmDimension"
            :loading="adjusting"
          >
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 提交预览对话框 -->
    <SubmitPreviewDialog
      v-model="submitDialogVisible"
      :plan-id="planId"
      @success="handleSubmitSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  getClassificationPlanDetail,
  getPlanItems,
  updateClassificationPlan,
  updatePlanItem,
  type ClassificationPlan,
  type PlanItem
} from '@/api/classification-plans'
import { getLeafNodes, type LeafNode } from '@/api/model'
import PlanItemTable from '@/components/PlanItemTable.vue'
import SubmitPreviewDialog from '@/components/SubmitPreviewDialog.vue'

const route = useRoute()
const router = useRouter()

// 数据
const planId = computed(() => Number(route.params.id))
const plan = ref<ClassificationPlan | null>(null)
const planName = ref('')
const loading = ref(false)

// 项目列表
const items = ref<PlanItem[]>([])
const itemsLoading = ref(false)
const itemsTotal = ref(0)
const currentFilters = ref<any>({})

// 维度选择
const dimensionDialogVisible = ref(false)
const currentItem = ref<PlanItem | null>(null)
const dimensions = ref<LeafNode[]>([])
const selectedDimensionId = ref<number | null>(null)
const adjusting = ref(false)

// 提交对话框
const submitDialogVisible = ref(false)

// 加载预案详情
const loadPlanDetail = async () => {
  loading.value = true
  try {
    plan.value = await getClassificationPlanDetail(planId.value)
    planName.value = plan.value.plan_name || ''
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载预案详情失败')
    handleBack()
  } finally {
    loading.value = false
  }
}

// 加载预案项目
const loadPlanItems = async (filters: any = {}) => {
  itemsLoading.value = true
  currentFilters.value = filters
  try {
    const res = await getPlanItems(planId.value, filters)
    items.value = res.items
    itemsTotal.value = res.total
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载预案项目失败')
  } finally {
    itemsLoading.value = false
  }
}

// 筛选变化
const handleFilterChange = (filters: any) => {
  loadPlanItems(filters)
}

// 保存预案名称
const handleSaveName = async () => {
  if (!planName.value.trim()) {
    ElMessage.warning('请输入预案名称')
    return
  }

  try {
    await updateClassificationPlan(planId.value, { plan_name: planName.value })
    ElMessage.success('保存成功')
    loadPlanDetail()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  }
}

// 调整维度
const handleAdjustDimension = (item: PlanItem) => {
  currentItem.value = item
  selectedDimensionId.value = item.user_set_dimension_id || item.ai_suggested_dimension_id
  dimensionDialogVisible.value = true
}

// 加载维度列表
const loadDimensions = async () => {
  if (dimensions.value.length > 0 || !plan.value?.model_version_id) return

  try {
    const res: any = await getLeafNodes(plan.value.model_version_id)
    dimensions.value = res || []
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载维度列表失败')
  }
}

// 确认调整维度
const handleConfirmDimension = async () => {
  if (!currentItem.value) return

  adjusting.value = true
  try {
    await updatePlanItem(planId.value, currentItem.value.id, {
      dimension_id: selectedDimensionId.value
    })
    ElMessage.success('调整成功')
    dimensionDialogVisible.value = false
    // 重新加载当前页数据
    loadPlanItems(currentFilters.value)
    loadPlanDetail() // 更新统计信息
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '调整失败')
  } finally {
    adjusting.value = false
  }
}

// 提交预案
const handleSubmit = () => {
  submitDialogVisible.value = true
}

// 提交成功
const handleSubmitSuccess = () => {
  ElMessage.success('提交成功')
  loadPlanDetail()
  loadPlanItems(currentFilters.value)
}

// 返回
const handleBack = () => {
  router.push({ name: 'ClassificationPlans' })
}

// 格式化收费类别
const formatChargeCategories = (categories: string[] | null) => {
  if (!categories || categories.length === 0) {
    return '-'
  }
  return categories.join(', ')
}

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
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

// 获取确信度标签类型
const getConfidenceType = (confidence: number | null) => {
  if (confidence === null) return 'info'
  if (confidence >= 0.8) return 'success'
  if (confidence >= 0.5) return 'warning'
  return 'danger'
}

// 初始化
onMounted(() => {
  loadPlanDetail()
  loadPlanItems()
})
</script>

<style scoped>
.plan-detail-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
