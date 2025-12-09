import request from '@/utils/request'

export interface MenuItem {
  path: string
  name: string
  children?: MenuItem[]
}

export type RoleType = 'department_user' | 'hospital_user' | 'admin' | 'maintainer'

export const ROLE_TYPE_DISPLAY: Record<RoleType, string> = {
  department_user: '科室用户',
  hospital_user: '全院用户',
  admin: '管理员',
  maintainer: '维护者'
}

export interface Role {
  id: number
  name: string
  code: string
  role_type: RoleType
  role_type_display?: string
  menu_permissions?: string[]
  description?: string
  user_count?: number
  created_at: string
  updated_at?: string
}

export interface RoleCreate {
  name: string
  code: string
  role_type: RoleType
  menu_permissions?: string[]
  description?: string
}

export interface RoleUpdate {
  name?: string
  role_type?: RoleType
  menu_permissions?: string[]
  description?: string
}

export interface RoleListResponse {
  total: number
  items: Role[]
}

// 获取系统菜单列表
export function getSystemMenus() {
  return request.get<MenuItem[]>('/roles/menus')
}

// 获取角色列表
export function getRoles(params?: { page?: number; size?: number; keyword?: string }) {
  return request.get<RoleListResponse>('/roles', { params })
}

// 获取角色详情
export function getRole(id: number) {
  return request.get<Role>(`/roles/${id}`)
}

// 创建角色
export function createRole(data: RoleCreate) {
  return request.post<Role>('/roles', data)
}

// 更新角色
export function updateRole(id: number, data: RoleUpdate) {
  return request.put<Role>(`/roles/${id}`, data)
}

// 删除角色
export function deleteRole(id: number) {
  return request.delete(`/roles/${id}`)
}
