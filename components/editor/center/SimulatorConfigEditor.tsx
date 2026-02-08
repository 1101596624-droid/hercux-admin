'use client';

/**
 * SimulatorConfigEditor - 模拟器配置编辑器
 */

import React, { useState } from 'react';
import { Input } from '@/components/ui/Input';
import { Plus, Trash2 } from 'lucide-react';
import { SimulatorAIGenerator } from './SimulatorAIGenerator';
import type {
  SimulatorConfig,
  SimulatorInputConfig,
  SimulatorOutputConfig,
  TimelineEvent,
  DecisionOption,
  ComparisonItem,
  ConceptNode,
  ConceptRelation,
} from '@/types/editor';
import { getAllPresetSimulators, getPresetSimulator } from '@/components/simulators/presets';

interface SimulatorConfigEditorProps {
  config?: SimulatorConfig;
  onChange: (config: SimulatorConfig) => void;
}

const DEFAULT_CONFIG: SimulatorConfig = {
  type: 'preset',
  name: '',
  description: '',
  inputs: [],
  outputs: [],
  instructions: [],
};

// 模拟器类型选项
const SIMULATOR_TYPES = [
  { value: 'preset', label: '预设模拟器', category: '理科' },
  { value: 'custom', label: '自定义计算', category: '理科' },
  { value: 'timeline', label: '时间线探索', category: '文科' },
  { value: 'decision', label: '决策情景', category: '文科' },
  { value: 'comparison', label: '对比分析', category: '文科' },
  { value: 'concept-map', label: '概念关系图', category: '文科' },
  { value: 'iframe', label: '外部嵌入', category: '通用' },
] as const;

export function SimulatorConfigEditor({ config, onChange }: SimulatorConfigEditorProps) {
  const currentConfig: SimulatorConfig = config || DEFAULT_CONFIG;
  const presets = getAllPresetSimulators();

  const updateConfig = (updates: Partial<SimulatorConfig>) => {
    onChange({ ...currentConfig, ...updates });
  };

  // 选择预设模拟器
  const handleSelectPreset = (presetId: string) => {
    const preset = getPresetSimulator(presetId);
    if (preset) {
      onChange({
        type: 'preset',
        presetId,
        ...preset.defaultConfig,
      });
    }
  };

  // 根据类型渲染不同的配置界面
  const renderTypeConfig = () => {
    switch (currentConfig.type) {
      case 'preset':
        return (
          <div>
            <label className="block text-sm font-medium text-dark-700 mb-2">
              选择预设模拟器
            </label>
            <div className="grid grid-cols-2 gap-3">
              {presets.map((preset) => (
                <button
                  key={preset.id}
                  onClick={() => handleSelectPreset(preset.id)}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    currentConfig.presetId === preset.id
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-dark-200 hover:border-dark-300'
                  }`}
                >
                  <div className="text-2xl mb-2">{preset.thumbnail}</div>
                  <div className="font-medium text-dark-800">{preset.name}</div>
                  <div className="text-xs text-dark-500 mt-1">{preset.description}</div>
                </button>
              ))}
            </div>
          </div>
        );

      case 'custom':
        return (
          <CustomSimulatorEditor config={currentConfig} onChange={updateConfig} />
        );

      case 'timeline':
        return (
          <TimelineEditor config={currentConfig} onChange={updateConfig} />
        );

      case 'decision':
        return (
          <DecisionEditor config={currentConfig} onChange={updateConfig} />
        );

      case 'comparison':
        return (
          <ComparisonEditor config={currentConfig} onChange={updateConfig} />
        );

      case 'concept-map':
        return (
          <ConceptMapEditor config={currentConfig} onChange={updateConfig} />
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
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* 模拟器类型选择 */}
      <div>
        <label className="block text-sm font-medium text-dark-700 mb-2">
          模拟器类型
        </label>
        <div className="grid grid-cols-2 gap-2">
          {SIMULATOR_TYPES.map((type) => (
            <button
              key={type.value}
              onClick={() => updateConfig({ type: type.value as SimulatorConfig['type'] })}
              className={`p-3 rounded-lg border-2 text-left transition-all ${
                currentConfig.type === type.value
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-dark-200 hover:border-dark-300'
              }`}
            >
              <div className="font-medium text-dark-800 text-sm">{type.label}</div>
              <div className="text-xs text-dark-400">{type.category}</div>
            </button>
          ))}
        </div>
      </div>

      {/* 类型特定配置 */}
      {renderTypeConfig()}
    </div>
  );
}

/** 自定义计算模拟器编辑器 */
function CustomSimulatorEditor({
  config,
  onChange,
}: {
  config: SimulatorConfig;
  onChange: (updates: Partial<SimulatorConfig>) => void;
}) {
  const [activeTab, setActiveTab] = useState<'ai' | 'basic' | 'inputs' | 'outputs'>('ai');

  return (
    <div className="space-y-4">
      <div className="flex border-b border-dark-200">
        {(['ai', 'basic', 'inputs', 'outputs'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-dark-500'
            }`}
          >
            {tab === 'ai' && 'AI 生成'}
            {tab === 'basic' && '基本'}
            {tab === 'inputs' && '输入'}
            {tab === 'outputs' && '输出'}
          </button>
        ))}
      </div>

      {activeTab === 'ai' && (
        <SimulatorAIGenerator onGenerated={onChange} />
      )}

      {activeTab === 'basic' && (
        <div className="space-y-4">
          <Input
            label="名称"
            value={config.name}
            onChange={(e) => onChange({ name: e.target.value })}
          />
          <div>
            <label className="block text-sm font-medium text-dark-700 mb-1.5">描述</label>
            <textarea
              value={config.description}
              onChange={(e) => onChange({ description: e.target.value })}
              rows={3}
              className="w-full rounded-lg border border-dark-200 px-3 py-2 text-sm"
            />
          </div>
        </div>
      )}

      {activeTab === 'inputs' && (
        <InputsEditor
          inputs={config.inputs}
          onChange={(inputs) => onChange({ inputs })}
        />
      )}

      {activeTab === 'outputs' && (
        <OutputsEditor
          outputs={config.outputs}
          onChange={(outputs) => onChange({ outputs })}
        />
      )}
    </div>
  );
}

/** 时间线编辑器 */
function TimelineEditor({
  config,
  onChange,
}: {
  config: SimulatorConfig;
  onChange: (updates: Partial<SimulatorConfig>) => void;
}) {
  const timeline = config.timeline || { title: '', events: [] };

  const updateTimeline = (updates: Partial<typeof timeline>) => {
    onChange({ timeline: { ...timeline, ...updates } });
  };

  const addEvent = () => {
    updateTimeline({
      events: [
        ...timeline.events,
        { id: `event-${Date.now()}`, year: '', title: '', description: '' },
      ],
    });
  };

  const updateEvent = (index: number, updates: Partial<TimelineEvent>) => {
    const newEvents = [...timeline.events];
    newEvents[index] = { ...newEvents[index], ...updates };
    updateTimeline({ events: newEvents });
  };

  const removeEvent = (index: number) => {
    updateTimeline({ events: timeline.events.filter((_, i) => i !== index) });
  };

  return (
    <div className="space-y-4">
      <Input
        label="时间线标题"
        value={timeline.title}
        onChange={(e) => updateTimeline({ title: e.target.value })}
        placeholder="例如：中国近代史大事记"
      />

      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-dark-700">事件列表 ({timeline.events.length})</span>
        <button onClick={addEvent} className="text-sm text-primary-600 hover:text-primary-700">
          + 添加事件
        </button>
      </div>

      {timeline.events.map((event, index) => (
        <div key={event.id} className="p-4 border border-dark-200 rounded-lg space-y-3">
          <div className="flex justify-between">
            <span className="text-sm font-medium">事件 {index + 1}</span>
            <button onClick={() => removeEvent(index)} className="text-red-500 text-sm">
              <Trash2 size={16} />
            </button>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="年份/时间"
              value={event.year}
              onChange={(e) => updateEvent(index, { year: e.target.value })}
              placeholder="1949"
            />
            <Input
              label="分类标签"
              value={event.category || ''}
              onChange={(e) => updateEvent(index, { category: e.target.value })}
              placeholder="政治/经济/文化"
            />
          </div>
          <Input
            label="事件标题"
            value={event.title}
            onChange={(e) => updateEvent(index, { title: e.target.value })}
          />
          <div>
            <label className="block text-sm font-medium text-dark-700 mb-1.5">事件描述</label>
            <textarea
              value={event.description}
              onChange={(e) => updateEvent(index, { description: e.target.value })}
              rows={2}
              className="w-full rounded-lg border border-dark-200 px-3 py-2 text-sm"
            />
          </div>
        </div>
      ))}
    </div>
  );
}

/** 决策情景编辑器 */
function DecisionEditor({
  config,
  onChange,
}: {
  config: SimulatorConfig;
  onChange: (updates: Partial<SimulatorConfig>) => void;
}) {
  const decision = config.decision || { title: '', scenario: '', question: '', options: [] };

  const updateDecision = (updates: Partial<typeof decision>) => {
    onChange({ decision: { ...decision, ...updates } });
  };

  const addOption = () => {
    updateDecision({
      options: [
        ...decision.options,
        { id: `opt-${Date.now()}`, label: '', result: '' },
      ],
    });
  };

  const updateOption = (index: number, updates: Partial<DecisionOption>) => {
    const newOptions = [...decision.options];
    newOptions[index] = { ...newOptions[index], ...updates };
    updateDecision({ options: newOptions });
  };

  const removeOption = (index: number) => {
    updateDecision({ options: decision.options.filter((_, i) => i !== index) });
  };

  return (
    <div className="space-y-4">
      <Input
        label="标题"
        value={decision.title}
        onChange={(e) => updateDecision({ title: e.target.value })}
      />
      <div>
        <label className="block text-sm font-medium text-dark-700 mb-1.5">情景描述</label>
        <textarea
          value={decision.scenario}
          onChange={(e) => updateDecision({ scenario: e.target.value })}
          rows={3}
          className="w-full rounded-lg border border-dark-200 px-3 py-2 text-sm"
          placeholder="描述决策的背景和情境..."
        />
      </div>
      <Input
        label="决策问题"
        value={decision.question}
        onChange={(e) => updateDecision({ question: e.target.value })}
        placeholder="你会如何选择？"
      />

      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-dark-700">选项 ({decision.options.length})</span>
        <button onClick={addOption} className="text-sm text-primary-600">+ 添加选项</button>
      </div>

      {decision.options.map((option, index) => (
        <div key={option.id} className="p-4 border border-dark-200 rounded-lg space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">选项 {index + 1}</span>
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-1 text-sm">
                <input
                  type="checkbox"
                  checked={option.isOptimal || false}
                  onChange={(e) => updateOption(index, { isOptimal: e.target.checked })}
                />
                最佳选择
              </label>
              <button onClick={() => removeOption(index)} className="text-red-500">
                <Trash2 size={16} />
              </button>
            </div>
          </div>
          <Input
            label="选项文本"
            value={option.label}
            onChange={(e) => updateOption(index, { label: e.target.value })}
          />
          <div>
            <label className="block text-sm font-medium text-dark-700 mb-1.5">选择结果</label>
            <textarea
              value={option.result}
              onChange={(e) => updateOption(index, { result: e.target.value })}
              rows={2}
              className="w-full rounded-lg border border-dark-200 px-3 py-2 text-sm"
              placeholder="选择此选项后的结果..."
            />
          </div>
        </div>
      ))}

      <div>
        <label className="block text-sm font-medium text-dark-700 mb-1.5">综合分析（可选）</label>
        <textarea
          value={decision.analysis || ''}
          onChange={(e) => updateDecision({ analysis: e.target.value })}
          rows={2}
          className="w-full rounded-lg border border-dark-200 px-3 py-2 text-sm"
        />
      </div>
    </div>
  );
}

/** 对比分析编辑器 */
function ComparisonEditor({
  config,
  onChange,
}: {
  config: SimulatorConfig;
  onChange: (updates: Partial<SimulatorConfig>) => void;
}) {
  const comparison = config.comparison || { title: '', dimensions: [], items: [] };

  const updateComparison = (updates: Partial<typeof comparison>) => {
    onChange({ comparison: { ...comparison, ...updates } });
  };

  const addItem = () => {
    updateComparison({
      items: [
        ...comparison.items,
        { id: `item-${Date.now()}`, name: '', attributes: {} },
      ],
    });
  };

  const updateItem = (index: number, updates: Partial<ComparisonItem>) => {
    const newItems = [...comparison.items];
    newItems[index] = { ...newItems[index], ...updates };
    updateComparison({ items: newItems });
  };

  const removeItem = (index: number) => {
    updateComparison({ items: comparison.items.filter((_, i) => i !== index) });
  };

  const updateItemAttribute = (itemIndex: number, dimension: string, value: string) => {
    const newItems = [...comparison.items];
    newItems[itemIndex] = {
      ...newItems[itemIndex],
      attributes: { ...newItems[itemIndex].attributes, [dimension]: value },
    };
    updateComparison({ items: newItems });
  };

  return (
    <div className="space-y-4">
      <Input
        label="标题"
        value={comparison.title}
        onChange={(e) => updateComparison({ title: e.target.value })}
      />
      <div>
        <label className="block text-sm font-medium text-dark-700 mb-1.5">
          对比维度（每行一个）
        </label>
        <textarea
          value={comparison.dimensions.join('\n')}
          onChange={(e) => updateComparison({ dimensions: e.target.value.split('\n').filter(Boolean) })}
          rows={3}
          className="w-full rounded-lg border border-dark-200 px-3 py-2 text-sm"
          placeholder="时间&#10;地点&#10;特点"
        />
      </div>

      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-dark-700">对比对象 ({comparison.items.length})</span>
        <button onClick={addItem} className="text-sm text-primary-600">+ 添加对象</button>
      </div>

      {comparison.items.map((item, index) => (
        <div key={item.id} className="p-4 border border-dark-200 rounded-lg space-y-3">
          <div className="flex justify-between">
            <Input
              label="名称"
              value={item.name}
              onChange={(e) => updateItem(index, { name: e.target.value })}
              className="flex-1"
            />
            <button onClick={() => removeItem(index)} className="text-red-500 ml-2 mt-6">
              <Trash2 size={16} />
            </button>
          </div>
          {comparison.dimensions.map((dim) => (
            <Input
              key={dim}
              label={dim}
              value={item.attributes[dim] || ''}
              onChange={(e) => updateItemAttribute(index, dim, e.target.value)}
            />
          ))}
        </div>
      ))}

      <div>
        <label className="block text-sm font-medium text-dark-700 mb-1.5">结论（可选）</label>
        <textarea
          value={comparison.conclusion || ''}
          onChange={(e) => updateComparison({ conclusion: e.target.value })}
          rows={2}
          className="w-full rounded-lg border border-dark-200 px-3 py-2 text-sm"
        />
      </div>
    </div>
  );
}

/** 概念关系图编辑器 */
function ConceptMapEditor({
  config,
  onChange,
}: {
  config: SimulatorConfig;
  onChange: (updates: Partial<SimulatorConfig>) => void;
}) {
  const conceptMap = config.conceptMap || { title: '', nodes: [], relations: [] };

  const updateConceptMap = (updates: Partial<typeof conceptMap>) => {
    onChange({ conceptMap: { ...conceptMap, ...updates } });
  };

  const addNode = () => {
    updateConceptMap({
      nodes: [
        ...conceptMap.nodes,
        { id: `node-${Date.now()}`, label: '', description: '' },
      ],
    });
  };

  const updateNode = (index: number, updates: Partial<ConceptNode>) => {
    const newNodes = [...conceptMap.nodes];
    newNodes[index] = { ...newNodes[index], ...updates };
    updateConceptMap({ nodes: newNodes });
  };

  const removeNode = (index: number) => {
    const nodeId = conceptMap.nodes[index].id;
    updateConceptMap({
      nodes: conceptMap.nodes.filter((_, i) => i !== index),
      relations: conceptMap.relations.filter(r => r.from !== nodeId && r.to !== nodeId),
    });
  };

  const addRelation = () => {
    if (conceptMap.nodes.length < 2) return;
    updateConceptMap({
      relations: [
        ...conceptMap.relations,
        { from: conceptMap.nodes[0].id, to: conceptMap.nodes[1].id, label: '' },
      ],
    });
  };

  const updateRelation = (index: number, updates: Partial<ConceptRelation>) => {
    const newRelations = [...conceptMap.relations];
    newRelations[index] = { ...newRelations[index], ...updates };
    updateConceptMap({ relations: newRelations });
  };

  const removeRelation = (index: number) => {
    updateConceptMap({ relations: conceptMap.relations.filter((_, i) => i !== index) });
  };

  return (
    <div className="space-y-4">
      <Input
        label="标题"
        value={conceptMap.title}
        onChange={(e) => updateConceptMap({ title: e.target.value })}
      />

      {/* 概念节点 */}
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-dark-700">概念节点 ({conceptMap.nodes.length})</span>
        <button onClick={addNode} className="text-sm text-primary-600">+ 添加概念</button>
      </div>

      {conceptMap.nodes.map((node, index) => (
        <div key={node.id} className="p-3 border border-dark-200 rounded-lg space-y-2">
          <div className="flex gap-2">
            <Input
              label="概念名称"
              value={node.label}
              onChange={(e) => updateNode(index, { label: e.target.value })}
              className="flex-1"
            />
            <Input
              label="分类"
              value={node.category || ''}
              onChange={(e) => updateNode(index, { category: e.target.value })}
              className="w-24"
            />
            <button onClick={() => removeNode(index)} className="text-red-500 mt-6">
              <Trash2 size={16} />
            </button>
          </div>
          <Input
            label="描述"
            value={node.description || ''}
            onChange={(e) => updateNode(index, { description: e.target.value })}
          />
        </div>
      ))}

      {/* 关系 */}
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-dark-700">关系 ({conceptMap.relations.length})</span>
        <button
          onClick={addRelation}
          disabled={conceptMap.nodes.length < 2}
          className="text-sm text-primary-600 disabled:opacity-40"
        >
          + 添加关系
        </button>
      </div>

      {conceptMap.relations.map((rel, index) => (
        <div key={index} className="p-3 border border-dark-200 rounded-lg flex gap-2 items-end">
          <div className="flex-1">
            <label className="block text-xs text-dark-500 mb-1">从</label>
            <select
              value={rel.from}
              onChange={(e) => updateRelation(index, { from: e.target.value })}
              className="w-full rounded border border-dark-200 px-2 py-1 text-sm"
            >
              {conceptMap.nodes.map(n => (
                <option key={n.id} value={n.id}>{n.label || n.id}</option>
              ))}
            </select>
          </div>
          <Input
            label="关系"
            value={rel.label || ''}
            onChange={(e) => updateRelation(index, { label: e.target.value })}
            className="w-24"
            placeholder="导致"
          />
          <div className="flex-1">
            <label className="block text-xs text-dark-500 mb-1">到</label>
            <select
              value={rel.to}
              onChange={(e) => updateRelation(index, { to: e.target.value })}
              className="w-full rounded border border-dark-200 px-2 py-1 text-sm"
            >
              {conceptMap.nodes.map(n => (
                <option key={n.id} value={n.id}>{n.label || n.id}</option>
              ))}
            </select>
          </div>
          <button onClick={() => removeRelation(index)} className="text-red-500">
            <Trash2 size={16} />
          </button>
        </div>
      ))}
    </div>
  );
}

/** 输入参数编辑器 */
function InputsEditor({
  inputs,
  onChange,
}: {
  inputs: SimulatorInputConfig[];
  onChange: (inputs: SimulatorInputConfig[]) => void;
}) {
  const addInput = () => {
    onChange([
      ...inputs,
      {
        id: `input-${Date.now()}`,
        name: `param${inputs.length + 1}`,
        label: '新参数',
        type: 'slider',
        defaultValue: 50,
        min: 0,
        max: 100,
        step: 1,
      },
    ]);
  };

  const updateInput = (index: number, updates: Partial<SimulatorInputConfig>) => {
    const newInputs = [...inputs];
    newInputs[index] = { ...newInputs[index], ...updates };
    onChange(newInputs);
  };

  const removeInput = (index: number) => {
    onChange(inputs.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-dark-700">
          输入参数 ({inputs.length})
        </span>
        <button
          onClick={addInput}
          className="flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700"
        >
          <Plus size={16} />
          添加参数
        </button>
      </div>

      {inputs.map((input, index) => (
        <div key={input.id} className="p-4 border border-dark-200 rounded-lg space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-dark-600">参数 {index + 1}</span>
            <button
              onClick={() => removeInput(index)}
              className="text-red-500 hover:text-red-600"
            >
              <Trash2 size={16} />
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="变量名"
              value={input.name}
              onChange={(e) => updateInput(index, { name: e.target.value })}
            />
            <Input
              label="显示标签"
              value={input.label}
              onChange={(e) => updateInput(index, { label: e.target.value })}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-dark-700 mb-1.5">类型</label>
              <select
                value={input.type}
                onChange={(e) => updateInput(index, { type: e.target.value as SimulatorInputConfig['type'] })}
                className="w-full rounded-lg border border-dark-200 px-3 py-2 text-sm"
              >
                <option value="slider">滑块</option>
                <option value="number">数字输入</option>
                <option value="select">下拉选择</option>
              </select>
            </div>
            <Input
              label="单位"
              value={input.unit || ''}
              onChange={(e) => updateInput(index, { unit: e.target.value })}
            />
          </div>

          {(input.type === 'slider' || input.type === 'number') && (
            <div className="grid grid-cols-4 gap-3">
              <Input
                label="默认值"
                type="number"
                value={input.defaultValue}
                onChange={(e) => updateInput(index, { defaultValue: Number(e.target.value) })}
              />
              <Input
                label="最小值"
                type="number"
                value={input.min ?? 0}
                onChange={(e) => updateInput(index, { min: Number(e.target.value) })}
              />
              <Input
                label="最大值"
                type="number"
                value={input.max ?? 100}
                onChange={(e) => updateInput(index, { max: Number(e.target.value) })}
              />
              <Input
                label="步长"
                type="number"
                value={input.step ?? 1}
                onChange={(e) => updateInput(index, { step: Number(e.target.value) })}
              />
            </div>
          )}

          <Input
            label="提示信息"
            value={input.hint || ''}
            onChange={(e) => updateInput(index, { hint: e.target.value })}
            placeholder="推荐值或说明..."
          />
        </div>
      ))}

      {inputs.length === 0 && (
        <div className="text-center py-8 text-dark-400 text-sm">
          暂无输入参数，点击上方按钮添加
        </div>
      )}
    </div>
  );
}

/** 输出配置编辑器 */
function OutputsEditor({
  outputs,
  onChange,
}: {
  outputs: SimulatorOutputConfig[];
  onChange: (outputs: SimulatorOutputConfig[]) => void;
}) {
  const addOutput = () => {
    onChange([
      ...outputs,
      {
        id: `output-${Date.now()}`,
        name: `result${outputs.length + 1}`,
        label: '新输出',
        type: 'number',
        formula: '',
      },
    ]);
  };

  const updateOutput = (index: number, updates: Partial<SimulatorOutputConfig>) => {
    const newOutputs = [...outputs];
    newOutputs[index] = { ...newOutputs[index], ...updates };
    onChange(newOutputs);
  };

  const removeOutput = (index: number) => {
    onChange(outputs.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-dark-700">
          输出配置 ({outputs.length})
        </span>
        <button
          onClick={addOutput}
          className="flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700"
        >
          <Plus size={16} />
          添加输出
        </button>
      </div>

      {outputs.map((output, index) => (
        <div key={output.id} className="p-4 border border-dark-200 rounded-lg space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-dark-600">输出 {index + 1}</span>
            <button
              onClick={() => removeOutput(index)}
              className="text-red-500 hover:text-red-600"
            >
              <Trash2 size={16} />
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="变量名"
              value={output.name}
              onChange={(e) => updateOutput(index, { name: e.target.value })}
            />
            <Input
              label="显示标签"
              value={output.label}
              onChange={(e) => updateOutput(index, { label: e.target.value })}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-dark-700 mb-1.5">类型</label>
              <select
                value={output.type}
                onChange={(e) => updateOutput(index, { type: e.target.value as SimulatorOutputConfig['type'] })}
                className="w-full rounded-lg border border-dark-200 px-3 py-2 text-sm"
              >
                <option value="number">数值</option>
                <option value="progress">进度条</option>
                <option value="text">文本</option>
              </select>
            </div>
            <Input
              label="单位"
              value={output.unit || ''}
              onChange={(e) => updateOutput(index, { unit: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-dark-700 mb-1.5">
              计算公式
            </label>
            <input
              value={output.formula || ''}
              onChange={(e) => updateOutput(index, { formula: e.target.value })}
              placeholder="例如: input.mass * input.acceleration"
              className="w-full rounded-lg border border-dark-200 px-3 py-2 text-sm font-mono"
            />
            <p className="text-xs text-dark-400 mt-1">
              使用 input.变量名 引用输入参数
            </p>
          </div>

          {output.type === 'progress' && (
            <Input
              label="进度条颜色"
              type="color"
              value={output.color || '#3b82f6'}
              onChange={(e) => updateOutput(index, { color: e.target.value })}
            />
          )}
        </div>
      ))}

      {outputs.length === 0 && (
        <div className="text-center py-8 text-dark-400 text-sm">
          暂无输出配置，点击上方按钮添加
        </div>
      )}
    </div>
  );
}

export default SimulatorConfigEditor;
