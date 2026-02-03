/**
 * Admin Auth Store Tests
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { act } from '@testing-library/react'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

// Mock localStorage
const localStorageMock = {
  store: {} as Record<string, string>,
  getItem: vi.fn((key: string) => localStorageMock.store[key] || null),
  setItem: vi.fn((key: string, value: string) => {
    localStorageMock.store[key] = value
  }),
  removeItem: vi.fn((key: string) => {
    delete localStorageMock.store[key]
  }),
  clear: vi.fn(() => {
    localStorageMock.store = {}
  }),
}
Object.defineProperty(window, 'localStorage', { value: localStorageMock })

// Import after mocks
import { useAdminAuthStore } from '@/stores/admin/useAdminAuthStore'

describe('useAdminAuthStore', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.clear()
    // Reset store state
    useAdminAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    })
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('Initial state', () => {
    it('should have correct initial state', () => {
      const state = useAdminAuthStore.getState()

      expect(state.user).toBeNull()
      expect(state.isAuthenticated).toBe(false)
      expect(state.isLoading).toBe(false)
      expect(state.error).toBeNull()
    })
  })

  describe('login', () => {
    const mockAdminUser = {
      id: 1,
      email: 'admin@hercu.com',
      username: 'admin',
      admin_level: 1,
      created_at: '2024-01-01T00:00:00Z',
    }

    it('should login admin successfully', async () => {
      // Mock login response
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          access_token: 'admin-token-123',
          expires_in: 604800,
        }),
      })

      // Mock user info response
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockAdminUser),
      })

      await act(async () => {
        await useAdminAuthStore.getState().login('admin@hercu.com', 'admin123')
      })

      const state = useAdminAuthStore.getState()
      expect(state.isAuthenticated).toBe(true)
      expect(state.user?.email).toBe('admin@hercu.com')
      expect(state.user?.level).toBe(1)
      expect(state.error).toBeNull()
      expect(localStorageMock.setItem).toHaveBeenCalledWith('auth_token', 'admin-token-123')
    })

    it('should handle login failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ detail: '登录失败，请检查用户名和密码' }),
      })

      await act(async () => {
        await useAdminAuthStore.getState().login('admin@hercu.com', 'wrongpassword')
      })

      const state = useAdminAuthStore.getState()
      expect(state.isAuthenticated).toBe(false)
      expect(state.error).toBe('登录失败，请检查用户名和密码')
      expect(state.isLoading).toBe(false)
    })
  })

  describe('logout', () => {
    it('should clear all auth state on logout', async () => {
      // Set up authenticated state
      useAdminAuthStore.setState({
        user: {
          id: 1,
          name: 'admin',
          email: 'admin@hercu.com',
          role: 'admin',
          level: 1,
          permissions: [],
          createdAt: '',
          isActive: true,
        },
        isAuthenticated: true,
      })

      await act(async () => {
        useAdminAuthStore.getState().logout()
      })

      const state = useAdminAuthStore.getState()
      expect(state.user).toBeNull()
      expect(state.isAuthenticated).toBe(false)
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token')
    })
  })

  describe('Permission checks', () => {
    it('should return true for super admin (level 1) on any permission', () => {
      useAdminAuthStore.setState({
        user: {
          id: 1,
          name: 'admin',
          email: 'admin@hercu.com',
          role: 'admin',
          level: 1,
          permissions: [],
          createdAt: '',
          isActive: true,
        },
        isAuthenticated: true,
      })

      expect(useAdminAuthStore.getState().hasPermission('course:create')).toBe(true)
      expect(useAdminAuthStore.getState().hasPermission('user:delete')).toBe(true)
      expect(useAdminAuthStore.getState().canAccessAdminManagement()).toBe(true)
    })

    it('should check permissions for non-super admin', () => {
      useAdminAuthStore.setState({
        user: {
          id: 2,
          name: 'editor',
          email: 'editor@hercu.com',
          role: 'admin',
          level: 2,
          permissions: ['course:create', 'course:edit', 'course:view'],
          createdAt: '',
          isActive: true,
        },
        isAuthenticated: true,
      })

      expect(useAdminAuthStore.getState().hasPermission('course:create')).toBe(true)
      expect(useAdminAuthStore.getState().hasPermission('user:delete')).toBe(false)
      expect(useAdminAuthStore.getState().canAccessAdminManagement()).toBe(false)
    })

    it('should return false when not authenticated', () => {
      useAdminAuthStore.setState({
        user: null,
        isAuthenticated: false,
      })

      expect(useAdminAuthStore.getState().hasPermission('course:create')).toBe(false)
      expect(useAdminAuthStore.getState().hasAnyPermission(['course:create'])).toBe(false)
    })

    it('should check hasAnyPermission correctly', () => {
      useAdminAuthStore.setState({
        user: {
          id: 2,
          name: 'editor',
          email: 'editor@hercu.com',
          role: 'admin',
          level: 2,
          permissions: ['course:create', 'course:edit'],
          createdAt: '',
          isActive: true,
        },
        isAuthenticated: true,
      })

      expect(useAdminAuthStore.getState().hasAnyPermission(['course:create', 'user:delete'])).toBe(true)
      expect(useAdminAuthStore.getState().hasAnyPermission(['user:delete', 'system:config'])).toBe(false)
    })

    it('should check hasAllPermissions correctly', () => {
      useAdminAuthStore.setState({
        user: {
          id: 2,
          name: 'editor',
          email: 'editor@hercu.com',
          role: 'admin',
          level: 2,
          permissions: ['course:create', 'course:edit', 'course:view'],
          createdAt: '',
          isActive: true,
        },
        isAuthenticated: true,
      })

      expect(useAdminAuthStore.getState().hasAllPermissions(['course:create', 'course:edit'])).toBe(true)
      expect(useAdminAuthStore.getState().hasAllPermissions(['course:create', 'user:delete'])).toBe(false)
    })
  })

  describe('getAdminLevel', () => {
    it('should return user level when authenticated', () => {
      useAdminAuthStore.setState({
        user: {
          id: 1,
          name: 'admin',
          email: 'admin@hercu.com',
          role: 'admin',
          level: 2,
          permissions: [],
          createdAt: '',
          isActive: true,
        },
        isAuthenticated: true,
      })

      expect(useAdminAuthStore.getState().getAdminLevel()).toBe(2)
    })

    it('should return default level 3 when not authenticated', () => {
      useAdminAuthStore.setState({
        user: null,
        isAuthenticated: false,
      })

      expect(useAdminAuthStore.getState().getAdminLevel()).toBe(3)
    })
  })

  describe('clearError', () => {
    it('should clear error state', () => {
      useAdminAuthStore.setState({ error: 'Some error' })

      useAdminAuthStore.getState().clearError()

      expect(useAdminAuthStore.getState().error).toBeNull()
    })
  })
})
