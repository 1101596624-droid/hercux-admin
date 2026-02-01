// Analytics API Types and Functions

export interface OverviewData {
  totalUsers: number;
  newUsersToday: number;
  newUsersYesterday: number;
  activeUsers: number;
  todayLearningHours: number;
  aiConversations: number;
  totalCourses: number;
  publishedCourses: number;
  avgCompletion: number;
}

export interface GrowthDataPoint {
  date: string;
  newUsers: number;
  totalUsers: number;
  activeUsers: number;
}

export interface RetentionData {
  d1: number;
  d3: number;
  d7: number;
  d14: number;
  d30: number;
  cohortSize: number;
  curve: { day: string; rate: number }[];
}

export interface FunnelStage {
  stage: string;
  count: number;
  rate: number;
}

export interface UserSourceData {
  name: string;
  value: number;
  color: string;
}

export interface LearningTimeData {
  range: string;
  count: number;
}

export interface HeatmapData {
  data: number[][];
  days: string[];
  hours: number[];
}

export interface UserCluster {
  name: string;
  description: string;
  count: number;
  color: string;
}

export interface AIUsageData {
  totalConversations: number;
  uniqueUsers: number;
  avgMessagesPerUser: number;
  trend: { time: string; count: number }[];
}

export interface CourseStats {
  id: number;
  name: string;
  enrolledUsers: number;
  totalNodes: number;
  avgCompletion: number;
  totalLearningHours: number;
}

// Cache configuration - 5 minutes
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes in milliseconds

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

const cache: Record<string, CacheEntry<unknown>> = {};

function getCachedData<T>(key: string): T | null {
  const entry = cache[key] as CacheEntry<T> | undefined;
  if (entry && Date.now() - entry.timestamp < CACHE_DURATION) {
    return entry.data;
  }
  return null;
}

function setCachedData<T>(key: string, data: T): void {
  cache[key] = { data, timestamp: Date.now() };
}

// Mock data for development (fallback when API is unavailable)
export const mockOverviewData: OverviewData = {
  totalUsers: 9579,
  newUsersToday: 156,
  newUsersYesterday: 142,
  activeUsers: 2847,
  todayLearningHours: 1250.5,
  aiConversations: 3421,
  totalCourses: 24,
  publishedCourses: 18,
  avgCompletion: 45.2,
};

export const mockGrowthData: GrowthDataPoint[] = [
  { date: '01/01', newUsers: 120, totalUsers: 8420, activeUsers: 2100 },
  { date: '01/05', newUsers: 185, totalUsers: 8605, activeUsers: 2250 },
  { date: '01/09', newUsers: 210, totalUsers: 8815, activeUsers: 2400 },
  { date: '01/13', newUsers: 165, totalUsers: 8980, activeUsers: 2350 },
  { date: '01/17', newUsers: 245, totalUsers: 9225, activeUsers: 2600 },
  { date: '01/21', newUsers: 198, totalUsers: 9423, activeUsers: 2750 },
  { date: '01/23', newUsers: 156, totalUsers: 9579, activeUsers: 2847 },
];

export const mockRetentionData: RetentionData = {
  d1: 68,
  d3: 52,
  d7: 41,
  d14: 35,
  d30: 28,
  cohortSize: 1500,
  curve: [
    { day: 'D0', rate: 100 },
    { day: 'D1', rate: 68 },
    { day: 'D3', rate: 52 },
    { day: 'D7', rate: 41 },
    { day: 'D14', rate: 35 },
    { day: 'D30', rate: 28 },
  ],
};

export const mockFunnelData: FunnelStage[] = [
  { stage: '注册用户', count: 9579, rate: 100 },
  { stage: '选课用户', count: 6705, rate: 70 },
  { stage: '开始学习', count: 5263, rate: 55 },
  { stage: '完成节点', count: 3834, rate: 40 },
  { stage: '完成课程', count: 1724, rate: 18 },
];

export const mockUserSourceData: UserSourceData[] = [
  { name: '自然搜索', value: 3352, color: '#3B82F6' },
  { name: '社交媒体', value: 2395, color: '#10B981' },
  { name: '口碑推荐', value: 1916, color: '#F59E0B' },
  { name: '付费推广', value: 1149, color: '#EF4444' },
  { name: '其他渠道', value: 767, color: '#8B5CF6' },
];

export const mockLearningTimeData: LearningTimeData[] = [
  { range: '0-15分钟', count: 1250 },
  { range: '15-30分钟', count: 2180 },
  { range: '30-60分钟', count: 1820 },
  { range: '1-2小时', count: 890 },
  { range: '2小时以上', count: 320 },
];

export const mockHeatmapData: HeatmapData = {
  data: [
    [2, 3, 5, 8, 12, 15, 18, 22, 28, 32, 35, 38, 42, 45, 48, 52, 48, 42, 35, 28, 18, 12, 8, 5],
    [3, 4, 6, 10, 15, 18, 22, 28, 35, 42, 48, 52, 55, 58, 62, 58, 52, 45, 38, 32, 22, 15, 10, 6],
    [2, 3, 5, 8, 12, 16, 20, 25, 32, 38, 45, 50, 55, 58, 60, 55, 48, 42, 35, 28, 20, 14, 8, 5],
    [3, 4, 6, 9, 14, 18, 24, 30, 38, 45, 52, 58, 62, 65, 68, 62, 55, 48, 40, 32, 24, 16, 10, 6],
    [2, 3, 4, 6, 10, 14, 18, 22, 28, 35, 42, 48, 52, 55, 52, 48, 42, 35, 28, 22, 16, 12, 8, 4],
    [5, 8, 12, 18, 25, 32, 40, 48, 55, 62, 68, 72, 75, 72, 68, 62, 55, 48, 42, 35, 28, 22, 15, 8],
    [4, 6, 10, 15, 22, 28, 35, 42, 50, 58, 65, 70, 72, 70, 65, 58, 50, 42, 35, 28, 22, 18, 12, 6],
  ],
  days: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
  hours: Array.from({ length: 24 }, (_, i) => i),
};

export const mockUserClusters: UserCluster[] = [
  { name: '高活跃学习者', description: '每周学习>5小时，完成率>80%', count: 1823, color: '#10B981' },
  { name: '稳定学习者', description: '每周学习2-5小时，完成率50-80%', count: 3456, color: '#3B82F6' },
  { name: '间歇学习者', description: '每周学习<2小时，完成率30-50%', count: 2891, color: '#F59E0B' },
  { name: '流失风险用户', description: '7天以上未活跃', count: 1409, color: '#EF4444' },
];

export const mockAIUsageData: AIUsageData = {
  totalConversations: 3421,
  uniqueUsers: 1256,
  avgMessagesPerUser: 2.7,
  trend: [
    { time: '00:00', count: 45 },
    { time: '04:00', count: 23 },
    { time: '08:00', count: 156 },
    { time: '12:00', count: 289 },
    { time: '16:00', count: 312 },
    { time: '20:00', count: 245 },
  ],
};

export const mockCourseStats: CourseStats[] = [
  { id: 1, name: '运动生物力学基础', enrolledUsers: 2456, totalNodes: 24, avgCompletion: 68.5, totalLearningHours: 4520 },
  { id: 2, name: '高级力量训练', enrolledUsers: 1823, totalNodes: 32, avgCompletion: 52.3, totalLearningHours: 3210 },
  { id: 3, name: '运动康复入门', enrolledUsers: 1567, totalNodes: 18, avgCompletion: 75.2, totalLearningHours: 2890 },
];

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1';

// Helper function to get auth headers
const getAuthHeaders = () => ({
  'Authorization': `Bearer ${typeof window !== 'undefined' ? localStorage.getItem('auth_token') : ''}`,
  'Content-Type': 'application/json',
});

// API Functions with 5-minute caching
export const analyticsAPI = {
  getOverview: async (): Promise<OverviewData> => {
    const cacheKey = 'analytics_overview';
    const cached = getCachedData<OverviewData>(cacheKey);
    if (cached) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/analytics/overview`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch overview');
      const data = await response.json();
      setCachedData(cacheKey, data);
      return data;
    } catch {
      // Return mock data for development
      return mockOverviewData;
    }
  },

  getGrowth: async (period: '7d' | '30d' | '90d' = '30d'): Promise<GrowthDataPoint[]> => {
    const cacheKey = `analytics_growth_${period}`;
    const cached = getCachedData<GrowthDataPoint[]>(cacheKey);
    if (cached) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/analytics/growth?period=${period}`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch growth data');
      const data = await response.json();
      setCachedData(cacheKey, data);
      return data;
    } catch {
      return mockGrowthData;
    }
  },

  getRetention: async (cohortDays: number = 30): Promise<RetentionData> => {
    const cacheKey = `analytics_retention_${cohortDays}`;
    const cached = getCachedData<RetentionData>(cacheKey);
    if (cached) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/analytics/retention?cohort_days=${cohortDays}`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch retention data');
      const data = await response.json();
      setCachedData(cacheKey, data);
      return data;
    } catch {
      return mockRetentionData;
    }
  },

  getFunnel: async (): Promise<FunnelStage[]> => {
    const cacheKey = 'analytics_funnel';
    const cached = getCachedData<FunnelStage[]>(cacheKey);
    if (cached) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/analytics/funnel`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch funnel data');
      const data = await response.json();
      setCachedData(cacheKey, data);
      return data;
    } catch {
      return mockFunnelData;
    }
  },

  getHeatmap: async (): Promise<HeatmapData> => {
    const cacheKey = 'analytics_heatmap';
    const cached = getCachedData<HeatmapData>(cacheKey);
    if (cached) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/analytics/heatmap`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch heatmap data');
      const data = await response.json();
      setCachedData(cacheKey, data);
      return data;
    } catch {
      return mockHeatmapData;
    }
  },

  getUserSources: async (): Promise<UserSourceData[]> => {
    const cacheKey = 'analytics_user_sources';
    const cached = getCachedData<UserSourceData[]>(cacheKey);
    if (cached) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/analytics/user-sources`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch user sources');
      const data = await response.json();
      setCachedData(cacheKey, data);
      return data;
    } catch {
      return mockUserSourceData;
    }
  },

  getLearningTime: async (): Promise<LearningTimeData[]> => {
    const cacheKey = 'analytics_learning_time';
    const cached = getCachedData<LearningTimeData[]>(cacheKey);
    if (cached) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/analytics/learning-time`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch learning time');
      const data = await response.json();
      setCachedData(cacheKey, data);
      return data;
    } catch {
      return mockLearningTimeData;
    }
  },

  getClusters: async (): Promise<UserCluster[]> => {
    const cacheKey = 'analytics_clusters';
    const cached = getCachedData<UserCluster[]>(cacheKey);
    if (cached) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/analytics/user-clusters`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch clusters');
      const data = await response.json();
      setCachedData(cacheKey, data);
      return data;
    } catch {
      return mockUserClusters;
    }
  },

  getAIUsage: async (period: '24h' | '7d' | '30d' = '24h'): Promise<AIUsageData> => {
    const cacheKey = `analytics_ai_usage_${period}`;
    const cached = getCachedData<AIUsageData>(cacheKey);
    if (cached) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/analytics/ai-usage?period=${period}`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch AI usage');
      const data = await response.json();
      setCachedData(cacheKey, data);
      return data;
    } catch {
      return mockAIUsageData;
    }
  },

  getCourseStats: async (): Promise<CourseStats[]> => {
    const cacheKey = 'analytics_course_stats';
    const cached = getCachedData<CourseStats[]>(cacheKey);
    if (cached) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/analytics/courses`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch course stats');
      const data = await response.json();
      setCachedData(cacheKey, data);
      return data;
    } catch {
      return mockCourseStats;
    }
  },

  // Force refresh - clears cache and fetches fresh data
  clearCache: () => {
    Object.keys(cache).forEach(key => {
      if (key.startsWith('analytics_')) {
        delete cache[key];
      }
    });
  },
};
