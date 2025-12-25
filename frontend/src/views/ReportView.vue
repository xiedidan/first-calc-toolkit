<template>
  <div class="report-view-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>分析报告查看</span>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-form">
        <el-form :inline="true" :model="searchForm">
          <el-form-item label="计算任务">
            <el-select
              v-model="searchForm.task_id"
              placeholder="全部任务"
              clearable
              filterable
              @change="handleSearch"
              style="width: 280px;"
            >
              <el-option
                v-for="task in taskList"
                :key="task.task_id"
                :label="`${task.task_id.substring(0, 8)}... (${task.workflow_name} - ${task.period})`"
                :value="task.task_id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="年月">
            <el-date-picker
              v-model="searchForm.period"
              type="month"
              placeholder="选择月份"
              format="YYYY-MM"
              value-format="YYYY-MM"
              clearable
              @change="handleSearch"
            />
          </el-form-item>
          <el-form-item label="科室代码">
            <el-input
              v-model="searchForm.department_code"
              placeholder="输入科室代码"
              clearable
              @keyup.enter="handleSearch"
              @clear="handleSearch"
            />
          </el-form-item>
          <el-form-item label="科室名称">
            <el-input
              v-model="searchForm.department_name"
              placeholder="输入科室名称"
              clearable
              @keyup.enter="handleSearch"
              @clear="handleSearch"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 报告列表 -->
      <el-table
        :data="reportList"
        v-loading="loading"
        stripe
        border
        @sort-change="handleSortChange"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="period" label="年月" width="120" sortable="custom" />
        <el-table-column prop="department_code" label="科室代码" width="120" sortable="custom" />
        <el-table-column prop="department_name" label="科室名称" min-width="180" sortable="custom" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 报告详情模态框 -->
    <ReportDetailModal
      v-model:visible="detailModalVisible"
      :report="currentReport"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAnalysisReports, getAvailableTasks, type AnalysisReport, type CalculationTaskBrief } from '@/api/analysis-reports'
import ReportDetailModal from '@/components/ReportDetailModal.vue'

// 计算任务列表
const taskList = ref<CalculationTaskBrief[]>([])

// 搜索表单
const searchForm = reactive({
  task_id: '' as string,
  period: '',
  department_code: '',
  department_name: ''
})

// 排序
const sortParams = reactive({
  sort_by: '',
  sort_order: '' as 'asc' | 'desc' | ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 数据
const loading = ref(false)
const reportList = ref<AnalysisReport[]>([])
const currentReport = ref<AnalysisReport | null>(null)
const detailModalVisible = ref(false)

// 加载报告列表
const loadReports = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      size: pagination.size
    }
    
    if (searchForm.period) {
      params.period = searchForm.period
    }
    if (searchForm.department_code) {
      params.department_code = searchForm.department_code
    }
    if (searchForm.department_name) {
      params.department_name = searchForm.department_name
    }
    if (searchForm.task_id) {
      params.task_id = searchForm.task_id
    }
    if (sortParams.sort_by && sortParams.sort_order) {
      params.sort_by = sortParams.sort_by
      params.sort_order = sortParams.sort_order
    }
    
    const res = await getAnalysisReports(params)
    reportList.value = res.items
    pagination.total = res.total
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载报告列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadReports()
}

// 重置搜索
const resetSearch = () => {
  searchForm.task_id = ''
  searchForm.period = ''
  searchForm.department_code = ''
  searchForm.department_name = ''
  pagination.page = 1
  loadReports()
}

// 加载计算任务列表
const loadTasks = async () => {
  try {
    const res = await getAvailableTasks({ status: 'completed' })
    taskList.value = res
  } catch (error) {
    console.error('加载计算任务失败', error)
  }
}

// 排序变化
const handleSortChange = ({ prop, order }: { prop: string; order: string | null }) => {
  if (order) {
    sortParams.sort_by = prop
    sortParams.sort_order = order === 'ascending' ? 'asc' : 'desc'
  } else {
    sortParams.sort_by = ''
    sortParams.sort_order = ''
  }
  pagination.page = 1
  loadReports()
}

// 分页大小变化
const handleSizeChange = () => {
  pagination.page = 1
  loadReports()
}

// 页码变化
const handlePageChange = () => {
  loadReports()
}

// 查看详情
const viewDetail = (row: AnalysisReport) => {
  currentReport.value = row
  detailModalVisible.value = true
}

onMounted(() => {
  loadTasks()
  loadReports()
})
</script>

<style scoped>
.report-view-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
