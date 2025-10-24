<template>
  <div class="dimension-items-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>维度目录管理</span>
          <el-button type="primary" @click="handleAdd">添加收费项目</el-button>
        </div>
      </template>

      <!-- 维度选择（临时，后续会从模型管理传入） -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="维度ID">
          <el-input-number
            v-model="dimensionId"
            :min="1"
            placeholder="请输入维度ID"
            @change="handleSearch"
          />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="项目编码/名称"
            clearable
            @clear="handleSearch"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="item_code" label="收费项目编码" width="150" />
        <el-table-column prop="item_name" label="收费项目名称" width="250" />
        <el-table-column prop="item_category" label="项目分类" width="150" />
        <el-table-column prop="created_at" label="添加时间" width="180" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
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
        @current-change="fetchDimensionItems"
        class="pagination"
      />
    </el-card>

    <!-- 添加收费项目对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="添加收费项目"
      width="600px"
    >
      <el-form>
        <el-form-item label="搜索收费项目">
          <el-input
            v-model="searchKeyword"
            placeholder="输入项目编码或名称搜索"
            @input="handleSearchItems"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearchItems" />
            </template>
          </el-input>
        </el-form-item>
      </el-form>

      <el-table
        :data="searchResults"
        border
        stripe
        v-loading="searchLoading"
        max-height="400"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="item_code" label="项目编码" width="120" />
        <el-table-column prop="item_name" label="项目名称" />
        <el-table-column prop="item_category" label="分类" width="100" />
        <el-table-column prop="unit_price" label="单价" width="100" />
      </el-table>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleSubmit"
          :loading="submitting"
          :disabled="selectedItems.length === 0"
        >
          添加选中项目 ({{ selectedItems.length }})
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import request from '@/utils/request'

interface DimensionItem {
  id: number
  dimension_id: number
  item_code: string
  item_name: string
  item_category: string
  created_at: string
}

interface ChargeItem {
  id: number
  item_code: string
  item_name: string
  item_category: string
  unit_price: string
}

const loading = ref(false)
const submitting = ref(false)
const searchLoading = ref(false)
const dialogVisible = ref(false)
const dimensionId = ref(1) // 临时硬编码，后续从路由参数获取
const searchKeyword = ref('')
const searchResults = ref<ChargeItem[]>([])
const selectedItems = ref<ChargeItem[]>([])

const searchForm = reactive({
  keyword: ''
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const tableData = ref<DimensionItem[]>([])

// 获取维度目录列表
const fetchDimensionItems = async () => {
  if (!dimensionId.value) {
    ElMessage.warning('请先输入维度ID')
    return
  }

  loading.value = true
  try {
    const params: any = {
      dimension_id: dimensionId.value,
      page: pagination.page,
      size: pagination.size
    }
    if (searchForm.keyword) {
      params.keyword = searchForm.keyword
    }

    const res = await request.get('/dimension-items', { params })
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('获取维度目录失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchDimensionItems()
}

// 处理每页数量变化
const handleSizeChange = () => {
  pagination.page = 1 // 改变每页数量时重置到第一页
  fetchDimensionItems()
}

// 打开添加对话框
const handleAdd = () => {
  if (!dimensionId.value) {
    ElMessage.warning('请先输入维度ID')
    return
  }
  searchKeyword.value = ''
  searchResults.value = []
  selectedItems.value = []
  dialogVisible.value = true
}

// 搜索收费项目
const handleSearchItems = async () => {
  if (!searchKeyword.value || searchKeyword.value.length < 2) {
    ElMessage.warning('请输入至少2个字符进行搜索')
    return
  }

  searchLoading.value = true
  try {
    const params = {
      keyword: searchKeyword.value,
      dimension_id: dimensionId.value,
      limit: 50
    }
    const res = await request.get('/dimension-items/charge-items/search', { params })
    searchResults.value = res
    if (res.length === 0) {
      ElMessage.info('未找到匹配的收费项目')
    }
  } catch (error) {
    ElMessage.error('搜索收费项目失败')
  } finally {
    searchLoading.value = false
  }
}

// 处理选择变化
const handleSelectionChange = (selection: ChargeItem[]) => {
  selectedItems.value = selection
}

// 提交添加
const handleSubmit = async () => {
  if (selectedItems.value.length === 0) {
    ElMessage.warning('请选择要添加的收费项目')
    return
  }

  submitting.value = true
  try {
    const item_codes = selectedItems.value.map(item => item.item_code)
    const res = await request.post('/dimension-items', {
      dimension_id: dimensionId.value,
      item_codes
    })
    ElMessage.success(res.message || '添加成功')
    dialogVisible.value = false
    fetchDimensionItems()
  } catch (error) {
    ElMessage.error('添加失败')
  } finally {
    submitting.value = false
  }
}

// 删除
const handleDelete = async (row: DimensionItem) => {
  try {
    await ElMessageBox.confirm('确定要删除该收费项目吗？', '提示', {
      type: 'warning'
    })
    await request.delete(`/dimension-items/${row.id}`)
    ElMessage.success('删除成功')
    fetchDimensionItems()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  if (dimensionId.value) {
    fetchDimensionItems()
  }
})
</script>

<style scoped>
.dimension-items-container {
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
  justify-content: flex-end;
}
</style>
