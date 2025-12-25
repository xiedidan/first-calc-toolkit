import { useUserStore } from '@/stores/user'
import type { RouteRecordRaw } from 'vue-router'
import { createRouter, createWebHistory } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/views/Layout.vue'),
    meta: { requiresAuth: true },
    redirect: '/dashboard',
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页' }
      },
      {
        path: '/users',
        name: 'Users',
        component: () => import('@/views/Users.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: '/roles',
        name: 'Roles',
        component: () => import('@/views/Roles.vue'),
        meta: { title: '用户角色管理' }
      },
      {
        path: '/charge-items',
        name: 'ChargeItems',
        component: () => import('@/views/ChargeItems.vue'),
        meta: { title: '收费项目管理' }
      },
      {
        path: '/departments',
        name: 'Departments',
        component: () => import('@/views/Departments.vue'),
        meta: { title: '科室管理' }
      },
      {
        path: '/dimension-items',
        name: 'DimensionItems',
        component: () => import('@/views/DimensionItems.vue'),
        meta: { title: '维度目录管理' }
      },
      {
        path: '/cost-benchmarks',
        name: 'CostBenchmarks',
        component: () => import('@/views/CostBenchmarks.vue'),
        meta: { title: '成本基准管理' }
      },
      {
        path: '/discipline-rules',
        name: 'DisciplineRules',
        component: () => import('@/views/DisciplineRules.vue'),
        meta: { title: '学科规则管理' }
      },
      {
        path: '/model-versions',
        name: 'ModelVersions',
        component: () => import('@/views/ModelVersions.vue'),
        meta: { title: '评估模型管理' }
      },
      {
        path: '/model-nodes/:versionId',
        name: 'ModelNodes',
        component: () => import('@/views/ModelNodes.vue'),
        meta: { title: '模型结构编辑' }
      },
      {
        path: '/model-rules/:versionId',
        name: 'ModelRules',
        component: () => import('@/views/ModelRules.vue'),
        meta: { title: '模型规则展示' }
      },
      {
        path: '/calculation-workflows',
        name: 'CalculationWorkflows',
        component: () => import('@/views/CalculationWorkflows.vue'),
        meta: { title: '计算流程管理' }
      },
      {
        path: '/data-sources',
        name: 'DataSources',
        component: () => import('@/views/DataSources.vue'),
        meta: { title: '数据源管理' }
      },
      {
        path: '/data-templates',
        name: 'DataTemplates',
        component: () => import('@/views/DataTemplates.vue'),
        meta: { title: '数据模板管理', requiresAdmin: true }
      },
      {
        path: '/data-template-publish',
        name: 'DataTemplatePublish',
        component: () => import('@/views/DataTemplatePublish.vue'),
        meta: { title: '数据模板发布' }
      },
      {
        path: '/system-settings',
        name: 'SystemSettings',
        component: () => import('@/views/SystemSettings.vue'),
        meta: { title: '系统设置' }
      },
      {
        path: '/ai-config',
        name: 'AIConfig',
        component: () => import('@/views/AIConfig.vue'),
        meta: { title: 'AI接口管理', requiresAdmin: true }
      },
      {
        path: '/calculation-tasks',
        name: 'CalculationTasks',
        component: () => import('@/views/CalculationTasks.vue'),
        meta: { title: '计算任务管理' }
      },
      {
        path: '/results',
        name: 'Results',
        component: () => import('@/views/Results.vue'),
        meta: { title: '业务价值报表' }
      },
      {
        path: '/hospitals',
        name: 'Hospitals',
        component: () => import('@/views/Hospitals.vue'),
        meta: { title: '医疗机构管理', requiresAdmin: true }
      },
      {
        path: '/data-issues',
        name: 'DataIssues',
        component: () => import('@/views/DataIssues.vue'),
        meta: { title: '数据问题记录' }
      },
      {
        path: '/orientation-rules',
        name: 'OrientationRules',
        component: () => import('@/views/OrientationRules.vue'),
        meta: { title: '导向规则管理' }
      },
      {
        path: '/orientation-benchmarks',
        name: 'OrientationBenchmarks',
        component: () => import('@/views/OrientationBenchmarks.vue'),
        meta: { title: '导向基准管理' }
      },
      {
        path: '/orientation-ladders',
        name: 'OrientationLadders',
        component: () => import('@/views/OrientationLadders.vue'),
        meta: { title: '导向阶梯管理' }
      },
      {
        path: '/classification-tasks',
        name: 'ClassificationTasks',
        component: () => import('@/views/ClassificationTasks.vue'),
        meta: { title: '医技智能分类' }
      },
      {
        path: '/classification-plans',
        name: 'ClassificationPlans',
        component: () => import('@/views/ClassificationPlans.vue'),
        meta: { title: '分类预案管理' }
      },
      {
        path: '/classification-plans/:id',
        name: 'ClassificationPlanDetail',
        component: () => import('@/views/ClassificationPlanDetail.vue'),
        meta: { title: '预案详情' }
      },
      {
        path: '/reference-values',
        name: 'ReferenceValues',
        component: () => import('@/views/ReferenceValues.vue'),
        meta: { title: '参考价值管理' }
      },
      {
        path: '/cost-reports',
        name: 'CostReports',
        component: () => import('@/views/CostReports.vue'),
        meta: { title: '成本报表管理' }
      },
      {
        path: '/report-view',
        name: 'ReportView',
        component: () => import('@/views/ReportView.vue'),
        meta: { title: '分析报告查看' }
      },
      {
        path: '/report-management',
        name: 'ReportManagement',
        component: () => import('@/views/ReportManagement.vue'),
        meta: { title: '分析报告管理', requiresAdmin: true }
      },
      {
        path: '/metric-assets',
        name: 'MetricAssets',
        component: () => import('@/views/MetricAssets.vue'),
        meta: { title: '指标资产管理' }
      },
      {
        path: '/smart-data-qa',
        name: 'SmartDataQA',
        component: () => import('@/views/SmartDataQA.vue'),
        meta: { title: '智能数据问答' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)

  if (requiresAuth && !userStore.isLoggedIn()) {
    // Redirect to login if not authenticated
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && userStore.isLoggedIn()) {
    // Redirect to home if already logged in
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
