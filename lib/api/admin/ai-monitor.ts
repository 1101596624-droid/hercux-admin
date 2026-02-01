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

// Mock data
export const mockAIOverview: AIOverviewData = {
  today: {
    call_count: 15234,
    total_tokens: 4523000,
    total_cost: 287.45,
    avg_latency_ms: 1250,
    error_rate: 0.008,
  },
  comparisons: {
    calls_vs_yesterday: 0.12,
    cost_vs_yesterday: 0.08,
  },
};

export const mockAITrends: AITrendPoint[] = [
  { time: '00:00', call_count: 523, tokens: 152300, cost: 9.74 },
  { time: '04:00', call_count: 312, tokens: 89200, cost: 5.82 },
  { time: '08:00', call_count: 1245, tokens: 356800, cost: 22.45 },
  { time: '12:00', call_count: 2156, tokens: 623400, cost: 39.87 },
  { time: '16:00', call_count: 1890, tokens: 548200, cost: 35.12 },
  { time: '20:00', call_count: 1678, tokens: 489300, cost: 31.24 },
];

export const mockAICostBreakdown: AICostBreakdown = {
  total_cost: 3847.25,
  budget: 5000,
  budget_usage: 0.769,
  breakdown: [
    { model: 'claude-sonnet-4', call_count: 125000, tokens: 48200000, cost: 2890.00, percentage: 0.751 },
    { model: 'claude-haiku-4', call_count: 89000, tokens: 12500000, cost: 312.00, percentage: 0.081 },
    { model: 'gpt-4o', call_count: 8500, tokens: 3200000, cost: 245.00, percentage: 0.064 },
    { model: 'whisper', call_count: 15200, tokens: 0, cost: 91.00, percentage: 0.024 },
    { model: 'tts', call_count: 18500, tokens: 0, cost: 278.00, percentage: 0.072 },
  ],
  forecast: {
    month_end_cost: 5200,
    will_exceed_budget: true,
  },
};

export const mockAILogs: AILogEntry[] = [
  { id: 'log_001', user_id: 1, user_name: '张明远', scene: 'tutor', model: 'claude-sonnet-4', input_tokens: 1250, output_tokens: 890, latency_ms: 1340, status: 'success', cost: 0.0234, created_at: '2025-01-23T10:30:15Z' },
  { id: 'log_002', user_id: 2, user_name: '李思琪', scene: 'planner', model: 'claude-sonnet-4', input_tokens: 2100, output_tokens: 1560, latency_ms: 2150, status: 'success', cost: 0.0412, created_at: '2025-01-23T10:28:42Z' },
  { id: 'log_003', user_id: 4, user_name: '陈雨萱', scene: 'tutor', model: 'claude-haiku-4', input_tokens: 850, output_tokens: 620, latency_ms: 680, status: 'success', cost: 0.0089, created_at: '2025-01-23T10:25:18Z' },
  { id: 'log_004', user_id: 5, user_name: '刘子轩', scene: 'voice', model: 'whisper', input_tokens: 0, output_tokens: 0, latency_ms: 3200, status: 'success', cost: 0.0180, created_at: '2025-01-23T10:22:05Z' },
  { id: 'log_005', user_id: 1, user_name: '张明远', scene: 'tutor', model: 'claude-sonnet-4', input_tokens: 3500, output_tokens: 0, latency_ms: 5000, status: 'timeout', error_code: 'timeout', cost: 0.0105, created_at: '2025-01-23T10:18:33Z' },
];

export const mockAIAlerts: AIAlert[] = [
  { id: 1, alert_type: 'cost_exceed', severity: 'critical', title: '日成本超过阈值', message: '今日 AI 成本已达 $320，超过设定阈值 $300', metric_value: 320, threshold_value: 300, status: 'open', created_at: '2025-01-23T14:30:00Z' },
  { id: 2, alert_type: 'error_rate', severity: 'warning', title: '错误率上升', message: '过去1小时错误率达到 2.5%，超过阈值 1%', metric_value: 2.5, threshold_value: 1, status: 'acknowledged', created_at: '2025-01-23T12:15:00Z' },
  { id: 3, alert_type: 'user_abuse', severity: 'info', title: '用户调用异常', message: '用户 ID:156 今日调用次数达 250 次', metric_value: 250, threshold_value: 200, status: 'resolved', created_at: '2025-01-23T09:45:00Z', resolved_at: '2025-01-23T10:30:00Z', resolution_note: '已确认为正常使用' },
];

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
    if (cached) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/ai/overview`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch AI overview');
      const data = await response.json();
      setCachedData(cacheKey, data);
      return data;
    } catch {
      return mockAIOverview;
    }
  },

  getTrends: async (period: '24h' | '7d' | '30d' = '24h'): Promise<AITrendPoint[]> => {
    const cacheKey = `ai_monitor_trends_${period}`;
    const cached = getCachedData<AITrendPoint[]>(cacheKey);
    if (cached) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/ai/trends?period=${period}`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch AI trends');
      const data = await response.json();
      setCachedData(cacheKey, data);
      return data;
    } catch {
      return mockAITrends;
    }
  },

  getCosts: async (): Promise<AICostBreakdown> => {
    const cacheKey = 'ai_monitor_costs';
    const cached = getCachedData<AICostBreakdown>(cacheKey);
    if (cached) return cached;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/ai/costs`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch AI costs');
      const data = await response.json();
      setCachedData(cacheKey, data);
      return data;
    } catch {
      return mockAICostBreakdown;
    }
  },

  getLogs: async (params?: { page?: number; limit?: number; scene?: string; status?: string }): Promise<{ data: AILogEntry[]; total: number }> => {
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
      return response.json();
    } catch {
      return { data: mockAILogs, total: mockAILogs.length };
    }
  },

  getAlerts: async (status?: string): Promise<{ data: AIAlert[]; stats: { open: number; acknowledged: number; resolved: number } }> => {
    const cacheKey = `ai_monitor_alerts_${status || 'all'}`;
    const cached = getCachedData<{ data: AIAlert[]; stats: { open: number; acknowledged: number; resolved: number } }>(cacheKey);
    if (cached) return cached;

    try {
      const url = status
        ? `${API_BASE_URL}/admin/ai/alerts?status=${status}`
        : `${API_BASE_URL}/admin/ai/alerts`;
      const response = await fetch(url, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) throw new Error('Failed to fetch AI alerts');
      const data = await response.json();
      setCachedData(cacheKey, data);
      return data;
    } catch {
      return {
        data: mockAIAlerts,
        stats: { open: 1, acknowledged: 1, resolved: 1 },
      };
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
    Object.keys(cache).forEach(key => {
      if (key.startsWith('ai_monitor_alerts')) {
        delete cache[key];
      }
    });
    return response.json();
  },

  // Force refresh - clears cache and fetches fresh data
  clearCache: () => {
    Object.keys(cache).forEach(key => {
      if (key.startsWith('ai_monitor_')) {
        delete cache[key];
      }
    });
  },
};
