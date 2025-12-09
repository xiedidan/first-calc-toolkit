<template>
  <el-dialog
    v-model="visible"
    title="提交预览"
    width="900px"
    append-to-body
    @close="handleClose"
  >
    <div v-loading="loading">
      <!-- 统计信息 -->
      <el-alert
        v-if="previewData"
        :title="`总计 ${previewData.total_items} 个项目：${previewData.new_count} 个新增，${previewData.overwrite_count} 个覆盖`"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      />

      <!-- 警告信息 -->
      <el-alert
        v-if="previewData && previewData.warnings.length > 0"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        <template #title>
          <div>警告信息：</div>
          <ul style="margin: 5px 0; padding-left: 20px;">
            <li v-for="(warning, index) in previewData.warnings" :key="index">
              {{ warning }}
            </li>
          </ul>
        </template>
      </el-alert>

      <!-- 标签页 -->
      <el-tabs v-if="previewData" v-model="activeTab">
        <!-- 新增项目 -->
        <el-tab-pane label="新增项目" :name="'new'">
          <template #label>
            <span>新增项目 <el-badge :value="previewData.new_count" :max="999" /></span>
          </template>
          
          <el-table
            :data="previewData.new_items"
            border
            stripe
            max-height="400"
            style="width: 100%;"
          >
            <el-table-column prop="item_name" label="项目名称" min-width="150" />
            <el-table-column label="目标维度" min-width="200">
              <template #default="{ row }">
                <div>
                  <div style="font-weight: 600;">{{ row.dimension_name }}</div>
                  <div style="font-size: 12px; color: #909399;">{{ row.dimension_path }}</div>
                </div>
              </template>
            </el-table-column>
          </el-table>
          
          <div v-if="previewData.new_items.length === 0" style="text-align: center; padding: 40px; color: #909399;">
            暂无新增项目
          </div>
        </el-tab-pane>

        <!-- 覆盖项目 -->
        <el-tab-pane label="覆盖项目" :name="'overwrite'">
          <template #label>
            <span>覆盖项目 <el-badge :value="previewData.overwrite_count" :max="999" type="warning" /></span>
          </template>
          
          <el-alert
            v-if="previewData.overwrite_count > 0"
            title="以下项目已存在于维度目录中，提交后将覆盖原有分类"
            type="warning"
            :closable="false"
            style="margin-bottom: 15px;"
          />
          
          <el-table
            :data="previewData.overwrite_items"
            border
            stripe
            max-height="400"
            style="width: 100%;"
            :row-class-name="() => 'overwrite-row'"
          >
            <el-table-column prop="item_name" label="项目名称" min-width="150" />
            <el-table-column label="原维度" min-width="180">
              <template #default="{ row }">
                <div>
                  <div style="font-weight: 600; color: #f56c6c;">{{ row.old_dimension_name }}</div>
                  <div style="font-size: 12px; color: #909399;">{{ row.old_dimension_path }}</div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="" width="60" align="center">
              <template>
                <el-icon :size="20" color="#409eff"><Right /></el-icon>
              </template>
            </el-table-column>
            <el-table-column label="新维度" min-width="180">
              <template #default="{ row }">
                <div>
                  <div style="font-weight: 600; color: #67c23a;">{{ row.dimension_name }}</div>
                  <div style="font-size: 12px; color: #909399;">{{ row.dimension_path }}</div>
                </div>
              </template>
            </el-table-column>
          </el-table>
          
          <div v-if="previewData.overwrite_items.length === 0" style="text-align: center; padding: 40px; color: #909399;">
            暂无覆盖项目
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          @click="handleConfirm"
          :loading="submitting"
          :disabled="!previewData"
        >
          确认提交
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Right } from '@element-plus/icons-vue'
import { generateSubmitPreview, submitClassificationPlan, type SubmitPreviewResponse } from '@/api/classification-plans'

// Props
interface Props {
  modelValue: boolean
  planId: number | null
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

// 数据
const visible = ref(false)
const loading = ref(false)
const submitting = ref(false)
const previewData = ref<SubmitPreviewResponse | null>(null)
const activeTab = ref('new')

// 监听modelValue变化
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.planId) {
    loadPreview()
  }
})

// 监听visible变化
watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 加载预览数据
const loadPreview = async () => {
  if (!props.planId) return
  
  loading.value = true
  try {
    previewData.value = await generateSubmitPreview(props.planId)
    
    // 默认显示有数据的标签页
    if (previewData.value.new_count > 0) {
      activeTab.value = 'new'
    } else if (previewData.value.overwrite_count > 0) {
      activeTab.value = 'overwrite'
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载预览数据失败')
    handleClose()
  } finally {
    loading.value = false
  }
}

// 确认提交
const handleConfirm = async () => {
  if (!props.planId) return
  
  submitting.value = true
  try {
    await submitClassificationPlan(props.planId, { confirm: true })
    ElMessage.success('提交成功')
    emit('success')
    handleClose()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '提交失败')
  } finally {
    submitting.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
  previewData.value = null
  activeTab.value = 'new'
}
</script>

<style scoped>
:deep(.overwrite-row) {
  background-color: #fef0f0 !important;
}

:deep(.overwrite-row:hover > td) {
  background-color: #fde2e2 !important;
}

:deep(.el-badge__content) {
  border: none;
}
</style>
