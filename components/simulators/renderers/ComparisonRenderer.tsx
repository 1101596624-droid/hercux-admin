'use client';

/**
 * 对比分析渲染器 - 增强版
 * 精美的对比表格，支持高亮和动画
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Scale, CheckCircle2, Info, ChevronDown, ChevronUp } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { ComparisonConfig } from '@/types/editor';

interface ComparisonRendererProps {
  config: ComparisonConfig;
}

export function ComparisonRenderer({ config }: ComparisonRendererProps) {
  const [hoveredCell, setHoveredCell] = useState<string | null>(null);
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  if (!config.items || config.items.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gradient-to-br from-slate-50 to-slate-100 rounded-2xl">
        <p className="text-slate-400">暂无对比数据</p>
      </div>
    );
  }

  // 生成渐变色
  const getItemColor = (index: number) => {
    const colors = [
      'from-blue-500 to-indigo-600',
      'from-emerald-500 to-teal-600',
      'from-purple-500 to-violet-600',
      'from-orange-500 to-amber-600',
      'from-pink-500 to-rose-600',
    ];
    return colors[index % colors.length];
  };

  const getItemBgColor = (index: number) => {
    const colors = [
      'bg-blue-500/10 border-blue-500/20',
      'bg-emerald-500/10 border-emerald-500/20',
      'bg-purple-500/10 border-purple-500/20',
      'bg-orange-500/10 border-orange-500/20',
      'bg-pink-500/10 border-pink-500/20',
    ];
    return colors[index % colors.length];
  };

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 p-6">
        {/* 标题 */}
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-gradient-to-br from-purple-500 to-violet-600 rounded-xl">
            <Scale className="w-5 h-5 text-white" />
          </div>
          <h3 className="text-xl font-bold text-white">{config.title}</h3>
        </div>

        {/* 对比项卡片 */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 mb-6">
          {config.items.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={cn(
                'relative overflow-hidden rounded-xl p-4 border backdrop-blur-sm',
                getItemBgColor(index)
              )}
            >
              <div className={cn(
                'absolute top-0 left-0 right-0 h-1 bg-gradient-to-r',
                getItemColor(index)
              )} />
              <h4 className="font-semibold text-white text-center">{item.name}</h4>
            </motion.div>
          ))}
        </div>

        {/* 对比表格 */}
        <div className="overflow-hidden rounded-xl border border-slate-700/50 backdrop-blur-sm">
          {/* 表头 */}
          <div className="grid bg-slate-800/80" style={{ gridTemplateColumns: `200px repeat(${config.items.length}, 1fr)` }}>
            <div className="p-4 font-medium text-slate-400 border-b border-r border-slate-700/50">
              对比维度
            </div>
            {config.items.map((item, index) => (
              <div
                key={item.id}
                className={cn(
                  'p-4 font-semibold text-center border-b border-slate-700/50',
                  index < config.items.length - 1 && 'border-r'
                )}
              >
                <span className={cn(
                  'bg-gradient-to-r bg-clip-text text-transparent',
                  getItemColor(index)
                )}>
                  {item.name}
                </span>
              </div>
            ))}
          </div>

          {/* 表格内容 */}
          {config.dimensions.map((dimension, rowIndex) => (
            <motion.div
              key={dimension}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: rowIndex * 0.05 }}
              className={cn(
                'grid transition-colors duration-200',
                rowIndex % 2 === 0 ? 'bg-slate-800/40' : 'bg-slate-800/20',
                expandedRow === dimension && 'bg-slate-700/40'
              )}
              style={{ gridTemplateColumns: `200px repeat(${config.items.length}, 1fr)` }}
            >
              {/* 维度名称 */}
              <div
                className={cn(
                  'p-4 font-medium text-slate-300 border-r border-slate-700/50 flex items-center justify-between cursor-pointer hover:bg-slate-700/30',
                  rowIndex < config.dimensions.length - 1 && 'border-b'
                )}
                onClick={() => setExpandedRow(expandedRow === dimension ? null : dimension)}
              >
                <span>{dimension}</span>
                {expandedRow === dimension ? (
                  <ChevronUp className="w-4 h-4 text-slate-500" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-slate-500" />
                )}
              </div>

              {/* 各项数值 */}
              {config.items.map((item, colIndex) => {
                const cellId = `${dimension}-${item.id}`;
                const value = item.attributes[dimension] || '-';
                const isHovered = hoveredCell === cellId;

                return (
                  <motion.div
                    key={item.id}
                    onMouseEnter={() => setHoveredCell(cellId)}
                    onMouseLeave={() => setHoveredCell(null)}
                    className={cn(
                      'p-4 text-center transition-all duration-200',
                      colIndex < config.items.length - 1 && 'border-r border-slate-700/50',
                      rowIndex < config.dimensions.length - 1 && 'border-b border-slate-700/50',
                      isHovered && 'bg-slate-600/30'
                    )}
                  >
                    <motion.span
                      animate={{ scale: isHovered ? 1.05 : 1 }}
                      className={cn(
                        'inline-block text-slate-200',
                        isHovered && 'font-medium'
                      )}
                    >
                      {value}
                    </motion.span>
                  </motion.div>
                );
              })}
            </motion.div>
          ))}
        </div>

        {/* 结论 */}
        {config.conclusion && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mt-6"
          >
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 rounded-2xl blur-xl" />
              <div className="relative bg-gradient-to-br from-emerald-500/10 to-teal-500/10 border border-emerald-500/20 rounded-2xl p-5">
                <div className="flex items-center gap-2 mb-3">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <h4 className="font-semibold text-emerald-300">结论</h4>
                </div>
                <p className="text-slate-300 leading-relaxed">{config.conclusion}</p>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}

export default ComparisonRenderer;
