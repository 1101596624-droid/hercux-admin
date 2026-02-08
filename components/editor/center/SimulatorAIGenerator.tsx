'use client';

/**
 * SimulatorAIGenerator - AI 模拟器代码生成组件
 * 对话式UI，用户输入描述后AI生成模拟器代码
 */

import React, { useState } from 'react';
import { simulatorAPI } from '@/lib/api/admin/simulator';
import type { SimulatorConfig } from '@/types/editor';

interface SimulatorAIGeneratorProps {
  onGenerated: (updates: Partial<SimulatorConfig>) => void;
}

export function SimulatorAIGenerator({ onGenerated }: SimulatorAIGeneratorProps) {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generated, setGenerated] = useState(false);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setError(null);
    setGenerated(false);
    try {
      const result = await simulatorAPI.generateCode(prompt.trim());
      onGenerated({
        type: 'custom',
        mode: 'custom',
        custom_code: result.custom_code,
        variables: result.variables.map((v) => ({
          name: v.name,
          label: v.label || v.name,
          min: v.min ?? 0,
          max: v.max ?? 100,
          default: v.default ?? 50,
          step: v.step ?? 1,
        })),
        name: result.name,
        description: result.description,
      });
      setGenerated(true);
    } catch (e: any) {
      setError(e.message || 'AI 生成失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4 p-4 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-lg border border-indigo-200">
      <div className="flex items-center gap-2">
        <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        <h4 className="text-sm font-medium text-indigo-800">AI 代码生成</h4>
      </div>

      <div>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="描述你想要的模拟器效果，例如：&#10;- 一个弹簧振动模拟器，可以调节弹簧系数和质量&#10;- 一个行星轨道模拟，展示开普勒定律&#10;- 一个波的干涉模拟器"
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
          ) : generated ? (
            '重新生成'
          ) : (
            '生成代码'
          )}
        </button>

        {generated && (
          <span className="text-sm text-green-600 flex items-center gap-1">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            代码已生成并填入
          </span>
        )}
      </div>

      {error && (
        <p className="text-sm text-red-500">{error}</p>
      )}
    </div>
  );
}

export default SimulatorAIGenerator;
