'use client';

/**
 * SimulatorRenderer - 模拟器渲染器
 * 支持多种模拟器类型：custom, preset, timeline, decision, comparison, concept-map, iframe
 */

import React, { useState, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { Play, RotateCcw, FlaskConical, Clock, GitBranch, BarChart3, Network, ExternalLink, CheckCircle2 } from 'lucide-react';
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
    // 支持 variables 和 inputs 两种格式
    const vars = config.variables || config.inputs;
    if (vars) {
      vars.forEach((v: any) => {
        initial[v.name || v.id] = v.default ?? v.defaultValue ?? 0;
      });
    }
    return initial;
  });
  const [selectedDecision, setSelectedDecision] = useState<string | null>(null);
  const [activeTimelineEvent, setActiveTimelineEvent] = useState<number>(0);

  const handleStart = useCallback(() => {
    setIsStarted(true);
  }, []);

  const handleReset = useCallback(() => {
    setIsStarted(false);
    setKey(k => k + 1);
    setSelectedDecision(null);
    setActiveTimelineEvent(0);
    // 重置变量
    const initial: Record<string, number> = {};
    const vars = config.variables || config.inputs;
    if (vars) {
      vars.forEach((v: any) => {
        initial[v.name || v.id] = v.default ?? v.defaultValue ?? 0;
      });
    }
    setVariables(initial);
  }, [config.variables, config.inputs]);

  const handleVariableChange = useCallback((name: string, value: number) => {
    setVariables(prev => ({ ...prev, [name]: value }));
  }, []);

  // 检查是否有有效的自定义代码
  const hasValidCode = config.mode === 'custom' && config.custom_code;
  // 检查是否有 inputs/outputs 配置（可以渲染交互式界面）
  const hasInputsOutputs = config.inputs && config.inputs.length > 0;

  // 根据类型渲染不同的模拟器
  const renderByType = () => {
    switch (config.type) {
      case 'timeline':
        return <TimelineRenderer config={config} activeEvent={activeTimelineEvent} onEventChange={setActiveTimelineEvent} />;
      case 'decision':
        return <DecisionRenderer config={config} selected={selectedDecision} onSelect={setSelectedDecision} />;
      case 'comparison':
        return <ComparisonRenderer config={config} />;
      case 'concept-map':
        return <ConceptMapRenderer config={config} />;
      case 'iframe':
        return <IframeRenderer config={config} />;
      case 'preset':
        return <PresetRenderer config={config} />;
      case 'custom':
        if (hasValidCode) {
          return null; // 使用下面的 CustomRenderer
        }
        if (hasInputsOutputs) {
          return <InputsOutputsRenderer config={config} variables={variables} onVariableChange={handleVariableChange} />;
        }
        return <PlaceholderRenderer config={config} message="模拟器代码未配置" />;
      default:
        // 默认情况：如果有 inputs/outputs，显示交互界面
        if (hasInputsOutputs) {
          return <InputsOutputsRenderer config={config} variables={variables} onVariableChange={handleVariableChange} />;
        }
        return <PlaceholderRenderer config={config} message={config.description || '模拟器预览'} />;
    }
  };

  // 如果是特殊类型（非 custom code），直接渲染
  if (config.type && config.type !== 'custom') {
    return (
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <div className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-purple-500/20 rounded-xl flex items-center justify-center">
              {getTypeIcon(config.type)}
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">{config.name || getTypeName(config.type)}</h3>
              <p className="text-slate-400 text-sm">{config.description || ''}</p>
            </div>
          </div>
          {renderByType()}
        </div>
      </div>
    );
  }

  // 如果有 inputs/outputs 但没有 custom_code，显示交互界面
  if (hasInputsOutputs && !hasValidCode) {
    return (
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <div className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-purple-500/20 rounded-xl flex items-center justify-center">
              <FlaskConical className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">{config.name || '互动模拟器'}</h3>
              <p className="text-slate-400 text-sm">{config.description || '通过调整参数观察变化'}</p>
            </div>
          </div>
          <InputsOutputsRenderer config={config} variables={variables} onVariableChange={handleVariableChange} />
        </div>
      </div>
    );
  }

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
          <PlaceholderRenderer config={config} message="模拟器预览" />
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

// 获取类型图标
function getTypeIcon(type: string) {
  switch (type) {
    case 'timeline': return <Clock className="w-5 h-5 text-blue-400" />;
    case 'decision': return <GitBranch className="w-5 h-5 text-green-400" />;
    case 'comparison': return <BarChart3 className="w-5 h-5 text-orange-400" />;
    case 'concept-map': return <Network className="w-5 h-5 text-cyan-400" />;
    case 'iframe': return <ExternalLink className="w-5 h-5 text-pink-400" />;
    default: return <FlaskConical className="w-5 h-5 text-purple-400" />;
  }
}

// 获取类型名称
function getTypeName(type: string) {
  switch (type) {
    case 'timeline': return '时间线探索';
    case 'decision': return '决策情景';
    case 'comparison': return '对比分析';
    case 'concept-map': return '概念关系图';
    case 'iframe': return '外部嵌入';
    case 'preset': return '预设模拟器';
    default: return '模拟器';
  }
}

// 占位渲染器
function PlaceholderRenderer({ config, message }: { config: SimulatorConfig; message: string }) {
  return (
    <div className="flex items-center justify-center h-48 bg-slate-800/50 rounded-xl">
      <div className="text-center">
        <FlaskConical className="w-12 h-12 text-purple-400 mx-auto mb-3" />
        <p className="text-slate-300 font-medium">{config.name || '模拟器'}</p>
        <p className="text-slate-500 text-sm mt-1">{message}</p>
      </div>
    </div>
  );
}

// 预设模拟器渲染器
function PresetRenderer({ config }: { config: SimulatorConfig }) {
  return (
    <div className="flex items-center justify-center h-48 bg-slate-800/50 rounded-xl">
      <div className="text-center">
        <FlaskConical className="w-12 h-12 text-purple-400 mx-auto mb-3" />
        <p className="text-slate-300 font-medium">{config.name || '预设模拟器'}</p>
        <p className="text-slate-500 text-sm mt-1">{config.description || '预设模拟器预览'}</p>
        {config.presetId && (
          <p className="text-purple-400 text-xs mt-2">预设ID: {config.presetId}</p>
        )}
      </div>
    </div>
  );
}

// 输入输出交互渲染器
function InputsOutputsRenderer({
  config,
  variables,
  onVariableChange
}: {
  config: SimulatorConfig;
  variables: Record<string, number>;
  onVariableChange: (name: string, value: number) => void;
}) {
  return (
    <div className="bg-slate-800/50 rounded-xl p-4 space-y-4">
      {/* 输入控件 */}
      {config.inputs && config.inputs.length > 0 && (
        <div className="space-y-3">
          <p className="text-slate-400 text-xs uppercase">输入参数</p>
          {config.inputs.map((input: any, i: number) => (
            <div key={i} className="flex items-center gap-4">
              <label className="text-slate-300 text-sm w-32">{input.label || input.name}</label>
              <input
                type="range"
                min={input.min ?? 0}
                max={input.max ?? 100}
                step={input.step ?? 1}
                value={variables[input.name] ?? input.defaultValue ?? input.default ?? 0}
                onChange={(e) => onVariableChange(input.name, parseFloat(e.target.value))}
                className="flex-1 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
              />
              <span className="text-purple-400 text-sm w-20 text-right">
                {variables[input.name] ?? input.defaultValue ?? input.default ?? 0} {input.unit || ''}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* 输出显示 */}
      {config.outputs && config.outputs.length > 0 && (
        <div className="border-t border-slate-700 pt-4">
          <p className="text-slate-400 text-xs uppercase mb-3">输出结果</p>
          <div className="grid grid-cols-2 gap-3">
            {config.outputs.map((output: any, i: number) => {
              let value = 0;
              if (output.formula) {
                try {
                  let formula = output.formula;
                  Object.entries(variables).forEach(([name, val]) => {
                    formula = formula.replace(new RegExp(`input\\.${name}`, 'g'), String(val));
                  });
                  value = eval(formula);
                } catch {
                  value = 0;
                }
              }
              return (
                <div key={i} className="bg-slate-700/50 rounded-lg p-3">
                  <p className="text-slate-400 text-xs">{output.label || output.name}</p>
                  <p className="text-purple-400 text-xl font-bold">
                    {value.toFixed(2)} {output.unit || ''}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 说明 */}
      {config.instructions && config.instructions.length > 0 && (
        <div className="border-t border-slate-700 pt-4">
          <p className="text-slate-400 text-xs uppercase mb-2">操作说明</p>
          <ul className="space-y-1">
            {config.instructions.map((instruction: string, i: number) => (
              <li key={i} className="text-slate-300 text-sm flex items-start gap-2">
                <span className="text-purple-400">•</span>
                {instruction}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

// 时间线渲染器
function TimelineRenderer({
  config,
  activeEvent,
  onEventChange
}: {
  config: SimulatorConfig;
  activeEvent: number;
  onEventChange: (index: number) => void;
}) {
  const timeline = config.timeline;
  if (!timeline || !timeline.events || timeline.events.length === 0) {
    return <PlaceholderRenderer config={config} message="时间线数据未配置" />;
  }

  return (
    <div className="bg-slate-800/50 rounded-xl p-4">
      {timeline.title && (
        <h4 className="text-white font-medium mb-4">{timeline.title}</h4>
      )}
      <div className="relative">
        {/* 时间线 */}
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-slate-600" />
        <div className="space-y-4">
          {timeline.events.map((event: any, index: number) => (
            <button
              key={event.id || index}
              onClick={() => onEventChange(index)}
              className={`relative pl-10 pr-4 py-3 w-full text-left rounded-lg transition-all ${
                activeEvent === index
                  ? 'bg-blue-500/20 border border-blue-500/50'
                  : 'hover:bg-slate-700/50'
              }`}
            >
              <div className={`absolute left-2 top-1/2 -translate-y-1/2 w-4 h-4 rounded-full border-2 ${
                activeEvent === index
                  ? 'bg-blue-500 border-blue-400'
                  : 'bg-slate-700 border-slate-500'
              }`} />
              <div className="flex items-center gap-2 mb-1">
                <span className="text-blue-400 text-sm font-medium">{event.year}</span>
                {event.category && (
                  <span className="text-xs px-2 py-0.5 bg-slate-600 rounded text-slate-300">{event.category}</span>
                )}
              </div>
              <p className="text-white font-medium">{event.title}</p>
              {activeEvent === index && event.description && (
                <p className="text-slate-400 text-sm mt-2">{event.description}</p>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

// 决策情景渲染器
function DecisionRenderer({
  config,
  selected,
  onSelect
}: {
  config: SimulatorConfig;
  selected: string | null;
  onSelect: (id: string) => void;
}) {
  const decision = config.decision;
  if (!decision) {
    return <PlaceholderRenderer config={config} message="决策数据未配置" />;
  }

  const selectedOption = decision.options?.find((o: any) => o.id === selected);

  return (
    <div className="bg-slate-800/50 rounded-xl p-4 space-y-4">
      {decision.scenario && (
        <div className="p-3 bg-slate-700/50 rounded-lg">
          <p className="text-slate-300 text-sm">{decision.scenario}</p>
        </div>
      )}
      {decision.question && (
        <p className="text-white font-medium">{decision.question}</p>
      )}
      <div className="space-y-2">
        {decision.options?.map((option: any) => (
          <button
            key={option.id}
            onClick={() => onSelect(option.id)}
            className={`w-full p-3 rounded-lg text-left transition-all flex items-center gap-3 ${
              selected === option.id
                ? option.isOptimal
                  ? 'bg-green-500/20 border border-green-500/50'
                  : 'bg-orange-500/20 border border-orange-500/50'
                : 'bg-slate-700/50 hover:bg-slate-700'
            }`}
          >
            <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
              selected === option.id
                ? option.isOptimal
                  ? 'border-green-500 bg-green-500'
                  : 'border-orange-500 bg-orange-500'
                : 'border-slate-500'
            }`}>
              {selected === option.id && <CheckCircle2 className="w-3 h-3 text-white" />}
            </div>
            <span className="text-slate-200">{option.label}</span>
          </button>
        ))}
      </div>
      {selectedOption && selectedOption.result && (
        <div className={`p-3 rounded-lg ${
          selectedOption.isOptimal ? 'bg-green-500/10 border border-green-500/30' : 'bg-orange-500/10 border border-orange-500/30'
        }`}>
          <p className="text-xs uppercase mb-1 ${selectedOption.isOptimal ? 'text-green-400' : 'text-orange-400'}">
            {selectedOption.isOptimal ? '最佳选择' : '选择结果'}
          </p>
          <p className="text-slate-300 text-sm">{selectedOption.result}</p>
        </div>
      )}
      {decision.analysis && selected && (
        <div className="p-3 bg-slate-700/50 rounded-lg">
          <p className="text-xs uppercase mb-1 text-slate-400">综合分析</p>
          <p className="text-slate-300 text-sm">{decision.analysis}</p>
        </div>
      )}
    </div>
  );
}

// 对比分析渲染器
function ComparisonRenderer({ config }: { config: SimulatorConfig }) {
  const comparison = config.comparison;
  if (!comparison || !comparison.items || comparison.items.length === 0) {
    return <PlaceholderRenderer config={config} message="对比数据未配置" />;
  }

  return (
    <div className="bg-slate-800/50 rounded-xl p-4">
      {comparison.title && (
        <h4 className="text-white font-medium mb-4">{comparison.title}</h4>
      )}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-600">
              <th className="text-left py-2 px-3 text-slate-400">维度</th>
              {comparison.items.map((item: any) => (
                <th key={item.id} className="text-left py-2 px-3 text-purple-400">{item.name}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {comparison.dimensions?.map((dim: string) => (
              <tr key={dim} className="border-b border-slate-700/50">
                <td className="py-2 px-3 text-slate-400">{dim}</td>
                {comparison.items.map((item: any) => (
                  <td key={item.id} className="py-2 px-3 text-slate-200">
                    {item.attributes?.[dim] || '-'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {comparison.conclusion && (
        <div className="mt-4 p-3 bg-slate-700/50 rounded-lg">
          <p className="text-xs uppercase mb-1 text-slate-400">结论</p>
          <p className="text-slate-300 text-sm">{comparison.conclusion}</p>
        </div>
      )}
    </div>
  );
}

// 概念关系图渲染器
function ConceptMapRenderer({ config }: { config: SimulatorConfig }) {
  const conceptMap = config.conceptMap;
  if (!conceptMap || !conceptMap.nodes || conceptMap.nodes.length === 0) {
    return <PlaceholderRenderer config={config} message="概念图数据未配置" />;
  }

  return (
    <div className="bg-slate-800/50 rounded-xl p-4">
      {conceptMap.title && (
        <h4 className="text-white font-medium mb-4">{conceptMap.title}</h4>
      )}
      {/* 简单的节点列表展示 */}
      <div className="space-y-3">
        {conceptMap.nodes.map((node: any) => (
          <div key={node.id} className="p-3 bg-slate-700/50 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-cyan-400 font-medium">{node.label}</span>
              {node.category && (
                <span className="text-xs px-2 py-0.5 bg-slate-600 rounded text-slate-300">{node.category}</span>
              )}
            </div>
            {node.description && (
              <p className="text-slate-400 text-sm">{node.description}</p>
            )}
          </div>
        ))}
      </div>
      {/* 关系列表 */}
      {conceptMap.relations && conceptMap.relations.length > 0 && (
        <div className="mt-4 pt-4 border-t border-slate-700">
          <p className="text-xs uppercase mb-2 text-slate-400">关系</p>
          <div className="space-y-2">
            {conceptMap.relations.map((rel: any, i: number) => {
              const fromNode = conceptMap.nodes.find((n: any) => n.id === rel.from);
              const toNode = conceptMap.nodes.find((n: any) => n.id === rel.to);
              return (
                <div key={i} className="flex items-center gap-2 text-sm">
                  <span className="text-cyan-400">{fromNode?.label || rel.from}</span>
                  <span className="text-slate-500">→</span>
                  <span className="text-purple-400">{rel.label || '关联'}</span>
                  <span className="text-slate-500">→</span>
                  <span className="text-cyan-400">{toNode?.label || rel.to}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

// iframe 渲染器
function IframeRenderer({ config }: { config: SimulatorConfig }) {
  if (!config.iframeUrl) {
    return <PlaceholderRenderer config={config} message="嵌入URL未配置" />;
  }

  return (
    <div className="rounded-xl overflow-hidden">
      <iframe
        src={config.iframeUrl}
        className="w-full h-96 border-0"
        title={config.name || '外部嵌入'}
        sandbox="allow-scripts allow-same-origin"
      />
    </div>
  );
}

export default SimulatorRenderer;
