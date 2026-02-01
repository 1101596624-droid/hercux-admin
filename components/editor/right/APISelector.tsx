'use client';

/**
 * APISelector - AI API 切换选择器
 * 支持切换不同的 AI 提供商
 */

import React from 'react';
import { useEditorStore } from '@/stores/editor/useEditorStore';
import type { AIProvider } from '@/types/editor';
import { AI_PROVIDER_LABELS } from '@/types/editor';

const providerConfig: Record<AIProvider, { description: string; color: string }> = {
  claude: {
    description: 'Anthropic Claude - 强大的推理能力',
    color: 'bg-orange-100 text-orange-700',
  },
  gpt: {
    description: 'OpenAI GPT - 广泛的知识库',
    color: 'bg-green-100 text-green-700',
  },
  deepseek: {
    description: 'DeepSeek - 高性价比选择',
    color: 'bg-blue-100 text-blue-700',
  },
  qwen: {
    description: '通义千问 - 中文优化',
    color: 'bg-purple-100 text-purple-700',
  },
};

export function APISelector() {
  const { aiGuidance, setAIProvider, updateAIGuidance } = useEditorStore();

  const handleProviderChange = (provider: AIProvider) => {
    setAIProvider(provider);
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-dark-700 mb-2">
          AI 提供商
        </label>
        <select
          value={aiGuidance.provider}
          onChange={(e) => handleProviderChange(e.target.value as AIProvider)}
          className="w-full rounded-lg border border-dark-200 px-3 py-2 text-dark-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          {(Object.keys(AI_PROVIDER_LABELS) as AIProvider[]).map((provider) => (
            <option key={provider} value={provider}>
              {AI_PROVIDER_LABELS[provider]}
            </option>
          ))}
        </select>
        <p className="mt-1.5 text-xs text-dark-500">
          {providerConfig[aiGuidance.provider].description}
        </p>
      </div>

      <div className="p-3 rounded-lg bg-dark-50 space-y-3">
        <div className="flex items-center gap-2">
          <span className={`px-2 py-0.5 rounded text-xs font-medium ${providerConfig[aiGuidance.provider].color}`}>
            {AI_PROVIDER_LABELS[aiGuidance.provider]}
          </span>
          <span className="text-xs text-dark-500">当前选择</span>
        </div>

        <div>
          <label className="block text-xs font-medium text-dark-600 mb-1">
            API Key（可选）
          </label>
          <input
            type="password"
            placeholder="使用默认配置或输入自定义 Key"
            value={aiGuidance.apiKey || ''}
            onChange={(e) => updateAIGuidance({ apiKey: e.target.value || undefined })}
            className="w-full rounded border border-dark-200 px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-dark-600 mb-1">
            最大对话轮数
          </label>
          <input
            type="number"
            min={1}
            max={50}
            value={aiGuidance.maxTurns}
            onChange={(e) => updateAIGuidance({ maxTurns: parseInt(e.target.value) || 10 })}
            className="w-full rounded border border-dark-200 px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-dark-600 mb-1">
            温度 (0-1)
          </label>
          <input
            type="number"
            min={0}
            max={1}
            step={0.1}
            value={aiGuidance.temperature}
            onChange={(e) => updateAIGuidance({ temperature: parseFloat(e.target.value) || 0.7 })}
            className="w-full rounded border border-dark-200 px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
        </div>
      </div>
    </div>
  );
}
