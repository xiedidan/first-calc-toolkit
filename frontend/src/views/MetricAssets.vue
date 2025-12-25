<template>
  <div class="metric-assets-container">
    <!-- 左侧：指标树 -->
    <div class="tree-panel">
      <el-card class="tree-card">
        <template #header>
          <div class="card-header">
            <span>指标树</span>
            <el-button type="primary" size="small" @click="handleAddProject">
              <el-icon><Plus /></el-icon>
              新建项目
            </el-button>
          </div>
        </template>
        
        <div class="tree-toolbar">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索指标..."
            clearable
            size="small"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
        
        <div class="tree-content" v-loading="treeLoading">
          <el-tree
            ref="treeRef"
            :data="treeData"
            :props="treeProps"
            node-key="nodeKey"
            :expand-on-click-node="false"
            :default-expand-all="true"
            :filter-node-method="filterNode"
            highlight-current
            draggable
            :allow-drop="allowDrop"
            @node-click="handleNodeClick"
            @node-drop="handleNodeDrop"
          >
            <template #default="{ node, data }">
              <div class="tree-node">
                <span class="node-label">
                  <el-icon v-if="data.node_type === 'project'" class="node-icon project-icon"><Folder /></el-icon>
                  <el-icon v-else-if="data.node_type === 'topic'" class="node-icon topic-icon"><FolderOpened /></el-icon>
                  <el-icon v-else class="node-icon metric-icon"><DataLine /></el-icon>
                  {{ data.name }}
                  <el-tag v-if="data.node_type === 'metric' && data.metric_type_display" size="small" type="info" style="margin-left: 4px">
                    {{ data.metric_type_display }}
                  </el-tag>
                </span>
                <span class="node-actions" @click.stop>
                  <el-dropdown trigger="click" @command="(cmd: string) => handleNodeCommand(cmd, data, node)">
                    <el-icon class="more-icon"><MoreFilled /></el-icon>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item v-if="data.node_type === 'project'" command="addTopic">
                          <el-icon><Plus /></el-icon>添加主题
                        </el-dropdown-item>
                        <el-dropdown-item v-if="data.node_type === 'topic'" command="addMetric">
                          <el-icon><Plus /></el-icon>添加指标
                        </el-dropdown-item>
                        <el-dropdown-item command="edit">
                          <el-icon><Edit /></el-icon>编辑
                        </el-dropdown-item>
                        <el-dropdown-item command="moveUp" :disabled="!canMoveUp(node)">
                          <el-icon><Top /></el-icon>上移
                        </el-dropdown-item>
                        <el-dropdown-item command="moveDown" :disabled="!canMoveDown(node)">
                          <el-icon><Bottom /></el-icon>下移
                        </el-dropdown-item>
                        <el-dropdown-item command="delete" divided>
                          <el-icon><Delete /></el-icon>删除
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </span>
              </div>
            </template>
          </el-tree>
          
          <el-empty v-if="!treeLoading && treeData.length === 0" description="暂无指标数据" />
        </div>
        
        <div class="tree-footer">
          <span>项目: {{ treeStats.total_projects }}</span>
          <span>主题: {{ treeStats.total_topics }}</span>
          <span>指标: {{ treeStats.total_metrics }}</span>
        </div>
      </el-card>
    </div>

    <!-- 右侧：详情面板 -->
    <div class="detail-panel">
      <el-card class="detail-card" v-loading="detailLoading">
        <template #header>
          <div class="card-header">
            <span>{{ detailTitle }}</span>
            <div v-if="selectedNode && selectedNode.node_type === 'metric'">
              <el-button type="primary" size="small" @click="handleEdit">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
            </div>
          </div>
        </template>
        
        <!-- 未选择节点 -->
        <el-empty v-if="!selectedNode" description="请从左侧选择一个节点查看详情" />
        
        <!-- 项目详情 -->
        <div v-else-if="selectedNode.node_type === 'project'" class="detail-content">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="项目名称">
              <el-input v-if="isEditing" v-model="editForm.name" placeholder="请输入项目名称" />
              <span v-else>{{ selectedProject?.name }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="项目描述">
              <el-input v-if="isEditing" v-model="editForm.description" type="textarea" :rows="3" placeholder="请输入项目描述" />
              <span v-else>{{ selectedProject?.description || '-' }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="主题数量">{{ selectedProject?.topic_count || 0 }}</el-descriptions-item>
            <el-descriptions-item label="指标数量">{{ selectedProject?.metric_count || 0 }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ selectedProject?.created_at }}</el-descriptions-item>
          </el-descriptions>
        </div>
        
        <!-- 主题详情 -->
        <div v-else-if="selectedNode.node_type === 'topic'" class="detail-content">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="主题名称">
              <el-input v-if="isEditing" v-model="editForm.name" placeholder="请输入主题名称" />
              <span v-else>{{ selectedTopic?.name }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="所属项目">{{ selectedTopic?.project_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="主题描述">
              <el-input v-if="isEditing" v-model="editForm.description" type="textarea" :rows="3" placeholder="请输入主题描述" />
              <span v-else>{{ selectedTopic?.description || '-' }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="指标数量">{{ selectedTopic?.metric_count || 0 }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ selectedTopic?.created_at }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 指标详情 -->
        <div v-else-if="selectedNode.node_type === 'metric'" class="detail-content">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="业务属性" name="business">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="所属项目">{{ selectedMetric?.project_name || '-' }}</el-descriptions-item>
                <el-descriptions-item label="所属主题">{{ selectedMetric?.topic_name || '-' }}</el-descriptions-item>
                <el-descriptions-item label="业务口径">
                  <div class="caliber-text">{{ selectedMetric?.business_caliber || '-' }}</div>
                </el-descriptions-item>
              </el-descriptions>
            </el-tab-pane>
            
            <el-tab-pane label="技术属性" name="technical">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="中文名称">{{ selectedMetric?.name_cn || '-' }}</el-descriptions-item>
                <el-descriptions-item label="英文名称">{{ selectedMetric?.name_en || '-' }}</el-descriptions-item>
                <el-descriptions-item label="指标类型">
                  <el-tag v-if="selectedMetric?.metric_type_display" size="small">{{ selectedMetric.metric_type_display }}</el-tag>
                  <span v-else>-</span>
                </el-descriptions-item>
                <el-descriptions-item label="指标层级">{{ selectedMetric?.metric_level || '-' }}</el-descriptions-item>
                <el-descriptions-item label="技术口径" :span="2">
                  <div class="caliber-text">{{ selectedMetric?.technical_caliber || '-' }}</div>
                </el-descriptions-item>
                <el-descriptions-item label="指标源表" :span="2">
                  <el-tag v-for="table in (selectedMetric?.source_tables || [])" :key="table" size="small" type="warning" style="margin-right: 4px; margin-bottom: 4px;">{{ table }}</el-tag>
                  <span v-if="!selectedMetric?.source_tables?.length">-</span>
                </el-descriptions-item>
                <el-descriptions-item label="关联维表" :span="2">
                  <el-tag v-for="table in (selectedMetric?.dimension_tables || [])" :key="table" size="small" style="margin-right: 4px; margin-bottom: 4px;">{{ table }}</el-tag>
                  <span v-if="!selectedMetric?.dimension_tables?.length">-</span>
                </el-descriptions-item>
                <el-descriptions-item label="指标维度" :span="2">
                  <el-tag v-for="dim in (selectedMetric?.dimensions || [])" :key="dim" size="small" type="success" style="margin-right: 4px; margin-bottom: 4px;">{{ dim }}</el-tag>
                  <span v-if="!selectedMetric?.dimensions?.length">-</span>
                </el-descriptions-item>
                <el-descriptions-item label="数据源" :span="2">{{ selectedMetric?.data_source_name || '-' }}</el-descriptions-item>
              </el-descriptions>
            </el-tab-pane>

            <el-tab-pane label="关联指标" name="relations">
              <MetricRelationManager
                ref="relationManagerRef"
                :metric-id="selectedMetric?.id || null"
                :metric-name="selectedMetric?.name_cn"
                @updated="handleRelationUpdated"
                @deleted="handleMetricDeleted"
              />
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-card>
    </div>
    
    <!-- 新建/编辑项目对话框 -->
    <el-dialog v-model="projectDialogVisible" :title="projectDialogTitle" width="500px" append-to-body>
      <el-form :model="projectForm" label-width="80px">
        <el-form-item label="项目名称" required>
          <el-input v-model="projectForm.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input v-model="projectForm.description" type="textarea" :rows="3" placeholder="请输入项目描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="projectDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveProject" :loading="saving">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 新建/编辑主题对话框 -->
    <el-dialog v-model="topicDialogVisible" :title="topicDialogTitle" width="500px" append-to-body>
      <el-form :model="topicForm" label-width="80px">
        <el-form-item label="所属项目">
          <el-select v-model="topicForm.project_id" placeholder="请选择项目" style="width: 100%" disabled>
            <el-option v-for="p in allProjects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="主题名称" required>
          <el-input v-model="topicForm.name" placeholder="请输入主题名称" />
        </el-form-item>
        <el-form-item label="主题描述">
          <el-input v-model="topicForm.description" type="textarea" :rows="3" placeholder="请输入主题描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="topicDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveTopic" :loading="saving">确定</el-button>
      </template>
    </el-dialog>

    <!-- 新建指标对话框 -->
    <el-dialog v-model="metricDialogVisible" title="新建指标" width="600px" append-to-body>
      <el-form :model="metricForm" label-width="100px">
        <el-form-item label="所属主题">
          <el-select v-model="metricForm.topic_id" placeholder="请选择主题" style="width: 100%" disabled>
            <el-option v-for="t in allTopics" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="中文名称" required>
          <el-input v-model="metricForm.name_cn" placeholder="请输入中文名称" />
        </el-form-item>
        <el-form-item label="英文名称">
          <el-input v-model="metricForm.name_en" placeholder="请输入英文名称" />
        </el-form-item>
        <el-form-item label="指标类型">
          <el-select v-model="metricForm.metric_type" placeholder="请选择指标类型" style="width: 100%">
            <el-option label="原子指标" value="atomic" />
            <el-option label="复合指标" value="composite" />
          </el-select>
        </el-form-item>
        <el-form-item label="业务口径">
          <el-input v-model="metricForm.business_caliber" type="textarea" :rows="3" placeholder="请输入业务口径" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="metricDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveMetric" :loading="saving">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 添加关联对话框 -->
    <el-dialog v-model="relationDialogVisible" title="添加关联指标" width="500px" append-to-body>
      <el-form :model="relationForm" label-width="80px">
        <el-form-item label="关联指标" required>
          <el-select v-model="relationForm.target_metric_id" placeholder="请选择关联指标" filterable style="width: 100%">
            <el-option 
              v-for="m in availableMetrics" 
              :key="m.id" 
              :label="`${m.name_cn} (${m.topic_name || '未分类'})`" 
              :value="m.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关联类型">
          <el-select v-model="relationForm.relation_type" placeholder="请选择关联类型" style="width: 100%">
            <el-option label="组成" value="component" />
            <el-option label="派生" value="derived" />
            <el-option label="相关" value="related" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="relationDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveRelation" :loading="saving">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 指标编辑对话框 -->
    <MetricEditDialog
      v-model="metricEditDialogVisible"
      :metric-id="editingMetricId"
      @saved="handleMetricEditSaved"
    />
  </div>
</template>


<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { ElTree } from 'element-plus'
import { Plus, Search, Edit, Delete, MoreFilled, Folder, FolderOpened, DataLine, Top, Bottom } from '@element-plus/icons-vue'
import { 
  getMetricTree, getMetric, createMetric, updateMetric, deleteMetric,
  getMetricRelations, createMetricRelation, deleteMetricRelation, getAffectedMetrics, getMetrics,
  reorderMetrics,
  type MetricTreeNode, type Metric, type MetricRelation, type MetricRelationListResponse
} from '@/api/metrics'
import { getMetricProjects, createMetricProject, updateMetricProject, deleteMetricProject, reorderMetricProjects, type MetricProject } from '@/api/metric-projects'
import { getMetricTopics, createMetricTopic, updateMetricTopic, deleteMetricTopic, reorderMetricTopics, type MetricTopic } from '@/api/metric-topics'
import request from '@/utils/request'
import MetricEditDialog from '@/components/MetricEditDialog.vue'
import MetricRelationManager from '@/components/MetricRelationManager.vue'

// 树形数据
const treeRef = ref<InstanceType<typeof ElTree>>()
const treeData = ref<MetricTreeNode[]>([])
const treeLoading = ref(false)
const searchKeyword = ref('')
const treeStats = reactive({
  total_projects: 0,
  total_topics: 0,
  total_metrics: 0
})

// 树节点配置
const treeProps = {
  children: 'children',
  label: 'name'
}

// 选中节点
const selectedNode = ref<MetricTreeNode | null>(null)
const selectedProject = ref<MetricProject | null>(null)
const selectedTopic = ref<MetricTopic | null>(null)
const selectedMetric = ref<Metric | null>(null)
const detailLoading = ref(false)

// 编辑状态
const isEditing = ref(false)
const saving = ref(false)
const activeTab = ref('business')
const editForm = reactive<any>({})

// 所有项目和主题（用于下拉选择）
const allProjects = ref<MetricProject[]>([])
const allTopics = ref<MetricTopic[]>([])
const dataSources = ref<any[]>([])

// 指标关联
const metricRelations = ref<MetricRelation[]>([])
const relationsLoading = ref(false)
const relationStats = ref<{ as_source_count: number; as_target_count: number } | null>(null)

// 对话框状态
const projectDialogVisible = ref(false)
const projectDialogTitle = ref('新建项目')
const projectForm = reactive({ id: 0, name: '', description: '' })

const topicDialogVisible = ref(false)
const topicDialogTitle = ref('新建主题')
const topicForm = reactive({ id: 0, project_id: 0, name: '', description: '' })

const metricDialogVisible = ref(false)
const metricForm = reactive({ topic_id: 0, name_cn: '', name_en: '', metric_type: 'atomic', business_caliber: '' })

const relationDialogVisible = ref(false)
const relationForm = reactive({ target_metric_id: 0, relation_type: 'related' })
const availableMetrics = ref<Metric[]>([])

// 指标编辑对话框状态
const metricEditDialogVisible = ref(false)
const editingMetricId = ref<number | null>(null)

// 关联管理组件引用
const relationManagerRef = ref<InstanceType<typeof MetricRelationManager> | null>(null)

// 计算属性
const detailTitle = computed(() => {
  if (!selectedNode.value) return '详情'
  switch (selectedNode.value.node_type) {
    case 'project': return '项目详情'
    case 'topic': return '主题详情'
    case 'metric': return '指标详情'
    default: return '详情'
  }
})

// 加载指标树
const loadTree = async () => {
  treeLoading.value = true
  try {
    const res = await getMetricTree()
    // 为每个节点添加唯一key
    const addNodeKey = (nodes: MetricTreeNode[], parentKey = ''): MetricTreeNode[] => {
      return nodes.map((node, index) => ({
        ...node,
        nodeKey: `${node.node_type}-${node.id}`,
        children: node.children ? addNodeKey(node.children, `${node.node_type}-${node.id}`) : undefined
      }))
    }
    treeData.value = addNodeKey(res.items)
    treeStats.total_projects = res.total_projects
    treeStats.total_topics = res.total_topics
    treeStats.total_metrics = res.total_metrics
  } catch (error) {
    ElMessage.error('加载指标树失败')
  } finally {
    treeLoading.value = false
  }
}

// 加载项目列表
const loadProjects = async () => {
  try {
    const res = await getMetricProjects()
    allProjects.value = res.items
  } catch (error) {
    console.error('加载项目列表失败', error)
  }
}

// 加载主题列表
const loadTopics = async () => {
  try {
    const res = await getMetricTopics()
    allTopics.value = res.items
  } catch (error) {
    console.error('加载主题列表失败', error)
  }
}

// 加载数据源列表
const loadDataSources = async () => {
  try {
    const res = await request.get('/data-sources')
    dataSources.value = res.items || []
  } catch (error) {
    console.error('加载数据源列表失败', error)
  }
}

// 搜索过滤
const filterNode = (value: string, data: MetricTreeNode) => {
  if (!value) return true
  return data.name.toLowerCase().includes(value.toLowerCase())
}

const handleSearch = () => {
  treeRef.value?.filter(searchKeyword.value)
}

watch(searchKeyword, (val) => {
  treeRef.value?.filter(val)
})

// 节点点击
const handleNodeClick = async (data: MetricTreeNode) => {
  selectedNode.value = data
  isEditing.value = false
  detailLoading.value = true
  
  try {
    if (data.node_type === 'project') {
      const res = await request.get(`/metric-projects/${data.id}`)
      selectedProject.value = res
      selectedTopic.value = null
      selectedMetric.value = null
    } else if (data.node_type === 'topic') {
      const res = await request.get(`/metric-topics/${data.id}`)
      selectedTopic.value = res
      selectedProject.value = null
      selectedMetric.value = null
    } else if (data.node_type === 'metric') {
      const res = await getMetric(data.id)
      selectedMetric.value = res
      selectedProject.value = null
      selectedTopic.value = null
      // 加载关联指标
      await loadMetricRelations(data.id)
    }
  } catch (error) {
    ElMessage.error('加载详情失败')
  } finally {
    detailLoading.value = false
  }
}

// 加载指标关联
const loadMetricRelations = async (metricId: number) => {
  relationsLoading.value = true
  try {
    const res = await getMetricRelations(metricId)
    metricRelations.value = res.items
    relationStats.value = {
      as_source_count: res.as_source_count,
      as_target_count: res.as_target_count
    }
  } catch (error) {
    console.error('加载关联指标失败', error)
  } finally {
    relationsLoading.value = false
  }
}

// 节点拖拽排序 - 判断是否允许放置
const allowDrop = (draggingNode: any, dropNode: any, type: string): boolean => {
  const dragData = draggingNode.data as MetricTreeNode
  const dropData = dropNode.data as MetricTreeNode
  
  // 项目：只能在项目之间排序（before/after），不能放入其他节点内部
  if (dragData.node_type === 'project') {
    // 项目只能放在其他项目的前后
    if (dropData.node_type !== 'project') return false
    // 不允许放入项目内部
    if (type === 'inner') return false
    return true
  }
  
  // 主题：可以在项目间移动，但不能放到主题下面或没有项目
  if (dragData.node_type === 'topic') {
    if (type === 'inner') {
      // 只能放入项目内部
      return dropData.node_type === 'project'
    } else {
      // before/after 只能放在其他主题旁边（同一项目或不同项目都可以）
      return dropData.node_type === 'topic'
    }
  }
  
  // 指标：可以在主题间移动，但不能放到项目下面或没有主题
  if (dragData.node_type === 'metric') {
    if (type === 'inner') {
      // 只能放入主题内部
      return dropData.node_type === 'topic'
    } else {
      // before/after 只能放在其他指标旁边（同一主题或不同主题都可以）
      return dropData.node_type === 'metric'
    }
  }
  
  return false
}

// 节点拖拽排序
const handleNodeDrop = async (draggingNode: any, dropNode: any, dropType: string) => {
  const dragData = draggingNode.data as MetricTreeNode
  const dropData = dropNode.data as MetricTreeNode
  
  try {
    if (dragData.node_type === 'project') {
      // 项目排序：获取所有项目的新顺序
      const parent = dropNode.parent
      const siblings = parent?.childNodes || []
      const siblingIds = siblings.map((n: any) => n.data.id)
      await reorderMetricProjects(siblingIds)
      ElMessage.success('排序已更新')
    } else if (dragData.node_type === 'topic') {
      // 主题移动或排序
      if (dropType === 'inner') {
        // 移动到项目内部（放到该项目的最后）
        const newProjectId = dropData.id
        await updateMetricTopic(dragData.id, { project_id: newProjectId })
        ElMessage.success('主题已移动')
        await loadTree()
      } else {
        // 放在其他主题旁边
        const targetProjectId = dropData.project_id
        const sourceProjectId = dragData.project_id
        
        if (targetProjectId !== sourceProjectId) {
          // 跨项目移动：先更新主题的项目ID
          await updateMetricTopic(dragData.id, { project_id: targetProjectId })
        }
        
        // 获取目标项目下所有主题的新顺序
        const parent = dropNode.parent
        const siblings = parent?.childNodes || []
        const siblingIds = siblings.map((n: any) => n.data.id)
        await reorderMetricTopics(siblingIds)
        
        ElMessage.success(targetProjectId !== sourceProjectId ? '主题已移动并排序' : '排序已更新')
        if (targetProjectId !== sourceProjectId) {
          await loadTree()
        }
      }
    } else if (dragData.node_type === 'metric') {
      // 指标移动或排序
      if (dropType === 'inner') {
        // 移动到主题内部（放到该主题的最后）
        const newTopicId = dropData.id
        await updateMetric(dragData.id, { topic_id: newTopicId })
        ElMessage.success('指标已移动')
        await loadTree()
      } else {
        // 放在其他指标旁边
        const targetTopicId = dropData.topic_id
        const sourceTopicId = dragData.topic_id
        
        if (targetTopicId !== sourceTopicId) {
          // 跨主题移动：先更新指标的主题ID
          await updateMetric(dragData.id, { topic_id: targetTopicId })
        }
        
        // 获取目标主题下所有指标的新顺序
        const parent = dropNode.parent
        const siblings = parent?.childNodes || []
        const siblingIds = siblings.map((n: any) => n.data.id)
        if (targetTopicId) {
          await reorderMetrics(targetTopicId, siblingIds)
        }
        
        ElMessage.success(targetTopicId !== sourceTopicId ? '指标已移动并排序' : '排序已更新')
        if (targetTopicId !== sourceTopicId) {
          await loadTree()
        }
      }
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
    // 失败时重新加载树恢复原状
    await loadTree()
  }
}

// 节点操作命令
const handleNodeCommand = (command: string, data: MetricTreeNode, node?: any) => {
  switch (command) {
    case 'addTopic':
      topicForm.id = 0
      topicForm.project_id = data.id
      topicForm.name = ''
      topicForm.description = ''
      topicDialogTitle.value = '新建主题'
      topicDialogVisible.value = true
      break
    case 'addMetric':
      metricForm.topic_id = data.id
      metricForm.name_cn = ''
      metricForm.name_en = ''
      metricForm.metric_type = 'atomic'
      metricForm.business_caliber = ''
      metricDialogVisible.value = true
      break
    case 'edit':
      if (data.node_type === 'project') {
        projectForm.id = data.id
        projectForm.name = data.name
        projectForm.description = data.description || ''
        projectDialogTitle.value = '编辑项目'
        projectDialogVisible.value = true
      } else if (data.node_type === 'topic') {
        topicForm.id = data.id
        topicForm.project_id = data.project_id || 0
        topicForm.name = data.name
        topicForm.description = data.description || ''
        topicDialogTitle.value = '编辑主题'
        topicDialogVisible.value = true
      } else if (data.node_type === 'metric') {
        handleNodeClick(data).then(() => {
          handleEdit()
        })
      }
      break
    case 'moveUp':
      if (node) handleMoveNode(data, node, 'up')
      break
    case 'moveDown':
      if (node) handleMoveNode(data, node, 'down')
      break
    case 'delete':
      handleDeleteNode(data)
      break
  }
}

// 判断节点是否可以上移
const canMoveUp = (node: any): boolean => {
  if (!node || !node.parent) return false
  const siblings = node.parent.childNodes || []
  const index = siblings.findIndex((n: any) => n.data.id === node.data.id && n.data.node_type === node.data.node_type)
  return index > 0
}

// 判断节点是否可以下移
const canMoveDown = (node: any): boolean => {
  if (!node || !node.parent) return false
  const siblings = node.parent.childNodes || []
  const index = siblings.findIndex((n: any) => n.data.id === node.data.id && n.data.node_type === node.data.node_type)
  return index >= 0 && index < siblings.length - 1
}

// 处理节点移动
const handleMoveNode = async (data: MetricTreeNode, node: any, direction: 'up' | 'down') => {
  if (!node.parent) return
  
  const siblings = node.parent.childNodes || []
  const currentIndex = siblings.findIndex((n: any) => n.data.id === data.id && n.data.node_type === data.node_type)
  
  if (currentIndex < 0) return
  
  // 计算目标位置
  const targetIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1
  if (targetIndex < 0 || targetIndex >= siblings.length) return
  
  // 获取同级节点的ID列表（按当前顺序）
  const siblingIds = siblings.map((n: any) => n.data.id)
  
  // 交换位置
  const temp = siblingIds[currentIndex]
  siblingIds[currentIndex] = siblingIds[targetIndex]
  siblingIds[targetIndex] = temp
  
  try {
    // 根据节点类型调用不同的排序API
    if (data.node_type === 'project') {
      await reorderMetricProjects(siblingIds)
    } else if (data.node_type === 'topic') {
      await reorderMetricTopics(siblingIds)
    } else if (data.node_type === 'metric') {
      // 指标需要传递所属主题ID
      const topicId = data.topic_id
      if (topicId) {
        await reorderMetrics(topicId, siblingIds)
      }
    }
    
    ElMessage.success(direction === 'up' ? '上移成功' : '下移成功')
    await loadTree()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '移动失败')
  }
}

// 删除节点
const handleDeleteNode = async (data: MetricTreeNode) => {
  let confirmMsg = ''
  if (data.node_type === 'project') {
    confirmMsg = `确定要删除项目"${data.name}"吗？该项目下的所有主题和指标都将被删除！`
  } else if (data.node_type === 'topic') {
    confirmMsg = `确定要删除主题"${data.name}"吗？该主题下的所有指标都将被删除！`
  } else {
    // 检查指标是否被关联
    try {
      const affected = await getAffectedMetrics(data.id)
      if (affected.total > 0) {
        const names = affected.items.map(m => m.name_cn).join('、')
        confirmMsg = `指标"${data.name}"被以下指标关联：${names}。确定要删除吗？`
      } else {
        confirmMsg = `确定要删除指标"${data.name}"吗？`
      }
    } catch {
      confirmMsg = `确定要删除指标"${data.name}"吗？`
    }
  }
  
  try {
    await ElMessageBox.confirm(confirmMsg, '确认删除', { type: 'warning' })
    
    if (data.node_type === 'project') {
      await deleteMetricProject(data.id)
    } else if (data.node_type === 'topic') {
      await deleteMetricTopic(data.id)
    } else {
      await deleteMetric(data.id, true)
    }
    
    ElMessage.success('删除成功')
    selectedNode.value = null
    await loadTree()
    await loadProjects()
    await loadTopics()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 新建项目
const handleAddProject = () => {
  projectForm.id = 0
  projectForm.name = ''
  projectForm.description = ''
  projectDialogTitle.value = '新建项目'
  projectDialogVisible.value = true
}

// 保存项目
const handleSaveProject = async () => {
  if (!projectForm.name.trim()) {
    ElMessage.warning('请输入项目名称')
    return
  }
  
  saving.value = true
  try {
    if (projectForm.id) {
      await updateMetricProject(projectForm.id, {
        name: projectForm.name,
        description: projectForm.description
      })
      ElMessage.success('更新成功')
    } else {
      await createMetricProject({
        name: projectForm.name,
        description: projectForm.description
      })
      ElMessage.success('创建成功')
    }
    projectDialogVisible.value = false
    await loadTree()
    await loadProjects()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

// 保存主题
const handleSaveTopic = async () => {
  if (!topicForm.name.trim()) {
    ElMessage.warning('请输入主题名称')
    return
  }
  
  saving.value = true
  try {
    if (topicForm.id) {
      await updateMetricTopic(topicForm.id, {
        name: topicForm.name,
        description: topicForm.description
      })
      ElMessage.success('更新成功')
    } else {
      await createMetricTopic({
        project_id: topicForm.project_id,
        name: topicForm.name,
        description: topicForm.description
      })
      ElMessage.success('创建成功')
    }
    topicDialogVisible.value = false
    await loadTree()
    await loadTopics()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

// 保存新建指标
const handleSaveMetric = async () => {
  if (!metricForm.name_cn.trim()) {
    ElMessage.warning('请输入指标中文名称')
    return
  }
  
  saving.value = true
  try {
    await createMetric({
      topic_id: metricForm.topic_id,
      name_cn: metricForm.name_cn,
      name_en: metricForm.name_en,
      metric_type: metricForm.metric_type as 'atomic' | 'composite',
      business_caliber: metricForm.business_caliber
    })
    ElMessage.success('创建成功')
    metricDialogVisible.value = false
    await loadTree()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

// 编辑指标 - 打开编辑对话框
const handleEdit = () => {
  if (!selectedMetric.value) return
  
  editingMetricId.value = selectedMetric.value.id
  metricEditDialogVisible.value = true
}

// 指标编辑保存后的回调
const handleMetricEditSaved = async (metric: Metric) => {
  // 更新选中的指标数据
  selectedMetric.value = metric
  // 刷新指标树
  await loadTree()
}

// 取消编辑
const handleCancelEdit = () => {
  isEditing.value = false
}

// 保存编辑
const handleSave = async () => {
  if (!selectedMetric.value) return
  
  if (!editForm.name_cn?.trim()) {
    ElMessage.warning('请输入指标中文名称')
    return
  }
  
  saving.value = true
  try {
    await updateMetric(selectedMetric.value.id, {
      topic_id: editForm.topic_id,
      name_cn: editForm.name_cn,
      name_en: editForm.name_en,
      metric_type: editForm.metric_type,
      metric_level: editForm.metric_level,
      business_caliber: editForm.business_caliber,
      technical_caliber: editForm.technical_caliber,
      source_table: editForm.source_table,
      dimension_tables: editForm.dimension_tables,
      dimensions: editForm.dimensions,
      data_source_id: editForm.data_source_id
    })
    ElMessage.success('保存成功')
    isEditing.value = false
    // 重新加载详情
    const res = await getMetric(selectedMetric.value.id)
    selectedMetric.value = res
    await loadTree()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

// 添加关联
const handleAddRelation = async () => {
  if (!selectedMetric.value) return
  
  // 加载可选指标列表（排除当前指标）
  try {
    const res = await getMetrics({ size: 1000 })
    availableMetrics.value = res.items.filter(m => m.id !== selectedMetric.value?.id)
  } catch (error) {
    ElMessage.error('加载指标列表失败')
    return
  }
  
  relationForm.target_metric_id = 0
  relationForm.relation_type = 'related'
  relationDialogVisible.value = true
}

// 保存关联
const handleSaveRelation = async () => {
  if (!selectedMetric.value || !relationForm.target_metric_id) {
    ElMessage.warning('请选择关联指标')
    return
  }
  
  saving.value = true
  try {
    await createMetricRelation(selectedMetric.value.id, {
      target_metric_id: relationForm.target_metric_id,
      relation_type: relationForm.relation_type as 'component' | 'derived' | 'related'
    })
    ElMessage.success('添加成功')
    relationDialogVisible.value = false
    await loadMetricRelations(selectedMetric.value.id)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '添加失败')
  } finally {
    saving.value = false
  }
}

// 删除关联
const handleDeleteRelation = async (row: MetricRelation) => {
  if (!selectedMetric.value) return
  
  try {
    await ElMessageBox.confirm(`确定要删除与"${row.target_metric_name}"的关联吗？`, '确认删除', { type: 'warning' })
    await deleteMetricRelation(selectedMetric.value.id, row.target_metric_id)
    ElMessage.success('删除成功')
    await loadMetricRelations(selectedMetric.value.id)
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 关联更新事件处理
const handleRelationUpdated = () => {
  // 关联更新后刷新指标树（更新关联数量显示）
  loadTree()
}

// 指标删除事件处理（从关联管理组件触发）
const handleMetricDeleted = () => {
  // 指标被删除后，清空选中状态并刷新树
  selectedNode.value = null
  selectedMetric.value = null
  loadTree()
  loadProjects()
  loadTopics()
}

// 初始化
onMounted(async () => {
  await Promise.all([
    loadTree(),
    loadProjects(),
    loadTopics(),
    loadDataSources()
  ])
})
</script>

<style scoped>
.metric-assets-container {
  display: flex;
  gap: 16px;
  height: 100%;
  padding: 0;
}

.tree-panel {
  width: 360px;
  flex-shrink: 0;
}

.detail-panel {
  flex: 1;
  min-width: 0;
}

.tree-card,
.detail-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.tree-card :deep(.el-card__body),
.detail-card :deep(.el-card__body) {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tree-toolbar {
  margin-bottom: 12px;
}

.tree-content {
  flex: 1;
  overflow: auto;
}

.tree-footer {
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding-right: 8px;
}

.node-label {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-icon {
  font-size: 16px;
}

.project-icon {
  color: #409eff;
}

.topic-icon {
  color: #67c23a;
}

.metric-icon {
  color: #e6a23c;
}

.node-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.tree-node:hover .node-actions {
  opacity: 1;
}

.more-icon {
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.more-icon:hover {
  background-color: #f5f7fa;
}

.detail-content {
  flex: 1;
  overflow: auto;
}

.relations-header {
  margin-bottom: 12px;
}

.relations-summary {
  margin-top: 12px;
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

:deep(.el-descriptions) {
  margin-bottom: 0;
}

:deep(.el-tabs__content) {
  padding: 12px 0;
}

:deep(.el-form-item) {
  margin-bottom: 16px;
}

.caliber-text {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}
</style>
