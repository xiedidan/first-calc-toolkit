<template>
  <div class="model-nodes-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <div>
            <el-button link @click="handleBack">
              <el-icon><ArrowLeft /></el-icon>
              返回版本列表
            </el-button>
            <span class="version-title">{{ versionInfo?.name }} ({{ versionInfo?.version }})</span>
          </div>
          <el-button type="primary" @click="handleAddRoot">
            <el-icon><Plus /></el-icon>
            添加根节点
          </el-button>
        </div>
      </template>

      <!-- 树形表格 -->
      <el-table
        :data="tableData"
        row-key="id"
        border
        stripe
        v-loading="loading"
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
        default-expand-all
      >
        <el-table-column label="节点名称" min-width="350">
          <template #default="{ row }">
            {{ row.name }} 
            <span class="sort-badge">
              ( Lvl.{{ getNodeLevel(row) }}, No.{{ row.sort_order }} )
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="code" label="节点编码" width="200" show-overflow-tooltip />
        <el-table-column label="节点类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.node_type === 'sequence'" type="primary" size="small">序列</el-tag>
            <el-tag v-else type="success" size="small">维度</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="末级维度" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_leaf" type="success" size="small">是</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="算法类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_leaf && row.calc_type === 'statistical'" type="info" size="small">指标</el-tag>
            <el-tag v-else-if="row.is_leaf && row.calc_type === 'calculational'" type="warning" size="small">目录</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="权重/单价" width="130" align="center">
          <template #default="{ row }">
            <span v-if="row.is_leaf && row.weight">
              {{ formatWeight(row.weight, row.unit) }} {{ row.unit || '%' }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="业务导向" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.is_leaf && row.business_guide ? row.business_guide : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right" align="center">
          <template #default="{ row }">
            <el-tooltip 
              v-if="row.is_leaf" 
              content="末级维度不能添加子节点" 
              placement="top"
            >
              <el-button link type="info" disabled size="small">
                <el-icon><Plus /></el-icon>
                添加子节点
              </el-button>
            </el-tooltip>
            <el-button v-else link type="primary" @click="handleAddChild(row)" size="small">
              <el-icon><Plus /></el-icon>
              添加子节点
            </el-button>
            <el-button link type="primary" @click="handleEdit(row)" size="small">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)" size="small">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      @close="handleDialogClose"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="节点名称" prop="name">
              <el-input v-model="form.name" placeholder="如: 医生序列" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="节点编码" prop="code">
              <el-input v-model="form.code" placeholder="如: DOCTOR" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="节点类型" prop="node_type">
              <el-select v-model="form.node_type" placeholder="请选择" style="width: 100%">
                <el-option label="序列" value="sequence" />
                <el-option label="维度" value="dimension" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序序号" prop="sort_order">
              <el-input-number 
                v-model="form.sort_order" 
                :precision="2"
                :step="0.1"
                :min="0"
                style="width: 100%"
                placeholder="留空自动设置"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="是否末级维度" prop="is_leaf">
              <el-switch 
                v-model="form.is_leaf"
                :disabled="hasChildren"
              />
              <el-text v-if="hasChildren" type="warning" size="small" style="margin-left: 10px">
                该节点有子节点，不能设为末级
              </el-text>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="算法类型" prop="calc_type" v-if="form.is_leaf">
              <el-select v-model="form.calc_type" placeholder="请选择" style="width: 100%">
                <el-option label="指标" value="statistical" />
                <el-option label="目录" value="calculational" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20" v-if="form.is_leaf">
          <el-col :span="12">
            <el-form-item label="权重/单价" prop="weight">
              <el-input-number 
                v-model="form.weight" 
                :precision="4"
                :step="0.01"
                :min="0"
                style="width: 100%"
                :placeholder="form.unit === '%' ? '如: 65.5 (表示65.5%)' : '如: 5000'"
              />
              <el-text v-if="form.unit === '%'" type="info" size="small" style="margin-top: 4px">
                百分比单位请直接输入数值，如输入 65.5 表示 65.5%
              </el-text>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位" prop="unit">
              <el-input 
                v-model="form.unit" 
                placeholder="如: %, 元/例, 元/人天"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="业务导向" prop="business_guide" v-if="form.is_leaf">
          <el-input 
            v-model="form.business_guide" 
            type="textarea" 
            :rows="3"
            placeholder="请输入业务导向说明"
          />
        </el-form-item>

        <el-form-item label="计算脚本" prop="script" v-if="form.is_leaf">
          <el-input 
            v-model="form.script" 
            type="textarea" 
            :rows="8"
            placeholder="请输入SQL或Python脚本"
          />
          <div style="margin-top: 10px">
            <el-button size="small" @click="handleTestCode" :loading="testing">
              <el-icon><VideoPlay /></el-icon>
              测试运行
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 测试结果对话框 -->
    <el-dialog
      v-model="testResultVisible"
      title="测试结果"
      width="700px"
    >
      <el-alert
        :title="testResult.success ? '测试成功' : '测试失败'"
        :type="testResult.success ? 'success' : 'error'"
        :closable="false"
        style="margin-bottom: 20px"
      />
      <el-descriptions v-if="testResult.success" :column="1" border>
        <el-descriptions-item label="执行结果">
          <pre>{{ JSON.stringify(testResult.result, null, 2) }}</pre>
        </el-descriptions-item>
      </el-descriptions>
      <el-alert
        v-else
        :title="testResult.error"
        type="error"
        :closable="false"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { ArrowLeft, Plus, VideoPlay } from '@element-plus/icons-vue'
import { useRouter, useRoute } from 'vue-router'
import {
  getModelVersion,
  getModelNodes,
  createModelNode,
  updateModelNode,
  deleteModelNode,
  testNodeCode,
  type ModelVersion,
  type ModelNode
} from '@/api/model'

const router = useRouter()
const route = useRoute()

const versionId = computed(() => Number(route.params.versionId))

// 版本信息
const versionInfo = ref<ModelVersion>()

// 表格数据
const tableData = ref<ModelNode[]>([])
const loading = ref(false)

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('添加节点')
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

// 表单
const form = reactive({
  id: 0,
  parent_id: undefined as number | undefined,
  sort_order: undefined as number | undefined,
  name: '',
  code: '',
  node_type: 'sequence' as 'sequence' | 'dimension',
  is_leaf: false,
  calc_type: 'calculational' as 'statistical' | 'calculational' | undefined,
  weight: undefined as number | undefined,
  unit: '%',
  business_guide: '',
  script: ''
})

const hasChildren = ref(false)

// 动态验证规则
const rules = computed<FormRules>(() => {
  const baseRules: FormRules = {
    name: [{ required: true, message: '请输入节点名称', trigger: 'blur' }],
    code: [{ required: true, message: '请输入节点编码', trigger: 'blur' }],
    node_type: [{ required: true, message: '请选择节点类型', trigger: 'change' }]
  }
  
  // 如果是末级维度，添加额外的必填验证
  if (form.is_leaf) {
    baseRules.calc_type = [{ required: true, message: '请选择算法类型', trigger: 'change' }]
    baseRules.weight = [{ required: true, message: '请输入权重/单价', trigger: 'blur' }]
    baseRules.unit = [{ required: true, message: '请输入单位', trigger: 'blur' }]
    baseRules.script = [{ required: true, message: '请输入计算脚本', trigger: 'blur' }]
  }
  
  return baseRules
})

// 测试结果
const testResultVisible = ref(false)
const testing = ref(false)
const testResult = reactive({
  success: false,
  result: null as any,
  error: ''
})

// 获取版本信息
const fetchVersionInfo = async () => {
  try {
    versionInfo.value = await getModelVersion(versionId.value)
  } catch (error) {
    ElMessage.error('获取版本信息失败')
  }
}

// 获取节点列表
const fetchData = async () => {
  loading.value = true
  try {
    const res = await getModelNodes({ version_id: versionId.value })
    tableData.value = res.items
  } catch (error) {
    ElMessage.error('获取节点列表失败')
  } finally {
    loading.value = false
  }
}

// 返回
const handleBack = () => {
  router.push({ name: 'ModelVersions' })
}

// 添加根节点
const handleAddRoot = () => {
  dialogTitle.value = '添加根节点'
  isEdit.value = false
  hasChildren.value = false
  Object.assign(form, {
    id: 0,
    parent_id: undefined,
    sort_order: undefined,  // 让后端自动计算
    name: '',
    code: '',
    node_type: 'sequence',
    is_leaf: false,
    calc_type: 'calculational',
    weight: undefined,
    unit: '%',
    business_guide: '',
    script: ''
  })
  dialogVisible.value = true
}

// 添加子节点
const handleAddChild = (row: ModelNode) => {
  dialogTitle.value = `添加子节点 (父节点: ${row.name})`
  isEdit.value = false
  hasChildren.value = false
  Object.assign(form, {
    id: 0,
    parent_id: row.id,
    sort_order: undefined,  // 让后端自动计算
    name: '',
    code: '',
    node_type: 'dimension',
    is_leaf: false,
    calc_type: 'calculational',
    weight: undefined,
    unit: '%',
    business_guide: '',
    script: ''
  })
  dialogVisible.value = true
}

// 格式化权重显示（百分比单位乘以100）
const formatWeight = (weight: number | undefined, unit: string | undefined): string => {
  if (weight === undefined || weight === null) return '-'
  const unitValue = unit || '%'
  // 如果单位是百分比，将值乘以100显示
  const displayValue = unitValue === '%' ? weight * 100 : weight
  return Number(displayValue).toFixed(2)
}

// 转换权重值用于编辑（百分比单位除以100）
const convertWeightForEdit = (weight: number | undefined, unit: string | undefined): number | undefined => {
  if (weight === undefined || weight === null) return undefined
  const unitValue = unit || '%'
  // 如果单位是百分比，将显示值除以100得到原始值
  return unitValue === '%' ? weight * 100 : weight
}

// 转换权重值用于保存（百分比单位除以100）
const convertWeightForSave = (weight: number | undefined, unit: string | undefined): number | undefined => {
  if (weight === undefined || weight === null) return undefined
  const unitValue = unit || '%'
  // 如果单位是百分比，将输入值除以100保存
  return unitValue === '%' ? weight / 100 : weight
}

// 编辑
const handleEdit = (row: ModelNode) => {
  dialogTitle.value = '编辑节点'
  isEdit.value = true
  hasChildren.value = row.has_children || false
  Object.assign(form, {
    id: row.id,
    parent_id: row.parent_id,
    sort_order: row.sort_order,
    name: row.name,
    code: row.code,
    node_type: row.node_type,
    is_leaf: row.is_leaf,
    calc_type: row.calc_type,
    weight: convertWeightForEdit(row.weight, row.unit),
    unit: row.unit || '%',
    business_guide: row.business_guide || '',
    script: row.script || ''
  })
  dialogVisible.value = true
}

// 删除
const handleDelete = async (row: ModelNode) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除节点 "${row.name}" 吗？删除后其所有子节点也将被删除！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteModelNode(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 测试代码
const handleTestCode = async () => {
  if (!form.script) {
    ElMessage.warning('请先输入脚本代码')
    return
  }

  testing.value = true
  try {
    const result = await testNodeCode(form.id || 0, {
      script: form.script
    })
    
    Object.assign(testResult, result)
    testResultVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '测试失败')
  } finally {
    testing.value = false
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      const data = {
        version_id: versionId.value,
        parent_id: form.parent_id,
        sort_order: form.sort_order,
        name: form.name,
        code: form.code,
        node_type: form.node_type,
        is_leaf: form.is_leaf,
        calc_type: form.calc_type,
        weight: convertWeightForSave(form.weight, form.unit),
        unit: form.unit,
        business_guide: form.business_guide,
        script: form.script
      }

      if (isEdit.value) {
        await updateModelNode(form.id, data)
        ElMessage.success('更新成功')
      } else {
        await createModelNode(data)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchData()
    } catch (error: any) {
      ElMessage.error(error.message || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

// 关闭对话框
const handleDialogClose = () => {
  formRef.value?.resetFields()
}

// 计算节点层级
const getNodeLevel = (node: ModelNode): number => {
  const findLevel = (nodes: ModelNode[], targetId: number, currentLevel: number = 0): number => {
    for (const n of nodes) {
      if (n.id === targetId) {
        return currentLevel
      }
      if (n.children && n.children.length > 0) {
        const childLevel = findLevel(n.children, targetId, currentLevel + 1)
        if (childLevel >= 0) return childLevel
      }
    }
    return -1
  }
  
  return findLevel(tableData.value, node.id)
}

onMounted(() => {
  fetchVersionInfo()
  fetchData()
})
</script>

<style scoped>
.model-nodes-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header .version-title {
  margin-left: 10px;
  font-size: 16px;
  font-weight: bold;
}

.sort-badge {
  color: #909399;
  font-size: 12px;
  margin-left: 4px;
}

pre {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>
