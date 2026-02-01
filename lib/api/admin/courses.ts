/**
 * Admin Course Management API Client
 */

import { apiClient } from './client';

// ============================================
// Mock Data (for development) - 清空演示数据
// ============================================

const MOCK_DELAY = 300;

const mockCourses: CourseListItem[] = [];

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
// Mock API Functions (for development)
// ============================================

async function mockGetCourses(filters: CourseFilters = {}): Promise<CourseListResponse> {
  await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY));

  let filtered = [...mockCourses];

  // Apply filters
  if (filters.search) {
    const search = filters.search.toLowerCase();
    filtered = filtered.filter(
      (c) =>
        c.name.toLowerCase().includes(search) ||
        c.description?.toLowerCase().includes(search)
    );
  }

  if (filters.difficulty) {
    filtered = filtered.filter((c) => c.difficulty === filters.difficulty);
  }

  if (filters.is_published !== undefined) {
    filtered = filtered.filter((c) => c.is_published === filters.is_published);
  }

  // Apply sorting
  const sortBy = filters.sort_by || 'created_at';
  const sortOrder = filters.sort_order || 'desc';
  filtered.sort((a, b) => {
    let aVal = a[sortBy as keyof CourseListItem];
    let bVal = b[sortBy as keyof CourseListItem];
    if (typeof aVal === 'string') aVal = aVal.toLowerCase();
    if (typeof bVal === 'string') bVal = bVal.toLowerCase();
    if (aVal === null) return 1;
    if (bVal === null) return -1;
    if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1;
    return 0;
  });

  // Apply pagination
  const page = filters.page || 1;
  const pageSize = filters.page_size || 20;
  const start = (page - 1) * pageSize;
  const items = filtered.slice(start, start + pageSize);

  return {
    items,
    total: filtered.length,
    page,
    page_size: pageSize,
    total_pages: Math.ceil(filtered.length / pageSize),
  };
}

async function mockGetCourseDetail(courseId: number): Promise<CourseDetail> {
  await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY));
  const course = mockCourses.find((c) => c.id === courseId);
  if (!course) {
    throw new Error('Course not found');
  }
  return {
    ...course,
    statistics: {
      total_nodes: course.total_nodes,
      enrolled_users: course.enrolled_users,
      completion_rate: 0.65,
      recent_enrollments: 12,
      total_completions: Math.floor(course.enrolled_users * 0.65),
    },
    nodes: [
      { id: 1, node_id: 'node-1', type: 'video', title: '课程介绍', sequence: 1, parent_id: null },
      { id: 2, node_id: 'node-2', type: 'text', title: '基础概念', sequence: 2, parent_id: null },
      { id: 3, node_id: 'node-3', type: 'quiz', title: '章节测验', sequence: 3, parent_id: null },
    ],
  };
}

async function mockCreateCourse(data: CourseFormData): Promise<{ id: number; message: string }> {
  await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY));
  const newId = Math.max(...mockCourses.map((c) => c.id)) + 1;
  mockCourses.push({
    id: newId,
    name: data.name,
    description: data.description || null,
    difficulty: data.difficulty,
    instructor: data.instructor || null,
    duration_hours: data.duration_hours || null,
    thumbnail_url: data.thumbnail_url || null,
    is_published: false,
    tags: data.tags || [],
    created_at: new Date().toISOString(),
    total_nodes: 0,
    enrolled_users: 0,
  });
  return { id: newId, message: '课程创建成功' };
}

async function mockUpdateCourse(
  courseId: number,
  data: Partial<CourseFormData>
): Promise<{ message: string }> {
  await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY));
  const index = mockCourses.findIndex((c) => c.id === courseId);
  if (index === -1) {
    throw new Error('Course not found');
  }
  mockCourses[index] = { ...mockCourses[index], ...data };
  return { message: '课程更新成功' };
}

async function mockDeleteCourse(courseId: number): Promise<{ message: string }> {
  await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY));
  const index = mockCourses.findIndex((c) => c.id === courseId);
  if (index === -1) {
    throw new Error('Course not found');
  }
  mockCourses.splice(index, 1);
  return { message: '课程删除成功' };
}

async function mockPublishCourse(
  courseId: number,
  publish: boolean = true
): Promise<{ message: string; is_published: boolean }> {
  await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY));
  const course = mockCourses.find((c) => c.id === courseId);
  if (!course) {
    throw new Error('Course not found');
  }
  course.is_published = publish;
  return {
    message: publish ? '课程已发布' : '课程已取消发布',
    is_published: publish,
  };
}

async function mockGetCourseStatistics(courseId: number): Promise<CourseStatistics> {
  await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY));
  const course = mockCourses.find((c) => c.id === courseId);
  if (!course) {
    throw new Error('Course not found');
  }
  return {
    course_id: courseId,
    course_name: course.name,
    monthly_enrollments: [
      { month: '2024-01', enrollments: 15 },
      { month: '2024-02', enrollments: 22 },
      { month: '2024-03', enrollments: 18 },
    ],
    node_completion_rates: [
      { node_id: 'node-1', title: '课程介绍', type: 'video', started: 100, completed: 95, completion_rate: 0.95 },
      { node_id: 'node-2', title: '基础概念', type: 'text', started: 90, completed: 80, completion_rate: 0.89 },
      { node_id: 'node-3', title: '章节测验', type: 'quiz', started: 75, completed: 60, completion_rate: 0.80 },
    ],
  };
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
