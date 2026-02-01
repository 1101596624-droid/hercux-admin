'use client';

/**
 * 概念关系图渲染器 - 增强版
 * 交互式概念网络，支持节点高亮和关系展示
 */

import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Network, ArrowRight, Info, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { ConceptMapConfig } from '@/types/editor';

interface ConceptMapRendererProps {
  config: ConceptMapConfig;
}

export function ConceptMapRenderer({ config }: ConceptMapRendererProps) {
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  if (!config.nodes || config.nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gradient-to-br from-slate-50 to-slate-100 rounded-2xl">
        <p className="text-slate-400">暂无概念数据</p>
      </div>
    );
  }

  // 获取与选中/悬停节点相关的关系
  const activeNodeId = selectedNode || hoveredNode;
  const relatedRelations = useMemo(() => {
    if (!activeNodeId) return [];
    return config.relations.filter(r => r.from === activeNodeId || r.to === activeNodeId);
  }, [activeNodeId, config.relations]);

  // 获取相关节点ID
  const relatedNodeIds = useMemo(() => {
    return new Set(relatedRelations.flatMap(r => [r.from, r.to]));
  }, [relatedRelations]);

  // 按分类分组节点
  const categories = useMemo(() => {
    return [...new Set(config.nodes.map(n => n.category || '其他'))];
  }, [config.nodes]);

  // 分类颜色
  const getCategoryColor = (category: string, index: number) => {
    const colors = [
      { bg: 'from-blue-500 to-indigo-600', light: 'bg-blue-500/10 border-blue-500/30', text: 'text-blue-400' },
      { bg: 'from-emerald-500 to-teal-600', light: 'bg-emerald-500/10 border-emerald-500/30', text: 'text-emerald-400' },
      { bg: 'from-purple-500 to-violet-600', light: 'bg-purple-500/10 border-purple-500/30', text: 'text-purple-400' },
      { bg: 'from-orange-500 to-amber-600', light: 'bg-orange-500/10 border-orange-500/30', text: 'text-orange-400' },
      { bg: 'from-pink-500 to-rose-600', light: 'bg-pink-500/10 border-pink-500/30', text: 'text-pink-400' },
      { bg: 'from-cyan-500 to-sky-600', light: 'bg-cyan-500/10 border-cyan-500/30', text: 'text-cyan-400' },
    ];
    return colors[index % colors.length];
  };

  const categoryColorMap = useMemo(() => {
    const map: Record<string, ReturnType<typeof getCategoryColor>> = {};
    categories.forEach((cat, index) => {
      map[cat] = getCategoryColor(cat, index);
    });
    return map;
  }, [categories]);

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
        {/* 网格背景 */}
        <div
          className="absolute inset-0 opacity-5"
          style={{
            backgroundImage: `radial-gradient(circle at 1px 1px, white 1px, transparent 0)`,
            backgroundSize: '40px 40px',
          }}
        />
      </div>

      <div className="relative z-10 p-6">
        {/* 标题 */}
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl">
            <Network className="w-5 h-5 text-white" />
          </div>
          <h3 className="text-xl font-bold text-white">{config.title}</h3>
        </div>

        {/* 分类图例 */}
        <div className="flex flex-wrap gap-2 mb-6">
          {categories.map((category) => {
            const color = categoryColorMap[category];
            return (
              <div
                key={category}
                className={cn(
                  'px-3 py-1.5 rounded-full text-xs font-medium border',
                  color.light,
                  color.text
                )}
              >
                {category}
              </div>
            );
          })}
        </div>

        {/* 概念节点网格 */}
        <div className="space-y-6 mb-6">
          {categories.map((category) => {
            const color = categoryColorMap[category];
            const categoryNodes = config.nodes.filter(n => (n.category || '其他') === category);

            return (
              <div key={category}>
                <div className={cn('text-sm font-medium mb-3', color.text)}>
                  {category}
                </div>
                <div className="flex flex-wrap gap-3">
                  {categoryNodes.map((node, index) => {
                    const isSelected = selectedNode === node.id;
                    const isRelated = activeNodeId && relatedNodeIds.has(node.id) && !isSelected;
                    const isActive = isSelected || node.id === hoveredNode;
                    const isDimmed = activeNodeId && !isSelected && !isRelated && node.id !== activeNodeId;

                    return (
                      <motion.button
                        key={node.id}
                        onClick={() => setSelectedNode(isSelected ? null : node.id)}
                        onMouseEnter={() => setHoveredNode(node.id)}
                        onMouseLeave={() => setHoveredNode(null)}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{
                          opacity: isDimmed ? 0.3 : 1,
                          scale: isActive ? 1.05 : 1,
                        }}
                        transition={{ delay: index * 0.05, duration: 0.2 }}
                        whileHover={{ scale: 1.08 }}
                        whileTap={{ scale: 0.95 }}
                        className={cn(
                          'relative px-4 py-2.5 rounded-xl font-medium transition-all duration-300',
                          'border-2 backdrop-blur-sm',
                          isSelected && `bg-gradient-to-r ${color.bg} text-white border-transparent shadow-lg`,
                          isRelated && `${color.light} ${color.text} border-2`,
                          !isSelected && !isRelated && 'bg-slate-800/50 text-slate-300 border-slate-700 hover:border-slate-600'
                        )}
                      >
                        {/* 脉冲动画 */}
                        {isSelected && (
                          <motion.div
                            className={cn('absolute inset-0 rounded-xl bg-gradient-to-r', color.bg)}
                            initial={{ scale: 1, opacity: 0.5 }}
                            animate={{ scale: 1.2, opacity: 0 }}
                            transition={{ duration: 1.5, repeat: Infinity }}
                          />
                        )}
                        <span className="relative z-10">{node.label}</span>
                      </motion.button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>

        {/* 选中节点详情 */}
        <AnimatePresence>
          {selectedNode && (
            <motion.div
              initial={{ opacity: 0, y: 20, height: 0 }}
              animate={{ opacity: 1, y: 0, height: 'auto' }}
              exit={{ opacity: 0, y: -20, height: 0 }}
              className="overflow-hidden"
            >
              {(() => {
                const node = config.nodes.find(n => n.id === selectedNode);
                if (!node) return null;
                const color = categoryColorMap[node.category || '其他'];

                return (
                  <div className="relative">
                    <div className={cn('absolute inset-0 bg-gradient-to-r rounded-2xl blur-xl opacity-30', color.bg)} />
                    <div className={cn(
                      'relative rounded-2xl p-5 border backdrop-blur-sm',
                      color.light
                    )}>
                      {/* 节点标题 */}
                      <div className="flex items-center gap-3 mb-4">
                        <div className={cn('p-2 rounded-lg bg-gradient-to-r', color.bg)}>
                          <Sparkles className="w-4 h-4 text-white" />
                        </div>
                        <div>
                          <h4 className="font-bold text-white text-lg">{node.label}</h4>
                          {node.category && (
                            <span className={cn('text-xs', color.text)}>{node.category}</span>
                          )}
                        </div>
                      </div>

                      {/* 节点描述 */}
                      {node.description && (
                        <p className="text-slate-300 leading-relaxed mb-4">
                          {node.description}
                        </p>
                      )}

                      {/* 关系列表 */}
                      {relatedRelations.length > 0 && (
                        <div className="space-y-3">
                          <div className="flex items-center gap-2 text-sm font-medium text-slate-400">
                            <Info className="w-4 h-4" />
                            相关关系
                          </div>
                          <div className="space-y-2">
                            {relatedRelations.map((rel, index) => {
                              const fromNode = config.nodes.find(n => n.id === rel.from);
                              const toNode = config.nodes.find(n => n.id === rel.to);
                              const isOutgoing = rel.from === selectedNode;

                              return (
                                <motion.div
                                  key={index}
                                  initial={{ opacity: 0, x: -10 }}
                                  animate={{ opacity: 1, x: 0 }}
                                  transition={{ delay: index * 0.1 }}
                                  className="flex items-center gap-3 p-3 rounded-lg bg-slate-800/50"
                                >
                                  <span className={cn(
                                    'font-medium',
                                    isOutgoing ? 'text-white' : 'text-slate-400'
                                  )}>
                                    {fromNode?.label}
                                  </span>
                                  <div className="flex items-center gap-2 text-slate-500">
                                    <div className="w-8 h-px bg-slate-600" />
                                    <span className="text-xs px-2 py-0.5 bg-slate-700 rounded-full">
                                      {rel.label || '关联'}
                                    </span>
                                    <ArrowRight className="w-4 h-4" />
                                  </div>
                                  <span className={cn(
                                    'font-medium',
                                    !isOutgoing ? 'text-white' : 'text-slate-400'
                                  )}>
                                    {toNode?.label}
                                  </span>
                                </motion.div>
                              );
                            })}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })()}
            </motion.div>
          )}
        </AnimatePresence>

        {/* 提示 */}
        {!selectedNode && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center text-sm text-slate-500 mt-4"
          >
            点击概念节点查看详情和关联关系
          </motion.p>
        )}
      </div>
    </div>
  );
}

export default ConceptMapRenderer;
