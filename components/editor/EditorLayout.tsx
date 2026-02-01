'use client';

/**
 * EditorLayout - 三段式布局容器
 * 左侧：课程结构编辑
 * 中间：节点配置
 * 右侧：AI 教学引导配置
 */

import React, { useState } from 'react';
import { cn } from '@/lib/cn';

interface EditorLayoutProps {
  leftPanel: React.ReactNode;
  centerPanel: React.ReactNode;
  rightPanel: React.ReactNode;
  header?: React.ReactNode;
}

export function EditorLayout({
  leftPanel,
  centerPanel,
  rightPanel,
  header,
}: EditorLayoutProps) {
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);

  return (
    <div className="h-screen flex flex-col bg-dark-50">
      {/* Header */}
      {header && (
        <div className="flex-shrink-0 border-b border-dark-200 bg-white">
          {header}
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel */}
        <div
          className={cn(
            'flex-shrink-0 border-r border-dark-200 bg-white transition-all duration-300 overflow-hidden',
            leftCollapsed ? 'w-12' : 'w-80'
          )}
        >
          <div className="h-full flex flex-col">
            {/* Panel Header */}
            <div className="flex-shrink-0 h-12 flex items-center justify-between px-3 border-b border-dark-100">
              {!leftCollapsed && (
                <span className="font-medium text-dark-900">课程结构</span>
              )}
              <button
                onClick={() => setLeftCollapsed(!leftCollapsed)}
                className="p-1.5 rounded hover:bg-dark-100 text-dark-500 hover:text-dark-700"
                title={leftCollapsed ? '展开' : '收起'}
              >
                <svg
                  className={cn('w-5 h-5 transition-transform', leftCollapsed && 'rotate-180')}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M11 19l-7-7 7-7m8 14l-7-7 7-7"
                  />
                </svg>
              </button>
            </div>

            {/* Panel Content */}
            {!leftCollapsed && (
              <div className="flex-1 overflow-auto">
                {leftPanel}
              </div>
            )}
          </div>
        </div>

        {/* Center Panel */}
        <div className="flex-1 flex flex-col overflow-hidden bg-dark-50">
          <div className="flex-shrink-0 h-12 flex items-center px-4 border-b border-dark-200 bg-white">
            <span className="font-medium text-dark-900">节点配置</span>
          </div>
          <div className="flex-1 overflow-auto p-4">
            {centerPanel}
          </div>
        </div>

        {/* Right Panel */}
        <div
          className={cn(
            'flex-shrink-0 border-l border-dark-200 bg-white transition-all duration-300 overflow-hidden',
            rightCollapsed ? 'w-12' : 'w-96'
          )}
        >
          <div className="h-full flex flex-col">
            {/* Panel Header */}
            <div className="flex-shrink-0 h-12 flex items-center justify-between px-3 border-b border-dark-100">
              <button
                onClick={() => setRightCollapsed(!rightCollapsed)}
                className="p-1.5 rounded hover:bg-dark-100 text-dark-500 hover:text-dark-700"
                title={rightCollapsed ? '展开' : '收起'}
              >
                <svg
                  className={cn('w-5 h-5 transition-transform', !rightCollapsed && 'rotate-180')}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 5l7 7-7 7M5 5l7 7-7 7"
                  />
                </svg>
              </button>
              {!rightCollapsed && (
                <span className="font-medium text-dark-900">AI 教学引导</span>
              )}
            </div>

            {/* Panel Content */}
            {!rightCollapsed && (
              <div className="flex-1 overflow-auto">
                {rightPanel}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
