<template>
  <div class="data-sources-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据源管理</span>
        </div>
      </template>

      <DataSourceManagement />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import DataSourceManagement from '@/components/DataSourceManagement.vue'
</script>

<style scoped>
.data-sources-container {
  padding: 0;
  width: 100%;
  height: 100%;
}

.data-sources-container :deep(.el-card) {
  width: 100%;
  height: 100%;
}

.data-sources-container :deep(.el-card__body) {
  height: calc(100% - 60px);
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
