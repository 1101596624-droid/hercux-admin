'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    router.push('/admin/login');
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="text-center">
        <div className="w-12 h-12 border-4 border-red-200 border-t-red-500 rounded-full animate-spin mx-auto mb-4"></div>
        <h2 className="text-xl font-bold text-slate-900 mb-2">
          HERCU Manager
        </h2>
        <p className="text-slate-600">正在跳转到登录页...</p>
      </div>
    </div>
  );
}
