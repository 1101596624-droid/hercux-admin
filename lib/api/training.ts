/**
 * Training API Client
 * Handles AI training plan generation and management
 */

import { apiClient } from './client';

export interface TrainingPlanRequest {
  sport: string;
  athlete_level: string;
  current_phase: string;
  weekly_hours: number;
  primary_goal: string;
  additional_context?: string;
}

export interface TrainingPlan {
  id: number;
  user_id: number;
  sport: string;
  athlete_level: string;
  current_phase: string;
  weekly_hours: number;
  primary_goal: string;
  plan_data: any; // JSON structure with weekly plans
  created_at: string;
  updated_at: string | null;
}

export interface AdjustPlanRequest {
  plan_id: number;
  adjustment_request: string;
  context?: any;
}

export const trainingAPI = {
  /**
   * Generate a new training plan using AI
   */
  async generatePlan(request: TrainingPlanRequest): Promise<TrainingPlan> {
    return apiClient.post<TrainingPlan>('/v1/ai/generate-plan', request);
  },

  /**
   * Get all training plans for current user
   */
  async getPlans(): Promise<TrainingPlan[]> {
    const response = await apiClient.get<{ plans: TrainingPlan[] }>('/v1/planner/plans');
    return response.plans || [];
  },

  /**
   * Get a specific training plan by ID
   */
  async getPlanById(planId: number): Promise<TrainingPlan> {
    return apiClient.get<TrainingPlan>(`/v1/planner/plans/${planId}`);
  },

  /**
   * Update a training plan
   */
  async updatePlan(planId: number, updates: Partial<TrainingPlanRequest>): Promise<TrainingPlan> {
    return apiClient.put<TrainingPlan>(`/v1/planner/plans/${planId}`, updates);
  },

  /**
   * Delete a training plan
   */
  async deletePlan(planId: number): Promise<{ message: string }> {
    return apiClient.delete(`/v1/planner/plans/${planId}`);
  },

  /**
   * Adjust an existing plan using AI
   */
  async adjustPlan(request: AdjustPlanRequest): Promise<TrainingPlan> {
    return apiClient.post<TrainingPlan>('/v1/ai/adjust-plan', request);
  },

  /**
   * Get plan recommendations based on user profile
   */
  async getRecommendations(): Promise<any> {
    return apiClient.get('/v1/planner/recommendations');
  },
};
