<template>
  <el-dialog
    v-model="visible"
    title="数据模板详情"
    width="900px"
    :close-on-click-modal="false"
  >
    <div v-loading="loading" class="detail-container">
      <el-descriptions :column="2" border v-if="template">
        <el-descriptions-item label="表名">{{ template.table_name }}</el-descriptions-item>
        <el-descriptions-item label="中文名">{{ template.table_name_cn }}</el-descriptions-item>
        <el-descriptions-item label="核心表">
          <el-tag v-if="template.is_core" type="danger" size="small">是</el-tag>
          <span v-else>否</span>
        </el-descriptions-item>
        <el-descriptions-item label="序号">{{ template.sort_order }}</el-descriptions-item>
        <el-descriptions-item label="说明" :span="2">
          {{ template.description || '-' }}
        </el-descriptions-item>
      </el-descriptions>

      <!-- 表定义文档 -->
      <div v-if="template?.has_definition" class="content-section">
        <el-divider content-position="left">
          <span class="section-title">表定义文档</span>
        </el-divider>
        <div v-if="definitionContent" class="markdown-content" v-html="renderedDefinition"></div>
        <el-empty v-else description="无法加载表定义文档" />
      </div>

      <!-- SQL建表代码 -->
      <div v-if="template?.has_sql" class="content-section">
        <el-divider content-position="left">
          <span class="section-title">SQL建表代码</span>
        </el-divider>
        <pre v-if="sqlContent" class="sql-content"><code>{{ sqlContent }}</code></pre>
        <el-empty v-else description="无法加载SQL文件" />
      </div>

      <el-empty v-if="!template?.has_definition && !template?.has_sql" description="暂无文档和SQL文件" />
    </div>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import type { DataTemplate } from '@/api/data-templates'
import request from '@/utils/request'

const props = defineProps<{
  modelValue: boolean
  templateId: number | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const loading = ref(false)
const template = ref<DataTemplate | null>(null)
const definitionContent = ref('')
const sqlContent = ref('')

// 渲染 Markdown
const renderedDefinition = computed(() => {
  if (!definitionContent.value) return ''
  try {
    return marked(definitionContent.value)
  } catch (error) {
    console.error('Markdown 渲染失败:', error)
    return '<p>Markdown 渲染失败</p>'
  }
})

// 加载模板详情
const loadTemplateDetail = async () => {
  if (!props.templateId) return

  loading.value = true
  try {
    // 获取模板基本信息
    const templateRes = await request.get(`/data-templates/${props.templateId}`)
    template.value = templateRes

    // 加载表定义文档内容
    if (templateRes.has_definition) {
      try {
        const defRes = await request.get(`/data-templates/${props.templateId}/definition-content`, {
          responseType: 'text'
        })
        definitionContent.value = defRes
      } catch (error) {
        console.error('加载表定义文档失败:', error)
      }
    }

    // 加载SQL文件内容
    if (templateRes.has_sql) {
      try {
        const sqlRes = await request.get(`/data-templates/${props.templateId}/sql-content`, {
          responseType: 'text'
        })
        sqlContent.value = sqlRes
      } catch (error) {
        console.error('加载SQL文件失败:', error)
      }
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载详情失败')
  } finally {
    loading.value = false
  }
}

// 监听对话框打开
watch(() => props.modelValue, (newVal) => {
  if (newVal && props.templateId) {
    loadTemplateDetail()
  } else {
    // 关闭时清空数据
    template.value = null
    definitionContent.value = ''
    sqlContent.value = ''
  }
})
</script>

<style scoped>
.detail-container {
  min-height: 200px;
}

.content-section {
  margin-top: 20px;
}

.section-title {
  font-weight: 600;
  font-size: 16px;
}

.markdown-content {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
  max-height: 500px;
  overflow-y: auto;
}

.markdown-content :deep(h1) {
  font-size: 24px;
  margin: 16px 0;
  border-bottom: 1px solid #ddd;
  padding-bottom: 8px;
}

.markdown-content :deep(h2) {
  font-size: 20px;
  margin: 14px 0;
}

.markdown-content :deep(h3) {
  font-size: 18px;
  margin: 12px 0;
}

.markdown-content :deep(p) {
  margin: 8px 0;
  line-height: 1.6;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 8px 0;
  padding-left: 24px;
}

.markdown-content :deep(li) {
  margin: 4px 0;
}

.markdown-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.markdown-content :deep(th) {
  background-color: #f0f0f0;
  font-weight: 600;
}

.markdown-content :deep(code) {
  background: #fff;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
}

.markdown-content :deep(pre) {
  background: #fff;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
}

.markdown-content :deep(pre code) {
  padding: 0;
  background: transparent;
}

.sql-content {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
  max-height: 500px;
  overflow: auto;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
}

.sql-content code {
  color: #333;
}
</style>
