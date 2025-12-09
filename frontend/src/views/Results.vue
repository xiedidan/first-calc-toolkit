<template>
  <div class="results-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>业务价值报表</span>
          <div class="header-actions">
            <el-button @click="exportSummary" :loading="exporting">导出汇总表</el-button>
            <el-button type="primary" @click="exportDetail" :loading="exporting">导出明细表</el-button>
          </div>
        </div>
      </template>

      <!-- 筛选条件 -->
      <div class="filter-section">
        <el-form :inline="true" :model="filterForm">
          <el-form-item label="评估月份">
            <el-date-picker
              v-model="filterForm.period"
              type="month"
              placeholder="选择月份"
              format="YYYY-MM"
              value-format="YYYY-MM"
              @change="onPeriodChange"
            />
          </el-form-item>
          <el-form-item label="模型版本">
            <el-select 
              v-model="filterForm.model_version_id" 
              placeholder="默认使用激活版本" 
              @change="onVersionChange" 
              clearable
              style="width: 240px"
            >
              <el-option
                v-for="version in versions"
                :key="version.id"
                :label="version.name"
                :value="version.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="计算任务">
            <el-select 
              v-model="selectedTaskId" 
              placeholder="默认使用最新任务" 
              @change="onTaskChange" 
              clearable
              :loading="loadingTasks"
              style="width: 320px"
            >
              <el-option
                v-for="task in availableTasks"
                :key="task.task_id"
                :label="task.label"
                :value="task.task_id"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>

      <!-- 汇总表 -->
      <div class="table-section">
        <h3>科室业务价值汇总</h3>
        <el-table :data="summaryData" v-loading="loading" stripe border>
        <el-table-column prop="department_code" label="科室代码" width="120" fixed>
          <template #default="{ row }">
            {{ row.department_code || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="department_name" label="科室名称" width="200" fixed />
        <el-table-column label="医生序列" align="center">
          <el-table-column prop="doctor_value" label="价值" width="120" align="right">
            <template #default="{ row }">
              {{ formatNumber(row.doctor_value) }}
            </template>
          </el-table-column>
          <el-table-column prop="doctor_ratio" label="占比" width="100" align="right">
            <template #default="{ row }">
              {{ formatPercent(row.doctor_ratio) }}
            </template>
          </el-table-column>
        </el-table-column>
        <el-table-column label="护理序列" align="center">
          <el-table-column prop="nurse_value" label="价值" width="120" align="right">
            <template #default="{ row }">
              {{ formatNumber(row.nurse_value) }}
            </template>
          </el-table-column>
          <el-table-column prop="nurse_ratio" label="占比" width="100" align="right">
            <template #default="{ row }">
              {{ formatPercent(row.nurse_ratio) }}
            </template>
          </el-table-column>
        </el-table-column>
        <el-table-column label="医技序列" align="center">
          <el-table-column prop="tech_value" label="价值" width="120" align="right">
            <template #default="{ row }">
              {{ formatNumber(row.tech_value) }}
            </template>
          </el-table-column>
          <el-table-column prop="tech_ratio" label="占比" width="100" align="right">
            <template #default="{ row }">
              {{ formatPercent(row.tech_ratio) }}
            </template>
          </el-table-column>
        </el-table-column>
        <el-table-column prop="total_value" label="科室总价值" width="150" align="right">
          <template #default="{ row }">
            {{ formatNumber(row.total_value) }}
          </template>
        </el-table-column>
        <el-table-column prop="reference_value" label="参考总价值" width="150" align="right">
          <template #default="{ row }">
            {{ formatReferenceValue(row) }}
          </template>
        </el-table-column>
        <el-table-column prop="actual_reference_ratio" label="实际参考比" width="120" align="right">
          <template #default="{ row }">
            {{ formatActualReferenceRatio(row) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">
              查看明细
            </el-button>
          </template>
        </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 明细对话框 -->
    <el-dialog 
      v-model="detailDialogVisible" 
      :title="`${currentDepartment?.department_name} - 业务价值明细`"
      width="95%" 
      top="3vh"
      append-to-body
      class="detail-dialog"
    >
      <el-tabs v-model="activeTab" class="detail-tabs">
        <!-- 医生序列 -->
        <el-tab-pane label="医生序列" name="doctor" v-if="detailData?.doctor && detailData.doctor.length > 0">
          <div class="table-title">{{ currentDepartment?.department_name }} - 医生序列业务价值明细（{{ filterForm.period }}）</div>
          <el-table 
            :data="detailData.doctor" 
            border 
            stripe
            class="structure-table"
            row-key="id"
            :tree-props="{ children: 'children' }"
            :default-expand-all="true"
          >
            <el-table-column prop="dimension_name" label="维度名称（业务价值占比）" min-width="240" align="left">
              <template #default="{ row }">
                <span class="dimension-name">{{ row.dimension_name }}</span>
                <span v-if="row.ratio != null" class="ratio-text">（{{ formatPercent(row.ratio) }}）</span>
              </template>
            </el-table-column>
            <el-table-column prop="workload" label="工作量" min-width="110" align="right">
              <template #default="{ row }">{{ formatNumber(row.workload) }}</template>
            </el-table-column>
            <el-table-column prop="hospital_value" label="全院业务价值" min-width="102" align="right">
              <template #default="{ row }">{{ formatValueOrDash(row.hospital_value) }}</template>
            </el-table-column>
            <el-table-column prop="business_guide" label="业务导向" min-width="168" align="center">
              <template #default="{ row }">{{ row.business_guide || '-' }}</template>
            </el-table-column>
            <el-table-column prop="dept_value" label="科室业务价值" min-width="102" align="right">
              <template #default="{ row }">{{ formatValueOrDash(row.dept_value) }}</template>
            </el-table-column>
            <el-table-column prop="amount" label="业务价值金额" min-width="110" align="right">
              <template #default="{ row }">{{ formatNumber(row.amount) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="80" align="center" fixed="right">
              <template #default="{ row }">
                <el-button
                  v-if="canDrillDown(row, 'doctor')"
                  link
                  type="primary"
                  size="small"
                  @click="handleDrillDown(row)"
                >
                  下钻
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 护理序列 -->
        <el-tab-pane label="护理序列" name="nurse" v-if="detailData?.nurse && detailData.nurse.length > 0">
          <div class="table-title">{{ currentDepartment?.department_name }} - 护理序列业务价值明细（{{ filterForm.period }}）</div>
          <el-table 
            :data="detailData.nurse" 
            border 
            stripe
            class="structure-table"
            row-key="id"
            :tree-props="{ children: 'children' }"
            :default-expand-all="true"
          >
            <el-table-column prop="dimension_name" label="维度名称（业务价值占比）" min-width="240" align="left">
              <template #default="{ row }">
                <span class="dimension-name">{{ row.dimension_name }}</span>
                <span v-if="row.ratio != null" class="ratio-text">（{{ formatPercent(row.ratio) }}）</span>
              </template>
            </el-table-column>
            <el-table-column prop="workload" label="工作量" min-width="110" align="right">
              <template #default="{ row }">{{ formatNumber(row.workload) }}</template>
            </el-table-column>
            <el-table-column prop="hospital_value" label="全院业务价值" min-width="102" align="right">
              <template #default="{ row }">{{ formatValueOrDash(row.hospital_value) }}</template>
            </el-table-column>
            <el-table-column prop="business_guide" label="业务导向" min-width="168" align="center">
              <template #default="{ row }">{{ row.business_guide || '-' }}</template>
            </el-table-column>
            <el-table-column prop="dept_value" label="科室业务价值" min-width="102" align="right">
              <template #default="{ row }">{{ formatValueOrDash(row.dept_value) }}</template>
            </el-table-column>
            <el-table-column prop="amount" label="业务价值金额" min-width="110" align="right">
              <template #default="{ row }">{{ formatNumber(row.amount) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="80" align="center" fixed="right">
              <template #default="{ row }">
                <el-button
                  v-if="canDrillDown(row, 'nurse')"
                  link
                  type="primary"
                  size="small"
                  @click="handleDrillDown(row)"
                >
                  下钻
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 医技序列 -->
        <el-tab-pane label="医技序列" name="tech" v-if="detailData?.tech && detailData.tech.length > 0">
          <div class="table-title">{{ currentDepartment?.department_name }} - 医技序列业务价值明细（{{ filterForm.period }}）</div>
          <el-table 
            :data="detailData.tech" 
            border 
            stripe
            class="structure-table"
            row-key="id"
            :tree-props="{ children: 'children' }"
            :default-expand-all="true"
          >
            <el-table-column prop="dimension_name" label="维度名称（业务价值占比）" min-width="240" align="left">
              <template #default="{ row }">
                <span class="dimension-name">{{ row.dimension_name }}</span>
                <span v-if="row.ratio != null" class="ratio-text">（{{ formatPercent(row.ratio) }}）</span>
              </template>
            </el-table-column>
            <el-table-column prop="workload" label="工作量" min-width="110" align="right">
              <template #default="{ row }">{{ formatNumber(row.workload) }}</template>
            </el-table-column>
            <el-table-column prop="hospital_value" label="全院业务价值" min-width="102" align="right">
              <template #default="{ row }">{{ formatValueOrDash(row.hospital_value) }}</template>
            </el-table-column>
            <el-table-column prop="business_guide" label="业务导向" min-width="168" align="center">
              <template #default="{ row }">{{ row.business_guide || '-' }}</template>
            </el-table-column>
            <el-table-column prop="dept_value" label="科室业务价值" min-width="102" align="right">
              <template #default="{ row }">{{ formatValueOrDash(row.dept_value) }}</template>
            </el-table-column>
            <el-table-column prop="amount" label="业务价值金额" min-width="110" align="right">
              <template #default="{ row }">{{ formatNumber(row.amount) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="80" align="center" fixed="right">
              <template #default="{ row }">
                <el-button
                  v-if="canDrillDown(row, 'tech')"
                  link
                  type="primary"
                  size="small"
                  @click="handleDrillDown(row)"
                >
                  下钻
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 导向汇总 -->
        <el-tab-pane label="导向汇总" name="orientation">
          <div class="table-title">{{ currentDepartment?.department_name }} - 业务导向调整汇总（{{ filterForm.period }}）</div>
          
          <el-tabs v-model="orientationActiveTab" type="card" class="orientation-tabs">
            <!-- 医生序列导向 -->
            <el-tab-pane label="医生序列" name="doctor" v-if="orientationData?.doctor && orientationData.doctor.length > 0">
              <el-table :data="orientationData.doctor" border stripe max-height="500">
                <el-table-column prop="department_name" label="科室" width="120" fixed />
                <el-table-column prop="node_code" label="维度代码" width="120" />
                <el-table-column prop="node_name" label="维度名称" width="180" />
                <el-table-column prop="orientation_rule_name" label="导向规则" width="150" />
                <el-table-column prop="orientation_type" label="导向类型" width="120">
                  <template #default="{ row }">
                    {{ row.orientation_type === 'benchmark_ladder' ? '基准阶梯' : '固定基准' }}
                  </template>
                </el-table-column>
                <el-table-column prop="actual_value" label="实际值" width="100" align="right">
                  <template #default="{ row }">{{ formatNumber(row.actual_value) }}</template>
                </el-table-column>
                <el-table-column prop="benchmark_value" label="基准值" width="100" align="right">
                  <template #default="{ row }">{{ formatNumber(row.benchmark_value) }}</template>
                </el-table-column>
                <el-table-column prop="orientation_ratio" label="导向比例" width="100" align="right">
                  <template #default="{ row }">{{ formatNumber(row.orientation_ratio) }}</template>
                </el-table-column>
                <el-table-column prop="adjustment_intensity" label="调整力度" width="100" align="right">
                  <template #default="{ row }">{{ formatNumber(row.adjustment_intensity) }}</template>
                </el-table-column>
                <el-table-column prop="original_weight" label="原始权重" width="110" align="right">
                  <template #default="{ row }">{{ formatNumber(row.original_weight) }}</template>
                </el-table-column>
                <el-table-column prop="adjusted_weight" label="调整后权重" width="110" align="right">
                  <template #default="{ row }">{{ formatNumber(row.adjusted_weight) }}</template>
                </el-table-column>
                <el-table-column prop="is_adjusted" label="是否调整" width="90" align="center">
                  <template #default="{ row }">
                    <el-tag :type="row.is_adjusted ? 'success' : 'info'" size="small">
                      {{ row.is_adjusted ? '是' : '否' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="adjustment_reason" label="未调整原因" min-width="150" show-overflow-tooltip />
              </el-table>
            </el-tab-pane>

            <!-- 护理序列导向 -->
            <el-tab-pane label="护理序列" name="nurse" v-if="orientationData?.nurse && orientationData.nurse.length > 0">
              <el-table :data="orientationData.nurse" border stripe max-height="500">
                <el-table-column prop="department_name" label="科室" width="120" fixed />
                <el-table-column prop="node_code" label="维度代码" width="120" />
                <el-table-column prop="node_name" label="维度名称" width="180" />
                <el-table-column prop="orientation_rule_name" label="导向规则" width="150" />
                <el-table-column prop="orientation_type" label="导向类型" width="120">
                  <template #default="{ row }">
                    {{ row.orientation_type === 'benchmark_ladder' ? '基准阶梯' : '固定基准' }}
                  </template>
                </el-table-column>
                <el-table-column prop="actual_value" label="实际值" width="100" align="right">
                  <template #default="{ row }">{{ formatNumber(row.actual_value) }}</template>
                </el-table-column>
                <el-table-column prop="benchmark_value" label="基准值" width="100" align="right">
                  <template #default="{ row }">{{ formatNumber(row.benchmark_value) }}</template>
                </el-table-column>
                <el-table-column prop="orientation_ratio" label="导向比例" width="100" align="right">
                  <template #default="{ row }">{{ formatNumber(row.orientation_ratio) }}</template>
                </el-table-column>
                <el-table-column prop="adjustment_intensity" label="调整力度" width="100" align="right">
                  <template #default="{ row }">{{ formatNumber(row.adjustment_intensity) }}</template>
                </el-table-column>
                <el-table-column prop="original_weight" label="原始权重" width="110" align="right">
                  <template #default="{ row }">{{ formatNumber(row.original_weight) }}</template>
                </el-table-column>
                <el-table-column prop="adjusted_weight" label="调整后权重" width="110" align="right">
                  <template #default="{ row }">{{ formatNumber(row.adjusted_weight) }}</template>
                </el-table-column>
                <el-table-column prop="is_adjusted" label="是否调整" width="90" align="center">
                  <template #default="{ row }">
                    <el-tag :type="row.is_adjusted ? 'success' : 'info'" size="small">
                      {{ row.is_adjusted ? '是' : '否' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="adjustment_reason" label="未调整原因" min-width="150" show-overflow-tooltip />
              </el-table>
            </el-tab-pane>

            <!-- 医技序列导向 -->
            <el-tab-pane label="医技序列" name="tech" v-if="orientationData?.tech && orientationData.tech.length > 0">
              <el-table :data="orientationData.tech" border stripe max-height="500">
                <el-table-column prop="department_name" label="科室" width="120" fixed />
                <el-table-column prop="node_code" label="维度代码" width="120" />
                <el-table-column prop="node_name" label="维度名称" width="180" />
                <el-table-column prop="orientation_rule_name" label="导向规则" width="150" />
                <el-table-column prop="orientation_type" label="导向类型" width="120">
                  <template #default="{ row }">
                    {{ row.orientation_type === 'benchmark_ladder' ? '基准阶梯' : '固定基准' }}
                  </template>
                </el-table-column>
                <el-table-column prop="actual_value" label="实际值" width="100" align="right">
                  <template #default="{ row }">{{ formatNumber(row.actual_value) }}</template>
                </el-table-column>
                <el-table-column prop="benchmark_value" label="基准值" width="100" align="right">
                  <template #default="{ row }">{{ formatNumber(row.benchmark_value) }}</template>
                </el-table-column>
                <el-table-column prop="orientation_ratio" label="导向比例" width="100" align="right">
                  <template #default="{ row }">{{ formatNumber(row.orientation_ratio) }}</template>
                </el-table-column>
                <el-table-column prop="adjustment_intensity" label="调整力度" width="100" align="right">
                  <template #default="{ row }">{{ formatNumber(row.adjustment_intensity) }}</template>
                </el-table-column>
                <el-table-column prop="original_weight" label="原始权重" width="110" align="right">
                  <template #default="{ row }">{{ formatNumber(row.original_weight) }}</template>
                </el-table-column>
                <el-table-column prop="adjusted_weight" label="调整后权重" width="110" align="right">
                  <template #default="{ row }">{{ formatNumber(row.adjusted_weight) }}</template>
                </el-table-column>
                <el-table-column prop="is_adjusted" label="是否调整" width="90" align="center">
                  <template #default="{ row }">
                    <el-tag :type="row.is_adjusted ? 'success' : 'info'" size="small">
                      {{ row.is_adjusted ? '是' : '否' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="adjustment_reason" label="未调整原因" min-width="150" show-overflow-tooltip />
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>

    <!-- 维度下钻对话框 -->
    <el-dialog
      v-model="drillDownVisible"
      :title="`${drillDownData?.dimension_name || '维度'} - 收费项目明细`"
      width="1000px"
      append-to-body
      destroy-on-close
      @open="resetDrillDownPagination"
    >
      <div v-loading="drillDownLoading" class="drilldown-content">
        <el-table
          :data="paginatedDrillDownItems"
          border
          stripe
          size="small"
        >
          <el-table-column prop="period" label="年月" width="80" />
          <el-table-column prop="department_code" label="科室代码" width="80" />
          <el-table-column prop="department_name" label="科室名称" width="120" />
          <el-table-column prop="item_code" label="项目编码" width="100" />
          <el-table-column prop="item_name" label="项目名称" min-width="160" />
          <el-table-column prop="item_category" label="项目类别" width="80">
            <template #default="{ row }">
              {{ row.item_category || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="unit_price" label="单价" width="70" align="right">
            <template #default="{ row }">
              {{ row.unit_price || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="amount" label="金额" width="100" align="right">
            <template #default="{ row }">
              {{ formatNumber(row.amount) }}
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="80" align="right">
            <template #default="{ row }">
              {{ formatNumber(row.quantity) }}
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <div v-if="drillDownData && drillDownData.items.length > 0" class="pagination-wrapper">
          <el-pagination
            v-model:current-page="drillDownCurrentPage"
            v-model:page-size="drillDownPageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="drillDownData.items.length"
            layout="total, sizes, prev, pager, next"
            small
          />
        </div>
        
        <!-- 汇总信息 -->
        <div v-if="drillDownData && drillDownData.items.length > 0" class="summary-info">
          <span>总金额: <strong>{{ formatNumber(drillDownData.total_amount) }}</strong></span>
          <span style="margin-left: 30px;">共 <strong>{{ drillDownData.items.length }}</strong> 条记录</span>
        </div>
        
        <div v-if="drillDownData?.message" class="data-message">
          {{ drillDownData.message }}
        </div>
        
        <el-empty v-if="!drillDownLoading && (!drillDownData?.items || drillDownData.items.length === 0)" description="暂无数据" />
      </div>

      <template #footer>
        <el-button @click="drillDownVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'
import { getModelVersions } from '@/api/model'
import { getSystemSettings } from '@/api/system-settings'
import { getReferenceValuesByPeriod } from '@/api/reference-values'
import { getDimensionDrillDownByTask, type DimensionDrillDownResponse } from '@/api/analysis-reports'
import request from '@/utils/request'

const route = useRoute()

// 任务选项接口
interface TaskOption {
  task_id: string
  label: string
  period: string
  model_version_id: number
  created_at: string
  completed_at: string
}

// 数据
const loading = ref(false)
const exporting = ref(false)
const versions = ref<any[]>([])
const summaryData = ref<any[]>([])
const detailData = ref<any>(null)
const orientationData = ref<any>(null)
const currentDepartment = ref<any>(null)
const detailDialogVisible = ref(false)
const activeTab = ref('doctor')
const orientationActiveTab = ref('doctor')

// 下钻相关
const drillDownVisible = ref(false)
const drillDownLoading = ref(false)
const drillDownData = ref<DimensionDrillDownResponse | null>(null)
const drillDownCurrentPage = ref(1)
const drillDownPageSize = ref(10)

// 参考价值数据
const referenceValues = ref<Record<string, any>>({})

// 任务选择器相关
const selectedTaskId = ref<string | null>(null)
const availableTasks = ref<TaskOption[]>([])
const loadingTasks = ref(false)

const filterForm = reactive({
  period: route.query.period as string || '',
  model_version_id: route.query.model_version_id ? Number(route.query.model_version_id) : null
})

// 方法
const loadVersions = async () => {
  try {
    const response: any = await getModelVersions({ skip: 0, limit: 1000 })
    versions.value = response.items || []
    
    // 如果URL参数中没有指定版本，则默认选中激活的版本
    if (!filterForm.model_version_id) {
      const activeVersion = versions.value.find((v: any) => v.is_active)
      if (activeVersion) {
        filterForm.model_version_id = activeVersion.id
      }
    }
  } catch (error: any) {
    ElMessage.error('加载模型版本失败')
    console.error('加载模型版本错误:', error)
  }
}

// 加载可选任务列表
const loadAvailableTasks = async () => {
  if (!filterForm.period) {
    availableTasks.value = []
    return
  }

  loadingTasks.value = true
  try {
    const response: any = await request({
      url: '/calculation/tasks',
      method: 'get',
      params: {
        period: filterForm.period,
        model_version_id: filterForm.model_version_id,
        status: 'completed',
        page: 1,
        size: 100
      }
    })
    
    // 格式化任务选项，在标签中显示计算流程名称
    availableTasks.value = (response.items || []).map((task: any) => {
      const taskIdShort = task.task_id.substring(0, 8)
      const createdTime = new Date(task.created_at).toLocaleString('zh-CN')
      const workflowName = task.workflow_name || '默认流程'
      
      return {
        task_id: task.task_id,
        label: `${taskIdShort}... (${workflowName} - ${createdTime})`,
        period: task.period,
        model_version_id: task.model_version_id,
        workflow_name: task.workflow_name,
        created_at: task.created_at,
        completed_at: task.completed_at
      }
    })
    
    // 自动选择最新的任务（第一个任务，因为后端已按创建时间倒序排序）
    if (availableTasks.value.length > 0 && !selectedTaskId.value) {
      selectedTaskId.value = availableTasks.value[0].task_id
    }
  } catch (error: any) {
    ElMessage.error('加载任务列表失败')
    console.error('加载任务列表错误:', error)
  } finally {
    loadingTasks.value = false
  }
}

const loadSummary = async () => {
  if (!filterForm.period && !selectedTaskId.value) {
    ElMessage.warning('请选择评估月份或任务')
    return
  }

  loading.value = true
  try {
    const params: any = {}
    
    // task_id优先于period+model_version_id
    if (selectedTaskId.value) {
      params.task_id = selectedTaskId.value
    } else {
      params.period = filterForm.period
      params.model_version_id = filterForm.model_version_id
    }
    
    const response: any = await request({
      url: '/calculation/results/summary',
      method: 'get',
      params
    })
    
    summaryData.value = [response.summary, ...response.departments]
    
    // 加载参考价值数据
    await loadReferenceValues()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载汇总数据失败')
  } finally {
    loading.value = false
  }
}

// 加载参考价值数据
const loadReferenceValues = async () => {
  if (!filterForm.period) {
    referenceValues.value = {}
    return
  }
  
  try {
    const res: any = await getReferenceValuesByPeriod(filterForm.period)
    referenceValues.value = res || {}
  } catch (error) {
    // 参考价值可能不存在，不显示错误
    referenceValues.value = {}
  }
}

// 处理任务选择变化
const onTaskChange = (taskId: string | null) => {
  selectedTaskId.value = taskId
  if (taskId) {
    loadSummary()
  }
}

// 处理评估月份变化
const onPeriodChange = () => {
  selectedTaskId.value = null
  availableTasks.value = []
  if (filterForm.period) {
    loadAvailableTasks()
    loadSummary()
  }
}

// 处理模型版本变化
const onVersionChange = () => {
  selectedTaskId.value = null
  availableTasks.value = []
  if (filterForm.period) {
    loadAvailableTasks()
    loadSummary()
  }
}

const viewDetail = async (row: any) => {
  currentDepartment.value = row
  
  // 使用选中的任务ID
  const taskId = selectedTaskId.value
  if (!taskId) {
    ElMessage.error('缺少任务ID，无法查看明细')
    return
  }
  
  try {
    let response: any
    
    // 判断是全院汇总还是单科室
    if (row.department_id === 0) {
      // 全院汇总明细
      response = await request({
        url: '/calculation/results/hospital-detail',
        method: 'get',
        params: {
          task_id: taskId
        }
      })
    } else {
      // 单科室明细
      response = await request({
        url: '/calculation/results/detail',
        method: 'get',
        params: {
          dept_id: row.department_id,
          task_id: taskId
        }
      })
    }
    
    detailData.value = response
    
    // 加载导向汇总数据
    await loadOrientationSummary(taskId, row.department_id)
    
    // 自动选择有数据的Tab：优先医生 -> 护理 -> 医技
    if (detailData.value.doctor && detailData.value.doctor.length > 0) {
      activeTab.value = 'doctor'
    } else if (detailData.value.nurse && detailData.value.nurse.length > 0) {
      activeTab.value = 'nurse'
    } else if (detailData.value.tech && detailData.value.tech.length > 0) {
      activeTab.value = 'tech'
    } else {
      // 如果都没有数据，默认显示导向汇总
      activeTab.value = 'orientation'
    }
    
    detailDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载明细数据失败')
  }
}

// 加载导向汇总数据
const loadOrientationSummary = async (taskId: string, deptId: number) => {
  try {
    const params: any = { task_id: taskId }
    if (deptId !== 0) {
      params.dept_id = deptId
    }
    
    const response: any = await request({
      url: '/calculation/results/orientation-summary',
      method: 'get',
      params
    })
    
    orientationData.value = response
  } catch (error: any) {
    console.error('加载导向汇总数据失败:', error)
    // 不显示错误消息，因为可能没有导向数据
    orientationData.value = { doctor: [], nurse: [], tech: [] }
  }
}

// 格式化值或显示"-"
const formatValueOrDash = (value: any) => {
  if (value === '-' || value === null || value === undefined) return '-'
  return formatNumber(value)
}

// 护理序列中用charge_details计算的维度编码前缀（可下钻）
const nurseChargeDimPrefixes = ['dim-nur-base', 'dim-nur-collab', 'dim-nur-tr-', 'dim-nur-other']
// 护理序列中用workload_statistics计算的维度编码前缀（不可下钻）
const nurseWorkloadDimPrefixes = ['dim-nur-bed', 'dim-nur-trans', 'dim-nur-op', 'dim-nur-or', 'dim-nur-mon']

// 判断护理维度是否可下钻
const isNurseChargeDim = (code: string | undefined) => {
  if (!code) return false
  // 排除用workload_statistics计算的维度
  if (nurseWorkloadDimPrefixes.some(prefix => code.startsWith(prefix))) return false
  // 检查是否为用charge_details计算的维度
  return nurseChargeDimPrefixes.some(prefix => code.startsWith(prefix))
}

// 判断是否可以下钻
const canDrillDown = (row: any, sequenceType: string) => {
  // 必须有 node_id 或 id（兼容两种字段名）
  const nodeId = row.node_id || row.id
  if (!nodeId) return false
  
  // 必须是叶子节点（没有 children 或 children 为空）
  if (row.children && row.children.length > 0) return false
  
  // 医生序列：排除病例价值维度
  if (sequenceType === 'doctor') {
    if (row.dimension_code === 'dim-doc-case' || row.dimension_name === '病例价值') return false
    return true
  }
  
  // 医技序列：所有末级维度都可下钻
  if (sequenceType === 'tech') {
    return true
  }
  
  // 护理序列：只有用charge_details计算的维度可下钻
  if (sequenceType === 'nurse') {
    return isNurseChargeDim(row.dimension_code)
  }
  
  return false
}

// 处理下钻
const handleDrillDown = async (row: any) => {
  if (!selectedTaskId.value || !currentDepartment.value) {
    ElMessage.warning('缺少任务ID或科室信息')
    return
  }
  
  // 兼容两种字段名
  const nodeId = row.node_id || row.id
  if (!nodeId) {
    ElMessage.warning('缺少节点ID')
    return
  }
  
  drillDownVisible.value = true
  drillDownLoading.value = true
  drillDownData.value = null
  
  try {
    const res = await getDimensionDrillDownByTask(
      selectedTaskId.value,
      currentDepartment.value.department_id,
      nodeId
    )
    drillDownData.value = res as DimensionDrillDownResponse
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载下钻数据失败')
    drillDownVisible.value = false
  } finally {
    drillDownLoading.value = false
  }
}

// 下钻分页数据
const paginatedDrillDownItems = computed(() => {
  if (!drillDownData.value?.items) return []
  const start = (drillDownCurrentPage.value - 1) * drillDownPageSize.value
  const end = start + drillDownPageSize.value
  return drillDownData.value.items.slice(start, end)
})

// 重置下钻分页
const resetDrillDownPagination = () => {
  drillDownCurrentPage.value = 1
}

const exportSummary = async () => {
  if (!filterForm.period) {
    ElMessage.warning('请选择评估月份')
    return
  }

  exporting.value = true
  try {
    const response = await request({
      url: '/calculation/results/export/summary',
      method: 'get',
      params: {
        period: filterForm.period,
        model_version_id: filterForm.model_version_id
      },
      responseType: 'blob'
    })
    
    // 从响应头获取文件名
    let filename = `科室业务价值汇总_${filterForm.period}.xlsx`
    const contentDisposition = response.headers?.['content-disposition']
    if (contentDisposition && contentDisposition.includes("filename*=UTF-8''")) {
      const filenameMatch = contentDisposition.split("filename*=UTF-8''")[1]
      if (filenameMatch) {
        filename = decodeURIComponent(filenameMatch)
      }
    }
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data || response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '导出失败')
  } finally {
    exporting.value = false
  }
}

const exportDetail = async () => {
  const taskId = selectedTaskId.value
  if (!taskId) {
    ElMessage.warning('缺少任务ID，无法导出明细')
    return
  }

  exporting.value = true
  try {
    const response = await request({
      url: '/calculation/results/export/detail',
      method: 'get',
      params: {
        task_id: taskId
      },
      responseType: 'blob'
    })
    
    // 从响应头获取文件名
    const taskIdShort = taskId.substring(0, 8)
    let filename = `业务价值明细表_${filterForm.period}_${taskIdShort}.zip`
    const contentDisposition = response.headers?.['content-disposition']
    if (contentDisposition && contentDisposition.includes("filename*=UTF-8''")) {
      const filenameMatch = contentDisposition.split("filename*=UTF-8''")[1]
      if (filenameMatch) {
        filename = decodeURIComponent(filenameMatch)
      }
    }
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data || response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '导出失败')
  } finally {
    exporting.value = false
  }
}

const formatNumber = (value: any) => {
  if (value === null || value === undefined) return '-'
  return Number(value).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

const formatPercent = (value: any) => {
  if (value === null || value === undefined) return '-'
  return `${Number(value).toFixed(2)}%`
}

// 格式化参考价值
const formatReferenceValue = (row: any) => {
  // 全院汇总行
  if (row.department_id === 0) {
    // 计算所有科室参考价值的总和
    let total = 0
    let hasData = false
    for (const deptCode in referenceValues.value) {
      const refVal = referenceValues.value[deptCode]?.reference_value
      if (refVal !== null && refVal !== undefined) {
        total += Number(refVal)
        hasData = true
      }
    }
    return hasData ? formatNumber(total) : '-'
  }
  
  // 单个科室
  const refData = referenceValues.value[row.department_code]
  if (!refData || refData.reference_value === null || refData.reference_value === undefined) {
    return '-'
  }
  return formatNumber(refData.reference_value)
}

// 格式化实际参考比
const formatActualReferenceRatio = (row: any) => {
  // 全院汇总行
  if (row.department_id === 0) {
    // 计算全院的实际参考比
    let totalRef = 0
    let hasData = false
    for (const deptCode in referenceValues.value) {
      const refVal = referenceValues.value[deptCode]?.reference_value
      if (refVal !== null && refVal !== undefined) {
        totalRef += Number(refVal)
        hasData = true
      }
    }
    if (!hasData || totalRef === 0) return '-'
    const totalValue = Number(row.total_value) || 0
    const ratio = totalValue / totalRef
    return `${(ratio * 100).toFixed(2)}%`
  }
  
  // 单个科室
  const refData = referenceValues.value[row.department_code]
  if (!refData || refData.reference_value === null || refData.reference_value === undefined) {
    return '-'
  }
  
  const refValue = Number(refData.reference_value)
  if (refValue === 0) return '-'
  
  const totalValue = Number(row.total_value) || 0
  const ratio = totalValue / refValue
  return `${(ratio * 100).toFixed(2)}%`
}

// 从URL参数初始化
const initFromUrlParams = async () => {
  const taskIdFromUrl = route.query.task_id as string
  
  if (taskIdFromUrl) {
    try {
      // 根据task_id加载任务详情
      const task: any = await request({
        url: `/calculation/tasks/${taskIdFromUrl}`,
        method: 'get'
      })
      
      // 设置筛选条件
      filterForm.period = task.period
      filterForm.model_version_id = task.model_version_id
      selectedTaskId.value = taskIdFromUrl
      
      // 加载任务列表和汇总数据
      await loadAvailableTasks()
      await loadSummary()
    } catch (error: any) {
      ElMessage.error('加载任务失败，使用默认筛选条件')
      console.error('加载任务错误:', error)
      // 清除无效的task_id参数
      selectedTaskId.value = null
    }
  }
}

// 生命周期
onMounted(async () => {
  await loadVersions()
  
  // 检查是否有task_id参数
  if (route.query.task_id) {
    await initFromUrlParams()
  } else {
    // 如果 URL 没有传入 period，则从系统设置获取当期年月
    if (!filterForm.period) {
      try {
        const settings = await getSystemSettings()
        if (settings.current_period) {
          filterForm.period = settings.current_period
        }
      } catch (error) {
        console.error('获取系统设置失败:', error)
      }
    }
    
    if (filterForm.period) {
      await loadAvailableTasks()
      await loadSummary()
    }
  }
})
</script>

<style scoped>
.results-container {
  padding: 0;
  width: 100%;
  height: 100%;
}

.results-container :deep(.el-card) {
  width: 100%;
  height: 100%;
}

.results-container :deep(.el-card__body) {
  height: calc(100% - 60px);
  display: flex;
  flex-direction: column;
  overflow: auto;
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

.filter-section {
  flex-shrink: 0;
  margin-bottom: 20px;
}

.table-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.table-section h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 500;
  flex-shrink: 0;
}

.table-section :deep(.el-table) {
  flex: 1;
}

.detail-dialog :deep(.el-dialog__body) {
  max-height: 75vh;
  overflow-y: auto;
}

.table-title {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 15px;
  text-align: center;
  color: #303133;
}

.structure-table {
  font-size: 13px;
}

.structure-table :deep(.el-table__cell) {
  padding: 8px 0;
}

.structure-table :deep(.cell) {
  padding: 0 8px;
  line-height: 1.5;
}

.dimension-name {
  font-weight: 600;
}

.ratio-text {
  font-size: 13px;
  margin-left: 4px;
}

.drilldown-content {
  min-height: 200px;
}

.pagination-wrapper {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.summary-info {
  margin-top: 16px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-size: 14px;
}

.summary-info strong {
  color: #409eff;
  font-size: 16px;
}

.data-message {
  margin-top: 8px;
  color: #909399;
  font-size: 13px;
}
</style>
