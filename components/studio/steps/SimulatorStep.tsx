'use client';

/**
 * SimulatorStep - 模拟器步骤组件
 * 用于 Studio 课程编辑器中渲染HTML模拟器
 */

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { Play, RotateCcw } from 'lucide-react';
import type { SimulatorSpec } from '@/types/coursePackage';

// 动态导入 HTMLSimulatorRenderer 避免 SSR 问题
const HTMLSimulatorRenderer = dynamic(
  () => import('@/components/simulator-engine/HTMLSimulatorRenderer'),
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

interface SimulatorStepProps {
  simulator_spec: SimulatorSpec;
}

export function SimulatorStep({ simulator_spec }: SimulatorStepProps) {
  const [isStarted, setIsStarted] = useState(false);
  const [key, setKey] = useState(0);

  const spec = simulator_spec as any;

  // 获取HTML内容（支持多种字段名）
  const htmlContent = spec?.html_content || spec?.htmlContent || spec?.code || spec?.custom_code || '';

  const handleStart = () => {
    setIsStarted(true);
  };

  const handleReset = () => {
    setIsStarted(false);
    setKey(k => k + 1);
  };

  if (!htmlContent) {
    return (
      <div className="flex items-center justify-center h-64 bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl">
        <p className="text-slate-400">模拟器内容为空</p>
      </div>
    );
  }

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* 控制按钮 */}
      <div className="absolute top-2 left-2 z-20 flex items-center gap-2">
        {!isStarted ? (
          <button
            onClick={handleStart}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors shadow-lg"
          >
            <Play size={14} />
            开始
          </button>
        ) : (
          <button
            onClick={handleReset}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-600 text-white text-sm font-medium rounded-lg hover:bg-slate-700 transition-colors shadow-lg"
          >
            <RotateCcw size={14} />
            重置
          </button>
        )}
        {isStarted && (
          <span className="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded-lg">
            运行中
          </span>
        )}
      </div>

      {/* 未开始时显示提示 */}
      {!isStarted && (
        <div
          className="flex items-center justify-center"
          style={{ height: 500, backgroundColor: '#1e293b' }}
        >
          <div className="text-center">
            <p className="text-slate-400 text-lg mb-2">点击左上角"开始"按钮</p>
            <p className="text-slate-500 text-sm">启动模拟器</p>
          </div>
        </div>
      )}

      {/* 模拟器内容 */}
      {isStarted && (
        <HTMLSimulatorRenderer
          key={key}
          htmlContent={htmlContent}
          height={500}
          onReady={() => console.log('HTML Simulator ready')}
          onError={(err) => console.error('HTML Simulator error:', err)}
        />
      )}
    </div>
  );
}

export default SimulatorStep;
