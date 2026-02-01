/**
 * Application-wide constants
 */

export const APP_NAME = 'hercuX'
export const APP_DESCRIPTION = '深度认知学习系统'

export const ROUTES = {
  HOME: '/',
  DASHBOARD: '/dashboard',
  COURSES: '/courses',
  WORKSTATION: '/courses/[courseId]/learn',
  ACHIEVEMENTS: '/achievements',
  TRAINING: '/training',
  PROFILE: '/profile',
  LOGIN: '/login',
  REGISTER: '/register',
} as const

export const COURSE_CATEGORIES = [
  '生物力学',
  '运动物理',
  '运动生理',
  '训练方法',
  '运动营养',
  '运动心理',
  '损伤康复',
] as const

export const COURSE_DIFFICULTIES = [
  '入门',
  '基础',
  '进阶',
  '高级',
  '专家',
] as const

export const NODE_TYPES = [
  'video',
  'simulator',
  'quiz',
  'reading',
  'exercise',
] as const

export const NODE_STATUS = [
  'locked',
  'unlocked',
  'current',
  'completed',
] as const
