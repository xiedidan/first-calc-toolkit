<template>
  <div class="classification-plans-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>分类预案管理</span>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" class="search-form" style="margin-bottom: 20px;">
        <el-form-item label="预案状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 150px;" @change="handleSearch">
            <el-option label="草稿" value="draft" />
            <el-option label="已提交" value="submitted" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 预案列表 -->
      <el-table
        :data="plans"
        border
        stripe
        v-loading="loading"
        style="width: 100%;"
      >
        <el-table-column prop="id" label="预案ID" width="80" />
        <el-table-column prop="plan_name" label="预案名称" min-width="150">
          <template #default="{ row }">
            {{ row.plan_name || '未命名预案' }}
          </template>
        </el-table-column>
        <el-table-column prop="task_name" label="关联任务" min-width="150">
          <template #default="{ row }">
            {{ row.task_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="charge_categories" label="收费类别" min-width="150">
          <template #default="{ row }">
            {{ formatChargeCategories(row.charge_categories) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'submitted' ? 'success' : 'info'">
              {{ row.status === 'submitted' ? '已提交' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="统计信息" width="200">
          <template #default="{ row }">
            <div>总数: {{ row.total_items }}</div>
            <div>已调整: {{ row.adjusted_items }}</div>
            <div>低确信度: {{ row.low_confidence_items }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleViewPlan(row)">
              查看详情
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row)"
              :disabled="row.status === 'submitted'"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end;"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getClassificationPlans, deleteClassificationPlan, type ClassificationPlan } from '@/api/classification-plans'

const router = useRouter()

// 数据
const plans = ref<ClassificationPlan[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 搜索表单
const searchForm = ref({
  status: ''
})

// 加载预案列表
const loadPlans = async () => {
  loading.value = true
  try {
    const res = await getClassificationPlans({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      status: searchForm.value.status || undefined
    })
    plans.value = res.items
    total.value = res.total
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载预案列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadPlans()
}

// 重置
const handleReset = () => {
  searchForm.value.status = ''
  currentPage.value = 1
  loadPlans()
}

// 分页处理
const handlePageChange = () => {
  loadPlans()
}

const handleSizeChange = () => {
  currentPage.value = 1
  loadPlans()
}

// 查看预案
const handleViewPlan = (plan: ClassificationPlan) => {
  router.push({
    name: 'ClassificationPlanDetail',
    params: { id: plan.id }
  })
}

// 删除预案
const handleDelete = async (plan: ClassificationPlan) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除预案"${plan.plan_name || '未命名预案'}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteClassificationPlan(plan.id)
    ElMessage.success('删除成功')
    loadPlans()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
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

// 初始化
onMounted(() => {
  loadPlans()
})
</script>

<style scoped>
.classification-plans-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.search-form {
  margin-bottom: 20px;
}
</style>
