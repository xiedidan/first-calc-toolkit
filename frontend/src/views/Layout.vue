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
                  <div>角色: {{ userRolesDisplay }}</div>
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

    <el-container class="layout-body">
      <el-aside width="220px" class="layout-aside">
        <el-menu
          :default-active="activeMenu"
          unique-opened
          router
          class="layout-menu"
        >
          <!-- 首页 -->
          <el-menu-item 
            v-if="isMenuItemEnabled('/dashboard')"
            index="/dashboard"
          >
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>

          <!-- 数据模板发布 -->
          <el-menu-item 
            v-if="isMenuItemEnabled('/data-template-publish')"
            index="/data-template-publish"
          >
            <el-icon><Grid /></el-icon>
            <span>数据模板发布</span>
          </el-menu-item>

          <!-- 数据质量报告 -->
          <el-sub-menu 
            v-if="isSubMenuVisible(['/data-issues'])"
            index="data-quality"
          >
            <template #title>
              <el-icon><DocumentChecked /></el-icon>
              <span>数据质量报告</span>
            </template>
            <el-menu-item v-if="isMenuItemEnabled('/data-issues')" index="/data-issues">数据问题记录</el-menu-item>
          </el-sub-menu>

          <!-- 智能分类分级 -->
          <el-sub-menu 
            v-if="isSubMenuVisible(['/classification-tasks', '/classification-plans'])"
            index="intelligent-classification"
          >
            <template #title>
              <el-icon><Operation /></el-icon>
              <span>智能分类分级</span>
            </template>
            <el-menu-item v-if="isMenuItemEnabled('/classification-tasks')" index="/classification-tasks">医技分类任务</el-menu-item>
            <el-menu-item v-if="isMenuItemEnabled('/classification-plans')" index="/classification-plans">分类预案管理</el-menu-item>
          </el-sub-menu>

          <!-- 评估模型管理 -->
          <el-sub-menu 
            v-if="isSubMenuVisible(['/model-versions', '/dimension-items', '/cost-benchmarks', '/inclusive-fees', '/discipline-rules', '/calculation-workflows'])"
            index="model"
          >
            <template #title>
              <el-icon><Document /></el-icon>
              <span>评估模型管理</span>
            </template>
            <el-menu-item v-if="isMenuItemEnabled('/model-versions')" index="/model-versions">模型版本管理</el-menu-item>
            <el-menu-item v-if="isMenuItemEnabled('/dimension-items')" index="/dimension-items">维度目录管理</el-menu-item>
            <el-menu-item v-if="isMenuItemEnabled('/cost-benchmarks')" index="/cost-benchmarks">成本基准管理</el-menu-item>
            <el-menu-item v-if="isMenuItemEnabled('/inclusive-fees')" index="/inclusive-fees">内含收费管理</el-menu-item>
            <el-menu-item v-if="isMenuItemEnabled('/discipline-rules')" index="/discipline-rules">学科规则管理</el-menu-item>
            <el-menu-item v-if="isMenuItemEnabled('/calculation-workflows')" index="/calculation-workflows">计算流程管理</el-menu-item>
          </el-sub-menu>

          <!-- 业务导向管理 -->
          <el-sub-menu 
            v-if="isSubMenuVisible(['/orientation-rules', '/orientation-benchmarks', '/orientation-ladders'])"
            index="orientation"
          >
            <template #title>
              <el-icon><Guide /></el-icon>
              <span>业务导向管理</span>
            </template>
            <el-menu-item v-if="isMenuItemEnabled('/orientation-rules')" index="/orientation-rules">导向规则管理</el-menu-item>
            <el-menu-item v-if="isMenuItemEnabled('/orientation-benchmarks')" index="/orientation-benchmarks">导向基准管理</el-menu-item>
            <el-menu-item v-if="isMenuItemEnabled('/orientation-ladders')" index="/orientation-ladders">导向阶梯管理</el-menu-item>
          </el-sub-menu>

          <!-- 计算任务管理 -->
          <el-menu-item 
            v-if="isMenuItemEnabled('/calculation-tasks')"
            index="/calculation-tasks"
          >
            <el-icon><Clock /></el-icon>
            <span>计算任务管理</span>
          </el-menu-item>

          <!-- 报表查询展示 -->
          <el-menu-item 
            v-if="isMenuItemEnabled('/results')"
            index="/results"
          >
            <el-icon><DataAnalysis /></el-icon>
            <span>业务价值报表</span>
          </el-menu-item>

          <!-- ADV自动建模 (未实现) -->
          <el-menu-item v-if="isAdmin" index="/adv-modeling" disabled>
            <el-icon><MagicStick /></el-icon>
            <span>ADV自动建模</span>
          </el-menu-item>

          <!-- 智能问数系统 -->
          <el-sub-menu 
            v-if="isSubMenuVisible(['/smart-data-qa', '/metric-assets'])"
            index="intelligent-query"
          >
            <template #title>
              <el-icon><ChatDotRound /></el-icon>
              <span>智能问数系统</span>
            </template>
            <el-menu-item v-if="isMenuItemEnabled('/smart-data-qa')" index="/smart-data-qa">智能数据问答</el-menu-item>
            <el-menu-item v-if="isMenuItemEnabled('/metric-assets')" index="/metric-assets">指标资产管理</el-menu-item>
          </el-sub-menu>

          <!-- 运营分析报告 -->
          <el-sub-menu 
            v-if="isSubMenuVisible(['/report-view', '/report-management'])"
            index="operation-analysis"
          >
            <template #title>
              <el-icon><TrendCharts /></el-icon>
              <span>运营分析报告</span>
            </template>
            <el-menu-item v-if="isMenuItemEnabled('/report-view')" index="/report-view">分析报告查看</el-menu-item>
            <el-menu-item v-if="isAdmin" index="/report-management">分析报告管理</el-menu-item>
          </el-sub-menu>

          <!-- 基础数据管理 -->
          <el-sub-menu 
            v-if="isSubMenuVisible(['/departments', '/charge-items', '/cost-reports', '/reference-values', '/data-templates'])"
            index="base-data"
          >
            <template #title>
              <el-icon><FolderOpened /></el-icon>
              <span>基础数据管理</span>
            </template>
            <el-menu-item v-if="isMenuItemEnabled('/departments')" index="/departments">科室对照管理</el-menu-item>
            <el-menu-item v-if="isMenuItemEnabled('/charge-items')" index="/charge-items">收费项目管理</el-menu-item>
            <el-menu-item v-if="isMenuItemEnabled('/cost-reports')" index="/cost-reports">成本报表管理</el-menu-item>
            <el-menu-item v-if="isMenuItemEnabled('/reference-values')" index="/reference-values">参考价值管理</el-menu-item>
            <el-menu-item v-if="isAdmin" index="/data-templates">数据模板管理</el-menu-item>
          </el-sub-menu>

          <!-- 数据源管理 -->
          <el-menu-item v-if="isMenuItemEnabled('/data-sources')" index="/data-sources">
            <el-icon><Connection /></el-icon>
            <span>数据源管理</span>
          </el-menu-item>

          <!-- 系统设置 -->
          <el-sub-menu index="system">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>系统设置</span>
            </template>
            <el-menu-item v-if="isMenuItemEnabled('/system-settings')" index="/system-settings">参数管理</el-menu-item>
            <el-menu-item v-if="isAdmin" index="/users">用户管理</el-menu-item>
            <el-menu-item v-if="isAdmin" index="/roles">用户角色管理</el-menu-item>
            <el-menu-item v-if="isMaintainer" index="/ai-config">AI接口管理</el-menu-item>
            <el-menu-item v-if="isAdmin" index="/hospitals">医疗机构管理</el-menu-item>
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
  Guide,
  Clock, 
  DataAnalysis,
  MagicStick,
  ChatDotRound,
  TrendCharts,
  FolderOpened, 
  Connection,
  Setting,
  OfficeBuilding,
  Check,
  Money
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

// Check if hospital is activated
const isHospitalActivated = computed(() => hospitalStore.isHospitalActivated)

// Check if user is admin
const isAdmin = computed(() => userStore.isAdmin)

// Check if user is maintainer
const isMaintainer = computed(() => userStore.isMaintainer)

// User roles display
const userRolesDisplay = computed(() => {
  return userStore.userInfo?.role_name || ''
})

// Check if menu item should be enabled (combines hospital activation + user permission)
const isMenuItemEnabled = (menuPath: string) => {
  // 首先检查医疗机构是否激活
  if (!hospitalStore.isMenuEnabled(menuPath)) {
    return false
  }
  // 管理员和维护者有所有权限
  if (isAdmin.value) {
    return true
  }
  // 普通用户检查菜单权限
  return userStore.hasMenuPermission(menuPath)
}

// Check if sub-menu should be visible (at least one child is permitted)
const isSubMenuVisible = (childPaths: string[]) => {
  if (isAdmin.value) return true
  return childPaths.some(path => userStore.hasMenuPermission(path))
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
  if (path.startsWith('/cost-benchmarks')) {
    return '/cost-benchmarks'
  }
  if (path.startsWith('/inclusive-fees')) {
    return '/inclusive-fees'
  }
  if (path.startsWith('/discipline-rules')) {
    return '/discipline-rules'
  }
  if (path.startsWith('/calculation-workflows')) {
    return '/calculation-workflows'
  }
  if (path.startsWith('/calculation-tasks')) {
    return '/calculation-tasks'
  }
  if (path.startsWith('/classification-plans')) {
    return '/classification-plans'
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
  if (path.startsWith('/data-issues')) {
    return '/data-issues'
  }
  if (path.startsWith('/ai-config')) {
    return '/ai-config'
  }
  if (path.startsWith('/roles')) {
    return '/roles'
  }
  return path
})

const handleHospitalSwitch = async (hospitalId: number) => {
  try {
    await hospitalStore.activate(hospitalId)
    ElMessage.success('切换医疗机构成功')
    // Navigate to dashboard instead of reloading
    router.push('/dashboard')
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
  width: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.layout-body {
  flex: 1;
  overflow: hidden;
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
  overflow-y: auto;
  overflow-x: hidden;
}

.layout-menu {
  border-right: none;
  height: auto;
  min-height: 100%;
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
  overflow-y: auto;
  height: calc(100vh - 60px);
}


</style>
