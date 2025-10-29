/**
 * 计算流程管理API
 */
import request from '@/utils/request'

// 类型定义
export interface CalculationWorkflow {
  id: number
  version_id: number
  version_name?: string
  name: string
  description?: string
  is_active: boolean
  step_count: number
  created_at: string
  updated_at: string
}

export interface CalculationStep {
  id: number
  workflow_id: number
  workflow_name?: string
  name: string
  description?: string
  code_type: 'python' | 'sql'
  code_content: string
  data_source_id?: number
  data_source_name?: string
  python_env?: string
  sort_order: number
  is_enabled: boolean
  created_at: string
  updated_at: string
}

export interface WorkflowListParams {
  version_id?: number
  page?: number
  size?: number
  keyword?: string
}

export interface WorkflowCreateData {
  version_id: number
  name: string
  description?: string
  is_active?: boolean
}

export interface WorkflowUpdateData {
  name?: string
  description?: string
  is_active?: boolean
}

export interface WorkflowCopyData {
  name: string
  description?: string
}

export interface StepCreateData {
  workflow_id: number
  name: string
  description?: string
  code_type: 'python' | 'sql'
  code_content: string
  data_source_id?: number
  python_env?: string
  is_enabled?: boolean
  sort_order?: number
}

export interface StepUpdateData {
  name?: string
  description?: string
  code_type?: 'python' | 'sql'
  code_content?: string
  data_source_id?: number
  python_env?: string
  is_enabled?: boolean
}

export interface TestCodeData {
  test_params?: Record<string, any>
}

// 计算流程API
export const calculationWorkflowApi = {
  // 获取计算流程列表
  getList(params?: WorkflowListParams) {
    return request.get<{ total: number; items: CalculationWorkflow[] }>(
      '/calculation-workflows',
      { params }
    )
  },

  // 创建计算流程
  create(data: WorkflowCreateData) {
    return request.post<CalculationWorkflow>('/calculation-workflows', data)
  },

  // 获取计算流程详情
  getDetail(id: number) {
    return request.get<CalculationWorkflow>(`/calculation-workflows/${id}`)
  },

  // 更新计算流程
  update(id: number, data: WorkflowUpdateData) {
    return request.put<CalculationWorkflow>(`/calculation-workflows/${id}`, data)
  },

  // 删除计算流程
  delete(id: number) {
    return request.delete(`/calculation-workflows/${id}`)
  },

  // 复制计算流程
  copy(id: number, data: WorkflowCopyData) {
    return request.post<{ id: number; name: string; step_count: number }>(
      `/calculation-workflows/${id}/copy`,
      data
    )
  }
}

// 计算步骤API
export const calculationStepApi = {
  // 获取计算步骤列表
  getList(workflowId: number) {
    return request.get<{ total: number; items: CalculationStep[] }>(
      '/calculation-steps',
      { params: { workflow_id: workflowId } }
    )
  },

  // 创建计算步骤
  create(data: StepCreateData) {
    return request.post<CalculationStep>('/calculation-steps', data)
  },

  // 获取计算步骤详情
  getDetail(id: number) {
    return request.get<CalculationStep>(`/calculation-steps/${id}`)
  },

  // 更新计算步骤
  update(id: number, data: StepUpdateData) {
    return request.put<CalculationStep>(`/calculation-steps/${id}`, data)
  },

  // 删除计算步骤
  delete(id: number) {
    return request.delete(`/calculation-steps/${id}`)
  },

  // 上移步骤
  moveUp(id: number) {
    return request.post<{ success: boolean; message: string }>(
      `/calculation-steps/${id}/move-up`
    )
  },

  // 下移步骤
  moveDown(id: number) {
    return request.post<{ success: boolean; message: string }>(
      `/calculation-steps/${id}/move-down`
    )
  },

  // 测试代码
  testCode(id: number, data?: TestCodeData) {
    return request.post<{
      success: boolean
      duration_ms?: number
      result?: any
      error?: string
    }>(`/calculation-steps/${id}/test`, data || {})
  },

  // 测试代码（不需要保存）
  testCodeWithoutSave(data: {
    code_type: string
    code_content: string
    data_source_id?: number
    test_params?: Record<string, any>
  }) {
    return request.post<{
      success: boolean
      duration_ms?: number
      result?: any
      error?: string
    }>('/calculation-steps/test-code', data)
  }
}
