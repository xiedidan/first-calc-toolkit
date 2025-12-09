<template>
  <div class="orientation-benchmarks-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>导向基准管理</span>
          <el-button type="primary" @click="handleAdd">新增导向基准</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="所属导向">
          <el-select
            v-model="searchForm.rule_id"
            placeholder="全部"
            clearable
            filterable
            @change="handleSearch"
            style="width: 250px"
          >
            <el-option
              v-for="rule in benchmarkLadderRules"
              :key="rule.id"
              :label="rule.name"
              :value="rule.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table 
        :data="tableData" 
        border 
        stripe 
        v-loading="loading"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="rule_name" label="所属导向" width="180" />
        <el-table-column prop="department_name" label="科室" width="150">
          <template #default="{ row }">
            {{ row.department_name }} ({{ row.department_code }})
          </template>
        </el-table-column>
        <el-table-column label="基准类别" width="120">
          <template #default="{ row }">
            <el-tag :type="getBenchmarkTypeTagType(row.benchmark_type)">
              {{ getBenchmarkTypeLabel(row.benchmark_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="control_intensity" label="管控力度" width="120" align="right" />
        <el-table-column label="统计时间" width="220">
          <template #default="{ row }">
            {{ formatDateRange(row.stat_start_date, row.stat_end_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="benchmark_value" label="基准值" width="120" align="right" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="fetchBenchmarks"
        class="pagination"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <OrientationBenchmarkDialog
      v-model="dialogVisible"
      :benchmark="currentBenchmark"
      :is-edit="isEdit"
      @success="handleDialogSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute } from 'vue-router'
import request from '@/utils/request'
import OrientationBenchmarkDialog from '@/components/OrientationBenchmarkDialog.vue'

interface OrientationBenchmark {
  id: number
  rule_id: number
  rule_name: string
  department_code: string
  department_name: string
  benchmark_type: 'average' | 'median' | 'max' | 'min' | 'other'
  control_intensity: string
  stat_start_date: string
  stat_end_date: string
  benchmark_value: string
  created_at: string
  updated_at: string
}

interface OrientationRule {
  id: number
  name: string
  category: string
}

const route = useRoute()
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentBenchmark = ref<OrientationBenchmark | null>(null)

const searchForm = reactive({
  rule_id: null as number | null
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const tableData = ref<OrientationBenchmark[]>([])
const benchmarkLadderRules = ref<OrientationRule[]>([])

// 获取基准阶梯类别的导向规则列表
const fetchBenchmarkLadderRules = async () => {
  try {
    const res = await request.get('/orientation-rules', {
      params: {
        category: 'benchmark_ladder',
        page: 1,
        size: 1000 // 获取所有基准阶梯类别的导向
      }
    })
    benchmarkLadderRules.value = res.items
  } catch (error) {
    ElMessage.error('获取导向规则列表失败')
  }
}

// 获取导向基准列表
const fetchBenchmarks = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      size: pagination.size
    }
    if (searchForm.rule_id) {
      params.rule_id = searchForm.rule_id
    }

    const res = await request.get('/orientation-benchmarks', { params })
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('获取导向基准列表失败')
  } finally {
    loading.value = false
  }
}

// 获取基准类别标签类型
const getBenchmarkTypeTagType = (type: string) => {
  const typeMap: Record<string, any> = {
    average: 'success',
    median: 'primary',
    max: 'danger',
    min: 'warning',
    other: 'info'
  }
  return typeMap[type] || 'info'
}

// 获取基准类别标签文本
const getBenchmarkTypeLabel = (type: string) => {
  const labelMap: Record<string, string> = {
    average: '平均值',
    median: '中位数',
    max: '最大值',
    min: '最小值',
    other: '其他'
  }
  return labelMap[type] || type
}

// 格式化日期范围
const formatDateRange = (startDate: string, endDate: string) => {
  const start = startDate ? startDate.substring(0, 10) : ''
  const end = endDate ? endDate.substring(0, 10) : ''
  return `${start} ~ ${end}`
}

// 处理每页数量变化
const handleSizeChange = () => {
  pagination.page = 1
  fetchBenchmarks()
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchBenchmarks()
}

// 重置
const handleReset = () => {
  searchForm.rule_id = null
  handleSearch()
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  currentBenchmark.value = null
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: OrientationBenchmark) => {
  isEdit.value = true
  currentBenchmark.value = { ...row }
  dialogVisible.value = true
}

// 删除
const handleDelete = async (row: OrientationBenchmark) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除该导向基准吗？`,
      '提示',
      {
        type: 'warning'
      }
    )
    
    await request.delete(`/orientation-benchmarks/${row.id}`)
    ElMessage.success('删除成功')
    fetchBenchmarks()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 对话框成功回调
const handleDialogSuccess = () => {
  fetchBenchmarks()
}

// 初始化
onMounted(async () => {
  // 先获取导向规则列表
  await fetchBenchmarkLadderRules()
  
  // 从 URL 参数读取 rule_id
  const ruleIdParam = route.query.rule_id
  if (ruleIdParam) {
    searchForm.rule_id = Number(ruleIdParam)
  }
  
  // 获取基准列表
  fetchBenchmarks()
})
</script>

<style scoped>
.orientation-benchmarks-container {
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

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
