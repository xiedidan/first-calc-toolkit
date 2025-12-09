<template>
  <div class="roles-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户角色管理</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建角色
          </el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-form">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索角色名称或代码"
          clearable
          style="width: 300px"
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch">
              <el-icon><Search /></el-icon>
            </el-button>
          </template>
        </el-input>
      </div>

      <!-- 角色列表 -->
      <el-table :data="roleList" v-loading="loading" border stripe>
        <el-table-column prop="name" label="角色名称" width="150" />
        <el-table-column prop="code" label="角色代码" width="150" />
        <el-table-column prop="role_type_display" label="角色类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getRoleTypeTagType(row.role_type)">
              {{ row.role_type_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="user_count" label="用户数" width="100" align="center" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" link @click="handlePermission(row)">权限配置</el-button>
            <el-button type="danger" link @click="handleDelete(row)" :disabled="row.user_count > 0">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 新建/编辑角色对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑角色' : '新建角色'"
      width="500px"
      append-to-body
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色代码" prop="code">
          <el-input v-model="formData.code" placeholder="请输入角色代码" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="角色类型" prop="role_type">
          <el-select v-model="formData.role_type" placeholder="请选择角色类型" style="width: 100%">
            <el-option
              v-for="(label, value) in roleTypeOptions"
              :key="value"
              :label="label"
              :value="value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 权限配置对话框 -->
    <el-dialog
      v-model="permissionDialogVisible"
      title="菜单权限配置"
      width="600px"
      append-to-body
    >
      <div class="permission-header">
        <span>角色：{{ currentRole?.name }}</span>
        <el-button type="primary" link @click="handleSelectAll">全选</el-button>
        <el-button type="primary" link @click="handleDeselectAll">取消全选</el-button>
      </div>
      <el-tree
        ref="treeRef"
        :data="menuTree"
        show-checkbox
        node-key="path"
        :props="{ label: 'name', children: 'children' }"
        :default-checked-keys="checkedMenus"
        :default-expand-all="true"
        @check="handleMenuCheck"
      />
      <template #footer>
        <el-button @click="permissionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSavePermission" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { getRoles, getRole, createRole, updateRole, deleteRole, type Role, type RoleType, ROLE_TYPE_DISPLAY } from '@/api/roles'
import { getPermissionMenuTree, getAllMenuPaths } from '@/config/menus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const loading = ref(false)
const submitting = ref(false)
const roleList = ref<Role[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchKeyword = ref('')

const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const formData = reactive({
  id: 0,
  name: '',
  code: '',
  role_type: '' as RoleType,
  description: ''
})

const permissionDialogVisible = ref(false)
const currentRole = ref<Role | null>(null)
const menuTree = ref<any[]>([])
const checkedMenus = ref<string[]>([])
const treeRef = ref()

// 角色类型选项（维护者只能由维护者创建）
const roleTypeOptions = computed(() => {
  const options: Record<string, string> = { ...ROLE_TYPE_DISPLAY }
  if (!userStore.isMaintainer) {
    delete options.maintainer
  }
  return options
})

const formRules: FormRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色代码', trigger: 'blur' }],
  role_type: [{ required: true, message: '请选择角色类型', trigger: 'change' }]
}

function getRoleTypeTagType(roleType: RoleType): string {
  const map: Record<RoleType, string> = {
    department_user: 'info',
    hospital_user: 'success',
    admin: 'warning',
    maintainer: 'danger'
  }
  return map[roleType] || ''
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

async function loadRoles() {
  loading.value = true
  try {
    const res = await getRoles({
      page: currentPage.value,
      size: pageSize.value,
      keyword: searchKeyword.value || undefined
    })
    roleList.value = res.items
    total.value = res.total
  } catch (error) {
    console.error('Failed to load roles:', error)
  } finally {
    loading.value = false
  }
}

function loadMenus() {
  // 使用前端统一的菜单配置
  menuTree.value = getPermissionMenuTree()
}

function handleSearch() {
  currentPage.value = 1
  loadRoles()
}

function handleSizeChange() {
  currentPage.value = 1
  loadRoles()
}

function handlePageChange() {
  loadRoles()
}

function handleCreate() {
  isEdit.value = false
  formData.id = 0
  formData.name = ''
  formData.code = ''
  formData.role_type = '' as RoleType
  formData.description = ''
  dialogVisible.value = true
}

function handleEdit(row: Role) {
  isEdit.value = true
  formData.id = row.id
  formData.name = row.name
  formData.code = row.code
  formData.role_type = row.role_type
  formData.description = row.description || ''
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate()
  
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateRole(formData.id, {
        name: formData.name,
        role_type: formData.role_type,
        description: formData.description
      })
      ElMessage.success('更新成功')
    } else {
      await createRole({
        name: formData.name,
        code: formData.code,
        role_type: formData.role_type,
        description: formData.description
      })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadRoles()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row: Role) {
  await ElMessageBox.confirm(`确定要删除角色"${row.name}"吗？`, '提示', {
    type: 'warning'
  })
  
  try {
    await deleteRole(row.id)
    ElMessage.success('删除成功')
    loadRoles()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

async function handlePermission(row: Role) {
  try {
    // 从后端获取角色详情，确保数据最新
    const role = await getRole(row.id)
    currentRole.value = role
    const permissions = role.menu_permissions ? [...role.menu_permissions] : []
    checkedMenus.value = permissions
    permissionDialogVisible.value = true
    // 等待对话框渲染后手动设置选中状态
    setTimeout(() => {
      treeRef.value?.setCheckedKeys(permissions)
    }, 100)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '获取角色详情失败')
  }
}

function handleMenuCheck() {
  // 获取选中的菜单路径
  checkedMenus.value = treeRef.value?.getCheckedKeys() || []
}

function handleSelectAll() {
  const allKeys = getAllMenuKeys()
  treeRef.value?.setCheckedKeys(allKeys)
  checkedMenus.value = allKeys
}

function handleDeselectAll() {
  treeRef.value?.setCheckedKeys([])
  checkedMenus.value = []
}

function getAllMenuKeys(): string[] {
  return getAllMenuPaths()
}

async function handleSavePermission() {
  if (!currentRole.value) return
  
  submitting.value = true
  try {
    await updateRole(currentRole.value.id, {
      menu_permissions: checkedMenus.value
    })
    ElMessage.success('权限配置保存成功')
    permissionDialogVisible.value = false
    loadRoles()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadRoles()
  loadMenus()
})
</script>

<style scoped>
.roles-container {
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

.permission-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.permission-header span {
  font-weight: 600;
}
</style>
