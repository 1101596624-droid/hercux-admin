/**
 * Course Nodes API Client
 */

import { apiClient } from './client';
import type { TimelineNode } from '@/types/timeline';
import type { NodeProgress } from './progress';


export interface CourseNode {
  id: number;
  course_id: number;
  node_id: string;
  title: string;
  description: string | null;
  type: 'video' | 'simulator' | 'quiz' | 'reading' | 'practice';
  sequence: number;
  config: any; // JSON configuration for the node
  dependencies: string[]; // Array of node_ids that must be completed first
  unlock_conditions: any; // JSON unlock conditions
  created_at: string;
  updated_at: string | null;
}

export interface CourseNodeWithProgress extends CourseNode {
  progress: NodeProgress | null;
}

export interface CourseMapResponse {
  course_id: number;
  nodes: CourseNodeWithProgress[];
}

export interface ProgressUpdate {
  completion_percentage?: number;
  time_spent_seconds?: number;
  status?: 'in_progress' | 'completed';
}

export interface CompleteNodeResponse {
  message: string;
  newly_unlocked_nodes: string[];
}

/**
 * Get course node map with user progress
 */
export async function getCourseMap(courseId: number): Promise<TimelineNode[]> {
  const response = await apiClient.get(`/v1/nodes/course/${courseId}/map`);
  const data = response as any;

  // Transform backend data to TimelineNode format
  return data.nodes.map((node: any) => {
    let status: 'locked' | 'unlocked' | 'current' | 'completed' = 'locked';

    if (node.status === 'completed') {
      status = 'completed';
    } else if (node.status === 'in_progress') {
      status = 'current';
    } else if (node.status === 'unlocked') {
      status = 'unlocked';
    }

    // Map node type - handle 'practice' vs 'exercise'
    const nodeType = node.type === 'practice' ? 'exercise' : node.type;

    return {
      id: node.node_id,
      type: nodeType as any,
      title: node.title,
      description: undefined,
      status,
      progress: node.completion_percentage || 0,
      duration: undefined,
      sequence: node.sequence,
      dependencies: [],
      unlockConditions: node.unlock_condition || [],
      moduleId: `module-${Math.floor(node.sequence / 10)}`, // Group by sequence
      metadata: {},
    };
  });
}

/**
 * Get detailed node information
 */
export async function getNode(nodeId: string): Promise<CourseNodeWithProgress> {
  const response = await apiClient.get(`/v1/nodes/${nodeId}`);
  return response as any;
}

/**
 * Update node progress
 */
export async function updateNodeProgress(
  nodeId: string,
  update: ProgressUpdate
): Promise<NodeProgress> {
  const response = await apiClient.put(`/v1/nodes/${nodeId}/progress`, update);
  return response as any;
}

/**
 * Mark node as completed
 */
export async function completeNode(nodeId: string): Promise<CompleteNodeResponse> {
  const response = await apiClient.post(`/v1/nodes/${nodeId}/complete`);
  return response as any;
}

/**
 * Start a node (mark as in_progress if unlocked)
 */
export async function startNode(nodeId: string): Promise<NodeProgress> {
  return updateNodeProgress(nodeId, {
    status: 'in_progress',
    completion_percentage: 0,
  });
}
