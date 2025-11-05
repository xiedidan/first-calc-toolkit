<template>
  <el-container class="layout-container">
    <el-header class="layout-header">
      <div class="header-left">
        <h3>{{ pageTitle }}</h3>
      </div>
      <div class="header-right">
        <!-- Hospital Selector -->
        <el-dropdown
          v-if="hospitalStore.accessibleHospitals.length > 0"
          @command="handleHospitalSwitch"
          class="hospital-selector"
        >
          <span class="hospital-info">
            <el-icon><OfficeBuilding /></el-icon>
            <span>{{ hospitalStore.currentHospitalName || '请选择医疗机构' }}</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-for="hospital in hospitalStore.accessibleHospitals"
                :key="hospital.id"
                :command="hospital.id"
                :disabled="hospital.id === hospitalStore.currentHospitalId"
              >
                <div class="hospital-item">
                  <span>{{ hospital.name }}</span>
                  <el-icon v-if="hospital.id === hospitalStore.currentHospitalId" color="#67C23A">
                    <Check />
                  </el-icon>
                </div>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!-- User Dropdown -->
        <el-dropdown @command="handleUserCommand">
          <span class="user-info">
            <el-icon><User /></el-icon>
            <span>{{ userStore.userInfo?.name }}</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item disabled>
                <div class="user-detail">
                  <div>用户名: {{ userStore.userInfo?.username }}</div>
                  <div>角色: {{ userStore.userInfo?.roles.join(', ') }}</div>
                </div>
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-container>
      <el-aside width="220px" class="layout-aside">
        <el-menu
          :default-active="activeMenu"
          :default-openeds="['model', 'base-data', 'system']"
          router
          class="layout-menu"
        >
          <!-- 首页 -->
          <el-menu-item 
            index="/dashboard"
            :disabled="!isMenuItemEnabled('/dashboard')"
          >
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>

          <!-- 数据模型管理 (未实现) -->
          <el-menu-item index="/data-model" disabled>
            <el-icon><Grid /></el-icon>
            <span>数据模型管理</span>
          </el-menu-item>

          <!-- 数据质量报告 (未实现) -->
          <el-menu-item index="/data-quality" disabled>
            <el-icon><DocumentChecked /></el-icon>
            <span>数据质量报告</span>
          </el-menu-item>

          <!-- 智能分类分级 (未实现) -->
          <el-menu-item index="/intelligent-classification" disabled>
            <el-icon><Operation /></el-icon>
            <span>智能分类分级</span>
          </el-menu-item>

          <!-- 评估模型管理 -->
          <el-sub-menu 
            index="model"
            :disabled="!isMenuItemEnabled('/model-versions')"
          >
            <template #title>
              <el-icon><Document /></el-icon>
              <span>评估模型管理</span>
            </template>
            <el-menu-item index="/model-versions">模型版本管理</el-menu-item>
            <el-menu-item index="/dimension-items">维度目录管理</el-menu-item>
            <el-menu-item index="/calculation-workflows">计算流程管理</el-menu-item>
          </el-sub-menu>

          <!-- 计算任务管理 -->
          <el-menu-item 
            index="/calculation-tasks"
            :disabled="!isMenuItemEnabled('/calculation-tasks')"
          >
            <el-icon><Clock /></el-icon>
            <span>计算任务管理</span>
          </el-menu-item>

          <!-- 报表查询展示 -->
          <el-menu-item 
            index="/results"
            :disabled="!isMenuItemEnabled('/results')"
          >
            <el-icon><DataAnalysis /></el-icon>
            <span>业务价值报表</span>
          </el-menu-item>

          <!-- ADV自动建模 (未实现) -->
          <el-menu-item index="/adv-modeling" disabled>
            <el-icon><MagicStick /></el-icon>
            <span>ADV自动建模</span>
          </el-menu-item>

          <!-- 智能问数系统 (未实现) -->
          <el-menu-item index="/intelligent-query" disabled>
            <el-icon><ChatDotRound /></el-icon>
            <span>智能问数系统</span>
          </el-menu-item>

          <!-- 运营分析报告 (未实现) -->
          <el-menu-item index="/operation-analysis" disabled>
            <el-icon><TrendCharts /></el-icon>
            <span>运营分析报告</span>
          </el-menu-item>

          <!-- 基础数据管理 -->
          <el-sub-menu 
            index="base-data"
            :disabled="!isMenuItemEnabled('/departments')"
          >
            <template #title>
              <el-icon><FolderOpened /></el-icon>
              <span>基础数据管理</span>
            </template>
            <el-menu-item index="/departments">科室对照管理</el-menu-item>
            <el-menu-item index="/charge-items">收费项目管理</el-menu-item>
          </el-sub-menu>

          <!-- 数据源管理 -->
          <el-menu-item index="/data-sources">
            <el-icon><Connection /></el-icon>
            <span>数据源管理</span>
          </el-menu-item>

          <!-- 医疗机构管理 -->
          <el-menu-item 
            v-if="isAdmin"
            index="/hospitals"
          >
            <el-icon><OfficeBuilding /></el-icon>
            <span>医疗机构管理</span>
          </el-menu-item>

          <!-- 系统设置 -->
          <el-sub-menu index="system">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>系统设置</span>
            </template>
            <el-menu-item index="/system-settings">参数管理</el-menu-item>
            <el-menu-item index="/users">用户管理</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>

      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, 
  ArrowDown, 
  SwitchButton, 
  HomeFilled,
  Grid,
  DocumentChecked,
  Operation,
  Document, 
  Clock, 
  DataAnalysis,
  MagicStick,
  ChatDotRound,
  TrendCharts,
  FolderOpened, 
  Connection,
  Setting,
  OfficeBuilding,
  Check
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { useHospitalStore } from '@/stores/hospital'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const hospitalStore = useHospitalStore()

// Page title based on current hospital
const pageTitle = computed(() => {
  if (hospitalStore.currentHospitalName) {
    return `${hospitalStore.currentHospitalName}科室业务价值评估工具`
  }
  return '医院科室业务价值评估工具'
})

// Check if user is admin
const isAdmin = computed(() => {
  return userStore.hasRole('admin') || userStore.hasRole('系统管理员')
})

// Check if menu item should be enabled
const isMenuItemEnabled = (menuPath: string) => {
  return hospitalStore.isMenuEnabled(menuPath)
}

const activeMenu = computed(() => {
  const path = route.path
  // 处理子路由，让对应的菜单项高亮
  if (path.startsWith('/model-nodes') || path.startsWith('/model-rules')) {
    return '/model-versions'
  }
  if (path.startsWith('/dimension-items')) {
    return '/dimension-items'
  }
  if (path.startsWith('/calculation-workflows')) {
    return '/calculation-workflows'
  }
  if (path.startsWith('/calculation-tasks')) {
    return '/calculation-tasks'
  }
  if (path.startsWith('/results')) {
    return '/results'
  }
  if (path.startsWith('/data-sources')) {
    return '/data-sources'
  }
  if (path.startsWith('/hospitals')) {
    return '/hospitals'
  }
  return path
})

const handleHospitalSwitch = async (hospitalId: number) => {
  try {
    await hospitalStore.activate(hospitalId)
    ElMessage.success('切换医疗机构成功')
    // Reload current page data
    router.go(0)
  } catch (error) {
    ElMessage.error('切换医疗机构失败')
  }
}

const handleUserCommand = (command: string) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      userStore.logout()
      hospitalStore.clearCurrentHospital()
      router.push('/login')
    })
  }
}

// Load accessible hospitals on mount
onMounted(async () => {
  try {
    await hospitalStore.fetchAccessibleHospitals()
  } catch (error) {
    console.error('Failed to load accessible hospitals:', error)
  }
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
  transform: scale(0.75);
  transform-origin: top left;
  width: 133.33%; /* 100% / 0.75 */
  height: 133.33vh; /* 100vh / 0.75 */
}

.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
}

.header-left h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.hospital-selector {
  margin-right: 8px;
}

.hospital-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background 0.3s;
  color: #409eff;
  font-weight: 500;
}

.hospital-info:hover {
  background: #ecf5ff;
}

.hospital-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-width: 200px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background 0.3s;
}

.user-info:hover {
  background: #f5f7fa;
}

.user-detail {
  padding: 8px 0;
  font-size: 13px;
  color: #606266;
}

.user-detail div {
  margin: 4px 0;
}

.layout-aside {
  background: #fff;
  border-right: 1px solid #e4e7ed;
}

.layout-menu {
  border-right: none;
}

/* 增强菜单项高亮效果 */
.layout-menu :deep(.el-menu-item) {
  transition: all 0.3s;
}

.layout-menu :deep(.el-menu-item:hover) {
  background-color: #ecf5ff;
}

.layout-menu :deep(.el-menu-item.is-active) {
  background-color: #409eff;
  color: #fff;
  font-weight: 600;
}

.layout-menu :deep(.el-menu-item.is-active .el-icon) {
  color: #fff;
}

/* 子菜单样式 */
.layout-menu :deep(.el-sub-menu__title) {
  transition: all 0.3s;
}

.layout-menu :deep(.el-sub-menu__title:hover) {
  background-color: #ecf5ff;
}

/* 二级菜单缩进 */
.layout-menu :deep(.el-menu-item) {
  padding-left: 20px !important;
}

.layout-menu :deep(.el-sub-menu .el-menu-item) {
  padding-left: 50px !important;
  min-width: 200px;
}

/* 禁用状态样式 */
.layout-menu :deep(.el-menu-item.is-disabled) {
  opacity: 0.5;
  cursor: not-allowed;
}

.layout-main {
  background: #f0f2f5;
  padding: 10px;
}
</style>
