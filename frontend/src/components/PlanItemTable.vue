<template>
  <div class="plan-item-table">
    <!-- 筛选和排序工具栏 -->
    <el-form :inline="true" class="filter-form" style="margin-bottom: 15px;">
      <el-form-item label="确信度排序">
        <el-select v-model="filters.sortBy" placeholder="请选择" clearable style="width: 150px;" @change="handleFilterChange">
          <el-option label="升序" value="confidence_asc" />
          <el-option label="降序" value="confidence_desc" />
        </el-select>
      </el-form-item>
      <el-form-item label="确信度范围">
        <el-input-number
          v-model="filters.minConfidence"
          :min="0"
          :max="1"
          :step="0.1"
          :precision="2"
          placeholder="最小值"
          style="width: 120px;"
          @change="handleFilterChange"
        />
        <span style="margin: 0 5px;">-</span>
        <el-input-number
          v-model="filters.maxConfidence"
          :min="0"
          :max="1"
          :step="0.1"
          :precision="2"
          placeholder="最大值"
          style="width: 120px;"
          @change="handleFilterChange"
        />
      </el-form-item>
      <el-form-item label="调整状态">
        <el-select v-model="filters.isAdjusted" placeholder="全部" clearable style="width: 120px;" @change="handleFilterChange">
          <el-option label="已调整" :value="true" />
          <el-option label="未调整" :value="false" />
        </el-select>
      </el-form-item>
      <el-form-item label="处理状态">
        <el-select v-model="filters.processingStatus" placeholder="全部" clearable style="width: 120px;" @change="handleFilterChange">
          <el-option label="待处理" value="pending" />
          <el-option label="处理中" value="processing" />
          <el-option label="已完成" value="completed" />
          <el-option label="失败" value="failed" />
        </el-select>
      </el-form-item>
    </el-form>

    <!-- 项目表格 -->
    <el-table
      :data="items"
      border
      stripe
      v-loading="loading"
      :row-class-name="getRowClassName"
      style="width: 100%;"
    >
      <el-table-column prop="charge_item_code" label="项目编码" width="120" fixed="left" />
      <el-table-column prop="charge_item_name" label="项目名称" min-width="150" />
      <el-table-column prop="charge_item_category" label="项目类别" width="100" />
      
      <el-table-column label="AI建议维度" min-width="200">
        <template #default="{ row }">
          <div v-if="row.ai_suggested_dimension_name">
            <div style="font-weight: 600;">{{ row.ai_suggested_dimension_name }}</div>
            <div style="font-size: 12px; color: #909399;">{{ row.ai_suggested_dimension_path }}</div>
          </div>
          <span v-else style="color: #909399;">-</span>
        </template>
      </el-table-column>
      
      <el-table-column prop="ai_confidence" label="确信度" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.ai_confidence !== null" :type="getConfidenceType(row.ai_confidence)">
            {{ (row.ai_confidence * 100).toFixed(1) }}%
          </el-tag>
          <span v-else style="color: #909399;">-</span>
        </template>
      </el-table-column>
      
      <el-table-column label="用户设置维度" min-width="200">
        <template #default="{ row }">
          <div v-if="row.user_set_dimension_name">
            <div style="font-weight: 600;">{{ row.user_set_dimension_name }}</div>
            <div style="font-size: 12px; color: #909399;">{{ row.user_set_dimension_path }}</div>
          </div>
          <span v-else style="color: #909399;">使用AI建议</span>
        </template>
      </el-table-column>
      
      <el-table-column label="最终维度" min-width="200">
        <template #default="{ row }">
          <div v-if="row.final_dimension_name">
            <div style="font-weight: 600;">{{ row.final_dimension_name }}</div>
            <div style="font-size: 12px; color: #909399;">{{ row.final_dimension_path }}</div>
          </div>
          <span v-else style="color: #909399;">-</span>
        </template>
      </el-table-column>
      
      <el-table-column prop="is_adjusted" label="调整状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_adjusted ? 'warning' : 'info'">
            {{ row.is_adjusted ? '已调整' : '未调整' }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="processing_status" label="处理状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.processing_status)">
            {{ getStatusText(row.processing_status) }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            @click="handleAdjust(row)"
            :disabled="disabled"
          >
            调整维度
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="[20, 50, 100, 200]"
      :total="total"
      layout="total, sizes, prev, pager, next, jumper"
      style="margin-top: 20px; justify-content: flex-end;"
      @size-change="handleSizeChange"
      @current-change="handlePageChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { PlanItem } from '@/api/classification-plans'

// Props
interface Props {
  items: PlanItem[]
  loading: boolean
  total: number
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false
})

// Emits
const emit = defineEmits<{
  filterChange: [filters: any]
  pageChange: [page: number, size: number]
  adjust: [item: PlanItem]
}>()

// 筛选条件
const filters = ref({
  sortBy: '',
  minConfidence: undefined as number | undefined,
  maxConfidence: undefined as number | undefined,
  isAdjusted: undefined as boolean | undefined,
  processingStatus: ''
})

// 分页
const currentPage = ref(1)
const pageSize = ref(50)

// 筛选变化
const handleFilterChange = () => {
  currentPage.value = 1
  emitFilterChange()
}

// 分页变化
const handlePageChange = () => {
  emitFilterChange()
}

const handleSizeChange = () => {
  currentPage.value = 1
  emitFilterChange()
}

// 发送筛选事件
const emitFilterChange = () => {
  const filterParams = {
    sort_by: filters.value.sortBy || undefined,
    min_confidence: filters.value.minConfidence,
    max_confidence: filters.value.maxConfidence,
    is_adjusted: filters.value.isAdjusted,
    processing_status: filters.value.processingStatus || undefined,
    page: currentPage.value,
    size: pageSize.value
  }
  emit('filterChange', filterParams)
}

// 调整维度
const handleAdjust = (item: PlanItem) => {
  emit('adjust', item)
}

// 获取行类名(高亮已调整项目)
const getRowClassName = ({ row }: { row: PlanItem }) => {
  return row.is_adjusted ? 'adjusted-row' : ''
}

// 获取确信度标签类型
const getConfidenceType = (confidence: number) => {
  if (confidence >= 0.8) return 'success'
  if (confidence >= 0.5) return 'warning'
  return 'danger'
}

// 获取状态标签类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return textMap[status] || status
}

// 监听total变化,重置页码
watch(() => props.total, () => {
  if (currentPage.value > 1 && props.items.length === 0) {
    currentPage.value = 1
    emitFilterChange()
  }
})
</script>

<style scoped>
.plan-item-table {
  width: 100%;
}

.filter-form {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}

:deep(.adjusted-row) {
  background-color: #fff7e6 !important;
}

:deep(.adjusted-row:hover > td) {
  background-color: #ffe7ba !important;
}
</style>
