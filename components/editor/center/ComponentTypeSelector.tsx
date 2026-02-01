'use client';

/**
 * ComponentTypeSelector - 组件类型选择器
 * 可视化选择节点的组件类型
 */

import React from 'react';
import { cn } from '@/lib/cn';
import type { ComponentType } from '@/types/editor';
import { COMPONENT_TYPE_LABELS } from '@/types/editor';

interface ComponentTypeSelectorProps {
  value: ComponentType;
  onChange: (type: ComponentType) => void;
}

const componentTypeConfig: Record<ComponentType, { icon: React.ReactNode; description: string; color: string }> = {
  video: {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    description: '视频播放器，支持字幕',
    color: 'bg-blue-50 border-blue-200 text-blue-700',
  },
  simulator: {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    description: '交互式模拟器',
    color: 'bg-purple-50 border-purple-200 text-purple-700',
  },
  assessment: {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
      </svg>
    ),
    description: '测验题目',
    color: 'bg-green-50 border-green-200 text-green-700',
  },
  illustrated_content: {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
      </svg>
    ),
    description: '图文内容',
    color: 'bg-orange-50 border-orange-200 text-orange-700',
  },
  text_content: {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
    description: '富文本内容',
    color: 'bg-gray-50 border-gray-200 text-gray-700',
  },
  ai_tutor: {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
      </svg>
    ),
    description: 'AI 对话导师',
    color: 'bg-indigo-50 border-indigo-200 text-indigo-700',
  },
  quick_check: {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    description: '快速检测',
    color: 'bg-teal-50 border-teal-200 text-teal-700',
  },
  practice: {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
      </svg>
    ),
    description: '简单练习',
    color: 'bg-yellow-50 border-yellow-200 text-yellow-700',
  },
  exam: {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
    ),
    description: '考试',
    color: 'bg-red-50 border-red-200 text-red-700',
  },
  model_3d: {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" />
      </svg>
    ),
    description: '3D 模型',
    color: 'bg-pink-50 border-pink-200 text-pink-700',
  },
  reading: {
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
    ),
    description: '阅读材料',
    color: 'bg-cyan-50 border-cyan-200 text-cyan-700',
  },
};

export function ComponentTypeSelector({ value, onChange }: ComponentTypeSelectorProps) {
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-dark-700">
        组件类型
      </label>
      <div className="grid grid-cols-2 gap-3">
        {(Object.keys(componentTypeConfig) as ComponentType[]).map((type) => {
          const config = componentTypeConfig[type];
          const isSelected = value === type;

          return (
            <button
              key={type}
              onClick={() => onChange(type)}
              className={cn(
                'flex flex-col items-center gap-2 p-4 rounded-lg border-2 transition-all',
                isSelected
                  ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-200'
                  : 'border-dark-200 hover:border-dark-300 hover:bg-dark-50'
              )}
            >
              <span className={cn('p-2 rounded-lg', config.color)}>
                {config.icon}
              </span>
              <span className="text-sm font-medium text-dark-800">
                {COMPONENT_TYPE_LABELS[type]}
              </span>
              <span className="text-xs text-dark-500 text-center">
                {config.description}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
