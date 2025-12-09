/**
 * Authentication API
 */
import request from '@/utils/request'

export interface LoginData {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export type RoleType = 'department_user' | 'hospital_user' | 'admin' | 'maintainer'

export interface UserInfo {
  id: number
  username: string
  name: string
  email: string | null
  status: string
  created_at: string
  updated_at: string
  role_id: number
  role_name: string
  role_type: RoleType
  hospital_id?: number
  hospital_name?: string
  department_id?: number
  department_name?: string
  menu_permissions?: string[]
}

/**
 * User login
 */
export function login(data: LoginData) {
  return request<LoginResponse>({
    url: '/auth/login',
    method: 'post',
    data
  })
}

/**
 * Get current user info
 */
export function getCurrentUser() {
  return request<UserInfo>({
    url: '/auth/me',
    method: 'get'
  })
}

/**
 * Logout
 */
export function logout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user_info')
}
