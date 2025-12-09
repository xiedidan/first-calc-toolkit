/**
 * 成本基准管理API
 */
import request from '@/utils/request'

// ==================== 类型定义 ====================

/**
 * 成本基准接口
 */
export interface CostBenchmark {
  id: number
  hospital_id: number
  department_code: string
  department_name: string
  version_id: number
  version_name: string
  dimension_code: string
  dimension_name: string
  benchmark_value: number
  created_at: string
  updated_at: string
}

/**
 * 创建成本基准接口
 */
export interface CostBenchmarkCreate {
  department_code: string
  department_name: string
  version_id: number
  version_name: string
  dimension_code: string
  dimension_name: string
  benchmark_value: number
}

/**
 * 成本基准列表接口
 */
export interface CostBenchmarkList {
  total: number
  items: CostBenchmark[]
}

// ==================== API方法 ====================

/**
 * 获取成本基准列表
 */
export function getCostBenchmarks(params?: {
  page?: number
  size?: number
  version_id?: number
  department_code?: string
  dimension_code?: string
  keyword?: string
}) {
  return request<CostBenchmarkList>({
    url: '/cost-benchmarks',
    method: 'get',
    params
  })
}

/**
 * 获取成本基准详情
 */
export function getCostBenchmark(id: number) {
  return request<CostBenchmark>({
    url: `/cost-benchmarks/${id}`,
    method: 'get'
  })
}

/**
 * 创建成本基准
 */
export function createCostBenchmark(data: CostBenchmarkCreate) {
  return request<CostBenchmark>({
    url: '/cost-benchmarks',
    method: 'post',
    data
  })
}

/**
 * 更新成本基准
 */
export function updateCostBenchmark(id: number, data: Partial<CostBenchmarkCreate>) {
  return request<CostBenchmark>({
    url: `/cost-benchmarks/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除成本基准
 */
export function deleteCostBenchmark(id: number) {
  return request<void>({
    url: `/cost-benchmarks/${id}`,
    method: 'delete'
  })
}

/**
 * 导出成本基准到Excel
 */
export function exportCostBenchmarks(params?: {
  version_id?: number
  department_code?: string
  dimension_code?: string
  keyword?: string
}) {
  return request<Blob>({
    url: '/cost-benchmarks/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}
