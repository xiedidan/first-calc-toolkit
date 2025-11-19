/**
 * 维度目录智能导入API
 */
import request from '@/utils/request'

// ==================== 类型定义 ====================

export interface SmartImportParseResponse {
  session_id: string
  sheet_names: string[]
  current_sheet: string
  headers: string[]
  preview_data: string[][]
  total_rows: number
  skip_rows: number
  suggested_mapping: Record<string, string>
}

export interface SystemDimension {
  id: number
  name: string
  code: string
  full_path: string
  score?: number
}

export interface UniqueValue {
  value: string
  source: string
  count: number
  suggested_dimensions: SystemDimension[]
}

export interface SmartImportExtractResponse {
  unique_values: UniqueValue[]
  system_dimensions: SystemDimension[]
}

export interface ValueMapping {
  value: string
  source: string
  dimension_codes: string[]
}

export interface PreviewItem {
  item_code: string
  item_name: string
  dimension_code: string
  dimension_name: string
  dimension_path: string
  source: string
  source_value: string
  status: string
  message: string
}

export interface PreviewStatistics {
  total: number
  ok: number
  warning: number
  error: number
}

export interface SmartImportPreviewResponse {
  preview_items: PreviewItem[]
  statistics: PreviewStatistics
}

export interface ImportError {
  item_code: string
  dimension_code: string
  reason: string
}

export interface ImportReport {
  success_count: number
  skipped_count: number
  error_count: number
  errors: ImportError[]
}

export interface SmartImportExecuteResponse {
  success: boolean
  report: ImportReport
}

// ==================== API方法 ====================

/**
 * 第一步：解析Excel文件
 */
export function parseExcel(file: File, sheetName?: string, skipRows?: number) {
  const formData = new FormData()
  formData.append('file', file)
  
  const params: Record<string, any> = {}
  if (sheetName) {
    params.sheet_name = sheetName
  }
  if (skipRows !== undefined && skipRows > 0) {
    params.skip_rows = skipRows
  }
  
  return request<SmartImportParseResponse>({
    url: '/dimension-items/smart-import/parse',
    method: 'post',
    data: formData,
    params,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 第二步：提取唯一值并获取智能匹配建议
 */
export function extractValues(data: {
  session_id: string
  field_mapping: Record<string, string>
  model_version_id: number
  match_by?: 'code' | 'name'  // 匹配方式：code(按编码) 或 name(按名称)
}) {
  return request<SmartImportExtractResponse>({
    url: '/dimension-items/smart-import/extract-values',
    method: 'post',
    data
  })
}

/**
 * 第三步：生成导入预览
 */
export function generatePreview(data: {
  session_id: string
  value_mapping: ValueMapping[]
}) {
  return request<SmartImportPreviewResponse>({
    url: '/dimension-items/smart-import/preview',
    method: 'post',
    data
  })
}

/**
 * 执行导入
 */
export function executeImport(data: {
  session_id: string
  confirmed_items?: PreviewItem[]
}) {
  return request<SmartImportExecuteResponse>({
    url: '/dimension-items/smart-import/execute',
    method: 'post',
    data
  })
}
