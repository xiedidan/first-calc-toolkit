<template>
  <el-dialog
    v-model="visible"
    :title="result.success ? '测试成功' : '测试失败'"
    width="900px"
    append-to-body
    :close-on-click-modal="false"
  >
    <div class="test-result-container">
      <!-- 执行信息 -->
      <el-alert
        :title="result.success ? '代码执行成功' : '代码执行失败'"
        :type="result.success ? 'success' : 'error'"
        :closable="false"
        show-icon
        style="margin-bottom: 16px"
      >
        <template #default>
          <div class="alert-content">
            <span>执行时间: <strong>{{ result.duration_ms }}ms</strong></span>
            <span v-if="result.result?.message" style="margin-left: 20px">
              {{ result.result.message }}
            </span>
          </div>
        </template>
      </el-alert>

      <!-- 成功结果 -->
      <div v-if="result.success && result.result">
        <!-- 列信息 -->
        <div v-if="result.result.columns && result.result.columns.length > 0" class="result-section">
          <div class="section-title">
            <el-icon><List /></el-icon>
            <span>返回列 ({{ result.result.columns.length }})</span>
          </div>
          <div class="columns-container">
            <el-tag
              v-for="(col, index) in result.result.columns"
              :key="index"
              type="info"
              size="small"
              style="margin: 4px"
            >
              {{ col }}
            </el-tag>
          </div>
        </div>

        <!-- 数据预览 -->
        <div v-if="result.result.rows && result.result.rows.length > 0" class="result-section">
          <div class="section-title">
            <el-icon><Document /></el-icon>
            <span>数据预览 (共 {{ result.result.row_count || result.result.rows.length }} 行)</span>
          </div>
          
          <!-- 表格视图 -->
          <div class="table-view">
            <el-table
              :data="result.result.rows.slice(0, 20)"
              border
              stripe
              max-height="400"
              size="small"
              style="width: 100%"
            >
              <el-table-column
                v-for="col in result.result.columns"
                :key="col"
                :prop="col"
                :label="col"
                min-width="120"
                show-overflow-tooltip
              >
                <template #default="{ row }">
                  <span class="cell-content">{{ formatCellValue(row[col]) }}</span>
                </template>
              </el-table-column>
            </el-table>
            
            <div v-if="result.result.rows.length > 20" class="more-rows-tip">
              <el-icon><InfoFilled /></el-icon>
              <span>仅显示前 20 行数据</span>
            </div>
          </div>

          <!-- JSON 视图切换 -->
          <el-divider />
          <el-collapse v-model="activeCollapse">
            <el-collapse-item title="查看 JSON 格式" name="json">
              <div class="json-view">
                <pre>{{ JSON.stringify(result.result.rows.slice(0, 20), null, 2) }}</pre>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>

        <!-- 无数据 -->
        <el-empty
          v-else
          description="查询成功但未返回数据"
          :image-size="80"
        />
      </div>

      <!-- 错误信息 -->
      <div v-else-if="!result.success" class="error-section">
        <div class="section-title error">
          <el-icon><WarningFilled /></el-icon>
          <span>错误详情</span>
        </div>
        <div class="error-content">
          <pre>{{ result.error }}</pre>
        </div>
      </div>
    </div>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
      <el-button v-if="result.success && result.result?.rows" type="primary" @click="handleCopy">
        <el-icon><CopyDocument /></el-icon>
        复制结果
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { List, Document, InfoFilled, WarningFilled, CopyDocument } from '@element-plus/icons-vue'

interface TestResult {
  success: boolean
  duration_ms: number
  result?: {
    message?: string
    columns?: string[]
    rows?: any[]
    row_count?: number
  }
  error?: string
}

const visible = defineModel<boolean>('visible', { required: true })
const props = defineProps<{
  result: TestResult
}>()

const activeCollapse = ref<string[]>([])

// 格式化单元格值
const formatCellValue = (value: any): string => {
  if (value === null || value === undefined) {
    return 'NULL'
  }
  if (typeof value === 'object') {
    return JSON.stringify(value)
  }
  return String(value)
}

// 复制结果
const handleCopy = () => {
  if (!props.result.result?.rows) return
  
  const text = JSON.stringify(props.result.result.rows, null, 2)
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}
</script>

<style scoped>
.test-result-container {
  max-height: 70vh;
  overflow-y: auto;
}

.alert-content {
  display: flex;
  align-items: center;
  font-size: 14px;
}

.result-section {
  margin-bottom: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e4e7ed;
}

.section-title.error {
  color: #f56c6c;
  border-bottom-color: #f56c6c;
}

.columns-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.table-view {
  background: #fff;
  border-radius: 4px;
}

.cell-content {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
}

.more-rows-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px;
  background: #f0f9ff;
  color: #409eff;
  font-size: 13px;
  border-top: 1px solid #e4e7ed;
}

.json-view {
  max-height: 400px;
  overflow: auto;
  background: #f5f7fa;
  border-radius: 4px;
  padding: 12px;
}

.json-view pre {
  margin: 0;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #303133;
}

.error-section {
  margin-top: 16px;
}

.error-content {
  background: #fef0f0;
  border: 1px solid #fde2e2;
  border-radius: 4px;
  padding: 16px;
}

.error-content pre {
  margin: 0;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #f56c6c;
  white-space: pre-wrap;
  word-break: break-word;
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-table th) {
  background: #f5f7fa;
  font-weight: 600;
}

:deep(.el-collapse-item__header) {
  font-size: 14px;
  color: #606266;
}
</style>
