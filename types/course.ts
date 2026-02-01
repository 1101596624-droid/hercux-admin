/**
 * Course-related type definitions
 */

export type CourseCategory =
  | '生物力学'
  | '运动物理'
  | '运动生理'
  | '训练方法'
  | '运动营养'
  | '运动心理'
  | '损伤康复';

export type CourseDifficulty = '入门' | '基础' | '进阶' | '高级' | '专家';

export interface Instructor {
  id: string;
  name: string;
  avatar: string;
  role: string;
  bio: string;
  specialties: string[];
  organization?: string;
}

export interface CourseModule {
  id: string;
  name: string;
  description?: string;
  nodes: number;
  completed: number;
  sequence: number;
  duration?: number; // minutes
}

export interface Course {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  category: CourseCategory;
  difficulty: CourseDifficulty;
  duration: number; // total minutes
  nodes: number; // total learning nodes
  students: number;
  rating: number;
  instructor: Instructor;
  thumbnail: string;
  tags: string[];
  progress?: number; // 0-100
  currentNode?: string; // current node display name for enrolled courses
  enrolled: boolean;
  featured: boolean;
  modules: CourseModule[];
  prerequisites: string[];
  outcomes: string[];
  createdAt?: Date;
  updatedAt?: Date;
}

export interface CourseProgress {
  courseId: string;
  userId: string;
  completedNodes: number;
  totalNodes: number;
  currentNodeId: string | null;
  lastAccessedAt: Date;
  totalTimeSpent: number; // minutes
  averageScore?: number;
}

export interface CourseEnrollment {
  courseId: string;
  userId: string;
  enrolledAt: Date;
  completedAt?: Date;
  certificateIssued: boolean;
}
