<template>
  <el-dialog
    v-model="visible"
    :title="`编辑提示词 - ${moduleInfo?.module_name || ''}`"
    width="800px"
    append-to-body
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div v-loading="loading">
      <!-- 模块信息 -->
      <div class="module-info" v-if="moduleInfo">
        <p class="module-desc">{{ moduleInfo.description }}</p>
        <div class="ai-interface-info">
          <span class="label">当前AI接口：</span>
          <el-tag v-if="moduleInfo.ai_interface" type="success" size="small">
            {{ moduleInfo.ai_interface.name }} ({{ moduleInfo.ai_interface.model_name }})
          </el-tag>
          <el-tag v-else type="warning" size="small">未配置</el-tag>
        </div>
      </div>

      <el-divider />

      <el-form
        ref="formRef"
        :model="form"
        label-width="120px"
        class="prompt-form"
      >
        <el-form-item label="模型温度">
          <el-slider
            v-model="form.temperature"
            :min="0"
            :max="2"
            :step="0.1"
            show-input
            :show-input-controls="false"
            style="width: 100%;"
          />
          <div class="form-item-tip">
            温度越低输出越确定，越高输出越随机（推荐0.3-0.7）
          </div>
        </el-form-item>

        <el-form-item label="支持的占位符">
          <div class="placeholders-list">
            <el-tag
              v-for="ph in moduleInfo?.placeholders || []"
              :key="ph.name"
              size="small"
              type="info"
              class="placeholder-tag"
              @click="insertPlaceholder(ph.name)"
            >
              {{ ph.name }}
              <el-tooltip :content="ph.description" placement="top">
                <el-icon style="margin-left: 4px;"><QuestionFilled /></el-icon>
              </el-tooltip>
            </el-tag>
          </div>
          <div class="form-item-tip">点击占位符可插入到用户提示词中</div>
        </el-form-item>

        <el-form-item label="系统提示词">
          <el-input
            v-model="form.system_prompt"
            type="textarea"
            :rows="10"
            placeholder="定义AI的角色和输出格式要求（可选）"
          />
        </el-form-item>

        <el-form-item label="用户提示词" required>
          <el-input
            ref="userPromptRef"
            v-model="form.user_prompt"
            type="textarea"
            :rows="10"
            placeholder="请输入提示词模板，可使用上方列出的占位符"
          />
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button @click="resetForm">重置</el-button>
      <el-button type="primary" @click="handleSave" :loading="saving">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { ElMessage, type FormInstance } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import {
  getPromptModule,
  updatePromptModule,
  type AIPromptModule,
  type AIPromptModuleUpdate,
} from '@/api/ai-prompt-modules'

const props = defineProps<{
  modelValue: boolean
  moduleCode: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'saved'): void
}>()

const visible = ref(false)
const loading = ref(false)
const saving = ref(false)
const formRef = ref<FormInstance>()
const userPromptRef = ref<any>()
const moduleInfo = ref<AIPromptModule | null>(null)

const form = ref<AIPromptModuleUpdate>({
  temperature: 0.7,
  system_prompt: '',
  user_prompt: '',
})

// 原始数据，用于重置
const originalForm = ref<AIPromptModuleUpdate>({
  temperature: 0.7,
  system_prompt: '',
  user_prompt: '',
})

// 同步visible状态
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.moduleCode) {
    loadModuleConfig()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const loadModuleConfig = async () => {
  if (!props.moduleCode) return

  loading.value = true
  try {
    const data = await getPromptModule(props.moduleCode)
    moduleInfo.value = data
    form.value = {
      temperature: data.temperature,
      system_prompt: data.system_prompt || '',
      user_prompt: data.user_prompt || '',
    }
    // 保存原始数据
    originalForm.value = { ...form.value }
  } catch (error) {
    console.error('加载模块配置失败:', error)
    ElMessage.error('加载模块配置失败')
  } finally {
    loading.value = false
  }
}

const insertPlaceholder = async (name: string) => {
  // 在用户提示词光标位置插入占位符
  const textarea = userPromptRef.value?.$el?.querySelector('textarea')
  if (textarea) {
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const text = form.value.user_prompt || ''
    form.value.user_prompt = text.substring(0, start) + name + text.substring(end)
    
    // 恢复光标位置
    await nextTick()
    textarea.focus()
    textarea.setSelectionRange(start + name.length, start + name.length)
  } else {
    // 如果无法获取光标位置，追加到末尾
    form.value.user_prompt = (form.value.user_prompt || '') + name
  }
}

const resetForm = () => {
  form.value = { ...originalForm.value }
  ElMessage.info('已重置为保存的配置')
}

const handleSave = async () => {
  if (!props.moduleCode) return

  if (!form.value.user_prompt) {
    ElMessage.warning('用户提示词不能为空')
    return
  }

  saving.value = true
  try {
    await updatePromptModule(props.moduleCode, form.value)
    ElMessage.success('保存成功')
    emit('saved')
    handleClose()
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || '保存失败'
    ElMessage.error(errorMsg)
  } finally {
    saving.value = false
  }
}

const handleClose = () => {
  visible.value = false
  moduleInfo.value = null
}
</script>

<style scoped>
.module-info {
  margin-bottom: 16px;
}

.module-desc {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #606266;
}

.ai-interface-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-interface-info .label {
  font-size: 14px;
  color: #909399;
}

.prompt-form {
  max-width: 100%;
}

.form-item-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.placeholders-list {
  line-height: 2;
}

.placeholder-tag {
  cursor: pointer;
  margin-right: 8px;
  margin-bottom: 4px;
}

.placeholder-tag:hover {
  background-color: #ecf5ff;
  border-color: #409eff;
}
</style>
