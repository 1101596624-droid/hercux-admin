/**
 * Admin Course Management API Client
 */

import { apiClient } from './client';

export interface CourseFilters {
  page?: number;
  page_size?: number;
  search?: string;
  difficulty?: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  is_published?: boolean;
  instructor?: string;
  sort_by?: 'created_at' | 'name' | 'duration_hours';
  sort_order?: 'asc' | 'desc';
}

export interface CourseListItem {
  id: number;
  name: string;
  description: string | null;
  difficulty: string;
  instructor: string | null;
  duration_hours: number | null;
  thumbnail_url: string | null;
  is_published: boolean;
  tags: string[];
  created_at: string;
  total_nodes: number;
  enrolled_users: number;
}

export interface CourseListResponse {
  items: CourseListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CourseDetail {
  id: number;
  name: string;
  description: string | null;
  difficulty: string;
  instructor: string | null;
  duration_hours: number | null;
  thumbnail_url: string | null;
  is_published: boolean;
  tags: string[];
  created_at: string;
  statistics: {
    total_nodes: number;
    enrolled_users: number;
    completion_rate: number;
    recent_enrollments: number;
    total_completions: number;
  };
  nodes: Array<{
    id: number;
    node_id: string;
    type: string;
    title: string;
    sequence: number;
    parent_id: number | null;
  }>;
}

export interface CourseFormData {
  name: string;
  description?: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  instructor?: string;
  duration_hours?: number;
  tags?: string[];
  thumbnail_url?: string;
}

export interface CourseStatistics {
  course_id: number;
  course_name: string;
  monthly_enrollments: Array<{
    month: string;
    enrollments: number;
  }>;
  node_completion_rates: Array<{
    node_id: string;
    title: string;
    type: string;
    started: number;
    completed: number;
    completion_rate: number;
  }>;
}

/**
 * Get paginated list of courses with filters
 */
export async function getCourses(filters: CourseFilters = {}): Promise<CourseListResponse> {
  const params = new URLSearchParams();

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      params.append(key, String(value));
    }
  });

  const response = await apiClient.get(`/admin/courses?${params.toString()}`);
  return response.data;
}

/**
 * Get detailed course information
 */
export async function getCourseDetail(courseId: number): Promise<CourseDetail> {
  const response = await apiClient.get(`/admin/courses/${courseId}`);
  return response.data;
}

/**
 * Create a new course
 */
export async function createCourse(data: CourseFormData): Promise<{ id: number; message: string }> {
  const response = await apiClient.post('/admin/courses', data);
  return response.data;
}

/**
 * Update course information
 */
export async function updateCourse(
  courseId: number,
  data: Partial<CourseFormData>
): Promise<{ message: string }> {
  const response = await apiClient.put(`/admin/courses/${courseId}`, data);
  return response.data;
}

/**
 * Delete a course
 */
export async function deleteCourse(courseId: number): Promise<{ message: string }> {
  const response = await apiClient.delete(`/admin/courses/${courseId}`);
  return response.data;
}

/**
 * Publish or unpublish a course
 */
export async function publishCourse(
  courseId: number,
  publish: boolean = true
): Promise<{ message: string; is_published: boolean }> {
  const response = await apiClient.post(`/admin/courses/${courseId}/publish`, null, {
    params: { publish }
  });
  return response.data;
}

/**
 * Get course statistics
 */
export async function getCourseStatistics(courseId: number): Promise<CourseStatistics> {
  const response = await apiClient.get(`/admin/courses/${courseId}/statistics`);
  return response.data;
}

// ============================================
// Export API (always use real API)
// ============================================

export const coursesAPI = {
  getCourses,
  getCourseDetail,
  createCourse,
  updateCourse,
  deleteCourse,
  publishCourse,
  getCourseStatistics,
};
