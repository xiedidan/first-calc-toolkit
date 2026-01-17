<template>
  <div class="inclusive-fees-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>内含收费管理</span>
          <el-button type="primary" @click="handleAdd">添加内含收费</el-button>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="项目代码/项目名称"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
            @input="handleKeywordInput"
            style="width: 250px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table
        :data="tableData"
        border
        stripe
        v-loading="loading"
      >
        <template #empty>
          <el-empty 
            :description="loading ? '加载中...' : getEmptyDescription()" 
            :image-size="100"
          />
        </template>
        <el-table-column prop="item_code" label="项目代码" width="200" show-overflow-tooltip />
        <el-table-column prop="item_name" label="项目名称" min-width="250" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.item_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="cost" label="单位成本" width="150" align="right">
          <template #default="{ row }">
            {{ formatNumber(row.cost) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column prop="updated_at" label="更新时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right" align="center">
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
        @current-change="fetchInclusiveFees"
        class="pagination"
      />
    </el-card>

    <!-- 添加/编辑对话框 -->
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
        <el-form-item label="项目代码" prop="item_code">
          <el-input
            v-model="form.item_code"
            placeholder="请输入项目代码"
            maxlength="255"
          />
        </el-form-item>
        <el-form-item label="项目名称" prop="item_name">
          <el-input
            v-model="form.item_name"
            placeholder="请输入项目名称（可选）"
            maxlength="255"
          />
        </el-form-item>
        <el-form-item label="单位成本" prop="cost">
          <el-input-number
            v-model="form.cost"
            :min="0"
            :precision="2"
            :step="1"
            placeholder="请输入单位成本"
            style="width: 100%"
          />
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
import {
  getInclusiveFees,
  createInclusiveFee,
  updateInclusiveFee,
  deleteInclusiveFee,
  type DimInclusiveFee
} from '@/api/dim-inclusive-fees'

// 防抖函数
function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null
  return function (this: any, ...args: Parameters<T>) {
    const context = this
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => {
      func.apply(context, args)
    }, wait)
  }
}

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const dialogTitle = ref('添加内含收费')
const formRef = ref<FormInstance>()

// 搜索表单
const searchForm = reactive({
  keyword: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 表格数据
const tableData = ref<DimInclusiveFee[]>([])

// 表单数据
const form = reactive({
  id: 0,
  item_code: '',
  item_name: '',
  cost: undefined as number | undefined
})

// 表单验证规则
const rules = {
  item_code: [
    { required: true, message: '请输入项目代码', trigger: 'blur' },
    { max: 255, message: '项目代码不能超过255个字符', trigger: 'blur' }
  ],
  item_name: [
    { max: 255, message: '项目名称不能超过255个字符', trigger: 'blur' }
  ],
  cost: [
    { required: true, message: '请输入单位成本', trigger: 'blur' },
    { type: 'number', min: 0, message: '单位成本不能为负数', trigger: ['blur', 'change'] }
  ]
}

// 获取内含式收费列表
const fetchInclusiveFees = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      size: pagination.size
    }
    if (searchForm.keyword) {
      params.keyword = searchForm.keyword
    }

    const res = await getInclusiveFees(params)
    tableData.value = res.items || []
    pagination.total = res.total || 0
  } catch (error: any) {
    console.error('获取内含式收费列表失败:', error)
    tableData.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchInclusiveFees()
}

// 防抖搜索
const debouncedSearch = debounce(() => {
  handleSearch()
}, 500)

// 处理关键词输入
const handleKeywordInput = () => {
  debouncedSearch()
}

// 重置
const handleReset = () => {
  searchForm.keyword = ''
  handleSearch()
}

// 处理每页数量变化
const handleSizeChange = () => {
  pagination.page = 1
  fetchInclusiveFees()
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '添加内含收费'
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: DimInclusiveFee) => {
  isEdit.value = true
  dialogTitle.value = '编辑内含收费'
  Object.assign(form, {
    id: row.id,
    item_code: row.item_code,
    item_name: row.item_name || '',
    cost: row.cost
  })
  dialogVisible.value = true
}

// 删除
const handleDelete = async (row: DimInclusiveFee) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目代码为 "${row.item_code}" 的内含收费吗？`,
      '提示',
      {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }
    )
    
    await deleteInclusiveFee(row.id)
    ElMessage.success('删除成功')
    
    // 如果删除后当前页没有数据，返回上一页
    if (tableData.value.length === 1 && pagination.page > 1) {
      pagination.page--
    }
    
    fetchInclusiveFees()
  } catch (error: any) {
    if (error === 'cancel') return
    console.error('删除内含式收费失败:', error)
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    const valid = await formRef.value.validate()
    if (!valid) {
      ElMessage.warning('请填写完整的表单信息')
      return
    }

    submitting.value = true
    
    const submitData = {
      item_code: form.item_code,
      item_name: form.item_name || undefined,
      cost: form.cost!
    }

    if (isEdit.value) {
      await updateInclusiveFee(form.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await createInclusiveFee(submitData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchInclusiveFees()
  } catch (error: any) {
    console.error('提交表单失败:', error)
  } finally {
    submitting.value = false
  }
}

// 关闭对话框
const handleDialogClose = () => {
  formRef.value?.resetFields()
  Object.assign(form, {
    id: 0,
    item_code: '',
    item_name: '',
    cost: undefined
  })
}

// 格式化数字
const formatNumber = (value: number) => {
  return value.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

// 获取空数据提示文本
const getEmptyDescription = () => {
  if (searchForm.keyword) {
    return '未找到符合条件的数据，请尝试调整搜索条件'
  }
  return '暂无内含收费数据，点击"添加内含收费"按钮创建'
}

// 生命周期
onMounted(() => {
  fetchInclusiveFees()
})
</script>

<style scoped>
.inclusive-fees-container {
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
