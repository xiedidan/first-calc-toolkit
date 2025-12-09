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
        <el-form-item label="角色">
          <el-select v-model="searchForm.role_id" placeholder="全部" clearable style="width: 150px" @change="handleSearch">
            <el-option v-for="role in roleList" :key="role.id" :label="role.name" :value="role.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="医疗机构">
          <el-select v-model="searchForm.hospital_id" placeholder="全部" clearable filterable style="width: 200px" @change="handleSearch">
            <el-option v-for="h in hospitalList" :key="h.id" :label="h.name" :value="h.id" />
          </el-select>
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
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="email" label="邮箱" width="180" show-overflow-tooltip />
        <el-table-column prop="role_name" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.role_type)" size="small">
              {{ row.role_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="hospital_name" label="所属医疗机构" width="180">
          <template #default="{ row }">
            {{ row.hospital_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="department_name" label="所属科室" width="150">
          <template #default="{ row }">
            {{ row.department_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
              {{ row.status === 'active' ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="handleEdit(row)">编辑</el-button>
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
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- Add/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      append-to-body
      @close="handleDialogClose"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" :disabled="isEdit" placeholder="请输入用户名" />
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
        <el-form-item label="角色" prop="role_id">
          <el-select v-model="formData.role_id" placeholder="请选择角色" style="width: 100%" @change="handleRoleChange">
            <el-option v-for="role in roleList" :key="role.id" :label="role.name" :value="role.id">
              <span>{{ role.name }}</span>
              <span style="color: #909399; margin-left: 8px; font-size: 12px;">{{ role.role_type_display }}</span>
            </el-option>
          </el-select>
          <div v-if="selectedRoleType" style="color: #909399; font-size: 12px; margin-top: 5px;">
            {{ getRoleTypeHint(selectedRoleType) }}
          </div>
        </el-form-item>
        <el-form-item label="所属医疗机构" prop="hospital_id" v-if="needHospital">
          <el-select
            v-model="formData.hospital_id"
            placeholder="请选择医疗机构"
            filterable
            style="width: 100%"
            @change="handleHospitalChange"
          >
            <el-option v-for="h in hospitalList" :key="h.id" :label="h.name" :value="h.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属科室" prop="department_id" v-if="needDepartment">
          <el-select
            v-model="formData.department_id"
            placeholder="请选择科室"
            filterable
            style="width: 100%"
            :disabled="!formData.hospital_id"
          >
            <el-option v-for="d in departmentList" :key="d.id" :label="d.his_name" :value="d.id" />
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
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getUserList, createUser, updateUser, deleteUser } from '@/api/user'
import type { UserInfo, RoleType } from '@/api/auth'
import { getAccessibleHospitals, type Hospital } from '@/api/hospital'
import { getRoles, type Role } from '@/api/roles'
import request from '@/utils/request'

const userStore = useUserStore()

// Search form
const searchForm = reactive({
  keyword: '',
  role_id: undefined as number | undefined,
  hospital_id: undefined as number | undefined
})

// Table data
const tableData = ref<UserInfo[]>([])
const loading = ref(false)

// Lists
const hospitalList = ref<Hospital[]>([])
const roleList = ref<Role[]>([])
const departmentList = ref<any[]>([])

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
  role_id: undefined as number | undefined,
  hospital_id: undefined as number | undefined,
  department_id: undefined as number | undefined
})

// 获取选中角色的类型
const selectedRoleType = computed<RoleType | null>(() => {
  if (!formData.role_id) return null
  const role = roleList.value.find(r => r.id === formData.role_id)
  return role?.role_type || null
})

// 是否需要选择医疗机构
const needHospital = computed(() => {
  return selectedRoleType.value === 'department_user' || selectedRoleType.value === 'hospital_user'
})

// 是否需要选择科室
const needDepartment = computed(() => {
  return selectedRoleType.value === 'department_user'
})

function getRoleTagType(roleType: RoleType) {
  const map: Record<RoleType, string> = {
    department_user: 'info',
    hospital_user: '',
    admin: 'warning',
    maintainer: 'danger'
  }
  return map[roleType] || ''
}

function getRoleTypeHint(roleType: RoleType) {
  const hints: Record<RoleType, string> = {
    department_user: '科室用户只能查看本科室的业务价值报表',
    hospital_user: '全院用户可以操作本医疗机构的所有数据',
    admin: '管理员可以跨医疗机构操作，但不能管理AI接口和维护者',
    maintainer: '维护者拥有最高权限，可管理所有用户和AI接口'
  }
  return hints[roleType] || ''
}

// Form rules
const formRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [{ type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }],
  password: [{
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
  }],
  role_id: [{ required: true, message: '请选择角色', trigger: 'change' }],
  hospital_id: [{
    validator: (rule, value, callback) => {
      if (needHospital.value && !value) {
        callback(new Error('请选择所属医疗机构'))
      } else {
        callback()
      }
    },
    trigger: 'change'
  }],
  department_id: [{
    validator: (rule, value, callback) => {
      if (needDepartment.value && !value) {
        callback(new Error('请选择所属科室'))
      } else {
        callback()
      }
    },
    trigger: 'change'
  }]
}

// Fetch data
const fetchData = async () => {
  loading.value = true
  try {
    const response = await getUserList({
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword || undefined,
      role_id: searchForm.role_id,
      hospital_id: searchForm.hospital_id
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

// Fetch roles
const fetchRoles = async () => {
  try {
    const res = await getRoles({ size: 100 })
    roleList.value = res.items
  } catch (error) {
    console.error('Failed to fetch roles:', error)
  }
}

// Fetch departments
const fetchDepartments = async (hospitalId: number) => {
  try {
    const res = await request.get<any>('/departments', { params: { hospital_id: hospitalId, size: 1000 } })
    departmentList.value = res.items || []
  } catch (error) {
    console.error('Failed to fetch departments:', error)
    departmentList.value = []
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
  searchForm.role_id = undefined
  searchForm.hospital_id = undefined
  pagination.page = 1
  fetchData()
}

function handleSizeChange() {
  pagination.page = 1
  fetchData()
}

function handlePageChange() {
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
const handleEdit = async (row: UserInfo) => {
  isEdit.value = true
  dialogTitle.value = '编辑用户'
  formData.id = row.id
  formData.username = row.username
  formData.name = row.name
  formData.email = row.email || ''
  formData.password = ''
  formData.status = row.status
  formData.role_id = row.role_id
  formData.hospital_id = row.hospital_id
  formData.department_id = row.department_id
  
  // 如果有医疗机构，加载科室列表
  if (row.hospital_id) {
    await fetchDepartments(row.hospital_id)
  }
  
  dialogVisible.value = true
}

// Handle role change
const handleRoleChange = () => {
  // 切换角色类型时清空相关字段
  if (!needHospital.value) {
    formData.hospital_id = undefined
    formData.department_id = undefined
    departmentList.value = []
  }
  if (!needDepartment.value) {
    formData.department_id = undefined
  }
  // 触发表单验证
  formRef.value?.validateField(['hospital_id', 'department_id'])
}

// Handle hospital change
const handleHospitalChange = async () => {
  formData.department_id = undefined
  if (formData.hospital_id) {
    await fetchDepartments(formData.hospital_id)
  } else {
    departmentList.value = []
  }
}

// Delete
const handleDelete = (row: UserInfo) => {
  ElMessageBox.confirm(`确定要删除用户 "${row.name}" 吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
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
          const updateData: any = {
            name: formData.name,
            email: formData.email || undefined,
            status: formData.status,
            role_id: formData.role_id,
            hospital_id: needHospital.value ? formData.hospital_id : undefined,
            department_id: needDepartment.value ? formData.department_id : undefined
          }
          if (formData.password) {
            updateData.password = formData.password
          }
          await updateUser(formData.id, updateData)
          ElMessage.success('更新成功')
        } else {
          await createUser({
            username: formData.username,
            name: formData.name,
            email: formData.email || undefined,
            password: formData.password,
            role_id: formData.role_id!,
            hospital_id: needHospital.value ? formData.hospital_id : undefined,
            department_id: needDepartment.value ? formData.department_id : undefined
          })
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '操作失败')
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
  formData.role_id = undefined
  formData.hospital_id = undefined
  formData.department_id = undefined
  departmentList.value = []
}

// Initialize
onMounted(() => {
  fetchData()
  fetchHospitals()
  fetchRoles()
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
