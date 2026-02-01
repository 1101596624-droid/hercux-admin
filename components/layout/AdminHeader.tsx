'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Button } from '@/components/ui';
import { useAdminAuthStore } from '@/stores/admin/useAdminAuthStore';

export function AdminHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isAuthenticated, logout } = useAdminAuthStore();

  const navItems = [
    { href: '/admin/dashboard', label: '仪表盘', icon: '📊' },
    { href: '/admin/users', label: '用户管理', icon: '👥' },
    { href: '/admin/courses', label: '课程管理', icon: '📚' },
    { href: '/admin/progress', label: '进度管理', icon: '📈' },
  ];

  const isActive = (href: string) => {
    if (href === '/admin/dashboard') return pathname === '/admin/dashboard' || pathname === '/admin';
    return pathname.startsWith(href);
  };

  const handleLogout = () => {
    logout();
    router.push('/admin/login');
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-dark-200 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/80">
      <div className="container mx-auto px-6">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/admin/dashboard" className="flex items-center gap-3 group">
            <div className="text-3xl group-hover:scale-110 transition-transform">🏋️</div>
            <div className="flex flex-col">
              <span className="text-xl font-bold text-dark-900 tracking-tight">HERCU</span>
              <span className="text-xs text-primary-600 font-medium -mt-1">管理后台</span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center gap-1">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`
                  flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all
                  ${isActive(item.href)
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-dark-600 hover:bg-dark-50 hover:text-dark-900'
                  }
                `}
              >
                <span className="text-lg">{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            ))}
          </nav>

          {/* User Menu */}
          <div className="flex items-center gap-4">
            {/* Notifications */}
            <button className="relative p-2 rounded-lg hover:bg-dark-50 transition-colors">
              <svg className="w-5 h-5 text-dark-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>

            {/* User Avatar */}
            {isAuthenticated && user ? (
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-3 p-1 pr-4 rounded-full hover:bg-dark-50 transition-colors">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-blue-600 flex items-center justify-center text-white font-semibold text-sm">
                    {user.name?.charAt(0).toUpperCase() || 'A'}
                  </div>
                  <div className="hidden lg:flex flex-col">
                    <span className="text-sm font-medium text-dark-900">{user.name}</span>
                    <span className="text-xs text-primary-600">
                      {user.role === 'super_admin' ? '超级管理员' : user.role === 'admin' ? '管理员' : '版主'}
                    </span>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                >
                  退出
                </Button>
              </div>
            ) : (
              <Link href="/admin/login">
                <Button variant="primary" size="sm">登录</Button>
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <nav className="lg:hidden border-t border-dark-200 bg-white overflow-x-auto">
        <div className="flex items-center gap-1 px-4 py-2">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`
                flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium whitespace-nowrap transition-all
                ${isActive(item.href)
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-dark-600 hover:bg-dark-50'
                }
              `}
            >
              <span className="text-base">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </div>
      </nav>
    </header>
  );
}
