/**
 * Axios request configuration
 */
import axios, { AxiosError, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

// Create axios instance
const request = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
request.interceptors.request.use(
  (config) => {
    // Add token to headers
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
request.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  (error: AxiosError) => {
    // Handle errors
    if (error.response) {
      const status = error.response.status
      const data: any = error.response.data

      switch (status) {
        case 401:
          ElMessage.error('未授权，请重新登录')
          // Clear token and redirect to login
          localStorage.removeItem('access_token')
          localStorage.removeItem('user_info')
          window.location.href = '/login'
          break
        case 403:
          ElMessage.error(data.detail || '没有权限访问')
          break
        case 404:
          ElMessage.error(data.detail || '请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误，请稍后重试')
          break
        default:
          ElMessage.error(data.detail || '请求失败')
      }
    } else if (error.request) {
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      ElMessage.error('请求配置错误')
    }

    return Promise.reject(error)
  }
)

export default request
