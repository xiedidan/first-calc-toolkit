<template>
  <div class="dimension-items-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>维度目录管理</span>
          <div>
            <el-button type="danger" plain @click="handleClearAll" v-if="!showingOrphans">全部清除</el-button>
            <el-button type="danger" @click="handleClearAllOrphans" v-if="showingOrphans">清除所有孤儿记录</el-button>
            <el-button type="success" @click="handleSmartImport">智能导入</el-button>
            <el-button type="primary" @click="handleAdd">添加收费项目</el-button>
          </div>
        </div>
      </template>

      <!-- 维度选择 -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="模型版本">
          <el-select 
            v-model="modelVersionId" 
            placeholder="请选择模型版本" 
            style="width: 250px"
            @change="handleVersionChange"
          >
            <el-option
              v-for="version in modelVersions"
              :key="version.id"
              :label="`${version.version} - ${version.name}`"
              :value="version.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="维度">
          <el-select
            v-model="dimensionIds"
            placeholder="请选择维度（可多选，不选则显示全部）"
            multiple
            clearable
            filterable
            collapse-tags
            collapse-tags-tooltip
            style="width: 400px"
            @change="handleSearch"
          >
            <el-option
              v-for="dim in leafDimensions"
              :key="dim.id"
              :label="dim.full_path"
              :value="dim.id"
            />
          </el-select>
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
          <el-button type="warning" @click="handleShowOrphans">查看孤儿记录</el-button>
        </el-form-item>
      </el-form>

      <!-- 提示信息 -->
      <el-alert
        v-if="showingOrphans"
        title="正在显示所有孤儿记录（收费编码不在收费项目表中的记录）"
        type="warning"
        :closable="false"
        style="margin-bottom: 16px"
      />
      <el-alert
        v-else-if="!showingOrphans && dimensionIds.length === 0 && tableData.length > 0"
        title="正在显示所有维度的收费项目"
        type="info"
        :closable="false"
        style="margin-bottom: 16px"
      />

      <!-- 表格 -->
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="dimension_code" label="节点ID" min-width="120" v-if="showingOrphans || dimensionIds.length === 0" />
        <el-table-column prop="dimension_name" label="维度名称" min-width="200" v-if="showingOrphans || dimensionIds.length === 0 || dimensionIds.length > 1" />
        <el-table-column prop="item_code" label="收费项目编码" min-width="150" />
        <el-table-column prop="item_name" label="收费项目名称" min-width="200">
          <template #default="{ row }">
            <span v-if="row.item_name">{{ row.item_name }}</span>
            <el-tag v-else type="warning" size="small">项目不存在</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="item_category" label="项目分类" min-width="120">
          <template #default="{ row }">
            <span v-if="row.item_category">{{ row.item_category }}</span>
            <span v-else style="color: #909399">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="添加时间" min-width="180" />
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
        @current-change="handlePageChange"
        class="pagination"
      />
    </el-card>

    <!-- 添加收费项目对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="添加收费项目"
      width="600px"
      custom-class="full-height-dialog"
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

    <!-- 智能导入对话框 -->
    <DimensionSmartImport
      v-model="smartImportVisible"
      :model-version-id="modelVersionId"
      @success="handleImportSuccess"
    />

    <!-- 编辑维度对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="调整维度"
      width="500px"
      custom-class="full-height-dialog"
    >
      <el-form label-width="120px">
        <el-form-item label="收费项目">
          <el-input :value="`${editingItem?.item_code} - ${editingItem?.item_name || '(无)'}`" disabled />
        </el-form-item>
        <el-form-item label="当前维度">
          <el-input :value="editingItem?.dimension_name || '(无)'" disabled />
        </el-form-item>
        <el-form-item label="目标维度" required>
          <el-select
            v-model="targetDimensionId"
            placeholder="请选择目标维度"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="dim in leafDimensions"
              :key="dim.id"
              :label="dim.full_path"
              :value="dim.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleSubmitEdit"
          :loading="submitting"
          :disabled="!targetDimensionId"
        >
          确定
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
import DimensionSmartImport from '@/components/DimensionSmartImport.vue'

interface DimensionItem {
  id: number
  dimension_code: string
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
const smartImportVisible = ref(false)
const editDialogVisible = ref(false)
const editingItem = ref<DimensionItem | null>(null)
const targetDimensionId = ref<number | null>(null)
const modelVersionId = ref(1) // 临时硬编码，后续从路由参数获取
const dimensionIds = ref<number[]>([]) // 改为数组，支持多选
const searchKeyword = ref('')
const searchResults = ref<ChargeItem[]>([])
const selectedItems = ref<ChargeItem[]>([])
const modelVersions = ref<any[]>([]) // 模型版本列表
const leafDimensions = ref<any[]>([]) // 末级维度列表
const showingOrphans = ref(false) // 是否正在显示孤儿记录

const searchForm = reactive({
  keyword: ''
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const tableData = ref<DimensionItem[]>([])

// 获取维度目录列表
const fetchDimensionItems = async (orphansOnly = false) => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      size: pagination.size,
      orphans_only: orphansOnly
    }
    
    // 只有在不是查看孤儿记录且选择了维度时才传递维度code
    // 如果不选维度，则查询全部
    if (!orphansOnly && dimensionIds.value.length > 0) {
      // 将选中的维度ID转换为code
      const selectedCodes = dimensionIds.value
        .map(id => leafDimensions.value.find(dim => dim.id === id)?.code)
        .filter(code => code) // 过滤掉undefined
      
      if (selectedCodes.length > 0) {
        params.dimension_codes = selectedCodes.join(',')
      }
    }
    
    if (searchForm.keyword) {
      params.keyword = searchForm.keyword
    }

    const res = await request.get('/dimension-items', { params })
    tableData.value = res.items
    pagination.total = res.total
    showingOrphans.value = orphansOnly
  } catch (error) {
    ElMessage.error('获取维度目录失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  showingOrphans.value = false
  fetchDimensionItems()
}

// 查看孤儿记录
const handleShowOrphans = () => {
  pagination.page = 1
  searchForm.keyword = ''
  fetchDimensionItems(true)
}

// 处理每页数量变化
const handleSizeChange = () => {
  pagination.page = 1 // 改变每页数量时重置到第一页
  fetchDimensionItems(showingOrphans.value)
}

// 处理页码变化
const handlePageChange = () => {
  fetchDimensionItems(showingOrphans.value)
}

// 打开添加对话框
const handleAdd = () => {
  if (dimensionIds.value.length === 0) {
    ElMessage.warning('请先选择维度')
    return
  }
  if (dimensionIds.value.length > 1) {
    ElMessage.warning('添加收费项目时只能选择一个维度')
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
    // 将维度ID转换为code
    const selectedDimension = leafDimensions.value.find(dim => dim.id === dimensionIds.value[0])
    const params = {
      keyword: searchKeyword.value,
      dimension_code: selectedDimension?.code, // 使用第一个选中维度的code
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
    // 将维度ID转换为code
    const selectedDimension = leafDimensions.value.find(dim => dim.id === dimensionIds.value[0])
    const item_codes = selectedItems.value.map(item => item.item_code)
    const res = await request.post('/dimension-items', {
      dimension_code: selectedDimension?.code, // 使用第一个选中维度的code
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

// 编辑
const handleEdit = (row: DimensionItem) => {
  editingItem.value = row
  targetDimensionId.value = null
  editDialogVisible.value = true
}

// 提交编辑
const handleSubmitEdit = async () => {
  if (!targetDimensionId.value) {
    ElMessage.warning('请选择目标维度')
    return
  }

  submitting.value = true
  try {
    await request.put(`/dimension-items/${editingItem.value?.id}`, null, {
      params: {
        new_dimension_code: targetDimensionId.value
      }
    })
    ElMessage.success('调整成功')
    editDialogVisible.value = false
    fetchDimensionItems()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '调整失败')
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

// 获取模型版本列表
const fetchModelVersions = async () => {
  try {
    const res = await request.get('/model-versions')
    modelVersions.value = res.items
    if (res.items.length > 0) {
      // 默认选择激活的版本
      const activeVersion = res.items.find((v: any) => v.is_active)
      modelVersionId.value = activeVersion ? activeVersion.id : res.items[0].id
      // 加载该版本的维度列表
      await fetchLeafDimensions(modelVersionId.value)
    }
  } catch (error) {
    ElMessage.error('获取模型版本列表失败')
  }
}

// 获取末级维度列表
const fetchLeafDimensions = async (versionId: number) => {
  try {
    const res = await request.get(`/model-nodes/version/${versionId}/leaf`)
    leafDimensions.value = res.map((node: any) => ({
      id: node.id,
      code: node.code,  // 添加code字段
      name: node.name,
      full_path: node.full_path || node.name
    }))
    // 加载完维度后自动查询
    await fetchDimensionItems()
  } catch (error) {
    ElMessage.error('获取维度列表失败')
  }
}

// 版本变化时重新加载维度列表
const handleVersionChange = async () => {
  dimensionIds.value = []
  tableData.value = []
  pagination.total = 0
  await fetchLeafDimensions(modelVersionId.value)
}

// 打开智能导入对话框
const handleSmartImport = () => {
  if (!modelVersionId.value) {
    ElMessage.warning('请先选择模型版本')
    return
  }
  smartImportVisible.value = true
}

// 导入成功回调
const handleImportSuccess = () => {
  ElMessage.success('导入成功')
  if (dimensionId.value) {
    fetchDimensionItems()
  }
}

// 全部清除
const handleClearAll = async () => {
  // 如果选择了多个维度，提示只能选择一个或不选
  if (dimensionIds.value.length > 1) {
    ElMessage.warning('清空操作只能选择一个维度或不选（清空全部）')
    return
  }

  // 根据是否选择维度显示不同的提示
  const confirmMessage = dimensionIds.value.length === 0
    ? `确定要清空当前医院的所有维度目录数据吗？此操作不可恢复！`
    : `确定要清空所选维度的所有收费项目吗？此操作不可恢复！`

  try {
    await ElMessageBox.confirm(
      confirmMessage,
      '警告',
      {
        confirmButtonText: '确定清空',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    // 如果选择了维度，清空该维度；否则清空全部
    if (dimensionIds.value.length === 1) {
      // 将维度ID转换为code
      const selectedDimension = leafDimensions.value.find(dim => dim.id === dimensionIds.value[0])
      if (!selectedDimension?.code) {
        ElMessage.error('无法获取维度编码')
        return
      }
      await request.delete(`/dimension-items/dimension/${selectedDimension.code}/clear-all`)
    } else {
      // 清空全部
      await request.delete('/dimension-items/clear-all')
    }
    
    ElMessage.success('清空成功')
    fetchDimensionItems()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('清空失败')
    }
  }
}

// 清除所有孤儿记录
const handleClearAllOrphans = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要清除所有孤儿记录吗？共 ${pagination.total} 条记录。此操作不可恢复！`,
      '警告',
      {
        confirmButtonText: '确定清除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    const res = await request.delete('/dimension-items/orphans/clear-all')
    ElMessage.success(res.message || `已清除 ${res.deleted_count} 条孤儿记录`)
    // 重新查询孤儿记录
    fetchDimensionItems(true)
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('清除失败')
    }
  }
}

onMounted(() => {
  fetchModelVersions()
  // 不再自动查询，等待用户输入维度ID或点击查看孤儿记录
})
</script>

<style scoped>
.dimension-items-container {
  padding: 0;
  width: 100%;
  height: 100%;
}

.dimension-items-container :deep(.el-card) {
  width: 100%;
  height: 100%;
}

.dimension-items-container :deep(.el-card__body) {
  height: calc(100% - 60px);
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.dimension-items-container :deep(.el-table) {
  flex: 1;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
