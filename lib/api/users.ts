/**
 * User API Client
 * Handles user profile, settings, and statistics
 */

import { apiClient } from './client';

export interface UserProfile {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  avatar_url: string | null;
  is_active: boolean;
  is_premium: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface UserSettings {
  language: string;
  theme: string;
  notifications: {
    email: boolean;
    push: boolean;
    achievement: boolean;
    course_update: boolean;
  };
  privacy: {
    show_profile: boolean;
    show_progress: boolean;
    show_achievements: boolean;
  };
  learning_preferences: {
    daily_goal_minutes: number;
    reminder_time: string;
    auto_play_next: boolean;
    playback_speed: number;
  };
}

export interface UserSummary {
  total_hours: number;
  consecutive_days: number;
  nodes_completed: number;
  active_courses: number;
}

export interface WeeklyStatistics {
  week_start: string;
  week_end: string;
  total_minutes: number;
  daily_breakdown: Array<{
    date: string;
    minutes: number;
    nodes_completed: number;
  }>;
}

export interface MonthlyStatistics {
  year: number;
  month: number;
  total_minutes: number;
  daily_breakdown: Array<{
    date: string;
    minutes: number;
    nodes_completed: number;
  }>;
}

export interface CourseProgressSummary {
  course_id: number;
  course_name: string;
  total_nodes: number;
  completed_nodes: number;
  in_progress_nodes: number;
  completion_percentage: number;
  last_accessed: string | null;
}

export interface ActiveCourse {
  courseId: number;
  courseName: string;
  nodeId: string;
  nodeTitle: string;
  lastAccessed: string | null;
  status: string;
  completionPercentage: number;
}

export const userAPI = {
  /**
   * Get user summary for dashboard
   */
  async getSummary(): Promise<UserSummary> {
    return apiClient.get<UserSummary>('/v1/user/summary');
  },

  /**
   * Get weekly learning statistics
   */
  async getWeeklyStatistics(): Promise<WeeklyStatistics> {
    return apiClient.get<WeeklyStatistics>('/v1/user/statistics/weekly');
  },

  /**
   * Get monthly learning statistics
   */
  async getMonthlyStatistics(year: number, month: number): Promise<MonthlyStatistics> {
    return apiClient.get<MonthlyStatistics>('/v1/user/statistics/monthly', { year, month });
  },

  /**
   * Get course progress summary
   */
  async getCourseProgressSummary(): Promise<{ courses: CourseProgressSummary[]; totalCourses: number }> {
    return apiClient.get('/v1/user/statistics/courses');
  },

  /**
   * Get user profile
   */
  async getProfile(): Promise<UserProfile> {
    return apiClient.get<UserProfile>('/v1/user/profile');
  },

  /**
   * Update user profile
   */
  async updateProfile(updates: { full_name?: string; avatar_url?: string }): Promise<UserProfile> {
    return apiClient.put<UserProfile>('/v1/user/profile', updates);
  },

  /**
   * Get active course (most recently accessed)
   */
  async getActiveCourse(): Promise<ActiveCourse | { message: string }> {
    return apiClient.get('/v1/user/active-course');
  },

  /**
   * Get user settings
   */
  async getSettings(): Promise<UserSettings> {
    return apiClient.get<UserSettings>('/v1/user/settings');
  },

  /**
   * Update user settings
   */
  async updateSettings(settings: Partial<UserSettings>): Promise<{ message: string; settings: UserSettings }> {
    return apiClient.put('/v1/user/settings', settings);
  },

  /**
   * Get notification settings
   */
  async getNotificationSettings(): Promise<UserSettings['notifications']> {
    return apiClient.get('/v1/user/settings/notifications');
  },

  /**
   * Update notification settings
   */
  async updateNotificationSettings(
    notifications: Partial<UserSettings['notifications']>
  ): Promise<{ message: string; notifications: UserSettings['notifications'] }> {
    return apiClient.put('/v1/user/settings/notifications', notifications);
  },

  /**
   * Get privacy settings
   */
  async getPrivacySettings(): Promise<UserSettings['privacy']> {
    return apiClient.get('/v1/user/settings/privacy');
  },

  /**
   * Update privacy settings
   */
  async updatePrivacySettings(
    privacy: Partial<UserSettings['privacy']>
  ): Promise<{ message: string; privacy: UserSettings['privacy'] }> {
    return apiClient.put('/v1/user/settings/privacy', privacy);
  },
};
