/**
 * 对话分组API - 智能问数系统
 */
import request from '@/utils/request'

// 对话分组
export interface ConversationGroup {
  id: number
  hospital_id: number
  name: string
  sort_order: number
  is_collapsed: boolean
  conversation_count: number
  created_at: string
}

// 创建分组请求
export interface CreateGroupRequest {
  name: string
  sort_order?: number
  is_collapsed?: boolean
}

// 更新分组请求
export interface UpdateGroupRequest {
  name?: string
  sort_order?: number
  is_collapsed?: boolean
}

/**
 * 获取分组列表
 */
export function getConversationGroups() {
  return request.get<{
    items: ConversationGroup[]
    total: number
  }>('/conversation-groups')
}

/**
 * 创建分组
 */
export function createConversationGroup(data: CreateGroupRequest) {
  return request.post<ConversationGroup>('/conversation-groups', data)
}

/**
 * 获取分组详情
 */
export function getConversationGroup(id: number) {
  return request.get<ConversationGroup>(`/conversation-groups/${id}`)
}

/**
 * 更新分组
 */
export function updateConversationGroup(id: number, data: UpdateGroupRequest) {
  return request.put<ConversationGroup>(`/conversation-groups/${id}`, data)
}

/**
 * 删除分组
 */
export function deleteConversationGroup(id: number) {
  return request.delete<{ ungrouped_conversations: number }>(`/conversation-groups/${id}`)
}

/**
 * 重新排序分组
 */
export function reorderConversationGroups(groupIds: number[]) {
  return request.put<void>('/conversation-groups/reorder', { group_ids: groupIds })
}

/**
 * 批量移动对话到分组
 */
export function moveConversationsToGroup(groupId: number, conversationIds: number[]) {
  return request.put<{ moved_count: number }>(
    `/conversation-groups/${groupId}/conversations`,
    conversationIds
  )
}
