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
  level: AdminLevel;
  is_active: boolean;
  created_at: string;
  last_login_at: string | null;
}

// 管理员列表响应
export interface AdminListResponse {
  items: AdminListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// 创建管理员请求
export interface CreateAdminRequest {
  username: string;
  email: string;
  password: string;
  level: AdminLevel;
}

// 更新管理员请求
export interface UpdateAdminRequest {
  username?: string;
  email?: string;
  password?: string;
  level?: AdminLevel;
  is_active?: boolean;
}

// 管理员筛选参数
export interface AdminFilters {
  page?: number;
  page_size?: number;
  level?: AdminLevel;
  is_active?: boolean;
  search?: string;
}

// 模拟数据存储 (实际应用中应该从后端获取)
let mockAdmins: AdminListItem[] = [
  {
    id: 1,
    username: 'superadmin',
    email: 'super@hercux.com',
    level: 1,
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
    last_login_at: new Date().toISOString(),
  },
];

let nextAdminId = 2;

/**
 * 获取管理员列表
 */
export async function getAdmins(filters: AdminFilters = {}): Promise<AdminListResponse> {
  const { page = 1, page_size = 20, level, is_active, search } = filters;

  // 模拟筛选
  let filtered = [...mockAdmins];

  if (level !== undefined) {
    filtered = filtered.filter(a => a.level === level);
  }

  if (is_active !== undefined) {
    filtered = filtered.filter(a => a.is_active === is_active);
  }

  if (search) {
    const searchLower = search.toLowerCase();
    filtered = filtered.filter(a =>
      a.username.toLowerCase().includes(searchLower) ||
      a.email.toLowerCase().includes(searchLower)
    );
  }

  const total = filtered.length;
  const total_pages = Math.ceil(total / page_size);
  const start = (page - 1) * page_size;
  const items = filtered.slice(start, start + page_size);

  return {
    items,
    total,
    page,
    page_size,
    total_pages,
  };
}

/**
 * 获取单个管理员
 */
export async function getAdmin(id: number): Promise<AdminListItem | null> {
  return mockAdmins.find(a => a.id === id) || null;
}

/**
 * 创建管理员
 */
export async function createAdmin(data: CreateAdminRequest): Promise<AdminListItem> {
  // 检查用户名和邮箱是否已存在
  if (mockAdmins.some(a => a.username === data.username)) {
    throw new Error('用户名已存在');
  }
  if (mockAdmins.some(a => a.email === data.email)) {
    throw new Error('邮箱已存在');
  }

  const newAdmin: AdminListItem = {
    id: nextAdminId++,
    username: data.username,
    email: data.email,
    level: data.level,
    is_active: true,
    created_at: new Date().toISOString(),
    last_login_at: null,
  };

  mockAdmins.push(newAdmin);
  return newAdmin;
}

/**
 * 更新管理员
 */
export async function updateAdmin(id: number, data: UpdateAdminRequest): Promise<AdminListItem> {
  const index = mockAdmins.findIndex(a => a.id === id);
  if (index === -1) {
    throw new Error('管理员不存在');
  }

  // 不能修改超级管理员的等级
  if (mockAdmins[index].level === 1 && data.level && data.level !== 1) {
    throw new Error('不能修改超级管理员的等级');
  }

  // 检查用户名和邮箱是否已被其他人使用
  if (data.username && mockAdmins.some(a => a.id !== id && a.username === data.username)) {
    throw new Error('用户名已存在');
  }
  if (data.email && mockAdmins.some(a => a.id !== id && a.email === data.email)) {
    throw new Error('邮箱已存在');
  }

  mockAdmins[index] = {
    ...mockAdmins[index],
    ...data,
  };

  return mockAdmins[index];
}

/**
 * 删除管理员
 */
export async function deleteAdmin(id: number): Promise<void> {
  const admin = mockAdmins.find(a => a.id === id);
  if (!admin) {
    throw new Error('管理员不存在');
  }

  // 不能删除超级管理员
  if (admin.level === 1) {
    throw new Error('不能删除超级管理员');
  }

  mockAdmins = mockAdmins.filter(a => a.id !== id);
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
