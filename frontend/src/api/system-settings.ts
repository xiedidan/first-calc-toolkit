/**
 * 系统设置API
 */
import request from '@/utils/request';

const API_BASE = '/system/settings';

export interface SystemSettings {
  current_period: string | null;
  system_name: string | null;
  version: string | null;
}

export interface SystemSettingsUpdate {
  current_period?: string;
  system_name?: string;
}

/**
 * 获取系统设置
 */
export const getSystemSettings = async (): Promise<SystemSettings> => {
  const response: any = await request.get(API_BASE);
  return response.data;
};

/**
 * 更新系统设置
 */
export const updateSystemSettings = async (
  data: SystemSettingsUpdate
): Promise<SystemSettings> => {
  const response: any = await request.put(API_BASE, data);
  return response.data;
};
