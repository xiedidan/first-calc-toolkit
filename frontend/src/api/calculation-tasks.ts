/**
 * 计算任务 API
 */
import request from '@/utils/request'

export interface CalculationTask {
  task_id: string
  batch_id?: string
  model_version_id: number
  workflow_id?: number
  workflow_name?: string
  period: string
  status: string
  progress: number
  description?: string
  created_at: string
  completed_at?: string
  error_message?: string
}

export interface CalculationTaskCreate {
  model_version_id: number
  workflow_id?: number
  period: string
  department_ids?: number[]
  description?: string
  batch_id?: string
}

export interface CalculationTaskListResponse {
  total: number
  items: CalculationTask[]
}

/**
 * 获取计算任务列表
 */
export function getCalculationTasks(params: {
  page?: number
  size?: number
  status?: string
  model_version_id?: number
  period?: string
}) {
  return request({
    url: '/calculation/tasks',
    method: 'get',
    params
  })
}

/**
 * 获取计算任务详情
 */
export function getCalculationTask(taskId: string) {
  return request({
    url: `/calculation/tasks/${taskId}`,
    method: 'get'
  })
}

/**
 * 根据批次ID获取同批次的所有任务
 */
export function getTasksByBatch(batchId: string) {
  return request({
    url: `/calculation/tasks/batch/${batchId}`,
    method: 'get'
  })
}

/**
 * 创建计算任务
 */
export function createCalculationTask(data: CalculationTaskCreate) {
  return request({
    url: '/calculation/tasks',
    method: 'post',
    data,
    timeout: 120000 // 设置超时时间为2分钟
  })
}

/**
 * 取消计算任务
 */
export function cancelCalculationTask(taskId: string) {
  return request({
    url: `/calculation/tasks/${taskId}/cancel`,
    method: 'post'
  })
}


export interface BatchInfo {
  batch_id: string
  task_count: number
  periods: string[]
  created_at: string
  model_version_id: number
  model_version_name?: string
}

export interface BatchListResponse {
  total: number
  items: BatchInfo[]
}

/**
 * 获取批次列表
 */
export function getBatchList(params: {
  model_version_id?: number
  page?: number
  size?: number
}) {
  return request({
    url: '/calculation/batches',
    method: 'get',
    params
  })
}

/**
 * 导出批次报表
 */
export function exportBatchReports(batchId: string) {
  return request({
    url: `/calculation/results/export/batch/${batchId}`,
    method: 'get',
    responseType: 'blob'
  })
}
