/**
 * 计算任务 API
 */
import request from '@/utils/request'

export interface CalculationTask {
  task_id: string
  model_version_id: number
  workflow_id?: number
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
