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
            v-for="rule in benchmarkLadderRules"
            :key="rule.id"
            :label="rule.name"
            :value="rule.id"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item label="科室" prop="department_code">
        <el-select
          v-model="form.department_code"
          placeholder="请选择科室"
          filterable
          style="width: 100%"
          @change="handleDepartmentChange"
        >
          <el-option
            v-for="dept in departments"
            :key="dept.his_code"
            :label="`${dept.his_name} (${dept.his_code})`"
            :value="dept.his_code"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item label="基准类别" prop="benchmark_type">
        <el-select
          v-model="form.benchmark_type"
          placeholder="请选择基准类别"
          style="width: 100%"
        >
          <el-option label="平均值" value="average" />
          <el-option label="中位数" value="median" />
          <el-option label="最大值" value="max" />
          <el-option label="最小值" value="min" />
          <el-option label="其他" value="other" />
        </el-select>
      </el-form-item>
      
      <el-form-item label="管控力度" prop="control_intensity">
        <el-input
          v-model="form.control_intensity"
          placeholder="请输入管控力度（保留4位小数）"
          @blur="formatDecimal('control_intensity')"
        />
      </el-form-item>
      
      <el-form-item label="统计时间" prop="stat_date_range">
        <el-date-picker
          v-model="form.stat_date_range"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          style="width: 100%"
          :clearable="true"
          :editable="true"
          unlink-panels
        />
      </el-form-item>
      
      <el-form-item label="基准值" prop="benchmark_value">
        <el-input
          v-model="form.benchmark_value"
          placeholder="请输入基准值（保留4位小数）"
          @blur="formatDecimal('benchmark_value')"
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

interface OrientationBenchmark {
  id: number
  rule_id: number
  rule_name: string
  department_code: string
  department_name: string
  benchmark_type: 'average' | 'median' | 'max' | 'min' | 'other'
  control_intensity: string
  stat_start_date: string
  stat_end_date: string
  benchmark_value: string
  created_at: string
  updated_at: string
}

interface OrientationRule {
  id: number
  name: string
  category: string
}

interface Department {
  his_code: string
  his_name: string
}

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  benchmark: {
    type: Object as PropType<OrientationBenchmark | null>,
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

const dialogTitle = computed(() => props.isEdit ? '编辑导向基准' : '新增导向基准')

const formRef = ref<FormInstance>()
const submitting = ref(false)

const form = reactive({
  rule_id: null as number | null,
  department_code: '',
  department_name: '',
  benchmark_type: '' as 'average' | 'median' | 'max' | 'min' | 'other' | '',
  control_intensity: '',
  stat_date_range: [] as string[],
  benchmark_value: ''
})

const benchmarkLadderRules = ref<OrientationRule[]>([])
const departments = ref<Department[]>([])

// 验证日期范围
const validateDateRange = (rule: any, value: any, callback: any) => {
  if (!value || value.length !== 2) {
    callback(new Error('请选择统计时间范围'))
  } else {
    const [start, end] = value
    if (new Date(start) >= new Date(end)) {
      callback(new Error('统计开始时间必须早于统计结束时间'))
    } else {
      callback()
    }
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

const rules: FormRules = {
  rule_id: [
    { required: true, message: '请选择所属导向', trigger: 'change' }
  ],
  department_code: [
    { required: true, message: '请选择科室', trigger: 'change' }
  ],
  benchmark_type: [
    { required: true, message: '请选择基准类别', trigger: 'change' }
  ],
  control_intensity: [
    { required: true, validator: validateDecimal, trigger: 'blur' }
  ],
  stat_date_range: [
    { required: true, validator: validateDateRange, trigger: 'change' }
  ],
  benchmark_value: [
    { required: true, validator: validateDecimal, trigger: 'blur' }
  ]
}

// 获取基准阶梯类别的导向规则列表
const fetchBenchmarkLadderRules = async () => {
  try {
    const res = await request.get('/orientation-rules', {
      params: {
        category: 'benchmark_ladder',
        page: 1,
        size: 1000
      }
    })
    benchmarkLadderRules.value = res.items
  } catch (error) {
    ElMessage.error('获取导向规则列表失败')
  }
}

// 获取科室列表
const fetchDepartments = async () => {
  try {
    const res = await request.get('/departments', {
      params: {
        page: 1,
        size: 1000
      }
    })
    departments.value = res.items
  } catch (error) {
    ElMessage.error('获取科室列表失败')
  }
}

// 处理科室选择变化
const handleDepartmentChange = (code: string) => {
  const dept = departments.value.find(d => d.his_code === code)
  if (dept) {
    form.department_name = dept.his_name
  }
}

// 格式化小数为4位
const formatDecimal = (field: 'control_intensity' | 'benchmark_value') => {
  const value = form[field]
  if (value && !isNaN(Number(value))) {
    form[field] = Number(value).toFixed(4)
  }
}

// 监听 benchmark 变化，更新表单
watch(() => props.benchmark, (newBenchmark) => {
  if (newBenchmark) {
    form.rule_id = newBenchmark.rule_id
    form.department_code = newBenchmark.department_code
    form.department_name = newBenchmark.department_name
    form.benchmark_type = newBenchmark.benchmark_type
    form.control_intensity = newBenchmark.control_intensity
    form.stat_date_range = [
      newBenchmark.stat_start_date.substring(0, 10),
      newBenchmark.stat_end_date.substring(0, 10)
    ]
    form.benchmark_value = newBenchmark.benchmark_value
  }
}, { immediate: true })

// 监听对话框打开，重置表单或加载数据
watch(visible, async (newVal) => {
  if (newVal) {
    await fetchBenchmarkLadderRules()
    await fetchDepartments()
    
    if (!props.isEdit) {
      resetForm()
    }
  }
})

// 重置表单
const resetForm = () => {
  form.rule_id = null
  form.department_code = ''
  form.department_name = ''
  form.benchmark_type = ''
  form.control_intensity = ''
  form.stat_date_range = []
  form.benchmark_value = ''
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
        rule_id: form.rule_id,
        department_code: form.department_code,
        department_name: form.department_name,
        benchmark_type: form.benchmark_type,
        control_intensity: Number(form.control_intensity),
        stat_start_date: form.stat_date_range[0] + 'T00:00:00',
        stat_end_date: form.stat_date_range[1] + 'T23:59:59',
        benchmark_value: Number(form.benchmark_value)
      }

      if (props.isEdit && props.benchmark) {
        await request.put(`/orientation-benchmarks/${props.benchmark.id}`, submitData)
        ElMessage.success('更新成功')
      } else {
        await request.post('/orientation-benchmarks', submitData)
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
