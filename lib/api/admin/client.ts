/**
 * Admin API Client
 * Fetch-based client for admin API calls with authentication
 */

// 支持环境变量配置，默认使用统一后端端口 8001
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1';

interface RequestConfig {
  params?: Record<string, string | number | boolean>;
  headers?: Record<string, string>;
}

class AdminAPIClient {
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

  private async request<T = any>(
    endpoint: string,
    method: string,
    data?: unknown,
    config?: RequestConfig
  ): Promise<{ data: T }> {
    let url = `${this.baseURL}${endpoint}`;

    // Add query parameters if provided
    if (config?.params) {
      const params = new URLSearchParams();
      Object.entries(config.params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
      const queryString = params.toString();
      if (queryString) {
        url += `?${queryString}`;
      }
    }

    const headers = {
      ...this.getAuthHeaders(),
      ...config?.headers,
    };

    const options: RequestInit = {
      method,
      headers,
    };

    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);

      // Handle 401 Unauthorized
      if (response.status === 401) {
        if (typeof window !== 'undefined') {
          window.location.href = '/admin/login';
        }
        throw new Error('Unauthorized');
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `API Error: ${response.status} ${response.statusText}`);
      }

      const responseData = await response.json();
      return { data: responseData };
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  async get<T = any>(url: string, config?: RequestConfig) {
    return this.request<T>(url, 'GET', undefined, config);
  }

  async post<T = any>(url: string, data?: unknown, config?: RequestConfig) {
    return this.request<T>(url, 'POST', data, config);
  }

  async put<T = any>(url: string, data?: unknown, config?: RequestConfig) {
    return this.request<T>(url, 'PUT', data, config);
  }

  async delete<T = any>(url: string, config?: RequestConfig) {
    return this.request<T>(url, 'DELETE', undefined, config);
  }

  async patch<T = any>(url: string, data?: unknown, config?: RequestConfig) {
    return this.request<T>(url, 'PATCH', data, config);
  }
}

export const apiClient = new AdminAPIClient(API_BASE_URL);
