/**
 * Hospital API
 */
import request from '@/utils/request'

export interface Hospital {
  id: number
  code: string
  name: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface HospitalCreate {
  code: string
  name: string
  is_active?: boolean
}

export interface HospitalUpdate {
  name: string
  is_active?: boolean
}

export interface HospitalListParams {
  page?: number
  size?: number
  search?: string
  is_active?: boolean
}

export interface HospitalListResponse {
  items: Hospital[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ActivateResponse {
  hospital_id: number
  hospital_name: string
  message: string
}

/**
 * Get accessible hospitals for current user
 */
export function getAccessibleHospitals() {
  return request<Hospital[]>({
    url: '/hospitals/accessible',
    method: 'get'
  })
}

/**
 * Activate hospital
 */
export function activateHospital(id: number) {
  return request<ActivateResponse>({
    url: `/hospitals/${id}/activate`,
    method: 'post'
  })
}

/**
 * Get hospital list (admin only)
 */
export function getHospitals(params?: HospitalListParams) {
  return request<HospitalListResponse>({
    url: '/hospitals',
    method: 'get',
    params
  })
}

/**
 * Get hospital by id (admin only)
 */
export function getHospital(id: number) {
  return request<Hospital>({
    url: `/hospitals/${id}`,
    method: 'get'
  })
}

/**
 * Create hospital (admin only)
 */
export function createHospital(data: HospitalCreate) {
  return request<Hospital>({
    url: '/hospitals',
    method: 'post',
    data
  })
}

/**
 * Update hospital (admin only)
 */
export function updateHospital(id: number, data: HospitalUpdate) {
  return request<Hospital>({
    url: `/hospitals/${id}`,
    method: 'put',
    data
  })
}

/**
 * Delete hospital (admin only)
 */
export function deleteHospital(id: number) {
  return request({
    url: `/hospitals/${id}`,
    method: 'delete'
  })
}
