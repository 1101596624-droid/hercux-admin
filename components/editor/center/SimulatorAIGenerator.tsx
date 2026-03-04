'use client';

/**
 * SimulatorAIGenerator - AI 模拟器代码生成组件
 * 对话式UI，用户输入描述后AI生成HTML格式模拟器
 *
 * V3 功能（2026-02-10 更新）：
 * - 生成完整HTML模拟器（替代ctx API）
 * - 预览HTML模拟器效果
 * - 管理员可选择：覆盖当前 / 重新生成
 */

import React, { useState, useCallback, useRef } from 'react';
import dynamic from 'next/dynamic';
import { simulatorAPI } from '@/lib/api/admin/simulator';
import type { SimulatorConfig } from '@/types/editor';

// 动态导入 HTMLSimulatorRenderer 避免 SSR 问题
const HTMLSimulatorRenderer = dynamic(
  () => import('@/components/simulator-engine/HTMLSimulatorRenderer').then(mod => mod.default),
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-64 bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg">
        <div className="flex flex-col items-center">
          <div className="w-8 h-8 border-4 border-purple-500 border-t-transparent rounded-full animate-spin" />
          <p className="mt-2 text-sm text-slate-400">加载预览...</p>
        </div>
      </div>
    ),
  }
);

interface GeneratedSimulator {
  custom_code: string; // HTML content
  html_content?: string; // Alternative field name
  variables: Array<{
    name: string;
    label?: string;
    min?: number;
    max?: number;
    default?: number;
    step?: number;
  }>;
  name: string;
  description: string;
}

interface SimulatorAIGeneratorProps {
  onApply: (updates: Partial<SimulatorConfig>) => void;
  hasExistingSimulator?: boolean; // 当前步骤是否已有模拟器
}

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export function SimulatorAIGenerator({
  onApply,
  hasExistingSimulator = false,
}: SimulatorAIGeneratorProps) {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generationStatus, setGenerationStatus] = useState<string | null>(null);
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [generatedSimulator, setGeneratedSimulator] = useState<GeneratedSimulator | null>(null);
  const stopPollingRef = useRef(false);

  const pollTask = useCallback(async (taskId: string, waitMs: number) => {
    const start = Date.now();
    const pollIntervalMs = 2000;

    while (Date.now() - start < waitMs) {
      if (stopPollingRef.current) {
        setGenerationStatus(`已停止前台轮询（task_id: ${taskId}），任务可能仍在后台执行`);
        return false;
      }
      const taskStatus = await simulatorAPI.getGenerateTaskStatus(taskId);
      const elapsedSec = Math.floor((Date.now() - start) / 1000);
      const stageText = taskStatus.stage_message || taskStatus.current_stage || '处理中';
      const runningSec = typeof taskStatus.running_seconds === 'number'
        ? Math.floor(taskStatus.running_seconds)
        : elapsedSec;

      if (taskStatus.status === 'queued') {
        setGenerationStatus(`任务排队中 (${taskId.slice(0, 8)})：${stageText}，已等待 ${elapsedSec}s`);
        await sleep(pollIntervalMs);
        continue;
      }

      if (taskStatus.status === 'running') {
        setGenerationStatus(`Agent 处理中 (${taskId.slice(0, 8)})：${stageText}，已运行 ${runningSec}s`);
        await sleep(pollIntervalMs);
        continue;
      }

      if (taskStatus.status === 'succeeded') {
        if (!taskStatus.result) {
          throw new Error('任务已完成但未返回代码');
        }
        setGeneratedSimulator(taskStatus.result);
        setGenerationStatus(null);
        setActiveTaskId(null);
        return true;
      }

      if (taskStatus.status === 'canceled') {
        setGenerationStatus(`任务已取消 (${taskId.slice(0, 8)})`);
        setActiveTaskId(null);
        return false;
      }

      const errMessage = taskStatus.error_message || `任务执行失败 (${taskStatus.status})`;
      throw new Error(errMessage);
    }

    setGenerationStatus(`任务仍在后台执行（task_id: ${taskId}），可稍后点击“继续查询任务”`);
    return false;
  }, []);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    stopPollingRef.current = false;
    setLoading(true);
    setError(null);
    setGenerationStatus('正在提交生成任务...');
    setGeneratedSimulator(null);
    try {
      const task = await simulatorAPI.createGenerateTask(prompt.trim());
      setActiveTaskId(task.task_id);
      setGenerationStatus(`任务已提交 (${task.task_id.slice(0, 8)})，正在排队...`);
      await pollTask(task.task_id, 20 * 60 * 1000);
    } catch (e: any) {
      setError(e.message || 'AI 生成失败，请重试');
      setGenerationStatus(null);
    } finally {
      setLoading(false);
    }
  };

  const handleContinuePolling = useCallback(async () => {
    if (!activeTaskId) return;
    stopPollingRef.current = false;
    setLoading(true);
    setError(null);
    try {
      await pollTask(activeTaskId, 10 * 60 * 1000);
    } catch (e: any) {
      setError(e.message || '任务查询失败，请重试');
    } finally {
      setLoading(false);
    }
  }, [activeTaskId, pollTask]);

  const handleCancelTask = useCallback(async () => {
    if (!activeTaskId) return;
    stopPollingRef.current = true;
    setLoading(true);
    setError(null);
    try {
      const canceled = await simulatorAPI.cancelGenerateTask(activeTaskId);
      const stageText = canceled.stage_message || canceled.current_stage || '已发送取消请求';
      setGenerationStatus(`任务 ${activeTaskId.slice(0, 8)}：${stageText}`);
      if (canceled.status === 'canceled') {
        setActiveTaskId(null);
      }
    } catch (e: any) {
      setError(e.message || '任务取消失败，请重试');
    } finally {
      setLoading(false);
    }
  }, [activeTaskId]);

  const handleRetryTask = useCallback(async () => {
    if (!activeTaskId) return;
    stopPollingRef.current = false;
    setLoading(true);
    setError(null);
    try {
      setGenerationStatus(`正在重试任务（${activeTaskId.slice(0, 8)}）...`);
      const retryTask = await simulatorAPI.retryGenerateTask(activeTaskId);
      setActiveTaskId(retryTask.task_id);
      setGenerationStatus(`重试任务已提交 (${retryTask.task_id.slice(0, 8)})，正在排队...`);
      await pollTask(retryTask.task_id, 20 * 60 * 1000);
    } catch (e: any) {
      setError(e.message || '任务重试失败，请重试');
    } finally {
      setLoading(false);
    }
  }, [activeTaskId, pollTask]);

  const handleRegenerate = useCallback(() => {
    stopPollingRef.current = true;
    setGeneratedSimulator(null);
    setError(null);
    setGenerationStatus(null);
    setActiveTaskId(null);
  }, []);

  const handleApply = useCallback(() => {
    if (!generatedSimulator) return;

    const htmlContent = generatedSimulator.html_content || generatedSimulator.custom_code;

    onApply({
      type: 'custom',
      mode: 'custom',
      html_content: htmlContent,
      custom_code: htmlContent, // Backward compatibility
      variables: [], // HTML模拟器自带交互，不需要外部变量
      name: generatedSimulator.name,
      description: generatedSimulator.description,
    });

    // 显示成功提示后清空
    const actionText = hasExistingSimulator ? '已覆盖当前模拟器！' : '已插入模拟器！';
    alert(actionText);
    setGeneratedSimulator(null);
    setPrompt('');
    setGenerationStatus(null);
    setActiveTaskId(null);
  }, [generatedSimulator, onApply, hasExistingSimulator]);

  return (
    <div className="space-y-4 p-4 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-lg border border-indigo-200">
      <div className="flex items-center gap-2">
        <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        <h4 className="text-sm font-medium text-indigo-800">AI HTML 模拟器生成</h4>
      </div>

      {/* 输入区域 */}
      {!generatedSimulator && (
        <>
          <div>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="描述你想要的模拟器效果，例如：&#10;- 一个弹簧振动模拟器，可以调节弹簧系数和质量&#10;- 一个行星轨道模拟，展示开普勒定律&#10;- 一个波的干涉模拟器，带控制面板"
              rows={4}
              disabled={loading}
              className="w-full rounded-lg border border-indigo-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 disabled:opacity-50"
            />
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleGenerate}
              disabled={loading || !prompt.trim()}
              className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading ? (
                <>
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  生成中...
                </>
              ) : (
                '生成代码'
              )}
            </button>
          </div>

          {error && (
            <p className="text-sm text-red-500">{error}</p>
          )}

          {loading && generationStatus && (
            <p className="text-xs text-indigo-700">{generationStatus}</p>
          )}

          {activeTaskId && !generatedSimulator && (
            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={handleContinuePolling}
                disabled={loading}
                className="px-3 py-1.5 text-xs bg-slate-600 text-white rounded hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                继续查询任务（{activeTaskId.slice(0, 8)}）
              </button>
              <button
                onClick={handleCancelTask}
                className="px-3 py-1.5 text-xs bg-rose-600 text-white rounded hover:bg-rose-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                取消任务
              </button>
              <button
                onClick={handleRetryTask}
                disabled={loading}
                className="px-3 py-1.5 text-xs bg-amber-600 text-white rounded hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                重试任务
              </button>
            </div>
          )}
        </>
      )}

      {/* 预览和操作区域 */}
      {generatedSimulator && (
        <div className="space-y-4">
          {/* 生成的模拟器信息 */}
          <div className="bg-white p-3 rounded-lg border border-indigo-100">
            <h5 className="text-sm font-medium text-gray-900 mb-1">{generatedSimulator.name}</h5>
            <p className="text-xs text-gray-600">{generatedSimulator.description}</p>
          </div>

          {/* HTML模拟器预览 */}
          <div className="bg-slate-900 rounded-lg overflow-hidden border-2 border-slate-700">
            <HTMLSimulatorRenderer
              htmlContent={generatedSimulator.html_content || generatedSimulator.custom_code}
              height={504}
              showBorder={false}
            />
          </div>

          {/* 操作按钮 */}
          <div className="flex items-center gap-3">
            <button
              onClick={handleApply}
              className="flex-1 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 flex items-center justify-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              {hasExistingSimulator ? '覆盖当前模拟器' : '插入'}
            </button>

            <button
              onClick={handleRegenerate}
              className="px-4 py-2 bg-gray-500 text-white text-sm font-medium rounded-lg hover:bg-gray-600 flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              重新生成
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default SimulatorAIGenerator;
