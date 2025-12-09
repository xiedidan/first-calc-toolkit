<template>
  <div class="ai-config">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>AI接口配置</span>
          <el-button
            v-if="hasConfig"
            type="primary"
            size="small"
            @click="showUsageStats"
          >
            查看使用统计
          </el-button>
        </div>
      </template>

      <el-form
        ref="configFormRef"
        :model="configForm"
        :rules="configRules"
        label-width="140px"
        style="max-width: 800px; padding: 20px;"
      >
        <el-form-item label="API访问端点" prop="api_endpoint">
          <el-input
            v-model="configForm.api_endpoint"
            placeholder="例如：https://api.deepseek.com/v1"
          />
          <div class="form-item-tip">
            DeepSeek API端点或其他OpenAI兼容的API端点
          </div>
        </el-form-item>

        <el-form-item label="AI模型" prop="model_name">
          <el-input
            v-model="configForm.model_name"
            placeholder="例如：deepseek-chat"
          />
          <div class="form-item-tip">
            DeepSeek模型：deepseek-chat、deepseek-reasoner；OpenAI模型：gpt-4o、gpt-4o-mini
          </div>
        </el-form-item>

        <el-form-item label="API密钥" prop="api_key">
          <el-input
            v-model="configForm.api_key"
            type="password"
            :placeholder="hasConfig ? '留空表示不修改密钥' : '请输入API密钥'"
            autocomplete="new-password"
          />
          <div class="form-item-tip">
            密钥将加密存储，不会传输到前端显示
          </div>
        </el-form-item>

        <el-form-item label="调用延迟（秒）" prop="call_delay">
          <el-input-number
            v-model="configForm.call_delay"
            :min="0.1"
            :max="10"
            :step="0.1"
            :precision="1"
          />
          <div class="form-item-tip">
            每次AI调用之间的延迟时间，避免超出频率限制
          </div>
        </el-form-item>

        <el-form-item label="每日调用限额" prop="daily_limit">
          <el-input-number
            v-model="configForm.daily_limit"
            :min="1"
            :max="100000"
            :step="100"
          />
          <div class="form-item-tip">
            每日最大API调用次数，达到限额后将暂停任务
          </div>
        </el-form-item>

        <el-form-item label="批次大小" prop="batch_size">
          <el-input-number
            v-model="configForm.batch_size"
            :min="1"
            :max="100"
            :step="5"
          />
          <div class="form-item-tip">
            每次AI调用处理的项目数量（建议10-30，过大可能导致响应超时）
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveConfig" :loading="saving">
            保存配置
          </el-button>
          <el-button @click="testConfig" :loading="testing" :disabled="!hasConfig">
            测试配置
          </el-button>
          <el-button @click="loadConfig">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 提示词配置 -->
    <el-card class="config-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>提示词配置</span>
        </div>
      </template>

      <div style="padding: 20px;">
        <el-tabs v-model="activePromptCategory" @tab-change="onPromptCategoryChange">
          <el-tab-pane
            v-for="cat in promptCategories"
            :key="cat.category"
            :label="cat.name"
            :name="cat.category"
          >
            <div class="prompt-category-desc">
              {{ cat.description }}
            </div>
            <div class="prompt-placeholders">
              <span class="placeholder-label">支持的占位符：</span>
              <el-tag
                v-for="ph in cat.placeholders"
                :key="ph"
                size="small"
                type="info"
                style="margin-right: 8px; margin-bottom: 4px;"
              >
                {{ ph }}
              </el-tag>
            </div>
          </el-tab-pane>
        </el-tabs>

        <el-form
          ref="promptFormRef"
          :model="promptForm"
          label-width="120px"
          style="max-width: 800px; margin-top: 20px;"
        >
          <el-form-item label="系统提示词">
            <el-input
              v-model="promptForm.system_prompt"
              type="textarea"
              :rows="6"
              placeholder="定义AI的角色和输出格式要求"
            />
          </el-form-item>

          <el-form-item label="用户提示词" required>
            <el-input
              v-model="promptForm.user_prompt"
              type="textarea"
              :rows="12"
              placeholder="请输入提示词模板，可使用上方列出的占位符"
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="savePromptConfig" :loading="savingPrompt">
              保存提示词
            </el-button>
            <el-button @click="resetPromptConfig">重置为默认</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>

    <!-- 测试对话框 -->
    <el-dialog
      v-model="testDialogVisible"
      title="测试AI配置"
      width="600px"
      append-to-body
    >
      <el-form :model="testForm" label-width="120px">
        <el-form-item label="测试项目名称">
          <el-input
            v-model="testForm.item_name"
            placeholder="例如：CT检查"
          />
        </el-form-item>
      </el-form>

      <div v-if="testResult" class="test-result">
        <el-alert
          :type="testResult.success ? 'success' : 'error'"
          :title="testResult.success ? '测试成功' : '测试失败'"
          :closable="false"
        >
          <template v-if="testResult.success">
            <div><strong>建议维度ID：</strong>{{ testResult.dimension_id }}</div>
            <div><strong>确信度：</strong>{{ testResult.confidence ? (testResult.confidence * 100).toFixed(2) : 0 }}%</div>
            <div><strong>响应时间：</strong>{{ testResult.response_time?.toFixed(0) || 0 }}ms</div>
          </template>
          <template v-else>
            <div>{{ testResult.error }}</div>
          </template>
        </el-alert>
      </div>

      <template #footer>
        <el-button @click="testDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="runTest" :loading="testing">
          执行测试
        </el-button>
      </template>
    </el-dialog>

    <!-- 使用统计对话框 -->
    <el-dialog
      v-model="statsDialogVisible"
      title="API使用统计"
      width="500px"
      append-to-body
    >
      <div v-if="usageStats" class="usage-stats">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="今日调用次数">
            {{ usageStats.today_calls }}
          </el-descriptions-item>
          <el-descriptions-item label="每日限额">
            {{ usageStats.today_limit }}
          </el-descriptions-item>
          <el-descriptions-item label="剩余次数">
            <span :class="{ 'text-danger': usageStats.remaining_calls < 100 }">
              {{ usageStats.remaining_calls }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="预估成本">
            ¥{{ usageStats.estimated_cost.toFixed(2) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <template #footer>
        <el-button type="primary" @click="statsDialogVisible = false">
          关闭
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import {
  getAIConfig,
  createOrUpdateAIConfig,
  testAIConfig,
  getAPIUsageStats,
  type AIConfig,
  type TestResultDisplay,
  type APIUsageStats
} from '@/api/ai-config'
import {
  getPromptCategories,
  getAllPromptConfigs,
  savePromptConfig as savePromptConfigApi,
  type AIPromptCategoryInfo,
  type AIPromptConfig
} from '@/api/ai-prompt-config'

const configFormRef = ref<FormInstance>()
const promptFormRef = ref<FormInstance>()
const saving = ref(false)
const savingPrompt = ref(false)
const testing = ref(false)
const hasConfig = ref(false)

const configForm = ref({
  api_endpoint: '',
  model_name: '',
  api_key: '',
  call_delay: 1.0,
  daily_limit: 10000,
  batch_size: 20,
})

// 提示词配置
const promptCategories = ref<AIPromptCategoryInfo[]>([])
const promptConfigs = ref<AIPromptConfig[]>([])
const activePromptCategory = ref('classification')
const promptForm = ref({
  system_prompt: '',
  user_prompt: '',
})

// 自定义API密钥验证器
const validateApiKey = (_rule: any, value: string, callback: any) => {
  if (hasConfig.value && !value) {
    callback()
    return
  }
  if (!value) {
    callback(new Error('API密钥不能为空'))
    return
  }
  if (value.length < 20) {
    callback(new Error('API密钥长度至少20个字符'))
    return
  }
  callback()
}

const configRules: FormRules = {
  api_endpoint: [
    { required: true, message: 'API端点不能为空', trigger: 'blur' },
    {
      pattern: /^https?:\/\/.+/,
      message: 'API端点必须是有效的URL',
      trigger: 'blur',
    },
  ],
  model_name: [
    { required: true, message: 'AI模型不能为空', trigger: 'blur' },
  ],
  api_key: [
    { validator: validateApiKey, trigger: 'blur' },
  ],
  call_delay: [
    { required: true, message: '调用延迟不能为空', trigger: 'blur' },
  ],
  daily_limit: [
    { required: true, message: '每日限额不能为空', trigger: 'blur' },
  ],
  batch_size: [
    { required: true, message: '批次大小不能为空', trigger: 'blur' },
  ],
}

// 测试对话框
const testDialogVisible = ref(false)
const testForm = ref({
  item_name: 'CT检查',
})
const testResult = ref<TestResultDisplay | null>(null)

// 统计对话框
const statsDialogVisible = ref(false)
const usageStats = ref<APIUsageStats | null>(null)

const loadConfig = async () => {
  try {
    const data = await getAIConfig()
    if (data) {
      configForm.value.api_endpoint = data.api_endpoint
      configForm.value.model_name = data.model_name || 'deepseek-chat'
      configForm.value.api_key = ''
      configForm.value.call_delay = data.call_delay
      configForm.value.daily_limit = data.daily_limit
      configForm.value.batch_size = data.batch_size
      hasConfig.value = true
    } else {
      configForm.value.api_endpoint = 'https://api.deepseek.com/v1/chat/completions'
      configForm.value.model_name = 'deepseek-chat'
      configForm.value.api_key = ''
      hasConfig.value = false
    }
  } catch (error) {
    ElMessage.error('加载配置失败')
    console.error(error)
  }
}

const loadPromptCategories = async () => {
  try {
    promptCategories.value = await getPromptCategories()
    if (promptCategories.value.length > 0) {
      activePromptCategory.value = promptCategories.value[0].category
    }
  } catch (error) {
    console.error('加载提示词分类失败:', error)
  }
}

const loadPromptConfigs = async () => {
  try {
    promptConfigs.value = await getAllPromptConfigs()
    updatePromptForm()
  } catch (error) {
    console.error('加载提示词配置失败:', error)
  }
}

const updatePromptForm = () => {
  const config = promptConfigs.value.find(c => c.category === activePromptCategory.value)
  if (config) {
    promptForm.value.system_prompt = config.system_prompt || ''
    promptForm.value.user_prompt = config.user_prompt || ''
  } else {
    promptForm.value.system_prompt = ''
    promptForm.value.user_prompt = ''
  }
}

const onPromptCategoryChange = () => {
  updatePromptForm()
}

const saveConfig = async () => {
  if (!configFormRef.value) return

  await configFormRef.value.validate(async (valid) => {
    if (!valid) return

    saving.value = true
    try {
      // 构建保存数据，包含当前分类的提示词
      const currentPromptConfig = promptConfigs.value.find(
        c => c.category === 'classification'
      )
      
      await createOrUpdateAIConfig({
        ...configForm.value,
        system_prompt: currentPromptConfig?.system_prompt || '',
        prompt_template: currentPromptConfig?.user_prompt || '',
      })
      ElMessage.success('保存成功')
      await loadConfig()
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || '保存失败'
      ElMessage.error(errorMsg)
      console.error(error)
    } finally {
      saving.value = false
    }
  })
}

const savePromptConfig = async () => {
  if (!promptForm.value.user_prompt) {
    ElMessage.warning('用户提示词不能为空')
    return
  }

  savingPrompt.value = true
  try {
    await savePromptConfigApi(activePromptCategory.value, {
      system_prompt: promptForm.value.system_prompt || null,
      user_prompt: promptForm.value.user_prompt,
    })
    ElMessage.success('提示词保存成功')
    await loadPromptConfigs()
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || '保存失败'
    ElMessage.error(errorMsg)
    console.error(error)
  } finally {
    savingPrompt.value = false
  }
}

const resetPromptConfig = () => {
  // 重新加载配置以恢复默认值
  loadPromptConfigs()
  ElMessage.info('已重置为保存的配置')
}

const testConfig = () => {
  testResult.value = null
  testDialogVisible.value = true
}

const runTest = async () => {
  if (!testForm.value.item_name) {
    ElMessage.warning('请输入测试项目名称')
    return
  }

  testing.value = true
  try {
    const res = await testAIConfig({
      test_item_name: testForm.value.item_name,
    })
    if (res.success && res.result) {
      testResult.value = {
        success: true,
        dimension_id: res.result.dimension_id,
        confidence: res.result.confidence,
        response_time: res.duration ? res.duration * 1000 : 0,
      }
    } else {
      testResult.value = {
        success: false,
        error: res.message || res.error || '测试失败',
      }
    }
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || '测试失败'
    testResult.value = {
      success: false,
      error: errorMsg,
    }
  } finally {
    testing.value = false
  }
}

const showUsageStats = async () => {
  try {
    usageStats.value = await getAPIUsageStats()
    statsDialogVisible.value = true
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || '获取统计失败'
    ElMessage.error(errorMsg)
    console.error(error)
  }
}

onMounted(async () => {
  await loadConfig()
  await loadPromptCategories()
  await loadPromptConfigs()
})
</script>

<style scoped>
.ai-config {
  padding: 0;
  width: 100%;
  height: 100%;
  overflow-y: auto;
}

.config-card {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-item-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.prompt-category-desc {
  color: #606266;
  font-size: 14px;
  margin-bottom: 12px;
}

.prompt-placeholders {
  margin-bottom: 16px;
}

.placeholder-label {
  color: #909399;
  font-size: 13px;
  margin-right: 8px;
}

.test-result {
  margin-top: 20px;
}

.test-result :deep(.el-alert__content) {
  line-height: 1.8;
}

.usage-stats {
  padding: 10px 0;
}

.text-danger {
  color: #f56c6c;
  font-weight: bold;
}
</style>
