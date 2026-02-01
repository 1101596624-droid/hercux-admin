// 管理后台相关类型定义

export type AdminRole = 'super_admin' | 'admin' | 'moderator';

// 管理员等级: 1=超级管理员(所有权限), 2=高级管理员(不能删除课程), 3=普通管理员(只能查看和生成)
export type AdminLevel = 1 | 2 | 3;

export type AdminPermission =
  | 'users.view'
  | 'users.create'
  | 'users.edit'
  | 'users.delete'
  | 'courses.view'
  | 'courses.create'
  | 'courses.edit'
  | 'courses.delete'
  | 'courses.publish'
  | 'content.view'
  | 'content.create'
  | 'content.edit'
  | 'content.delete'
  | 'analytics.view'
  | 'analytics.export'
  | 'system.view'
  | 'system.edit'
  | 'permissions.manage'
  | 'admins.manage';

// 各等级管理员的权限配置
export const ADMIN_LEVEL_PERMISSIONS: Record<AdminLevel, AdminPermission[]> = {
  1: [
    'users.view', 'users.create', 'users.edit', 'users.delete',
    'courses.view', 'courses.create', 'courses.edit', 'courses.delete', 'courses.publish',
    'content.view', 'content.create', 'content.edit', 'content.delete',
    'analytics.view', 'analytics.export',
    'system.view', 'system.edit',
    'permissions.manage', 'admins.manage'
  ],
  2: [
    'users.view', 'users.create', 'users.edit', 'users.delete',
    'courses.view', 'courses.create', 'courses.edit', 'courses.publish',
    'content.view', 'content.create', 'content.edit', 'content.delete',
    'analytics.view', 'analytics.export',
    'system.view'
  ],
  3: [
    'users.view',
    'courses.view', 'courses.create',
    'content.view', 'content.create',
    'analytics.view'
  ]
};

export const ADMIN_LEVEL_NAMES: Record<AdminLevel, string> = {
  1: '超级管理员',
  2: '高级管理员',
  3: '普通管理员'
};

export const ADMIN_LEVEL_DESCRIPTIONS: Record<AdminLevel, string> = {
  1: '拥有所有权限，可以管理其他管理员账号',
  2: '拥有大部分权限，但不能删除课程',
  3: '只能查看数据和生成课程，不能删除或上下架课程'
};

export interface AdminUser {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: AdminRole;
  level: AdminLevel;
  permissions: AdminPermission[];
  createdAt: string;
  lastLoginAt?: string;
  isActive: boolean;
}

export interface AdminAuthState {
  user: AdminUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface AdminLoginRequest {
  email: string;
  password: string;
}

export interface AdminLoginResponse {
  user: AdminUser;
  token: string;
  expiresAt: string;
}

// 系统日志
export type LogLevel = 'info' | 'warn' | 'error' | 'debug';
export type LogType = 'operation' | 'error' | 'security' | 'system';

export interface SystemLog {
  id: string;
  type: LogType;
  level: LogLevel;
  message: string;
  userId?: string;
  userName?: string;
  action?: string;
  resource?: string;
  resourceId?: string;
  ip?: string;
  userAgent?: string;
  metadata?: Record<string, any>;
  timestamp: string;
}

// 系统设置
export interface SystemSettings {
  siteName: string;
  siteDescription: string;
  logo?: string;
  favicon?: string;
  contactEmail: string;
  supportEmail: string;
  maintenanceMode: boolean;
  registrationEnabled: boolean;
  emailVerificationRequired: boolean;
  maxUploadSize: number; // MB
  allowedFileTypes: string[];
  apiRateLimit: number; // requests per minute
  sessionTimeout: number; // minutes
}

// 权限角色
export interface Role {
  id: string;
  name: string;
  displayName: string;
  description: string;
  permissions: AdminPermission[];
  isSystem: boolean; // 系统角色不可删除
  createdAt: string;
  updatedAt: string;
}

// 权限定义
export interface PermissionDefinition {
  key: AdminPermission;
  name: string;
  description: string;
  category: 'users' | 'courses' | 'content' | 'analytics' | 'system' | 'permissions';
}

// 系统状态
export interface SystemStatus {
  status: 'healthy' | 'degraded' | 'down';
  uptime: number; // seconds
  version: string;
  database: {
    status: 'connected' | 'disconnected';
    responseTime: number; // ms
  };
  redis: {
    status: 'connected' | 'disconnected';
    responseTime: number; // ms
  };
  storage: {
    total: number; // bytes
    used: number; // bytes
    available: number; // bytes
  };
  api: {
    requestsPerMinute: number;
    averageResponseTime: number; // ms
    errorRate: number; // percentage
  };
}

// 快捷操作
export interface QuickAction {
  id: string;
  label: string;
  icon: string;
  href: string;
  color?: string;
  count?: number;
}

// 最近活动
export interface RecentActivity {
  id: string;
  type: 'user_registered' | 'course_created' | 'course_published' | 'user_banned' | 'content_uploaded';
  title: string;
  description: string;
  userId?: string;
  userName?: string;
  userAvatar?: string;
  timestamp: string;
  metadata?: Record<string, any>;
}
