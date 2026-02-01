/**
 * Admin Learning Progress Management API Client
 */

import { apiClient } from './client';

export interface ProgressFilters {
  page?: number;
  page_size?: number;
  user_id?: number;
  course_id?: number;
  status?: 'locked' | 'unlocked' | 'in_progress' | 'completed';
  sort_by?: 'last_accessed' | 'created_at' | 'completion_percentage';
  sort_order?: 'asc' | 'desc';
}

export interface ProgressListItem {
  id: number;
  user_id: number;
  username: string;
  user_email: string;
  course_id: number;
  course_name: string;
  node_id: string;
  node_title: string;
  node_type: string;
  status: string;
  completion_percentage: number;
  time_spent_seconds: number;
  time_spent_hours: number;
  last_accessed: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface ProgressListResponse {
  items: ProgressListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ProgressDetail {
  id: number;
  user: {
    id: number;
    username: string;
    email: string;
    full_name: string | null;
    avatar_url: string | null;
  };
  course: {
    id: number;
    name: string;
    description: string | null;
    difficulty: string;
  };
  node: {
    id: number;
    node_id: string;
    title: string;
    description: string | null;
    type: string;
    sequence: number;
  };
  status: string;
  completion_percentage: number;
  time_spent_seconds: number;
  time_spent_hours: number;
  last_accessed: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface CourseProgressOverview {
  course_id: number;
  course_name: string;
  enrolled_users: number;
  total_nodes: number;
  node_statistics: Array<{
    node_id: string;
    title: string;
    type: string;
    sequence: number;
    started_count: number;
    completed_count: number;
    completion_rate: number;
    avg_completion_percentage: number;
    avg_time_hours: number;
  }>;
}

export interface UserProgressOverview {
  user_id: number;
  username: string;
  email: string;
  course_progress: Array<{
    course_id: number;
    course_name: string;
    difficulty: string;
    enrolled_at: string;
    last_accessed: string | null;
    total_nodes: number;
    started_nodes: number;
    completed_nodes: number;
    completion_rate: number;
    time_spent_hours: number;
  }>;
  total_courses: number;
}

/**
 * Get paginated list of progress records with filters
 */
export async function getProgress(filters: ProgressFilters = {}): Promise<ProgressListResponse> {
  const params = new URLSearchParams();

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      params.append(key, String(value));
    }
  });

  const response = await apiClient.get(`/admin/progress?${params.toString()}`);
  return response.data;
}

/**
 * Get detailed progress information
 */
export async function getProgressDetail(progressId: number): Promise<ProgressDetail> {
  const response = await apiClient.get(`/admin/progress/${progressId}`);
  return response.data;
}

/**
 * Update progress information
 */
export async function updateProgress(
  progressId: number,
  data: {
    status?: 'locked' | 'unlocked' | 'in_progress' | 'completed';
    completion_percentage?: number;
  }
): Promise<{ message: string }> {
  const params = new URLSearchParams();

  if (data.status !== undefined) params.append('status', data.status);
  if (data.completion_percentage !== undefined) params.append('completion_percentage', String(data.completion_percentage));

  const response = await apiClient.put(`/admin/progress/${progressId}?${params.toString()}`);
  return response.data;
}

/**
 * Delete a progress record
 */
export async function deleteProgress(progressId: number): Promise<{ message: string }> {
  const response = await apiClient.delete(`/admin/progress/${progressId}`);
  return response.data;
}

/**
 * Get course progress overview
 */
export async function getCourseProgressOverview(courseId: number): Promise<CourseProgressOverview> {
  const response = await apiClient.get(`/admin/progress/course/${courseId}/overview`);
  return response.data;
}

/**
 * Get user progress overview
 */
export async function getUserProgressOverview(userId: number): Promise<UserProgressOverview> {
  const response = await apiClient.get(`/admin/progress/user/${userId}/overview`);
  return response.data;
}
