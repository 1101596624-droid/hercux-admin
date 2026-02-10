'use client';

/**
 * SimulatorRenderer - 模拟器渲染器（新版本）
 * 只支持：custom（AI生成PixiJS代码）和 iframe（外部嵌入）
 */

import React, { useState, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { Play, RotateCcw, ExternalLink } from 'lucide-react';
import type { SimulatorConfig } from '@/types/editor';

// 动态导入 CustomRenderer 避免 SSR 问题
const CustomRenderer = dynamic(
  () => import('@/components/simulator-engine/CustomRenderer').then(mod => mod.CustomRenderer),
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
  const [isStarted, setIsStarted] = useState(false);
  const [key, setKey] = useState(0);
  const [variables, setVariables] = useState<Record<string, number>>(() => {
    const initial: Record<string, number> = {};
    const vars = config.variables || [];
    vars.forEach((v) => {
      initial[v.name] = v.default ?? 0;
    });
    return initial;
  });

  const handleStart = useCallback(() => {
    setIsStarted(true);
  }, []);

  const handleReset = useCallback(() => {
    setIsStarted(false);
    setKey(k => k + 1);
    // 重置变量
    const initial: Record<string, number> = {};
    const vars = config.variables || [];
    vars.forEach((v) => {
      initial[v.name] = v.default ?? 0;
    });
    setVariables(initial);
  }, [config.variables]);

  const handleVariableChange = useCallback((name: string, value: number) => {
    setVariables(prev => ({ ...prev, [name]: value }));
  }, []);

  // 检查是否有有效的自定义代码
  const hasValidCode = config.mode === 'custom' && config.custom_code;

  // 根据类型渲染
  if (config.type === 'iframe') {
    return <IframeRenderer config={config} />;
  }

  if (config.type === 'custom') {
    if (!hasValidCode) {
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
        {/* 控制按钮 */}
        {!readOnly && (
          <div className="flex gap-2">
            {!isStarted ? (
              <button
                onClick={handleStart}
                className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
              >
                <Play size={16} />
                开始
              </button>
            ) : (
              <button
                onClick={handleReset}
                className="flex items-center gap-2 px-4 py-2 bg-dark-200 text-dark-700 rounded-lg hover:bg-dark-300 transition-colors"
              >
                <RotateCcw size={16} />
                重置
              </button>
            )}
          </div>
        )}

        {/* 模拟器画布 */}
        {(isStarted || readOnly) && (
          <div className="relative">
            <CustomRenderer
              key={key}
              custom_code={config.custom_code!}
              variables={variables}
              onVariableChange={handleVariableChange}
            />
          </div>
        )}

        {/* 变量控制面板 */}
        {isStarted && !readOnly && config.variables && config.variables.length > 0 && (
          <div className="grid grid-cols-1 gap-3 p-4 bg-dark-50 rounded-lg">
            {config.variables.map((variable) => (
              <div key={variable.name} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <label className="font-medium text-dark-700">
                    {variable.label || variable.name}
                  </label>
                  <span className="text-dark-500">
                    {variables[variable.name]?.toFixed(1)} {variable.unit || ''}
                  </span>
                </div>
                <input
                  type="range"
                  min={variable.min ?? 0}
                  max={variable.max ?? 100}
                  step={variable.step ?? 1}
                  value={variables[variable.name] || 0}
                  onChange={(e) => handleVariableChange(variable.name, Number(e.target.value))}
                  className="w-full"
                />
              </div>
            ))}
          </div>
        )}

        {/* 提示信息 */}
        {!isStarted && !readOnly && (
          <div className="text-center text-sm text-dark-500 py-8">
            点击"开始"按钮启动模拟器
          </div>
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
