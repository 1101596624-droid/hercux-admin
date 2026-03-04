/**
 * Authentication Store - User authentication state management
 * 后台应用：3天不活动自动登出
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001/api';

// 不活动超时时间：3天（毫秒）
const INACTIVITY_TIMEOUT = 3 * 24 * 60 * 60 * 1000;

// Token 刷新阈值：剩余12小时时刷新
const TOKEN_REFRESH_THRESHOLD = 12 * 60 * 60 * 1000;

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: 'student' | 'instructor' | 'admin';
  createdAt: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  lastActivityTime: number | null;  // 最后活动时间戳
  tokenExpiresAt: number | null;    // Token 过期时间戳

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  updateActivity: () => void;        // 更新活动时间
  checkSession: () => boolean;       // 检查会话是否有效
  refreshToken: () => Promise<void>; // 刷新 Token
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      lastActivityTime: null,
      tokenExpiresAt: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });

        try {
          // Login to get token
          const formData = new URLSearchParams();
          formData.append('username', email);
          formData.append('password', password);

          const loginResponse = await fetch(`${API_BASE_URL}/v1/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
              'X-Client-Type': 'admin',  // 后台应用标识，token有效期3天
            },
            body: formData,
          });

          if (!loginResponse.ok) {
            const error = await loginResponse.json().catch(() => ({ detail: '登录失败' }));
            console.error('Login failed:', error);
            set({
              isLoading: false,
              error: error.detail || error.message || '邮箱或密码错误'
            });
            return;
          }

          const loginData = await loginResponse.json();
          const { access_token, expires_in } = loginData;

          if (!access_token) {
            console.error('No access token in response');
            set({
              isLoading: false,
              error: '登录失败：未收到访问令牌'
            });
            return;
          }

          // Store token in localStorage
          if (typeof window !== 'undefined') {
            localStorage.setItem('auth_token', access_token);
          }

          // Get user info
          const userResponse = await fetch(`${API_BASE_URL}/v1/auth/me`, {
            headers: {
              'Authorization': `Bearer ${access_token}`,
            },
          });

          if (!userResponse.ok) {
            const errorText = await userResponse.text();
            console.error('Failed to get user info:', errorText);
            throw new Error('Failed to get user info');
          }

          const userData = await userResponse.json();

          const user: User = {
            id: String(userData.id),
            email: userData.email,
            name: userData.full_name || userData.username,
            avatar: userData.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(userData.username)}&background=DC2626&color=fff`,
            role: 'admin',
            createdAt: userData.created_at,
          };

          // 计算 Token 过期时间（默认3天）
          const expiresInMs = (expires_in || 3 * 24 * 60 * 60) * 1000;
          const tokenExpiresAt = Date.now() + expiresInMs;

          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
            lastActivityTime: Date.now(),
            tokenExpiresAt,
          });
        } catch (error) {
          console.error('Login error:', error);
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : '登录失败，请重试'
          });
        }
      },

      register: async (email: string, password: string, name: string) => {
        set({ isLoading: true, error: null });

        try {
          const response = await fetch(`${API_BASE_URL}/v1/auth/register`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              email,
              username: email.split('@')[0],
              password,
              full_name: name,
            }),
          });

          if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: '注册失败' }));
            set({
              isLoading: false,
              error: error.detail || '注册失败，请重试'
            });
            return;
          }

          // Auto-login after registration
          await useAuthStore.getState().login(email, password);
        } catch (error) {
          console.error('Registration error:', error);
          set({
            isLoading: false,
            error: '注册失败，请重试'
          });
        }
      },

      logout: () => {
        // Clear token from localStorage
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
        }

        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
          lastActivityTime: null,
          tokenExpiresAt: null,
        });
      },

      clearError: () => {
        set({ error: null });
      },

      // 更新最后活动时间
      updateActivity: () => {
        const { isAuthenticated } = get();
        if (isAuthenticated) {
          set({ lastActivityTime: Date.now() });
        }
      },

      // 检查会话是否有效（基于不活动时间）
      checkSession: () => {
        const { isAuthenticated, lastActivityTime, tokenExpiresAt, logout, refreshToken } = get();

        if (!isAuthenticated) {
          return false;
        }

        const now = Date.now();

        // 检查是否超过不活动时间（3天）
        if (lastActivityTime && (now - lastActivityTime) > INACTIVITY_TIMEOUT) {
          logout();
          return false;
        }

        // 检查 Token 是否过期
        if (tokenExpiresAt && now > tokenExpiresAt) {
          logout();
          return false;
        }

        // 检查是否需要刷新 Token（剩余12小时时刷新）
        if (tokenExpiresAt && (tokenExpiresAt - now) < TOKEN_REFRESH_THRESHOLD) {
          refreshToken().catch(console.error);
        }

        return true;
      },

      // 刷新 Token
      refreshToken: async () => {
        const { token } = get();
        if (!token) return;

        try {
          const response = await fetch(`${API_BASE_URL}/v1/auth/refresh`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'X-Client-Type': 'admin',
            },
          });

          if (!response.ok) {
            console.error('Token refresh failed');
            return;
          }

          const data = await response.json();
          const { access_token, expires_in } = data;

          if (access_token) {
            // 更新 Token
            if (typeof window !== 'undefined') {
              localStorage.setItem('auth_token', access_token);
            }

            const expiresInMs = (expires_in || 3 * 24 * 60 * 60) * 1000;
            set({
              token: access_token,
              tokenExpiresAt: Date.now() + expiresInMs,
              lastActivityTime: Date.now(),
            });
          }
        } catch (error) {
          console.error('Token refresh error:', error);
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
        lastActivityTime: state.lastActivityTime,
        tokenExpiresAt: state.tokenExpiresAt,
      }),
    }
  )
);

// 初始化时检查会话
if (typeof window !== 'undefined') {
  // 页面加载时检查会话
  const checkOnLoad = () => {
    const store = useAuthStore.getState();
    if (store.isAuthenticated) {
      store.checkSession();
    }
  };

  // 延迟执行，确保 store 已初始化
  setTimeout(checkOnLoad, 100);

  // 监听用户活动事件
  const activityEvents = ['mousedown', 'keydown', 'touchstart', 'scroll'];
  let activityTimeout: NodeJS.Timeout | null = null;

  const handleActivity = () => {
    // 节流：每30秒最多更新一次活动时间
    if (activityTimeout) return;

    activityTimeout = setTimeout(() => {
      activityTimeout = null;
    }, 30000);

    useAuthStore.getState().updateActivity();
  };

  activityEvents.forEach(event => {
    window.addEventListener(event, handleActivity, { passive: true });
  });

  // 页面可见性变化时检查会话
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
      const store = useAuthStore.getState();
      if (store.isAuthenticated) {
        store.checkSession();
        store.updateActivity();
      }
    }
  });
}
