import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { AdminUser, AdminPermission, AdminLevel } from '@/types';
import { ADMIN_LEVEL_PERMISSIONS, ADMIN_LEVEL_NAMES } from '@/types';

interface AdminAuthState {
  user: AdminUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setUser: (user: AdminUser | null) => void;
  clearError: () => void;
  hasPermission: (permission: AdminPermission) => boolean;
  hasAnyPermission: (permissions: AdminPermission[]) => boolean;
  hasAllPermissions: (permissions: AdminPermission[]) => boolean;
  getAdminLevel: () => AdminLevel;
  getAdminLevelName: () => string;
  canAccessAdminManagement: () => boolean;
}

export const useAdminAuthStore = create<AdminAuthState>()(
  devtools(
    persist(
      (set, get) => ({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,

        login: async (email: string, password: string) => {
          set({ isLoading: true, error: null });

          try {
            // 使用主应用的登录API
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
            console.log('Admin login API URL:', API_URL);

            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);

            console.log('Sending login request to:', `${API_URL}/auth/login`);
            const response = await fetch(`${API_URL}/auth/login`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Client-Type': 'admin',
              },
              body: formData,
            });

            console.log('Login response status:', response.status);

            if (!response.ok) {
              const errorData = await response.json().catch(() => ({}));
              console.error('Login failed:', errorData);
              throw new Error(errorData.detail || '登录失败，请检查用户名和密码');
            }

            const data = await response.json();

            // 存储 token (使用与主应用相同的key)
            localStorage.setItem('auth_token', data.access_token);

            // 获取用户信息
            const userResponse = await fetch(`${API_URL}/auth/me`, {
              headers: { 'Authorization': `Bearer ${data.access_token}` },
            });

            if (userResponse.ok) {
              const userData = await userResponse.json();

              // 根据用户角色确定管理员等级 (默认为1级超级管理员用于演示)
              const adminLevel: AdminLevel = userData.admin_level || 1;

              set({
                user: {
                  id: userData.id,
                  name: userData.username,
                  email: userData.email,
                  role: 'admin',
                  level: adminLevel,
                  permissions: ADMIN_LEVEL_PERMISSIONS[adminLevel],
                  createdAt: userData.created_at || new Date().toISOString(),
                  isActive: true,
                },
                isAuthenticated: true,
                isLoading: false,
                error: null,
              });
            } else {
              throw new Error('获取用户信息失败');
            }
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : '登录失败',
              isLoading: false,
            });
          }
        },

        logout: () => {
          localStorage.removeItem('auth_token');
          set({
            user: null,
            isAuthenticated: false,
            error: null,
          });
        },

        setUser: (user) => {
          set({
            user,
            isAuthenticated: !!user,
          });
        },

        clearError: () => {
          set({ error: null });
        },

        hasPermission: (permission) => {
          const { user } = get();
          if (!user) return false;
          if (user.level === 1) return true; // 超级管理员拥有所有权限
          return user.permissions.includes(permission);
        },

        hasAnyPermission: (permissions) => {
          const { user } = get();
          if (!user) return false;
          if (user.level === 1) return true;
          return permissions.some((p) => user.permissions.includes(p));
        },

        hasAllPermissions: (permissions) => {
          const { user } = get();
          if (!user) return false;
          if (user.level === 1) return true;
          return permissions.every((p) => user.permissions.includes(p));
        },

        getAdminLevel: () => {
          const { user } = get();
          return user?.level || 3;
        },

        getAdminLevelName: () => {
          const { user } = get();
          return ADMIN_LEVEL_NAMES[user?.level || 3];
        },

        canAccessAdminManagement: () => {
          const { user } = get();
          return user?.level === 1;
        },
      }),
      {
        name: 'admin-auth-storage',
        partialize: (state) => ({
          user: state.user,
          isAuthenticated: state.isAuthenticated,
        }),
      }
    ),
    { name: 'AdminAuthStore' }
  )
);
