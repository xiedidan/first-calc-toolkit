/**
 * 数据源管理API
 */
import axios from 'axios';

const API_BASE = '/api/v1/data-sources';

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
  const response = await axios.get(API_BASE, { params });
  return response.data.data;
};

/**
 * 创建数据源
 */
export const createDataSource = async (
  data: DataSourceCreate
): Promise<DataSource> => {
  const response = await axios.post(API_BASE, data);
  return response.data.data;
};

/**
 * 获取数据源详情
 */
export const getDataSource = async (id: number): Promise<DataSource> => {
  const response = await axios.get(`${API_BASE}/${id}`);
  return response.data.data;
};

/**
 * 更新数据源
 */
export const updateDataSource = async (
  id: number,
  data: DataSourceUpdate
): Promise<DataSource> => {
  const response = await axios.put(`${API_BASE}/${id}`, data);
  return response.data.data;
};

/**
 * 删除数据源
 */
export const deleteDataSource = async (id: number): Promise<void> => {
  await axios.delete(`${API_BASE}/${id}`);
};

/**
 * 测试数据源连接
 */
export const testDataSource = async (
  id: number
): Promise<DataSourceTestResult> => {
  const response = await axios.post(`${API_BASE}/${id}/test`);
  return response.data.data;
};

/**
 * 切换数据源启用状态
 */
export const toggleDataSource = async (
  id: number
): Promise<{ is_enabled: boolean }> => {
  const response = await axios.put(`${API_BASE}/${id}/toggle`);
  return response.data.data;
};

/**
 * 设置为默认数据源
 */
export const setDefaultDataSource = async (id: number): Promise<void> => {
  await axios.put(`${API_BASE}/${id}/set-default`);
};

/**
 * 获取连接池状态
 */
export const getPoolStatus = async (
  id: number
): Promise<DataSourcePoolStatus> => {
  const response = await axios.get(`${API_BASE}/${id}/pool-status`);
  return response.data.data;
};
