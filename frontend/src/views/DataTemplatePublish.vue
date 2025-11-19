<template>
  <div class="data-template-publish-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据模板发布</span>
          <div class="header-buttons">
            <el-button type="primary" @click="handleExport" :disabled="selectedIds.length === 0">
              <el-icon><Download /></el-icon>
              导出数据模板 ({{ selectedIds.length }})
            </el-button>
          </div>
        </div>
      </template>

      <!-- 搜索和筛选栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索表名、中文名、说明"
          style="width: 300px"
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </div>
      
      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-checkbox v-model="filterCore" @change="handleSearch">仅显示核心表</el-checkbox>
        <el-checkbox v-model="filterHasDefinition" @change="handleSearch">仅显示已上传文档</el-checkbox>
        <el-checkbox v-model="filterHasSql" @change="handleSearch">仅显示已上传SQL</el-checkbox>
        <div style="margin-left: auto; display: flex; gap: 10px; align-items: center;">
          <el-button size="small" @click="handleSelectAll">全选所有</el-button>
          <el-button size="small" @click="handleClearSelection">清空选择</el-button>
          <span style="color: #909399;">已选择 {{ selectedIds.length }} / {{ total }} 项</span>
        </div>
      </div>

      <!-- 数据表格 -->
      <el-table
        ref="tableRef"
        :data="tableData"
        v-loading="loading"
        border
        stripe
        style="width: 100%"
        @select="handleSelect"
        @select-all="handleSelectAllInPage"
        :row-key="(row) => row.id"
      >
        <el-table-column type="selection" width="55" :reserve-selection="true" :selectable="() => true" />
        <el-table-column prop="sort_order" label="序号" width="80" align="center" />
        <el-table-column prop="table_name" label="表名" width="200" />
        <el-table-column prop="table_name_cn" label="中文名" width="200" />
        <el-table-column label="核心" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_core" type="danger" size="small">核心</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="文档状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.has_definition" type="success" size="small">已上传</el-tag>
            <el-tag v-else type="info" size="small">未上传</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="SQL状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.has_sql" type="success" size="small">已上传</el-tag>
            <el-tag v-else type="info" size="small">未上传</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleViewDetail(row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <DataTemplateDetailDialog
      v-model="detailDialogVisible"
      :template-id="currentTemplateId"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Download } from '@element-plus/icons-vue'
import {
  getDataTemplates,
  type DataTemplate
} from '@/api/data-templates'
import request from '@/utils/request'
import DataTemplateDetailDialog from '@/components/DataTemplateDetailDialog.vue'

// 数据
const loading = ref(false)
const tableData = ref<DataTemplate[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchKeyword = ref('')
const filterCore = ref(false)
const filterHasDefinition = ref(false)
const filterHasSql = ref(false)
const selectedIds = ref<number[]>([])
const tableRef = ref()

// 详情对话框
const detailDialogVisible = ref(false)
const currentTemplateId = ref<number | null>(null)

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      size: pageSize.value
    }
    
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    if (filterCore.value) {
      params.is_core = true
    }
    if (filterHasDefinition.value) {
      params.has_definition = true
    }
    if (filterHasSql.value) {
      params.has_sql = true
    }
    
    const res = await getDataTemplates(params)
    tableData.value = res.items
    total.value = res.total
    
    // 恢复当前页的选中状态
    await nextTick()
    restoreSelection()
  } catch (error: any) {
    ElMessage.error(error.message || '加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

// 处理每页数量变化
const handleSizeChange = () => {
  currentPage.value = 1
  loadData()
}

// 处理页码变化
const handlePageChange = () => {
  loadData()
}

// 单行选择/取消选择
const handleSelect = (selection: DataTemplate[], row: DataTemplate) => {
  const index = selectedIds.value.indexOf(row.id)
  if (index > -1) {
    // 取消选择
    selectedIds.value.splice(index, 1)
  } else {
    // 选择
    selectedIds.value.push(row.id)
  }
}

// 当前页全选/取消全选
const handleSelectAllInPage = (selection: DataTemplate[]) => {
  const currentPageIds = tableData.value.map(item => item.id)
  
  if (selection.length === 0) {
    // 取消当前页的所有选择
    selectedIds.value = selectedIds.value.filter(id => !currentPageIds.includes(id))
  } else {
    // 选择当前页的所有项
    const otherPageIds = selectedIds.value.filter(id => !currentPageIds.includes(id))
    const currentPageSelectedIds = selection.map(item => item.id)
    selectedIds.value = [...otherPageIds, ...currentPageSelectedIds]
  }
}

// 恢复当前页的选中状态
const restoreSelection = () => {
  if (!tableRef.value) return
  
  tableData.value.forEach(row => {
    if (selectedIds.value.includes(row.id)) {
      tableRef.value.toggleRowSelection(row, true)
    }
  })
}

// 全选所有
const handleSelectAll = async () => {
  try {
    loading.value = true
    // 获取所有数据的 ID（不分页）
    const params: any = {
      page: 1,
      size: 1000 // 获取所有数据（后端限制最大1000）
    }
    
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    if (filterCore.value) {
      params.is_core = true
    }
    if (filterHasDefinition.value) {
      params.has_definition = true
    }
    if (filterHasSql.value) {
      params.has_sql = true
    }
    
    const res = await getDataTemplates(params)
    selectedIds.value = res.items.map(item => item.id)
    
    // 恢复当前页的选中状态
    await nextTick()
    restoreSelection()
    
    ElMessage.success(`已选择全部 ${selectedIds.value.length} 项`)
  } catch (error: any) {
    ElMessage.error(error.message || '全选失败')
  } finally {
    loading.value = false
  }
}

// 清空选择
const handleClearSelection = () => {
  selectedIds.value = []
  if (tableRef.value) {
    tableRef.value.clearSelection()
  }
}

// 查看详情
const handleViewDetail = (row: DataTemplate) => {
  currentTemplateId.value = row.id
  detailDialogVisible.value = true
}

// 导出数据模板
const handleExport = async () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请选择要导出的数据模板')
    return
  }

  try {
    loading.value = true
    const response = await request({
      url: '/data-templates/export',
      method: 'post',
      data: { template_ids: selectedIds.value },
      responseType: 'blob'
    })

    // 创建下载链接
    const blob = new Blob([response], { type: 'text/markdown' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `数据模板_${new Date().toISOString().split('T')[0]}.md`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success('导出成功')
  } catch (error: any) {
    ElMessage.error(error.message || '导出失败')
  } finally {
    loading.value = false
  }
}

// 初始化
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.data-template-publish-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-buttons {
  display: flex;
  gap: 10px;
}

.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.filter-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 20px;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
