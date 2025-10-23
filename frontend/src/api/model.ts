/**
 * 模型管理API
 */
import request from '@/utils/request'

// ==================== 模型版本 ====================

export interface ModelVersion {
  id: number
  version: string
  name: string
  description?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ModelVersionCreate {
  version: string
  name: string
  description?: string
  base_version_id?: number
}

export interface ModelVersionUpdate {
  name?: string
  description?: string
}

/**
 * 获取模型版本列表
 */
export function getModelVersions(params?: { skip?: number; limit?: number }) {
  return request<{ total: number; items: ModelVersion[] }>({
    url: '/model-versions',
    method: 'get',
    params
  })
}

/**
 * 获取模型版本详情
 */
export function getModelVersion(id: number) {
  return request<ModelVersion>({
    url: `/model-versions/${id}`,
    method: 'get'
  })
}

/**
 * 创建模型版本
 */
export function createModelVersion(data: ModelVersionCreate) {
  return request<ModelVersion>({
    url: '/model-versions',
    method: 'post',
    data
  })
}

/**
 * 更新模型版本
 */
export function updateModelVersion(id: number, data: ModelVersionUpdate) {
  return request<ModelVersion>({
    url: `/model-versions/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除模型版本
 */
export function deleteModelVersion(id: number) {
  return request({
    url: `/model-versions/${id}`,
    method: 'delete'
  })
}

/**
 * 激活模型版本
 */
export function activateModelVersion(id: number) {
  return request<ModelVersion>({
    url: `/model-versions/${id}/activate`,
    method: 'put'
  })
}

// ==================== 模型节点 ====================

export interface ModelNode {
  id: number
  version_id: number
  parent_id?: number
  sort_order: number
  name: string
  code: string
  node_type: 'sequence' | 'dimension'
  is_leaf: boolean
  calc_type?: 'statistical' | 'calculational'
  weight?: number
  unit?: string
  business_guide?: string
  script?: string
  created_at: string
  updated_at: string
  children?: ModelNode[]
  has_children?: boolean
}

export interface ModelNodeCreate {
  version_id: number
  parent_id?: number
  sort_order?: number
  name: string
  code: string
  node_type: 'sequence' | 'dimension'
  is_leaf?: boolean
  calc_type?: 'statistical' | 'calculational'
  weight?: number
  unit?: string
  business_guide?: string
  script?: string
}

export interface ModelNodeUpdate {
  name?: string
  code?: string
  node_type?: 'sequence' | 'dimension'
  sort_order?: number
  is_leaf?: boolean
  calc_type?: 'statistical' | 'calculational'
  weight?: number
  unit?: string
  business_guide?: string
  script?: string
}

/**
 * 获取模型节点列表
 */
export function getModelNodes(params: { version_id: number; parent_id?: number }) {
  return request<{ total: number; items: ModelNode[] }>({
    url: '/model-nodes',
    method: 'get',
    params
  })
}

/**
 * 获取模型节点详情
 */
export function getModelNode(id: number) {
  return request<ModelNode>({
    url: `/model-nodes/${id}`,
    method: 'get'
  })
}

/**
 * 创建模型节点
 */
export function createModelNode(data: ModelNodeCreate) {
  return request<ModelNode>({
    url: '/model-nodes',
    method: 'post',
    data
  })
}

/**
 * 更新模型节点
 */
export function updateModelNode(id: number, data: ModelNodeUpdate) {
  return request<ModelNode>({
    url: `/model-nodes/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除模型节点
 */
export function deleteModelNode(id: number) {
  return request({
    url: `/model-nodes/${id}`,
    method: 'delete'
  })
}

/**
 * 测试节点代码
 */
export function testNodeCode(id: number, data: { script: string; test_params?: any }) {
  return request<{ success: boolean; result?: any; error?: string }>({
    url: `/model-nodes/${id}/test-code`,
    method: 'post',
    data
  })
}
