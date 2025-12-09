import request from '@/utils/request'

// 参考价值类型定义
export interface ReferenceValue {
  id: number
  hospital_id: number
  period: string
  department_code: string
  department_name: string
  reference_value: number
  doctor_reference_value: number | null
  nurse_reference_value: number | null
  tech_reference_value: number | null
  created_at: string
  updated_at: string
}

export interface ReferenceValueCreate {
  period: string
  department_code: string
  department_name: string
  reference_value: number
  doctor_reference_value?: number | null
  nurse_reference_value?: number | null
  tech_reference_value?: number | null
}

export interface ReferenceValueUpdate {
  period?: string
  department_code?: string
  department_name?: string
  reference_value?: number
  doctor_reference_value?: number | null
  nurse_reference_value?: number | null
  tech_reference_value?: number | null
}

export interface ReferenceValueList {
  total: number
  items: ReferenceValue[]
}

// 导入相关类型
export interface ImportParseResponse {
  session_id: string
  sheet_names: string[]
  current_sheet: string
  headers: string[]
  preview_data: string[][]
  total_rows: number
  skip_rows: number
  suggested_mapping: Record<string, string>
}

export interface DepartmentMatch {
  id: number
  code: string
  name: string
  score: number
}

export interface UniqueValueForMatch {
  value: string
  count: number
  suggested_departments: DepartmentMatch[]
}

export interface ImportExtractResponse {
  unique_values: UniqueValueForMatch[]
  system_departments: DepartmentMatch[]
}

export interface DepartmentValueMapping {
  value: string
  department_code: string | null
}

export interface PreviewItem {
  period: string
  department_code: string
  department_name: string
  excel_department_name: string
  reference_value: number
  doctor_reference_value: number | null
  nurse_reference_value: number | null
  tech_reference_value: number | null
  status: 'new' | 'update' | 'error'
  message: string
}

export interface PreviewStatistics {
  total: number
  new_count: number
  update_count: number
  error_count: number
}

export interface ImportPreviewResponse {
  preview_items: PreviewItem[]
  statistics: PreviewStatistics
}

export interface ImportReport {
  success_count: number
  update_count: number
  error_count: number
  errors: Array<{
    period: string
    department_code: string
    reason: string
  }>
}

export interface ImportExecuteResponse {
  success: boolean
  report: ImportReport
}

// API 函数

// 获取参考价值列表
export function getReferenceValues(params: {
  period?: string
  department_code?: string
  keyword?: string
  page?: number
  size?: number
}) {
  return request({
    url: '/reference-values',
    method: 'get',
    params
  })
}

// 获取指定月份的参考价值（用于报表对比）
export function getReferenceValuesByPeriod(period: string) {
  return request({
    url: `/reference-values/by-period/${period}`,
    method: 'get'
  })
}

// 获取已有参考价值的月份列表
export function getAvailablePeriods() {
  return request({
    url: '/reference-values/periods',
    method: 'get'
  })
}

// 获取单个参考价值
export function getReferenceValue(id: number) {
  return request({
    url: `/reference-values/${id}`,
    method: 'get'
  })
}

// 创建参考价值
export function createReferenceValue(data: ReferenceValueCreate) {
  return request({
    url: '/reference-values',
    method: 'post',
    data
  })
}

// 更新参考价值
export function updateReferenceValue(id: number, data: ReferenceValueUpdate) {
  return request({
    url: `/reference-values/${id}`,
    method: 'put',
    data
  })
}

// 删除参考价值
export function deleteReferenceValue(id: number) {
  return request({
    url: `/reference-values/${id}`,
    method: 'delete'
  })
}

// 清空指定月份的参考价值
export function clearPeriodReferenceValues(period: string) {
  return request({
    url: `/reference-values/period/${period}/clear-all`,
    method: 'delete'
  })
}

// 清空所有参考价值
export function clearAllReferenceValues() {
  return request({
    url: '/reference-values/clear-all',
    method: 'delete'
  })
}

// 导入相关API

// 第一步：解析Excel文件
export function importParse(file: File, sheetName?: string, skipRows?: number) {
  const formData = new FormData()
  formData.append('file', file)
  
  const params: Record<string, any> = {}
  if (sheetName) params.sheet_name = sheetName
  if (skipRows !== undefined) params.skip_rows = skipRows
  
  return request({
    url: '/reference-values/import/parse',
    method: 'post',
    data: formData,
    params,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 第二步：提取唯一值并匹配
export function importExtractValues(data: {
  session_id: string
  field_mapping: Record<string, string>
  match_by: 'code' | 'name'
}) {
  return request({
    url: '/reference-values/import/extract-values',
    method: 'post',
    data
  })
}

// 第三步：生成预览
export function importPreview(data: {
  session_id: string
  value_mapping: DepartmentValueMapping[]
}) {
  return request({
    url: '/reference-values/import/preview',
    method: 'post',
    data
  })
}

// 执行导入
export function importExecute(data: {
  session_id: string
  confirmed_items?: PreviewItem[]
}) {
  return request({
    url: '/reference-values/import/execute',
    method: 'post',
    data
  })
}
