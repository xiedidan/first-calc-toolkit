<template>
  <div class="departments-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>科室管理</span>
          <el-button type="primary" @click="handleAdd">新增科室</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="科室代码/名称"
            clearable
            @clear="handleSearch"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="searchForm.is_active"
            placeholder="全部"
            clearable
            @clear="handleSearch"
            style="width: 140px"
          >
            <el-option label="参与评估" :value="true" />
            <el-option label="不参与评估" :value="false" />
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
        <el-table-column prop="sort_order" label="序号" width="100" sortable="custom" />
        <el-table-column prop="his_code" label="HIS科室代码" width="150" sortable="custom" />
        <el-table-column prop="his_name" label="HIS科室名称" width="180" sortable="custom" />
        <el-table-column prop="cost_center_code" label="成本中心代码" width="150" sortable="custom" />
        <el-table-column prop="cost_center_name" label="成本中心名称" width="180" sortable="custom" />
        <el-table-column prop="accounting_unit_code" label="核算单元代码" width="150" sortable="custom" />
        <el-table-column prop="accounting_unit_name" label="核算单元名称" width="180" sortable="custom" />
        <el-table-column label="评估状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '参与评估' : '不参与' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" sortable="custom" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button
              link
              :type="row.is_active ? 'warning' : 'success'"
              @click="handleToggle(row)"
            >
              {{ row.is_active ? '停用' : '启用' }}
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
        @current-change="fetchDepartments"
        class="pagination"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="HIS科室代码" prop="his_code">
          <el-input
            v-model="form.his_code"
            :disabled="isEdit"
            placeholder="请输入HIS科室代码"
          />
        </el-form-item>
        <el-form-item label="HIS科室名称" prop="his_name">
          <el-input v-model="form.his_name" placeholder="请输入HIS科室名称" />
        </el-form-item>
        <el-form-item label="排序序号">
          <el-input-number 
            v-model="form.sort_order" 
            :min="0" 
            :precision="2"
            :step="1"
            placeholder="留空自动分配"
          />
        </el-form-item>
        <el-form-item label="成本中心代码">
          <el-input v-model="form.cost_center_code" placeholder="请输入成本中心代码" />
        </el-form-item>
        <el-form-item label="成本中心名称">
          <el-input v-model="form.cost_center_name" placeholder="请输入成本中心名称" />
        </el-form-item>
        <el-form-item label="核算单元代码">
          <el-input v-model="form.accounting_unit_code" placeholder="请输入核算单元代码" />
        </el-form-item>
        <el-form-item label="核算单元名称">
          <el-input v-model="form.accounting_unit_name" placeholder="请输入核算单元名称" />
        </el-form-item>
        <el-form-item label="是否参与评估" v-if="!isEdit">
          <el-switch v-model="form.is_active" />
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
import request from '@/utils/request'

interface Department {
  id: number
  sort_order: number
  his_code: string
  his_name: string
  cost_center_code?: string
  cost_center_name?: string
  accounting_unit_code?: string
  accounting_unit_name?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const dialogTitle = ref('新增科室')
const formRef = ref<FormInstance>()

const searchForm = reactive({
  keyword: '',
  is_active: undefined as boolean | undefined,
  sort_by: 'sort_order',
  sort_order: 'asc'
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const tableData = ref<Department[]>([])

const form = reactive({
  id: 0,
  sort_order: undefined as number | undefined,
  his_code: '',
  his_name: '',
  cost_center_code: '',
  cost_center_name: '',
  accounting_unit_code: '',
  accounting_unit_name: '',
  is_active: true
})

const rules = {
  his_code: [{ required: true, message: '请输入HIS科室代码', trigger: 'blur' }],
  his_name: [{ required: true, message: '请输入HIS科室名称', trigger: 'blur' }]
}

// 获取科室列表
const fetchDepartments = async () => {
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
    if (searchForm.is_active !== undefined) {
      params.is_active = searchForm.is_active
    }

    const res = await request.get('/departments', { params })
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('获取科室列表失败')
  } finally {
    loading.value = false
  }
}

// 处理排序变化
const handleSortChange = ({ prop, order }: any) => {
  if (prop && order) {
    searchForm.sort_by = prop
    searchForm.sort_order = order === 'ascending' ? 'asc' : 'desc'
  } else {
    searchForm.sort_by = 'sort_order'
    searchForm.sort_order = 'asc'
  }
  // 排序时不重置页码，直接刷新当前页
  fetchDepartments()
}

// 处理每页数量变化
const handleSizeChange = () => {
  pagination.page = 1 // 改变每页数量时重置到第一页
  fetchDepartments()
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchDepartments()
}

// 重置
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.is_active = undefined
  searchForm.sort_by = 'sort_order'
  searchForm.sort_order = 'asc'
  handleSearch()
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增科室'
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: Department) => {
  isEdit.value = true
  dialogTitle.value = '编辑科室'
  Object.assign(form, row)
  dialogVisible.value = true
}

// 切换状态
const handleToggle = async (row: Department) => {
  try {
    await request.put(`/departments/${row.id}/toggle-evaluation`)
    ElMessage.success('状态切换成功')
    fetchDepartments()
  } catch (error) {
    ElMessage.error('状态切换失败')
  }
}

// 删除
const handleDelete = async (row: Department) => {
  try {
    await ElMessageBox.confirm('确定要删除该科室吗？', '提示', {
      type: 'warning'
    })
    await request.delete(`/departments/${row.id}`)
    ElMessage.success('删除成功')
    fetchDepartments()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
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
        const { his_code, is_active, id, created_at, updated_at, ...updateData } = form
        await request.put(`/departments/${form.id}`, updateData)
        ElMessage.success('更新成功')
      } else {
        const submitData = { ...form }
        // 如果sort_order为undefined，删除该字段让后端自动分配
        if (submitData.sort_order === undefined) {
          delete submitData.sort_order
        }
        await request.post('/departments', submitData)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchDepartments()
    } catch (error) {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
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
    sort_order: undefined,
    his_code: '',
    his_name: '',
    cost_center_code: '',
    cost_center_name: '',
    accounting_unit_code: '',
    accounting_unit_name: '',
    is_active: true
  })
}

onMounted(() => {
  fetchDepartments()
})
</script>

<style scoped>
.departments-container {
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
