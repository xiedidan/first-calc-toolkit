/**
 * 内含式收费管理API
 */
import request from '@/utils/request'

export interface DimInclusiveFee {
  id: number
  item_code: string
  item_name: string | null
  cost: number
  created_at: string
  updated_at: string
}

export interface DimInclusiveFeeListResponse {
  items: DimInclusiveFee[]
  total: number
  page: number
  size: number
}

export interface DimInclusiveFeeCreate {
  item_code: string
  item_name?: string
  cost: number
}

export interface DimInclusiveFeeUpdate {
  item_code?: string
  item_name?: string
  cost?: number
}

/**
 * 获取内含式收费列表
 */
export function getInclusiveFees(params: {
  page?: number
  size?: number
  keyword?: string
}): Promise<DimInclusiveFeeListResponse> {
  return request.get('/dim-inclusive-fees', { params })
}

/**
 * 获取单个内含式收费
 */
export function getInclusiveFee(id: number): Promise<DimInclusiveFee> {
  return request.get(`/dim-inclusive-fees/${id}`)
}

/**
 * 创建内含式收费
 */
export function createInclusiveFee(data: DimInclusiveFeeCreate): Promise<DimInclusiveFee> {
  return request.post('/dim-inclusive-fees', data)
}

/**
 * 更新内含式收费
 */
export function updateInclusiveFee(id: number, data: DimInclusiveFeeUpdate): Promise<DimInclusiveFee> {
  return request.put(`/dim-inclusive-fees/${id}`, data)
}

/**
 * 删除内含式收费
 */
export function deleteInclusiveFee(id: number): Promise<{ message: string }> {
  return request.delete(`/dim-inclusive-fees/${id}`)
}
