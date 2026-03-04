/**
 * App API Client (non-admin)
 * Returns response payload directly to match existing app API modules.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api';

type QueryValue = string | number | boolean | null | undefined;

interface RequestConfig extends RequestInit {
  params?: Record<string, QueryValue>;
}

const FETCH_INIT_KEYS = new Set([
  'method',
  'headers',
  'body',
  'mode',
  'cache',
  'credentials',
  'redirect',
  'referrer',
  'referrerPolicy',
  'integrity',
  'keepalive',
  'signal',
  'window',
  'duplex',
  'priority',
]);

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private getAuthHeaders(): Record<string, string> {
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
    return {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    };
  }

  private buildUrl(endpoint: string, params?: Record<string, QueryValue>): string {
    const base = `${this.baseURL}${endpoint}`;
    if (!params) return base;

    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        searchParams.append(key, String(value));
      }
    });

    const query = searchParams.toString();
    return query ? `${base}?${query}` : base;
  }

  private normalizeConfig(config?: RequestConfig): {
    params?: Record<string, QueryValue>;
    init: RequestInit;
  } {
    if (!config) return { init: {} };

    const { params, ...rest } = config as Record<string, unknown>;
    const inferredParams: Record<string, QueryValue> = {};
    const fetchInit: Record<string, unknown> = {};

    Object.entries(rest).forEach(([key, value]) => {
      if (FETCH_INIT_KEYS.has(key)) {
        fetchInit[key] = value;
      } else if (value === null || value === undefined || ['string', 'number', 'boolean'].includes(typeof value)) {
        inferredParams[key] = value as QueryValue;
      }
    });

    const explicitParams =
      params && typeof params === 'object' && !Array.isArray(params)
        ? (params as Record<string, QueryValue>)
        : undefined;

    return {
      params: explicitParams ?? (Object.keys(inferredParams).length > 0 ? inferredParams : undefined),
      init: fetchInit as RequestInit,
    };
  }

  private async request<T>(endpoint: string, config: RequestConfig = {}): Promise<T> {
    const { params, init } = this.normalizeConfig(config);
    const url = this.buildUrl(endpoint, params);

    const headers: Record<string, string> = {
      ...this.getAuthHeaders(),
      ...(init.headers as Record<string, string> | undefined),
    };

    const options: RequestInit = {
      ...init,
      headers,
    };

    try {
      const response = await fetch(url, options);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.message || `API Error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', endpoint, error);
      throw error;
    }
  }

  async get<T = any>(endpoint: string, config?: RequestConfig | Record<string, QueryValue>): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET', ...(config as RequestConfig | undefined) });
  }

  async post<T = any>(endpoint: string, data?: unknown, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data !== undefined ? JSON.stringify(data) : undefined,
      ...config,
    });
  }

  async put<T = any>(endpoint: string, data?: unknown, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data !== undefined ? JSON.stringify(data) : undefined,
      ...config,
    });
  }

  async patch<T = any>(endpoint: string, data?: unknown, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: data !== undefined ? JSON.stringify(data) : undefined,
      ...config,
    });
  }

  async delete<T = any>(endpoint: string, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE', ...config });
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
