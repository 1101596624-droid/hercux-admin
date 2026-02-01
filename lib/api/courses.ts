/**
 * Courses API Client
 * Handles course listing, enrollment, and progress
 */

import { apiClient } from './client';

export interface Course {
  id: number;
  name: string;
  description: string | null;
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  instructor: string | null;
  duration_hours: number | null;
  thumbnail_url: string | null;
  is_published: boolean;
  tags: string[];
  created_at: string;
  node_count?: number;
}

export interface CourseDetail extends Course {
  nodes: Array<{
    id: number;
    node_id: string;
    type: string;
    title: string;
    description: string | null;
    sequence: number;
    parent_id: number | null;
  }>;
}

export interface CourseProgress {
  course_id: number;
  user_id: number;
  total_nodes: number;
  completed_nodes: number;
  in_progress_nodes: number;
  completion_percentage: number;
  last_accessed: string | null;
  enrolled_at: string;
}

export interface EnrollmentResponse {
  message: string;
  enrollment: {
    user_id: number;
    course_id: number;
    enrolled_at: string;
  };
}

export const coursesAPI = {
  /**
   * Get all published courses
   */
  async getCourses(): Promise<Course[]> {
    const response = await apiClient.get<{ courses: Course[] }>('/v1/courses');
    return response.courses || [];
  },

  /**
   * Get course by ID
   */
  async getCourseById(courseId: number): Promise<CourseDetail> {
    return apiClient.get<CourseDetail>(`/v1/courses/${courseId}`);
  },

  /**
   * Enroll in a course
   */
  async enrollCourse(courseId: number): Promise<EnrollmentResponse> {
    return apiClient.post<EnrollmentResponse>(`/v1/courses/${courseId}/enroll`);
  },

  /**
   * Unenroll from a course
   */
  async unenrollCourse(courseId: number): Promise<{ message: string }> {
    return apiClient.delete(`/v1/courses/${courseId}/enroll`);
  },

  /**
   * Get user's enrolled courses
   */
  async getEnrolledCourses(): Promise<Course[]> {
    const response = await apiClient.get<{ courses: Course[] }>('/v1/courses/enrolled');
    return response.courses || [];
  },

  /**
   * Get course progress for a specific course
   */
  async getCourseProgress(courseId: number): Promise<CourseProgress> {
    return apiClient.get<CourseProgress>(`/v1/courses/${courseId}/progress`);
  },

  /**
   * Get timeline (nodes) for a course
   */
  async getTimeline(courseId: number): Promise<any[]> {
    const course = await apiClient.get<CourseDetail>(`/v1/internal/ingestion/course/${courseId}`);
    return course.nodes || [];
  },

  /**
   * Search courses
   */
  async searchCourses(query: string): Promise<Course[]> {
    const response = await apiClient.get<{ courses: Course[] }>('/v1/courses/search', { q: query });
    return response.courses || [];
  },

  /**
   * Get recommended courses
   */
  async getRecommendedCourses(): Promise<Course[]> {
    const response = await apiClient.get<{ courses: Course[] }>('/v1/courses/recommended');
    return response.courses || [];
  },
};
