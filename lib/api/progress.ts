/**
 * Progress API Client
 * Handles node progress tracking and completion
 */

import { apiClient } from './client';

export interface NodeProgress {
  id: number;
  user_id: number;
  node_id: number;
  status: 'not_started' | 'in_progress' | 'completed';
  completion_percentage: number;
  time_spent_seconds: number;
  last_accessed: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface UpdateProgressRequest {
  completion_percentage: number;
  status?: 'not_started' | 'in_progress' | 'completed';
  time_spent_seconds?: number;
}

export interface CompleteNodeRequest {
  time_spent_seconds?: number;
  result_data?: any;
}

export const progressAPI = {
  /**
   * Get progress for a specific node
   */
  async getNodeProgress(nodeId: number): Promise<NodeProgress> {
    return apiClient.get<NodeProgress>(`/v1/progress/node/${nodeId}`);
  },

  /**
   * Update progress for a node
   */
  async updateNodeProgress(nodeId: number, data: UpdateProgressRequest): Promise<NodeProgress> {
    return apiClient.put<NodeProgress>(`/v1/nodes/${nodeId}/progress`, data);
  },

  /**
   * Mark a node as completed
   */
  async completeNode(nodeId: number, data?: CompleteNodeRequest): Promise<{
    message: string;
    progress: NodeProgress;
    unlocked_nodes: string[];
  }> {
    return apiClient.post(`/v1/nodes/${nodeId}/complete`, data);
  },

  /**
   * Get all progress for current user
   */
  async getAllProgress(): Promise<NodeProgress[]> {
    const response = await apiClient.get<{ progress: NodeProgress[] }>('/v1/progress');
    return response.progress || [];
  },

  /**
   * Get progress for a specific course
   */
  async getCourseProgress(courseId: number): Promise<NodeProgress[]> {
    const response = await apiClient.get<{ progress: NodeProgress[] }>(`/v1/progress/course/${courseId}`);
    return response.progress || [];
  },

  /**
   * Reset progress for a node
   */
  async resetNodeProgress(nodeId: number): Promise<{ message: string }> {
    return apiClient.delete(`/v1/progress/node/${nodeId}`);
  },
};
