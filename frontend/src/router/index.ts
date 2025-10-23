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
