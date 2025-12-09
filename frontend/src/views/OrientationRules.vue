<template>
  <div class="orientation-rules-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>导向规则管理</span>
          <el-button type="primary" @click="handleAdd">新增导向规则</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="导向名称">
          <el-input
            v-model="searchForm.name"
            placeholder="请输入导向名称"
            clearable
            @clear="handleSearch"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="导向类别">
          <el-select
            v-model="searchForm.category"
            placeholder="全部"
            clearable
            @clear="handleSearch"
            style="width: 160px"
          >
            <el-option label="基准阶梯" value="benchmark_ladder" />
            <el-option label="直接阶梯" value="direct_ladder" />
            <el-option label="其他" value="other" />
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
        <el-table-column prop="name" label="导向名称" width="200" />
        <el-table-column label="导向类别" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)">
              {{ getCategoryLabel(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="导向规则描述" min-width="300" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="400" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="success" @click="handleCopy(row)">复制</el-button>
            <el-dropdown @command="(cmd) => handleExport(row, cmd)" style="display: inline-block; vertical-align: middle; margin: 0 5px;">
              <span style="display: inline-block;">
                <el-button link type="info" style="vertical-align: middle;">
                  导出<el-icon style="vertical-align: middle;"><arrow-down /></el-icon>
                </el-button>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="markdown">导出为Markdown</el-dropdown-item>
                  <el-dropdown-item command="pdf">导出为PDF</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button 
              v-if="row.category === 'benchmark_ladder'"
              link 
              type="warning" 
              @click="handleSetBenchmarks(row)"
            >
              设置基准
            </el-button>
            <el-button 
              v-if="row.category === 'benchmark_ladder' || row.category === 'direct_ladder'"
              link 
              type="warning" 
              @click="handleSetLadders(row)"
            >
              设置阶梯
            </el-button>
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
        @current-change="fetchOrientationRules"
        class="pagination"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <OrientationRuleDialog
      v-model="dialogVisible"
      :rule="currentRule"
      :is-edit="isEdit"
      @success="handleDialogSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import OrientationRuleDialog from '@/components/OrientationRuleDialog.vue'

interface OrientationRule {
  id: number
  name: string
  category: 'benchmark_ladder' | 'direct_ladder' | 'other'
  description?: string
  created_at: string
  updated_at: string
}

const router = useRouter()
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentRule = ref<OrientationRule | null>(null)

const searchForm = reactive({
  name: '',
  category: ''
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const tableData = ref<OrientationRule[]>([])

// 获取导向规则列表
const fetchOrientationRules = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      size: pagination.size
    }
    if (searchForm.name) {
      params.name = searchForm.name
    }
    if (searchForm.category) {
      params.category = searchForm.category
    }

    const res = await request.get('/orientation-rules', { params })
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('获取导向规则列表失败')
  } finally {
    loading.value = false
  }
}

// 获取类别标签类型
const getCategoryTagType = (category: string) => {
  const typeMap: Record<string, any> = {
    benchmark_ladder: 'success',
    direct_ladder: 'warning',
    other: 'info'
  }
  return typeMap[category] || 'info'
}

// 获取类别标签文本
const getCategoryLabel = (category: string) => {
  const labelMap: Record<string, string> = {
    benchmark_ladder: '基准阶梯',
    direct_ladder: '直接阶梯',
    other: '其他'
  }
  return labelMap[category] || category
}

// 处理每页数量变化
const handleSizeChange = () => {
  pagination.page = 1
  fetchOrientationRules()
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchOrientationRules()
}

// 重置
const handleReset = () => {
  searchForm.name = ''
  searchForm.category = ''
  handleSearch()
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  currentRule.value = null
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: OrientationRule) => {
  isEdit.value = true
  currentRule.value = { ...row }
  dialogVisible.value = true
}

// 复制
const handleCopy = async (row: OrientationRule) => {
  try {
    await ElMessageBox.confirm(
      `确定要复制导向规则"${row.name}"吗？将同时复制关联的基准和阶梯数据。`,
      '提示',
      {
        type: 'info'
      }
    )
    
    const res = await request.post(`/orientation-rules/${row.id}/copy`)
    ElMessage.success(`复制成功，新导向规则ID: ${res.id}`)
    fetchOrientationRules()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '复制失败')
    }
  }
}

// 导出
const handleExport = async (row: OrientationRule, format: 'markdown' | 'pdf' = 'markdown') => {
  try {
    const response = await request.get(`/orientation-rules/${row.id}/export`, {
      params: { format },
      responseType: 'blob'
    })
    
    // 根据格式设置MIME类型和文件扩展名
    const mimeType = format === 'pdf' ? 'application/pdf' : 'text/markdown'
    const extension = format === 'pdf' ? 'pdf' : 'md'
    
    // 从响应头获取文件名
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5)
    let filename = `${row.name}_${timestamp}.${extension}`
    const contentDisposition = response.headers?.['content-disposition']
    if (contentDisposition && contentDisposition.includes("filename*=UTF-8''")) {
      const filenameMatch = contentDisposition.split("filename*=UTF-8''")[1]
      if (filenameMatch) {
        filename = decodeURIComponent(filenameMatch)
      }
    }
    
    // 创建下载链接
    const blob = new Blob([response.data || response], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    ElMessage.success(`导出${format === 'pdf' ? 'PDF' : 'Markdown'}成功`)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '导出失败')
  }
}

// 设置基准
const handleSetBenchmarks = (row: OrientationRule) => {
  router.push({
    path: '/orientation-benchmarks',
    query: { rule_id: row.id }
  })
}

// 设置阶梯
const handleSetLadders = (row: OrientationRule) => {
  router.push({
    path: '/orientation-ladders',
    query: { rule_id: row.id }
  })
}

// 删除
const handleDelete = async (row: OrientationRule) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除导向规则"${row.name}"吗？如果有模型节点关联该规则，将无法删除。`,
      '提示',
      {
        type: 'warning'
      }
    )
    
    await request.delete(`/orientation-rules/${row.id}`)
    ElMessage.success('删除成功')
    fetchOrientationRules()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 对话框成功回调
const handleDialogSuccess = () => {
  fetchOrientationRules()
}

onMounted(() => {
  fetchOrientationRules()
})
</script>

<style scoped>
.orientation-rules-container {
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
