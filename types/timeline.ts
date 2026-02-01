/**
 * Timeline and learning path type definitions
 */

export type NodeType = 'video' | 'quiz' | 'reading' | 'exercise' | 'lesson' | 'practice';

export type NodeStatus = 'locked' | 'unlocked' | 'current' | 'completed';

export interface UnlockCondition {
  type: 'video_watch' | 'quiz_pass' | 'time_spent';
  nodeId?: string;
  threshold?: number; // percentage for video, score for quiz, etc.
  description?: string;
}

export interface TimelineNode {
  id: string;
  type: NodeType;
  title: string;
  description?: string;
  duration?: number; // minutes
  status: NodeStatus;
  progress: number; // 0-100
  moduleId: string;
  sequence: number;
  dependencies: string[]; // node IDs that must be completed first
  unlockConditions: UnlockCondition[];
  metadata?: {
    videoUrl?: string;
    quizId?: string;
  };
}

export interface NodeState {
  nodeId: string;
  unlocked: boolean;
  progress: number;
  attempts: number;
  score?: number;
  completedAt?: Date;
  lastAccessedAt?: Date;
  timeSpent: number; // minutes
}

export interface TimelineState {
  courseId: string;
  currentNodeId: string | null;
  completedNodeIds: string[];
  nodeStates: Record<string, NodeState>;
  lastUpdatedAt: Date;
}

export interface LearningPath {
  id: string;
  courseId: string;
  name: string;
  nodes: TimelineNode[];
  totalDuration: number;
  estimatedCompletionTime: number;
}
