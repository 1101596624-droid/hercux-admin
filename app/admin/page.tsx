'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAdminAuthStore } from '@/stores/admin/useAdminAuthStore';

export default function AdminPage() {
  const router = useRouter();
  const isAuthenticated = useAdminAuthStore((state) => state.isAuthenticated);

  useEffect(() => {
    if (isAuthenticated) {
      router.replace('/admin/dashboard');
    } else {
      router.replace('/admin/login');
    }
  }, [isAuthenticated, router]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-slate-50">
      <div className="flex flex-col items-center gap-4">
        <div className="w-12 h-12 border-4 border-red-200 border-t-red-500 rounded-full animate-spin"></div>
        <p className="text-slate-600">正在跳转...</p>
      </div>
    </div>
  );
}
