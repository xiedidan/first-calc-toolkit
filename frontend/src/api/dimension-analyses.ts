/**
 * 维度分析 API
 */
import request from '@/utils/request'

export interface DimensionAnalysis {
  id: number
  hospital_id: number
  department_id: number
  node_id: number
  period: string | null
  content: string
  department_name?: string
  node_name?: string
  created_by?: number
  created_by_name?: string
  updated_by?: number
  updated_by_name?: string
  created_at: string
  updated_at: string
}

export interface DimensionAnalysisCreate {
  department_id: number
  node_id: number
  period?: string | null
  content: string
}

export interface DimensionAnalysisBatchQuery {
  department_id: number
  node_ids: number[]
  period?: string | null
}

export interface DimensionAnalysisBatchResponse {
  current_analyses: Record<string, DimensionAnalysis>
  long_term_analyses: Record<string, DimensionAnalysis>
}

/**
 * 获取单个维度分析
 */
export function getDimensionAnalysis(params: {
  department_id: number
  node_id: number
  period?: string | null
}) {
  return request<DimensionAnalysis>({
    url: '/dimension-analyses',
    method: 'get',
    params,
    silent404: true  // 静默处理404，因为新维度没有分析记录是正常情况
  } as any)
}

/**
 * 批量查询维度分析
 */
export function batchQueryDimensionAnalyses(data: DimensionAnalysisBatchQuery) {
  return request<DimensionAnalysisBatchResponse>({
    url: '/dimension-analyses/batch-query',
    method: 'post',
    data
  })
}

/**
 * 创建或更新维度分析
 */
export function createOrUpdateDimensionAnalysis(data: DimensionAnalysisCreate) {
  return request<DimensionAnalysis>({
    url: '/dimension-analyses',
    method: 'post',
    data
  })
}

/**
 * 更新维度分析
 */
export function updateDimensionAnalysis(id: number, data: { content: string }) {
  return request<DimensionAnalysis>({
    url: `/dimension-analyses/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除维度分析
 */
export function deleteDimensionAnalysis(id: number) {
  return request({
    url: `/dimension-analyses/${id}`,
    method: 'delete'
  })
}

/**
 * 列出维度分析
 */
export function listDimensionAnalyses(params: {
  department_id?: number
  node_id?: number
  period?: string
  analysis_type?: 'current' | 'long_term'
  page?: number
  size?: number
}) {
  return request<DimensionAnalysis[]>({
    url: '/dimension-analyses/list',
    method: 'get',
    params
  })
}

export interface DimensionAnalysisByCodesItem {
  long_term_content: string | null
  current_analyses: Array<{
    period: string
    content: string
  }>
}

/**
 * 根据科室代码和维度代码批量查询维度分析
 */
export function batchQueryByDeptAndDimCodes(
  departmentCodes: string[],
  dimensionCodes: string[]
) {
  const params = new URLSearchParams()
  departmentCodes.forEach(code => params.append('department_codes', code))
  dimensionCodes.forEach(code => params.append('dimension_codes', code))
  
  return request<Record<string, DimensionAnalysisByCodesItem>>({
    url: `/dimension-analyses/batch-query-by-codes?${params.toString()}`,
    method: 'post'
  })
}
