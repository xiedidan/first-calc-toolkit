<template>
  <div class="progress-indicator">
    <el-progress
      :percentage="progressPercentage"
      :status="progressStatus"
      :stroke-width="20"
    >
      <template #default="{ percentage }">
        <span class="progress-text">{{ percentage }}%</span>
      </template>
    </el-progress>
    <div class="progress-info">
      <span class="progress-count">
        已处理: {{ processedItems }} / {{ totalItems }}
      </span>
      <span class="progress-status" :class="`status-${status}`">
        {{ statusText }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  status: string;
  totalItems: number;
  processedItems: number;
  failedItems?: number;
}

const props = withDefaults(defineProps<Props>(), {
  failedItems: 0
});

// 计算进度百分比
const progressPercentage = computed(() => {
  if (props.totalItems === 0) return 0;
  return Math.round((props.processedItems / props.totalItems) * 100);
});

// 进度条状态
const progressStatus = computed(() => {
  if (props.status === 'completed') return 'success';
  if (props.status === 'failed') return 'exception';
  if (props.status === 'paused') return 'warning';
  return undefined;
});

// 状态文本
const statusText = computed(() => {
  const statusMap: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
    paused: '已暂停'
  };
  return statusMap[props.status] || props.status;
});
</script>

<style scoped>
.progress-indicator {
  width: 100%;
}

.progress-text {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  font-size: 13px;
  color: #909399;
}

.progress-count {
  font-weight: 500;
}

.progress-status {
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
}

.status-pending {
  color: #909399;
  background-color: #f4f4f5;
}

.status-processing {
  color: #409eff;
  background-color: #ecf5ff;
}

.status-completed {
  color: #67c23a;
  background-color: #f0f9ff;
}

.status-failed {
  color: #f56c6c;
  background-color: #fef0f0;
}

.status-paused {
  color: #e6a23c;
  background-color: #fdf6ec;
}
</style>
