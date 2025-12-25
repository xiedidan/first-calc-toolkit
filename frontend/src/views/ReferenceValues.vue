<template>
  <div class="reference-values-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>参考价值管理</span>
          <div class="header-actions">
            <el-button type="primary" @click="showImportDialog">Excel导入</el-button>
            <el-button @click="showAddDialog">手动添加</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-form">
        <el-form :inline="true" :model="searchForm">
          <el-form-item label="年月">
            <el-date-picker
              v-model="searchForm.period"
              type="month"
              placeholder="选择月份"
              format="YYYY-MM"
              value-format="YYYY-MM"
              clearable
              @change="handleSearch"
            />
          </el-form-item>
          <el-form-item label="关键词">
            <el-input
              v-model="searchForm.keyword"
              placeholder="科室代码/名称"
              clearable
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
            <el-button type="danger" @click="handleClearFiltered">清除全部筛选记录</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 数据表格 -->
      <el-table :data="tableData" v-loading="loading" stripe border>
        <el-table-column prop="period" label="年月" width="100" />
        <el-table-column prop="department_code" label="科室代码" width="120" />
        <el-table-column prop="department_name" label="科室名称" width="150" />
        <el-table-column prop="reference_value" label="参考总价值" width="140" align="right">
          <template #default="{ row }">
            {{ formatNumber(row.reference_value) }}
          </template>
        </el-table-column>
        <el-table-column prop="doctor_reference_value" label="医生参考价值" width="140" align="right">
          <template #default="{ row }">
            {{ formatNumberOrDash(row.doctor_reference_value) }}
          </template>
        </el-table-column>
        <el-table-column prop="nurse_reference_value" label="护理参考价值" width="140" align="right">
          <template #default="{ row }">
            {{ formatNumberOrDash(row.nurse_reference_value) }}
          </template>
        </el-table-column>
        <el-table-column prop="tech_reference_value" label="医技参考价值" width="140" align="right">
          <template #default="{ row }">
            {{ formatNumberOrDash(row.tech_reference_value) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="formDialogVisible"
      :title="isEdit ? '编辑参考价值' : '添加参考价值'"
      width="600px"
      append-to-body
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="年月" prop="period">
          <el-date-picker
            v-model="formData.period"
            type="month"
            placeholder="选择月份"
            format="YYYY-MM"
            value-format="YYYY-MM"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="科室" prop="department_code">
          <el-select
            v-model="formData.department_code"
            placeholder="选择科室"
            filterable
            style="width: 100%"
            @change="handleDepartmentChange"
          >
            <el-option
              v-for="dept in departments"
              :key="dept.code"
              :label="`${dept.name} (${dept.code})`"
              :value="dept.code"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="参考总价值" prop="reference_value">
          <el-input-number
            v-model="formData.reference_value"
            :precision="4"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="医生参考价值">
          <el-input-number
            v-model="formData.doctor_reference_value"
            :precision="4"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="护理参考价值">
          <el-input-number
            v-model="formData.nurse_reference_value"
            :precision="4"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="医技参考价值">
          <el-input-number
            v-model="formData.tech_reference_value"
            :precision="4"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="Excel智能导入"
      width="900px"
      append-to-body
      :close-on-click-modal="false"
    >
      <el-steps :active="importStep" finish-status="success" simple style="margin-bottom: 20px">
        <el-step title="上传文件" />
        <el-step title="科室匹配" />
        <el-step title="预览确认" />
      </el-steps>

      <!-- 步骤1：上传文件 -->
      <div v-if="importStep === 0" class="import-step">
        <el-form label-width="120px">
          <el-form-item label="选择文件">
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :limit="1"
              accept=".xlsx,.xls"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
            >
              <el-button type="primary">选择Excel文件</el-button>
              <template #tip>
                <div class="el-upload__tip">只能上传 xlsx/xls 文件</div>
              </template>
            </el-upload>
          </el-form-item>
          <el-form-item label="标题行位置">
            <el-input-number v-model="importConfig.skipRows" :min="0" :max="100" />
            <span style="margin-left: 10px; color: #909399">跳过前N行后的第一行作为标题行</span>
          </el-form-item>
          <el-form-item label="匹配方式">
            <el-radio-group v-model="importConfig.matchBy">
              <el-radio value="code">按科室代码精确匹配</el-radio>
              <el-radio value="name">按科室名称模糊匹配</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>

        <div v-if="parseResult" class="parse-result">
          <h4>文件预览</h4>
          <el-form label-width="120px">
            <el-form-item label="工作表">
              <el-select v-model="importConfig.sheetName" @change="handleSheetChange">
                <el-option
                  v-for="sheet in parseResult.sheet_names"
                  :key="sheet"
                  :label="sheet"
                  :value="sheet"
                />
              </el-select>
            </el-form-item>
          </el-form>
          
          <h4>字段映射</h4>
          <el-form label-width="120px">
            <el-form-item label="年月列" required>
              <el-select v-model="fieldMapping.period" placeholder="选择年月列">
                <el-option v-for="h in parseResult.headers" :key="h" :label="h" :value="h" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="importConfig.matchBy === 'code'" label="科室代码列" required>
              <el-select v-model="fieldMapping.department_code" placeholder="选择科室代码列">
                <el-option v-for="h in parseResult.headers" :key="h" :label="h" :value="h" />
              </el-select>
            </el-form-item>
            <el-form-item v-else label="科室名称列" required>
              <el-select v-model="fieldMapping.department_name" placeholder="选择科室名称列">
                <el-option v-for="h in parseResult.headers" :key="h" :label="h" :value="h" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="importConfig.matchBy === 'code'" label="科室名称列">
              <el-select v-model="fieldMapping.department_name" placeholder="选择科室名称列（可选）" clearable>
                <el-option v-for="h in parseResult.headers" :key="h" :label="h" :value="h" />
              </el-select>
            </el-form-item>
            <el-form-item label="参考总价值列" required>
              <el-select v-model="fieldMapping.reference_value" placeholder="选择参考总价值列">
                <el-option v-for="h in parseResult.headers" :key="h" :label="h" :value="h" />
              </el-select>
            </el-form-item>
            <el-form-item label="医生参考价值列">
              <el-select v-model="fieldMapping.doctor_reference_value" placeholder="选择医生参考价值列（可选）" clearable>
                <el-option v-for="h in parseResult.headers" :key="h" :label="h" :value="h" />
              </el-select>
            </el-form-item>
            <el-form-item label="护理参考价值列">
              <el-select v-model="fieldMapping.nurse_reference_value" placeholder="选择护理参考价值列（可选）" clearable>
                <el-option v-for="h in parseResult.headers" :key="h" :label="h" :value="h" />
              </el-select>
            </el-form-item>
            <el-form-item label="医技参考价值列">
              <el-select v-model="fieldMapping.tech_reference_value" placeholder="选择医技参考价值列（可选）" clearable>
                <el-option v-for="h in parseResult.headers" :key="h" :label="h" :value="h" />
              </el-select>
            </el-form-item>
          </el-form>

          <h4>数据预览（前10行）</h4>
          <el-table :data="parseResult.preview_data" border size="small" max-height="200">
            <el-table-column
              v-for="(header, index) in parseResult.headers"
              :key="index"
              :label="header"
              :prop="String(index)"
              min-width="120"
            >
              <template #default="{ row }">{{ row[index] }}</template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- 步骤2：科室匹配（仅名称匹配时显示） -->
      <div v-if="importStep === 1" class="import-step">
        <div v-if="importConfig.matchBy === 'name'">
          <p style="margin-bottom: 15px; color: #909399">
            请为Excel中的科室名称选择对应的系统科室。系统已根据名称相似度提供建议。
          </p>
          <el-table :data="uniqueValues" border max-height="400">
            <el-table-column prop="value" label="Excel科室名称" width="200" />
            <el-table-column prop="count" label="出现次数" width="100" align="center" />
            <el-table-column label="匹配科室" min-width="300">
              <template #default="{ row }">
                <el-select
                  v-model="departmentMapping[row.value]"
                  placeholder="选择匹配的科室"
                  filterable
                  clearable
                  style="width: 100%"
                >
                  <el-option
                    v-for="dept in row.suggested_departments"
                    :key="dept.code"
                    :label="`${dept.name} (${dept.code}) - 相似度: ${(dept.score * 100).toFixed(0)}%`"
                    :value="dept.code"
                  />
                  <el-option-group label="所有科室">
                    <el-option
                      v-for="dept in systemDepartments"
                      :key="'all-' + dept.code"
                      :label="`${dept.name} (${dept.code})`"
                      :value="dept.code"
                    />
                  </el-option-group>
                </el-select>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-else>
          <p>按科室代码精确匹配，无需手动映射。</p>
        </div>
      </div>

      <!-- 步骤3：预览确认 -->
      <div v-if="importStep === 2" class="import-step">
        <div class="preview-statistics">
          <el-tag type="success">新增: {{ previewStatistics.new_count }}</el-tag>
          <el-tag type="warning">覆盖: {{ previewStatistics.update_count }}</el-tag>
          <el-tag type="danger">错误: {{ previewStatistics.error_count }}</el-tag>
          <el-tag>总计: {{ previewStatistics.total }}</el-tag>
        </div>
        <el-table :data="previewItems" border max-height="400">
          <el-table-column prop="period" label="年月" width="100" />
          <el-table-column prop="department_code" label="科室代码" width="100" />
          <el-table-column prop="department_name" label="科室名称" width="120" />
          <el-table-column prop="reference_value" label="参考总价值" width="120" align="right">
            <template #default="{ row }">{{ formatNumber(row.reference_value) }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="message" label="说明" min-width="150" show-overflow-tooltip />
        </el-table>
      </div>

      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button v-if="importStep > 0" @click="importStep--">上一步</el-button>
        <el-button 
          v-if="importStep < 2" 
          type="primary" 
          @click="handleNextStep" 
          :loading="importLoading"
        >
          下一步
        </el-button>
        <el-button 
          v-if="importStep === 2" 
          type="primary" 
          @click="handleImportExecute" 
          :loading="importLoading"
        >
          确认导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>


<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, UploadInstance } from 'element-plus'
import {
  getReferenceValues,
  createReferenceValue,
  updateReferenceValue,
  deleteReferenceValue,
  clearPeriodReferenceValues,
  clearAllReferenceValues,
  importParse,
  importExtractValues,
  importPreview,
  importExecute,
  type ReferenceValue,
  type ImportParseResponse,
  type UniqueValueForMatch,
  type DepartmentMatch,
  type PreviewItem,
  type PreviewStatistics
} from '@/api/reference-values'
import request from '@/utils/request'

// 数据
const loading = ref(false)
const submitting = ref(false)
const tableData = ref<ReferenceValue[]>([])
const departments = ref<any[]>([])

// 搜索
const searchForm = reactive({
  period: '',
  keyword: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

// 表单
const formDialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()
const formData = reactive({
  period: '',
  department_code: '',
  department_name: '',
  reference_value: 0,
  doctor_reference_value: null as number | null,
  nurse_reference_value: null as number | null,
  tech_reference_value: null as number | null
})

const formRules = {
  period: [{ required: true, message: '请选择年月', trigger: 'change' }],
  department_code: [{ required: true, message: '请选择科室', trigger: 'change' }],
  reference_value: [{ required: true, message: '请输入参考总价值', trigger: 'blur' }]
}

// 导入相关
const importDialogVisible = ref(false)
const importStep = ref(0)
const importLoading = ref(false)
const uploadRef = ref<UploadInstance>()
const uploadFile = ref<File | null>(null)

const importConfig = reactive({
  skipRows: 0,
  matchBy: 'code' as 'code' | 'name',
  sheetName: ''
})

const fieldMapping = reactive({
  period: '',
  department_code: '',
  department_name: '',
  reference_value: '',
  doctor_reference_value: '',
  nurse_reference_value: '',
  tech_reference_value: ''
})

const parseResult = ref<ImportParseResponse | null>(null)
const sessionId = ref('')
const uniqueValues = ref<UniqueValueForMatch[]>([])
const systemDepartments = ref<DepartmentMatch[]>([])
const departmentMapping = reactive<Record<string, string>>({})
const previewItems = ref<PreviewItem[]>([])
const previewStatistics = ref<PreviewStatistics>({
  total: 0,
  new_count: 0,
  update_count: 0,
  error_count: 0
})

// 方法
const loadData = async () => {
  loading.value = true
  try {
    const res: any = await getReferenceValues({
      period: searchForm.period || undefined,
      keyword: searchForm.keyword || undefined,
      page: pagination.page,
      size: pagination.size
    })
    tableData.value = res.items || []
    pagination.total = res.total || 0
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载数据失败')
  } finally {
    loading.value = false
  }
}

const loadDepartments = async () => {
  try {
    const res: any = await request({
      url: '/departments',
      method: 'get',
      params: { page: 1, size: 1000 }
    })
    departments.value = res.items || []
  } catch (error) {
    console.error('加载科室失败:', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const resetSearch = () => {
  searchForm.period = ''
  searchForm.keyword = ''
  pagination.page = 1
  loadData()
}

const handleSizeChange = () => {
  pagination.page = 1
  loadData()
}

const handlePageChange = () => {
  loadData()
}

const formatNumber = (value: any) => {
  if (value === null || value === undefined) return '-'
  return Number(value).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 4
  })
}

const formatNumberOrDash = (value: any) => {
  if (value === null || value === undefined) return '-'
  return formatNumber(value)
}

const showAddDialog = () => {
  isEdit.value = false
  editingId.value = null
  Object.assign(formData, {
    period: '',
    department_code: '',
    department_name: '',
    reference_value: 0,
    doctor_reference_value: null,
    nurse_reference_value: null,
    tech_reference_value: null
  })
  formDialogVisible.value = true
}

const handleEdit = (row: ReferenceValue) => {
  isEdit.value = true
  editingId.value = row.id
  Object.assign(formData, {
    period: row.period,
    department_code: row.department_code,
    department_name: row.department_name,
    reference_value: row.reference_value,
    doctor_reference_value: row.doctor_reference_value,
    nurse_reference_value: row.nurse_reference_value,
    tech_reference_value: row.tech_reference_value
  })
  formDialogVisible.value = true
}

const handleDepartmentChange = (code: string) => {
  const dept = departments.value.find(d => d.code === code)
  if (dept) {
    formData.department_name = dept.name
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (isEdit.value && editingId.value) {
        await updateReferenceValue(editingId.value, formData)
        ElMessage.success('更新成功')
      } else {
        await createReferenceValue(formData)
        ElMessage.success('添加成功')
      }
      formDialogVisible.value = false
      loadData()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

const handleDelete = async (row: ReferenceValue) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${row.period} ${row.department_name} 的参考价值吗？`,
      '确认删除',
      { type: 'warning' }
    )
    await deleteReferenceValue(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

const handleClearFiltered = async () => {
  // 根据筛选条件决定清除范围
  const hasPeriodFilter = !!searchForm.period
  const hasKeywordFilter = !!searchForm.keyword
  
  if (!hasPeriodFilter && !hasKeywordFilter) {
    // 没有筛选条件，清除全部
    try {
      await ElMessageBox.confirm(
        `确定要清除所有参考价值数据吗？此操作不可恢复！`,
        '确认清除全部',
        { type: 'warning' }
      )
      const res: any = await clearAllReferenceValues()
      ElMessage.success(`已清除 ${res.deleted_count} 条记录`)
      loadData()
    } catch (error: any) {
      if (error !== 'cancel') {
        ElMessage.error(error.response?.data?.detail || '清除失败')
      }
    }
  } else if (hasPeriodFilter && !hasKeywordFilter) {
    // 只有年月筛选，清除该月份全部
    try {
      await ElMessageBox.confirm(
        `确定要清除 ${searchForm.period} 的所有参考价值数据吗？此操作不可恢复！`,
        '确认清除',
        { type: 'warning' }
      )
      const res: any = await clearPeriodReferenceValues(searchForm.period)
      ElMessage.success(`已清除 ${res.deleted_count} 条记录`)
      loadData()
    } catch (error: any) {
      if (error !== 'cancel') {
        ElMessage.error(error.response?.data?.detail || '清除失败')
      }
    }
  } else {
    // 有关键词筛选，提示不支持
    ElMessage.warning('关键词筛选时不支持批量清除，请仅使用年月筛选或清除全部')
  }
}

// 导入相关方法
const showImportDialog = () => {
  importStep.value = 0
  parseResult.value = null
  sessionId.value = ''
  uploadFile.value = null
  Object.assign(importConfig, { skipRows: 0, matchBy: 'code', sheetName: '' })
  Object.assign(fieldMapping, {
    period: '',
    department_code: '',
    department_name: '',
    reference_value: '',
    doctor_reference_value: '',
    nurse_reference_value: '',
    tech_reference_value: ''
  })
  uniqueValues.value = []
  systemDepartments.value = []
  Object.keys(departmentMapping).forEach(key => delete departmentMapping[key])
  previewItems.value = []
  previewStatistics.value = { total: 0, new_count: 0, update_count: 0, error_count: 0 }
  importDialogVisible.value = true
}

const handleFileChange = (file: any) => {
  uploadFile.value = file.raw
  parseExcelFile()
}

const handleFileRemove = () => {
  uploadFile.value = null
  parseResult.value = null
}

const parseExcelFile = async () => {
  if (!uploadFile.value) return
  
  importLoading.value = true
  try {
    const res: any = await importParse(uploadFile.value, importConfig.sheetName, importConfig.skipRows)
    parseResult.value = res
    sessionId.value = res.session_id
    importConfig.sheetName = res.current_sheet
    
    // 应用建议的字段映射
    if (res.suggested_mapping) {
      Object.assign(fieldMapping, res.suggested_mapping)
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '解析文件失败')
  } finally {
    importLoading.value = false
  }
}

const handleSheetChange = () => {
  parseExcelFile()
}

const handleNextStep = async () => {
  if (importStep.value === 0) {
    // 验证字段映射
    if (!fieldMapping.period) {
      ElMessage.warning('请选择年月列')
      return
    }
    if (importConfig.matchBy === 'code' && !fieldMapping.department_code) {
      ElMessage.warning('请选择科室代码列')
      return
    }
    if (importConfig.matchBy === 'name' && !fieldMapping.department_name) {
      ElMessage.warning('请选择科室名称列')
      return
    }
    if (!fieldMapping.reference_value) {
      ElMessage.warning('请选择参考总价值列')
      return
    }
    
    // 提取唯一值
    importLoading.value = true
    try {
      const res: any = await importExtractValues({
        session_id: sessionId.value,
        field_mapping: fieldMapping,
        match_by: importConfig.matchBy
      })
      
      uniqueValues.value = res.unique_values || []
      systemDepartments.value = res.system_departments || []
      
      // 自动选择最佳匹配
      for (const uv of uniqueValues.value) {
        if (uv.suggested_departments && uv.suggested_departments.length > 0) {
          const best = uv.suggested_departments[0]
          if (best.score >= 0.8) {
            departmentMapping[uv.value] = best.code
          }
        }
      }
      
      // 如果是代码匹配，直接跳到预览
      if (importConfig.matchBy === 'code') {
        await generatePreview()
        importStep.value = 2
      } else {
        importStep.value = 1
      }
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '提取数据失败')
    } finally {
      importLoading.value = false
    }
  } else if (importStep.value === 1) {
    // 生成预览
    await generatePreview()
    importStep.value = 2
  }
}

const generatePreview = async () => {
  importLoading.value = true
  try {
    const valueMapping = Object.entries(departmentMapping).map(([value, code]) => ({
      value,
      department_code: code || null
    }))
    
    const res: any = await importPreview({
      session_id: sessionId.value,
      value_mapping: valueMapping
    })
    
    previewItems.value = res.preview_items || []
    previewStatistics.value = res.statistics || { total: 0, new_count: 0, update_count: 0, error_count: 0 }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '生成预览失败')
    throw error
  } finally {
    importLoading.value = false
  }
}

const handleImportExecute = async () => {
  importLoading.value = true
  try {
    const res: any = await importExecute({
      session_id: sessionId.value,
      confirmed_items: previewItems.value
    })
    
    if (res.success) {
      const report = res.report
      ElMessage.success(`导入完成：新增 ${report.success_count} 条，更新 ${report.update_count} 条，失败 ${report.error_count} 条`)
      importDialogVisible.value = false
      loadData()
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '导入失败')
  } finally {
    importLoading.value = false
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'new': return 'success'
    case 'update': return 'warning'
    case 'error': return 'danger'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'new': return '新增'
    case 'update': return '覆盖'
    case 'error': return '错误'
    default: return status
  }
}

// 生命周期
onMounted(() => {
  loadData()
  loadDepartments()
})
</script>

<style scoped>
.reference-values-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.search-form {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.import-step {
  min-height: 300px;
}

.parse-result {
  margin-top: 20px;
}

.parse-result h4 {
  margin: 15px 0 10px;
  color: #303133;
}

.preview-statistics {
  margin-bottom: 15px;
  display: flex;
  gap: 10px;
}
</style>
