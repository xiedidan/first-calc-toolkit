<template>
  <div class="model-rules-container">
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
        <el-table-column label="节点名称" width="345">
          <template #default="{ row }">
            {{ row.name }}
            <el-tag v-if="row.node_type === 'sequence'" type="primary" size="small" style="margin-left: 8px">序列</el-tag>
            <el-tag v-else type="success" size="small" style="margin-left: 8px">维度</el-tag>
            <el-tag v-if="row.is_leaf" type="warning" size="small" style="margin-left: 4px">末级</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="code" label="节点编码" width="200" />
        <el-table-column label="规则说明" min-width="400">
          <template #default="{ row }">
            <div v-if="row.rule && row.rule.trim()" class="rule-text">
              {{ row.rule }}
            </div>
            <span v-else class="rule-empty">暂无规则说明</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getModelVersion, getModelNodes, type ModelVersion, type ModelNode } from '@/api/model'

const route = useRoute()
const router = useRouter()

// 数据
const loading = ref(false)
const versionInfo = ref<ModelVersion>()
const tableData = ref<ModelNode[]>([])

// 从路由参数获取 versionId
const versionId = computed(() => {
  const id = route.params.versionId
  return typeof id === 'string' ? parseInt(id, 10) : 0
})

// 获取版本信息
const fetchVersionInfo = async () => {
  try {
    versionInfo.value = await getModelVersion(versionId.value)
  } catch (error: any) {
    ElMessage.error(error.message || '获取版本信息失败')
    throw error
  }
}

// 获取节点数据
const fetchNodes = async () => {
  try {
    const res = await getModelNodes({ version_id: versionId.value })
    tableData.value = res.items
  } catch (error: any) {
    ElMessage.error(error.message || '获取节点数据失败')
    throw error
  }
}

// 加载所有数据
const fetchData = async () => {
  // 验证 versionId
  if (!versionId.value || isNaN(versionId.value)) {
    ElMessage.error('无效的版本ID')
    router.push({ name: 'ModelVersions' })
    return
  }

  loading.value = true
  try {
    await Promise.all([
      fetchVersionInfo(),
      fetchNodes()
    ])
  } catch (error) {
    // 错误已在各自的函数中处理
  } finally {
    loading.value = false
  }
}

// 返回版本列表
const handleBack = () => {
  router.push({ name: 'ModelVersions' })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.model-rules-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.version-title {
  margin-left: 20px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.rule-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.6;
  color: #606266;
}

.rule-empty {
  color: #c0c4cc;
  font-style: italic;
}
</style>
