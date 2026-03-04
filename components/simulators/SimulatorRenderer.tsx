'use client';

/**
 * SimulatorRenderer - 模拟器渲染器（V3 - 2026-02-10更新）
 * 只支持：custom（HTML模拟器）和 iframe（外部嵌入）
 */

import React, { useState, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { Play, RotateCcw, ExternalLink } from 'lucide-react';
import type { SimulatorConfig } from '@/types/editor';

// 动态导入 HTMLSimulatorRenderer 避免 SSR 问题
const HTMLSimulatorRenderer = dynamic(
  () => import('@/components/simulator-engine/HTMLSimulatorRenderer').then(mod => mod.default),
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-64 bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl">
        <div className="flex flex-col items-center">
          <div className="w-8 h-8 border-4 border-purple-500 border-t-transparent rounded-full animate-spin" />
          <p className="mt-2 text-sm text-slate-400">加载模拟器...</p>
        </div>
      </div>
    ),
  }
);

interface SimulatorRendererProps {
  config: SimulatorConfig;
  readOnly?: boolean;
  compact?: boolean;
}

export function SimulatorRenderer({ config, readOnly = false, compact = false }: SimulatorRendererProps) {
  const [key, setKey] = useState(0);
  const [isRunning, setIsRunning] = useState(false);

  const handleStart = useCallback(() => {
    setIsRunning(true);
  }, []);

  const handleReset = useCallback(() => {
    setIsRunning(false);
    setKey(k => k + 1);
  }, []);

  // 获取HTML内容（支持多种字段名）
  const htmlContent = config.html_content || config.custom_code || '';

  // 根据类型渲染
  if (config.type === 'iframe') {
    return <IframeRenderer config={config} />;
  }

  if (config.type === 'custom') {
    if (!htmlContent) {
      return (
        <div className="flex flex-col items-center justify-center h-64 bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl text-white p-6">
          <div className="text-center">
            <div className="text-6xl mb-4">🔧</div>
            <h3 className="text-lg font-medium mb-2">模拟器未配置</h3>
            <p className="text-sm text-slate-400">
              请使用 AI 生成功能创建模拟器代码
            </p>
          </div>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {/* 未开始时的提示和按钮 */}
        {!isRunning && (
          <div className="flex flex-col items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl text-white p-6 space-y-6" style={{ aspectRatio: '16/9' }}>
            <div className="text-center">
              <div className="text-6xl mb-4">🎮</div>
              <h3 className="text-lg font-medium mb-2">准备就绪</h3>
              <p className="text-sm text-slate-400 mb-6">
                点击下方按钮启动模拟器
              </p>
            </div>

            {/* 开始按钮 */}
            {!readOnly && (
              <button
                onClick={handleStart}
                className="flex items-center gap-2 px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors shadow-lg"
              >
                <Play size={20} />
                <span className="font-medium">开始运行</span>
              </button>
            )}
          </div>
        )}

        {/* HTML模拟器画布 - 运行时显示 */}
        {isRunning && (
          <>
            {/* 重置按钮 */}
            {!readOnly && (
              <div className="flex gap-2">
                <button
                  onClick={handleReset}
                  className="flex items-center gap-2 px-4 py-2 bg-dark-200 text-dark-700 rounded-lg hover:bg-dark-300 transition-colors"
                >
                  <RotateCcw size={16} />
                  重置
                </button>
              </div>
            )}

            {/* 模拟器画布 */}
            <div className="relative w-full flex justify-center overflow-hidden rounded-lg">
              <HTMLSimulatorRenderer
                key={key}
                htmlContent={htmlContent}
                width={946}
                height={554}
                showBorder={true}
              />
            </div>
          </>
        )}
      </div>
    );
  }

  // 未知类型
  return (
    <div className="flex flex-col items-center justify-center h-64 bg-dark-100 rounded-lg text-dark-500">
      <p>不支持的模拟器类型: {config.type}</p>
    </div>
  );
}

/** Iframe 渲染器 */
function IframeRenderer({ config }: { config: SimulatorConfig }) {
  if (!config.iframeUrl) {
    return (
      <div className="flex flex-col items-center justify-center h-64 bg-dark-100 rounded-lg">
        <ExternalLink size={48} className="text-dark-300 mb-4" />
        <p className="text-dark-500">未配置 URL</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {config.name && (
        <div className="flex items-center justify-between">
          <h3 className="font-medium text-dark-800">{config.name}</h3>
          <a
            href={config.iframeUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700"
          >
            <ExternalLink size={14} />
            在新窗口打开
          </a>
        </div>
      )}
      {config.description && (
        <p className="text-sm text-dark-600">{config.description}</p>
      )}
      <div className="border border-dark-200 rounded-lg overflow-hidden">
        <iframe
          src={config.iframeUrl}
          className="w-full h-[500px]"
          title={config.name || '外部模拟器'}
          sandbox="allow-scripts allow-same-origin allow-forms"
          loading="lazy"
        />
      </div>
    </div>
  );
}
