<template>
  <div class="users-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增用户
          </el-button>
        </div>
      </template>

      <!-- Search bar -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="用户名/姓名/邮箱"
            clearable
            @clear="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>

      <!-- Table -->
      <el-table
        :data="tableData"
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="name" label="姓名" width="150" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'" size="small">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="hospital_name" label="所属医疗机构" width="200">
          <template #default="{ row }">
            {{ row.hospital_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              link
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              link
              @click="handleDelete(row)"
              :disabled="row.id === userStore.userInfo?.id"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchData"
        @current-change="fetchData"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- Add/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      custom-class="full-height-dialog"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="formData.username"
            :disabled="isEdit"
            placeholder="请输入用户名"
          />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="formData.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="formData.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="formData.password"
            type="password"
            :placeholder="isEdit ? '不修改请留空' : '请输入密码'"
            show-password
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-radio-group v-model="formData.role" @change="handleRoleChange">
            <el-radio label="admin">管理员</el-radio>
            <el-radio label="user">普通用户</el-radio>
          </el-radio-group>
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">
            管理员可访问所有医疗机构，普通用户只能访问所属医疗机构
          </div>
        </el-form-item>
        <el-form-item label="所属医疗机构" prop="hospital_id" v-if="formData.role === 'user'">
          <el-select
            v-model="formData.hospital_id"
            placeholder="请选择医疗机构"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="hospital in hospitalList"
              :key="hospital.id"
              :label="hospital.name"
              :value="hospital.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status" v-if="isEdit">
          <el-radio-group v-model="formData.status">
            <el-radio label="active">正常</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
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
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getUserList, createUser, updateUser, deleteUser, type UserInfo } from '@/api/user'
import { getAccessibleHospitals, type Hospital } from '@/api/hospital'

const userStore = useUserStore()

// Search form
const searchForm = reactive({
  keyword: ''
})

// Table data
const tableData = ref<UserInfo[]>([])
const loading = ref(false)

// Hospital list
const hospitalList = ref<Hospital[]>([])

// Pagination
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// Dialog
const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

// Form data
const formData = reactive({
  id: 0,
  username: '',
  name: '',
  email: '',
  password: '',
  status: 'active',
  role: 'user' as 'admin' | 'user',
  hospital_id: undefined as number | undefined
})

// Form rules
const formRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    {
      validator: (rule, value, callback) => {
        if (!isEdit.value && !value) {
          callback(new Error('请输入密码'))
        } else if (value && value.length < 6) {
          callback(new Error('密码长度不能少于6个字符'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  hospital_id: [
    {
      validator: (rule, value, callback) => {
        if (formData.role === 'user' && !value) {
          callback(new Error('普通用户必须选择所属医疗机构'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

// Fetch data
const fetchData = async () => {
  loading.value = true
  try {
    const response = await getUserList({
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword || undefined
    })
    tableData.value = response.items
    pagination.total = response.total
  } catch (error) {
    console.error('Failed to fetch users:', error)
  } finally {
    loading.value = false
  }
}

// Fetch hospitals
const fetchHospitals = async () => {
  try {
    hospitalList.value = await getAccessibleHospitals()
  } catch (error) {
    console.error('Failed to fetch hospitals:', error)
  }
}

// Search
const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

// Reset
const handleReset = () => {
  searchForm.keyword = ''
  pagination.page = 1
  fetchData()
}

// Add
const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增用户'
  resetForm()
  dialogVisible.value = true
}

// Edit
const handleEdit = (row: UserInfo) => {
  isEdit.value = true
  dialogTitle.value = '编辑用户'
  formData.id = row.id
  formData.username = row.username
  formData.name = row.name
  formData.email = row.email || ''
  formData.password = ''
  formData.status = row.status
  formData.role = row.role
  formData.hospital_id = row.hospital_id
  dialogVisible.value = true
}

// Handle role change
const handleRoleChange = () => {
  // 切换为管理员时清空医疗机构
  if (formData.role === 'admin') {
    formData.hospital_id = undefined
  }
  // 触发表单验证
  formRef.value?.validateField('hospital_id')
}

// Delete
const handleDelete = (row: UserInfo) => {
  ElMessageBox.confirm(
    `确定要删除用户 "${row.name}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteUser(row.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      console.error('Failed to delete user:', error)
    }
  })
}

// Submit
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value) {
          // Update
          const updateData: any = {
            name: formData.name,
            email: formData.email || undefined,
            status: formData.status,
            role: formData.role
          }
          if (formData.password) {
            updateData.password = formData.password
          }
          if (formData.role === 'user' && formData.hospital_id) {
            updateData.hospital_id = formData.hospital_id
          }
          await updateUser(formData.id, updateData)
          ElMessage.success('更新成功')
        } else {
          // Create
          await createUser({
            username: formData.username,
            name: formData.name,
            email: formData.email || undefined,
            password: formData.password,
            role: formData.role,
            hospital_id: formData.role === 'user' ? formData.hospital_id : undefined
          })
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        console.error('Failed to submit:', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

// Dialog close
const handleDialogClose = () => {
  formRef.value?.resetFields()
  resetForm()
}

// Reset form
const resetForm = () => {
  formData.id = 0
  formData.username = ''
  formData.name = ''
  formData.email = ''
  formData.password = ''
  formData.status = 'active'
  formData.role = 'user'
  formData.hospital_id = undefined
}

// Initialize
onMounted(() => {
  fetchData()
  fetchHospitals()
})
</script>

<style scoped>
.users-page {
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
</style>
