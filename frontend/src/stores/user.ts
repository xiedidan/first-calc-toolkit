/**
 * User store
 */
import { getCurrentUser, login as loginApi, logout as logoutApi, type LoginData, type UserInfo } from '@/api/auth'
import { defineStore } from 'pinia'
import { ref } from 'vue'

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
   * Check if user has role
   */
  function hasRole(role: string) {
    return userInfo.value?.roles?.includes(role) || false
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
    login,
    logout,
    fetchUserInfo,
    isLoggedIn,
    hasRole
  }
})
