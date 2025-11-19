/**
 * User management API
 */
import request from '@/utils/request'
import type { UserInfo } from './auth'

export interface UserListParams {
  page?: number
  size?: number
  keyword?: string
}

export interface UserListResponse {
  total: number
  items: UserInfo[]
}

export interface CreateUserData {
  username: string
  name: string
  email?: string
  password: string
  role: 'admin' | 'user'
  hospital_id?: number
}

export interface UpdateUserData {
  name?: string
  email?: string
  password?: string
  status?: string
  role?: 'admin' | 'user'
  hospital_id?: number
}

/**
 * Get user list
 */
export function getUserList(params: UserListParams) {
  return request<UserListResponse>({
    url: '/users',
    method: 'get',
    params
  })
}

/**
 * Get user by ID
 */
export function getUser(id: number) {
  return request<UserInfo>({
    url: `/users/${id}`,
    method: 'get'
  })
}

/**
 * Create user
 */
export function createUser(data: CreateUserData) {
  return request<UserInfo>({
    url: '/users',
    method: 'post',
    data
  })
}

/**
 * Update user
 */
export function updateUser(id: number, data: UpdateUserData) {
  return request<UserInfo>({
    url: `/users/${id}`,
    method: 'put',
    data
  })
}

/**
 * Delete user
 */
export function deleteUser(id: number) {
  return request({
    url: `/users/${id}`,
    method: 'delete'
  })
}
