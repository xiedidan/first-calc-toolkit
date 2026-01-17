<template>
  <div class="calculation-tasks-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>计算任务管理</span>
          <el-button type="primary" @click="showCreateDialog">创建计算任务</el-button>
        </div>
      </template>
      <el-table :data="tasks" v-loading="loading" stripe>
        <el-table-column prop="task_id" label="任务ID" width="280" />
        <el-table-column prop="period" label="计算周期" width="120" />
        <el-table-column label="模型版本" width="200">
          <template #default="{ row }">
            {{ getVersionName(row.model_version_id) }}
          </template>
        </el-table-column>
        <el-table-column label="计算流程" width="200">
          <template #default="{ row }">
            {{ row.workflow_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="批次" width="240">
          <template #default="{ row }">
            <span v-if="row.batch_id" class="batch-id">{{ row.batch_id }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="150">
          <template #default="{ row }">
            <el-progress :percentage="Number(row.progress)" v-if="row.status === 'running'" />
            <span v-else>{{ row.progress }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="250">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewResults(row)" v-if="row.status === 'completed'">
              查看结果
            </el-button>
            <el-button link type="info" @click="viewLogs(row)">
              执行日志
            </el-button>
            <el-button link type="danger" @click="cancelTask(row)" v-if="row.status === 'pending' || row.status === 'running'">
              取消
            </el-button>
            <el-button link type="warning" @click="retryTask(row)" v-if="row.status === 'failed'">
              重试
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadTasks"
        @current-change="loadTasks"
        class="pagination"
      />
    </el-card>

    <!-- 执行日志对话框 -->
    <el-dialog v-model="logsDialogVisible" title="执行日志" width="900px" append-to-body>
      <div v-loading="logsLoading">
        <el-descriptions :column="2" border style="margin-bottom: 20px">
          <el-descriptions-item label="任务ID">{{ currentTask?.task_id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentTask?.status)">
              {{ getStatusText(currentTask?.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="计算周期">{{ currentTask?.period }}</el-descriptions-item>
          <el-descriptions-item label="进度">{{ currentTask?.progress }}%</el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">
            {{ formatDateTime(currentTask?.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="错误信息" :span="2" v-if="currentTask?.error_message">
            <el-text type="danger">{{ currentTask?.error_message }}</el-text>
          </el-descriptions-item>
        </el-descriptions>

        <el-tabs v-model="activeLogTab">
          <el-tab-pane label="步骤执行详情" name="steps">
            <el-table :data="stepLogs" stripe max-height="400">
              <el-table-column prop="step_id" label="步骤ID" width="80" align="center" />
              <el-table-column label="步骤名称" width="180">
                <template #default="{ row }">
                  {{ getStepName(row.step_id) }}
                </template>
              </el-table-column>
              <el-table-column label="科室" width="150">
                <template #default="{ row }">
                  {{ getDepartmentName(row.department_id) }}
                </template>
              </el-table-column>
              <el-table-column label="状态" width="80" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
                    {{ row.status === 'success' ? '成功' : '失败' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="duration_ms" label="耗时(ms)" width="100" align="right" />
              <el-table-column label="开始时间" width="160">
                <template #default="{ row }">
                  {{ formatDateTime(row.start_time) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80" align="center" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" @click="viewLogDetail(row)">详情</el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <!-- 执行信息列表 -->
            <div style="margin-top: 20px;">
              <el-divider content-position="left">执行信息</el-divider>
              <el-timeline>
                <el-timeline-item
                  v-for="log in stepLogs"
                  :key="log.id"
                  :timestamp="formatDateTime(log.start_time)"
                  :type="log.status === 'success' ? 'success' : 'danger'"
                  placement="top"
                >
                  <el-card>
                    <template #header>
                      <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span>
                          <el-tag :type="log.status === 'success' ? 'success' : 'danger'" size="small" style="margin-right: 8px;">
                            {{ log.status === 'success' ? '成功' : '失败' }}
                          </el-tag>
                          {{ getStepName(log.step_id) }} - {{ getDepartmentName(log.department_id) }}
                        </span>
                        <span style="color: #909399; font-size: 12px;">耗时: {{ log.duration_ms }}ms</span>
                      </div>
                    </template>
                    <div :style="{ color: log.status === 'success' ? '#67c23a' : '#f56c6c' }">
                      {{ log.execution_info || '无执行信息' }}
                    </div>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="任务信息" name="info">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="任务ID">{{ currentTask?.task_id }}</el-descriptions-item>
              <el-descriptions-item label="模型版本">
                {{ getVersionName(currentTask?.model_version_id) }}
              </el-descriptions-item>
              <el-descriptions-item label="计算流程">
                {{ getWorkflowName(currentTask?.workflow_id) }}
              </el-descriptions-item>
              <el-descriptions-item label="计算周期">{{ currentTask?.period }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="getStatusType(currentTask?.status)">
                  {{ getStatusText(currentTask?.status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="进度">{{ currentTask?.progress }}%</el-descriptions-item>
              <el-descriptions-item label="创建时间">
                {{ formatDateTime(currentTask?.created_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="开始时间">
                {{ formatDateTime(currentTask?.started_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="完成时间">
                {{ formatDateTime(currentTask?.completed_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="任务描述">
                {{ currentTask?.description || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="任务错误信息" v-if="currentTask?.error_message">
                <el-text type="danger">{{ currentTask?.error_message }}</el-text>
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>

    <!-- 日志详情对话框 -->
    <el-dialog v-model="logDetailVisible" title="步骤执行详情" width="800px" append-to-body>
      <el-descriptions :column="1" border v-if="currentLog">
        <el-descriptions-item label="步骤名称">
          {{ getStepName(currentLog.step_id) }}
        </el-descriptions-item>
        <el-descriptions-item label="科室">
          {{ getDepartmentName(currentLog.department_id) }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentLog.status === 'success' ? 'success' : 'danger'">
            {{ currentLog.status === 'success' ? '成功' : '失败' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="耗时">{{ currentLog.duration_ms }} ms</el-descriptions-item>
        <el-descriptions-item label="开始时间">
          {{ formatDateTime(currentLog.start_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="结束时间">
          {{ formatDateTime(currentLog.end_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="执行信息">
          <el-text :type="currentLog.status === 'success' ? 'success' : 'danger'">
            {{ currentLog.execution_info || '无执行信息' }}
          </el-text>
        </el-descriptions-item>
        <el-descriptions-item label="执行结果" v-if="currentLog.result_data">
          <el-input
            type="textarea"
            :value="JSON.stringify(currentLog.result_data, null, 2)"
            :rows="15"
            readonly
          />
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 创建任务对话框 -->
    <el-dialog v-model="createDialogVisible" title="创建计算任务" width="600px" append-to-body>
      <el-form :model="taskForm" :rules="taskRules" ref="taskFormRef" label-width="120px">
        <el-form-item label="模型版本" prop="model_version_id">
          <el-select v-model="taskForm.model_version_id" placeholder="请选择模型版本" @change="onVersionChange">
            <el-option
              v-for="version in versions"
              :key="version.id"
              :label="version.name"
              :value="version.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="计算流程" prop="workflow_id">
          <el-select v-model="taskForm.workflow_id" placeholder="请选择计算流程">
            <el-option
              v-for="workflow in filteredWorkflows"
              :key="workflow.id"
              :label="workflow.name"
              :value="workflow.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="计算周期">
          <el-radio-group v-model="taskForm.periodMode">
            <el-radio value="single">单月</el-radio>
            <el-radio value="range">范围</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="taskForm.periodMode === 'single'" label=" " prop="period">
          <div style="display: flex; align-items: center;">
            <el-date-picker
              v-model="taskForm.period"
              type="month"
              placeholder="选择月份"
              format="YYYY-MM"
              value-format="YYYY-MM"
              style="width: 140px;"
            />
            <el-checkbox v-model="taskForm.createMomTask" style="margin-left: 16px">
              环比月份
            </el-checkbox>
            <el-checkbox v-model="taskForm.createYoyTask" style="margin-left: 8px">
              同比月份
            </el-checkbox>
          </div>
        </el-form-item>

        <el-form-item v-else label=" " prop="period">
          <div style="display: flex; align-items: center; gap: 10px;">
            <el-date-picker
              v-model="taskForm.startPeriod"
              type="month"
              placeholder="开始月份"
              format="YYYY-MM"
              value-format="YYYY-MM"
              style="width: 140px;"
            />
            <span>至</span>
            <el-date-picker
              v-model="taskForm.endPeriod"
              type="month"
              placeholder="结束月份"
              format="YYYY-MM"
              value-format="YYYY-MM"
              style="width: 140px;"
            />
            <span v-if="rangeMonthCount > 0" style="color: #909399; font-size: 12px; margin-left: 6px;">
              共 {{ rangeMonthCount }} 个月
            </span>
          </div>
        </el-form-item>

        <el-form-item label="科室范围" prop="department_ids">
          <el-select v-model="taskForm.department_ids" multiple placeholder="不选择则计算所有科室">
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.his_name"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="任务描述" prop="description">
          <el-input v-model="taskForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createTask" :loading="submitting">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useRouter } from 'vue-router'
import { getCalculationTasks, createCalculationTask, cancelCalculationTask } from '@/api/calculation-tasks'
import { getModelVersions } from '@/api/model'
import { getCalculationWorkflows } from '@/api/calculation-workflow'
import { getSystemSettings } from '@/api/system-settings'
import request from '@/utils/request'

const router = useRouter()

// 数据
const loading = ref(false)
const tasks = ref<any[]>([])
const versions = ref<any[]>([])
const workflows = ref<any[]>([])
const departments = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
let pollingTimer: number | null = null

// 执行日志相关
const logsDialogVisible = ref(false)
const logsLoading = ref(false)
const currentTask = ref<any>(null)
const stepLogs = ref<any[]>([])
const activeLogTab = ref('steps')
const logDetailVisible = ref(false)
const currentLog = ref<any>(null)

// 创建任务对话框
const createDialogVisible = ref(false)
const submitting = ref(false)
const taskFormRef = ref<FormInstance>()
const taskForm = reactive({
  model_version_id: null as number | null,
  workflow_id: null as number | null,
  periodMode: 'single' as 'single' | 'range',
  period: '',
  startPeriod: '',
  endPeriod: '',
  department_ids: [] as number[],
  description: '',
  createMomTask: false,
  createYoyTask: false
})

const taskRules: FormRules = {
  model_version_id: [{ required: true, message: '请选择模型版本', trigger: 'change' }],
  workflow_id: [{ required: true, message: '请选择计算流程', trigger: 'change' }],
  period: [{ 
    validator: (rule, value, callback) => {
      if (taskForm.periodMode === 'single' && !taskForm.period) {
        callback(new Error('请选择计算周期'))
      } else if (taskForm.periodMode === 'range' && (!taskForm.startPeriod || !taskForm.endPeriod)) {
        callback(new Error('请选择开始和结束月份'))
      } else if (taskForm.periodMode === 'range' && taskForm.startPeriod > taskForm.endPeriod) {
        callback(new Error('开始月份不能大于结束月份'))
      } else {
        callback()
      }
    }, 
    trigger: 'change' 
  }]
}

// 计算属性
const filteredWorkflows = computed(() => {
  if (!taskForm.model_version_id) return []
  return workflows.value.filter(w => w.version_id === taskForm.model_version_id)
})

// 计算范围模式下的月份数量
const rangeMonthCount = computed(() => {
  if (!taskForm.startPeriod || !taskForm.endPeriod) return 0
  if (taskForm.startPeriod > taskForm.endPeriod) return 0
  return getMonthsBetween(taskForm.startPeriod, taskForm.endPeriod).length
})

// 获取两个月份之间的所有月份列表
const getMonthsBetween = (start: string, end: string): string[] => {
  const months: string[] = []
  const [startYear, startMonth] = start.split('-').map(Number)
  const [endYear, endMonth] = end.split('-').map(Number)
  
  let year = startYear
  let month = startMonth
  
  while (year < endYear || (year === endYear && month <= endMonth)) {
    months.push(`${year}-${String(month).padStart(2, '0')}`)
    month++
    if (month > 12) {
      month = 1
      year++
    }
  }
  
  return months
}

// 方法
const loadTasks = async () => {
  loading.value = true
  try {
    const response: any = await getCalculationTasks({
      page: currentPage.value,
      size: pageSize.value
    })
    tasks.value = response.items
    total.value = response.total
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载任务列表失败')
  } finally {
    loading.value = false
  }
}

const loadVersions = async () => {
  try {
    const response: any = await getModelVersions({ skip: 0, limit: 1000 })
    versions.value = response.items || []
  } catch (error: any) {
    ElMessage.error('加载模型版本失败')
    console.error('加载模型版本错误:', error)
  }
}

const loadWorkflows = async () => {
  try {
    const response: any = await getCalculationWorkflows({ page: 1, size: 1000 })
    workflows.value = response.items || []
  } catch (error: any) {
    ElMessage.error('加载计算流程失败')
    console.error('加载计算流程错误:', error)
  }
}

const loadDepartments = async () => {
  try {
    const response: any = await request({
      url: '/departments',
      method: 'get',
      params: { page: 1, size: 1000 }
    })
    departments.value = response.items
  } catch (error: any) {
    ElMessage.error('加载科室列表失败')
  }
}

const showCreateDialog = async () => {
  createDialogVisible.value = true
  taskForm.model_version_id = null
  taskForm.workflow_id = null
  taskForm.periodMode = 'single'
  taskForm.startPeriod = ''
  taskForm.endPeriod = ''
  taskForm.department_ids = []
  taskForm.description = ''
  taskForm.createMomTask = true
  taskForm.createYoyTask = true
  
  // 加载系统设置，获取当期年月
  try {
    const settings = await getSystemSettings()
    taskForm.period = settings.current_period || ''
  } catch (error) {
    taskForm.period = ''
  }
  
  // 确保 workflows 已加载
  if (workflows.value.length === 0) {
    await loadWorkflows()
  }
  if (departments.value.length === 0) {
    loadDepartments()
  }
  
  // 默认选中最新的模型版本（按 created_at 降序，取第一个）
  if (versions.value.length > 0) {
    const sortedVersions = [...versions.value].sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
    taskForm.model_version_id = sortedVersions[0].id
    
    // 默认选中该版本下最新的计算流程
    const versionWorkflows = workflows.value
      .filter(w => w.version_id === taskForm.model_version_id)
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    if (versionWorkflows.length > 0) {
      taskForm.workflow_id = versionWorkflows[0].id
    }
  }
}

const onVersionChange = () => {
  // 切换版本时，自动选中该版本下最新的计算流程
  const versionWorkflows = workflows.value
    .filter(w => w.version_id === taskForm.model_version_id)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  taskForm.workflow_id = versionWorkflows.length > 0 ? versionWorkflows[0].id : null
}

// 计算环比月份（上月）
const getMomPeriod = (period: string) => {
  if (!period) return ''
  const [year, month] = period.split('-').map(Number)
  if (month === 1) {
    return `${year - 1}-12`
  }
  return `${year}-${String(month - 1).padStart(2, '0')}`
}

// 计算同比月份（去年同月）
const getYoyPeriod = (period: string) => {
  if (!period) return ''
  const [year, month] = period.split('-').map(Number)
  return `${year - 1}-${String(month).padStart(2, '0')}`
}

// 生成批次ID
const generateBatchId = () => {
  return `batch-${Date.now()}-${Math.random().toString(36).substring(2, 10)}`
}

const createTask = async () => {
  if (!taskFormRef.value) return
  
  await taskFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      // 生成批次ID，同一次创建的所有任务共享同一个批次ID
      const batchId = generateBatchId()
      
      const baseParams = {
        model_version_id: taskForm.model_version_id!,
        workflow_id: taskForm.workflow_id || undefined,
        department_ids: taskForm.department_ids,
        description: taskForm.description,
        batch_id: batchId  // 所有任务使用同一个批次ID
      }
      
      let taskCount = 0
      
      if (taskForm.periodMode === 'range') {
        // 范围模式：创建所有月份的任务
        const periods = getMonthsBetween(taskForm.startPeriod, taskForm.endPeriod)
        for (const period of periods) {
          try {
            await createCalculationTask({
              ...baseParams,
              period,
              description: baseParams.description || `${period} 批量任务`
            })
            taskCount++
          } catch (e: any) {
            console.warn(`创建 ${period} 任务失败:`, e)
          }
        }
      } else {
        // 单月模式
        // 创建主任务
        await createCalculationTask({
          ...baseParams,
          period: taskForm.period
        })
        taskCount++
        
        // 创建环比月份任务
        if (taskForm.createMomTask) {
          const momPeriod = getMomPeriod(taskForm.period)
          if (momPeriod) {
            try {
              await createCalculationTask({
                ...baseParams,
                period: momPeriod,
                description: baseParams.description ? `${baseParams.description}（环比）` : `${taskForm.period} 环比任务`
              })
              taskCount++
            } catch (e: any) {
              console.warn('创建环比任务失败:', e)
            }
          }
        }
        
        // 创建同比月份任务
        if (taskForm.createYoyTask) {
          const yoyPeriod = getYoyPeriod(taskForm.period)
          if (yoyPeriod) {
            try {
              await createCalculationTask({
                ...baseParams,
                period: yoyPeriod,
                description: baseParams.description ? `${baseParams.description}（同比）` : `${taskForm.period} 同比任务`
              })
              taskCount++
            } catch (e: any) {
              console.warn('创建同比任务失败:', e)
            }
          }
        }
      }
      
      ElMessage.success(`已创建 ${taskCount} 个计算任务（批次: ${batchId.substring(0, 16)}...）`)
      createDialogVisible.value = false
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '创建任务失败')
    } finally {
      submitting.value = false
      // 不管成功还是失败，都刷新任务列表
      loadTasks()
    }
  })
}

const cancelTask = async (task: any) => {
  try {
    await ElMessageBox.confirm('确定要取消该任务吗？', '提示', {
      type: 'warning'
    })
    
    await cancelCalculationTask(task.task_id)
    ElMessage.success('任务已取消')
    loadTasks()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '取消任务失败')
    }
  }
}

const retryTask = async (task: any) => {
  // TODO: 实现重试逻辑
  ElMessage.info('重试功能开发中')
}

const viewResults = (task: any) => {
  router.push({
    name: 'Results',
    query: {
      task_id: task.task_id,
      period: task.period,
      model_version_id: task.model_version_id
    }
  })
}

const viewLogs = async (task: any) => {
  currentTask.value = task
  logsDialogVisible.value = true
  activeLogTab.value = 'steps'
  
  logsLoading.value = true
  try {
    // 获取步骤日志
    const response: any = await request({
      url: `/calculation/tasks/${task.task_id}/logs`,
      method: 'get'
    })
    stepLogs.value = response.logs || []
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载执行日志失败')
  } finally {
    logsLoading.value = false
  }
}

const viewLogDetail = (log: any) => {
  currentLog.value = log
  logDetailVisible.value = true
}

const getStepName = (stepId: number) => {
  // 这里可以从 workflows 中查找步骤名称
  // 简化处理，直接返回步骤ID
  return `步骤 ${stepId}`
}

const getDepartmentName = (deptId: number | null) => {
  if (!deptId) return '全部科室'
  const dept = departments.value.find(d => d.id === deptId)
  return dept?.his_name || `科室 ${deptId}`
}

const getVersionName = (versionId: number) => {
  const version = versions.value.find(v => v.id === versionId)
  return version?.name || '-'
}

const getWorkflowName = (workflowId: number) => {
  if (!workflowId) return '-'
  const workflow = workflows.value.find(w => w.id === workflowId)
  return workflow?.name || '-'
}

const getStatusType = (status: string) => {
  const types: Record<string, any> = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info'
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '排队中',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return texts[status] || status
}

const formatDateTime = (dateTime: string) => {
  if (!dateTime) return '-'
  return new Date(dateTime).toLocaleString('zh-CN')
}

// 启动轮询
const startPolling = () => {
  // 清除已有的定时器
  if (pollingTimer) {
    clearInterval(pollingTimer)
  }
  
  // 每5秒刷新一次任务列表
  pollingTimer = window.setInterval(() => {
    loadTasks()
  }, 5000)
}

// 停止轮询
const stopPolling = () => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
}

// 生命周期
onMounted(() => {
  loadTasks()
  loadVersions()
  startPolling()
})

// 组件卸载时清理定时器
onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.calculation-tasks-container {
  padding: 0;
  width: 100%;
  height: 100%;
}

.calculation-tasks-container :deep(.el-card) {
  width: 100%;
  height: 100%;
}

.calculation-tasks-container :deep(.el-card__body) {
  height: calc(100% - 60px);
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.calculation-tasks-container :deep(.el-table) {
  flex: 1;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
