/**
 * User store
 */
import { getCurrentUser, login as loginApi, logout as logoutApi, type LoginData, type RoleType, type UserInfo } from '@/api/auth'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('access_token') || '')
  const userInfo = ref<UserInfo | null>(null)

  /**
   * Login
   */
  async function login(loginData: LoginData) {
    try {
      const response = await loginApi(loginData)
      token.value = response.access_token
      localStorage.setItem('access_token', response.access_token)
      
      // Get user info after login
      await fetchUserInfo()
      
      return true
    } catch (error) {
      return false
    }
  }

  /**
   * Fetch user info
   */
  async function fetchUserInfo() {
    try {
      const info = await getCurrentUser()
      userInfo.value = info
      localStorage.setItem('user_info', JSON.stringify(info))
    } catch (error) {
      console.error('Failed to fetch user info:', error)
      throw error
    }
  }

  /**
   * Logout
   */
  function logout() {
    token.value = ''
    userInfo.value = null
    logoutApi()
  }

  /**
   * Check if user is logged in
   */
  function isLoggedIn() {
    return !!token.value
  }

  /**
   * 获取用户角色类型
   */
  const roleType = computed<RoleType | null>(() => userInfo.value?.role_type || null)

  /**
   * 检查是否是管理员或维护者
   */
  const isAdmin = computed(() => {
    const rt = userInfo.value?.role_type
    return rt === 'admin' || rt === 'maintainer'
  })

  /**
   * 检查是否是维护者
   */
  const isMaintainer = computed(() => userInfo.value?.role_type === 'maintainer')

  /**
   * 检查是否是科室用户
   */
  const isDepartmentUser = computed(() => userInfo.value?.role_type === 'department_user')

  /**
   * 检查是否是全院用户
   */
  const isHospitalUser = computed(() => userInfo.value?.role_type === 'hospital_user')

  /**
   * 获取菜单权限列表
   */
  const menuPermissions = computed(() => userInfo.value?.menu_permissions || [])

  /**
   * 检查是否有菜单权限
   */
  function hasMenuPermission(menuPath: string): boolean {
    // 管理员和维护者有所有权限
    if (isAdmin.value) return true
    
    // 普通用户（科室用户、全院用户）：完全按配置的菜单权限控制
    const permissions = userInfo.value?.menu_permissions
    if (!permissions || permissions.length === 0) {
      return false  // 没有配置权限则无法访问任何菜单
    }
    return permissions.includes(menuPath)
  }

  /**
   * Check if user has role (兼容旧代码)
   */
  function hasRole(role: string) {
    // 兼容旧的 'admin' 判断
    if (role === 'admin' || role === '系统管理员') {
      return isAdmin.value
    }
    return userInfo.value?.role_type === role || false
  }

  /**
   * Initialize from localStorage
   */
  function init() {
    const savedUserInfo = localStorage.getItem('user_info')
    if (savedUserInfo) {
      try {
        userInfo.value = JSON.parse(savedUserInfo)
      } catch (error) {
        console.error('Failed to parse user info:', error)
      }
    }
  }

  // Initialize on store creation
  init()

  return {
    token,
    userInfo,
    roleType,
    isAdmin,
    isMaintainer,
    isDepartmentUser,
    isHospitalUser,
    menuPermissions,
    login,
    logout,
    fetchUserInfo,
    isLoggedIn,
    hasRole,
    hasMenuPermission
  }
})
