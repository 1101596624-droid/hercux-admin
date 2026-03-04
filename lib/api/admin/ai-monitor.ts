// AI API Monitoring Types and Functions

export interface AIOverviewData {
  today: {
    call_count: number;
    total_tokens: number;
    total_cost: number;
    avg_latency_ms: number;
    error_rate: number;
  };
  comparisons: {
    calls_vs_yesterday: number;
    cost_vs_yesterday: number;
  };
}

export interface AITrendPoint {
  time: string;
  call_count: number;
  tokens: number;
  cost: number;
}

export interface AICostBreakdown {
  total_cost: number;
  budget: number;
  budget_usage: number;
  breakdown: {
    model: string;
    call_count: number;
    tokens: number;
    cost: number;
    percentage: number;
  }[];
  forecast: {
    month_end_cost: number;
    will_exceed_budget: boolean;
  };
}

export interface AILogEntry {
  id: string;
  user_id: number;
  user_name: string;
  scene: 'tutor' | 'planner' | 'voice' | 'summary';
  model: string;
  input_tokens: number;
  output_tokens: number;
  latency_ms: number;
  status: 'success' | 'error' | 'timeout';
  error_code?: string;
  cost: number;
  created_at: string;
}

export interface AIAlert {
  id: number;
  alert_type: string;
  severity: 'critical' | 'warning' | 'info';
  title: string;
  message: string;
  metric_value: number;
  threshold_value: number;
  status: 'open' | 'acknowledged' | 'resolved';
  created_at: string;
  resolved_at?: string;
  resolution_note?: string;
}

export interface AIQuota {
  user_id: number;
  user_level: string;
  daily: {
    calls: { used: number; limit: number | null };
    tokens: { used: number; limit: number | null };
    voice_seconds: { used: number; limit: number };
  };
  monthly: {
    calls: number;
    cost: number;
  };
  status: {
    is_rate_limited: boolean;
    is_blacklisted: boolean;
  };
}

// UI fallback data for loading/error states
export const mockAIOverview: AIOverviewData = {
  today: {
    call_count: 0,
    total_tokens: 0,
    total_cost: 0,
    avg_latency_ms: 0,
    error_rate: 0,
  },
  comparisons: {
    calls_vs_yesterday: 0,
    cost_vs_yesterday: 0,
  },
};

export const mockAITrends: AITrendPoint[] = [
  { time: '00:00', call_count: 0, tokens: 0, cost: 0 },
  { time: '04:00', call_count: 0, tokens: 0, cost: 0 },
  { time: '08:00', call_count: 0, tokens: 0, cost: 0 },
  { time: '12:00', call_count: 0, tokens: 0, cost: 0 },
  { time: '16:00', call_count: 0, tokens: 0, cost: 0 },
  { time: '20:00', call_count: 0, tokens: 0, cost: 0 },
];

export const mockAICostBreakdown: AICostBreakdown = {
  total_cost: 0,
  budget: 0,
  budget_usage: 0,
  breakdown: [],
  forecast: {
    month_end_cost: 0,
    will_exceed_budget: false,
  },
};

export const mockAILogs: AILogEntry[] = [];

export const mockAIAlerts: AIAlert[] = [];

type AlertStats = { open: number; acknowledged: number; resolved: number };
type LogsResponse = { data: AILogEntry[]; total: number };
type AlertsResponse = { data: AIAlert[]; stats: AlertStats };

const VALID_SCENES: AILogEntry['scene'][] = ['tutor', 'planner', 'voice', 'summary'];
const VALID_LOG_STATUS: AILogEntry['status'][] = ['success', 'error', 'timeout'];
const VALID_ALERT_SEVERITY: AIAlert['severity'][] = ['critical', 'warning', 'info'];
const VALID_ALERT_STATUS: AIAlert['status'][] = ['open', 'acknowledged', 'resolved'];

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

const toBoolean = (value: unknown, fallback = false): boolean =>
  typeof value === 'boolean' ? value : fallback;

const clamp = (value: number, min: number, max: number): number =>
  Math.min(max, Math.max(min, value));

function toScene(value: unknown): AILogEntry['scene'] {
  return VALID_SCENES.includes(value as AILogEntry['scene']) ? (value as AILogEntry['scene']) : 'tutor';
}

function toLogStatus(value: unknown): AILogEntry['status'] {
  return VALID_LOG_STATUS.includes(value as AILogEntry['status']) ? (value as AILogEntry['status']) : 'success';
}

function toAlertSeverity(value: unknown): AIAlert['severity'] {
  return VALID_ALERT_SEVERITY.includes(value as AIAlert['severity']) ? (value as AIAlert['severity']) : 'info';
}

function toAlertStatus(value: unknown): AIAlert['status'] {
  return VALID_ALERT_STATUS.includes(value as AIAlert['status']) ? (value as AIAlert['status']) : 'open';
}

function normalizeOverview(raw: unknown): AIOverviewData {
  const data = isRecord(raw) ? raw : {};
  const today = isRecord(data.today) ? data.today : {};
  const comparisons = isRecord(data.comparisons) ? data.comparisons : {};

  return {
    today: {
      call_count: toNonNegativeNumber(today.call_count),
      total_tokens: toNonNegativeNumber(today.total_tokens),
      total_cost: toNonNegativeNumber(today.total_cost),
      avg_latency_ms: toNonNegativeNumber(today.avg_latency_ms),
      error_rate: clamp(toNonNegativeNumber(today.error_rate), 0, 1),
    },
    comparisons: {
      calls_vs_yesterday: toNumber(comparisons.calls_vs_yesterday),
      cost_vs_yesterday: toNumber(comparisons.cost_vs_yesterday),
    },
  };
}

function normalizeTrends(raw: unknown): AITrendPoint[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((item, index) => {
    const data = isRecord(item) ? item : {};
    return {
      time: toString(data.time, `T${index + 1}`),
      call_count: toNonNegativeNumber(data.call_count),
      tokens: toNonNegativeNumber(data.tokens),
      cost: toNonNegativeNumber(data.cost),
    };
  });
}

function normalizeCosts(raw: unknown): AICostBreakdown {
  const data = isRecord(raw) ? raw : {};
  const breakdownRaw = Array.isArray(data.breakdown) ? data.breakdown : [];
  const forecastRaw = isRecord(data.forecast) ? data.forecast : {};

  return {
    total_cost: toNonNegativeNumber(data.total_cost),
    budget: toNonNegativeNumber(data.budget),
    budget_usage: clamp(toNonNegativeNumber(data.budget_usage), 0, 1),
    breakdown: breakdownRaw.map((item, index) => {
      const entry = isRecord(item) ? item : {};
      return {
        model: toString(entry.model, `model-${index + 1}`),
        call_count: toNonNegativeNumber(entry.call_count),
        tokens: toNonNegativeNumber(entry.tokens),
        cost: toNonNegativeNumber(entry.cost),
        percentage: clamp(toNonNegativeNumber(entry.percentage), 0, 1),
      };
    }),
    forecast: {
      month_end_cost: toNonNegativeNumber(forecastRaw.month_end_cost),
      will_exceed_budget: toBoolean(forecastRaw.will_exceed_budget),
    },
  };
}

function normalizeLog(raw: unknown, index: number): AILogEntry {
  const data = isRecord(raw) ? raw : {};
  const idValue = toString(data.id, `log_${index + 1}`);
  return {
    id: idValue,
    user_id: toNonNegativeNumber(data.user_id),
    user_name: toString(data.user_name, '匿名用户'),
    scene: toScene(data.scene),
    model: toString(data.model, 'unknown'),
    input_tokens: toNonNegativeNumber(data.input_tokens),
    output_tokens: toNonNegativeNumber(data.output_tokens),
    latency_ms: toNonNegativeNumber(data.latency_ms),
    status: toLogStatus(data.status),
    error_code: toString(data.error_code) || undefined,
    cost: toNonNegativeNumber(data.cost),
    created_at: toString(data.created_at, new Date(0).toISOString()),
  };
}

function normalizeLogsResponse(raw: unknown): LogsResponse {
  const data = isRecord(raw) ? raw : {};
  const rows = Array.isArray(data.data) ? data.data : [];
  return {
    data: rows.map((row, index) => normalizeLog(row, index)),
    total: toNonNegativeNumber(data.total, rows.length),
  };
}

function normalizeAlert(raw: unknown, index: number): AIAlert {
  const data = isRecord(raw) ? raw : {};
  return {
    id: toNonNegativeNumber(data.id, index + 1),
    alert_type: toString(data.alert_type, 'system'),
    severity: toAlertSeverity(data.severity),
    title: toString(data.title, '系统告警'),
    message: toString(data.message),
    metric_value: toNonNegativeNumber(data.metric_value),
    threshold_value: toNonNegativeNumber(data.threshold_value),
    status: toAlertStatus(data.status),
    created_at: toString(data.created_at, new Date(0).toISOString()),
    resolved_at: toString(data.resolved_at) || undefined,
    resolution_note: toString(data.resolution_note) || undefined,
  };
}

function normalizeAlertsResponse(raw: unknown): AlertsResponse {
  const data = isRecord(raw) ? raw : {};
  const rows = Array.isArray(data.data) ? data.data : [];
  const normalizedData = rows.map((row, index) => normalizeAlert(row, index));

  const statsRaw = isRecord(data.stats) ? data.stats : {};
  const stats: AlertStats = {
    open: toNonNegativeNumber(statsRaw.open),
    acknowledged: toNonNegativeNumber(statsRaw.acknowledged),
    resolved: toNonNegativeNumber(statsRaw.resolved),
  };

  return {
    data: normalizedData,
    stats,
  };
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
export const aiMonitorAPI = {
  getOverview: async (): Promise<AIOverviewData> => {
    const cacheKey = 'ai_monitor_overview';
    const cached = getCachedData<AIOverviewData>(cacheKey);
    if (cached !== null) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/ai/overview`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch AI overview');
      const data = normalizeOverview(await response.json());
      setCachedData(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Failed to fetch AI overview:', error);
      throw error;
    }
  },

  getTrends: async (period: '24h' | '7d' | '30d' = '24h'): Promise<AITrendPoint[]> => {
    const cacheKey = `ai_monitor_trends_${period}`;
    const cached = getCachedData<AITrendPoint[]>(cacheKey);
    if (cached !== null) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/ai/trends?period=${period}`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch AI trends');
      const data = normalizeTrends(await response.json());
      setCachedData(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Failed to fetch AI trends:', error);
      throw error;
    }
  },

  getCosts: async (): Promise<AICostBreakdown> => {
    const cacheKey = 'ai_monitor_costs';
    const cached = getCachedData<AICostBreakdown>(cacheKey);
    if (cached !== null) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/ai/costs`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch AI costs');
      const data = normalizeCosts(await response.json());
      setCachedData(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Failed to fetch AI costs:', error);
      throw error;
    }
  },

  getLogs: async (params?: { page?: number; limit?: number; scene?: string; status?: string }): Promise<LogsResponse> => {
    // Logs are not cached as they need to be fresh
    try {
      const searchParams = new URLSearchParams();
      if (params?.page) searchParams.set('page', String(params.page));
      if (params?.limit) searchParams.set('limit', String(params.limit));
      if (params?.scene) searchParams.set('feature', params.scene);
      if (params?.status) searchParams.set('status', params.status);

      const response = await fetch(`${API_BASE_URL}/admin/ai/logs?${searchParams}`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch AI logs');
      return normalizeLogsResponse(await response.json());
    } catch (error) {
      console.error('Failed to fetch AI logs:', error);
      throw error;
    }
  },

  getAlerts: async (status?: string): Promise<AlertsResponse> => {
    const cacheKey = `ai_monitor_alerts_${status || 'all'}`;
    const cached = getCachedData<AlertsResponse>(cacheKey);
    if (cached !== null) return cached;

    try {
      const url = status
        ? `${API_BASE_URL}/admin/ai/alerts?status=${status}`
        : `${API_BASE_URL}/admin/ai/alerts`;
      const response = await fetch(url, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch AI alerts');
      const data = normalizeAlertsResponse(await response.json());
      setCachedData(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Failed to fetch AI alerts:', error);
      throw error;
    }
  },

  updateAlert: async (id: number, data: { status: string; resolution_note?: string }): Promise<AIAlert> => {
    const response = await fetch(`${API_BASE_URL}/admin/ai/alerts/${id}`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to update alert');
    // Clear alerts cache after update
    Object.keys(cache).forEach((key) => {
      if (key.startsWith('ai_monitor_alerts')) {
        delete cache[key];
      }
    });
    return normalizeAlert(await response.json(), id);
  },

  // Force refresh - clears cache and fetches fresh data
  clearCache: () => {
    Object.keys(cache).forEach((key) => {
      if (key.startsWith('ai_monitor_')) {
        delete cache[key];
      }
    });
  },
};
