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
};
