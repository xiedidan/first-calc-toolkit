/**
 * 业务导向管理API
 */
import request from '@/utils/request'

// ==================== 导向规则 ====================

export interface OrientationRule {
  id: number
  hospital_id: number
  name: string
  category: 'benchmark_ladder' | 'direct_ladder' | 'other'
  description?: string
  created_at: string
  updated_at: string
}

/**
 * 获取导向规则列表
 */
export function getOrientationRules(params?: { 
  skip?: number
  limit?: number
  name?: string
  category?: string
}) {
  return request<{ total: number; items: OrientationRule[] }>({
    url: '/orientation-rules',
    method: 'get',
    params
  })
}

/**
 * 获取导向规则详情
 */
export function getOrientationRule(id: number) {
  return request<OrientationRule>({
    url: `/orientation-rules/${id}`,
    method: 'get'
  })
}
