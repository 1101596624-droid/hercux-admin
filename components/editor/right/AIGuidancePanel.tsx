'use client';

/**
 * AIGuidancePanel - 右侧面板容器
 * AI 教学引导配置
 */

import React, { useState } from 'react';
import { cn } from '@/lib/cn';
import { APISelector } from './APISelector';
import { PersonaEditor } from './PersonaEditor';
import { TriggerList } from './TriggerList';

type TabType = 'api' | 'persona' | 'triggers';

const tabs: { id: TabType; label: string; icon: React.ReactNode }[] = [
  {
    id: 'api',
    label: 'API',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
      </svg>
    ),
  },
  {
    id: 'persona',
    label: '人设',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
    ),
  },
  {
    id: 'triggers',
    label: '触发器',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
  },
];

export function AIGuidancePanel() {
  const [activeTab, setActiveTab] = useState<TabType>('api');

  return (
    <div className="h-full flex flex-col">
      {/* Tab Navigation */}
      <div className="flex-shrink-0 border-b border-dark-100">
        <div className="flex">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'flex-1 flex items-center justify-center gap-1.5 px-3 py-2.5 text-sm font-medium transition-colors',
                activeTab === tab.id
                  ? 'text-primary-600 border-b-2 border-primary-500 bg-primary-50/50'
                  : 'text-dark-500 hover:text-dark-700 hover:bg-dark-50'
              )}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-auto p-4">
        {activeTab === 'api' && <APISelector />}
        {activeTab === 'persona' && <PersonaEditor />}
        {activeTab === 'triggers' && <TriggerList />}
      </div>

      {/* Footer Info */}
      <div className="flex-shrink-0 p-3 border-t border-dark-100 bg-dark-50">
        <div className="flex items-center gap-2 text-xs text-dark-500">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>AI 引导配置将应用于当前选中的小节</span>
        </div>
      </div>
    </div>
  );
}
