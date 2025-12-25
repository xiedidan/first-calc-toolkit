<template>
  <div class="conversation-message" :class="[message.role, { 'with-actions': showActions }]">
    <!-- 头像 -->
    <div class="message-avatar">
      <el-avatar v-if="message.role === 'user'" :size="avatarSize" :icon="User" />
      <el-avatar v-else :size="avatarSize" :icon="Monitor" class="assistant-avatar" />
    </div>

    <!-- 消息内容 -->
    <div class="message-content">
      <!-- 消息头部 -->
      <div class="message-header" v-if="showHeader">
        <span class="message-role">{{ message.role === 'user' ? '我' : 'AI助手' }}</span>
        <span class="message-time">{{ formatTime(message.created_at) }}</span>
      </div>

      <!-- 消息主体 -->
      <div class="message-body">
        <!-- 文本内容 -->
        <div v-if="message.content_type === 'text'" class="text-content" v-html="formattedContent"></div>

        <!-- 代码块 -->
        <div v-else-if="message.content_type === 'code'" class="code-content">
          <div class="code-header">
            <span class="code-language">{{ codeLanguage }}</span>
            <el-button size="small" text class="copy-btn" @click="handleCopyCode">
              <el-icon><CopyDocument /></el-icon>
              复制
            </el-button>
          </div>
          <pre class="code-block"><code>{{ codeContent }}</code></pre>
        </div>

        <!-- 表格内容 -->
        <div v-else-if="message.content_type === 'table'" class="table-content">
          <el-table
            :data="tableRows"
            border
            stripe
            :max-height="tableMaxHeight"
            size="small"
          >
            <el-table-column
              v-for="(col, idx) in tableColumns"
              :key="idx"
              :prop="String(idx)"
              :label="col"
              :min-width="getColumnWidth(col)"
              show-overflow-tooltip
            />
          </el-table>
          <div v-if="tableTotalRows && tableTotalRows > tableRows.length" class="table-footer">
            <span class="table-info">显示 {{ tableRows.length }} / {{ tableTotalRows }} 条记录</span>
          </div>
        </div>

        <!-- 图表内容 -->
        <div v-else-if="message.content_type === 'chart'" class="chart-content">
          <ChartRenderer
            v-if="chartType && chartData"
            :type="chartType"
            :data="chartData"
            :config="chartConfig"
            :height="chartHeight"
            @click="handleChartClick"
          />
          <div v-else class="chart-placeholder">
            <el-icon :size="48"><DataLine /></el-icon>
            <p>图表数据不完整</p>
          </div>
        </div>

        <!-- 错误内容 -->
        <div v-else-if="message.content_type === 'error'" class="error-content">
          <el-alert
            :title="message.content"
            type="error"
            :closable="false"
            show-icon
          />
        </div>

        <!-- 默认文本 -->
        <div v-else class="text-content">{{ message.content }}</div>
      </div>

      <!-- 消息操作按钮 -->
      <div v-if="showActions && message.role === 'assistant'" class="message-actions">
        <el-button
          v-if="canExport"
          size="small"
          text
          :loading="exportingFormat === 'markdown'"
          :disabled="!!exportingFormat"
          @click="handleExport('markdown')"
        >
          <el-icon v-if="exportingFormat !== 'markdown'"><Document /></el-icon>
          Markdown
        </el-button>
        <el-button
          v-if="canExportPdf"
          size="small"
          text
          :loading="exportingFormat === 'pdf'"
          :disabled="!!exportingFormat"
          @click="handleExport('pdf')"
        >
          <el-icon v-if="exportingFormat !== 'pdf'"><Tickets /></el-icon>
          PDF
        </el-button>
        <el-button
          v-if="canExportExcel"
          size="small"
          text
          :loading="exportingFormat === 'excel'"
          :disabled="!!exportingFormat"
          @click="handleExport('excel')"
        >
          <el-icon v-if="exportingFormat !== 'excel'"><Grid /></el-icon>
          Excel
        </el-button>
        <el-button
          v-if="canExportCsv"
          size="small"
          text
          :loading="exportingFormat === 'csv'"
          :disabled="!!exportingFormat"
          @click="handleExport('csv')"
        >
          <el-icon v-if="exportingFormat !== 'csv'"><List /></el-icon>
          CSV
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  User,
  Monitor,
  CopyDocument,
  DataLine,
  Document,
  Tickets,
  Grid,
  List,
  Loading
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { marked } from 'marked'
import ChartRenderer from '@/components/ChartRenderer.vue'
import type { ChartType, ChartData, ChartConfig } from '@/components/ChartRenderer.vue'
import { downloadExportedMessage, type ExportFormat } from '@/api/conversations'

// 配置 marked
marked.setOptions({
  breaks: true, // 支持换行
  gfm: true // 支持 GitHub Flavored Markdown
})

// 消息接口定义
export interface MessageMetadata {
  // 代码块
  language?: string
  code?: string
  // 表格
  columns?: string[]
  rows?: any[]
  total_rows?: number
  // 图表
  chart_type?: ChartType
  chart_data?: ChartData
  chart_config?: ChartConfig
}

export interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  content_type: 'text' | 'code' | 'table' | 'chart' | 'error'
  message_metadata?: MessageMetadata
  created_at: string
}

// Props
const props = withDefaults(defineProps<{
  message: Message
  conversationId?: number
  conversationTitle?: string
  showHeader?: boolean
  showActions?: boolean
  avatarSize?: number
  tableMaxHeight?: number
  chartHeight?: number
}>(), {
  conversationId: 0,
  conversationTitle: '',
  showHeader: true,
  showActions: true,
  avatarSize: 36,
  tableMaxHeight: 400,
  chartHeight: 300
})

// 导出状态
const exportingFormat = ref<ExportFormat | null>(null)

// Emits
const emit = defineEmits<{
  (e: 'copy', content: string): void
  (e: 'export', format: 'markdown' | 'pdf' | 'excel' | 'csv'): void
  (e: 'chart-click', params: any): void
}>()

// 格式化时间
const formatTime = (time: string) => {
  return dayjs(time).format('MM-DD HH:mm')
}

// 格式化文本内容（使用 marked 渲染完整 Markdown）
const formattedContent = computed(() => {
  const content = props.message.content
  try {
    return marked.parse(content) as string
  } catch (e) {
    console.error('Markdown 解析失败:', e)
    // 降级处理：简单换行
    return content.replace(/\n/g, '<br>')
  }
})

// 代码相关
const codeLanguage = computed(() => {
  return props.message.message_metadata?.language || 'sql'
})

const codeContent = computed(() => {
  return props.message.message_metadata?.code || props.message.content
})

// 表格相关
const tableColumns = computed(() => {
  return props.message.message_metadata?.columns || []
})

const tableRows = computed(() => {
  const rows = props.message.message_metadata?.rows || []
  // 将数组行转换为对象格式供el-table使用
  return rows.map(row => {
    if (Array.isArray(row)) {
      const obj: Record<string, any> = {}
      row.forEach((val, idx) => {
        obj[String(idx)] = val
      })
      return obj
    }
    return row
  })
})

const tableTotalRows = computed(() => {
  return props.message.message_metadata?.total_rows
})

// 计算列宽
const getColumnWidth = (col: string) => {
  const len = col.length
  if (len <= 4) return 80
  if (len <= 8) return 120
  if (len <= 12) return 160
  return 200
}

// 图表相关
const chartType = computed(() => {
  return props.message.message_metadata?.chart_type
})

const chartData = computed(() => {
  return props.message.message_metadata?.chart_data
})

const chartConfig = computed(() => {
  return props.message.message_metadata?.chart_config
})

// 导出相关
const canExport = computed(() => {
  return ['text', 'table', 'code'].includes(props.message.content_type)
})

const canExportPdf = computed(() => {
  return ['text', 'table'].includes(props.message.content_type)
})

const canExportExcel = computed(() => {
  return props.message.content_type === 'table'
})

const canExportCsv = computed(() => {
  return props.message.content_type === 'table'
})

// 复制代码
const handleCopyCode = async () => {
  try {
    await navigator.clipboard.writeText(codeContent.value)
    ElMessage.success('已复制到剪贴板')
    emit('copy', codeContent.value)
  } catch (e) {
    ElMessage.error('复制失败')
  }
}

// 导出
const handleExport = async (format: ExportFormat) => {
  // 如果没有传入conversationId，则通过事件让父组件处理
  if (!props.conversationId) {
    emit('export', format)
    return
  }
  
  // 直接调用API导出
  exportingFormat.value = format
  try {
    const timestamp = dayjs().format('YYYYMMDD_HHmmss')
    const filename = `导出_${props.conversationTitle || '对话'}_${timestamp}`
    await downloadExportedMessage(
      props.conversationId,
      props.message.id,
      format,
      filename
    )
    ElMessage.success('导出成功')
  } catch (error: any) {
    console.error('导出失败:', error)
    // 尝试解析错误信息
    if (error.response?.data instanceof Blob) {
      try {
        const text = await error.response.data.text()
        const errorData = JSON.parse(text)
        ElMessage.error(errorData.detail || '导出失败')
      } catch {
        ElMessage.error('导出失败')
      }
    } else {
      ElMessage.error(error.message || '导出失败')
    }
  } finally {
    exportingFormat.value = null
  }
}

// 图表点击
const handleChartClick = (params: any) => {
  emit('chart-click', params)
}
</script>

<style scoped>
.conversation-message {
  display: flex;
  gap: 12px;
}

.conversation-message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.assistant-avatar {
  background-color: #409eff;
}

.message-content {
  max-width: 70%;
  min-width: 200px;
}

.conversation-message.user .message-content {
  text-align: right;
}

.message-header {
  margin-bottom: 4px;
  font-size: 12px;
  color: #909399;
}

.message-role {
  margin-right: 8px;
}

.message-body {
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 8px;
}

.conversation-message.user .message-body {
  background: #ecf5ff;
}

/* 文本内容 */
.text-content {
  line-height: 1.6;
  word-break: break-word;
}

/* Markdown 渲染样式 */
.text-content :deep(p) {
  margin: 0 0 8px;
}

.text-content :deep(p:last-child) {
  margin-bottom: 0;
}

.text-content :deep(h1),
.text-content :deep(h2),
.text-content :deep(h3),
.text-content :deep(h4),
.text-content :deep(h5),
.text-content :deep(h6) {
  margin: 16px 0 8px;
  font-weight: 600;
  line-height: 1.4;
}

.text-content :deep(h1:first-child),
.text-content :deep(h2:first-child),
.text-content :deep(h3:first-child),
.text-content :deep(h4:first-child),
.text-content :deep(h5:first-child),
.text-content :deep(h6:first-child) {
  margin-top: 0;
}

.text-content :deep(h1) { font-size: 1.5em; }
.text-content :deep(h2) { font-size: 1.3em; }
.text-content :deep(h3) { font-size: 1.15em; }
.text-content :deep(h4) { font-size: 1em; }

.text-content :deep(code) {
  background: #e6e8eb;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
}

.text-content :deep(pre) {
  background: #1e1e1e;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 8px 0;
}

.text-content :deep(pre code) {
  background: transparent;
  padding: 0;
  color: #d4d4d4;
  font-size: 13px;
  line-height: 1.5;
}

.text-content :deep(strong) {
  font-weight: 600;
}

.text-content :deep(em) {
  font-style: italic;
}

.text-content :deep(ul),
.text-content :deep(ol) {
  margin: 8px 0;
  padding-left: 24px;
}

.text-content :deep(li) {
  margin: 4px 0;
}

.text-content :deep(blockquote) {
  margin: 8px 0;
  padding: 8px 16px;
  border-left: 4px solid #409eff;
  background: #f0f7ff;
  color: #606266;
}

.text-content :deep(blockquote p) {
  margin: 0;
}

.text-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
  font-size: 13px;
}

.text-content :deep(th),
.text-content :deep(td) {
  border: 1px solid #dcdfe6;
  padding: 8px 12px;
  text-align: left;
}

.text-content :deep(th) {
  background: #f5f7fa;
  font-weight: 600;
}

.text-content :deep(tr:nth-child(even)) {
  background: #fafafa;
}

.text-content :deep(a) {
  color: #409eff;
  text-decoration: none;
}

.text-content :deep(a:hover) {
  text-decoration: underline;
}

.text-content :deep(hr) {
  border: none;
  border-top: 1px solid #dcdfe6;
  margin: 16px 0;
}

.text-content :deep(img) {
  max-width: 100%;
  border-radius: 4px;
}

/* 代码块 */
.code-content {
  background: #1e1e1e;
  border-radius: 8px;
  overflow: hidden;
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #2d2d2d;
  color: #909399;
  font-size: 12px;
}

.code-language {
  text-transform: uppercase;
  font-weight: 500;
}

.copy-btn {
  color: #909399 !important;
}

.copy-btn:hover {
  color: #409eff !important;
}

.code-block {
  margin: 0;
  padding: 12px;
  overflow-x: auto;
}

.code-block code {
  color: #d4d4d4;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre;
}

/* 表格内容 */
.table-content {
  max-width: 100%;
  overflow-x: auto;
}

.table-footer {
  margin-top: 8px;
  text-align: right;
}

.table-info {
  font-size: 12px;
  color: #909399;
}

/* 图表内容 */
.chart-content {
  min-height: 200px;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #909399;
  background: #fafafa;
  border-radius: 8px;
}

.chart-placeholder p {
  margin: 8px 0 0;
}

/* 错误内容 */
.error-content {
  max-width: 100%;
}

/* 消息操作 */
.message-actions {
  margin-top: 8px;
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.conversation-message.user .message-actions {
  justify-content: flex-end;
}

/* 加载状态 */
.loading-message {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
}

.loading-message .el-icon {
  font-size: 16px;
}
</style>
