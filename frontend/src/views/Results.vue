<template>
  <div class="results-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>业务价值报表</span>
          <div class="header-actions">
            <el-button @click="exportSummary" :loading="exporting">导出汇总表</el-button>
            <el-button type="primary" @click="exportDetail" :loading="exporting">导出明细表</el-button>
          </div>
        </div>
      </template>

      <!-- 筛选条件 -->
      <div class="filter-section">
        <el-form :inline="true" :model="filterForm">
          <el-form-item label="评估月份">
            <el-date-picker
              v-model="filterForm.period"
              type="month"
              placeholder="选择月份"
              format="YYYY-MM"
              value-format="YYYY-MM"
              @change="loadSummary"
            />
          </el-form-item>
          <el-form-item label="模型版本">
            <el-select 
              v-model="filterForm.model_version_id" 
              placeholder="默认使用激活版本" 
              @change="loadSummary" 
              clearable
              style="width: 240px"
            >
              <el-option
                v-for="version in versions"
                :key="version.id"
                :label="version.name"
                :value="version.id"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>

      <!-- 汇总表 -->
      <div class="table-section">
        <h3>科室业务价值汇总</h3>
        <el-table :data="summaryData" v-loading="loading" stripe border>
        <el-table-column prop="department_name" label="科室" width="200" fixed />
        <el-table-column label="医生序列" align="center">
          <el-table-column prop="doctor_value" label="价值" width="120" align="right">
            <template #default="{ row }">
              {{ formatNumber(row.doctor_value) }}
            </template>
          </el-table-column>
          <el-table-column prop="doctor_ratio" label="占比" width="100" align="right">
            <template #default="{ row }">
              {{ formatPercent(row.doctor_ratio) }}
            </template>
          </el-table-column>
        </el-table-column>
        <el-table-column label="护理序列" align="center">
          <el-table-column prop="nurse_value" label="价值" width="120" align="right">
            <template #default="{ row }">
              {{ formatNumber(row.nurse_value) }}
            </template>
          </el-table-column>
          <el-table-column prop="nurse_ratio" label="占比" width="100" align="right">
            <template #default="{ row }">
              {{ formatPercent(row.nurse_ratio) }}
            </template>
          </el-table-column>
        </el-table-column>
        <el-table-column label="医技序列" align="center">
          <el-table-column prop="tech_value" label="价值" width="120" align="right">
            <template #default="{ row }">
              {{ formatNumber(row.tech_value) }}
            </template>
          </el-table-column>
          <el-table-column prop="tech_ratio" label="占比" width="100" align="right">
            <template #default="{ row }">
              {{ formatPercent(row.tech_ratio) }}
            </template>
          </el-table-column>
        </el-table-column>
        <el-table-column prop="total_value" label="科室总价值" width="150" align="right" fixed="right">
          <template #default="{ row }">
            {{ formatNumber(row.total_value) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">
              查看明细
            </el-button>
          </template>
        </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 明细对话框 -->
    <el-dialog 
      v-model="detailDialogVisible" 
      :title="`${currentDepartment?.department_name} - 业务价值明细`" 
      width="95%" 
      top="3vh"
      class="detail-dialog"
    >
      <el-tabs v-model="activeTab" class="detail-tabs">
        <!-- 医生序列 -->
        <el-tab-pane label="医生序列" name="doctor" v-if="detailData?.doctor && detailData.doctor.length > 0">
          <div class="table-title">{{ currentDepartment?.department_name }} - 医生序列业务价值明细（{{ filterForm.period }}）</div>
          <el-table 
            :data="detailData.doctor" 
            border 
            stripe
            class="structure-table"
            row-key="id"
            :tree-props="{ children: 'children' }"
            :default-expand-all="true"
          >
            <el-table-column prop="dimension_name" label="维度名称（业务价值占比）" min-width="240" align="left">
              <template #default="{ row }">
                <span class="dimension-name">{{ row.dimension_name }}</span>
                <span v-if="row.ratio != null" class="ratio-text">（{{ formatPercent(row.ratio) }}）</span>
              </template>
            </el-table-column>
            <el-table-column prop="workload" label="工作量" min-width="110" align="right">
              <template #default="{ row }">{{ formatNumber(row.workload) }}</template>
            </el-table-column>
            <el-table-column prop="hospital_value" label="全院业务价值" min-width="102" align="right">
              <template #default="{ row }">{{ formatValueOrDash(row.hospital_value) }}</template>
            </el-table-column>
            <el-table-column prop="business_guide" label="业务导向" min-width="168" align="center">
              <template #default="{ row }">{{ row.business_guide || '-' }}</template>
            </el-table-column>
            <el-table-column prop="dept_value" label="科室业务价值" min-width="102" align="right">
              <template #default="{ row }">{{ formatValueOrDash(row.dept_value) }}</template>
            </el-table-column>
            <el-table-column prop="amount" label="业务价值金额" min-width="110" align="right">
              <template #default="{ row }">{{ formatNumber(row.amount) }}</template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 护理序列 -->
        <el-tab-pane label="护理序列" name="nurse" v-if="detailData?.nurse && detailData.nurse.length > 0">
          <div class="table-title">{{ currentDepartment?.department_name }} - 护理序列业务价值明细（{{ filterForm.period }}）</div>
          <el-table 
            :data="detailData.nurse" 
            border 
            stripe
            class="structure-table"
            row-key="id"
            :tree-props="{ children: 'children' }"
            :default-expand-all="true"
          >
            <el-table-column prop="dimension_name" label="维度名称（业务价值占比）" min-width="240" align="left">
              <template #default="{ row }">
                <span class="dimension-name">{{ row.dimension_name }}</span>
                <span v-if="row.ratio != null" class="ratio-text">（{{ formatPercent(row.ratio) }}）</span>
              </template>
            </el-table-column>
            <el-table-column prop="workload" label="工作量" min-width="110" align="right">
              <template #default="{ row }">{{ formatNumber(row.workload) }}</template>
            </el-table-column>
            <el-table-column prop="hospital_value" label="全院业务价值" min-width="102" align="right">
              <template #default="{ row }">{{ formatValueOrDash(row.hospital_value) }}</template>
            </el-table-column>
            <el-table-column prop="business_guide" label="业务导向" min-width="168" align="center">
              <template #default="{ row }">{{ row.business_guide || '-' }}</template>
            </el-table-column>
            <el-table-column prop="dept_value" label="科室业务价值" min-width="102" align="right">
              <template #default="{ row }">{{ formatValueOrDash(row.dept_value) }}</template>
            </el-table-column>
            <el-table-column prop="amount" label="业务价值金额" min-width="110" align="right">
              <template #default="{ row }">{{ formatNumber(row.amount) }}</template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 医技序列 -->
        <el-tab-pane label="医技序列" name="tech" v-if="detailData?.tech && detailData.tech.length > 0">
          <div class="table-title">{{ currentDepartment?.department_name }} - 医技序列业务价值明细（{{ filterForm.period }}）</div>
          <el-table 
            :data="detailData.tech" 
            border 
            stripe
            class="structure-table"
            row-key="id"
            :tree-props="{ children: 'children' }"
            :default-expand-all="true"
          >
            <el-table-column prop="dimension_name" label="维度名称（业务价值占比）" min-width="240" align="left">
              <template #default="{ row }">
                <span class="dimension-name">{{ row.dimension_name }}</span>
                <span v-if="row.ratio != null" class="ratio-text">（{{ formatPercent(row.ratio) }}）</span>
              </template>
            </el-table-column>
            <el-table-column prop="workload" label="工作量" min-width="110" align="right">
              <template #default="{ row }">{{ formatNumber(row.workload) }}</template>
            </el-table-column>
            <el-table-column prop="hospital_value" label="全院业务价值" min-width="102" align="right">
              <template #default="{ row }">{{ formatValueOrDash(row.hospital_value) }}</template>
            </el-table-column>
            <el-table-column prop="business_guide" label="业务导向" min-width="168" align="center">
              <template #default="{ row }">{{ row.business_guide || '-' }}</template>
            </el-table-column>
            <el-table-column prop="dept_value" label="科室业务价值" min-width="102" align="right">
              <template #default="{ row }">{{ formatValueOrDash(row.dept_value) }}</template>
            </el-table-column>
            <el-table-column prop="amount" label="业务价值金额" min-width="110" align="right">
              <template #default="{ row }">{{ formatNumber(row.amount) }}</template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'
import { getModelVersions } from '@/api/model'
import { getSystemSettings } from '@/api/system-settings'
import request from '@/utils/request'

const route = useRoute()

// 数据
const loading = ref(false)
const exporting = ref(false)
const versions = ref<any[]>([])
const summaryData = ref<any[]>([])
const detailData = ref<any>(null)
const currentDepartment = ref<any>(null)
const detailDialogVisible = ref(false)
const activeTab = ref('doctor')

const filterForm = reactive({
  period: route.query.period as string || '',
  model_version_id: null as number | null
})

// 方法
const loadVersions = async () => {
  try {
    const response: any = await getModelVersions({ skip: 0, limit: 1000 })
    versions.value = response.items || []
    
    // 默认选中激活的版本
    const activeVersion = versions.value.find((v: any) => v.is_active)
    if (activeVersion && !filterForm.model_version_id) {
      filterForm.model_version_id = activeVersion.id
    }
  } catch (error: any) {
    ElMessage.error('加载模型版本失败')
    console.error('加载模型版本错误:', error)
  }
}

const currentTaskId = ref<string>('')

const loadSummary = async () => {
  if (!filterForm.period) {
    ElMessage.warning('请选择评估月份')
    return
  }

  loading.value = true
  try {
    const response: any = await request({
      url: '/calculation/results/summary',
      method: 'get',
      params: {
        period: filterForm.period,
        model_version_id: filterForm.model_version_id
      }
    })
    
    summaryData.value = [response.summary, ...response.departments]
    currentTaskId.value = response.task_id || ''
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载汇总数据失败')
  } finally {
    loading.value = false
  }
}

const viewDetail = async (row: any) => {
  currentDepartment.value = row
  
  // 使用当前任务ID或URL参数中的任务ID
  const taskId = currentTaskId.value || route.query.task_id as string
  if (!taskId) {
    ElMessage.error('缺少任务ID，无法查看明细')
    return
  }
  
  try {
    let response: any
    
    // 判断是全院汇总还是单科室
    if (row.department_id === 0) {
      // 全院汇总明细
      response = await request({
        url: '/calculation/results/hospital-detail',
        method: 'get',
        params: {
          task_id: taskId
        }
      })
    } else {
      // 单科室明细
      response = await request({
        url: '/calculation/results/detail',
        method: 'get',
        params: {
          dept_id: row.department_id,
          task_id: taskId
        }
      })
    }
    
    detailData.value = response
    activeTab.value = 'doctor'
    detailDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载明细数据失败')
  }
}

// 格式化值或显示"-"
const formatValueOrDash = (value: any) => {
  if (value === '-' || value === null || value === undefined) return '-'
  return formatNumber(value)
}

const exportSummary = async () => {
  if (!filterForm.period) {
    ElMessage.warning('请选择评估月份')
    return
  }

  exporting.value = true
  try {
    const response = await request({
      url: '/calculation/results/export/summary',
      method: 'get',
      params: {
        period: filterForm.period,
        model_version_id: filterForm.model_version_id
      },
      responseType: 'blob'
    })
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `科室业务价值汇总_${filterForm.period}.xlsx`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '导出失败')
  } finally {
    exporting.value = false
  }
}

const exportDetail = async () => {
  const taskId = currentTaskId.value || route.query.task_id as string
  if (!taskId) {
    ElMessage.warning('缺少任务ID，无法导出明细')
    return
  }

  exporting.value = true
  try {
    const response = await request({
      url: '/calculation/results/export/detail',
      method: 'get',
      params: {
        task_id: taskId
      },
      responseType: 'blob'
    })
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `业务价值明细表_${filterForm.period}.zip`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '导出失败')
  } finally {
    exporting.value = false
  }
}

const formatNumber = (value: any) => {
  if (value === null || value === undefined) return '-'
  return Number(value).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

const formatPercent = (value: any) => {
  if (value === null || value === undefined) return '-'
  return `${Number(value).toFixed(2)}%`
}

// 生命周期
onMounted(async () => {
  loadVersions()
  
  // 如果 URL 没有传入 period，则从系统设置获取当期年月
  if (!filterForm.period) {
    try {
      const settings = await getSystemSettings()
      if (settings.current_period) {
        filterForm.period = settings.current_period
      }
    } catch (error) {
      console.error('获取系统设置失败:', error)
    }
  }
  
  if (filterForm.period) {
    loadSummary()
  }
})
</script>

<style scoped>
.results-container {
  padding: 0;
  width: 100%;
  height: 100%;
}

.results-container :deep(.el-card) {
  width: 100%;
  height: 100%;
}

.results-container :deep(.el-card__body) {
  height: calc(100% - 60px);
  display: flex;
  flex-direction: column;
  overflow: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-section {
  flex-shrink: 0;
  margin-bottom: 20px;
}

.table-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.table-section h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 500;
  flex-shrink: 0;
}

.table-section :deep(.el-table) {
  flex: 1;
}

.detail-dialog :deep(.el-dialog__body) {
  max-height: 75vh;
  overflow-y: auto;
}

.table-title {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 15px;
  text-align: center;
  color: #303133;
}

.structure-table {
  font-size: 13px;
}

.structure-table :deep(.el-table__cell) {
  padding: 8px 0;
}

.structure-table :deep(.cell) {
  padding: 0 8px;
  line-height: 1.5;
}

.dimension-name {
  font-weight: 600;
}

.ratio-text {
  font-size: 13px;
  margin-left: 4px;
}
</style>
