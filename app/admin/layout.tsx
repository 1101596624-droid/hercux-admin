'use client';

import { ReactNode, useEffect, useState, useCallback } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { Sidebar } from '@/components/layout';
import { useAdminAuthStore } from '@/stores/admin/useAdminAuthStore';

interface AdminLayoutProps {
  children: ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [mounted, setMounted] = useState(false);
  const [isChecking, setIsChecking] = useState(true);

  const { isAuthenticated, logout } = useAdminAuthStore();

  // 不需要认证的页面
  const publicPages = ['/admin/login'];
  const isPublicPage = publicPages.includes(pathname);

  // 全屏页面（不需要侧边栏和padding）
  const fullscreenPages = pathname.startsWith('/admin/editor');

  // 验证 token 有效性
  const validateToken = useCallback(async () => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      return false;
    }

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1';
      const response = await fetch(`${API_URL}/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      return response.ok;
    } catch {
      return false;
    }
  }, []);

  // 等待客户端挂载完成
  useEffect(() => {
    setMounted(true);
  }, []);

  // 认证检查 - 每次路由变化时执行
  useEffect(() => {
    if (!mounted) return;

    const checkAuth = async () => {
      setIsChecking(true);

      // 公开页面不需要检查
      if (isPublicPage) {
        setIsChecking(false);
        return;
      }

      // 检查 store 中的认证状态
      const storeAuth = useAdminAuthStore.getState().isAuthenticated;
      const token = localStorage.getItem('auth_token');

      // 没有 token 或 store 未认证，直接跳转登录
      if (!token || !storeAuth) {
        logout();
        router.replace('/admin/login');
        setIsChecking(false);
        return;
      }

      // 验证 token 有效性
      const isValid = await validateToken();
      if (!isValid) {
        logout();
        router.replace('/admin/login');
        setIsChecking(false);
        return;
      }

      setIsChecking(false);
    };

    checkAuth();
  }, [mounted, pathname, isPublicPage, router, logout, validateToken]);

  // 未挂载时显示加载
  if (!mounted || isChecking) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-50">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-red-200 border-t-red-500 rounded-full animate-spin"></div>
          <p className="text-slate-600">加载中...</p>
        </div>
      </div>
    );
  }

  // 公开页面直接渲染
  if (isPublicPage) {
    return <>{children}</>;
  }

  // 未认证
  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-50">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-red-200 border-t-red-500 rounded-full animate-spin"></div>
          <p className="text-slate-600">正在跳转...</p>
        </div>
      </div>
    );
  }

  // 全屏页面（编辑器等）- 不显示侧边栏
  if (fullscreenPages) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <Sidebar />
      <main className="ml-[240px] min-h-screen">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
