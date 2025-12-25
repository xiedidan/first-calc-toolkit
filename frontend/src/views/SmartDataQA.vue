<template>
  <div class="smart-data-qa-container">
    <!-- 左侧：对话列表 -->
    <div class="sidebar-panel">
      <el-card class="sidebar-card">
        <template #header>
          <div class="card-header">
            <span>对话列表</span>
            <div class="header-actions">
              <el-button type="primary" size="small" @click="handleNewConversation">
                <el-icon><Plus /></el-icon>
                新建对话
              </el-button>
            </div>
          </div>
        </template>
        
        <!-- 搜索栏 -->
        <div class="sidebar-toolbar">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索对话..."
            clearable
            size="small"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button size="small" @click="handleNewGroup" title="新建分组">
            <el-icon><FolderAdd /></el-icon>
          </el-button>
        </div>
        
        <!-- 对话分组列表 -->
        <div class="conversation-list" v-loading="listLoading">
          <!-- 分组列表 -->
          <div v-for="group in groups" :key="group.id" class="conversation-group">
            <div 
              class="group-header" 
              @click="toggleGroup(group)"
              @dragover.prevent="handleDragOver($event, group.id)"
              @dragleave="handleDragLeave($event)"
              @drop="handleDropToGroup($event, group.id)"
              :class="{ 'drag-over': dragOverGroupId === group.id }"
            >
              <el-icon class="collapse-icon" :class="{ collapsed: group.is_collapsed }">
                <ArrowDown />
              </el-icon>
              <span class="group-name">{{ group.name }}</span>
              <span class="group-count">({{ group.conversation_count }})</span>
              <el-dropdown trigger="click" @command="(cmd: string) => handleGroupCommand(cmd, group)" @click.stop>
                <el-icon class="more-icon"><MoreFilled /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="rename"><el-icon><Edit /></el-icon>重命名</el-dropdown-item>
                    <el-dropdown-item command="delete" divided><el-icon><Delete /></el-icon>删除分组</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
            <div v-show="!group.is_collapsed" class="group-conversations">
              <div
                v-for="conv in getGroupConversations(group.id)"
                :key="conv.id"
                class="conversation-item"
                :class="{ active: currentConversation?.id === conv.id, 'drag-over': dragOverConvId === conv.id }"
                @click="selectConversation(conv)"
                draggable="true"
                @dragstart="handleDragStart($event, conv)"
                @dragover.prevent="handleDragOverConv($event, conv)"
                @dragleave="handleDragLeaveConv($event)"
                @drop="handleDropToConv($event, conv)"
              >
                <el-icon class="conv-icon"><ChatDotRound /></el-icon>
                <div class="conv-info">
                  <div class="conv-title">{{ conv.title }}</div>
                  <div class="conv-meta">
                    <el-tag size="small" :type="getTypeTagType(conv.conversation_type)">{{ conv.conversation_type_display }}</el-tag>
                  </div>
                </div>
                <el-dropdown trigger="click" @command="(cmd: string) => handleConvCommand(cmd, conv)" @click.stop>
                  <el-icon class="more-icon"><MoreFilled /></el-icon>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="rename"><el-icon><Edit /></el-icon>重命名</el-dropdown-item>
                      <el-dropdown-item command="delete" divided><el-icon><Delete /></el-icon>删除</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </div>
          
          <!-- 未分组对话 -->
          <div class="conversation-group ungrouped">
            <div 
              class="group-header" 
              @click="toggleUngrouped"
              @dragover.prevent="handleDragOver($event, null)"
              @dragleave="handleDragLeave($event)"
              @drop="handleDropToGroup($event, null)"
              :class="{ 'drag-over': dragOverGroupId === 'ungrouped' }"
            >
              <el-icon class="collapse-icon" :class="{ collapsed: ungroupedCollapsed }"><ArrowDown /></el-icon>
              <span class="group-name">未分组</span>
              <span class="group-count">({{ ungroupedConversations.length }})</span>
            </div>
            <div v-show="!ungroupedCollapsed" class="group-conversations">
              <div
                v-for="conv in ungroupedConversations"
                :key="conv.id"
                class="conversation-item"
                :class="{ active: currentConversation?.id === conv.id, 'drag-over': dragOverConvId === conv.id }"
                @click="selectConversation(conv)"
                draggable="true"
                @dragstart="handleDragStart($event, conv)"
                @dragover.prevent="handleDragOverConv($event, conv)"
                @dragleave="handleDragLeaveConv($event)"
                @drop="handleDropToConv($event, conv)"
              >
                <el-icon class="conv-icon"><ChatDotRound /></el-icon>
                <div class="conv-info">
                  <div class="conv-title">{{ conv.title }}</div>
                  <div class="conv-meta">
                    <el-tag size="small" :type="getTypeTagType(conv.conversation_type)">{{ conv.conversation_type_display }}</el-tag>
                  </div>
                </div>
                <el-dropdown trigger="click" @command="(cmd: string) => handleConvCommand(cmd, conv)" @click.stop>
                  <el-icon class="more-icon"><MoreFilled /></el-icon>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="rename"><el-icon><Edit /></el-icon>重命名</el-dropdown-item>
                      <el-dropdown-item command="delete" divided><el-icon><Delete /></el-icon>删除</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </div>
          <el-empty v-if="!listLoading && conversations.length === 0" description="暂无对话" />
        </div>
      </el-card>
    </div>

    <!-- 右侧：对话主界面 -->
    <div class="main-panel">
      <el-card class="main-card" v-loading="detailLoading">
        <div v-if="!currentConversation" class="empty-state">
          <el-empty description="请选择或创建一个对话">
            <el-button type="primary" @click="handleNewConversation"><el-icon><Plus /></el-icon>新建对话</el-button>
          </el-empty>
        </div>
        <template v-else>
          <div class="conversation-header">
            <div class="title-section">
              <span v-if="!isEditingTitle" @dblclick="startEditTitle" class="conv-title-text">
                {{ currentConversation.title }}
                <el-icon class="edit-icon" @click="startEditTitle"><Edit /></el-icon>
              </span>
              <el-input v-else v-model="editingTitle" size="small" @blur="saveTitle" @keyup.enter="saveTitle" @keyup.escape="cancelEditTitle" ref="titleInputRef" style="width: 300px" />
            </div>
            <div class="type-section">
              <span class="type-label">对话类型：</span>
              <el-radio-group v-model="currentType" size="small" @change="handleTypeChange">
                <el-radio-button value="caliber">指标口径查询</el-radio-button>
                <el-radio-button value="data">数据智能查询</el-radio-button>
                <el-radio-button value="sql">SQL代码编写</el-radio-button>
              </el-radio-group>
              <el-button
                v-if="userStore.isMaintainer"
                type="primary"
                link
                size="small"
                @click="openPromptEditModal"
                class="prompt-edit-btn"
              >
                <el-icon><Setting /></el-icon>
                修改提示词
              </el-button>
            </div>
          </div>
          
          <div class="messages-container" ref="messagesContainerRef">
            <div v-if="messages.length === 0" class="no-messages">
              <el-icon :size="48" color="#909399"><ChatLineSquare /></el-icon>
              <p>开始您的对话吧</p>
              <p class="hint">{{ getTypeHint(currentType) }}</p>
            </div>
            <div v-else class="messages-list">
              <ConversationMessage
                v-for="msg in messages"
                :key="msg.id"
                :message="msg"
                :conversation-id="currentConversation?.id"
                :conversation-title="currentConversation?.title"
                :show-actions="msg.role === 'assistant'"
                @copy="handleCodeCopy"
                @export="(format) => handleMessageExport(msg, format)"
                @chart-click="handleChartClick"
              />
              <div v-if="sending" class="message-item assistant loading">
                <div class="message-avatar"><el-avatar :size="36" :icon="Monitor" style="background-color: #409eff" /></div>
                <div class="message-content">
                  <div class="message-body">
                    <div class="loading-indicator"><el-icon class="is-loading"><Loading /></el-icon><span>AI正在思考...</span></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="input-container">
            <el-input v-model="inputMessage" type="textarea" :rows="3" placeholder="输入您的问题..." @keydown.enter.exact.prevent="handleSend" :disabled="sending" />
            <div class="input-actions">
              <span class="input-hint">按 Enter 发送，Shift+Enter 换行</span>
              <el-button type="primary" @click="handleSend" :loading="sending" :disabled="!inputMessage.trim()"><el-icon><Promotion /></el-icon>发送</el-button>
            </div>
          </div>
        </template>
      </el-card>
    </div>

    <!-- 新建对话对话框 -->
    <el-dialog v-model="newConvDialogVisible" title="新建对话" width="500px" append-to-body>
      <el-form :model="newConvForm" label-width="80px">
        <el-form-item label="对话标题" required><el-input v-model="newConvForm.title" placeholder="请输入对话标题" /></el-form-item>
        <el-form-item label="对话类型">
          <el-select v-model="newConvForm.conversation_type" style="width: 100%">
            <el-option label="指标口径查询" value="caliber" />
            <el-option label="数据智能查询" value="data" />
            <el-option label="SQL代码编写" value="sql" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属分组">
          <el-select v-model="newConvForm.group_id" placeholder="未分组" clearable style="width: 100%">
            <el-option v-for="g in groups" :key="g.id" :label="g.name" :value="g.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述"><el-input v-model="newConvForm.description" type="textarea" :rows="2" placeholder="可选描述" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="newConvDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createNewConversation" :loading="creating">创建</el-button>
      </template>
    </el-dialog>
    
    <!-- 新建分组对话框 -->
    <el-dialog v-model="newGroupDialogVisible" title="新建分组" width="400px" append-to-body>
      <el-form :model="newGroupForm" label-width="80px">
        <el-form-item label="分组名称" required><el-input v-model="newGroupForm.name" placeholder="请输入分组名称" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="newGroupDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createNewGroup" :loading="creating">创建</el-button>
      </template>
    </el-dialog>
    
    <!-- 重命名对话框 -->
    <el-dialog v-model="renameDialogVisible" :title="renameDialogTitle" width="400px" append-to-body>
      <el-input v-model="renameValue" placeholder="请输入新名称" />
      <template #footer>
        <el-button @click="renameDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmRename" :loading="renaming">确定</el-button>
      </template>
    </el-dialog>

    <!-- 提示词编辑模态框 (仅Maintainer可见) -->
    <PromptEditModal
      v-model="promptEditModalVisible"
      :module-code="currentPromptModuleCode"
      @saved="handlePromptSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, FolderAdd, ArrowDown, MoreFilled, Edit, Delete, ChatDotRound, User, Monitor, ChatLineSquare, Loading, Promotion, Setting } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import ChartRenderer from '@/components/ChartRenderer.vue'
import type { ChartType, ChartData, ChartConfig } from '@/components/ChartRenderer.vue'
import ConversationMessage from '@/components/ConversationMessage.vue'
import type { Message as ConversationMessageType } from '@/components/ConversationMessage.vue'
import PromptEditModal from '@/components/PromptEditModal.vue'
import { getConversations, createConversation, updateConversation, deleteConversation, getConversation, sendMessage } from '@/api/conversations'
import { getConversationGroups, createConversationGroup, updateConversationGroup, deleteConversationGroup, moveConversationsToGroup } from '@/api/conversation-groups'
import { useUserStore } from '@/stores/user'

interface ConversationGroup { id: number; name: string; sort_order: number; is_collapsed: boolean; conversation_count: number }
interface Conversation { id: number; title: string; description?: string; conversation_type: string; conversation_type_display: string; group_id?: number; created_at: string; updated_at: string }
interface Message { id: number; role: 'user' | 'assistant'; content: string; content_type: 'text' | 'code' | 'table' | 'chart' | 'error'; message_metadata?: { language?: string; code?: string; columns?: string[]; rows?: any[]; chart_type?: ChartType; chart_data?: ChartData; chart_config?: ChartConfig }; created_at: string }

// 对话类型到提示词模块代码的映射
const conversationTypeToModuleCode: Record<string, string> = {
  caliber: 'query_caliber',
  data: 'query_data',
  sql: 'query_sql'
}

// 用户store
const userStore = useUserStore()

const listLoading = ref(false)
const detailLoading = ref(false)
const sending = ref(false)
const creating = ref(false)
const renaming = ref(false)
const searchKeyword = ref('')
const groups = ref<ConversationGroup[]>([])
const conversations = ref<Conversation[]>([])
const currentConversation = ref<Conversation | null>(null)
const messages = ref<Message[]>([])
const inputMessage = ref('')
const currentType = ref('caliber')
const ungroupedCollapsed = ref(false)
const isEditingTitle = ref(false)
const editingTitle = ref('')
const titleInputRef = ref<HTMLInputElement | null>(null)
const messagesContainerRef = ref<HTMLElement | null>(null)
const newConvDialogVisible = ref(false)
const newGroupDialogVisible = ref(false)
const renameDialogVisible = ref(false)
const renameDialogTitle = ref('')
const renameValue = ref('')
let renameTarget: { type: 'group' | 'conversation', id: number } | null = null
const newConvForm = ref({ title: '', conversation_type: 'caliber', group_id: null as number | null, description: '' })
const newGroupForm = ref({ name: '' })
let draggedConversation: Conversation | null = null
const dragOverGroupId = ref<number | string | null>(null)
const dragOverConvId = ref<number | null>(null)

// 提示词编辑模态框
const promptEditModalVisible = ref(false)
const currentPromptModuleCode = ref('')

// 打开提示词编辑模态框
const openPromptEditModal = () => {
  currentPromptModuleCode.value = conversationTypeToModuleCode[currentType.value] || ''
  if (currentPromptModuleCode.value) {
    promptEditModalVisible.value = true
  }
}

// 提示词保存成功回调
const handlePromptSaved = () => {
  ElMessage.success('提示词配置已更新')
}

const ungroupedConversations = computed(() => conversations.value.filter(c => !c.group_id))
const getGroupConversations = (groupId: number) => conversations.value.filter(c => c.group_id === groupId)
const getTypeTagType = (type: string) => { switch (type) { case 'caliber': return 'primary'; case 'data': return 'success'; case 'sql': return 'warning'; default: return 'info' } }
const getTypeHint = (type: string) => { switch (type) { case 'caliber': return '输入指标名称或关键词，查询指标的业务口径定义'; case 'data': return '用自然语言描述您想查询的数据，AI将生成SQL并返回结果'; case 'sql': return '描述您需要的SQL逻辑，AI将为您生成SQL代码'; default: return '' } }
const formatTime = (time: string) => dayjs(time).format('MM-DD HH:mm')
const formatContent = (content: string) => content.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/`(.*?)`/g, '<code>$1</code>')

const loadGroups = async () => { try { const res = await getConversationGroups() as any; groups.value = res.data?.items || [] } catch (e) { console.error('Failed to load groups:', e) } }
const loadConversations = async () => { listLoading.value = true; try { const res = await getConversations({ keyword: searchKeyword.value || undefined }) as any; conversations.value = res.data?.items || [] } catch (e) { console.error('Failed to load conversations:', e) } finally { listLoading.value = false } }
const loadConversationDetail = async (id: number) => { detailLoading.value = true; try { const res = await getConversation(id) as any; currentConversation.value = res.data; messages.value = res.data?.messages || []; currentType.value = res.data?.conversation_type || 'caliber'; scrollToBottom() } catch (e) { ElMessage.error('加载对话详情失败') } finally { detailLoading.value = false } }
const scrollToBottom = () => { nextTick(() => { if (messagesContainerRef.value) { messagesContainerRef.value.scrollTop = messagesContainerRef.value.scrollHeight } }) }
const handleSearch = () => { loadConversations() }
const toggleGroup = (group: ConversationGroup) => { group.is_collapsed = !group.is_collapsed; updateConversationGroup(group.id, { is_collapsed: group.is_collapsed }).catch(() => {}) }
const toggleUngrouped = () => { ungroupedCollapsed.value = !ungroupedCollapsed.value }
const handleGroupCommand = async (cmd: string, group: ConversationGroup) => {
  if (cmd === 'rename') { renameDialogTitle.value = '重命名分组'; renameValue.value = group.name; renameTarget = { type: 'group', id: group.id }; renameDialogVisible.value = true }
  else if (cmd === 'delete') { try { await ElMessageBox.confirm('删除分组后，分组内的对话将移至未分组。确定删除？', '确认删除'); await deleteConversationGroup(group.id); ElMessage.success('删除成功'); loadGroups(); loadConversations() } catch (e: any) { if (e !== 'cancel') ElMessage.error('删除失败') } }
}
const selectConversation = (conv: Conversation) => { if (currentConversation.value?.id === conv.id) return; loadConversationDetail(conv.id) }
const handleConvCommand = async (cmd: string, conv: Conversation) => {
  if (cmd === 'rename') { renameDialogTitle.value = '重命名对话'; renameValue.value = conv.title; renameTarget = { type: 'conversation', id: conv.id }; renameDialogVisible.value = true }
  else if (cmd === 'delete') { try { await ElMessageBox.confirm('确定删除该对话及其所有消息？', '确认删除'); await deleteConversation(conv.id); ElMessage.success('删除成功'); if (currentConversation.value?.id === conv.id) { currentConversation.value = null; messages.value = [] } loadConversations(); loadGroups() } catch (e: any) { if (e !== 'cancel') ElMessage.error('删除失败') } }
}
const handleNewConversation = () => { newConvForm.value = { title: `新对话 ${dayjs().format('MM-DD HH:mm')}`, conversation_type: 'caliber', group_id: null, description: '' }; newConvDialogVisible.value = true }
const createNewConversation = async () => { if (!newConvForm.value.title.trim()) { ElMessage.warning('请输入对话标题'); return } creating.value = true; try { const res = await createConversation(newConvForm.value) as any; ElMessage.success('创建成功'); newConvDialogVisible.value = false; loadConversations(); loadGroups(); loadConversationDetail(res.data.id) } catch (e) { ElMessage.error('创建失败') } finally { creating.value = false } }
const handleNewGroup = () => { newGroupForm.value = { name: '' }; newGroupDialogVisible.value = true }
const createNewGroup = async () => { if (!newGroupForm.value.name.trim()) { ElMessage.warning('请输入分组名称'); return } creating.value = true; try { await createConversationGroup(newGroupForm.value); ElMessage.success('创建成功'); newGroupDialogVisible.value = false; loadGroups() } catch (e) { ElMessage.error('创建失败') } finally { creating.value = false } }
const confirmRename = async () => { if (!renameValue.value.trim() || !renameTarget) { ElMessage.warning('请输入名称'); return } renaming.value = true; try { if (renameTarget.type === 'group') { await updateConversationGroup(renameTarget.id, { name: renameValue.value }); loadGroups() } else { await updateConversation(renameTarget.id, { title: renameValue.value }); loadConversations(); if (currentConversation.value?.id === renameTarget.id) { currentConversation.value.title = renameValue.value } } ElMessage.success('重命名成功'); renameDialogVisible.value = false } catch (e) { ElMessage.error('重命名失败') } finally { renaming.value = false } }
const startEditTitle = () => { if (!currentConversation.value) return; editingTitle.value = currentConversation.value.title; isEditingTitle.value = true; nextTick(() => { titleInputRef.value?.focus() }) }
const saveTitle = async () => { if (!currentConversation.value || !editingTitle.value.trim()) { cancelEditTitle(); return } try { await updateConversation(currentConversation.value.id, { title: editingTitle.value }); currentConversation.value.title = editingTitle.value; loadConversations() } catch (e) { ElMessage.error('保存失败') } isEditingTitle.value = false }
const cancelEditTitle = () => { isEditingTitle.value = false }
const handleTypeChange = async (type: string) => { if (!currentConversation.value) return; try { await updateConversation(currentConversation.value.id, { conversation_type: type }); currentConversation.value.conversation_type = type; loadConversations() } catch (e) { ElMessage.error('切换类型失败') } }

const handleSend = async () => {
  if (!currentConversation.value || !inputMessage.value.trim() || sending.value) return
  const content = inputMessage.value.trim()
  inputMessage.value = ''
  sending.value = true
  const userMsg: Message = { id: Date.now(), role: 'user', content, content_type: 'text', created_at: new Date().toISOString() }
  messages.value.push(userMsg)
  scrollToBottom()
  try {
    const res = await sendMessage(currentConversation.value.id, content) as any
    messages.value.pop()
    if (res.data?.user_message) messages.value.push(res.data.user_message)
    if (res.data?.assistant_message) messages.value.push(res.data.assistant_message)
    scrollToBottom()
  } catch (e: any) {
    messages.value.push({ id: Date.now() + 1, role: 'assistant', content: e.message || '发送失败，请重试', content_type: 'error', created_at: new Date().toISOString() })
    scrollToBottom()
  } finally { sending.value = false }
}
const copyCode = async (code: string) => { try { await navigator.clipboard.writeText(code); ElMessage.success('已复制到剪贴板') } catch (e) { ElMessage.error('复制失败') } }
const handleCodeCopy = (content: string) => { console.log('Code copied:', content.substring(0, 50)) }
const handleMessageExport = async (msg: Message, format: 'markdown' | 'pdf' | 'excel' | 'csv') => {
  // 注意：ConversationMessage组件已经直接处理导出，此函数仅作为备用
  // 当组件没有传入conversationId时会触发此事件
  console.log('Export message fallback:', msg.id, format)
}
const handleChartClick = (params: any) => { console.log('Chart clicked:', params) }
const handleDragStart = (event: DragEvent, conv: Conversation) => { draggedConversation = conv; if (event.dataTransfer) event.dataTransfer.effectAllowed = 'move' }
const handleDragOver = (event: DragEvent, groupId: number | null) => { 
  event.preventDefault()
  dragOverGroupId.value = groupId === null ? 'ungrouped' : groupId
  dragOverConvId.value = null
}
const handleDragLeave = (event: DragEvent) => { 
  const relatedTarget = event.relatedTarget as HTMLElement
  if (!relatedTarget || !relatedTarget.closest('.group-header')) {
    dragOverGroupId.value = null 
  }
}
const handleDragOverConv = (event: DragEvent, conv: Conversation) => {
  event.preventDefault()
  if (draggedConversation && draggedConversation.id !== conv.id) {
    dragOverConvId.value = conv.id
    dragOverGroupId.value = null
  }
}
const handleDragLeaveConv = (event: DragEvent) => {
  const relatedTarget = event.relatedTarget as HTMLElement
  if (!relatedTarget || !relatedTarget.closest('.conversation-item')) {
    dragOverConvId.value = null
  }
}
const handleDropToConv = async (event: DragEvent, targetConv: Conversation) => {
  event.preventDefault()
  event.stopPropagation()
  dragOverConvId.value = null
  dragOverGroupId.value = null
  if (!draggedConversation || draggedConversation.id === targetConv.id) {
    draggedConversation = null
    return
  }
  const targetGroupId = targetConv.group_id || null
  const currentGroupId = draggedConversation.group_id || null
  if (currentGroupId === targetGroupId) {
    draggedConversation = null
    return
  }
  try {
    await updateConversation(draggedConversation.id, { group_id: targetGroupId })
    ElMessage.success('移动成功')
    loadConversations()
    loadGroups()
  } catch (e) {
    ElMessage.error('移动失败')
  }
  draggedConversation = null
}
const handleDropToGroup = async (event: DragEvent, groupId: number | null) => {
  event.preventDefault()
  dragOverGroupId.value = null
  if (!draggedConversation) return
  
  // 检查是否移动到同一分组
  const currentGroupId = draggedConversation.group_id || null
  if (currentGroupId === groupId) { 
    draggedConversation = null
    return 
  }
  
  try { 
    // 使用 updateConversation 更新 group_id
    await updateConversation(draggedConversation.id, { group_id: groupId })
    ElMessage.success('移动成功')
    loadConversations()
    loadGroups() 
  } catch (e) { 
    ElMessage.error('移动失败') 
  }
  draggedConversation = null
}
const handleDrop = async (event: DragEvent, groupId: number) => {
  event.preventDefault()
  if (!draggedConversation || draggedConversation.group_id === groupId) { draggedConversation = null; return }
  try { await moveConversationsToGroup(groupId, { conversation_ids: [draggedConversation.id] }); ElMessage.success('移动成功'); loadConversations(); loadGroups() } catch (e) { ElMessage.error('移动失败') }
  draggedConversation = null
}
onMounted(() => { loadGroups(); loadConversations() })
</script>

<style scoped>
.smart-data-qa-container {
  display: flex;
  gap: 16px;
  height: 100%;
  padding: 0;
}

.sidebar-panel {
  width: 320px;
  flex-shrink: 0;
}

.main-panel {
  flex: 1;
  min-width: 0;
}

.sidebar-card,
.main-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.sidebar-card :deep(.el-card__body),
.main-card :deep(.el-card__body) {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.card-header { display: flex; justify-content: space-between; align-items: center; }
.sidebar-toolbar { display: flex; gap: 8px; margin-bottom: 12px; }
.sidebar-toolbar .el-input { flex: 1; }
.conversation-list { flex: 1; overflow-y: auto; }
.conversation-group { margin-bottom: 8px; }
.group-header { display: flex; align-items: center; padding: 8px 12px; background: #f5f7fa; border-radius: 4px; cursor: pointer; user-select: none; }
.group-header:hover { background: #e6e8eb; }
.group-header.drag-over { background: #ecf5ff; border: 2px dashed #409eff; }
.collapse-icon { transition: transform 0.2s; margin-right: 8px; }
.collapse-icon.collapsed { transform: rotate(-90deg); }
.group-name { flex: 1; font-weight: 500; }
.group-count { color: #909399; font-size: 12px; margin-right: 8px; }
.more-icon { color: #909399; cursor: pointer; }
.more-icon:hover { color: #409eff; }
.group-conversations { padding-left: 20px; }
.conversation-item { display: flex; align-items: center; padding: 10px 12px; border-radius: 4px; cursor: pointer; margin-top: 4px; }
.conversation-item:hover { background: #f5f7fa; }
.conversation-item.active { background: #ecf5ff; }
.conversation-item.drag-over { background: #ecf5ff; border: 2px dashed #409eff; }
.conv-icon { color: #909399; margin-right: 10px; }
.conv-info { flex: 1; min-width: 0; }
.conv-title { font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.conv-meta { margin-top: 4px; }
.empty-state { flex: 1; display: flex; align-items: center; justify-content: center; }
.conversation-header { padding: 16px 20px; border-bottom: 1px solid #ebeef5; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; flex-shrink: 0; }
.title-section { display: flex; align-items: center; }
.conv-title-text { margin: 0; font-size: 16px; font-weight: normal; display: flex; align-items: center; gap: 8px; color: #303133; }
.edit-icon { color: #909399; cursor: pointer; font-size: 14px; }
.edit-icon:hover { color: #409eff; }
.type-section { display: flex; align-items: center; gap: 8px; }
.type-label { color: #606266; font-size: 14px; }
.prompt-edit-btn { margin-left: 12px; }
.messages-container { flex: 1; overflow-y: auto; padding: 20px; }
.no-messages { height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #909399; }
.no-messages p { margin: 8px 0 0; }
.no-messages .hint { font-size: 12px; color: #c0c4cc; }
.messages-list { display: flex; flex-direction: column; gap: 20px; }
.message-item { display: flex; gap: 12px; }
.message-item.user { flex-direction: row-reverse; }
.message-content { max-width: 70%; }
.message-item.user .message-content { text-align: right; }
.message-header { margin-bottom: 4px; font-size: 12px; color: #909399; }
.message-role { margin-right: 8px; }
.message-body { background: #f5f7fa; padding: 12px 16px; border-radius: 8px; }
.message-item.user .message-body { background: #ecf5ff; }
.text-content { line-height: 1.6; word-break: break-word; }
.text-content :deep(code) { background: #e6e8eb; padding: 2px 6px; border-radius: 4px; font-family: monospace; }
.code-content { background: #1e1e1e; border-radius: 8px; overflow: hidden; }
.code-header { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #2d2d2d; color: #909399; font-size: 12px; }
.code-content pre { margin: 0; padding: 12px; overflow-x: auto; }
.code-content code { color: #d4d4d4; font-family: 'Consolas', 'Monaco', monospace; font-size: 13px; line-height: 1.5; }
.table-content { max-width: 100%; overflow-x: auto; }
.chart-content { min-height: 300px; }
.chart-placeholder { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 200px; color: #909399; background: #fafafa; border-radius: 8px; }
.error-content { max-width: 100%; }
.loading-indicator { display: flex; align-items: center; gap: 8px; color: #909399; }
.input-container { padding: 16px 20px; border-top: 1px solid #ebeef5; flex-shrink: 0; }
.input-actions { display: flex; justify-content: space-between; align-items: center; margin-top: 12px; }
.input-hint { font-size: 12px; color: #909399; }
.ungrouped .group-header { background: transparent; border: 1px dashed #dcdfe6; }
</style>
