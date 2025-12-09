<template>
  <div class="charge-items-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>收费项目管理</span>
          <div>
            <el-button @click="showImport = true">
              <el-icon><Upload /></el-icon>
              批量导入
            </el-button>
            <el-button type="danger" plain @click="handleClearAll">
              清空全部
            </el-button>
            <el-button type="primary" @click="handleAdd">新建项目</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="项目编码/名称/分类"
            clearable
            @clear="handleSearch"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select
            v-model="searchForm.item_category"
            placeholder="全部"
            clearable
            @clear="handleSearch"
            style="width: 140px"
          >
            <el-option
              v-for="cat in categories"
              :key="cat"
              :label="cat"
              :value="cat"
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
        @sort-change="handleSortChange"
      >
        <el-table-column prop="item_code" label="项目编码" width="150" sortable="custom" />
        <el-table-column prop="item_name" label="项目名称" min-width="250" sortable="custom" />
        <el-table-column prop="item_category" label="项目分类" width="150" sortable="custom" />
        <el-table-column prop="unit_price" label="单价" width="120" sortable="custom" />
        <el-table-column prop="created_at" label="创建时间" width="180" sortable="custom" />
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
        @current-change="fetchChargeItems"
        class="pagination"
      />
    </el-card>

    <!-- Excel导入对话框 -->
    <ExcelImport
      v-model="showImport"
      :import-config="importConfig"
      @success="handleImportSuccess"
    />

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      append-to-body
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="项目编码" prop="item_code">
          <el-input
            v-model="form.item_code"
            :disabled="isEdit"
            placeholder="请输入项目编码"
          />
        </el-form-item>
        <el-form-item label="项目名称" prop="item_name">
          <el-input v-model="form.item_name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目分类">
          <el-input v-model="form.item_category" placeholder="请输入项目分类" />
        </el-form-item>
        <el-form-item label="单价">
          <el-input v-model="form.unit_price" placeholder="请输入单价" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import request from '@/utils/request'
import ExcelImport from '@/components/ExcelImport.vue'

interface ChargeItem {
  id: number
  item_code: string
  item_name: string
  item_category?: string
  unit_price?: string
  created_at: string
  updated_at: string
}

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const dialogTitle = ref('新建收费项目')
const formRef = ref<FormInstance>()
const categories = ref<string[]>([])
const showImport = ref(false)

// 导入配置
const importConfig = {
  fields: [
    { value: 'item_code', label: '项目编码', required: true },
    { value: 'item_name', label: '项目名称', required: true },
    { value: 'item_category', label: '项目分类', required: false },
    { value: 'unit_price', label: '单价', required: false }
  ],
  parseUrl: '/charge-items/parse',
  importUrl: '/charge-items/import',
  templateUrl: '/charge-items/template'
}

const searchForm = reactive({
  keyword: '',
  item_category: '',
  sort_by: 'item_code',
  sort_order: 'asc'
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const tableData = ref<ChargeItem[]>([])

const form = reactive({
  id: 0,
  item_code: '',
  item_name: '',
  item_category: '',
  unit_price: ''
})

const rules = {
  item_code: [{ required: true, message: '请输入项目编码', trigger: 'blur' }],
  item_name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }]
}

// 获取收费项目列表
const fetchChargeItems = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      size: pagination.size,
      sort_by: searchForm.sort_by,
      sort_order: searchForm.sort_order
    }
    if (searchForm.keyword) {
      params.keyword = searchForm.keyword
    }
    if (searchForm.item_category) {
      params.item_category = searchForm.item_category
    }

    const res = await request.get('/charge-items', { params })
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('获取收费项目列表失败')
  } finally {
    loading.value = false
  }
}

// 获取分类列表
const fetchCategories = async () => {
  try {
    const res = await request.get('/charge-items/categories/list')
    categories.value = res
  } catch (error) {
    console.error('获取分类列表失败', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchChargeItems()
}

// 重置
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.item_category = ''
  searchForm.sort_by = 'item_code'
  searchForm.sort_order = 'asc'
  handleSearch()
}

// 处理每页数量变化
const handleSizeChange = () => {
  pagination.page = 1 // 改变每页数量时重置到第一页
  fetchChargeItems()
}

// 处理排序变化
const handleSortChange = ({ prop, order }: any) => {
  if (prop && order) {
    searchForm.sort_by = prop
    searchForm.sort_order = order === 'ascending' ? 'asc' : 'desc'
  } else {
    searchForm.sort_by = 'item_code'
    searchForm.sort_order = 'asc'
  }
  // 排序时不重置页码，直接刷新当前页
  fetchChargeItems()
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新建收费项目'
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: ChargeItem) => {
  isEdit.value = true
  dialogTitle.value = '编辑收费项目'
  Object.assign(form, row)
  dialogVisible.value = true
}

// 删除
const handleDelete = async (row: ChargeItem) => {
  try {
    await ElMessageBox.confirm('确定要删除该收费项目吗？', '提示', {
      type: 'warning'
    })
    await request.delete(`/charge-items/${row.id}`)
    ElMessage.success('删除成功')
    fetchChargeItems()
    fetchCategories() // 刷新分类列表
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (isEdit.value) {
        const { item_code, id, created_at, updated_at, ...updateData } = form
        await request.put(`/charge-items/${form.id}`, updateData)
        ElMessage.success('更新成功')
      } else {
        await request.post('/charge-items', form)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchChargeItems()
      fetchCategories() // 刷新分类列表
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || (isEdit.value ? '更新失败' : '创建失败'))
    } finally {
      submitting.value = false
    }
  })
}

// 关闭对话框
const handleDialogClose = () => {
  formRef.value?.resetFields()
  Object.assign(form, {
    id: 0,
    item_code: '',
    item_name: '',
    item_category: '',
    unit_price: ''
  })
}

// 导入成功回调
const handleImportSuccess = () => {
  fetchChargeItems()
  fetchCategories()
}

// 清空全部
const handleClearAll = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有收费项目吗？此操作不可恢复！',
      '危险操作',
      {
        type: 'error',
        confirmButtonText: '确定清空',
        cancelButtonText: '取消'
      }
    )
    
    const res = await request.delete('/charge-items/clear-all')
    ElMessage.success(res.message || '清空成功')
    fetchChargeItems()
    fetchCategories()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '清空失败')
    }
  }
}

onMounted(() => {
  fetchChargeItems()
  fetchCategories()
})
</script>

<style scoped>
.charge-items-container {
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
