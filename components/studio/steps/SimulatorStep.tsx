'use client';

/**
 * SimulatorStep - 模拟器步骤组件
 * 用于 Studio 课程编辑器中渲染 SDL 模拟器
 * 支持 SDL 模式和自定义代码模式
 */

import React, { useMemo, useCallback, useState } from 'react';
import dynamic from 'next/dynamic';
import { Play, RotateCcw } from 'lucide-react';
import type { SimulatorSpec } from '@/types/coursePackage';

// 动态导入 PixiRenderer 避免 SSR 问题
const PixiRenderer = dynamic(
  () => import('@/components/simulator-engine/renderers/PixiRenderer').then(mod => mod.PixiRenderer),
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-64 bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl">
        <div className="flex flex-col items-center">
          <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <p className="mt-2 text-sm text-slate-400">加载模拟器...</p>
        </div>
      </div>
    ),
  }
);

// 动态导入 CustomRenderer 避免 SSR 问题
const CustomRenderer = dynamic(
  () => import('@/components/simulator-engine/CustomRenderer').then(mod => mod.CustomRenderer),
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-64 bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl">
        <div className="flex flex-col items-center">
          <div className="w-8 h-8 border-4 border-purple-500 border-t-transparent rounded-full animate-spin" />
          <p className="mt-2 text-sm text-slate-400">加载高级模拟器...</p>
        </div>
      </div>
    ),
  }
);

interface SimulatorStepProps {
  simulator_spec: SimulatorSpec;
}

export function SimulatorStep({ simulator_spec }: SimulatorStepProps) {
  // 检查是否使用自定义代码模式
  const spec = simulator_spec as any;
  const isCustomMode = spec?.mode === 'custom' && spec?.custom_code;

  if (isCustomMode) {
    return <CustomCodeSimulator spec={spec} />;
  }

  return <SDLSimulator simulator_spec={simulator_spec} />;
}

/** 自定义代码模拟器 */
function CustomCodeSimulator({ spec }: { spec: any }) {
  const [isStarted, setIsStarted] = useState(false);
  const [key, setKey] = useState(0);
  const [variables, setVariables] = useState<Record<string, number>>(() => {
    const initial: Record<string, number> = {};
    if (spec.variables) {
      spec.variables.forEach((v: any) => {
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
    const initial: Record<string, number> = {};
    if (spec.variables) {
      spec.variables.forEach((v: any) => {
        initial[v.name || v.id] = v.default ?? 0;
      });
    }
    setVariables(initial);
  }, [spec.variables]);

  const handleVariableChange = useCallback((name: string, value: number) => {
    setVariables(prev => ({ ...prev, [name]: value }));
  }, []);

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
            高级模式
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
            <p className="text-slate-500 text-sm">启动高级模拟器</p>
          </div>
        </div>
      )}

      {/* 模拟器内容 */}
      {isStarted && (
        <div>
          <CustomRenderer
            key={key}
            code={spec.custom_code}
            variables={variables}
            onVariableChange={handleVariableChange}
          />

          {/* 变量控制面板 */}
          {spec.variables && spec.variables.length > 0 && (
            <div className="p-4 bg-slate-800/50">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {spec.variables.map((variable: any) => (
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

/** SDL 模拟器 - 使用 PixiRenderer */
function SDLSimulator({ simulator_spec }: { simulator_spec: SimulatorSpec }) {
  const [isStarted, setIsStarted] = useState(false);
  const [key, setKey] = useState(0);

  // 解析 SDL 数据
  const sdlScene = useMemo(() => {
    let spec = simulator_spec as any;
    if (typeof spec === 'string') {
      try {
        spec = JSON.parse(spec.replace(/'/g, '"'));
      } catch {
        return null;
      }
    }
    const data = spec?.sdl || spec?.sdl_scene || spec?.scene || spec;
    if (data?.canvas && data?.elements) {
      return data;
    }
    return null;
  }, [simulator_spec]);

  const handleStart = useCallback(() => {
    setIsStarted(true);
  }, []);

  const handleReset = useCallback(() => {
    setIsStarted(false);
    setKey(k => k + 1);
  }, []);

  if (!sdlScene) {
    return (
      <div className="flex items-center justify-center h-64 bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl">
        <p className="text-slate-400">{(simulator_spec as any)?.description || '模拟器配置中...'}</p>
      </div>
    );
  }

  return (
    <div className="relative">
      {/* 控制按钮 */}
      <div className="absolute top-2 left-2 z-10 flex items-center gap-2">
        {!isStarted ? (
          <button
            onClick={handleStart}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors shadow-lg"
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
          <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-lg">
            运行中
          </span>
        )}
      </div>

      {/* 模拟器容器 */}
      <div
        className="rounded-2xl overflow-hidden"
        style={{
          width: '100%',
          maxWidth: sdlScene.canvas?.width || 800,
          margin: '0 auto',
        }}
      >
        {/* 未开始时显示提示 */}
        {!isStarted && (
          <div
            className="flex items-center justify-center"
            style={{
              height: sdlScene.canvas?.height || 500,
              backgroundColor: sdlScene.canvas?.backgroundColor || '#1e293b'
            }}
          >
            <div className="text-center">
              <p className="text-slate-400 text-lg mb-2">点击左上角"开始"按钮</p>
              <p className="text-slate-500 text-sm">启动模拟器后可以进行交互</p>
            </div>
          </div>
        )}

        {/* 使用 PixiRenderer 渲染 */}
        {isStarted && (
          <PixiRenderer
            key={key}
            scene={sdlScene}
            onReady={() => console.log('SimulatorStep: PixiRenderer ready')}
            onError={(err) => console.error('SimulatorStep: PixiRenderer error', err)}
          />
        )}
      </div>
    </div>
  );
}

export default SimulatorStep;
