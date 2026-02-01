/**
 * API Configuration Management
 * 管理所有 API 配置（API Key、Base URL、端口等）
 */

import { apiClient } from './client';

// 类型定义
export interface APIConfigItem {
  key: string;
  name: string;
  description: string;
  category: string;
  value: string;
  masked_value: string;
  is_secret: boolean;
  is_configured: boolean;
}

export interface APIConfigCategory {
  name: string;
  description: string;
  items: APIConfigItem[];
}

export interface APIConfigResponse {
  categories: APIConfigCategory[];
  env_file_path: string;
}

export interface UpdateAPIConfigRequest {
  key: string;
  value: string;
}

export interface TestAPIResponse {
  success: boolean;
  message: string;
}

/**
 * 获取所有 API 配置
 */
export async function getAPIConfig(): Promise<APIConfigResponse> {
  const { data } = await apiClient.get<APIConfigResponse>('/admin/api-config');
  return data;
}

/**
 * 更新 API 配置
 */
export async function updateAPIConfig(request: UpdateAPIConfigRequest): Promise<{ success: boolean; message: string; note: string }> {
  const { data } = await apiClient.put<{ success: boolean; message: string; note: string }>('/admin/api-config', request);
  return data;
}

/**
 * 测试 API 连接
 */
export async function testAPIConnection(category: string): Promise<TestAPIResponse> {
  const { data } = await apiClient.post<TestAPIResponse>(`/admin/api-config/test/${category}`);
  return data;
}
