/**
 * Achievements API Client
 * Handles user achievements and badges
 */

import { apiClient } from './client';

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
    const response: any = await apiClient.get('/v1/achievements');
    return response?.data?.achievements || response?.achievements || [];
  },

  /**
   * Get user's unlocked achievements
   */
  async getUserAchievements(): Promise<UserAchievement[]> {
    const response: any = await apiClient.get('/v1/achievements/user');
    return response?.data?.achievements || response?.achievements || [];
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
    const response: any = await apiClient.get(`/v1/achievements/${achievementId}/progress`);
    return response?.data || response;
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
  async getSkillTree(): Promise<any> {
    const response: any = await apiClient.get('/v1/achievements/skill-tree');
    return response?.data || response;
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
