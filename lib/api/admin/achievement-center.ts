// Achievement Center API Types and Functions
import { apiClient } from './client';

// Types
export type BadgeCategory = 'learning' | 'persistence' | 'practice' | 'quiz' | 'special';
export type BadgeRarity = 'common' | 'rare' | 'epic' | 'legendary';

export interface BadgeConfig {
  id: string;
  name: string;
  name_en?: string;
  icon: string;
  description?: string;
  category: BadgeCategory;
  rarity: BadgeRarity;
  points: number;
  condition: Record<string, any>;
  is_active: number;
  sort_order: number;
  created_at?: string;
  updated_at?: string;
  created_by?: string;
  unlock_count?: number;
}

export interface SkillTreeConfig {
  id: string;
  name: string;
  name_en?: string;
  icon: string;
  color: string;
  description?: string;
  match_rules: Record<string, any>;
  level_thresholds: number[];
  prerequisites: { treeId: string; requiredLevel: number }[];
  unlocks: string[];
  is_advanced: number;
  is_active: number;
  sort_order: number;
  created_at?: string;
  updated_at?: string;
  active_users?: number;
}

export interface SkillAchievementConfig {
  id: string;
  name: string;
  name_en?: string;
  icon: string;
  description?: string;
  points: number;
  condition: Record<string, any>;
  is_active: number;
  sort_order: number;
  created_at?: string;
  updated_at?: string;
  unlock_count?: number;
}

export interface PendingDomain {
  domain: string;
  node_count: number;
  completed_users: number;
  first_seen: string;
  status: 'pending' | 'approved' | 'rejected';
  reviewed_at?: string;
  reviewed_by?: string;
  reject_reason?: string;
}

export interface AchievementStats {
  total_badges: number;
  active_badges: number;
  total_skill_trees: number;
  active_skill_trees: number;
  total_skill_achievements: number;
  active_skill_achievements: number;
  pending_domains: number;
  total_badge_unlocks: number;
  total_skill_achievement_unlocks: number;
}

export interface BadgeCreateInput {
  id: string;
  name: string;
  name_en?: string;
  icon: string;
  description?: string;
  category: BadgeCategory;
  rarity?: BadgeRarity;
  points?: number;
  condition: Record<string, any>;
  is_active?: number;
  sort_order?: number;
}

export interface BadgeUpdateInput {
  name?: string;
  name_en?: string;
  icon?: string;
  description?: string;
  category?: BadgeCategory;
  rarity?: BadgeRarity;
  points?: number;
  condition?: Record<string, any>;
  is_active?: number;
  sort_order?: number;
}

export interface SkillTreeCreateInput {
  id: string;
  name: string;
  name_en?: string;
  icon: string;
  color: string;
  description?: string;
  match_rules: Record<string, any>;
  level_thresholds?: number[];
  prerequisites?: { treeId: string; requiredLevel: number }[];
  unlocks?: string[];
  is_advanced?: number;
  is_active?: number;
  sort_order?: number;
}

export interface SkillTreeUpdateInput {
  name?: string;
  name_en?: string;
  icon?: string;
  color?: string;
  description?: string;
  match_rules?: Record<string, any>;
  level_thresholds?: number[];
  prerequisites?: { treeId: string; requiredLevel: number }[];
  unlocks?: string[];
  is_advanced?: number;
  is_active?: number;
  sort_order?: number;
}

export interface SkillAchievementCreateInput {
  id: string;
  name: string;
  name_en?: string;
  icon: string;
  description?: string;
  points?: number;
  condition: Record<string, any>;
  is_active?: number;
  sort_order?: number;
}

export interface SkillAchievementUpdateInput {
  name?: string;
  name_en?: string;
  icon?: string;
  description?: string;
  points?: number;
  condition?: Record<string, any>;
  is_active?: number;
  sort_order?: number;
}

// API Functions
export const achievementCenterAPI = {
  // Stats
  getStats: async (): Promise<AchievementStats> => {
    const { data } = await apiClient.get<any>('/admin/achievement-center/stats');
    // Transform backend response to frontend format
    return {
      total_badges: data.badges?.total || 0,
      active_badges: data.badges?.active || 0,
      total_skill_trees: data.skillTrees?.total || 0,
      active_skill_trees: data.skillTrees?.active || 0,
      total_skill_achievements: data.achievements?.total || 0,
      active_skill_achievements: data.achievements?.active || 0,
      pending_domains: data.pendingDomains || 0,
      total_badge_unlocks: data.badges?.totalUnlocked || 0,
      total_skill_achievement_unlocks: data.achievements?.totalUnlocked || 0,
    };
  },

  // Badges
  getBadges: async (params?: { category?: BadgeCategory; is_active?: number }): Promise<BadgeConfig[]> => {
    const { data } = await apiClient.get<any>('/admin/achievement-center/badges', { params });
    // Transform backend response - backend returns { data: [...], pagination: {...} }
    const badges = data.data || data;
    return (Array.isArray(badges) ? badges : []).map((b: any) => ({
      id: b.id,
      name: b.name,
      name_en: b.nameEn || b.name_en,
      icon: b.icon,
      description: b.description,
      category: b.category,
      rarity: b.rarity,
      points: b.points,
      condition: b.condition,
      is_active: b.isActive ? 1 : (b.is_active ?? 0),
      sort_order: b.sortOrder || b.sort_order || 0,
      created_at: b.createdAt || b.created_at,
      unlock_count: b.stats?.unlockedCount || b.unlock_count || 0,
    }));
  },

  getBadge: async (id: string): Promise<BadgeConfig> => {
    const { data } = await apiClient.get<BadgeConfig>(`/admin/achievement-center/badges/${id}`);
    return data;
  },

  createBadge: async (input: BadgeCreateInput): Promise<BadgeConfig> => {
    await apiClient.post('/admin/achievement-center/badges', input);
    // Backend returns { message, id }, construct badge from input
    return {
      ...input,
      is_active: input.is_active ?? 1,
      sort_order: input.sort_order ?? 0,
      unlock_count: 0,
    } as BadgeConfig;
  },

  updateBadge: async (id: string, input: BadgeUpdateInput): Promise<BadgeConfig> => {
    await apiClient.put(`/admin/achievement-center/badges/${id}`, input);
    // Backend returns { message }, return input merged with id for frontend to use
    return { id, ...input } as BadgeConfig;
  },

  deleteBadge: async (id: string): Promise<void> => {
    await apiClient.delete(`/admin/achievement-center/badges/${id}`);
  },

  // Skill Trees
  getSkillTrees: async (params?: { is_active?: number }): Promise<SkillTreeConfig[]> => {
    const { data } = await apiClient.get<any>('/admin/achievement-center/skill-trees', { params });
    // Transform backend response - backend returns { data: [...] }
    const trees = data.data || data;
    return (Array.isArray(trees) ? trees : []).map((t: any) => ({
      id: t.id,
      name: t.name,
      name_en: t.nameEn || t.name_en,
      icon: t.icon,
      color: t.color,
      description: t.description,
      match_rules: t.matchRules || t.match_rules || {},
      level_thresholds: t.levelThresholds || t.level_thresholds || [0, 50, 150, 300, 500],
      prerequisites: t.prerequisites || [],
      unlocks: t.unlocks || [],
      is_advanced: t.isAdvanced ? 1 : (t.is_advanced ?? 0),
      is_active: t.isActive ? 1 : (t.is_active ?? 0),
      sort_order: t.sortOrder || t.sort_order || 0,
      active_users: t.stats?.userCount || t.active_users || 0,
    }));
  },

  getSkillTree: async (id: string): Promise<SkillTreeConfig> => {
    const { data } = await apiClient.get<SkillTreeConfig>(`/admin/achievement-center/skill-trees/${id}`);
    return data;
  },

  createSkillTree: async (input: SkillTreeCreateInput): Promise<SkillTreeConfig> => {
    const { data } = await apiClient.post<SkillTreeConfig>('/admin/achievement-center/skill-trees', input);
    return data;
  },

  updateSkillTree: async (id: string, input: SkillTreeUpdateInput): Promise<SkillTreeConfig> => {
    const { data } = await apiClient.put<SkillTreeConfig>(`/admin/achievement-center/skill-trees/${id}`, input);
    return data;
  },

  deleteSkillTree: async (id: string): Promise<void> => {
    await apiClient.delete(`/admin/achievement-center/skill-trees/${id}`);
  },

  // Skill Achievements
  getSkillAchievements: async (params?: { is_active?: number }): Promise<SkillAchievementConfig[]> => {
    const { data } = await apiClient.get<SkillAchievementConfig[]>('/admin/achievement-center/skill-achievements', { params });
    return data;
  },

  getSkillAchievement: async (id: string): Promise<SkillAchievementConfig> => {
    const { data } = await apiClient.get<SkillAchievementConfig>(`/admin/achievement-center/skill-achievements/${id}`);
    return data;
  },

  createSkillAchievement: async (input: SkillAchievementCreateInput): Promise<SkillAchievementConfig> => {
    const { data } = await apiClient.post<SkillAchievementConfig>('/admin/achievement-center/skill-achievements', input);
    return data;
  },

  updateSkillAchievement: async (id: string, input: SkillAchievementUpdateInput): Promise<SkillAchievementConfig> => {
    const { data } = await apiClient.put<SkillAchievementConfig>(`/admin/achievement-center/skill-achievements/${id}`, input);
    return data;
  },

  deleteSkillAchievement: async (id: string): Promise<void> => {
    await apiClient.delete(`/admin/achievement-center/skill-achievements/${id}`);
  },

  // Pending Domains
  getPendingDomains: async (params?: { status?: string }): Promise<PendingDomain[]> => {
    const { data } = await apiClient.get<PendingDomain[]>('/admin/achievement-center/pending-domains', { params });
    return data;
  },

  approveDomain: async (domain: string): Promise<PendingDomain> => {
    const { data } = await apiClient.post<PendingDomain>(`/admin/achievement-center/pending-domains/${domain}/approve`);
    return data;
  },

  rejectDomain: async (domain: string, reason?: string): Promise<PendingDomain> => {
    const { data } = await apiClient.post<PendingDomain>(`/admin/achievement-center/pending-domains/${domain}/reject`, { reason });
    return data;
  },

  // AI Badge Generation
  generateBadge: async (unlockDescription: string, badgeName?: string, badgeCategory?: string): Promise<{
    success: boolean;
    badge?: BadgeCreateInput;
    error?: string;
  }> => {
    const { data } = await apiClient.post<any>('/admin/achievement-center/generate-badge', {
      unlock_description: unlockDescription,
      badge_name: badgeName,
      badge_category: badgeCategory,
    });
    return data;
  },
};
