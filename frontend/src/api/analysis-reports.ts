/**
 * 科室运营分析报告 API
 */
import request from '@/utils/request'

// ==================== 类型定义 ====================

/**
 * 分析报告接口
 */
export interface AnalysisReport {
  id: number
  hospital_id: number
  department_id: number
  department_code: string
  department_name: string
  period: string
  current_issues: string | null
  future_plans: string | null
  created_at: string
  updated_at: string
  created_by: number | null
}

/**
 * 创建分析报告接口
 */
export interface AnalysisReportCreate {
  department_id: number
  period: string
  current_issues?: string | null
  future_plans?: string | null
}

/**
 * 更新分析报告接口
 */
export interface AnalysisReportUpdate {
  current_issues?: string | null
  future_plans?: string | null
}

/**
 * 分析报告列表接口
 */
export interface AnalysisReportList {
  total: number
  items: AnalysisReport[]
}

/**
 * 科室主业价值分布项
 */
export interface ValueDistributionItem {
  rank: number
  node_id: number
  dimension_name: string
  value: number
  workload: number
}

/**
 * 科室主业价值分布响应
 */
export interface ValueDistributionResponse {
  items: ValueDistributionItem[]
  total_value: number
  message: string | null
}

/**
 * 科室业务内涵项（单个项目）
 */
export interface BusinessContentItem {
  item_code: string
  item_name: string
  item_category: string | null
  unit_price: string | null
  amount: number
  quantity: number
}

/**
 * 按维度分组的业务内涵
 */
export interface DimensionBusinessContent {
  dimension_name: string
  items: BusinessContentItem[]
}

/**
 * 科室业务内涵响应（按维度分组）
 */
export interface BusinessContentResponse {
  dimensions: DimensionBusinessContent[]
  message: string | null
}

/**
 * 维度下钻明细项
 */
export interface DimensionDrillDownItem {
  period: string
  department_code: string
  department_name: string
  item_code: string
  item_name: string
  item_category: string | null
  unit_price: string | null
  amount: number
  quantity: number
}

/**
 * 维度下钻响应
 */
export interface DimensionDrillDownResponse {
  dimension_name: string
  items: DimensionDrillDownItem[]
  total_amount: number
  total_quantity: number
  message: string | null
}

// ==================== API 方法 ====================

/**
 * 获取分析报告列表
 */
export function getAnalysisReports(params?: {
  page?: number
  size?: number
  period?: string
  department_code?: string
  department_name?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}) {
  return request<AnalysisReportList>({
    url: '/analysis-reports',
    method: 'get',
    params
  })
}

/**
 * 获取分析报告详情
 */
export function getAnalysisReport(id: number) {
  return request<AnalysisReport>({
    url: `/analysis-reports/${id}`,
    method: 'get'
  })
}

/**
 * 创建分析报告
 */
export function createAnalysisReport(data: AnalysisReportCreate) {
  return request<AnalysisReport>({
    url: '/analysis-reports',
    method: 'post',
    data
  })
}

/**
 * 更新分析报告
 */
export function updateAnalysisReport(id: number, data: AnalysisReportUpdate) {
  return request<AnalysisReport>({
    url: `/analysis-reports/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除分析报告
 */
export function deleteAnalysisReport(id: number) {
  return request<void>({
    url: `/analysis-reports/${id}`,
    method: 'delete'
  })
}

/**
 * 获取科室主业价值分布 (Top 10 维度)
 */
export function getValueDistribution(id: number) {
  return request<ValueDistributionResponse>({
    url: `/analysis-reports/${id}/value-distribution`,
    method: 'get'
  })
}

/**
 * 获取科室业务内涵 (Top 20 业务项目)
 */
export function getBusinessContent(id: number) {
  return request<BusinessContentResponse>({
    url: `/analysis-reports/${id}/business-content`,
    method: 'get'
  })
}

/**
 * 获取维度下钻明细（通过任务ID）
 */
export function getDimensionDrillDownByTask(taskId: string, departmentId: number, nodeId: number) {
  return request<DimensionDrillDownResponse>({
    url: '/analysis-reports/dimension-drilldown',
    method: 'get',
    params: {
      task_id: taskId,
      department_id: departmentId,
      node_id: nodeId
    }
  })
}

/**
 * 获取维度下钻明细（通过报告ID）
 */
export function getDimensionDrillDown(reportId: number, nodeId: number) {
  return request<DimensionDrillDownResponse>({
    url: `/analysis-reports/${reportId}/dimension-drilldown/${nodeId}`,
    method: 'get'
  })
}

/**
 * 预览科室主业价值分布（用于新建报告时）
 */
export function previewValueDistribution(departmentId: number, period: string) {
  return request<ValueDistributionResponse>({
    url: '/analysis-reports/preview/value-distribution',
    method: 'get',
    params: {
      department_id: departmentId,
      period: period
    }
  })
}

/**
 * 预览科室业务内涵展示（用于新建报告时）
 */
export function previewBusinessContent(departmentId: number, period: string) {
  return request<BusinessContentResponse>({
    url: '/analysis-reports/preview/business-content',
    method: 'get',
    params: {
      department_id: departmentId,
      period: period
    }
  })
}

/**
 * 预览维度下钻明细（用于新建报告时）
 */
export function previewDimensionDrillDown(departmentId: number, period: string, nodeId: number) {
  return request<DimensionDrillDownResponse>({
    url: '/analysis-reports/preview/dimension-drilldown',
    method: 'get',
    params: {
      department_id: departmentId,
      period: period,
      node_id: nodeId
    }
  })
}
