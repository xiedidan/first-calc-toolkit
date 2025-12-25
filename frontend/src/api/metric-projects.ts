/**
 * 指标项目API - 智能问数系统
 * 指标树的根节点管理，用于组织指标
 */
import request from '@/utils/request'

const API_BASE = '/metric-projects'

// ============ 类型定义 ============

/** 指标项目 */
export interface MetricProject {
  id: number
  hospital_id: number
  name: string
  description: string | null
  sort_order: number
  created_at: string
  updated_at: string
  topic_count: number
  metric_count: number
}

/** 创建指标项目请求 */
export interface MetricProjectCreate {
  name: string
  description?: string
  sort_order?: number
}

/** 更新指标项目请求 */
export interface MetricProjectUpdate {
  name?: string
  description?: string
  sort_order?: number
}

/** 指标项目列表响应 */
export interface MetricProjectListResponse {
  items: MetricProject[]
  total: number
}

/** 删除项目响应数据 */
export interface MetricProjectDeleteResult {
  deleted_topics: number
  deleted_metrics: number
}

// ============ API函数 ============

/**
 * 获取指标项目列表
 * 需求 7.2: 当用户创建新项目时，指标资产管理模块应在树中添加新的根节点
 */
export const getMetricProjects = async (): Promise<MetricProjectListResponse> => {
  const res = await request.get(API_BASE)
  return res.data
}

/**
 * 获取指标项目详情
 */
export const getMetricProject = async (id: number): Promise<MetricProject> => {
  const res = await request.get(`${API_BASE}/${id}`)
  return res.data
}

/**
 * 创建指标项目
 * 需求 7.2: 当用户创建新项目时，指标资产管理模块应在树中添加新的根节点
 */
export const createMetricProject = async (data: MetricProjectCreate): Promise<MetricProject> => {
  const res = await request.post(API_BASE, data)
  return res.data
}

/**
 * 更新指标项目
 */
export const updateMetricProject = async (id: number, data: MetricProjectUpdate): Promise<MetricProject> => {
  const res = await request.put(`${API_BASE}/${id}`, data)
  return res.data
}

/**
 * 删除指标项目
 * 需求 7.5: 当用户删除项目或主题时，指标资产管理模块应在确认后移除该节点及其所有子节点
 */
export const deleteMetricProject = async (id: number): Promise<MetricProjectDeleteResult> => {
  const res = await request.delete(`${API_BASE}/${id}`)
  return res.data
}

/**
 * 重新排序指标项目
 * 需求 7.4: 当用户对同级节点重新排序时，指标资产管理模块应更新排序顺序并持久化更改
 */
export const reorderMetricProjects = async (projectIds: number[]): Promise<void> => {
  await request.put(`${API_BASE}/reorder`, { project_ids: projectIds })
}
