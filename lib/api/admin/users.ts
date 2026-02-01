/**
 * Admin User Management API Client
 */

import { apiClient } from './client';

export interface UserFilters {
  page?: number;
  page_size?: number;
  search?: string;
  is_active?: boolean;
  is_premium?: boolean;
  sort_by?: 'created_at' | 'username' | 'email';
  sort_order?: 'asc' | 'desc';
}

export interface UserListItem {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  is_active: boolean;
  is_premium: boolean;
  created_at: string;
  enrolled_courses: number;
  completed_nodes: number;
  total_time_hours: number;
  last_activity: string | null;
}

export interface UserListResponse {
  items: UserListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CourseProgress {
  course_id: number;
  course_name: string;
  enrolled_at: string;
  last_accessed: string | null;
  is_favorite: boolean;
  total_nodes: number;
  completed_nodes: number;
  completion_rate: number;
}

export interface Achievement {
  badge_id: string;
  badge_name: string;
  badge_description: string | null;
  rarity: string | null;
  icon_url: string | null;
  unlocked_at: string;
}

export interface DailyStatistic {
  date: string;
  total_time_seconds: number;
  nodes_completed: number;
  streak_days: number;
}

export interface UserDetail {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  is_active: boolean;
  is_premium: boolean;
  created_at: string;
  updated_at: string | null;
  statistics: {
    enrolled_courses: number;
    completed_nodes: number;
    total_time_hours: number;
    current_streak: number;
    achievements_count: number;
  };
  enrolled_courses: CourseProgress[];
  achievements: Achievement[];
  daily_statistics: DailyStatistic[];
}

export interface UserStatistics {
  user_id: number;
  username: string;
  daily_statistics: DailyStatistic[];
  course_progress: Array<{
    course_id: number;
    course_name: string;
    total_nodes: number;
    completed_nodes: number;
    completion_rate: number;
    time_spent_hours: number;
  }>;
}

/**
 * Get paginated list of users with filters
 */
export async function getUsers(filters: UserFilters = {}): Promise<UserListResponse> {
  const params = new URLSearchParams();

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      params.append(key, String(value));
    }
  });

  const response = await apiClient.get(`/admin/users?${params.toString()}`);
  return response.data;
}

/**
 * Get detailed user information
 */
export async function getUserDetail(userId: number): Promise<UserDetail> {
  const response = await apiClient.get(`/admin/users/${userId}`);
  return response.data;
}

/**
 * Update user information
 */
export async function updateUser(
  userId: number,
  data: {
    full_name?: string;
    is_active?: boolean;
    is_premium?: boolean;
  }
): Promise<{ message: string }> {
  const params = new URLSearchParams();

  if (data.full_name !== undefined) params.append('full_name', data.full_name);
  if (data.is_active !== undefined) params.append('is_active', String(data.is_active));
  if (data.is_premium !== undefined) params.append('is_premium', String(data.is_premium));

  const response = await apiClient.put(`/admin/users/${userId}?${params.toString()}`);
  return response.data;
}

/**
 * Delete a user
 */
export async function deleteUser(userId: number): Promise<{ message: string }> {
  const response = await apiClient.delete(`/admin/users/${userId}`);
  return response.data;
}

/**
 * Get user statistics
 */
export async function getUserStatistics(
  userId: number,
  days: number = 30
): Promise<UserStatistics> {
  const response = await apiClient.get(`/admin/users/${userId}/statistics?days=${days}`);
  return response.data;
}
