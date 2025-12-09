/**
 * Data Issue API
 */
import request from '@/utils/request'

export type ProcessingStage = 'not_started' | 'in_progress' | 'resolved' | 'confirmed'

export interface DataIssue {
  id: number
  title: string
  description: string
  reporter: string
  reporter_user_id?: number
  assignee?: string
  assignee_user_id?: number
  processing_stage: ProcessingStage
  resolution?: string
  hospital_id: number
  created_at: string
  resolved_at?: string
  updated_at: string
}

export interface DataIssueListParams {
  page?: number
  size?: number
  keyword?: string
  processing_stage?: ProcessingStage
}

export interface DataIssueListResponse {
  total: number
  items: DataIssue[]
}

export interface CreateDataIssueData {
  title: string
  description: string
  reporter: string
  reporter_user_id?: number
  assignee?: string
  assignee_user_id?: number
  processing_stage?: ProcessingStage
  resolution?: string
}

export interface UpdateDataIssueData {
  title?: string
  description?: string
  reporter?: string
  reporter_user_id?: number
  assignee?: string
  assignee_user_id?: number
  processing_stage?: ProcessingStage
  resolution?: string
}

/**
 * Get data issue list
 */
export function getDataIssueList(params: DataIssueListParams) {
  return request<DataIssueListResponse>({
    url: '/data-issues',
    method: 'get',
    params
  })
}

/**
 * Get data issue by ID
 */
export function getDataIssue(id: number) {
  return request<DataIssue>({
    url: `/data-issues/${id}`,
    method: 'get'
  })
}

/**
 * Create data issue
 */
export function createDataIssue(data: CreateDataIssueData) {
  return request<DataIssue>({
    url: '/data-issues',
    method: 'post',
    data
  })
}

/**
 * Update data issue
 */
export function updateDataIssue(id: number, data: UpdateDataIssueData) {
  return request<DataIssue>({
    url: `/data-issues/${id}`,
    method: 'put',
    data
  })
}

/**
 * Delete data issue
 */
export function deleteDataIssue(id: number) {
  return request({
    url: `/data-issues/${id}`,
    method: 'delete'
  })
}
