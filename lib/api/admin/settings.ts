/**
 * System Settings API
 * 系统设置管理
 */

import { apiClient } from './client';

// ============ 类型定义 ============

export interface PlatformSettings {
  platform_name: string;
  platform_description: string;
  logo_url: string | null;
  announcement: string | null;
  announcement_enabled: boolean;
  maintenance_mode: boolean;
  maintenance_message: string;
}

export interface CourseDefaultSettings {
  default_difficulty: string;
  default_tags: string[];
  ai_generation_steps: number;
  ai_content_min_length: number;
  auto_publish: boolean;
  require_review: boolean;
}

export interface UserSettings {
  allow_registration: boolean;
  default_user_role: string;
  login_fail_lock_threshold: number;
  login_fail_lock_minutes: number;
  session_timeout_minutes: number;
  require_email_verification: boolean;
}

export interface StorageSettings {
  max_upload_size_mb: number;
  allowed_image_types: string[];
  allowed_video_types: string[];
  allowed_document_types: string[];
  storage_path: string;
  auto_cleanup_days: number;
}

export interface LogSettings {
  log_level: string;
  log_retention_days: number;
  enable_access_log: boolean;
  enable_error_log: boolean;
}

export interface AllSettings {
  platform: PlatformSettings;
  course: CourseDefaultSettings;
  user: UserSettings;
  storage: StorageSettings;
  log: LogSettings;
}

export interface SystemInfo {
  version: string;
  environment: string;
  server_time: string;
  uptime_seconds: number | null;
  python_version: string;
  database_type: string;
  database_size_mb: number | null;
}

export interface SystemStats {
  total_users: number;
  total_admins: number;
  total_courses: number;
  published_courses: number;
  total_nodes: number;
  total_progress_records: number;
  storage_used_mb: number;
}

export interface CacheInfo {
  redis_connected: boolean;
  redis_url: string;
  keys_count: number | null;
  memory_used_mb: number | null;
}

// ============ API 函数 ============

/**
 * 获取所有系统设置
 */
export async function getSettings(): Promise<AllSettings> {
  const { data } = await apiClient.get<AllSettings>('/admin/settings');
  return data;
}

/**
 * 更新所有系统设置
 */
export async function updateSettings(settings: AllSettings): Promise<{ success: boolean; message: string }> {
  const { data } = await apiClient.put<{ success: boolean; message: string }>('/admin/settings', settings);
  return data;
}

/**
 * 更新平台设置
 */
export async function updatePlatformSettings(platform: PlatformSettings): Promise<{ success: boolean; message: string }> {
  const { data } = await apiClient.put<{ success: boolean; message: string }>('/admin/settings/platform', platform);
  return data;
}

/**
 * 更新课程默认设置
 */
export async function updateCourseSettings(course: CourseDefaultSettings): Promise<{ success: boolean; message: string }> {
  const { data } = await apiClient.put<{ success: boolean; message: string }>('/admin/settings/course', course);
  return data;
}

/**
 * 更新用户设置
 */
export async function updateUserSettings(user: UserSettings): Promise<{ success: boolean; message: string }> {
  const { data } = await apiClient.put<{ success: boolean; message: string }>('/admin/settings/user', user);
  return data;
}

/**
 * 更新存储设置
 */
export async function updateStorageSettings(storage: StorageSettings): Promise<{ success: boolean; message: string }> {
  const { data } = await apiClient.put<{ success: boolean; message: string }>('/admin/settings/storage', storage);
  return data;
}

/**
 * 更新日志设置
 */
export async function updateLogSettings(log: LogSettings): Promise<{ success: boolean; message: string }> {
  const { data } = await apiClient.put<{ success: boolean; message: string }>('/admin/settings/log', log);
  return data;
}

/**
 * 获取系统信息
 */
export async function getSystemInfo(): Promise<SystemInfo> {
  const { data } = await apiClient.get<SystemInfo>('/admin/system-info');
  return data;
}

/**
 * 获取系统统计
 */
export async function getSystemStats(): Promise<SystemStats> {
  const { data } = await apiClient.get<SystemStats>('/admin/system-stats');
  return data;
}

/**
 * 获取缓存信息
 */
export async function getCacheInfo(): Promise<CacheInfo> {
  const { data } = await apiClient.get<CacheInfo>('/admin/cache-info');
  return data;
}

/**
 * 清除缓存
 */
export async function clearCache(): Promise<{ success: boolean; message: string }> {
  const { data } = await apiClient.post<{ success: boolean; message: string }>('/admin/cache/clear');
  return data;
}

/**
 * 重置设置为默认值
 */
export async function resetSettings(): Promise<{ success: boolean; message: string }> {
  const { data } = await apiClient.post<{ success: boolean; message: string }>('/admin/settings/reset');
  return data;
}
