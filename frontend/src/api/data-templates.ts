/**
 * 数据模板管理API
 */
import request from '@/utils/request'

// 类型定义
export interface DataTemplate {
  id: number
  hospital_id: number
  table_name: string
  table_name_cn: string
  description?: string
  is_core: boolean
  sort_order: number
  definition_file_path?: string
  definition_file_name?: string
  sql_file_path?: string
  sql_file_name?: string
  has_definition: boolean
  has_sql: boolean
  created_at: string
  updated_at: string
}

export interface DataTemplateCreate {
  table_name: string
  table_name_cn: string
  description?: string
  is_core?: boolean
  sort_order?: number
}

export interface DataTemplateUpdate {
  table_name_cn?: string
  description?: string
  is_core?: boolean
  sort_order?: number
}

export interface DataTemplateList {
  total: number
  items: DataTemplate[]
}

export interface BatchUploadItem {
  table_name: string
  table_name_cn?: string
  definition_file_name?: string
  sql_file_name?: string
  status: string
  message?: string
}

export interface BatchUploadPreview {
  items: BatchUploadItem[]
  total: number
  matched: number
  partial: number
  unmatched: number
}

export interface BatchUploadResult {
  success_count: number
  failed_count: number
  skipped_count: number
  details: any[]
}

export interface CopyTemplateRequest {
  source_hospital_id: number
  template_ids: number[]
  conflict_strategy: 'skip' | 'overwrite'
}

export interface CopyResult {
  success_count: number
  skipped_count: number
  failed_count: number
  details: any[]
}

export interface HospitalSimple {
  id: number
  code: string
  name: string
}

/**
 * 获取数据模板列表
 */
export function getDataTemplates(params: {
  page?: number
  size?: number
  keyword?: string
  is_core?: boolean
  has_definition?: boolean
  has_sql?: boolean
  sort_by?: string
  sort_order?: string
}) {
  return request<DataTemplateList>({
    url: '/data-templates',
    method: 'get',
    params
  })
}

/**
 * 创建数据模板
 */
export function createDataTemplate(data: DataTemplateCreate) {
  return request<DataTemplate>({
    url: '/data-templates',
    method: 'post',
    data
  })
}

/**
 * 获取数据模板详情
 */
export function getDataTemplate(id: number) {
  return request<DataTemplate>({
    url: `/data-templates/${id}`,
    method: 'get'
  })
}

/**
 * 更新数据模板
 */
export function updateDataTemplate(id: number, data: DataTemplateUpdate) {
  return request<DataTemplate>({
    url: `/data-templates/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除数据模板
 */
export function deleteDataTemplate(id: number) {
  return request({
    url: `/data-templates/${id}`,
    method: 'delete'
  })
}

/**
 * 上传表定义文档
 */
export function uploadDefinitionFile(id: number, file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: `/data-templates/${id}/upload-definition`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 上传SQL建表代码
 */
export function uploadSqlFile(id: number, file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: `/data-templates/${id}/upload-sql`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 下载表定义文档
 */
export function downloadDefinitionFile(id: number) {
  return `/api/v1/data-templates/${id}/download-definition`
}

/**
 * 下载SQL建表代码
 */
export function downloadSqlFile(id: number) {
  return `/api/v1/data-templates/${id}/download-sql`
}

/**
 * 批量上传文件
 */
export function batchUploadFiles(definitionFiles: File[], sqlFiles: File[]) {
  const formData = new FormData()
  definitionFiles.forEach(file => {
    formData.append('definition_files', file)
  })
  sqlFiles.forEach(file => {
    formData.append('sql_files', file)
  })
  return request<BatchUploadResult>({
    url: '/data-templates/batch-upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 预览批量上传
 */
export function previewBatchUpload(definitionFiles: File[], sqlFiles: File[]) {
  const formData = new FormData()
  definitionFiles.forEach(file => {
    formData.append('definition_files', file)
  })
  sqlFiles.forEach(file => {
    formData.append('sql_files', file)
  })
  return request<BatchUploadPreview>({
    url: '/data-templates/batch-upload/preview',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 上移数据模板
 */
export function moveUp(id: number) {
  return request({
    url: `/data-templates/${id}/move-up`,
    method: 'post'
  })
}

/**
 * 下移数据模板
 */
export function moveDown(id: number) {
  return request({
    url: `/data-templates/${id}/move-down`,
    method: 'post'
  })
}

/**
 * 切换核心标志
 */
export function toggleCore(id: number) {
  return request({
    url: `/data-templates/${id}/toggle-core`,
    method: 'put'
  })
}

/**
 * 获取其他医疗机构列表
 */
export function getHospitalsForCopy() {
  return request<HospitalSimple[]>({
    url: '/data-templates/hospitals/list',
    method: 'get'
  })
}

/**
 * 获取指定医疗机构的数据模板列表
 */
export function getHospitalTemplates(hospitalId: number) {
  return request<DataTemplate[]>({
    url: `/data-templates/hospitals/${hospitalId}/templates`,
    method: 'get'
  })
}

/**
 * 复制数据模板
 */
export function copyTemplates(data: CopyTemplateRequest) {
  return request<CopyResult>({
    url: '/data-templates/copy',
    method: 'post',
    data
  })
}
