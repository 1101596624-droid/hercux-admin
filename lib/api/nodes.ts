/**
 * Course Nodes API Client
 */

import { apiClient } from './client';
import type { TimelineNode, NodeType, UnlockCondition } from '@/types/timeline';
import type { NodeProgress } from './progress';

/** Shape of a node returned from the course map API */
interface CourseMapAPINode {
  node_id: string;
  type: string;
  title: string;
  status: string;
  completion_percentage?: number;
  sequence: number;
  unlock_condition?: unknown[];
}


export interface CourseNode {
  id: number;
  course_id: number;
  node_id: string;
  title: string;
  description: string | null;
  type: 'video' | 'simulator' | 'quiz' | 'reading' | 'practice';
  sequence: number;
  config: Record<string, unknown>; // JSON configuration for the node
  dependencies: string[]; // Array of node_ids that must be completed first
  unlock_conditions: Record<string, unknown>; // JSON unlock conditions
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
  const response = await apiClient.get<{ nodes: CourseMapAPINode[] }>(`/v1/nodes/course/${courseId}/map`);

  // Transform backend data to TimelineNode format
  return response.nodes.map((node: CourseMapAPINode) => {
    let status: 'locked' | 'unlocked' | 'current' | 'completed' = 'locked';

    if (node.status === 'completed') {
      status = 'completed';
    } else if (node.status === 'in_progress') {
      status = 'current';
    } else if (node.status === 'unlocked') {
      status = 'unlocked';
    }

    // Map node type - handle 'practice' vs 'exercise'
    const nodeType = (node.type === 'practice' ? 'exercise' : node.type) as NodeType;

    const unlockConditions: UnlockCondition[] = Array.isArray(node.unlock_condition)
      ? node.unlock_condition
          .map((item): UnlockCondition | null => {
            if (!item || typeof item !== 'object') return null;
            const raw = item as Record<string, unknown>;
            const rawType = typeof raw.type === 'string' ? raw.type : '';
            const type: UnlockCondition['type'] =
              rawType === 'video_watch' || rawType === 'quiz_pass' || rawType === 'time_spent'
                ? rawType
                : 'time_spent';

            return {
              type,
              nodeId: typeof raw.nodeId === 'string' ? raw.nodeId : undefined,
              threshold: typeof raw.threshold === 'number' ? raw.threshold : undefined,
              description: typeof raw.description === 'string' ? raw.description : undefined,
            };
          })
          .filter((condition): condition is UnlockCondition => condition !== null)
      : [];

    return {
      id: node.node_id,
      type: nodeType,
      title: node.title,
      description: undefined,
      status,
      progress: node.completion_percentage || 0,
      duration: undefined,
      sequence: node.sequence,
      dependencies: [],
      unlockConditions,
      moduleId: `module-${Math.floor(node.sequence / 10)}`, // Group by sequence
      metadata: {},
    };
  });
}

/**
 * Get detailed node information
 */
export async function getNode(nodeId: string): Promise<CourseNodeWithProgress> {
  return apiClient.get<CourseNodeWithProgress>(`/v1/nodes/${nodeId}`);
}

/**
 * Update node progress
 */
export async function updateNodeProgress(
  nodeId: string,
  update: ProgressUpdate
): Promise<NodeProgress> {
  return apiClient.put<NodeProgress>(`/v1/nodes/${nodeId}/progress`, update);
}

/**
 * Mark node as completed
 */
export async function completeNode(nodeId: string): Promise<CompleteNodeResponse> {
  return apiClient.post<CompleteNodeResponse>(`/v1/nodes/${nodeId}/complete`);
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
