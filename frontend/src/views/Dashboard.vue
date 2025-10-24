<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>欢迎使用医院科室业务价值评估工具</span>
            </div>
          </template>
          <div class="welcome-content">
            <el-result icon="success" title="系统运行正常">
              <template #sub-title>
                <p>欢迎您，{{ userStore.userInfo?.name }}</p>
                <p>当前角色：{{ userStore.userInfo?.roles.join(', ') }}</p>
              </template>
              <template #extra>
                <el-button type="primary" @click="router.push('/users')">
                  用户管理
                </el-button>
              </template>
            </el-result>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="8">
        <el-card>
          <el-statistic title="系统用户" :value="stats.totalUsers">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <el-statistic title="在线用户" :value="stats.onlineUsers">
            <template #prefix>
              <el-icon><UserFilled /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <el-statistic title="系统角色" :value="stats.totalRoles">
            <template #prefix>
              <el-icon><Avatar /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, UserFilled, Avatar } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getUserList } from '@/api/user'

const router = useRouter()
const userStore = useUserStore()

const stats = ref({
  totalUsers: 0,
  onlineUsers: 1,
  totalRoles: 5
})

onMounted(async () => {
  try {
    const response = await getUserList({ page: 1, size: 1 })
    stats.value.totalUsers = response.total
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-content {
  padding: 10px 0;
}
</style>
