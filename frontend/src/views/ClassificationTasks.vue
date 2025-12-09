<template>
  <div class="classification-tasks-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>医技智能分类任务</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            创建分类任务
          </el-button>
        </div>
      </template>

      <el-table
        :data="tasks"
        border
        stripe
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column label="任务名称" min-width="200">
          <template #default="{ row }">
            <el-input
              v-if="editingTaskId === row.id"
              v-model="editingTaskName"
              size="small"
              @blur="saveTaskName(row)"
              @keyup.enter="saveTaskName(row)"
              style="width: 100%"
            />
            <div v-else style="display: flex; align-items: center; justify-content: space-between;">
              <span>{{ row.task_name }}</span>
              <el-button
                type="text"
                size="small"
                @click="startEditTaskName(row)"
                style="margin-left: 10px;"
              >
                <el-icon><Edit /></el-icon>
              </el-button>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="收费类别" min-width="150">
          <template #default="{ row }">
            <el-tag
              v-for="(category, index) in row.charge_categories"
              :key="index"
              size="small"
              style="margin-right: 5px"
            >
              {{ category }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="进度" min-width="300">
          <template #default="{ row }">
            <ProgressIndicator
              :status="row.status"
              :total-items="row.total_items"
              :processed-items="row.processed_items"
              :failed-items="row.failed_items"
            />
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'paused' || row.status === 'failed'"
              type="primary"
              size="small"
              @click="continueTask(row.id)"
            >
              继续处理
            </el-button>
            <el-button
              v-if="row.status === 'completed'"
              type="success"
              size="small"
              @click="viewPlan(row.id)"
            >
              查看预案
            </el-button>
            <el-button
              type="info"
              size="small"
              @click="viewLogs(row.id)"
            >
              查看日志
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="deleteTask(row.id)"
              :disabled="row.status === 'processing'"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建任务对话框 -->
    <CreateTaskDialog
      v-model:visible="createDialogVisible"
      @success="handleCreateSuccess"
    />

    <!-- 日志对话框 -->
    <el-dialog
      v-model="logsDialogVisible"
      title="处理日志"
      width="800px"
      append-to-body
    >
      <el-table
        :data="taskLogs"
        border
        stripe
        max-height="400"
      >
        <el-table-column prop="charge_item_name" label="项目名称" min-width="150" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="error_message" label="错误信息" min-width="200" show-overflow-tooltip />
        <el-table-column prop="processed_at" label="处理时间" width="180">
          <template #default="{ row }">
            {{ row.processed_at ? formatDateTime(row.processed_at) : '-' }}
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Edit } from '@element-plus/icons-vue';
import { useRouter } from 'vue-router';
import {
  getClassificationTasks,
  updateClassificationTask,
  deleteClassificationTask,
  continueClassificationTask,
  getTaskLogs,
  type ClassificationTask,
  type TaskLog
} from '@/api/classification-tasks';
import { getClassificationPlans } from '@/api/classification-plans';
import CreateTaskDialog from '@/components/CreateTaskDialog.vue';
import ProgressIndicator from '@/components/ProgressIndicator.vue';

const router = useRouter();
const loading = ref(false);
const tasks = ref<ClassificationTask[]>([]);
const createDialogVisible = ref(false);
const logsDialogVisible = ref(false);
const taskLogs = ref<TaskLog[]>([]);
const editingTaskId = ref<number | null>(null);
const editingTaskName = ref('');
let pollingTimer: number | null = null;

// 加载任务列表
const loadTasks = async () => {
  try {
    loading.value = true;
    tasks.value = await getClassificationTasks();
  } catch (error) {
    console.error('加载任务列表失败:', error);
    ElMessage.error('加载任务列表失败');
  } finally {
    loading.value = false;
  }
};

// 显示创建对话框
const showCreateDialog = () => {
  createDialogVisible.value = true;
};

// 创建成功回调
const handleCreateSuccess = () => {
  loadTasks();
  startPolling();
};

// 开始编辑任务名称
const startEditTaskName = (task: ClassificationTask) => {
  editingTaskId.value = task.id;
  editingTaskName.value = task.task_name;
};

// 保存任务名称
const saveTaskName = async (task: ClassificationTask) => {
  if (!editingTaskName.value.trim()) {
    ElMessage.warning('任务名称不能为空');
    editingTaskId.value = null;
    return;
  }

  if (editingTaskName.value === task.task_name) {
    editingTaskId.value = null;
    return;
  }

  try {
    await updateClassificationTask(task.id, { task_name: editingTaskName.value });
    ElMessage.success('任务名称已更新');
    task.task_name = editingTaskName.value;
    editingTaskId.value = null;
  } catch (error: any) {
    console.error('更新任务名称失败:', error);
    ElMessage.error(error.response?.data?.detail || '更新失败');
    editingTaskId.value = null;
  }
};

// 继续处理任务
const continueTask = async (id: number) => {
  try {
    await continueClassificationTask(id);
    ElMessage.success('任务已继续处理');
    loadTasks();
    startPolling();
  } catch (error: any) {
    console.error('继续处理失败:', error);
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail);
    } else {
      ElMessage.error('继续处理失败');
    }
  }
};

// 查看预案
const viewPlan = async (taskId: number) => {
  try {
    // 查询该任务的预案
    const res: any = await getClassificationPlans({
      skip: 0,
      limit: 100
    });
    
    // 找到该任务的预案
    const plan = res.items?.find((p: any) => p.task_id === taskId);
    
    if (plan) {
      // 直接跳转到预案详情页
      router.push({
        name: 'ClassificationPlanDetail',
        params: { id: plan.id }
      });
    } else {
      ElMessage.warning('该任务暂无预案');
    }
  } catch (error) {
    console.error('查询预案失败:', error);
    ElMessage.error('查询预案失败');
  }
};

// 查看日志
const viewLogs = async (id: number) => {
  try {
    taskLogs.value = await getTaskLogs(id);
    logsDialogVisible.value = true;
  } catch (error) {
    console.error('加载日志失败:', error);
    ElMessage.error('加载日志失败');
  }
};

// 删除任务
const deleteTask = async (id: number) => {
  try {
    await ElMessageBox.confirm(
      '删除任务将同时删除关联的预案和处理记录，是否继续？',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );

    await deleteClassificationTask(id);
    ElMessage.success('删除成功');
    loadTasks();
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error);
      ElMessage.error('删除失败');
    }
  }
};

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    pending: 'info',
    processing: 'primary',
    completed: 'success',
    failed: 'danger',
    paused: 'warning'
  };
  return typeMap[status] || 'info';
};

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
    paused: '已暂停'
  };
  return textMap[status] || status;
};

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

// 开始轮询
const startPolling = () => {
  // 如果已有轮询，先停止
  stopPolling();
  
  // 每3秒轮询一次
  pollingTimer = window.setInterval(() => {
    // 检查是否有处理中的任务
    const hasProcessing = tasks.value.some(task => task.status === 'processing');
    if (hasProcessing) {
      loadTasks();
    } else {
      // 没有处理中的任务，停止轮询
      stopPolling();
    }
  }, 3000);
};

// 停止轮询
const stopPolling = () => {
  if (pollingTimer) {
    clearInterval(pollingTimer);
    pollingTimer = null;
  }
};

onMounted(() => {
  loadTasks();
  // 检查是否有处理中的任务，如果有则开始轮询
  setTimeout(() => {
    const hasProcessing = tasks.value.some(task => task.status === 'processing');
    if (hasProcessing) {
      startPolling();
    }
  }, 1000);
});

onUnmounted(() => {
  stopPolling();
});
</script>

<style scoped>
.classification-tasks-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
