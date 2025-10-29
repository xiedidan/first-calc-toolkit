/**
 * 数据源管理API
 */
import request from '@/utils/request';

const API_BASE = '/data-sources';

export interface DataSource {
  id: number;
  name: string;
  db_type: 'postgresql' | 'mysql' | 'sqlserver' | 'oracle';
  host: string;
  port: number;
  database_name: string;
  username: string;
  password?: string;
  schema_name?: string;
  connection_params?: Record<string, any>;
  is_default: boolean;
  is_enabled: boolean;
  description?: string;
  pool_size_min: number;
  pool_size_max: number;
  pool_timeout: number;
  connection_status?: 'online' | 'offline' | 'error';
  created_at: string;
  updated_at: string;
}

export interface DataSourceCreate {
  name: string;
  db_type: 'postgresql' | 'mysql' | 'sqlserver' | 'oracle';
  host: string;
  port: number;
  database_name: string;
  username: string;
  password: string;
  schema_name?: string;
  connection_params?: Record<string, any>;
  is_default?: boolean;
  is_enabled?: boolean;
  description?: string;
  pool_size_min?: number;
  pool_size_max?: number;
  pool_timeout?: number;
}

export interface DataSourceUpdate {
  name?: string;
  host?: string;
  port?: number;
  database_name?: string;
  username?: string;
  password?: string;
  schema_name?: string;
  connection_params?: Record<string, any>;
  description?: string;
  pool_size_min?: number;
  pool_size_max?: number;
  pool_timeout?: number;
}

export interface DataSourceTestResult {
  success: boolean;
  message: string;
  duration_ms?: number;
  error?: string;
}

export interface DataSourcePoolStatus {
  pool_size: number;
  active_connections: number;
  idle_connections: number;
  waiting_requests: number;
  total_connections_created: number;
  total_connections_closed: number;
}

export interface DataSourceListParams {
  page?: number;
  size?: number;
  keyword?: string;
  db_type?: string;
  is_enabled?: boolean;
}

/**
 * 获取数据源列表
 */
export const getDataSources = async (
  params: DataSourceListParams = {}
): Promise<{ total: number; items: DataSource[] }> => {
  // request 实例的拦截器已经返回 response.data
  // 后端返回: { code: 200, message: "success", data: { total, items } }
  // 拦截器后: { code: 200, message: "success", data: { total, items } }
  const response = await request.get(API_BASE, { params });
  return response.data;
};

/**
 * 创建数据源
 */
export const createDataSource = async (
  data: DataSourceCreate
): Promise<DataSource> => {
  const response = await request.post(API_BASE, data);
  return response.data;
};

/**
 * 获取数据源详情
 */
export const getDataSource = async (id: number): Promise<DataSource> => {
  const response = await request.get(`${API_BASE}/${id}`);
  return response.data;
};

/**
 * 更新数据源
 */
export const updateDataSource = async (
  id: number,
  data: DataSourceUpdate
): Promise<DataSource> => {
  const response = await request.put(`${API_BASE}/${id}`, data);
  return response.data;
};

/**
 * 删除数据源
 */
export const deleteDataSource = async (id: number): Promise<void> => {
  await request.delete(`${API_BASE}/${id}`);
};

/**
 * 使用配置信息测试数据源连接（不保存到数据库）
 */
export const testConnectionWithConfig = async (
  config: DataSourceCreate
): Promise<DataSourceTestResult> => {
  const response = await request.post(`${API_BASE}/test-connection`, config);
  return response.data;
};

/**
 * 测试数据源连接
 */
export const testDataSource = async (
  id: number
): Promise<DataSourceTestResult> => {
  const response = await request.post(`${API_BASE}/${id}/test`);
  return response.data;
};

/**
 * 切换数据源启用状态
 */
export const toggleDataSource = async (
  id: number
): Promise<{ is_enabled: boolean }> => {
  const response = await request.put(`${API_BASE}/${id}/toggle`);
  return response.data;
};

/**
 * 设置为默认数据源
 */
export const setDefaultDataSource = async (id: number): Promise<void> => {
  await request.put(`${API_BASE}/${id}/set-default`);
};

/**
 * 获取连接池状态
 */
export const getPoolStatus = async (
  id: number
): Promise<DataSourcePoolStatus> => {
  const response = await request.get(`${API_BASE}/${id}/pool-status`);
  return response.data;
};
