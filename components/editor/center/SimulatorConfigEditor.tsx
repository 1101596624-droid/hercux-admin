'use client';

/**
 * SimulatorConfigEditor - 模拟器配置编辑器
 * 新版本：只支持 custom（AI生成）和 iframe（外部嵌入）两种类型
 */

import React, { useState } from 'react';
import { Input } from '@/components/ui/Input';
import { Plus, Trash2 } from 'lucide-react';
import { SimulatorAIGenerator } from './SimulatorAIGenerator';
import type {
  SimulatorConfig,
  SimulatorInputConfig,
  SimulatorOutputConfig,
} from '@/types/editor';

interface SimulatorConfigEditorProps {
  config?: SimulatorConfig;
  onChange: (config: SimulatorConfig) => void;
}

const DEFAULT_CONFIG: SimulatorConfig = {
  type: 'custom',
  mode: 'custom',
  name: '',
  description: '',
  inputs: [],
  outputs: [],
  instructions: [],
};

// 模拟器类型选项（只保留新版本支持的类型）
const SIMULATOR_TYPES = [
  { value: 'custom', label: '自定义模拟器', description: '使用 AI 生成 PixiJS 代码', category: '推荐' },
  { value: 'iframe', label: '外部嵌入', description: '嵌入外部网页或H5', category: '通用' },
] as const;

export function SimulatorConfigEditor({ config, onChange }: SimulatorConfigEditorProps) {
  const currentConfig: SimulatorConfig = config || DEFAULT_CONFIG;

  const updateConfig = (updates: Partial<SimulatorConfig>) => {
    onChange({ ...currentConfig, ...updates });
  };

  // 根据类型渲染不同的配置界面
  const renderTypeConfig = () => {
    switch (currentConfig.type) {
      case 'custom':
        return (
          <CustomSimulatorEditor config={currentConfig} onChange={updateConfig} />
        );

      case 'iframe':
        return (
          <div className="space-y-4">
            <Input
              label="嵌入 URL"
              placeholder="https://example.com/simulator"
              value={currentConfig.iframeUrl || ''}
              onChange={(e) => updateConfig({ iframeUrl: e.target.value })}
            />
            <Input
              label="标题"
              value={currentConfig.name}
              onChange={(e) => updateConfig({ name: e.target.value })}
            />
            <div>
              <label className="block text-sm font-medium text-dark-700 mb-1.5">描述</label>
              <textarea
                value={currentConfig.description}
                onChange={(e) => updateConfig({ description: e.target.value })}
                rows={3}
                className="w-full rounded-lg border border-dark-200 px-3 py-2 text-sm"
              />
            </div>
          </div>
        );

      default:
        return (
          <div className="text-center py-8 text-dark-400 text-sm">
            请选择模拟器类型
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* 模拟器类型选择 */}
      <div>
        <label className="block text-sm font-medium text-dark-700 mb-2">
          模拟器类型
        </label>
        <div className="grid grid-cols-1 gap-3">
          {SIMULATOR_TYPES.map((type) => (
            <button
              key={type.value}
              onClick={() => updateConfig({
                type: type.value as SimulatorConfig['type'],
                mode: type.value === 'custom' ? 'custom' : undefined,
              })}
              className={`p-4 rounded-lg border-2 text-left transition-all ${
                currentConfig.type === type.value
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-dark-200 hover:border-dark-300'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="font-medium text-dark-800 text-sm mb-1">{type.label}</div>
                  <div className="text-xs text-dark-500">{type.description}</div>
                </div>
                <div className="text-xs font-medium text-primary-600 bg-primary-100 px-2 py-1 rounded">
                  {type.category}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 类型特定配置 */}
      {renderTypeConfig()}
    </div>
  );
}

/** 自定义模拟器编辑器 */
function CustomSimulatorEditor({
  config,
  onChange,
}: {
  config: SimulatorConfig;
  onChange: (updates: Partial<SimulatorConfig>) => void;
}) {
  const [activeTab, setActiveTab] = useState<'ai' | 'basic' | 'variables'>('ai');

  return (
    <div className="space-y-4">
      <div className="flex border-b border-dark-200">
        {(['ai', 'basic', 'variables'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-dark-500 hover:text-dark-700'
            }`}
          >
            {tab === 'ai' && 'AI 生成'}
            {tab === 'basic' && '基本信息'}
            {tab === 'variables' && '变量配置'}
          </button>
        ))}
      </div>

      {activeTab === 'ai' && (
        <SimulatorAIGenerator
          onApply={onChange}
          hasExistingSimulator={!!(config.custom_code || config.mode === 'custom')}
        />
      )}

      {activeTab === 'basic' && (
        <div className="space-y-4">
          <Input
            label="名称"
            value={config.name}
            onChange={(e) => onChange({ name: e.target.value })}
            placeholder="例如：弹簧振子模拟器"
          />
          <div>
            <label className="block text-sm font-medium text-dark-700 mb-1.5">描述</label>
            <textarea
              value={config.description}
              onChange={(e) => onChange({ description: e.target.value })}
              rows={3}
              className="w-full rounded-lg border border-dark-200 px-3 py-2 text-sm"
              placeholder="简要描述模拟器的功能和用途..."
            />
          </div>
          {config.custom_code && (
            <div>
              <label className="block text-sm font-medium text-dark-700 mb-1.5">
                自定义代码
                <span className="ml-2 text-xs text-dark-400">
                  ({config.custom_code.split('\n').length} 行)
                </span>
              </label>
              <textarea
                value={config.custom_code}
                onChange={(e) => onChange({ custom_code: e.target.value })}
                rows={12}
                className="w-full rounded-lg border border-dark-200 px-3 py-2 text-sm font-mono"
                placeholder="// PixiJS 代码"
              />
            </div>
          )}
        </div>
      )}

      {activeTab === 'variables' && (
        <VariablesEditor
          variables={config.variables || []}
          onChange={(variables) => onChange({ variables })}
        />
      )}
    </div>
  );
}

/** 变量配置编辑器 */
function VariablesEditor({
  variables,
  onChange,
}: {
  variables: NonNullable<SimulatorConfig['variables']>;
  onChange: (variables: NonNullable<SimulatorConfig['variables']>) => void;
}) {
  const addVariable = () => {
    onChange([
      ...variables,
      {
        name: `var${variables.length + 1}`,
        label: `变量 ${variables.length + 1}`,
        min: 0,
        max: 100,
        default: 50,
        step: 1,
      },
    ]);
  };

  const updateVariable = (index: number, updates: Partial<NonNullable<SimulatorConfig['variables']>[0]>) => {
    const newVariables = [...variables];
    newVariables[index] = { ...newVariables[index], ...updates };
    onChange(newVariables);
  };

  const removeVariable = (index: number) => {
    onChange(variables.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-dark-700">
          变量列表 ({variables.length})
        </span>
        <button
          onClick={addVariable}
          className="flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700"
        >
          <Plus size={16} />
          添加变量
        </button>
      </div>

      {variables.map((variable, index) => (
        <div key={index} className="p-4 border border-dark-200 rounded-lg space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-dark-600">变量 {index + 1}</span>
            <button
              onClick={() => removeVariable(index)}
              className="text-red-500 hover:text-red-600"
            >
              <Trash2 size={16} />
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="变量名"
              value={variable.name}
              onChange={(e) => updateVariable(index, { name: e.target.value })}
              placeholder="varName"
            />
            <Input
              label="显示标签"
              value={variable.label || ''}
              onChange={(e) => updateVariable(index, { label: e.target.value })}
              placeholder="变量名称"
            />
          </div>

          <div className="grid grid-cols-4 gap-3">
            <Input
              label="最小值"
              type="number"
              value={variable.min ?? 0}
              onChange={(e) => updateVariable(index, { min: Number(e.target.value) })}
            />
            <Input
              label="最大值"
              type="number"
              value={variable.max ?? 100}
              onChange={(e) => updateVariable(index, { max: Number(e.target.value) })}
            />
            <Input
              label="默认值"
              type="number"
              value={variable.default ?? 50}
              onChange={(e) => updateVariable(index, { default: Number(e.target.value) })}
            />
            <Input
              label="步长"
              type="number"
              value={variable.step ?? 1}
              onChange={(e) => updateVariable(index, { step: Number(e.target.value) })}
            />
          </div>

          <Input
            label="单位"
            value={variable.unit || ''}
            onChange={(e) => updateVariable(index, { unit: e.target.value })}
            placeholder="例如：m, kg, s"
          />
        </div>
      ))}

      {variables.length === 0 && (
        <div className="text-center py-8 text-dark-400 text-sm">
          暂无变量，AI 生成代码时会自动创建变量
        </div>
      )}
    </div>
  );
}

export default SimulatorConfigEditor;
