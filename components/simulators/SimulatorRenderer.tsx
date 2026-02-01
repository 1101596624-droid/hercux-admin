'use client';

/**
 * SimulatorRenderer - 模拟器渲染器
 * 只支持 AI 生成代码模式
 */

import React, { useState, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { Play, RotateCcw, FlaskConical } from 'lucide-react';
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
    if (config.variables) {
      config.variables.forEach((v: any) => {
        initial[v.name || v.id] = v.default ?? 0;
      });
    }
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
    if (config.variables) {
      config.variables.forEach((v: any) => {
        initial[v.name || v.id] = v.default ?? 0;
      });
    }
    setVariables(initial);
  }, [config.variables]);

  const handleVariableChange = useCallback((name: string, value: number) => {
    setVariables(prev => ({ ...prev, [name]: value }));
  }, []);

  // 检查是否有有效的自定义代码
  const hasValidCode = config.mode === 'custom' && config.custom_code;

  // 如果没有有效代码，显示提示
  if (!hasValidCode) {
    return (
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <div className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-purple-500/20 rounded-xl flex items-center justify-center">
              <FlaskConical className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">{config.name || '模拟器'}</h3>
              <p className="text-slate-400 text-sm">{config.description || '模拟器配置中...'}</p>
            </div>
          </div>
          <div className="flex items-center justify-center h-48 bg-slate-800/50 rounded-xl">
            <div className="text-center">
              <FlaskConical className="w-12 h-12 text-amber-400 mx-auto mb-3" />
              <p className="text-amber-400 font-medium">模拟器代码未配置</p>
              <p className="text-slate-500 text-sm mt-1">请重新生成课程以获取模拟器代码</p>
            </div>
          </div>
        </div>
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
          style={{ height: compact ? 300 : 500, backgroundColor: '#1e293b' }}
        >
          <div className="text-center">
            <p className="text-slate-400 text-lg mb-2">点击左上角"开始"按钮</p>
            <p className="text-slate-500 text-sm">启动模拟器</p>
          </div>
        </div>
      )}

      {/* 模拟器内容 */}
      {isStarted && (
        <div>
          <CustomRenderer
            key={key}
            code={config.custom_code || ''}
            variables={variables}
            onVariableChange={handleVariableChange}
          />

          {/* 变量控制面板 */}
          {config.variables && config.variables.length > 0 && (
            <div className="p-4 bg-slate-800/50">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {config.variables.map((variable: any) => (
                  <div key={variable.name || variable.id}>
                    <div className="flex justify-between mb-1 text-sm">
                      <span className="text-slate-400">{variable.label || variable.name}</span>
                      <span className="text-slate-300">
                        {variables[variable.name || variable.id]?.toFixed(1)}
                        {variable.unit && ` ${variable.unit}`}
                      </span>
                    </div>
                    <input
                      type="range"
                      min={variable.min ?? 0}
                      max={variable.max ?? 100}
                      step={variable.step ?? 0.1}
                      value={variables[variable.name || variable.id] ?? variable.default ?? 0}
                      onChange={(e) => handleVariableChange(variable.name || variable.id, parseFloat(e.target.value))}
                      className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default SimulatorRenderer;
