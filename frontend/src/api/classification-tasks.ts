/**
 * 分类任务API
 */
import request from '@/utils/request';

const API_BASE = '/classification-tasks';

export interface ClassificationTask {
  id: number;
  hospital_id: number;
  task_name: string;
  model_version_id: number;
  charge_categories: string[];
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'paused';
  total_items: number;
  processed_items: number;
  failed_items: number;
  celery_task_id: string | null;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface ClassificationTaskCreate {
  task_name: string;
  model_version_id: number;
  charge_categories: string[];
}

export interface TaskProgress {
  task_id: number;
  status: string;
  total_items: number;
  processed_items: number;
  failed_items: number;
  progress_percentage: number;
}

export interface TaskLog {
  id: number;
  task_id: number;
  charge_item_id: number;
  charge_item_name: string;
  status: string;
  error_message: string | null;
  processed_at: string | null;
}

/**
 * 获取任务列表
 */
export const getClassificationTasks = async (): Promise<ClassificationTask[]> => {
  const res: any = await request.get(API_BASE);
  return res.data?.items || [];
};

/**
 * 创建分类任务
 */
export const createClassificationTask = async (
  data: ClassificationTaskCreate
): Promise<ClassificationTask> => {
  const res: any = await request.post(API_BASE, data, {
    timeout: 60000  // 创建任务可能需要更长时间，设置60秒超时
  });
  return res.data;
};

/**
 * 获取任务详情
 */
export const getClassificationTask = async (id: number): Promise<ClassificationTask> => {
  const res: any = await request.get(`${API_BASE}/${id}`);
  return res.data;
};

/**
 * 更新任务
 */
export const updateClassificationTask = async (id: number, data: { task_name: string }): Promise<ClassificationTask> => {
  const res: any = await request.put(`${API_BASE}/${id}`, data);
  return res.data;
};

/**
 * 删除任务
 */
export const deleteClassificationTask = async (id: number): Promise<void> => {
  await request.delete(`${API_BASE}/${id}`);
};

/**
 * 继续处理任务
 */
export const continueClassificationTask = async (id: number): Promise<ClassificationTask> => {
  const res: any = await request.post(`${API_BASE}/${id}/continue`);
  return res.data;
};

/**
 * 获取任务进度
 */
export const getTaskProgress = async (id: number): Promise<TaskProgress> => {
  const res: any = await request.get(`${API_BASE}/${id}/progress`);
  return res.data;
};

/**
 * 获取任务日志
 */
export const getTaskLogs = async (id: number): Promise<TaskLog[]> => {
  const res: any = await request.get(`${API_BASE}/${id}/logs`);
  return res.data?.logs || [];
};

/**
 * 获取收费类别列表
 */
export const getChargeCategories = async (): Promise<string[]> => {
  const res: any = await request.get(`${API_BASE}/charge-categories`);
  return res.data || [];
};
