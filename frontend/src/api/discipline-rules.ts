/**
 * 学科规则管理API
 */
import request from '@/utils/request'

export interface DisciplineRule {
  id: number
  department_code: string
  department_name: string
  version_id: number
  version_name?: string
  dimension_code: string
  dimension_name: string
  rule_description?: string
  rule_coefficient: number
  created_at: string
  updated_at: string
}

export interface DisciplineRuleCreate {
  department_code: string
  department_name: string
  version_id: number
  dimension_code: string
  dimension_name: string
  rule_description?: string
  rule_coefficient: number
}

export interface DisciplineRuleUpdate {
  department_code?: string
  department_name?: string
  dimension_code?: string
  dimension_name?: string
  rule_description?: string
  rule_coefficient?: number
}

export interface DisciplineRuleListResponse {
  items: DisciplineRule[]
  total: number
}

export interface DisciplineRuleQueryParams {
  page?: number
  size?: number
  version_id?: number
  department_code?: string
  dimension_code?: string
  keyword?: string
}

/**
 * 获取学科规则列表
 */
export function getDisciplineRules(params: DisciplineRuleQueryParams): Promise<DisciplineRuleListResponse> {
  return request({
    url: '/discipline-rules',
    method: 'get',
    params
  })
}

/**
 * 获取学科规则详情
 */
export function getDisciplineRule(id: number): Promise<DisciplineRule> {
  return request({
    url: `/discipline-rules/${id}`,
    method: 'get'
  })
}

/**
 * 创建学科规则
 */
export function createDisciplineRule(data: DisciplineRuleCreate): Promise<DisciplineRule> {
  return request({
    url: '/discipline-rules',
    method: 'post',
    data
  })
}

/**
 * 更新学科规则
 */
export function updateDisciplineRule(id: number, data: DisciplineRuleUpdate): Promise<DisciplineRule> {
  return request({
    url: `/discipline-rules/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除学科规则
 */
export function deleteDisciplineRule(id: number): Promise<void> {
  return request({
    url: `/discipline-rules/${id}`,
    method: 'delete'
  })
}
