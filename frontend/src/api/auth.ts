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

export interface UserInfo {
  id: number
  username: string
  name: string
  email: string | null
  status: string
  created_at: string
  updated_at: string
  role: 'admin' | 'user'
  hospital_id?: number
  hospital_name?: string
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
