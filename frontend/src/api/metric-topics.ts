/**
 * 指标主题API - 智能问数系统
 * 项目下的一级分类，用于归类指标
 */
import request from '@/utils/request'

const API_BASE = '/metric-topics'

// ============ 类型定义 ============

/** 指标主题 */
export interface MetricTopic {
  id: number
  project_id: number
  project_name: string | null
  name: string
  description: string | null
  sort_order: number
  created_at: string
  updated_at: string
  metric_count: number
}

/** 创建指标主题请求 */
export interface MetricTopicCreate {
  project_id: number
  name: string
  description?: string
  sort_order?: number
}

/** 更新指标主题请求 */
export interface MetricTopicUpdate {
  project_id?: number
  name?: string
  description?: string
  sort_order?: number
}

/** 指标主题列表响应 */
export interface MetricTopicListResponse {
  items: MetricTopic[]
  total: number
}

/** 删除主题响应数据 */
export interface MetricTopicDeleteResult {
  deleted_metrics: number
}

// ============ API函数 ============

/**
 * 获取指标主题列表
 * @param projectId 可选，按项目ID筛选
 * 需求 7.3: 当用户在项目下创建新主题时，指标资产管理模块应将主题添加为所选项目的子节点
 */
export const getMetricTopics = async (projectId?: number): Promise<MetricTopicListResponse> => {
  const params = projectId !== undefined ? { project_id: projectId } : {}
  const res = await request.get(API_BASE, { params })
  return res.data
}

/**
 * 获取指标主题详情
 */
export const getMetricTopic = async (id: number): Promise<MetricTopic> => {
  const res = await request.get(`${API_BASE}/${id}`)
  return res.data
}

/**
 * 创建指标主题
 * 需求 7.3: 当用户在项目下创建新主题时，指标资产管理模块应将主题添加为所选项目的子节点
 */
export const createMetricTopic = async (data: MetricTopicCreate): Promise<MetricTopic> => {
  const res = await request.post(API_BASE, data)
  return res.data
}

/**
 * 更新指标主题
 */
export const updateMetricTopic = async (id: number, data: MetricTopicUpdate): Promise<MetricTopic> => {
  const res = await request.put(`${API_BASE}/${id}`, data)
  return res.data
}

/**
 * 删除指标主题
 * 需求 7.5: 当用户删除项目或主题时，指标资产管理模块应在确认后移除该节点及其所有子节点
 */
export const deleteMetricTopic = async (id: number): Promise<MetricTopicDeleteResult> => {
  const res = await request.delete(`${API_BASE}/${id}`)
  return res.data
}

/**
 * 重新排序指标主题
 * 需求 7.4: 当用户对同级节点重新排序时，指标资产管理模块应更新排序顺序并持久化更改
 */
export const reorderMetricTopics = async (topicIds: number[]): Promise<void> => {
  await request.put(`${API_BASE}/reorder`, { topic_ids: topicIds })
}
