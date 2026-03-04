/**
 * Achievements API Client
 * Handles user achievements and badges
 */

import { apiClient } from './client';

/** Flexible API response that may nest data differently */
interface FlexibleResponse<T> {
  data?: { achievements?: T[]; [key: string]: unknown };
  achievements?: T[];
  [key: string]: unknown;
}

export interface Achievement {
  id: number;
  name: string;
  description: string;
  category: 'learning' | 'completion' | 'streak' | 'mastery' | 'social';
  icon: string;
  points: number;
  requirement_type: string;
  requirement_value: number;
  is_hidden: boolean;
  created_at: string;
}

export interface UserAchievement {
  id: number;
  user_id: number;
  achievement_id: number;
  unlocked_at: string;
  progress: number;
  achievement: Achievement;
}

export interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: 'learning' | 'completion' | 'streak' | 'mastery' | 'social';
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  earnedAt?: Date;
  progress?: number;
  total?: number;
}

export const achievementsAPI = {
  /**
   * Get all available achievements
   */
  async getAllAchievements(): Promise<Achievement[]> {
    const data = await apiClient.get<FlexibleResponse<Achievement>>('/v1/achievements');
    return data?.data?.achievements || data?.achievements || [];
  },

  /**
   * Get user's unlocked achievements
   */
  async getUserAchievements(): Promise<UserAchievement[]> {
    const data = await apiClient.get<FlexibleResponse<UserAchievement>>('/v1/achievements/user');
    return data?.data?.achievements || data?.achievements || [];
  },

  /**
   * Get achievement progress
   */
  async getAchievementProgress(achievementId: number): Promise<{
    achievement_id: number;
    progress: number;
    requirement_value: number;
    is_unlocked: boolean;
  }> {
    const data = await apiClient.get<Record<string, unknown>>(`/v1/achievements/${achievementId}/progress`);
    return ((data as Record<string, unknown>)?.data || data) as {
      achievement_id: number;
      progress: number;
      requirement_value: number;
      is_unlocked: boolean;
    };
  },

  /**
   * Get user badges (formatted for UI)
   */
  async getUserBadges(): Promise<Badge[]> {
    const userAchievements = await this.getUserAchievements();

    return userAchievements.map(ua => ({
      id: String(ua.achievement.id),
      name: ua.achievement.name,
      description: ua.achievement.description,
      icon: ua.achievement.icon,
      category: ua.achievement.category,
      rarity: this.getRarityFromPoints(ua.achievement.points),
      earnedAt: new Date(ua.unlocked_at),
      progress: ua.progress,
      total: ua.achievement.requirement_value,
    }));
  },

  /**
   * Get skill tree data
   */
  async getSkillTree(): Promise<Record<string, unknown>> {
    const data = await apiClient.get<Record<string, unknown>>('/v1/achievements/skill-tree');
    return ((data as Record<string, unknown>)?.data || data) as Record<string, unknown>;
  },

  /**
   * Helper to determine rarity from points
   */
  getRarityFromPoints(points: number): 'common' | 'rare' | 'epic' | 'legendary' {
    if (points >= 100) return 'legendary';
    if (points >= 50) return 'epic';
    if (points >= 20) return 'rare';
    return 'common';
  },
};
