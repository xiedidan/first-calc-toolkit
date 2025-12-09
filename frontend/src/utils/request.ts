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
    
    // Add hospital ID to headers (for business APIs)
    const hospitalId = localStorage.getItem('currentHospitalId')
    if (hospitalId) {
      config.headers['X-Hospital-ID'] = hospitalId
    }
    
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Track if we're already redirecting to avoid multiple redirects
let isRedirecting = false

// Response interceptor
request.interceptors.response.use(
  (response: AxiosResponse) => {
    // For blob responses, return the full response to preserve headers
    if (response.config.responseType === 'blob') {
      return response
    }
    return response.data
  },
  (error: AxiosError) => {
    // Handle errors
    if (error.response) {
      const status = error.response.status
      const data: any = error.response.data

      switch (status) {
        case 400:
          // Handle hospital not activated error
          if (data.detail && data.detail.includes('激活医疗机构')) {
            ElMessage.warning('请先选择医疗机构')
          } else {
            ElMessage.error(data.detail || '请求参数错误')
          }
          break
        case 401:
          // Only show message and redirect once
          if (!isRedirecting) {
            isRedirecting = true
            ElMessage.error('登录已过期，请重新登录')
            // Clear token and redirect to login
            localStorage.removeItem('access_token')
            localStorage.removeItem('user_info')
            localStorage.removeItem('currentHospitalId')
            localStorage.removeItem('currentHospital')
            // Use setTimeout to avoid multiple redirects
            setTimeout(() => {
              window.location.href = '/login'
            }, 500)
          }
          break
        case 403:
          // Handle hospital access denied error
          if (data.detail && data.detail.includes('医疗机构')) {
            ElMessage.error('您没有权限访问该医疗机构')
          } else {
            ElMessage.error(data.detail || '没有权限访问')
          }
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
