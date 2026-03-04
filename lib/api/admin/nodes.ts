/**
 * Admin Node Management API Client
 */

import { apiClient } from './client';

export interface NodeListItem {
  id: number;
  node_id: string;
  type: 'video' | 'assessment' | 'reading' | 'practice' | 'quiz' | 'lesson' | 'simulator';
  component_id: string;
  title: string;
  description: string | null;
  sequence: number;
  parent_id: number | null;
  timeline_config: Record<string, unknown>;
  unlock_condition: Record<string, unknown>;
  created_at: string;
  updated_at: string | null;
}

export interface NodeDetail extends NodeListItem {
  course: {
    id: number;
    name: string;
  };
  statistics: {
    total_started: number;
    total_completed: number;
    completion_rate: number;
  };
}

export interface CourseNodesResponse {
  course_id: number;
  course_name: string;
  nodes: NodeListItem[];
}

export interface NodeCreateData {
  node_id: string;
  type: 'video' | 'assessment' | 'reading' | 'practice' | 'quiz' | 'lesson' | 'simulator';
  component_id: string;
  title: string;
  description?: string;
  sequence?: number;
  parent_id?: number;
  timeline_config?: Record<string, unknown>;
  unlock_condition?: Record<string, unknown>;
}

export interface NodeUpdateData {
  node_id?: string;
  type?: 'video' | 'quiz' | 'reading' | 'practice' | 'lesson';
  component_id?: string;
  title?: string;
  description?: string;
  sequence?: number;
  parent_id?: number;
  timeline_config?: Record<string, unknown>;
  unlock_condition?: Record<string, unknown>;
}

/**
 * Get all nodes for a course
 */
export async function getCourseNodes(courseId: number): Promise<CourseNodesResponse> {
  const response = await apiClient.get(`/admin/courses/${courseId}/nodes`);
  return response.data;
}

/**
 * Get detailed node information
 */
export async function getNodeDetail(nodeId: number): Promise<NodeDetail> {
  const response = await apiClient.get(`/admin/nodes/${nodeId}`);
  return response.data;
}

/**
 * Create a new node
 */
export async function createNode(
  courseId: number,
  data: NodeCreateData
): Promise<{ message: string }> {
  const response = await apiClient.post(`/admin/courses/${courseId}/nodes`, data);
  return response.data;
}

/**
 * Update node information
 */
export async function updateNode(
  nodeId: number,
  data: NodeUpdateData
): Promise<{ message: string }> {
  const response = await apiClient.put(`/admin/nodes/${nodeId}`, data);
  return response.data;
}

/**
 * Delete a node
 */
export async function deleteNode(nodeId: number): Promise<{ message: string }> {
  const response = await apiClient.delete(`/admin/nodes/${nodeId}`);
  return response.data;
}
