/**
 * Badges API - 勋章相关接口
 */

import { apiClient } from './client';
import type { Badge } from '@/types/user';

export interface BadgeResponse {
  badges: Badge[];
  stats: {
    total: number;
    earned: number;
    completionRate: number;
    rareBadges: number;
  };
}

export interface BadgeCategoryResponse {
  category: string;
  badges: Badge[];
  earned: number;
  total: number;
}

/**
 * 获取用户所有勋章
 */
export async function getUserBadges(userId: string): Promise<BadgeResponse> {
  return apiClient.get<BadgeResponse>(`/users/${userId}/badges`);
}

/**
 * 获取指定分类的勋章
 */
export async function getBadgesByCategory(
  userId: string,
  category: string
): Promise<BadgeCategoryResponse> {
  return apiClient.get<BadgeCategoryResponse>(
    `/users/${userId}/badges/category/${category}`
  );
}

/**
 * 获取所有可用勋章（包括未获得的）
 */
export async function getAllAvailableBadges(): Promise<Badge[]> {
  return apiClient.get<Badge[]>('/badges');
}

/**
 * 手动触发勋章检查（用于调试）
 */
export async function checkBadgeProgress(userId: string): Promise<void> {
  return apiClient.post(`/users/${userId}/badges/check`);
}
