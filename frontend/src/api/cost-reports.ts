/**
 * 成本报表管理API
 */
import request from '@/utils/request'

export interface CostReport {
  id: number
  hospital_id: number
  period: string
  department_code: string
  department_name: string
  personnel_cost: number
  material_cost: number
  medicine_cost: number
  depreciation_cost: number
  other_cost: number
  created_at: string
  updated_at: string
}

export interface CostReportCreate {
  period: string
  department_code: string
  department_name: string
  personnel_cost?: number
  material_cost?: number
  medicine_cost?: number
  depreciation_cost?: number
  other_cost?: number
}

export interface CostReportUpdate {
  period?: string
  department_code?: string
  department_name?: string
  personnel_cost?: number
  material_cost?: number
  medicine_cost?: number
  depreciation_cost?: number
  other_cost?: number
}

export interface CostReportListResponse {
  total: number
  items: CostReport[]
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
  header_row: number
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
  personnel_cost: number
  material_cost: number
  medicine_cost: number
  depreciation_cost: number
  other_cost: number
  status: string
  message: string
}

export interface PreviewStatistics {
  total: number
  new_count: number
  update_count: number
  skip_count: number
  error_count: number
}

export interface ImportPreviewResponse {
  preview_items: PreviewItem[]
  statistics: PreviewStatistics
}

export interface ImportReport {
  success_count: number
  update_count: number
  skip_count: number
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

// API函数

export function getCostReports(params: {
  period?: string
  department_code?: string
  keyword?: string
  page?: number
  size?: number
}) {
  return request({
    url: '/cost-reports',
    method: 'get',
    params
  })
}

export function getCostReport(id: number) {
  return request({
    url: `/cost-reports/${id}`,
    method: 'get'
  })
}

export function createCostReport(data: CostReportCreate) {
  return request({
    url: '/cost-reports',
    method: 'post',
    data
  })
}

export function updateCostReport(id: number, data: CostReportUpdate) {
  return request({
    url: `/cost-reports/${id}`,
    method: 'put',
    data
  })
}

export function deleteCostReport(id: number) {
  return request({
    url: `/cost-reports/${id}`,
    method: 'delete'
  })
}

export function clearFilteredCostReports(params: {
  period?: string
  department_code?: string
}) {
  return request({
    url: '/cost-reports/clear-filtered/batch',
    method: 'delete',
    params
  })
}

export function getAvailablePeriods() {
  return request({
    url: '/cost-reports/periods',
    method: 'get'
  })
}

// 导入相关API

export function importParse(file: File, sheetName?: string, skipRows?: number, headerRow?: number) {
  const formData = new FormData()
  formData.append('file', file)
  
  const params: Record<string, any> = {}
  if (sheetName) params.sheet_name = sheetName
  if (skipRows !== undefined) params.skip_rows = skipRows
  if (headerRow !== undefined) params.header_row = headerRow
  
  return request({
    url: '/cost-reports/import/parse',
    method: 'post',
    data: formData,
    params,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function importExtractValues(data: {
  session_id: string
  field_mapping: Record<string, string>
  match_by: string
}) {
  return request({
    url: '/cost-reports/import/extract-values',
    method: 'post',
    data
  })
}

export function importPreview(data: {
  session_id: string
  value_mapping: DepartmentValueMapping[]
}) {
  return request({
    url: '/cost-reports/import/preview',
    method: 'post',
    data
  })
}

export function importExecute(data: {
  session_id: string
  confirmed_items?: PreviewItem[]
}) {
  return request({
    url: '/cost-reports/import/execute',
    method: 'post',
    data
  })
}
