<template>
  <div class="home">
    <el-container>
      <el-header>
        <h1>医院科室业务价值评估工具</h1>
      </el-header>
      <el-main>
        <el-card>
          <template #header>
            <div class="card-header">
              <span>欢迎使用</span>
            </div>
          </template>
          <div class="content">
            <el-icon :size="60" color="#409EFF">
              <SuccessFilled />
            </el-icon>
            <p>系统已成功启动！</p>
            <el-space>
              <el-button type="primary" @click="goToDocs">查看API文档</el-button>
              <el-button @click="testApi">测试API连接</el-button>
            </el-space>
            <div v-if="apiStatus" class="api-status">
              <el-alert :title="apiStatus.message" :type="apiStatus.type" show-icon />
            </div>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { SuccessFilled } from '@element-plus/icons-vue'
import axios from 'axios'

const apiStatus = ref<{ message: string; type: 'success' | 'error' } | null>(null)

const goToDocs = () => {
  window.open('http://localhost:8000/docs', '_blank')
}

const testApi = async () => {
  try {
    const response = await axios.get('/api/v1/')
    apiStatus.value = {
      message: `API连接成功！版本: ${response.data.version}`,
      type: 'success'
    }
  } catch (error) {
    apiStatus.value = {
      message: 'API连接失败，请检查后端服务是否启动',
      type: 'error'
    }
  }
}
</script>

<style scoped>
.home {
  height: 100%;
  background: #f0f2f5;
}

.el-header {
  background: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.el-main {
  display: flex;
  align-items: center;
  justify-content: center;
}

.content {
  text-align: center;
  padding: 40px;
}

.content p {
  margin: 20px 0;
  font-size: 18px;
  color: #606266;
}

.api-status {
  margin-top: 20px;
}
</style>
