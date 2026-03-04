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

const SOURCE_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];
const DEFAULT_HEATMAP_DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const DEFAULT_HEATMAP_HOURS = Array.from({ length: 24 }, (_, hour) => hour);

const buildEmptyHeatmapMatrix = (): number[][] =>
  Array.from({ length: DEFAULT_HEATMAP_DAYS.length }, () =>
    Array.from({ length: DEFAULT_HEATMAP_HOURS.length }, () => 0),
  );

// UI fallback data for loading/error states
export const mockOverviewData: OverviewData = {
  totalUsers: 0,
  newUsersToday: 0,
  newUsersYesterday: 0,
  activeUsers: 0,
  todayLearningHours: 0,
  aiConversations: 0,
  totalCourses: 0,
  publishedCourses: 0,
  avgCompletion: 0,
};

export const mockGrowthData: GrowthDataPoint[] = [
  { date: '01/01', newUsers: 0, totalUsers: 0, activeUsers: 0 },
  { date: '01/02', newUsers: 0, totalUsers: 0, activeUsers: 0 },
  { date: '01/03', newUsers: 0, totalUsers: 0, activeUsers: 0 },
  { date: '01/04', newUsers: 0, totalUsers: 0, activeUsers: 0 },
  { date: '01/05', newUsers: 0, totalUsers: 0, activeUsers: 0 },
  { date: '01/06', newUsers: 0, totalUsers: 0, activeUsers: 0 },
  { date: '01/07', newUsers: 0, totalUsers: 0, activeUsers: 0 },
];

export const mockRetentionData: RetentionData = {
  d1: 0,
  d3: 0,
  d7: 0,
  d14: 0,
  d30: 0,
  cohortSize: 0,
  curve: [
    { day: 'D0', rate: 100 },
    { day: 'D1', rate: 0 },
    { day: 'D3', rate: 0 },
    { day: 'D7', rate: 0 },
    { day: 'D14', rate: 0 },
    { day: 'D30', rate: 0 },
  ],
};

export const mockFunnelData: FunnelStage[] = [
  { stage: '访问课程页', count: 0, rate: 100 },
  { stage: '开始学习', count: 0, rate: 0 },
  { stage: '完成首个章节', count: 0, rate: 0 },
  { stage: '完成课程', count: 0, rate: 0 },
];

export const mockUserSourceData: UserSourceData[] = [
  { name: '直接访问', value: 0, color: SOURCE_COLORS[0] },
  { name: '课程推荐', value: 0, color: SOURCE_COLORS[1] },
  { name: '搜索引擎', value: 0, color: SOURCE_COLORS[2] },
  { name: '社群分享', value: 0, color: SOURCE_COLORS[3] },
];

export const mockLearningTimeData: LearningTimeData[] = [
  { range: '0-15分钟', count: 0 },
  { range: '15-30分钟', count: 0 },
  { range: '30-60分钟', count: 0 },
  { range: '60分钟以上', count: 0 },
];

export const mockHeatmapData: HeatmapData = {
  data: buildEmptyHeatmapMatrix(),
  days: DEFAULT_HEATMAP_DAYS,
  hours: DEFAULT_HEATMAP_HOURS,
};

export const mockUserClusters: UserCluster[] = [
  { name: '高活跃学习者', description: '高频学习与高完成率', count: 0, color: '#10B981' },
  { name: '稳定学习者', description: '持续稳定地完成学习任务', count: 0, color: '#3B82F6' },
  { name: '间歇学习者', description: '学习行为波动较大', count: 0, color: '#F59E0B' },
  { name: '流失风险用户', description: '近期学习活跃度显著下降', count: 0, color: '#EF4444' },
];

export const mockAIUsageData: AIUsageData = {
  totalConversations: 0,
  uniqueUsers: 0,
  avgMessagesPerUser: 0,
  trend: [],
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value);

const toNumber = (value: unknown, fallback = 0): number => {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value === 'string' && value.trim() !== '') {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) return parsed;
  }
  return fallback;
};

const toNonNegativeNumber = (value: unknown, fallback = 0): number =>
  Math.max(0, toNumber(value, fallback));

const toString = (value: unknown, fallback = ''): string =>
  typeof value === 'string' ? value : fallback;

const clamp = (value: number, min: number, max: number): number =>
  Math.min(max, Math.max(min, value));

function normalizeOverview(raw: unknown): OverviewData {
  const data = isRecord(raw) ? raw : {};
  return {
    totalUsers: toNonNegativeNumber(data.totalUsers),
    newUsersToday: toNonNegativeNumber(data.newUsersToday),
    newUsersYesterday: toNonNegativeNumber(data.newUsersYesterday),
    activeUsers: toNonNegativeNumber(data.activeUsers),
    todayLearningHours: toNonNegativeNumber(data.todayLearningHours),
    aiConversations: toNonNegativeNumber(data.aiConversations),
    totalCourses: toNonNegativeNumber(data.totalCourses),
    publishedCourses: toNonNegativeNumber(data.publishedCourses),
    avgCompletion: clamp(toNonNegativeNumber(data.avgCompletion), 0, 100),
  };
}

function normalizeGrowth(raw: unknown): GrowthDataPoint[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((item, index) => {
    const data = isRecord(item) ? item : {};
    return {
      date: toString(data.date, `Day ${index + 1}`),
      newUsers: toNonNegativeNumber(data.newUsers),
      totalUsers: toNonNegativeNumber(data.totalUsers),
      activeUsers: toNonNegativeNumber(data.activeUsers),
    };
  });
}

function normalizeRetention(raw: unknown): RetentionData {
  const data = isRecord(raw) ? raw : {};
  const curveRaw = Array.isArray(data.curve) ? data.curve : [];
  const curve = curveRaw.map((point, index) => {
    const curvePoint = isRecord(point) ? point : {};
    return {
      day: toString(curvePoint.day, `D${index}`),
      rate: clamp(toNonNegativeNumber(curvePoint.rate), 0, 100),
    };
  });

  return {
    d1: clamp(toNonNegativeNumber(data.d1), 0, 100),
    d3: clamp(toNonNegativeNumber(data.d3), 0, 100),
    d7: clamp(toNonNegativeNumber(data.d7), 0, 100),
    d14: clamp(toNonNegativeNumber(data.d14), 0, 100),
    d30: clamp(toNonNegativeNumber(data.d30), 0, 100),
    cohortSize: toNonNegativeNumber(data.cohortSize),
    curve,
  };
}

function normalizeFunnel(raw: unknown): FunnelStage[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((item, index) => {
    const data = isRecord(item) ? item : {};
    return {
      stage: toString(data.stage, `Stage ${index + 1}`),
      count: toNonNegativeNumber(data.count),
      rate: clamp(toNonNegativeNumber(data.rate), 0, 100),
    };
  });
}

function normalizeUserSources(raw: unknown): UserSourceData[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((item, index) => {
    const data = isRecord(item) ? item : {};
    return {
      name: toString(data.name, `Source ${index + 1}`),
      value: toNonNegativeNumber(data.value),
      color: toString(data.color, SOURCE_COLORS[index % SOURCE_COLORS.length]),
    };
  });
}

function normalizeLearningTime(raw: unknown): LearningTimeData[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((item, index) => {
    const data = isRecord(item) ? item : {};
    return {
      range: toString(data.range, `Bucket ${index + 1}`),
      count: toNonNegativeNumber(data.count),
    };
  });
}

function normalizeHeatmap(raw: unknown): HeatmapData {
  const data = isRecord(raw) ? raw : {};

  const daysCandidate = Array.isArray(data.days)
    ? data.days.map((day) => toString(day)).filter((day) => day.length > 0)
    : [];
  const hoursCandidate = Array.isArray(data.hours)
    ? data.hours.map((hour) => toNonNegativeNumber(hour)).filter((hour) => Number.isFinite(hour))
    : [];

  const days = daysCandidate.length > 0 ? daysCandidate : DEFAULT_HEATMAP_DAYS;
  const hours = hoursCandidate.length > 0 ? hoursCandidate : DEFAULT_HEATMAP_HOURS;

  const inputRows = Array.isArray(data.data)
    ? data.data.map((row) =>
      Array.isArray(row) ? row.map((value) => toNonNegativeNumber(value)) : [],
    )
    : [];

  const normalizedRows = Array.from({ length: days.length }, (_, rowIndex) =>
    Array.from({ length: hours.length }, (_, colIndex) => inputRows[rowIndex]?.[colIndex] ?? 0),
  );

  return {
    data: normalizedRows.length > 0 ? normalizedRows : buildEmptyHeatmapMatrix(),
    days,
    hours,
  };
}

function normalizeUserClusters(raw: unknown): UserCluster[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((item, index) => {
    const data = isRecord(item) ? item : {};
    return {
      name: toString(data.name, `Cluster ${index + 1}`),
      description: toString(data.description),
      count: toNonNegativeNumber(data.count),
      color: toString(data.color, SOURCE_COLORS[index % SOURCE_COLORS.length]),
    };
  });
}

function normalizeAIUsage(raw: unknown): AIUsageData {
  const data = isRecord(raw) ? raw : {};
  const trendRaw = Array.isArray(data.trend) ? data.trend : [];
  const trend = trendRaw.map((item, index) => {
    const trendPoint = isRecord(item) ? item : {};
    return {
      time: toString(trendPoint.time, `T${index + 1}`),
      count: toNonNegativeNumber(trendPoint.count),
    };
  });

  return {
    totalConversations: toNonNegativeNumber(data.totalConversations),
    uniqueUsers: toNonNegativeNumber(data.uniqueUsers),
    avgMessagesPerUser: toNonNegativeNumber(data.avgMessagesPerUser),
    trend,
  };
}

function normalizeCourseStats(raw: unknown): CourseStats[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((item, index) => {
    const data = isRecord(item) ? item : {};
    return {
      id: toNonNegativeNumber(data.id, index + 1),
      name: toString(data.name, `Course ${index + 1}`),
      enrolledUsers: toNonNegativeNumber(data.enrolledUsers),
      totalNodes: toNonNegativeNumber(data.totalNodes),
      avgCompletion: clamp(toNonNegativeNumber(data.avgCompletion), 0, 100),
      totalLearningHours: toNonNegativeNumber(data.totalLearningHours),
    };
  });
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
    if (cached !== null) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/analytics/overview`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch overview');
      const data = normalizeOverview(await response.json());
      setCachedData(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Failed to fetch overview:', error);
      throw error;
    }
  },

  getGrowth: async (period: '7d' | '30d' | '90d' = '30d'): Promise<GrowthDataPoint[]> => {
    const cacheKey = `analytics_growth_${period}`;
    const cached = getCachedData<GrowthDataPoint[]>(cacheKey);
    if (cached !== null) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/analytics/growth?period=${period}`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch growth data');
      const data = normalizeGrowth(await response.json());
      setCachedData(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Failed to fetch growth data:', error);
      throw error;
    }
  },

  getRetention: async (cohortDays: number = 30): Promise<RetentionData> => {
    const cacheKey = `analytics_retention_${cohortDays}`;
    const cached = getCachedData<RetentionData>(cacheKey);
    if (cached !== null) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/analytics/retention?cohort_days=${cohortDays}`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch retention data');
      const data = normalizeRetention(await response.json());
      setCachedData(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Failed to fetch retention data:', error);
      throw error;
    }
  },

  getFunnel: async (): Promise<FunnelStage[]> => {
    const cacheKey = 'analytics_funnel';
    const cached = getCachedData<FunnelStage[]>(cacheKey);
    if (cached !== null) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/analytics/funnel`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch funnel data');
      const data = normalizeFunnel(await response.json());
      setCachedData(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Failed to fetch funnel data:', error);
      throw error;
    }
  },

  getHeatmap: async (): Promise<HeatmapData> => {
    const cacheKey = 'analytics_heatmap';
    const cached = getCachedData<HeatmapData>(cacheKey);
    if (cached !== null) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/analytics/heatmap`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch heatmap data');
      const data = normalizeHeatmap(await response.json());
      setCachedData(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Failed to fetch heatmap data:', error);
      throw error;
    }
  },

  getUserSources: async (): Promise<UserSourceData[]> => {
    const cacheKey = 'analytics_user_sources';
    const cached = getCachedData<UserSourceData[]>(cacheKey);
    if (cached !== null) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/analytics/user-sources`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch user sources');
      const data = normalizeUserSources(await response.json());
      setCachedData(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Failed to fetch user sources:', error);
      throw error;
    }
  },

  getLearningTime: async (): Promise<LearningTimeData[]> => {
    const cacheKey = 'analytics_learning_time';
    const cached = getCachedData<LearningTimeData[]>(cacheKey);
    if (cached !== null) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/analytics/learning-time`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch learning time');
      const data = normalizeLearningTime(await response.json());
      setCachedData(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Failed to fetch learning time:', error);
      throw error;
    }
  },

  getClusters: async (): Promise<UserCluster[]> => {
    const cacheKey = 'analytics_clusters';
    const cached = getCachedData<UserCluster[]>(cacheKey);
    if (cached !== null) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/analytics/user-clusters`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch clusters');
      const data = normalizeUserClusters(await response.json());
      setCachedData(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Failed to fetch clusters:', error);
      throw error;
    }
  },

  getAIUsage: async (period: '24h' | '7d' | '30d' = '24h'): Promise<AIUsageData> => {
    const cacheKey = `analytics_ai_usage_${period}`;
    const cached = getCachedData<AIUsageData>(cacheKey);
    if (cached !== null) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/analytics/ai-usage?period=${period}`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch AI usage');
      const data = normalizeAIUsage(await response.json());
      setCachedData(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Failed to fetch AI usage:', error);
      throw error;
    }
  },

  getCourseStats: async (): Promise<CourseStats[]> => {
    const cacheKey = 'analytics_course_stats';
    const cached = getCachedData<CourseStats[]>(cacheKey);
    if (cached !== null) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/analytics/courses`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch course stats');
      const data = normalizeCourseStats(await response.json());
      setCachedData(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Failed to fetch course stats:', error);
      throw error;
    }
  },

  // Force refresh - clears cache and fetches fresh data
  clearCache: () => {
    Object.keys(cache).forEach((key) => {
      if (key.startsWith('analytics_')) {
        delete cache[key];
      }
    });
  },
};
