/**
 * AI提示词配置API
 */
import request from '@/utils/request'

const API_BASE = '/ai-prompt-config'

/**
 * 提示词分类信息
 */
export interface AIPromptCategoryInfo {
  category: string
  name: string
  description: string
  placeholders: string[]
}

/**
 * 提示词配置
 */
export interface AIPromptConfig {
  id: number | null
  hospital_id: number
  category: string
  system_prompt: string | null
  user_prompt: string
  created_at: string | null
  updated_at: string | null
}

/**
 * 保存提示词配置请求
 */
export interface AIPromptConfigSave {
  system_prompt?: string | null
  user_prompt: string
}

/**
 * 报告AI生成请求
 */
export interface ReportAIGenerateRequest {
  report_id: number
  category: 'report_issues' | 'report_plans'
}

/**
 * 报告AI生成响应
 */
export interface ReportAIGenerateResponse {
  success: boolean
  content: string | null
  error: string | null
  duration: number | null
}

/**
 * 获取所有提示词分类信息
 */
export async function getPromptCategories(): Promise<AIPromptCategoryInfo[]> {
  const res: any = await request.get(`${API_BASE}/categories`)
  return res.categories
}

/**
 * 获取所有分类的提示词配置
 */
export async function getAllPromptConfigs(): Promise<AIPromptConfig[]> {
  const res: any = await request.get(API_BASE)
  return res.data
}

/**
 * 获取指定分类的提示词配置
 */
export async function getPromptConfig(category: string): Promise<AIPromptConfig> {
  const res: any = await request.get(`${API_BASE}/${category}`)
  return res.data
}

/**
 * 保存指定分类的提示词配置
 */
export async function savePromptConfig(
  category: string,
  data: AIPromptConfigSave
): Promise<AIPromptConfig> {
  const res: any = await request.post(`${API_BASE}/${category}`, data)
  return res.data
}

/**
 * 使用AI生成报告内容
 */
export async function generateReportContent(
  data: ReportAIGenerateRequest
): Promise<ReportAIGenerateResponse> {
  const res: any = await request.post(`${API_BASE}/generate/report`, data)
  return res.data
}
