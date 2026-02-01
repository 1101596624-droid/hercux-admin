/**
 * User-related type definitions
 */

export type UserRole = 'student' | 'coach' | 'admin';

export type SubscriptionPlan = 'free' | 'pro' | 'team';

export type SubscriptionStatus = 'active' | 'expired' | 'cancelled' | 'trial';

export interface User {
  id: string;
  name: string;
  email: string;
  phone?: string;
  avatar?: string;
  role: UserRole;
  level: string; // e.g., 'Gold', 'Silver', 'Bronze'
  joinDate: Date;
  bio?: string;
  organization?: string;
  specialties: string[];
  badges?: Badge[];
}

export interface UserSettings {
  notifications: {
    dailyReminder: boolean;
    weeklyReport: boolean;
    achievementAlert: boolean;
    courseUpdate: boolean;
  };
  learning: {
    reminderTime: string; // HH:mm format
    weeklyGoal: number; // hours
    autoPlay: boolean;
    playbackSpeed: number; // 0.75, 1.0, 1.25, 1.5, 2.0
  };
  privacy: {
    showProfile: boolean;
    showProgress: boolean;
    showAchievements: boolean;
  };
  language: string; // 'zh-CN', 'zh-TW', 'en'
  theme: 'light' | 'dark' | 'auto';
}

export interface UserStats {
  totalHours: number;
  totalCourses: number;
  completedCourses: number;
  completedNodes?: number; // Total completed nodes
  studyTime?: number; // Total study time in hours
  averageScore?: number; // Average quiz/test score (0-100)
  currentStreak: number;
  longestStreak: number;
  totalBadges: number;
  rankPercentile: number; // 1-100
  weeklyProgress?: number;
  weeklyGoal?: number;
  weeklyData: Array<{
    day: string;
    hours: number;
  }>;
  monthlyData: Array<{
    month: string;
    hours: number;
  }>;
  skillDistribution: Array<{
    skill: string;
    progress: number; // 0-100
    color: string;
  }>;
  recentActivities?: Activity[];
}

export interface Activity {
  id: string;
  userId: string;
  type: 'course_completed' | 'node_completed' | 'badge_earned' | 'plan_generated' | 'quiz_passed';
  action: string;
  detail: string;
  timestamp: string | Date;
  metadata?: Record<string, any>;
}

export interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: 'learning' | 'achievement' | 'streak' | 'mastery';
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  earnedAt?: Date;
  progress?: number; // 0-100 for progressive badges
}

export interface Subscription {
  plan: SubscriptionPlan;
  status: SubscriptionStatus;
  startDate: Date;
  nextBilling?: Date;
  price: number;
  features: Array<{
    name: string;
    included: boolean;
    limit?: string;
  }>;
}

export interface StorageInfo {
  total: number; // MB
  used: number; // MB
  breakdown: Array<{
    type: string;
    size: number; // MB
    color: string;
  }>;
}

export interface Invoice {
  id: string;
  date: Date;
  amount: number;
  status: 'paid' | 'pending' | 'failed';
  downloadUrl?: string;
}
