<template>
  <el-dialog
    v-model="visible"
    :title="dialogTitle"
    width="600px"
    append-to-body
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
    >
      <el-form-item label="导向名称" prop="name">
        <el-input
          v-model="form.name"
          placeholder="请输入导向名称（最多100字符）"
          maxlength="100"
          show-word-limit
        />
      </el-form-item>
      
      <el-form-item label="导向类别" prop="category">
        <el-select
          v-model="form.category"
          placeholder="请选择导向类别"
          style="width: 100%"
        >
          <el-option label="基准阶梯" value="benchmark_ladder">
            <div>
              <div>基准阶梯</div>
              <div style="font-size: 12px; color: #999;">
                需要配置科室基准值和阶梯规则
              </div>
            </div>
          </el-option>
          <el-option label="直接阶梯" value="direct_ladder">
            <div>
              <div>直接阶梯</div>
              <div style="font-size: 12px; color: #999;">
                仅需要配置阶梯规则
              </div>
            </div>
          </el-option>
          <el-option label="其他" value="other">
            <div>
              <div>其他</div>
              <div style="font-size: 12px; color: #999;">
                不需要配置基准和阶梯
              </div>
            </div>
          </el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="导向规则描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="6"
          placeholder="请输入导向规则描述（最多1024字符）"
          maxlength="1024"
          show-word-limit
        />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitting">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed, type PropType } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import request from '@/utils/request'

interface OrientationRule {
  id: number
  name: string
  category: 'benchmark_ladder' | 'direct_ladder' | 'other'
  description?: string
  created_at: string
  updated_at: string
}

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  rule: {
    type: Object as PropType<OrientationRule | null>,
    default: null
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const dialogTitle = computed(() => props.isEdit ? '编辑导向规则' : '新增导向规则')

const formRef = ref<FormInstance>()
const submitting = ref(false)

const form = reactive({
  name: '',
  category: '' as 'benchmark_ladder' | 'direct_ladder' | 'other' | '',
  description: ''
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入导向名称', trigger: 'blur' },
    { max: 100, message: '导向名称不能超过100个字符', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择导向类别', trigger: 'change' }
  ],
  description: [
    { max: 1024, message: '导向规则描述不能超过1024个字符', trigger: 'blur' }
  ]
}

// 监听 rule 变化，更新表单
watch(() => props.rule, (newRule) => {
  if (newRule) {
    form.name = newRule.name
    form.category = newRule.category
    form.description = newRule.description || ''
  }
}, { immediate: true })

// 监听对话框打开，重置表单
watch(visible, (newVal) => {
  if (newVal && !props.isEdit) {
    resetForm()
  }
})

// 重置表单
const resetForm = () => {
  form.name = ''
  form.category = ''
  form.description = ''
  formRef.value?.clearValidate()
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      const submitData = {
        name: form.name,
        category: form.category,
        description: form.description || undefined
      }

      if (props.isEdit && props.rule) {
        await request.put(`/orientation-rules/${props.rule.id}`, submitData)
        ElMessage.success('更新成功')
      } else {
        await request.post('/orientation-rules', submitData)
        ElMessage.success('创建成功')
      }
      
      visible.value = false
      emit('success')
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || (props.isEdit ? '更新失败' : '创建失败'))
    } finally {
      submitting.value = false
    }
  })
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
  resetForm()
}
</script>

<style scoped>
:deep(.el-select-dropdown__item) {
  height: auto;
  padding: 10px 20px;
}
</style>
