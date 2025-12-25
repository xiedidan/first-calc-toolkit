<template>
  <div class="ai-config">
    <!-- AI接口管理 -->
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>AI接口管理</span>
          <el-button type="primary" size="small" @click="showCreateInterfaceDialog">
            <el-icon><Plus /></el-icon>
            新建接口
          </el-button>
        </div>
      </template>

      <el-table
        :data="interfaces"
        v-loading="loadingInterfaces"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="name" label="接口名称" width="150" />
        <el-table-column prop="api_endpoint" label="API端点" min-width="200" show-overflow-tooltip />
        <el-table-column prop="model_name" label="模型名称" width="150" />
        <el-table-column prop="api_key_masked" label="API密钥" width="150" />
        <el-table-column prop="call_delay" label="调用延迟" width="100">
          <template #default="{ row }">{{ row.call_delay }}秒</template>
        </el-table-column>
        <el-table-column prop="daily_limit" label="每日限额" width="100" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="引用模块" min-width="150">
          <template #default="{ row }">
            <el-tag
              v-for="mod in row.referenced_modules"
              :key="mod"
              size="small"
              type="info"
              style="margin-right: 4px; margin-bottom: 2px;"
            >
              {{ mod }}
            </el-tag>
            <span v-if="!row.referenced_modules?.length" class="text-muted">未被引用</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="testInterface(row)">
              测试
            </el-button>
            <el-button type="primary" link size="small" @click="editInterface(row)">
              编辑
            </el-button>
            <el-button
              type="danger"
              link
              size="small"
              @click="deleteInterface(row)"
              :disabled="row.referenced_modules?.length > 0"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 提示词模块配置 -->
    <el-card class="config-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>提示词模块配置</span>
        </div>
      </template>

      <div class="module-config-container">
        <!-- 左侧模块列表 -->
        <div class="module-list">
          <div
            v-for="group in moduleGroups"
            :key="group.name"
            class="module-group"
          >
            <div class="group-title">{{ group.name }}</div>
            <div
              v-for="mod in group.modules"
              :key="mod.module_code"
              class="module-item"
              :class="{ active: selectedModule?.module_code === mod.module_code }"
              @click="selectModule(mod)"
            >
              <div class="module-name">{{ mod.module_name }}</div>
              <div class="module-status">
                <el-tag
                  :type="mod.is_configured ? 'success' : 'warning'"
                  size="small"
                >
                  {{ mod.is_configured ? '已配置' : '未配置' }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧配置详情 -->
        <div class="module-detail" v-if="selectedModule">
          <div class="module-header">
            <h3>{{ selectedModule.module_name }}</h3>
            <p class="module-desc">{{ selectedModule.description }}</p>
          </div>

          <el-form
            ref="moduleFormRef"
            :model="moduleForm"
            label-width="120px"
            class="module-form"
          >
            <el-form-item label="AI接口">
              <el-select
                v-model="moduleForm.ai_interface_id"
                placeholder="请选择AI接口"
                clearable
                style="width: 100%;"
              >
                <el-option
                  v-for="iface in activeInterfaces"
                  :key="iface.id"
                  :label="`${iface.name} (${iface.model_name})`"
                  :value="iface.id"
                />
              </el-select>
              <div class="form-item-tip" v-if="!moduleForm.ai_interface_id">
                未配置AI接口时，该模块功能将无法使用
              </div>
            </el-form-item>

            <el-form-item label="模型温度">
              <el-slider
                v-model="moduleForm.temperature"
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
                  v-for="ph in selectedModule.placeholders"
                  :key="ph.name"
                  size="small"
                  type="info"
                  style="margin-right: 8px; margin-bottom: 4px;"
                >
                  {{ ph.name }}
                  <el-tooltip :content="ph.description" placement="top">
                    <el-icon style="margin-left: 4px;"><QuestionFilled /></el-icon>
                  </el-tooltip>
                </el-tag>
              </div>
            </el-form-item>

            <el-form-item label="系统提示词">
              <el-input
                v-model="moduleForm.system_prompt"
                type="textarea"
                :rows="10"
                placeholder="定义AI的角色和输出格式要求（可选）"
              />
            </el-form-item>

            <el-form-item label="用户提示词" required>
              <el-input
                v-model="moduleForm.user_prompt"
                type="textarea"
                :rows="10"
                placeholder="请输入提示词模板，可使用上方列出的占位符"
              />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="saveModuleConfig" :loading="savingModule">
                保存配置
              </el-button>
              <el-button @click="resetModuleForm">重置</el-button>
            </el-form-item>
          </el-form>
        </div>

        <div class="module-detail empty" v-else>
          <el-empty description="请从左侧选择一个模块进行配置" />
        </div>
      </div>
    </el-card>

    <!-- 创建/编辑AI接口对话框 -->
    <el-dialog
      v-model="interfaceDialogVisible"
      :title="editingInterface ? '编辑AI接口' : '新建AI接口'"
      width="600px"
      append-to-body
    >
      <el-form
        ref="interfaceFormRef"
        :model="interfaceForm"
        :rules="interfaceRules"
        label-width="120px"
      >
        <el-form-item label="接口名称" prop="name">
          <el-input v-model="interfaceForm.name" placeholder="例如：DeepSeek主接口" />
        </el-form-item>

        <el-form-item label="API端点" prop="api_endpoint">
          <el-input
            v-model="interfaceForm.api_endpoint"
            placeholder="例如：https://api.deepseek.com/v1"
          />
          <div class="form-item-tip">
            DeepSeek API端点或其他OpenAI兼容的API端点
          </div>
        </el-form-item>

        <el-form-item label="模型名称" prop="model_name">
          <el-input v-model="interfaceForm.model_name" placeholder="例如：deepseek-chat" />
          <div class="form-item-tip">
            DeepSeek模型：deepseek-chat、deepseek-reasoner；OpenAI模型：gpt-4o、gpt-4o-mini
          </div>
        </el-form-item>

        <el-form-item label="API密钥" prop="api_key">
          <el-input
            v-model="interfaceForm.api_key"
            type="password"
            :placeholder="editingInterface ? '留空表示不修改密钥' : '请输入API密钥'"
            autocomplete="new-password"
            show-password
          />
          <div v-if="editingInterface" class="form-item-tip">
            当前密钥：{{ editingInterface.api_key_masked }}
          </div>
        </el-form-item>

        <el-form-item label="调用延迟" prop="call_delay">
          <el-input-number
            v-model="interfaceForm.call_delay"
            :min="0.1"
            :max="10"
            :step="0.1"
            :precision="1"
          />
          <span style="margin-left: 8px;">秒</span>
          <div class="form-item-tip">
            每次AI调用之间的延迟时间，避免超出频率限制
          </div>
        </el-form-item>

        <el-form-item label="每日限额" prop="daily_limit">
          <el-input-number
            v-model="interfaceForm.daily_limit"
            :min="1"
            :max="100000"
            :step="100"
          />
          <span style="margin-left: 8px;">次</span>
        </el-form-item>

        <el-form-item label="启用状态" prop="is_active">
          <el-switch v-model="interfaceForm.is_active" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="interfaceDialogVisible = false">取消</el-button>
        <el-button @click="testInterfaceInDialog" :loading="testingInDialog">
          测试配置
        </el-button>
        <el-button type="primary" @click="saveInterface" :loading="savingInterface">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 对话框内测试结果 -->
    <el-dialog
      v-model="dialogTestResultVisible"
      title="测试结果"
      width="500px"
      append-to-body
    >
      <el-alert
        v-if="dialogTestResult"
        :type="dialogTestResult.success ? 'success' : 'error'"
        :title="dialogTestResult.success ? '测试成功' : '测试失败'"
        :closable="false"
      >
        <template v-if="dialogTestResult.success">
          <div><strong>响应内容：</strong></div>
          <div class="test-response">{{ dialogTestResult.response_content }}</div>
          <div><strong>响应时间：</strong>{{ (dialogTestResult.response_time || 0).toFixed(2) }}秒</div>
        </template>
        <template v-else>
          <div>{{ dialogTestResult.error_message }}</div>
        </template>
      </el-alert>
      <template #footer>
        <el-button @click="dialogTestResultVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 测试AI接口对话框 -->
    <el-dialog
      v-model="testDialogVisible"
      title="测试AI接口"
      width="600px"
      append-to-body
    >
      <div v-if="testingInterface" class="test-interface-info">
        <p><strong>接口名称：</strong>{{ testingInterface.name }}</p>
        <p><strong>模型：</strong>{{ testingInterface.model_name }}</p>
      </div>

      <el-form :model="testForm" label-width="100px">
        <el-form-item label="测试消息">
          <el-input
            v-model="testForm.test_message"
            type="textarea"
            :rows="3"
            placeholder="请输入测试消息"
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
            <div><strong>响应内容：</strong></div>
            <div class="test-response">{{ testResult.response_content }}</div>
            <div><strong>响应时间：</strong>{{ (testResult.response_time || 0).toFixed(2) }}秒</div>
          </template>
          <template v-else>
            <div>{{ testResult.error_message }}</div>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, QuestionFilled } from '@element-plus/icons-vue'
import {
  getAIInterfaces,
  createAIInterface,
  updateAIInterface,
  deleteAIInterface as deleteAIInterfaceApi,
  testAIInterface,
  testAIInterfaceConfig,
  type AIInterface,
  type AIInterfaceCreate,
  type AIInterfaceUpdate,
  type AIInterfaceTestResponse,
} from '@/api/ai-interfaces'
import {
  getPromptModules,
  updatePromptModule,
  type AIPromptModule,
  type AIPromptModuleUpdate,
  PromptModuleCode,
} from '@/api/ai-prompt-modules'

// ============ AI接口管理 ============
const interfaces = ref<AIInterface[]>([])
const loadingInterfaces = ref(false)
const interfaceDialogVisible = ref(false)
const editingInterface = ref<AIInterface | null>(null)
const savingInterface = ref(false)
const interfaceFormRef = ref<FormInstance>()

const interfaceForm = ref<AIInterfaceCreate & { is_active: boolean }>({
  name: '',
  api_endpoint: 'https://api.deepseek.com/v1',
  model_name: 'deepseek-chat',
  api_key: '',
  call_delay: 1.0,
  daily_limit: 10000,
  is_active: true,
})

// 自定义API密钥验证器
const validateApiKey = (_rule: any, value: string, callback: any) => {
  if (editingInterface.value && !value) {
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

const interfaceRules: FormRules = {
  name: [
    { required: true, message: '接口名称不能为空', trigger: 'blur' },
  ],
  api_endpoint: [
    { required: true, message: 'API端点不能为空', trigger: 'blur' },
    { pattern: /^https?:\/\/.+/, message: 'API端点必须是有效的URL', trigger: 'blur' },
  ],
  model_name: [
    { required: true, message: '模型名称不能为空', trigger: 'blur' },
  ],
  api_key: [
    { validator: validateApiKey, trigger: 'blur' },
  ],
}

// 对话框内测试相关
const testingInDialog = ref(false)
const dialogTestResultVisible = ref(false)
const dialogTestResult = ref<AIInterfaceTestResponse | null>(null)

// 获取启用的接口列表（用于模块配置选择）
const activeInterfaces = computed(() => {
  return interfaces.value.filter(i => i.is_active)
})

const loadInterfaces = async () => {
  loadingInterfaces.value = true
  try {
    const res: any = await getAIInterfaces()
    // 后端返回 { code, message, data: { items, total } }
    const data = res.data || res
    interfaces.value = data.items || []
  } catch (error) {
    console.error('加载AI接口列表失败:', error)
    ElMessage.error('加载AI接口列表失败')
  } finally {
    loadingInterfaces.value = false
  }
}

const showCreateInterfaceDialog = () => {
  editingInterface.value = null
  interfaceForm.value = {
    name: '',
    api_endpoint: 'https://api.deepseek.com/v1',
    model_name: 'deepseek-chat',
    api_key: '',
    call_delay: 1.0,
    daily_limit: 10000,
    is_active: true,
  }
  interfaceDialogVisible.value = true
}

const editInterface = (row: AIInterface) => {
  editingInterface.value = row
  interfaceForm.value = {
    name: row.name,
    api_endpoint: row.api_endpoint,
    model_name: row.model_name,
    api_key: '',
    call_delay: row.call_delay,
    daily_limit: row.daily_limit,
    is_active: row.is_active,
  }
  interfaceDialogVisible.value = true
}

const saveInterface = async () => {
  if (!interfaceFormRef.value) return

  await interfaceFormRef.value.validate(async (valid) => {
    if (!valid) return

    savingInterface.value = true
    try {
      if (editingInterface.value) {
        // 更新
        const updateData: AIInterfaceUpdate = {
          name: interfaceForm.value.name,
          api_endpoint: interfaceForm.value.api_endpoint,
          model_name: interfaceForm.value.model_name,
          call_delay: interfaceForm.value.call_delay,
          daily_limit: interfaceForm.value.daily_limit,
          is_active: interfaceForm.value.is_active,
        }
        if (interfaceForm.value.api_key) {
          updateData.api_key = interfaceForm.value.api_key
        }
        await updateAIInterface(editingInterface.value.id, updateData)
        ElMessage.success('更新成功')
      } else {
        // 创建
        await createAIInterface(interfaceForm.value)
        ElMessage.success('创建成功')
      }
      interfaceDialogVisible.value = false
      await loadInterfaces()
      // 重新加载模块配置以更新接口引用信息
      await loadModules()
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || '保存失败'
      ElMessage.error(errorMsg)
    } finally {
      savingInterface.value = false
    }
  })
}

const deleteInterface = async (row: AIInterface) => {
  if (row.referenced_modules?.length > 0) {
    ElMessage.warning('该接口被模块引用，无法删除')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除接口"${row.name}"吗？`,
      '确认删除',
      { type: 'warning' }
    )
    await deleteAIInterfaceApi(row.id)
    ElMessage.success('删除成功')
    await loadInterfaces()
  } catch (error: any) {
    if (error !== 'cancel') {
      const errorMsg = error.response?.data?.detail || '删除失败'
      ElMessage.error(errorMsg)
    }
  }
}

// 对话框内测试配置（保存前测试）
const testInterfaceInDialog = async () => {
  // 验证必填字段
  if (!interfaceForm.value.api_endpoint) {
    ElMessage.warning('请填写API端点')
    return
  }
  if (!interfaceForm.value.model_name) {
    ElMessage.warning('请填写模型名称')
    return
  }
  
  // 编辑模式下，如果没有填写新密钥，则使用已保存的密钥（通过 interface_id）
  // 新建模式下，必须填写密钥
  if (!interfaceForm.value.api_key && !editingInterface.value) {
    ElMessage.warning('请填写API密钥')
    return
  }

  testingInDialog.value = true
  dialogTestResult.value = null
  
  try {
    const testParams: any = {
      api_endpoint: interfaceForm.value.api_endpoint,
      model_name: interfaceForm.value.model_name,
      test_message: '你好，请简单介绍一下你自己。',
    }
    
    // 如果填写了新密钥，使用新密钥；否则传递 interface_id 让后端从数据库获取
    if (interfaceForm.value.api_key) {
      testParams.api_key = interfaceForm.value.api_key
    } else if (editingInterface.value) {
      testParams.interface_id = editingInterface.value.id
    }
    
    const res: any = await testAIInterfaceConfig(testParams)
    // 后端返回 { code, message, data }，需要从 data 中获取测试结果
    dialogTestResult.value = res.data || res
    dialogTestResultVisible.value = true
  } catch (error: any) {
    dialogTestResult.value = {
      success: false,
      error_message: error.response?.data?.detail || '测试失败',
    }
    dialogTestResultVisible.value = true
  } finally {
    testingInDialog.value = false
  }
}

// ============ 测试AI接口 ============
const testDialogVisible = ref(false)
const testingInterface = ref<AIInterface | null>(null)
const testing = ref(false)
const testForm = ref({
  test_message: '你好，请简单介绍一下你自己。',
})
const testResult = ref<AIInterfaceTestResponse | null>(null)

const testInterface = (row: AIInterface) => {
  testingInterface.value = row
  testResult.value = null
  testDialogVisible.value = true
}

const runTest = async () => {
  if (!testingInterface.value) return

  testing.value = true
  testResult.value = null
  try {
    const res: any = await testAIInterface(testingInterface.value.id, {
      test_message: testForm.value.test_message,
    })
    // 后端返回 { code, message, data }，需要从 data 中获取测试结果
    testResult.value = res.data || res
  } catch (error: any) {
    testResult.value = {
      success: false,
      error_message: error.response?.data?.detail || '测试失败',
    }
  } finally {
    testing.value = false
  }
}

// ============ 提示词模块配置 ============
const modules = ref<AIPromptModule[]>([])
const selectedModule = ref<AIPromptModule | null>(null)
const savingModule = ref(false)
const moduleFormRef = ref<FormInstance>()

const moduleForm = ref<AIPromptModuleUpdate>({
  ai_interface_id: null,
  temperature: 0.7,
  system_prompt: '',
  user_prompt: '',
})

// 按分组组织模块
const moduleGroups = computed(() => {
  const groups = [
    {
      name: '智能分类分级',
      codes: [PromptModuleCode.CLASSIFICATION],
      modules: [] as AIPromptModule[],
    },
    {
      name: '业务价值报表',
      codes: [PromptModuleCode.REPORT_ISSUES, PromptModuleCode.REPORT_PLANS],
      modules: [] as AIPromptModule[],
    },
    {
      name: '智能问数系统',
      codes: [PromptModuleCode.QUERY_KEYWORD, PromptModuleCode.QUERY_CALIBER, PromptModuleCode.QUERY_DATA, PromptModuleCode.QUERY_SQL],
      modules: [] as AIPromptModule[],
    },
  ]

  // 按 codes 数组顺序添加模块
  for (const group of groups) {
    for (const code of group.codes) {
      const mod = modules.value.find(m => m.module_code === code)
      if (mod) {
        group.modules.push(mod)
      }
    }
  }

  return groups.filter(g => g.modules.length > 0)
})

const loadModules = async () => {
  try {
    const res: any = await getPromptModules()
    // 后端返回 { code, message, data: { items, total } }
    const data = res.data || res
    modules.value = data.items || []
    // 如果有选中的模块，更新其数据
    if (selectedModule.value) {
      const updated = modules.value.find(m => m.module_code === selectedModule.value?.module_code)
      if (updated) {
        selectedModule.value = updated
        updateModuleForm()
      }
    }
  } catch (error) {
    console.error('加载提示词模块失败:', error)
    ElMessage.error('加载提示词模块失败')
  }
}

const selectModule = (mod: AIPromptModule) => {
  selectedModule.value = mod
  updateModuleForm()
}

const updateModuleForm = () => {
  if (!selectedModule.value) return
  moduleForm.value = {
    ai_interface_id: selectedModule.value.ai_interface_id,
    temperature: selectedModule.value.temperature,
    system_prompt: selectedModule.value.system_prompt || '',
    user_prompt: selectedModule.value.user_prompt || '',
  }
}

const resetModuleForm = () => {
  updateModuleForm()
  ElMessage.info('已重置为保存的配置')
}

const saveModuleConfig = async () => {
  if (!selectedModule.value) return

  if (!moduleForm.value.user_prompt) {
    ElMessage.warning('用户提示词不能为空')
    return
  }

  savingModule.value = true
  try {
    await updatePromptModule(selectedModule.value.module_code, moduleForm.value)
    ElMessage.success('保存成功')
    await loadModules()
    // 重新加载接口列表以更新引用信息
    await loadInterfaces()
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || '保存失败'
    ElMessage.error(errorMsg)
  } finally {
    savingModule.value = false
  }
}

// ============ 初始化 ============
onMounted(async () => {
  await Promise.all([loadInterfaces(), loadModules()])
})
</script>

<style scoped>
.ai-config {
  padding: 0;
}

.config-card {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.text-muted {
  color: #909399;
  font-size: 12px;
}

.form-item-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* 模块配置布局 */
.module-config-container {
  display: flex;
  min-height: 500px;
}

.module-list {
  width: 280px;
  border-right: 1px solid #ebeef5;
  padding-right: 20px;
}

.module-group {
  margin-bottom: 20px;
}

.group-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 10px;
  padding-left: 10px;
}

.module-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  margin-bottom: 4px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.module-item:hover {
  background-color: #f5f7fa;
}

.module-item.active {
  background-color: #ecf5ff;
  border-left: 3px solid #409eff;
}

.module-name {
  font-size: 14px;
  color: #606266;
}

.module-detail {
  flex: 1;
  padding-left: 20px;
}

.module-detail.empty {
  display: flex;
  align-items: center;
  justify-content: center;
}

.module-header {
  margin-bottom: 20px;
}

.module-header h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #303133;
}

.module-desc {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.module-form {
  max-width: 700px;
}

.placeholders-list {
  line-height: 2;
}

/* 测试对话框 */
.test-interface-info {
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 16px;
}

.test-interface-info p {
  margin: 4px 0;
  font-size: 14px;
}

.test-result {
  margin-top: 16px;
}

.test-result :deep(.el-alert__content) {
  line-height: 1.8;
}

.test-response {
  background-color: #f5f7fa;
  padding: 8px 12px;
  border-radius: 4px;
  margin: 8px 0;
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
