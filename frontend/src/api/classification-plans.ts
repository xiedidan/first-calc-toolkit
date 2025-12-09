/**
 * 分类预案管理API
 * @module classification-plans
 */
import request from '@/utils/request'

// 类型定义
export interface PlanItem {
  id: number
  plan_id: number
  charge_item_id: number
  charge_item_name: string
  charge_item_code: string | null
  charge_item_category: string | null
  
  // AI建议
  ai_suggested_dimension_id: number | null
  ai_suggested_dimension_name: string | null
  ai_suggested_dimension_path: string | null
  ai_confidence: number | null
  
  // 用户设置
  user_set_dimension_id: number | null
  user_set_dimension_name: string | null
  user_set_dimension_path: string | null
  is_adjusted: boolean
  
  // 最终维度
  final_dimension_id: number | null
  final_dimension_name: string | null
  final_dimension_path: string | null
  
  // 处理状态
  processing_status: string
  error_message: string | null
  
  created_at: string
  updated_at: string
}

export interface ClassificationPlan {
  id: number
  hospital_id: number
  task_id: number
  plan_name: string | null
  status: string  // draft, submitted
  submitted_at: string | null
  created_at: string
  updated_at: string
  
  // 任务元数据
  task_name: string | null
  model_version_id: number | null
  charge_categories: string[] | null
  
  // 统计信息
  total_items: number
  adjusted_items: number
  low_confidence_items: number
}

export interface SubmitPreviewItem {
  item_id: number
  item_name: string
  dimension_id: number
  dimension_name: string
  dimension_path: string
}

export interface SubmitPreviewOverwriteItem extends SubmitPreviewItem {
  old_dimension_id: number
  old_dimension_name: string
  old_dimension_path: string
}

export interface SubmitPreviewResponse {
  plan_id: number
  plan_name: string | null
  total_items: number
  new_count: number
  overwrite_count: number
  new_items: SubmitPreviewItem[]
  overwrite_items: SubmitPreviewOverwriteItem[]
  warnings: string[]
}

// API函数
export function getClassificationPlans(params: {
  skip?: number
  limit?: number
  status?: string
}) {
  return request({
    url: '/classification-plans',
    method: 'get',
    params
  })
}

export function getClassificationPlanDetail(planId: number) {
  return request({
    url: `/classification-plans/${planId}`,
    method: 'get'
  })
}

export function updateClassificationPlan(planId: number, data: { plan_name?: string }) {
  return request({
    url: `/classification-plans/${planId}`,
    method: 'put',
    data
  })
}

export function deleteClassificationPlan(planId: number) {
  return request({
    url: `/classification-plans/${planId}`,
    method: 'delete'
  })
}

export function getPlanItems(planId: number, params: {
  sort_by?: string
  min_confidence?: number
  max_confidence?: number
  is_adjusted?: boolean
  processing_status?: string
  page?: number
  size?: number
}) {
  return request({
    url: `/classification-plans/${planId}/items`,
    method: 'get',
    params
  })
}

export function updatePlanItem(planId: number, itemId: number, data: { dimension_id: number }) {
  return request({
    url: `/classification-plans/${planId}/items/${itemId}`,
    method: 'put',
    data
  })
}

export function generateSubmitPreview(planId: number) {
  return request({
    url: `/classification-plans/${planId}/preview`,
    method: 'post'
  })
}

export function submitClassificationPlan(planId: number, data: { confirm: boolean }) {
  return request({
    url: `/classification-plans/${planId}/submit`,
    method: 'post',
    data
  })
}
