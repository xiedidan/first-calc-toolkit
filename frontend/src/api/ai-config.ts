/**
 * AI接口配置API
 */
import request from '@/utils/request';

const API_BASE = '/ai-config';

export interface AIConfig {
  id: number;
  hospital_id: number;
  api_endpoint: string;
  model_name: string;
  api_key_masked: string;
  system_prompt: string | null;
  prompt_template: string;
  call_delay: number;
  daily_limit: number;
  batch_size: number;
  created_at: string;
  updated_at: string;
}

export interface AIConfigCreate {
  api_endpoint: string;
  model_name: string;
  api_key?: string;
  system_prompt?: string;
  prompt_template: string;
  call_delay?: number;
  daily_limit?: number;
  batch_size?: number;
}

export interface AIConfigUpdate {
  api_endpoint?: string;
  api_key?: string;
  prompt_template?: string;
  call_delay?: number;
  daily_limit?: number;
  batch_size?: number;
}

export interface AIConfigTestRequest {
  test_item_name: string;
}

export interface AIConfigTestResponse {
  success: boolean;
  message?: string;
  result?: {
    item_id: number;
    dimension_id: number;
    confidence: number;
  };
  duration?: number;
  error?: string;
}

export interface TestResultDisplay {
  success: boolean;
  dimension_id?: number;
  confidence?: number;
  response_time?: number;
  error?: string;
}

export interface APIUsageStats {
  today_calls: number;
  today_limit: number;
  remaining_calls: number;
  estimated_cost: number;
}

/**
 * 获取AI配置
 */
export const getAIConfig = async (): Promise<AIConfig | null> => {
  const res: any = await request.get(API_BASE);
  return res.data;
};

/**
 * 创建或更新AI配置
 */
export const createOrUpdateAIConfig = async (
  data: AIConfigCreate | AIConfigUpdate
): Promise<AIConfig> => {
  const res: any = await request.post(API_BASE, data);
  return res.data;
};

/**
 * 测试AI配置
 */
export const testAIConfig = async (
  data: AIConfigTestRequest
): Promise<AIConfigTestResponse> => {
  const res: any = await request.post(`${API_BASE}/test`, data);
  return res.data;
};

/**
 * 获取API使用统计
 */
export const getAPIUsageStats = async (): Promise<APIUsageStats> => {
  const res: any = await request.get(`${API_BASE}/usage-stats`);
  return res.data;
};
