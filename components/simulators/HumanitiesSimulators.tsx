'use client';

/**
 * 文科模拟器渲染组件
 * 简单的数据驱动设计，AI只需填充文本内容
 */

import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Check, X, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import type {
  TimelineConfig,
  DecisionScenarioConfig,
  ComparisonConfig,
  ConceptMapConfig,
} from '@/types/editor';

// ============================================
// 时间线探索
// ============================================

interface TimelineRendererProps {
  config: TimelineConfig;
}

export function TimelineRenderer({ config }: TimelineRendererProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const events = config.events;

  if (!events || events.length === 0) {
    return <div className="text-slate-400 text-center py-8">暂无时间线数据</div>;
  }

  const currentEvent = events[currentIndex];

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-slate-800">{config.title}</h3>

      {/* 时间轴导航 */}
      <div className="flex items-center gap-2 overflow-x-auto py-2">
        {events.map((event, index) => (
          <button
            key={event.id}
            onClick={() => setCurrentIndex(index)}
            className={cn(
              'flex-shrink-0 px-3 py-1.5 rounded-full text-sm font-medium transition-all',
              index === currentIndex
                ? 'bg-blue-500 text-white'
                : event.highlight
                ? 'bg-amber-100 text-amber-700 hover:bg-amber-200'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            )}
          >
            {event.year}
          </button>
        ))}
      </div>

      {/* 当前事件详情 */}
      <div className="bg-slate-50 rounded-xl p-5 border border-slate-200">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-2xl font-bold text-blue-600">{currentEvent.year}</span>
          {currentEvent.category && (
            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">
              {currentEvent.category}
            </span>
          )}
        </div>
        <h4 className="text-lg font-semibold text-slate-800 mb-2">{currentEvent.title}</h4>
        <p className="text-slate-600 leading-relaxed">{currentEvent.description}</p>
      </div>

      {/* 前后导航 */}
      <div className="flex justify-between">
        <button
          onClick={() => setCurrentIndex(Math.max(0, currentIndex - 1))}
          disabled={currentIndex === 0}
          className="flex items-center gap-1 px-3 py-1.5 text-sm text-slate-600 hover:text-slate-800 disabled:opacity-40"
        >
          <ChevronLeft size={16} /> 上一个
        </button>
        <span className="text-sm text-slate-400">{currentIndex + 1} / {events.length}</span>
        <button
          onClick={() => setCurrentIndex(Math.min(events.length - 1, currentIndex + 1))}
          disabled={currentIndex === events.length - 1}
          className="flex items-center gap-1 px-3 py-1.5 text-sm text-slate-600 hover:text-slate-800 disabled:opacity-40"
        >
          下一个 <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
}

// ============================================
// 决策情景模拟
// ============================================

interface DecisionRendererProps {
  config: DecisionScenarioConfig;
}

export function DecisionRenderer({ config }: DecisionRendererProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [showResult, setShowResult] = useState(false);

  const selectedOption = config.options.find(o => o.id === selectedId);

  const handleSelect = (id: string) => {
    setSelectedId(id);
    setShowResult(false);
  };

  const handleConfirm = () => {
    setShowResult(true);
  };

  const handleReset = () => {
    setSelectedId(null);
    setShowResult(false);
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-slate-800">{config.title}</h3>

      {/* 情景描述 */}
      <div className="bg-amber-50 rounded-xl p-4 border border-amber-200">
        <p className="text-slate-700 leading-relaxed">{config.scenario}</p>
      </div>

      {/* 决策问题 */}
      <div className="font-medium text-slate-800">{config.question}</div>

      {/* 选项列表 */}
      <div className="space-y-2">
        {config.options.map((option) => (
          <button
            key={option.id}
            onClick={() => handleSelect(option.id)}
            disabled={showResult}
            className={cn(
              'w-full text-left p-4 rounded-lg border-2 transition-all',
              selectedId === option.id
                ? showResult
                  ? option.isOptimal
                    ? 'border-green-500 bg-green-50'
                    : 'border-red-300 bg-red-50'
                  : 'border-blue-500 bg-blue-50'
                : 'border-slate-200 hover:border-slate-300 bg-white',
              showResult && option.isOptimal && selectedId !== option.id && 'border-green-300 bg-green-50'
            )}
          >
            <div className="flex items-start gap-3">
              <div className={cn(
                'w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5',
                selectedId === option.id
                  ? showResult
                    ? option.isOptimal ? 'bg-green-500 text-white' : 'bg-red-400 text-white'
                    : 'bg-blue-500 text-white'
                  : 'bg-slate-200'
              )}>
                {showResult && selectedId === option.id && (
                  option.isOptimal ? <Check size={14} /> : <X size={14} />
                )}
              </div>
              <div className="flex-1">
                <div className="font-medium text-slate-800">{option.label}</div>
                {showResult && (
                  <p className="text-sm text-slate-600 mt-2">{option.result}</p>
                )}
              </div>
            </div>
          </button>
        ))}
      </div>

      {/* 操作按钮 */}
      <div className="flex gap-2">
        {!showResult ? (
          <button
            onClick={handleConfirm}
            disabled={!selectedId}
            className="flex-1 py-2 bg-blue-500 text-white rounded-lg font-medium disabled:opacity-40 hover:bg-blue-600"
          >
            确认选择
          </button>
        ) : (
          <button
            onClick={handleReset}
            className="flex-1 py-2 bg-slate-500 text-white rounded-lg font-medium hover:bg-slate-600"
          >
            重新选择
          </button>
        )}
      </div>

      {/* 综合分析 */}
      {showResult && config.analysis && (
        <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
          <h4 className="font-medium text-blue-800 mb-2">综合分析</h4>
          <p className="text-slate-700 text-sm leading-relaxed">{config.analysis}</p>
        </div>
      )}
    </div>
  );
}

// ============================================
// 对比分析
// ============================================

interface ComparisonRendererProps {
  config: ComparisonConfig;
}

export function ComparisonRenderer({ config }: ComparisonRendererProps) {
  if (!config.items || config.items.length === 0) {
    return <div className="text-slate-400 text-center py-8">暂无对比数据</div>;
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-slate-800">{config.title}</h3>

      {/* 对比表格 */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-slate-100">
              <th className="text-left p-3 font-medium text-slate-600 border-b border-slate-200">
                对比维度
              </th>
              {config.items.map((item) => (
                <th key={item.id} className="text-left p-3 font-medium text-slate-800 border-b border-slate-200">
                  {item.name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {config.dimensions.map((dimension, index) => (
              <tr key={dimension} className={index % 2 === 0 ? 'bg-white' : 'bg-slate-50'}>
                <td className="p-3 font-medium text-slate-600 border-b border-slate-100">
                  {dimension}
                </td>
                {config.items.map((item) => (
                  <td key={item.id} className="p-3 text-slate-700 border-b border-slate-100">
                    {item.attributes[dimension] || '-'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 结论 */}
      {config.conclusion && (
        <div className="bg-green-50 rounded-xl p-4 border border-green-200">
          <h4 className="font-medium text-green-800 mb-2">结论</h4>
          <p className="text-slate-700 text-sm leading-relaxed">{config.conclusion}</p>
        </div>
      )}
    </div>
  );
}

// ============================================
// 概念关系图
// ============================================

interface ConceptMapRendererProps {
  config: ConceptMapConfig;
}

export function ConceptMapRenderer({ config }: ConceptMapRendererProps) {
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  if (!config.nodes || config.nodes.length === 0) {
    return <div className="text-slate-400 text-center py-8">暂无概念数据</div>;
  }

  // 获取与选中节点相关的关系
  const relatedRelations = selectedNode
    ? config.relations.filter(r => r.from === selectedNode || r.to === selectedNode)
    : [];

  // 获取相关节点ID
  const relatedNodeIds = new Set(
    relatedRelations.flatMap(r => [r.from, r.to])
  );

  // 按分类分组节点
  const categories = [...new Set(config.nodes.map(n => n.category || '其他'))];

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-slate-800">{config.title}</h3>

      {/* 概念节点 */}
      <div className="space-y-3">
        {categories.map(category => (
          <div key={category}>
            <div className="text-sm font-medium text-slate-500 mb-2">{category}</div>
            <div className="flex flex-wrap gap-2">
              {config.nodes
                .filter(n => (n.category || '其他') === category)
                .map(node => (
                  <button
                    key={node.id}
                    onClick={() => setSelectedNode(selectedNode === node.id ? null : node.id)}
                    className={cn(
                      'px-3 py-2 rounded-lg text-sm font-medium transition-all',
                      selectedNode === node.id
                        ? 'bg-blue-500 text-white'
                        : selectedNode && relatedNodeIds.has(node.id)
                        ? 'bg-blue-100 text-blue-700 border-2 border-blue-300'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    )}
                  >
                    {node.label}
                  </button>
                ))}
            </div>
          </div>
        ))}
      </div>

      {/* 选中节点详情 */}
      {selectedNode && (
        <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
          {(() => {
            const node = config.nodes.find(n => n.id === selectedNode);
            if (!node) return null;
            return (
              <>
                <h4 className="font-semibold text-blue-800 mb-2">{node.label}</h4>
                {node.description && (
                  <p className="text-slate-700 text-sm mb-3">{node.description}</p>
                )}

                {/* 关系列表 */}
                {relatedRelations.length > 0 && (
                  <div className="space-y-2">
                    <div className="text-sm font-medium text-slate-600">相关关系：</div>
                    {relatedRelations.map((rel, index) => {
                      const fromNode = config.nodes.find(n => n.id === rel.from);
                      const toNode = config.nodes.find(n => n.id === rel.to);
                      return (
                        <div key={index} className="flex items-center gap-2 text-sm text-slate-600">
                          <span className={rel.from === selectedNode ? 'font-medium text-blue-700' : ''}>
                            {fromNode?.label}
                          </span>
                          <ArrowRight size={14} className="text-slate-400" />
                          <span className="text-slate-500">{rel.label || '关联'}</span>
                          <ArrowRight size={14} className="text-slate-400" />
                          <span className={rel.to === selectedNode ? 'font-medium text-blue-700' : ''}>
                            {toNode?.label}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                )}
              </>
            );
          })()}
        </div>
      )}

      <p className="text-xs text-slate-400 text-center">点击概念查看详情和关联关系</p>
    </div>
  );
}
