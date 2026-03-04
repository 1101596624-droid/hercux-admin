/**
 * Simulator API - 模拟器相关 API
 */

import { apiClient } from './client';

interface VariableSpec {
  name: string;
  min?: number;
  max?: number;
  default?: number;
}

interface GenerateCodeResponse {
  custom_code: string;
  variables: Array<{
    name: string;
    label?: string;
    min?: number;
    max?: number;
    default?: number;
    step?: number;
  }>;
  name: string;
  description: string;
}

export type GenerateTaskState = 'queued' | 'running' | 'succeeded' | 'failed' | 'canceled';

interface GenerateCodeTaskCreateResponse {
  task_id: string;
  status: GenerateTaskState;
  queue_depth: number;
  retry_of?: string;
}

interface GenerateCodeTaskStatusResponse {
  task_id: string;
  status: GenerateTaskState;
  created_at: string;
  started_at?: string;
  finished_at?: string;
  current_stage?: string;
  stage_message?: string;
  stage_updated_at?: string;
  stage_history?: Array<{
    stage: string;
    at: string;
    message?: string;
    meta?: Record<string, unknown>;
  }>;
  queue_wait_seconds?: number;
  running_seconds?: number;
  total_elapsed_seconds?: number;
  cancel_requested_at?: string;
  result?: GenerateCodeResponse;
  error_code?: string;
  error_message?: string;
}

export const simulatorAPI = {
  /**
   * AI 生成模拟器代码
   */
  async generateCode(prompt: string, variables?: VariableSpec[]): Promise<GenerateCodeResponse> {
    const { data } = await apiClient.post<GenerateCodeResponse>('/simulator/generate-code', {
      prompt,
      variables,
    });
    return data;
  },

  /**
   * 创建 AI 模拟器代码异步任务
   */
  async createGenerateTask(prompt: string, variables?: VariableSpec[]): Promise<GenerateCodeTaskCreateResponse> {
    const { data } = await apiClient.post<GenerateCodeTaskCreateResponse>('/simulator/generate-code/tasks', {
      prompt,
      variables,
    });
    return data;
  },

  /**
   * 查询 AI 模拟器代码异步任务状态
   */
  async getGenerateTaskStatus(taskId: string): Promise<GenerateCodeTaskStatusResponse> {
    const { data } = await apiClient.get<GenerateCodeTaskStatusResponse>(`/simulator/generate-code/tasks/${taskId}`);
    return data;
  },

  /**
   * 取消 AI 模拟器代码异步任务
   */
  async cancelGenerateTask(taskId: string): Promise<GenerateCodeTaskStatusResponse> {
    const { data } = await apiClient.post<GenerateCodeTaskStatusResponse>(`/simulator/generate-code/tasks/${taskId}/cancel`);
    return data;
  },

  /**
   * 重试已结束的 AI 模拟器异步任务
   */
  async retryGenerateTask(taskId: string): Promise<GenerateCodeTaskCreateResponse> {
    const { data } = await apiClient.post<GenerateCodeTaskCreateResponse>(`/simulator/generate-code/tasks/${taskId}/retry`);
    return data;
  },
};
