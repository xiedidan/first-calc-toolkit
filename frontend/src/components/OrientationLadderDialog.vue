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
      <el-form-item label="所属导向" prop="rule_id">
        <el-select
          v-model="form.rule_id"
          placeholder="请选择所属导向"
          filterable
          style="width: 100%"
          :disabled="isEdit"
        >
          <el-option
            v-for="rule in ladderRules"
            :key="rule.id"
            :label="rule.name"
            :value="rule.id"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item label="阶梯次序" prop="ladder_order">
        <el-input-number
          v-model="form.ladder_order"
          :min="1"
          :max="999"
          placeholder="请输入阶梯次序"
          style="width: 100%"
        />
      </el-form-item>
      
      <el-form-item label="阶梯下限" prop="lower_limit">
        <div style="display: flex; align-items: center; gap: 10px;">
          <el-input
            v-model="form.lower_limit"
            placeholder="请输入阶梯下限（保留4位小数）"
            :disabled="form.lower_limit_infinity"
            @blur="formatDecimal('lower_limit')"
            style="flex: 1;"
          />
          <el-checkbox v-model="form.lower_limit_infinity" @change="handleLowerInfinityChange">
            负无穷
          </el-checkbox>
        </div>
      </el-form-item>
      
      <el-form-item label="阶梯上限" prop="upper_limit">
        <div style="display: flex; align-items: center; gap: 10px;">
          <el-input
            v-model="form.upper_limit"
            placeholder="请输入阶梯上限（保留4位小数）"
            :disabled="form.upper_limit_infinity"
            @blur="formatDecimal('upper_limit')"
            style="flex: 1;"
          />
          <el-checkbox v-model="form.upper_limit_infinity" @change="handleUpperInfinityChange">
            正无穷
          </el-checkbox>
        </div>
      </el-form-item>
      
      <el-form-item label="调整力度" prop="adjustment_intensity">
        <el-input
          v-model="form.adjustment_intensity"
          placeholder="请输入调整力度（保留4位小数）"
          @blur="formatDecimal('adjustment_intensity')"
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

interface OrientationLadder {
  id: number
  rule_id: number
  rule_name: string
  ladder_order: number
  upper_limit: string | null
  lower_limit: string | null
  adjustment_intensity: string
  created_at: string
  updated_at: string
}

interface OrientationRule {
  id: number
  name: string
  category: string
}

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  ladder: {
    type: Object as PropType<OrientationLadder | null>,
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

const dialogTitle = computed(() => props.isEdit ? '编辑导向阶梯' : '新增导向阶梯')

const formRef = ref<FormInstance>()
const submitting = ref(false)

const form = reactive({
  rule_id: null as number | null,
  ladder_order: null as number | null,
  upper_limit: '',
  lower_limit: '',
  upper_limit_infinity: false,
  lower_limit_infinity: false,
  adjustment_intensity: ''
})

const ladderRules = ref<OrientationRule[]>([])

// 验证阶梯范围
const validateRange = (rule: any, value: any, callback: any) => {
  // 如果两个都是无穷，跳过验证
  if (form.upper_limit_infinity && form.lower_limit_infinity) {
    callback()
    return
  }
  
  // 如果有一个是无穷，跳过验证
  if (form.upper_limit_infinity || form.lower_limit_infinity) {
    callback()
    return
  }
  
  // 如果两个都有值，验证下限小于上限
  if (form.upper_limit && form.lower_limit) {
    const upper = Number(form.upper_limit)
    const lower = Number(form.lower_limit)
    
    if (isNaN(upper) || isNaN(lower)) {
      callback(new Error('请输入有效的数值'))
    } else if (lower >= upper) {
      callback(new Error('阶梯下限必须小于阶梯上限'))
    } else {
      callback()
    }
  } else {
    callback()
  }
}

// 验证数值格式
const validateDecimal = (rule: any, value: any, callback: any) => {
  if (!value) {
    callback(new Error('请输入数值'))
  } else if (isNaN(Number(value))) {
    callback(new Error('请输入有效的数值'))
  } else {
    callback()
  }
}

// 验证上限（可以为空如果勾选了无穷）
const validateUpperLimit = (rule: any, value: any, callback: any) => {
  if (form.upper_limit_infinity) {
    callback()
  } else if (!value) {
    callback(new Error('请输入阶梯上限或勾选正无穷'))
  } else if (isNaN(Number(value))) {
    callback(new Error('请输入有效的数值'))
  } else {
    // 验证范围
    validateRange(rule, value, callback)
  }
}

// 验证下限（可以为空如果勾选了无穷）
const validateLowerLimit = (rule: any, value: any, callback: any) => {
  if (form.lower_limit_infinity) {
    callback()
  } else if (!value) {
    callback(new Error('请输入阶梯下限或勾选负无穷'))
  } else if (isNaN(Number(value))) {
    callback(new Error('请输入有效的数值'))
  } else {
    // 验证范围
    validateRange(rule, value, callback)
  }
}

const rules: FormRules = {
  rule_id: [
    { required: true, message: '请选择所属导向', trigger: 'change' }
  ],
  ladder_order: [
    { required: true, message: '请输入阶梯次序', trigger: 'blur' }
  ],
  upper_limit: [
    { validator: validateUpperLimit, trigger: 'blur' }
  ],
  lower_limit: [
    { validator: validateLowerLimit, trigger: 'blur' }
  ],
  adjustment_intensity: [
    { required: true, validator: validateDecimal, trigger: 'blur' }
  ]
}

// 获取支持阶梯的导向规则列表
const fetchLadderRules = async () => {
  try {
    // 获取基准阶梯类别
    const res1 = await request.get('/orientation-rules', {
      params: {
        category: 'benchmark_ladder',
        page: 1,
        size: 1000
      }
    })
    
    // 获取直接阶梯类别
    const res2 = await request.get('/orientation-rules', {
      params: {
        category: 'direct_ladder',
        page: 1,
        size: 1000
      }
    })
    
    // 合并两个列表
    ladderRules.value = [...res1.items, ...res2.items]
  } catch (error) {
    ElMessage.error('获取导向规则列表失败')
  }
}

// 处理上限无穷复选框变化
const handleUpperInfinityChange = (checked: boolean) => {
  if (checked) {
    form.upper_limit = ''
  }
  // 触发验证
  formRef.value?.validateField('upper_limit')
  formRef.value?.validateField('lower_limit')
}

// 处理下限无穷复选框变化
const handleLowerInfinityChange = (checked: boolean) => {
  if (checked) {
    form.lower_limit = ''
  }
  // 触发验证
  formRef.value?.validateField('upper_limit')
  formRef.value?.validateField('lower_limit')
}

// 格式化小数为4位
const formatDecimal = (field: 'upper_limit' | 'lower_limit' | 'adjustment_intensity') => {
  const value = form[field]
  if (value && !isNaN(Number(value))) {
    form[field] = Number(value).toFixed(4)
  }
}

// 监听 ladder 变化，更新表单
watch(() => props.ladder, (newLadder) => {
  if (newLadder) {
    form.rule_id = newLadder.rule_id
    form.ladder_order = newLadder.ladder_order
    
    // 处理上限
    if (newLadder.upper_limit === null || newLadder.upper_limit === undefined) {
      form.upper_limit = ''
      form.upper_limit_infinity = true
    } else {
      form.upper_limit = newLadder.upper_limit
      form.upper_limit_infinity = false
    }
    
    // 处理下限
    if (newLadder.lower_limit === null || newLadder.lower_limit === undefined) {
      form.lower_limit = ''
      form.lower_limit_infinity = true
    } else {
      form.lower_limit = newLadder.lower_limit
      form.lower_limit_infinity = false
    }
    
    form.adjustment_intensity = newLadder.adjustment_intensity
  }
}, { immediate: true })

// 监听对话框打开，重置表单或加载数据
watch(visible, async (newVal) => {
  if (newVal) {
    await fetchLadderRules()
    
    if (!props.isEdit) {
      resetForm()
    }
  }
})

// 重置表单
const resetForm = () => {
  form.rule_id = null
  form.ladder_order = null
  form.upper_limit = ''
  form.lower_limit = ''
  form.upper_limit_infinity = false
  form.lower_limit_infinity = false
  form.adjustment_intensity = ''
  formRef.value?.clearValidate()
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      const submitData: any = {
        rule_id: form.rule_id,
        ladder_order: form.ladder_order,
        adjustment_intensity: Number(form.adjustment_intensity)
      }
      
      // 处理上限：如果勾选无穷则发送 null，否则发送数值
      if (form.upper_limit_infinity) {
        submitData.upper_limit = null
      } else {
        submitData.upper_limit = Number(form.upper_limit)
      }
      
      // 处理下限：如果勾选无穷则发送 null，否则发送数值
      if (form.lower_limit_infinity) {
        submitData.lower_limit = null
      } else {
        submitData.lower_limit = Number(form.lower_limit)
      }

      if (props.isEdit && props.ladder) {
        await request.put(`/orientation-ladders/${props.ladder.id}`, submitData)
        ElMessage.success('更新成功')
      } else {
        await request.post('/orientation-ladders', submitData)
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
/* 样式继承自全局 */
</style>
