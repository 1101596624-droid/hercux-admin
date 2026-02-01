/**
 * SceneRenderer - 统一的场景渲染入口
 * 根据配置自动选择合适的渲染器
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { useSceneStore } from '@/stores/useSceneStore';
import { validateScene, isValidScene } from './utils/SDLValidator';
import type { SceneDefinition, SceneState, EvaluationConfig } from '@/types/simulator-engine';
import { cn } from '@/lib/cn';

// 动态导入渲染器 (避免 SSR 问题)
const PixiRenderer = dynamic(() => import('./renderers/PixiRenderer'), {
  ssr: false,
  loading: () => <RendererLoading />,
});

// ==================== Props ====================

interface SceneRendererProps {
  /** 场景定义 */
  scene: SceneDefinition;
  /** 准备就绪回调 */
  onReady?: () => void;
  /** 错误回调 */
  onError?: (error: Error) => void;
  /** 完成回调 (评估通过) */
  onComplete?: (result: SceneState['evaluation']) => void;
  /** 状态变化回调 */
  onStateChange?: (state: SceneState) => void;
  /** 自定义类名 */
  className?: string;
  /** 是否显示控制栏 */
  showControls?: boolean;
  /** 是否只读模式 */
  readOnly?: boolean;
  /** 是否显示标题 */
  showTitle?: boolean;
  /** 是否自动启动 */
  autoStart?: boolean;
}

// ==================== 组件 ====================

export function SceneRenderer({
  scene,
  onReady,
  onError,
  onComplete,
  onStateChange,
  className,
  showControls = true,
  readOnly = false,
  showTitle = true,
  autoStart = false,
}: SceneRendererProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const {
    loaded,
    running,
    paused,
    start,
    pause,
    resume,
    stop,
    resetScene,
    checkEvaluation,
    submitResult,
    getSceneState,
    on,
    off,
  } = useSceneStore();

  // 验证场景
  useEffect(() => {
    if (!scene) {
      setError('场景定义为空');
      return;
    }

    const validation = validateScene(scene);
    if (!validation.valid) {
      const errorMsg = validation.errors.map(e => `${e.path}: ${e.message}`).join('\n');
      setError(`场景验证失败:\n${errorMsg}`);
      onError?.(new Error(errorMsg));
    } else {
      setError(null);
    }
  }, [scene, onError]);

  // 监听场景事件
  useEffect(() => {
    const handleComplete = () => {
      const state = getSceneState();
      if (state?.evaluation) {
        onComplete?.(state.evaluation);
      }
    };

    const handleStateChange = () => {
      const state = getSceneState();
      if (state) {
        onStateChange?.(state);
      }
    };

    on('complete', handleComplete);
    on('variableChange', handleStateChange);
    on('evaluationUpdate', handleStateChange);

    return () => {
      off('complete', handleComplete);
      off('variableChange', handleStateChange);
      off('evaluationUpdate', handleStateChange);
    };
  }, [on, off, getSceneState, onComplete, onStateChange]);

  // 渲染器就绪回调
  const handleReady = useCallback(() => {
    setIsLoading(false);
    // 自动启动
    if (autoStart && !running) {
      start();
    }
    onReady?.();
  }, [onReady, autoStart, running, start]);

  // 渲染器错误回调
  const handleError = useCallback((err: Error) => {
    setError(err.message);
    setIsLoading(false);
    onError?.(err);
  }, [onError]);

  // 控制按钮处理
  const handleStart = useCallback(() => {
    if (!running) {
      start();
    } else if (paused) {
      resume();
    }
  }, [running, paused, start, resume]);

  const handlePause = useCallback(() => {
    if (running && !paused) {
      pause();
    }
  }, [running, paused, pause]);

  const handleStop = useCallback(() => {
    stop();
  }, [stop]);

  const handleReset = useCallback(() => {
    resetScene();
  }, [resetScene]);

  const handleSubmit = useCallback(() => {
    checkEvaluation();
    const result = submitResult();
    if (result) {
      onComplete?.(result);
    }
  }, [checkEvaluation, submitResult, onComplete]);

  // 错误状态
  if (error) {
    return (
      <div className={cn('flex flex-col items-center justify-center p-8 bg-red-50 rounded-xl border border-red-200', className)}>
        <div className="text-red-500 text-4xl mb-4">⚠️</div>
        <h3 className="text-lg font-semibold text-red-800 mb-2">场景加载失败</h3>
        <pre className="text-sm text-red-600 whitespace-pre-wrap max-w-md">{error}</pre>
      </div>
    );
  }

  // 选择渲染器
  const renderScene = () => {
    switch (scene.canvas.renderer) {
      case 'pixi':
        return (
          <PixiRenderer
            scene={scene}
            onReady={handleReady}
            onError={handleError}
            className="rounded-lg"
          />
        );
      case 'svg':
        // TODO: 实现 SVG 渲染器
        return <div className="p-4 text-center text-slate-500">SVG 渲染器开发中...</div>;
      case 'three':
        // TODO: 实现 Three.js 渲染器
        return <div className="p-4 text-center text-slate-500">3D 渲染器开发中...</div>;
      default:
        return <div className="p-4 text-center text-red-500">未知的渲染器类型: {scene.canvas.renderer}</div>;
    }
  };

  return (
    <div className={cn('flex flex-col', className)}>
      {/* 场景标题 */}
      {showTitle && (
        <div className="mb-4">
          <h2 className="text-xl font-bold text-slate-900">{scene.name}</h2>
          {scene.description && (
            <p className="text-sm text-slate-600 mt-1">{scene.description}</p>
          )}
        </div>
      )}

      {/* 渲染区域 */}
      <div className="relative bg-slate-100 rounded-xl shadow-inner" style={{ minHeight: scene.canvas.height }}>
        {isLoading && <RendererLoading />}
        {renderScene()}
      </div>

      {/* 控制栏 */}
      {showControls && !readOnly && (
        <div className="mt-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            {/* 播放/暂停 */}
            {!running || paused ? (
              <button
                onClick={handleStart}
                disabled={!loaded}
                className="flex items-center gap-1.5 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <PlayIcon />
                {running && paused ? '继续' : '开始'}
              </button>
            ) : (
              <button
                onClick={handlePause}
                className="flex items-center gap-1.5 px-4 py-2 bg-amber-600 text-white text-sm font-medium rounded-lg hover:bg-amber-700 transition-colors"
              >
                <PauseIcon />
                暂停
              </button>
            )}

            {/* 停止 */}
            <button
              onClick={handleStop}
              disabled={!running}
              className="flex items-center gap-1.5 px-4 py-2 bg-slate-600 text-white text-sm font-medium rounded-lg hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <StopIcon />
              停止
            </button>

            {/* 重置 */}
            <button
              onClick={handleReset}
              className="flex items-center gap-1.5 px-4 py-2 bg-slate-200 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-300 transition-colors"
            >
              <ResetIcon />
              重置
            </button>
          </div>

          {/* 提交按钮 (如果有评估) */}
          {scene.evaluation && (
            <button
              onClick={handleSubmit}
              disabled={!running}
              className="flex items-center gap-1.5 px-6 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <CheckIcon />
              提交结果
            </button>
          )}
        </div>
      )}

      {/* 状态指示器 */}
      {showControls && (
        <div className="mt-2 flex items-center gap-4 text-xs text-slate-500">
          <span className="flex items-center gap-1">
            <span className={cn(
              'w-2 h-2 rounded-full',
              loaded ? 'bg-green-500' : 'bg-slate-300'
            )} />
            {loaded ? '已加载' : '未加载'}
          </span>
          <span className="flex items-center gap-1">
            <span className={cn(
              'w-2 h-2 rounded-full',
              running ? (paused ? 'bg-amber-500' : 'bg-green-500 animate-pulse') : 'bg-slate-300'
            )} />
            {running ? (paused ? '已暂停' : '运行中') : '已停止'}
          </span>
        </div>
      )}
    </div>
  );
}

// ==================== 子组件 ====================

function RendererLoading() {
  return (
    <div className="absolute inset-0 flex items-center justify-center bg-slate-100/80 backdrop-blur-sm z-10">
      <div className="flex flex-col items-center">
        <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        <p className="mt-2 text-sm text-slate-600">加载渲染器...</p>
      </div>
    </div>
  );
}

// ==================== 图标 ====================

function PlayIcon() {
  return (
    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
    </svg>
  );
}

function PauseIcon() {
  return (
    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
    </svg>
  );
}

function StopIcon() {
  return (
    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
    </svg>
  );
}

function ResetIcon() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
  );
}

export default SceneRenderer;
