/**
 * Admin Management API
 * 管理员账号管理接口
 */

import { apiClient } from './client';
import type { AdminLevel, AdminUser } from '@/types';
import { ADMIN_LEVEL_PERMISSIONS } from '@/types';

// 管理员列表项
export interface AdminListItem {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  level: AdminLevel;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

// 后端返回的管理员响应
interface BackendAdminResponse {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  admin_level: number;
  is_active: number;
  created_at: string | null;
  updated_at: string | null;
}

// 管理员列表响应
export interface AdminListResponse {
  items: AdminListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// 后端返回的列表响应
interface BackendAdminListResponse {
  items: BackendAdminResponse[];
  total: number;
  page: number;
  page_size: number;
}

// 创建管理员请求
export interface CreateAdminRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  level: AdminLevel;
}

// 更新管理员请求
export interface UpdateAdminRequest {
  full_name?: string;
  level?: AdminLevel;
  is_active?: boolean;
}

// 管理员筛选参数
export interface AdminFilters {
  page?: number;
  page_size?: number;
  level?: AdminLevel;
  search?: string;
}

// 转换后端响应为前端格式
function transformAdminResponse(admin: BackendAdminResponse): AdminListItem {
  return {
    id: admin.id,
    username: admin.username,
    email: admin.email,
    full_name: admin.full_name,
    level: admin.admin_level as AdminLevel,
    is_active: admin.is_active === 1,
    created_at: admin.created_at || '',
    updated_at: admin.updated_at,
  };
}

/**
 * 获取管理员列表
 */
export async function getAdmins(filters: AdminFilters = {}): Promise<AdminListResponse> {
  const { page = 1, page_size = 20, level, search } = filters;

  const params = new URLSearchParams();
  params.append('page', page.toString());
  params.append('page_size', page_size.toString());
  if (level !== undefined) {
    params.append('level', level.toString());
  }
  if (search) {
    params.append('search', search);
  }

  const { data: response } = await apiClient.get<BackendAdminListResponse>(`/admin/admins?${params.toString()}`);

  const items = response.items.map(transformAdminResponse);
  const total_pages = Math.ceil(response.total / response.page_size);

  return {
    items,
    total: response.total,
    page: response.page,
    page_size: response.page_size,
    total_pages,
  };
}

/**
 * 获取单个管理员
 */
export async function getAdmin(id: number): Promise<AdminListItem | null> {
  try {
    // 通过列表接口获取，因为后端没有单独的获取接口
    const response = await getAdmins({ page: 1, page_size: 100 });
    return response.items.find(a => a.id === id) || null;
  } catch {
    return null;
  }
}

/**
 * 获取当前管理员信息
 */
export async function getCurrentAdmin(): Promise<AdminListItem> {
  const { data: response } = await apiClient.get<BackendAdminResponse>('/admin/admins/me');
  return transformAdminResponse(response);
}

/**
 * 创建管理员
 */
export async function createAdmin(data: CreateAdminRequest): Promise<AdminListItem> {
  const { data: response } = await apiClient.post<BackendAdminResponse>('/admin/admins', {
    username: data.username,
    email: data.email,
    password: data.password,
    full_name: data.full_name,
    admin_level: data.level,
  });
  return transformAdminResponse(response);
}

/**
 * 更新管理员
 */
export async function updateAdmin(id: number, data: UpdateAdminRequest): Promise<AdminListItem> {
  const updateData: Record<string, any> = {};

  if (data.full_name !== undefined) {
    updateData.full_name = data.full_name;
  }
  if (data.level !== undefined) {
    updateData.admin_level = data.level;
  }
  if (data.is_active !== undefined) {
    updateData.is_active = data.is_active ? 1 : 0;
  }

  const { data: response } = await apiClient.put<BackendAdminResponse>(`/admin/admins/${id}`, updateData);
  return transformAdminResponse(response);
}

/**
 * 删除管理员
 */
export async function deleteAdmin(id: number): Promise<void> {
  await apiClient.delete(`/admin/admins/${id}`);
}

/**
 * 检查当前用户是否有权限执行某操作
 */
export function checkPermission(userLevel: AdminLevel, permission: string): boolean {
  const permissions = ADMIN_LEVEL_PERMISSIONS[userLevel];
  return permissions.includes(permission as any);
}

/**
 * 获取权限不足的提示信息
 */
export function getPermissionDeniedMessage(action: string): string {
  return `权限不足：您没有${action}的权限`;
}
