'use client';

import { ReactNode } from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: string;
  changeType?: 'up' | 'down';
  icon: ReactNode;
  subtitle?: string;
}

export function StatCard({ title, value, change, changeType, icon, subtitle }: StatCardProps) {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-500 font-medium">{title}</p>
          <p className="text-3xl font-bold text-slate-900 mt-2 tracking-tight">{value}</p>
          {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
        </div>
        <div className="w-12 h-12 rounded-xl bg-slate-50 flex items-center justify-center">
          {icon}
        </div>
      </div>
      {change && (
        <div className={`flex items-center gap-1 mt-4 text-sm font-medium ${changeType === 'up' ? 'text-green-600' : 'text-red-600'}`}>
          {changeType === 'up' ? (
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M7 17l5-5 5 5M7 7l5 5 5-5" />
            </svg>
          ) : (
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M7 7l5 5 5-5M7 17l5-5 5 5" />
            </svg>
          )}
          <span>{change}</span>
          <span className="text-slate-400 font-normal">vs 上周</span>
        </div>
      )}
    </div>
  );
}
