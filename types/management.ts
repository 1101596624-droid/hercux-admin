// 管理功能相关类型定义

import { User, Course, CourseProgress } from './index';

// 用户管理
export interface UserManagementFilters {
  search?: string;
  role?: 'student' | 'coach' | 'admin' | 'all';
  status?: 'active' | 'inactive' | 'banned' | 'all';
  subscription?: 'free' | 'pro' | 'team' | 'all';
  dateFrom?: string;
  dateTo?: string;
}

export interface UserManagementSort {
  field: 'name' | 'email' | 'joinDate' | 'lastLogin' | 'level';
  order: 'asc' | 'desc';
}

export interface UserListItem extends User {
  lastLoginAt?: string;
  coursesEnrolled: number;
  coursesCompleted: number;
  totalLearningHours: number;
  status: 'active' | 'inactive' | 'banned';
}

export interface UserDetailStats {
  totalCourses: number;
  completedCourses: number;
  inProgressCourses: number;
  totalLearningHours: number;
  averageScore: number;
  currentStreak: number;
  longestStreak: number;
  totalBadges: number;
  lastActive: string;
}

export interface BulkUserAction {
  action: 'activate' | 'deactivate' | 'ban' | 'delete' | 'export';
  userIds: string[];
  reason?: string;
}

// 课程管理
export interface CourseManagementFilters {
  search?: string;
  category?: string | 'all';
  difficulty?: string | 'all';
  status?: 'draft' | 'published' | 'archived' | 'all';
  instructor?: string | 'all';
  dateFrom?: string;
  dateTo?: string;
}

export interface CourseManagementSort {
  field: 'title' | 'students' | 'rating' | 'createdAt' | 'updatedAt';
  order: 'asc' | 'desc';
}

export interface CourseListItem extends Course {
  status: 'draft' | 'published' | 'archived';
  enrolledStudents: number;
  completedStudents: number;
  averageCompletionRate: number;
  averageRating: number;
  totalReviews: number;
  lastUpdated: string;
}

export interface CourseDetailStats {
  totalEnrollments: number;
  activeStudents: number;
  completedStudents: number;
  averageCompletionTime: number; // hours
  completionRate: number; // percentage
  averageScore: number;
  averageRating: number;
  totalReviews: number;
  totalRevenue: number;
}

export interface CourseFormData {
  title: string;
  subtitle?: string;
  description: string;
  category: string;
  difficulty: string;
  thumbnail?: string;
  instructorId: string;
  tags: string[];
  prerequisites: string[];
  outcomes: string[];
  estimatedDuration: number; // minutes
  price?: number;
  featured: boolean;
}

// 内容管理
export interface ContentFilters {
  search?: string;
  type?: 'video' | 'quiz' | 'reading' | 'all';
  status?: 'draft' | 'published' | 'archived' | 'all';
  courseId?: string | 'all';
  dateFrom?: string;
  dateTo?: string;
}

export interface ResourceFile {
  id: string;
  name: string;
  type: 'video' | 'image' | 'document' | 'audio';
  mimeType: string;
  size: number; // bytes
  url: string;
  cdnUrl?: string;
  thumbnail?: string;
  duration?: number; // seconds (for video/audio)
  dimensions?: { width: number; height: number }; // for images/videos
  uploadedBy: string;
  uploadedAt: string;
  usedInCourses: string[]; // course IDs
  tags: string[];
}

export interface ResourceUploadProgress {
  fileId: string;
  fileName: string;
  progress: number; // 0-100
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  error?: string;
}

export interface ContentLibraryStats {
  totalFiles: number;
  totalSize: number; // bytes
  byType: {
    video: { count: number; size: number };
    image: { count: number; size: number };
    document: { count: number; size: number };
    audio: { count: number; size: number };
  };
  storageUsed: number; // bytes
  storageLimit: number; // bytes
}

// 分页
export interface PaginationConfig {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: PaginationConfig;
}

// 批量操作结果
export interface BulkOperationResult {
  success: number;
  failed: number;
  errors: Array<{
    id: string;
    error: string;
  }>;
}

// 导出配置
export interface ExportConfig {
  format: 'csv' | 'excel' | 'json';
  fields: string[];
  filters?: Record<string, any>;
  filename?: string;
}
