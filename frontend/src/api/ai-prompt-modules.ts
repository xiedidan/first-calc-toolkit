/**
 * AI提示词模块配置API - 智能问数系统
 * 支持按功能模块配置独立的提示词，优化不同场景的AI响应质量
 */
import request from '@/utils/request'

const API_BASE = '/ai-prompt-modules'

// ============ 类型定义 ============

/** AI接口简要信息 */
export interface AIInterfaceInfo {
  id: number
  name: string
  model_name: string
  is_active: boolean
}

/** 占位符定义 */
export interface PlaceholderInfo {
  name: string
  description: string
  example?: string
}

/** 提示词模块配置 */
export interface AIPromptModule {
  id: number
  hospital_id: number
  module_code: string
  module_name: string
  description: string | null
  ai_interface_id: number | null
  ai_interface: AIInterfaceInfo | null
  temperature: number
  placeholders: PlaceholderInfo[]
  system_prompt: string | null
  user_prompt: string
  created_at: string
  updated_at: string
  is_configured: boolean
}

/** 更新提示词模块请求 */
export interface AIPromptModuleUpdate {
  ai_interface_id?: number | null
  temperature?: number
  system_prompt?: string | null
  user_prompt?: string
}

/** 提示词模块列表响应 */
export interface AIPromptModuleListResponse {
  items: AIPromptModule[]
  total: number
}

// ============ 模块代码常量 ============

/** 提示词模块代码 */
export const PromptModuleCode = {
  /** 智能分类分级 */
  CLASSIFICATION: 'classification',
  /** 业务价值报表-当前存在问题 */
  REPORT_ISSUES: 'report_issues',
  /** 业务价值报表-未来发展计划 */
  REPORT_PLANS: 'report_plans',
  /** 智能问数系统-指标口径查询 */
  QUERY_CALIBER: 'query_caliber',
  /** 智能问数系统-查询数据生成 */
  QUERY_DATA: 'query_data',
  /** 智能问数系统-SQL代码编写 */
  QUERY_SQL: 'query_sql',
} as const

export type PromptModuleCodeType = typeof PromptModuleCode[keyof typeof PromptModuleCode]

/** 模块分组（用于UI展示） */
export const ModuleGroups = [
  {
    name: '智能分类分级',
    modules: [PromptModuleCode.CLASSIFICATION],
  },
  {
    name: '业务价值报表',
    modules: [PromptModuleCode.REPORT_ISSUES, PromptModuleCode.REPORT_PLANS],
  },
  {
    name: '智能问数系统',
    modules: [PromptModuleCode.QUERY_CALIBER, PromptModuleCode.QUERY_DATA, PromptModuleCode.QUERY_SQL],
  },
]

// ============ API函数 ============

/**
 * 获取所有提示词模块配置
 */
export const getPromptModules = async (): Promise<AIPromptModuleListResponse> => {
  const res: any = await request.get(API_BASE)
  return res.data || res
}

/**
 * 获取指定模块的提示词配置
 */
export const getPromptModule = async (moduleCode: string): Promise<AIPromptModule> => {
  const res: any = await request.get(`${API_BASE}/${moduleCode}`)
  return res.data || res
}

/**
 * 更新提示词模块配置
 */
export const updatePromptModule = async (moduleCode: string, data: AIPromptModuleUpdate): Promise<AIPromptModule> => {
  const res: any = await request.put(`${API_BASE}/${moduleCode}`, data)
  return res.data || res
}
