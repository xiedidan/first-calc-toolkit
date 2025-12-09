<template>
  <div class="orientation-ladders-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>导向阶梯管理</span>
          <el-button type="primary" @click="handleAdd">新增导向阶梯</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="所属导向">
          <el-select
            v-model="searchForm.rule_id"
            placeholder="全部"
            clearable
            filterable
            @change="handleSearch"
            style="width: 250px"
          >
            <el-option
              v-for="rule in ladderRules"
              :key="rule.id"
              :label="rule.name"
              :value="rule.id"
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
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="rule_name" label="所属导向" width="200" />
        <el-table-column prop="ladder_order" label="阶梯次序" width="100" align="center" />
        <el-table-column label="阶梯下限" width="150" align="right">
          <template #default="{ row }">
            {{ formatInfinityValue(row.lower_limit, false) }}
          </template>
        </el-table-column>
        <el-table-column label="阶梯上限" width="150" align="right">
          <template #default="{ row }">
            {{ formatInfinityValue(row.upper_limit, true) }}
          </template>
        </el-table-column>
        <el-table-column prop="adjustment_intensity" label="调整力度" width="120" align="right" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
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
        @current-change="fetchLadders"
        class="pagination"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <OrientationLadderDialog
      v-model="dialogVisible"
      :ladder="currentLadder"
      :is-edit="isEdit"
      @success="handleDialogSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute } from 'vue-router'
import request from '@/utils/request'
import OrientationLadderDialog from '@/components/OrientationLadderDialog.vue'

interface OrientationLadder {
  id: number
  rule_id: number
  rule_name: string
  ladder_order: number
  upper_limit: string | null
  lower_limit: string | null
  adjustment_intensity: string
  created_at: string
  updated_at: string
}

interface OrientationRule {
  id: number
  name: string
  category: string
}

const route = useRoute()
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentLadder = ref<OrientationLadder | null>(null)

const searchForm = reactive({
  rule_id: null as number | null
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const tableData = ref<OrientationLadder[]>([])
const ladderRules = ref<OrientationRule[]>([])

// 获取支持阶梯的导向规则列表（基准阶梯和直接阶梯）
const fetchLadderRules = async () => {
  try {
    // 获取基准阶梯类别
    const res1 = await request.get('/orientation-rules', {
      params: {
        category: 'benchmark_ladder',
        page: 1,
        size: 1000
      }
    })
    
    // 获取直接阶梯类别
    const res2 = await request.get('/orientation-rules', {
      params: {
        category: 'direct_ladder',
        page: 1,
        size: 1000
      }
    })
    
    // 合并两个列表
    ladderRules.value = [...res1.items, ...res2.items]
  } catch (error) {
    ElMessage.error('获取导向规则列表失败')
  }
}

// 获取导向阶梯列表
const fetchLadders = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      size: pagination.size
    }
    if (searchForm.rule_id) {
      params.rule_id = searchForm.rule_id
    }

    const res = await request.get('/orientation-ladders', { params })
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('获取导向阶梯列表失败')
  } finally {
    loading.value = false
  }
}

// 格式化无穷值显示
const formatInfinityValue = (value: string | null, isUpper: boolean) => {
  if (value === null || value === undefined) {
    return isUpper ? '+∞' : '-∞'
  }
  return value
}

// 处理每页数量变化
const handleSizeChange = () => {
  pagination.page = 1
  fetchLadders()
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchLadders()
}

// 重置
const handleReset = () => {
  searchForm.rule_id = null
  handleSearch()
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  currentLadder.value = null
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: OrientationLadder) => {
  isEdit.value = true
  currentLadder.value = { ...row }
  dialogVisible.value = true
}

// 删除
const handleDelete = async (row: OrientationLadder) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除该导向阶梯吗？`,
      '提示',
      {
        type: 'warning'
      }
    )
    
    await request.delete(`/orientation-ladders/${row.id}`)
    ElMessage.success('删除成功')
    fetchLadders()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 对话框成功回调
const handleDialogSuccess = () => {
  fetchLadders()
}

// 初始化
onMounted(async () => {
  // 先获取导向规则列表
  await fetchLadderRules()
  
  // 从 URL 参数读取 rule_id
  const ruleIdParam = route.query.rule_id
  if (ruleIdParam) {
    searchForm.rule_id = Number(ruleIdParam)
  }
  
  // 获取阶梯列表
  fetchLadders()
})
</script>

<style scoped>
.orientation-ladders-container {
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
