<template>
  <div class="data-templates-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据模板管理</span>
          <div class="header-buttons">
            <el-button type="primary" @click="handleCreate">新建数据模板</el-button>
            <el-button @click="handleBatchUpload">批量上传</el-button>
            <el-button @click="handleCopy">复制数据模板</el-button>
            <el-button type="danger" @click="handleDeleteAll">全部删除</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索和筛选栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索表名、中文名、说明"
          style="width: 300px"
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </div>
      
      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-checkbox v-model="filterCore" @change="handleSearch">仅显示核心表</el-checkbox>
        <el-checkbox v-model="filterHasDefinition" @change="handleSearch">仅显示已上传文档</el-checkbox>
        <el-checkbox v-model="filterHasSql" @change="handleSearch">仅显示已上传SQL</el-checkbox>
      </div>

      <!-- 数据表格 -->
      <el-table
        :data="tableData"
        v-loading="loading"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="sort_order" label="序号" width="80" align="center" />
        <el-table-column prop="table_name" label="表名" width="200" />
        <el-table-column prop="table_name_cn" label="中文名" width="200" />
        <el-table-column label="核心" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_core" type="danger" size="small">核心</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="文档状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.has_definition" type="success" size="small">已上传</el-tag>
            <el-tag v-else type="info" size="small">未上传</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="SQL状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.has_sql" type="success" size="small">已上传</el-tag>
            <el-tag v-else type="info" size="small">未上传</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" show-overflow-tooltip />
        <el-table-column label="操作" width="400" fixed="right">
          <template #default="{ row, $index }">
            <el-button link type="primary" @click="handleViewDetail(row)">查看详情</el-button>
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link @click="handleMoveUp(row)" :disabled="isFirstItem(row, $index)">上移</el-button>
            <el-button link @click="handleMoveDown(row)" :disabled="isLastItem(row, $index)">下移</el-button>
            <el-button link :type="row.is_core ? 'warning' : 'success'" @click="handleToggleCore(row)">
              {{ row.is_core ? '取消核心' : '设为核心' }}
            </el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="editForm.id ? '编辑数据模板' : '新建数据模板'"
      width="600px"
      append-to-body
      @close="handleEditDialogClose"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editFormRules"
        label-width="120px"
      >
        <el-form-item label="表名" prop="table_name">
          <el-input
            v-model="editForm.table_name"
            placeholder="请输入表名，如：TB_CIS_JJBJL"
            :disabled="!!editForm.id"
          />
        </el-form-item>
        <el-form-item label="中文名" prop="table_name_cn">
          <el-input
            v-model="editForm.table_name_cn"
            placeholder="请输入中文名，如：交接班记录"
          />
        </el-form-item>
        <el-form-item label="说明">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入表说明"
          />
        </el-form-item>
        <el-form-item label="核心表">
          <el-switch v-model="editForm.is_core" />
        </el-form-item>
        
        <!-- 文件上传区域 -->
        <el-divider content-position="left">文件管理</el-divider>
        
        <el-form-item label="表定义文档">
          <div v-if="editForm.has_definition" class="file-info">
            <el-link :href="getDefinitionDownloadUrl(editForm.id!)" target="_blank" type="primary">
              {{ editForm.definition_file_name }}
            </el-link>
            <el-button size="small" type="danger" @click="handleRemoveDefinition" style="margin-left: 10px">
              删除
            </el-button>
          </div>
          <el-upload
            v-else
            ref="definitionUploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".md"
            :on-change="handleDefinitionFileChange"
          >
            <el-button size="small" type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">只能上传 .md 文件，且不超过 10MB</div>
            </template>
          </el-upload>
        </el-form-item>
        
        <el-form-item label="SQL建表代码">
          <div v-if="editForm.has_sql" class="file-info">
            <el-link :href="getSqlDownloadUrl(editForm.id!)" target="_blank" type="primary">
              {{ editForm.sql_file_name }}
            </el-link>
            <el-button size="small" type="danger" @click="handleRemoveSql" style="margin-left: 10px">
              删除
            </el-button>
          </div>
          <el-upload
            v-else
            ref="sqlUploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".sql"
            :on-change="handleSqlFileChange"
          >
            <el-button size="small" type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">只能上传 .sql 文件，且不超过 10MB</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleEditSubmit" :loading="editSubmitting">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 批量上传对话框 -->
    <el-dialog
      v-model="batchUploadDialogVisible"
      title="批量上传数据模板"
      width="800px"
      append-to-body
      @close="handleBatchUploadDialogClose"
    >
      <el-steps :active="batchUploadStep" finish-status="success" align-center>
        <el-step title="选择文件" />
        <el-step title="预览匹配结果" />
        <el-step title="导入完成" />
      </el-steps>

      <!-- 步骤1：选择文件 -->
      <div v-if="batchUploadStep === 0" style="margin-top: 30px">
        <el-form label-width="140px">
          <el-form-item label="表定义文档">
            <el-upload
              ref="batchDefinitionUploadRef"
              :auto-upload="false"
              multiple
              accept=".md"
              :file-list="batchDefinitionFiles"
              :on-change="handleBatchDefinitionChange"
              :on-remove="handleBatchDefinitionRemove"
            >
              <el-button type="primary">选择文件</el-button>
              <template #tip>
                <div class="el-upload__tip">
                  支持多选，文件命名格式：中文名(表名).md，如：交接班记录(TB_CIS_JJBJL).md
                </div>
              </template>
            </el-upload>
          </el-form-item>
          
          <el-form-item label="SQL建表代码">
            <el-upload
              ref="batchSqlUploadRef"
              :auto-upload="false"
              multiple
              accept=".sql"
              :file-list="batchSqlFiles"
              :on-change="handleBatchSqlChange"
              :on-remove="handleBatchSqlRemove"
            >
              <el-button type="primary">选择文件</el-button>
              <template #tip>
                <div class="el-upload__tip">
                  支持多选，文件命名格式：表名.sql，如：TB_CIS_JJBJL.sql
                </div>
              </template>
            </el-upload>
          </el-form-item>
        </el-form>
      </div>

      <!-- 步骤2：预览匹配结果 -->
      <div v-if="batchUploadStep === 1" style="margin-top: 30px">
        <el-alert
          :title="`共匹配 ${batchPreviewData.total} 个数据模板，其中完全匹配 ${batchPreviewData.matched} 个，部分匹配 ${batchPreviewData.partial} 个`"
          type="info"
          :closable="false"
          style="margin-bottom: 15px"
        />
        
        <el-table :data="batchPreviewData.items" border max-height="400">
          <el-table-column prop="table_name" label="表名" width="150" />
          <el-table-column prop="table_name_cn" label="中文名" width="150" />
          <el-table-column prop="definition_file_name" label="表定义文档" show-overflow-tooltip />
          <el-table-column prop="sql_file_name" label="SQL文件" show-overflow-tooltip />
          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <el-tag v-if="row.status === 'matched'" type="success">完全匹配</el-tag>
              <el-tag v-else-if="row.status === 'partial'" type="warning">部分匹配</el-tag>
              <el-tag v-else type="info">未匹配</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="message" label="说明" show-overflow-tooltip />
        </el-table>
      </div>

      <!-- 步骤3：导入完成 -->
      <div v-if="batchUploadStep === 2" style="margin-top: 30px">
        <el-result
          icon="success"
          title="导入完成"
          :sub-title="`成功 ${batchUploadResult.success_count} 个，失败 ${batchUploadResult.failed_count} 个`"
        >
          <template #extra>
            <el-button type="primary" @click="handleBatchUploadFinish">完成</el-button>
          </template>
        </el-result>
        
        <el-collapse v-if="batchUploadResult.details.length > 0" style="margin-top: 20px">
          <el-collapse-item title="查看详细信息" name="1">
            <el-table :data="batchUploadResult.details" border max-height="300">
              <el-table-column prop="table_name" label="表名" width="150" />
              <el-table-column prop="action" label="操作" width="100">
                <template #default="{ row }">
                  <el-tag v-if="row.action === 'created'" type="success">创建</el-tag>
                  <el-tag v-else-if="row.action === 'updated'" type="warning">更新</el-tag>
                  <el-tag v-else type="danger">失败</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="message" label="说明" show-overflow-tooltip />
            </el-table>
          </el-collapse-item>
        </el-collapse>
      </div>

      <template #footer>
        <div v-if="batchUploadStep === 0">
          <el-button @click="batchUploadDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            @click="handleBatchUploadNext"
            :disabled="batchDefinitionFiles.length === 0 && batchSqlFiles.length === 0"
          >
            下一步
          </el-button>
        </div>
        <div v-else-if="batchUploadStep === 1">
          <el-button @click="batchUploadStep = 0">上一步</el-button>
          <el-button type="primary" @click="handleBatchUploadConfirm" :loading="batchUploading">
            确认导入
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 复制对话框 -->
    <el-dialog
      v-model="copyDialogVisible"
      title="复制数据模板"
      width="900px"
      append-to-body
      @close="handleCopyDialogClose"
    >
      <el-steps :active="copyStep" finish-status="success" align-center>
        <el-step title="选择医疗机构" />
        <el-step title="选择数据模板" />
        <el-step title="复制完成" />
      </el-steps>

      <!-- 步骤1：选择医疗机构 -->
      <div v-if="copyStep === 0" style="margin-top: 30px">
        <el-table
          :data="hospitalList"
          border
          highlight-current-row
          @current-change="handleHospitalSelect"
          max-height="400"
        >
          <el-table-column type="index" label="序号" width="60" />
          <el-table-column prop="code" label="机构编码" width="150" />
          <el-table-column prop="name" label="机构名称" />
        </el-table>
      </div>

      <!-- 步骤2：选择数据模板 -->
      <div v-if="copyStep === 1" style="margin-top: 30px">
        <el-alert
          :title="`从 ${selectedHospital?.name} 复制数据模板`"
          type="info"
          :closable="false"
          style="margin-bottom: 15px"
        />
        
        <el-form label-width="120px" style="margin-bottom: 15px">
          <el-form-item label="冲突处理策略">
            <el-radio-group v-model="copyConflictStrategy">
              <el-radio label="skip">跳过已存在的表</el-radio>
              <el-radio label="overwrite">覆盖已存在的表</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
        
        <el-table
          ref="copyTableRef"
          :data="sourceTemplateList"
          border
          @selection-change="handleCopySelectionChange"
          max-height="400"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="table_name" label="表名" width="150" />
          <el-table-column prop="table_name_cn" label="中文名" width="150" />
          <el-table-column label="核心" width="80" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.is_core" type="danger" size="small">核心</el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="文档" width="80" align="center">
            <template #default="{ row }">
              <el-icon v-if="row.has_definition" color="#67C23A"><Check /></el-icon>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="SQL" width="80" align="center">
            <template #default="{ row }">
              <el-icon v-if="row.has_sql" color="#67C23A"><Check /></el-icon>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="说明" show-overflow-tooltip />
        </el-table>
        
        <div style="margin-top: 10px">
          <el-button size="small" @click="handleCopySelectAll">全选</el-button>
          <el-button size="small" @click="handleCopyClearSelection">清空</el-button>
          <span style="margin-left: 10px; color: #909399">
            已选择 {{ copySelectedIds.length }} 个数据模板
          </span>
        </div>
      </div>

      <!-- 步骤3：复制完成 -->
      <div v-if="copyStep === 2" style="margin-top: 30px">
        <el-result
          icon="success"
          title="复制完成"
          :sub-title="`成功 ${copyResult.success_count} 个，跳过 ${copyResult.skipped_count} 个，失败 ${copyResult.failed_count} 个`"
        >
          <template #extra>
            <el-button type="primary" @click="handleCopyFinish">完成</el-button>
          </template>
        </el-result>
        
        <el-collapse v-if="copyResult.details.length > 0" style="margin-top: 20px">
          <el-collapse-item title="查看详细信息" name="1">
            <el-table :data="copyResult.details" border max-height="300">
              <el-table-column prop="table_name" label="表名" width="150" />
              <el-table-column prop="action" label="操作" width="100">
                <template #default="{ row }">
                  <el-tag v-if="row.action === 'copied'" type="success">复制</el-tag>
                  <el-tag v-else-if="row.action === 'overwritten'" type="warning">覆盖</el-tag>
                  <el-tag v-else-if="row.action === 'skipped'" type="info">跳过</el-tag>
                  <el-tag v-else type="danger">失败</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="message" label="说明" show-overflow-tooltip />
            </el-table>
          </el-collapse-item>
        </el-collapse>
      </div>

      <template #footer>
        <div v-if="copyStep === 0">
          <el-button @click="copyDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            @click="handleCopyNext"
            :disabled="!selectedHospital"
          >
            下一步
          </el-button>
        </div>
        <div v-else-if="copyStep === 1">
          <el-button @click="copyStep = 0">上一步</el-button>
          <el-button
            type="primary"
            @click="handleCopyConfirm"
            :loading="copying"
            :disabled="copySelectedIds.length === 0"
          >
            确认复制
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <DataTemplateDetailDialog
      v-model="detailDialogVisible"
      :template-id="currentTemplateId"
    />
  </div>
</template>


<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Check } from '@element-plus/icons-vue'
import DataTemplateDetailDialog from '@/components/DataTemplateDetailDialog.vue'
import type { FormInstance, FormRules, UploadFile, UploadInstance } from 'element-plus'
import request from '@/utils/request'
import {
  getDataTemplates,
  createDataTemplate,
  updateDataTemplate,
  deleteDataTemplate,
  uploadDefinitionFile,
  uploadSqlFile,
  downloadDefinitionFile,
  downloadSqlFile,
  batchUploadFiles,
  moveUp,
  moveDown,
  toggleCore,
  getHospitalsForCopy,
  getHospitalTemplates,
  copyTemplates,
  type DataTemplate,
  type DataTemplateCreate,
  type DataTemplateUpdate,
  type BatchUploadPreview,
  type BatchUploadResult,
  type HospitalSimple,
  type CopyResult
} from '@/api/data-templates'

// 数据
const loading = ref(false)
const tableData = ref<DataTemplate[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchKeyword = ref('')
const filterCore = ref(false)
const filterHasDefinition = ref(false)
const filterHasSql = ref(false)

// 编辑对话框
const editDialogVisible = ref(false)
const editSubmitting = ref(false)
const editFormRef = ref<FormInstance>()
const definitionUploadRef = ref<UploadInstance>()
const sqlUploadRef = ref<UploadInstance>()
const editForm = reactive<any>({
  id: null,
  table_name: '',
  table_name_cn: '',
  description: '',
  is_core: false,
  has_definition: false,
  has_sql: false,
  definition_file_name: '',
  sql_file_name: ''
})
const editFormRules: FormRules = {
  table_name: [
    { required: true, message: '请输入表名', trigger: 'blur' },
    { pattern: /^[A-Za-z0-9_]+$/, message: '表名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  table_name_cn: [
    { required: true, message: '请输入中文名', trigger: 'blur' }
  ]
}

// 待上传的文件
const pendingDefinitionFile = ref<File | null>(null)
const pendingSqlFile = ref<File | null>(null)

// 批量上传对话框
const batchUploadDialogVisible = ref(false)
const batchUploadStep = ref(0)
const batchUploading = ref(false)
const batchDefinitionUploadRef = ref<UploadInstance>()
const batchSqlUploadRef = ref<UploadInstance>()
const batchDefinitionFiles = ref<UploadFile[]>([])
const batchSqlFiles = ref<UploadFile[]>([])
const batchPreviewData = ref<BatchUploadPreview>({
  items: [],
  total: 0,
  matched: 0,
  partial: 0,
  unmatched: 0
})
const batchUploadResult = ref<BatchUploadResult>({
  success_count: 0,
  failed_count: 0,
  skipped_count: 0,
  details: []
})

// 详情对话框
const detailDialogVisible = ref(false)
const currentTemplateId = ref<number | null>(null)

// 复制对话框
const copyDialogVisible = ref(false)
const copyStep = ref(0)
const copying = ref(false)
const copyTableRef = ref()
const hospitalList = ref<HospitalSimple[]>([])
const selectedHospital = ref<HospitalSimple | null>(null)
const sourceTemplateList = ref<DataTemplate[]>([])
const copySelectedIds = ref<number[]>([])
const copyConflictStrategy = ref<'skip' | 'overwrite'>('skip')
const copyResult = ref<CopyResult>({
  success_count: 0,
  skipped_count: 0,
  failed_count: 0,
  details: []
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      size: pageSize.value
    }
    
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    if (filterCore.value) {
      params.is_core = true
    }
    if (filterHasDefinition.value) {
      params.has_definition = true
    }
    if (filterHasSql.value) {
      params.has_sql = true
    }
    
    const res = await getDataTemplates(params)
    tableData.value = res.items
    total.value = res.total
  } catch (error: any) {
    ElMessage.error(error.message || '加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

// 处理每页数量变化
const handleSizeChange = () => {
  currentPage.value = 1
  loadData()
}

// 处理页码变化
const handlePageChange = () => {
  loadData()
}

// 查看详情
const handleViewDetail = (row: DataTemplate) => {
  currentTemplateId.value = row.id
  detailDialogVisible.value = true
}

// 新建
const handleCreate = () => {
  Object.assign(editForm, {
    id: null,
    table_name: '',
    table_name_cn: '',
    description: '',
    is_core: false,
    has_definition: false,
    has_sql: false,
    definition_file_name: '',
    sql_file_name: ''
  })
  pendingDefinitionFile.value = null
  pendingSqlFile.value = null
  editDialogVisible.value = true
}

// 编辑
const handleEdit = (row: DataTemplate) => {
  Object.assign(editForm, {
    id: row.id,
    table_name: row.table_name,
    table_name_cn: row.table_name_cn,
    description: row.description || '',
    is_core: row.is_core,
    has_definition: row.has_definition,
    has_sql: row.has_sql,
    definition_file_name: row.definition_file_name || '',
    sql_file_name: row.sql_file_name || ''
  })
  pendingDefinitionFile.value = null
  pendingSqlFile.value = null
  editDialogVisible.value = true
}

// 关闭编辑对话框
const handleEditDialogClose = () => {
  editFormRef.value?.resetFields()
  pendingDefinitionFile.value = null
  pendingSqlFile.value = null
}

// 提交编辑
const handleEditSubmit = async () => {
  if (!editFormRef.value) return
  
  await editFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    editSubmitting.value = true
    try {
      if (editForm.id) {
        // 更新
        const updateData: DataTemplateUpdate = {
          table_name_cn: editForm.table_name_cn,
          description: editForm.description,
          is_core: editForm.is_core
        }
        await updateDataTemplate(editForm.id, updateData)
        
        // 上传文件
        if (pendingDefinitionFile.value) {
          await uploadDefinitionFile(editForm.id, pendingDefinitionFile.value)
        }
        if (pendingSqlFile.value) {
          await uploadSqlFile(editForm.id, pendingSqlFile.value)
        }
        
        ElMessage.success('更新成功')
      } else {
        // 创建
        const createData: DataTemplateCreate = {
          table_name: editForm.table_name,
          table_name_cn: editForm.table_name_cn,
          description: editForm.description,
          is_core: editForm.is_core
        }
        const res = await createDataTemplate(createData)
        
        // 上传文件
        if (pendingDefinitionFile.value) {
          await uploadDefinitionFile(res.id, pendingDefinitionFile.value)
        }
        if (pendingSqlFile.value) {
          await uploadSqlFile(res.id, pendingSqlFile.value)
        }
        
        ElMessage.success('创建成功')
      }
      
      editDialogVisible.value = false
      loadData()
    } catch (error: any) {
      ElMessage.error(error.message || '操作失败')
    } finally {
      editSubmitting.value = false
    }
  })
}

// 文件选择处理
const handleDefinitionFileChange = (file: UploadFile) => {
  if (file.raw) {
    pendingDefinitionFile.value = file.raw
  }
}

const handleSqlFileChange = (file: UploadFile) => {
  if (file.raw) {
    pendingSqlFile.value = file.raw
  }
}

// 删除文件
const handleRemoveDefinition = async () => {
  try {
    await ElMessageBox.confirm('确定要删除表定义文档吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    editForm.has_definition = false
    editForm.definition_file_name = ''
    ElMessage.success('已标记删除，保存后生效')
  } catch (error) {
    // 用户取消
  }
}

const handleRemoveSql = async () => {
  try {
    await ElMessageBox.confirm('确定要删除SQL建表代码吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    editForm.has_sql = false
    editForm.sql_file_name = ''
    ElMessage.success('已标记删除，保存后生效')
  } catch (error) {
    // 用户取消
  }
}

// 获取下载URL
const getDefinitionDownloadUrl = (id: number) => {
  return downloadDefinitionFile(id)
}

const getSqlDownloadUrl = (id: number) => {
  return downloadSqlFile(id)
}

// 删除
const handleDelete = async (row: DataTemplate) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除数据模板"${row.table_name_cn}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteDataTemplate(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 判断是否是第一项（全局）
const isFirstItem = (row: DataTemplate, index: number) => {
  // 如果是第一页的第一项，则是全局第一项
  return currentPage.value === 1 && index === 0
}

// 判断是否是最后一项（全局）
const isLastItem = (row: DataTemplate, index: number) => {
  // 如果是最后一页的最后一项，则是全局最后一项
  const isLastPage = currentPage.value * pageSize.value >= total.value
  const isLastInPage = index === tableData.value.length - 1
  return isLastPage && isLastInPage
}

// 上移
const handleMoveUp = async (row: DataTemplate) => {
  try {
    await moveUp(row.id)
    ElMessage.success('上移成功')
    
    // 如果上移后当前项是当前页的第一项，且不是第一页，则跳转到上一页
    const currentIndex = tableData.value.findIndex(item => item.id === row.id)
    if (currentIndex === 0 && currentPage.value > 1) {
      currentPage.value--
    }
    
    loadData()
  } catch (error: any) {
    ElMessage.error(error.message || '上移失败')
  }
}

// 下移
const handleMoveDown = async (row: DataTemplate) => {
  try {
    await moveDown(row.id)
    ElMessage.success('下移成功')
    
    // 如果下移后当前项是当前页的最后一项，且不是最后一页，则跳转到下一页
    const currentIndex = tableData.value.findIndex(item => item.id === row.id)
    const isLastInPage = currentIndex === tableData.value.length - 1
    const isNotLastPage = currentPage.value * pageSize.value < total.value
    if (isLastInPage && isNotLastPage) {
      currentPage.value++
    }
    
    loadData()
  } catch (error: any) {
    ElMessage.error(error.message || '下移失败')
  }
}

// 切换核心标志
const handleToggleCore = async (row: DataTemplate) => {
  try {
    await toggleCore(row.id)
    ElMessage.success(row.is_core ? '已取消核心标记' : '已设为核心表')
    loadData()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

// 批量上传
const handleBatchUpload = () => {
  batchUploadStep.value = 0
  batchDefinitionFiles.value = []
  batchSqlFiles.value = []
  batchPreviewData.value = {
    items: [],
    total: 0,
    matched: 0,
    partial: 0,
    unmatched: 0
  }
  batchUploadResult.value = {
    success_count: 0,
    failed_count: 0,
    skipped_count: 0,
    details: []
  }
  batchUploadDialogVisible.value = true
}

const handleBatchUploadDialogClose = () => {
  batchDefinitionFiles.value = []
  batchSqlFiles.value = []
}

const handleBatchDefinitionChange = (file: UploadFile, fileList: UploadFile[]) => {
  batchDefinitionFiles.value = fileList
}

const handleBatchDefinitionRemove = (file: UploadFile, fileList: UploadFile[]) => {
  batchDefinitionFiles.value = fileList
}

const handleBatchSqlChange = (file: UploadFile, fileList: UploadFile[]) => {
  batchSqlFiles.value = fileList
}

const handleBatchSqlRemove = (file: UploadFile, fileList: UploadFile[]) => {
  batchSqlFiles.value = fileList
}

const handleBatchUploadNext = async () => {
  // 这里可以调用预览API，但为了简化，直接进入下一步
  batchUploadStep.value = 1
  
  // 模拟预览数据（实际应该调用API）
  const definitionFilesList = batchDefinitionFiles.value.map(f => f.raw!).filter(f => f)
  const sqlFilesList = batchSqlFiles.value.map(f => f.raw!).filter(f => f)
  
  // 简单的本地匹配预览
  const preview: any = {
    items: [],
    total: 0,
    matched: 0,
    partial: 0,
    unmatched: 0
  }
  
  // 解析文件名（支持英文括号和中文括号）
  definitionFilesList.forEach(file => {
    const match = file.name.match(/^(.+?)[\(（]([A-Za-z0-9_]+)[\)）]\.md$/)
    if (match) {
      const tableName = match[2]
      const tableNameCn = match[1]
      const sqlFile = sqlFilesList.find(f => f.name === `${tableName}.sql`)
      
      preview.items.push({
        table_name: tableName,
        table_name_cn: tableNameCn,
        definition_file_name: file.name,
        sql_file_name: sqlFile?.name || '',
        status: sqlFile ? 'matched' : 'partial',
        message: sqlFile ? '完全匹配' : '仅有表定义文档'
      })
      
      if (sqlFile) {
        preview.matched++
      } else {
        preview.partial++
      }
    }
  })
  
  // 检查只有SQL文件的情况
  sqlFilesList.forEach(file => {
    const tableName = file.name.replace('.sql', '')
    const hasDefinition = preview.items.some((item: any) => item.table_name === tableName)
    
    if (!hasDefinition) {
      preview.items.push({
        table_name: tableName,
        table_name_cn: '',
        definition_file_name: '',
        sql_file_name: file.name,
        status: 'partial',
        message: '仅有SQL建表代码'
      })
      preview.partial++
    }
  })
  
  preview.total = preview.items.length
  batchPreviewData.value = preview
}

const handleBatchUploadConfirm = async () => {
  batchUploading.value = true
  try {
    const definitionFilesList = batchDefinitionFiles.value.map(f => f.raw!).filter(f => f)
    const sqlFilesList = batchSqlFiles.value.map(f => f.raw!).filter(f => f)
    
    const res = await batchUploadFiles(definitionFilesList, sqlFilesList)
    batchUploadResult.value = res
    batchUploadStep.value = 2
  } catch (error: any) {
    ElMessage.error(error.message || '批量上传失败')
  } finally {
    batchUploading.value = false
  }
}

const handleBatchUploadFinish = () => {
  batchUploadDialogVisible.value = false
  loadData()
}

// 复制
const handleCopy = async () => {
  copyStep.value = 0
  selectedHospital.value = null
  sourceTemplateList.value = []
  copySelectedIds.value = []
  copyConflictStrategy.value = 'skip'
  copyResult.value = {
    success_count: 0,
    skipped_count: 0,
    failed_count: 0,
    details: []
  }
  
  try {
    const res = await getHospitalsForCopy()
    hospitalList.value = res
    copyDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取医疗机构列表失败')
  }
}

const handleCopyDialogClose = () => {
  selectedHospital.value = null
  sourceTemplateList.value = []
  copySelectedIds.value = []
}

const handleHospitalSelect = (row: HospitalSimple) => {
  selectedHospital.value = row
}

const handleCopyNext = async () => {
  if (!selectedHospital.value) {
    ElMessage.warning('请选择医疗机构')
    return
  }
  
  try {
    // 加载源医疗机构的数据模板列表
    const res = await getHospitalTemplates(selectedHospital.value.id)
    sourceTemplateList.value = res
    copyStep.value = 1
  } catch (error: any) {
    ElMessage.error(error.message || '加载数据模板失败')
  }
}

const handleCopySelectionChange = (selection: DataTemplate[]) => {
  copySelectedIds.value = selection.map(item => item.id)
}

const handleCopySelectAll = () => {
  copyTableRef.value?.toggleAllSelection()
}

const handleCopyClearSelection = () => {
  copyTableRef.value?.clearSelection()
}

const handleCopyConfirm = async () => {
  if (copySelectedIds.value.length === 0) {
    ElMessage.warning('请选择要复制的数据模板')
    return
  }
  
  copying.value = true
  try {
    const res = await copyTemplates({
      source_hospital_id: selectedHospital.value!.id,
      template_ids: copySelectedIds.value,
      conflict_strategy: copyConflictStrategy.value
    })
    copyResult.value = res
    copyStep.value = 2
  } catch (error: any) {
    ElMessage.error(error.message || '复制失败')
  } finally {
    copying.value = false
  }
}

const handleCopyFinish = () => {
  copyDialogVisible.value = false
  loadData()
}

// 全部删除
const handleDeleteAll = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要删除当前医院的所有数据模板吗？此操作不可恢复！',
      '警告',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    loading.value = true
    await request.delete('/data-templates/clear-all')
    ElMessage.success('删除成功')
    loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  } finally {
    loading.value = false
  }
}

// 初始化
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.data-templates-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-buttons {
  display: flex;
  gap: 10px;
}

.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.filter-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.file-info {
  display: flex;
  align-items: center;
}
</style>
