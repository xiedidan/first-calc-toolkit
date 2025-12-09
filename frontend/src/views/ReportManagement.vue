<template>
  <div class="report-management-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>分析报告管理</span>
          <el-button type="primary" @click="openCreateModal">
            新建分析报告
          </el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-form">
        <el-form :inline="true" :model="searchForm">
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
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="editReport(row)">
              编辑详情
            </el-button>
            <el-button link type="danger" @click="confirmDelete(row)">
              删除
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

    <!-- 报告编辑模态框 -->
    <ReportEditModal
      v-model:visible="editModalVisible"
      :report="currentReport"
      @saved="handleSaved"
    />

    <!-- 新建报告对话框 -->
    <ReportCreateModal
      v-model:visible="createModalVisible"
      @created="handleCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAnalysisReports, deleteAnalysisReport, type AnalysisReport } from '@/api/analysis-reports'
import ReportEditModal from '@/components/ReportEditModal.vue'
import ReportCreateModal from '@/components/ReportCreateModal.vue'

// 搜索表单
const searchForm = reactive({
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
const editModalVisible = ref(false)
const createModalVisible = ref(false)

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
  searchForm.period = ''
  searchForm.department_code = ''
  searchForm.department_name = ''
  pagination.page = 1
  loadReports()
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

// 编辑报告
const editReport = (row: AnalysisReport) => {
  currentReport.value = row
  editModalVisible.value = true
}

// 确认删除
const confirmDelete = async (row: AnalysisReport) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${row.department_name} - ${row.period} 的分析报告吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteAnalysisReport(row.id)
    ElMessage.success('删除成功')
    loadReports()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 保存成功回调
const handleSaved = () => {
  loadReports()
}

// 打开新建对话框
const openCreateModal = () => {
  createModalVisible.value = true
}

// 创建成功回调
const handleCreated = () => {
  loadReports()
}

onMounted(() => {
  loadReports()
})
</script>

<style scoped>
.report-management-container {
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
