/**
 * AI-related type definitions
 */

export type AIMessageRole = 'user' | 'assistant' | 'system';

export type AIContextType = 'video' | 'quiz' | 'reading' | 'general';

export interface Reference {
  type: 'concept' | 'example' | 'exercise' | 'node';
  title: string;
  nodeId?: string;
  url?: string;
  description?: string;
}

export interface AIMessage {
  id: string;
  role: AIMessageRole;
  content: string;
  timestamp: Date;
  metadata?: {
    contextType?: AIContextType;
    contextId?: string;
    suggestions?: string[];
    references?: Reference[];
    thinking?: string; // AI's reasoning process
  };
}

export interface AIContext {
  courseId: string;
  currentNodeId: string | null;
  userProgress: number; // 0-100
  recentNodes: Array<{
    nodeId: string;
    type: string;
    completedAt: Date;
  }>;
  quizAnswers?: Record<string, any>;
  strugglingTopics?: string[];
}

export interface AIChatSession {
  id: string;
  userId: string;
  courseId: string;
  messages: AIMessage[];
  context: AIContext;
  createdAt: Date;
  updatedAt: Date;
}

export interface AIMode {
  type: 'text' | 'voice';
  enabled: boolean;
  language?: string;
}

export interface AITrainingPlan {
  id: string;
  userId: string;
  sport: string;
  phase: string;
  totalWeeks: number;
  currentWeek?: number;
  weeklyHours: number;
  todayWorkout?: string;
  primaryGoal: string;
  generatedAt: Date;
  periodization: Array<{
    phase: string;
    weeks: number[];
    color: string;
    goal: string;
  }>;
  weeklyPlans: Array<{
    week: number;
    theme: string;
    totalHours: number;
    distribution: {
      strength: number;
      endurance: number;
      speed: number;
      recovery: number;
    };
    weekGoals: string[];
    dailyFocus: string[];
  }>;
}
