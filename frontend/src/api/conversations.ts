/**
 * 对话API - 智能问数系统
 */
import request from '@/utils/request'

// 对话类型
export interface Conversation {
  id: number
  hospital_id: number
  group_id: number | null
  group_name: string | null
  title: string
  description: string | null
  conversation_type: string
  conversation_type_display: string
  message_count: number
  created_at: string
  updated_at: string
}

// 对话消息
export interface ConversationMessage {
  id: number
  conversation_id: number
  role: 'user' | 'assistant'
  content: string
  content_type: string
  content_type_display: string
  message_metadata: Record<string, any> | null
  created_at: string
}

// 对话详情（包含消息）
export interface ConversationDetail extends Conversation {
  messages: ConversationMessage[]
}

// 创建对话请求
export interface CreateConversationRequest {
  title: string
  description?: string
  conversation_type?: string
  group_id?: number | null
}

// 更新对话请求
export interface UpdateConversationRequest {
  title?: string
  description?: string
  conversation_type?: string
  group_id?: number | null
}

// 发送消息响应
export interface SendMessageResponse {
  user_message: ConversationMessage
  assistant_message: ConversationMessage
}

// 对话类型选项
export const CONVERSATION_TYPES = [
  { value: 'caliber', label: '指标口径查询' },
  { value: 'data', label: '数据智能查询' },
  { value: 'sql', label: 'SQL代码编写' },
]

/**
 * 获取对话列表
 */
export function getConversations(params?: {
  keyword?: string
  group_id?: number
  conversation_type?: string
  page?: number
  size?: number
}) {
  return request.get<{
    items: Conversation[]
    total: number
    page: number
    size: number
  }>('/conversations', { params })
}

/**
 * 创建对话
 */
export function createConversation(data: CreateConversationRequest) {
  return request.post<Conversation>('/conversations', data)
}

/**
 * 获取对话详情（包含消息历史）
 */
export function getConversation(id: number) {
  if (!id || isNaN(id)) {
    return Promise.reject(new Error('无效的对话ID'))
  }
  return request.get<ConversationDetail>(`/conversations/${id}`)
}

/**
 * 更新对话
 */
export function updateConversation(id: number, data: UpdateConversationRequest) {
  if (!id || isNaN(id)) {
    return Promise.reject(new Error('无效的对话ID'))
  }
  return request.put<Conversation>(`/conversations/${id}`, data)
}

/**
 * 删除对话
 */
export function deleteConversation(id: number) {
  if (!id || isNaN(id)) {
    return Promise.reject(new Error('无效的对话ID'))
  }
  return request.delete<{ deleted_messages: number }>(`/conversations/${id}`)
}

/**
 * 发送消息
 */
export function sendMessage(conversationId: number, content: string) {
  if (!conversationId || isNaN(conversationId)) {
    return Promise.reject(new Error('无效的对话ID'))
  }
  return request.post<SendMessageResponse>(`/conversations/${conversationId}/messages`, {
    content,
  })
}

/**
 * 获取对话消息列表（分页）
 */
export function getMessages(conversationId: number, params?: { page?: number; size?: number }) {
  if (!conversationId || isNaN(conversationId)) {
    return Promise.reject(new Error('无效的对话ID'))
  }
  return request.get<{
    items: ConversationMessage[]
    total: number
    page: number
    size: number
  }>(`/conversations/${conversationId}/messages`, { params })
}


// 导出格式类型
export type ExportFormat = 'markdown' | 'pdf' | 'excel' | 'csv'

/**
 * 导出消息内容
 * 
 * 需求 3.3: 当用户请求下载结果时，智能数据问答模块应生成并下载Markdown或PDF格式的结果文件
 * 需求 4.4: 当用户请求下载结果时，智能数据问答模块应生成并下载Excel或CSV格式的数据文件
 */
export async function exportMessage(
  conversationId: number,
  messageId: number,
  format: ExportFormat
): Promise<{ blob: Blob; filename?: string }> {
  if (!conversationId || isNaN(conversationId)) {
    throw new Error('无效的对话ID')
  }
  if (!messageId || isNaN(messageId)) {
    throw new Error('无效的消息ID')
  }
  const response = await request.post(
    `/conversations/${conversationId}/messages/${messageId}/export`,
    { format },
    { responseType: 'blob' }
  )
  
  // 响应拦截器对blob类型返回完整response对象
  const axiosResponse = response as any
  const blob = axiosResponse.data as Blob
  
  // 从Content-Disposition头获取文件名
  const contentDisposition = axiosResponse.headers?.['content-disposition']
  let filename: string | undefined
  if (contentDisposition) {
    // 解析 filename*=UTF-8''xxx 格式
    const filenameMatch = contentDisposition.match(/filename\*=UTF-8''(.+)/)
    if (filenameMatch) {
      filename = decodeURIComponent(filenameMatch[1])
    } else {
      // 尝试解析 filename="xxx" 格式
      const simpleMatch = contentDisposition.match(/filename="?([^";\n]+)"?/)
      if (simpleMatch) {
        filename = simpleMatch[1]
      }
    }
  }
  
  return { blob, filename }
}

/**
 * 下载导出的消息文件
 */
export function downloadExportedMessage(
  conversationId: number,
  messageId: number,
  format: ExportFormat,
  defaultFilename?: string
): Promise<void> {
  return new Promise(async (resolve, reject) => {
    try {
      const { blob, filename } = await exportMessage(conversationId, messageId, format)
      
      // 创建下载链接
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      
      // 优先使用后端返回的文件名，否则使用默认文件名
      if (filename) {
        link.download = filename
      } else {
        const ext = format === 'markdown' ? '.md' : format === 'excel' ? '.xlsx' : `.${format}`
        link.download = defaultFilename || `导出_${new Date().toISOString().slice(0, 10)}${ext}`
      }
      
      // 触发下载
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      // 释放URL
      URL.revokeObjectURL(url)
      
      resolve()
    } catch (error) {
      reject(error)
    }
  })
}
