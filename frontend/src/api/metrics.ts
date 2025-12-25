/**
 * 指标API - 智能问数系统
 * 具有业务含义的数据度量单位管理
 */
import request from '@/utils/request'

const API_BASE = '/metrics'

// ============ 类型定义 ============

/** 指标类型 */
export type MetricType = 'atomic' | 'composite'

/** 关联类型 */
export type RelationType = 'component' | 'derived' | 'related'

/** 指标 */
export interface Metric {
  id: number
  topic_id: number
  topic_name: string | null
  project_id: number | null
  project_name: string | null
  name_cn: string
  name_en: string | null
  metric_type: MetricType
  metric_type_display: string
  metric_level: string | null
  business_caliber: string | null
  technical_caliber: string | null
  source_tables: string[] | null
  dimension_tables: string[] | null
  dimensions: string[] | null
  data_source_id: number | null
  data_source_name: string | null
  sort_order: number
  created_at: string
  updated_at: string
  related_metric_count: number
}

/** 创建指标请求 */
export interface MetricCreate {
  topic_id: number
  name_cn: string
  name_en?: string
  metric_type?: MetricType
  metric_level?: string
  business_caliber?: string
  technical_caliber?: string
  source_tables?: string[]
  dimension_tables?: string[]
  dimensions?: string[]
  data_source_id?: number
  sort_order?: number
}

/** 更新指标请求 */
export interface MetricUpdate {
  topic_id?: number
  name_cn?: string
  name_en?: string
  metric_type?: MetricType
  metric_level?: string
  business_caliber?: string
  technical_caliber?: string
  source_tables?: string[]
  dimension_tables?: string[]
  dimensions?: string[]
  data_source_id?: number
  sort_order?: number
}

/** 指标列表响应 */
export interface MetricListResponse {
  items: Metric[]
  total: number
  page: number
  size: number
}

/** 指标搜索参数 */
export interface MetricSearchParams {
  keyword?: string
  project_id?: number
  topic_id?: number
  metric_type?: MetricType
  page?: number
  size?: number
}

/** 指标树节点 */
export interface MetricTreeNode {
  id: number
  name: string
  node_type: 'project' | 'topic' | 'metric'
  sort_order: number
  description?: string | null
  project_id?: number | null
  topic_id?: number | null
  metric_type?: MetricType | null
  metric_type_display?: string | null
  children?: MetricTreeNode[] | null
}

/** 指标树响应 */
export interface MetricTreeResponse {
  items: MetricTreeNode[]
  total_projects: number
  total_topics: number
  total_metrics: number
}

/** 指标关联 */
export interface MetricRelation {
  id: number
  source_metric_id: number
  source_metric_name: string | null
  target_metric_id: number
  target_metric_name: string | null
  relation_type: RelationType
  relation_type_display: string
  created_at: string
}

/** 创建指标关联请求 */
export interface MetricRelationCreate {
  target_metric_id: number
  relation_type?: RelationType
}

/** 指标关联列表响应 */
export interface MetricRelationListResponse {
  items: MetricRelation[]
  total: number
  as_source_count: number
  as_target_count: number
}

/** 受影响的指标 */
export interface AffectedMetric {
  id: number
  name_cn: string
  topic_name: string | null
  project_name: string | null
  relation_type: RelationType
}

/** 受影响的指标列表响应 */
export interface AffectedMetricsResponse {
  items: AffectedMetric[]
  total: number
  can_delete: boolean
}

// ============ API函数 ============

/**
 * 获取指标树结构
 * 需求 7.1: 当用户查看指标树时，指标资产管理模块应显示多根树结构
 */
export const getMetricTree = async (): Promise<MetricTreeResponse> => {
  const res = await request.get(`${API_BASE}/tree`)
  return res.data
}

/**
 * 获取指标列表（支持搜索和筛选）
 * 需求 8.1: 当用户点击树中的指标时，指标资产管理模块应在右侧显示指标详情面板
 */
export const getMetrics = async (params?: MetricSearchParams): Promise<MetricListResponse> => {
  const res = await request.get(API_BASE, { params })
  return res.data
}

/**
 * 获取指标详情
 * 需求 8.1: 当用户点击树中的指标时，指标资产管理模块应在右侧显示指标详情面板
 */
export const getMetric = async (id: number): Promise<Metric> => {
  const res = await request.get(`${API_BASE}/${id}`)
  return res.data
}

/**
 * 创建指标
 * 需求 8.5: 当用户创建新指标时，指标资产管理模块应将其添加到所选主题下并设置默认值
 */
export const createMetric = async (data: MetricCreate): Promise<Metric> => {
  const res = await request.post(API_BASE, data)
  return res.data
}

/**
 * 更新指标
 * 需求 8.2, 8.3: 当用户编辑指标业务属性/技术属性时，指标资产管理模块应允许编辑相关字段
 * 需求 8.4: 当用户保存指标更改时，指标资产管理模块应验证必填字段并持久化更改
 */
export const updateMetric = async (id: number, data: MetricUpdate): Promise<Metric> => {
  const res = await request.put(`${API_BASE}/${id}`, data)
  return res.data
}

/**
 * 删除指标
 * 需求 9.4: 当用户尝试删除被其他指标关联的指标时，应在删除前显示受影响的指标列表
 */
export const deleteMetric = async (id: number, force: boolean = false): Promise<void> => {
  await request.delete(`${API_BASE}/${id}`, { params: { force } })
}

/**
 * 重新排序指标
 * 需求 7.4: 当用户对同级节点重新排序时，指标资产管理模块应更新排序顺序并持久化更改
 */
export const reorderMetrics = async (topicId: number, metricIds: number[]): Promise<void> => {
  await request.put(`${API_BASE}/reorder`, { topic_id: topicId, metric_ids: metricIds })
}

// ============ 指标关联API ============

/**
 * 获取指标的关联列表
 * 需求 9.1: 当用户添加关联指标时，指标资产管理模块应允许从现有指标中选择并保存关联关系
 * 需求 9.2: 当用户查看复合指标时，指标资产管理模块应显示所有关联的原子指标
 */
export const getMetricRelations = async (metricId: number): Promise<MetricRelationListResponse> => {
  const res = await request.get(`${API_BASE}/${metricId}/relations`)
  return res.data
}

/**
 * 添加指标关联
 * 需求 9.1: 当用户添加关联指标时，指标资产管理模块应允许从现有指标中选择并保存关联关系
 */
export const createMetricRelation = async (metricId: number, data: MetricRelationCreate): Promise<MetricRelation> => {
  const res = await request.post(`${API_BASE}/${metricId}/relations`, data)
  return res.data
}

/**
 * 删除指标关联
 * 需求 9.3: 当用户移除指标关联时，指标资产管理模块应删除关联关系但不影响指标本身
 */
export const deleteMetricRelation = async (metricId: number, relatedId: number): Promise<void> => {
  await request.delete(`${API_BASE}/${metricId}/relations/${relatedId}`)
}

/**
 * 获取受影响的指标列表（删除前检查）
 * 需求 9.4: 当用户尝试删除被其他指标关联的指标时，应在删除前显示受影响的指标列表
 */
export const getAffectedMetrics = async (metricId: number): Promise<AffectedMetricsResponse> => {
  const res = await request.get(`${API_BASE}/${metricId}/affected`)
  return res.data
}
