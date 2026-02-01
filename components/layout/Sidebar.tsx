'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useState } from 'react';
import { useAdminAuthStore } from '@/stores/admin/useAdminAuthStore';
import { ADMIN_LEVEL_NAMES } from '@/types';

interface NavItem {
  href: string;
  label: string;
  icon: React.ReactNode;
  active: boolean;
  disabled?: boolean;
  requireLevel1?: boolean;
}

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout, canAccessAdminManagement, getAdminLevelName } = useAdminAuthStore();
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  const navItems: NavItem[] = [
    {
      href: '/admin/dashboard',
      label: '课程管理中心',
      active: true,
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="3" y="3" width="7" height="7" rx="1" />
          <rect x="14" y="3" width="7" height="7" rx="1" />
          <rect x="3" y="14" width="7" height="7" rx="1" />
          <rect x="14" y="14" width="7" height="7" rx="1" />
        </svg>
      ),
    },
    {
      href: '/admin/courses',
      label: '内容编辑器',
      active: true,
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
        </svg>
      ),
    },
    {
      href: '/admin/analytics',
      label: '数据分析',
      active: true,
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M18 20V10" />
          <path d="M12 20V4" />
          <path d="M6 20v-6" />
        </svg>
      ),
    },
    {
      href: '/admin/users',
      label: '用户管理',
      active: true,
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
          <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
      ),
    },
    {
      href: '/admin/ai-monitor',
      label: 'AI API 监控',
      active: true,
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z" />
          <circle cx="7.5" cy="14.5" r="1.5" />
          <circle cx="16.5" cy="14.5" r="1.5" />
        </svg>
      ),
    },
    {
      href: '/admin/api-config',
      label: 'API 管理',
      active: true,
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 2L2 7l10 5 10-5-10-5z" />
          <path d="M2 17l10 5 10-5" />
          <path d="M2 12l10 5 10-5" />
        </svg>
      ),
    },
    {
      href: '/admin/processors',
      label: '处理器管理',
      active: true,
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
        </svg>
      ),
    },
    {
      href: '/admin/achievement-center',
      label: '勋章中心',
      active: true,
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="8" r="6" />
          <path d="M15.477 12.89L17 22l-5-3-5 3 1.523-9.11" />
        </svg>
      ),
    },
    {
      href: '/admin/permissions',
      label: '协作与权限',
      active: true,
      requireLevel1: true,
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
          <path d="M7 11V7a5 5 0 0 1 10 0v4" />
        </svg>
      ),
    },
    {
      href: '/admin/settings',
      label: '系统设置',
      active: true,
      icon: (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="3" />
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
        </svg>
      ),
    },
  ];

  const isActive = (href: string) => {
    if (href === '/admin/dashboard') {
      return pathname === '/admin/dashboard' || pathname === '/admin';
    }
    return pathname.startsWith(href);
  };

  const handleLogout = () => {
    logout();
    router.push('/admin/login');
    setShowLogoutConfirm(false);
  };

  return (
    <>
      <aside className="fixed left-0 top-0 h-screen w-[240px] bg-[#1a1f2e] flex flex-col z-50">
        {/* Logo */}
        <div className="px-6 py-6">
          <Link href="/admin/dashboard" className="flex items-center gap-3">
            <div className="w-9 h-9 bg-red-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">H</span>
            </div>
            <span className="text-white font-semibold text-lg tracking-tight">
              hercuX <span className="text-red-400">Manager</span>
            </span>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map((item) => {
            const active = isActive(item.href);
            const disabled = item.disabled || (item.requireLevel1 && !canAccessAdminManagement());

            if (disabled) {
              return (
                <div
                  key={item.label}
                  className="flex items-center gap-3 px-4 py-3 rounded-xl text-gray-500 cursor-not-allowed"
                  title={item.requireLevel1 ? '需要超级管理员权限' : '功能开发中'}
                >
                  {item.icon}
                  <span className="text-sm font-medium">{item.label}</span>
                </div>
              );
            }

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-xl transition-all
                  ${active
                    ? 'bg-red-500 text-white shadow-lg shadow-red-500/30'
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }
                `}
              >
                {item.icon}
                <span className="text-sm font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* User Section */}
        <div className="px-3 py-4 border-t border-white/10">
          <button
            onClick={() => setShowLogoutConfirm(true)}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-gray-400 hover:text-white hover:bg-white/5 transition-all"
          >
            <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold ${
              user?.level === 1 ? 'bg-red-500' : user?.level === 2 ? 'bg-blue-500' : 'bg-gray-600'
            }`}>
              {user?.name?.charAt(0).toUpperCase() || 'A'}
            </div>
            <div className="flex-1 text-left">
              <div className="text-sm font-medium text-white">{user?.name || 'Admin'}</div>
              <div className="text-xs text-gray-500">{getAdminLevelName()}</div>
            </div>
          </button>
        </div>
      </aside>

      {/* Logout Confirmation Modal */}
      {showLogoutConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[100]">
          <div className="bg-white rounded-2xl p-6 w-[400px] shadow-2xl">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">确认退出登录</h3>
            <p className="text-gray-600 mb-6">您确定要退出登录吗？退出后需要重新登录才能访问管理系统。</p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowLogoutConfirm(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-white bg-red-500 rounded-lg hover:bg-red-600 transition-colors"
              >
                确认退出
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
