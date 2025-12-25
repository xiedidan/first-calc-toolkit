/**
 * AI接口配置API - 智能问数系统
 * 支持多AI接口管理，按模块分配不同的AI服务
 */
import request from '@/utils/request'

const API_BASE = '/ai-interfaces'

// ============ 类型定义 ============

/** AI接口配置 */
export interface AIInterface {
  id: number
  hospital_id: number
  name: string
  api_endpoint: string
  model_name: string
  api_key_masked: string
  call_delay: number
  daily_limit: number
  is_active: boolean
  created_at: string
  updated_at: string
  referenced_modules: string[]
}

/** 创建AI接口请求 */
export interface AIInterfaceCreate {
  name: string
  api_endpoint: string
  model_name: string
  api_key: string
  call_delay?: number
  daily_limit?: number
  is_active?: boolean
}

/** 更新AI接口请求 */
export interface AIInterfaceUpdate {
  name?: string
  api_endpoint?: string
  model_name?: string
  api_key?: string
  call_delay?: number
  daily_limit?: number
  is_active?: boolean
}

/** 测试AI接口请求 */
export interface AIInterfaceTestRequest {
  test_message?: string
}

/** 使用自定义配置测试AI接口请求 */
export interface AIInterfaceTestConfigRequest {
  api_endpoint: string
  model_name: string
  api_key?: string
  interface_id?: number
  test_message?: string
}

/** 测试AI接口响应 */
export interface AIInterfaceTestResponse {
  success: boolean
  response_content?: string
  response_time?: number
  error_message?: string
}

/** AI接口列表响应 */
export interface AIInterfaceListResponse {
  items: AIInterface[]
  total: number
}

// ============ API函数 ============

/**
 * 获取AI接口列表
 */
export const getAIInterfaces = async (): Promise<AIInterfaceListResponse> => {
  return await request.get(API_BASE)
}

/**
 * 获取AI接口详情
 */
export const getAIInterface = async (id: number): Promise<AIInterface> => {
  return await request.get(`${API_BASE}/${id}`)
}

/**
 * 创建AI接口
 */
export const createAIInterface = async (data: AIInterfaceCreate): Promise<AIInterface> => {
  return await request.post(API_BASE, data)
}

/**
 * 更新AI接口
 */
export const updateAIInterface = async (id: number, data: AIInterfaceUpdate): Promise<AIInterface> => {
  return await request.put(`${API_BASE}/${id}`, data)
}

/**
 * 删除AI接口
 */
export const deleteAIInterface = async (id: number): Promise<void> => {
  await request.delete(`${API_BASE}/${id}`)
}

/**
 * 测试AI接口连接（已保存的接口）
 */
export const testAIInterface = async (id: number, data?: AIInterfaceTestRequest): Promise<AIInterfaceTestResponse> => {
  return await request.post(`${API_BASE}/${id}/test`, data || {})
}

/**
 * 使用自定义配置测试AI接口（用于保存前测试）
 */
export const testAIInterfaceConfig = async (data: AIInterfaceTestConfigRequest): Promise<AIInterfaceTestResponse> => {
  return await request.post(`${API_BASE}/test-config`, data)
}
