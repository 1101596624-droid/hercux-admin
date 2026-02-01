'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAdminAuthStore } from '@/stores/admin/useAdminAuthStore';

export default function AdminLoginPage() {
  const router = useRouter();
  const { login, isLoading, error } = useAdminAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await login(email, password);
    // 登录成功后跳转由 layout 处理
    router.replace('/admin/dashboard');
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-[#1a1f2e] flex-col justify-between p-12">
        <div>
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">H</span>
            </div>
            <span className="text-white font-semibold text-xl tracking-tight">
              hercuX <span className="text-red-400">Manager</span>
            </span>
          </div>
        </div>

        {/* Center Content */}
        <div className="flex-1 flex flex-col justify-center">
          <h1 className="text-5xl font-bold text-white leading-tight mb-6">
            深度认知<br />
            <span className="text-red-400">学习系统</span>
          </h1>
          <p className="text-gray-400 text-lg max-w-md">
            HERCU 后台管理系统，为教研团队提供专业的课程管理、内容编辑和数据分析工具。
          </p>

          {/* Feature List */}
          <div className="mt-12 space-y-4">
            <div className="flex items-center gap-3 text-gray-300">
              <div className="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
                  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
                </svg>
              </div>
              <span>课程内容管理</span>
            </div>
            <div className="flex items-center gap-3 text-gray-300">
              <div className="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                </svg>
              </div>
              <span>AI 辅助课程生成</span>
            </div>
            <div className="flex items-center gap-3 text-gray-300">
              <div className="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 20V10" />
                  <path d="M12 20V4" />
                  <path d="M6 20v-6" />
                </svg>
              </div>
              <span>教研数据统计</span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-gray-500 text-sm">
          © 2024 HERCU. All rights reserved.
        </div>
      </div>

      {/* Right Panel - Login Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-slate-50">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="lg:hidden flex items-center gap-3 mb-12 justify-center">
            <div className="w-10 h-10 bg-red-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">H</span>
            </div>
            <span className="text-slate-900 font-semibold text-xl tracking-tight">
              hercuX <span className="text-red-500">Manager</span>
            </span>
          </div>

          {/* Login Card */}
          <div className="bg-white rounded-2xl shadow-xl shadow-slate-200/50 p-8">
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-slate-900">欢迎回来</h2>
              <p className="text-slate-500 mt-2">请登录您的管理员账号</p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-100 rounded-xl">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-red-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="12" y1="8" x2="12" y2="12" />
                    <line x1="12" y1="16" x2="12.01" y2="16" />
                  </svg>
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              </div>
            )}

            {/* Login Form */}
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-2">
                  用户名 / 邮箱
                </label>
                <input
                  id="email"
                  type="text"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="请输入用户名或邮箱"
                  className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 transition-all bg-slate-50"
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-slate-700 mb-2">
                  密码
                </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="请输入密码"
                  className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 transition-all bg-slate-50"
                />
              </div>

              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 rounded border-slate-300 text-red-500 focus:ring-red-500"
                  />
                  <span className="text-sm text-slate-600">记住登录状态</span>
                </label>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3 bg-red-500 text-white rounded-xl font-medium hover:bg-red-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    登录中...
                  </>
                ) : (
                  '登录'
                )}
              </button>
            </form>

            {/* Divider */}
            <div className="mt-8 pt-6 border-t border-slate-100">
              <p className="text-center text-sm text-slate-500">
                使用 HERCU 主应用账号登录
              </p>
            </div>
          </div>

          {/* Help Text */}
          <p className="text-center text-slate-400 text-sm mt-6">
            遇到问题？请联系系统管理员
          </p>
        </div>
      </div>
    </div>
  );
}
