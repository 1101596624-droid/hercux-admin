'use client';

/**
 * 决策情景渲染器 - 增强版
 * 沉浸式决策体验，精美的视觉反馈
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  AlertCircle,
  CheckCircle2,
  XCircle,
  Lightbulb,
  RotateCcw,
  Sparkles,
  Target
} from 'lucide-react';
import { cn } from '@/lib/utils';
import type { DecisionScenarioConfig } from '@/types/editor';

interface DecisionRendererProps {
  config: DecisionScenarioConfig;
}

export function DecisionRenderer({ config }: DecisionRendererProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  const selectedOption = config.options.find(o => o.id === selectedId);
  const isCorrect = selectedOption?.isOptimal;

  const handleSelect = (id: string) => {
    if (showResult) return;
    setSelectedId(id);
  };

  const handleConfirm = async () => {
    if (!selectedId) return;
    setIsAnimating(true);
    await new Promise(resolve => setTimeout(resolve, 800));
    setShowResult(true);
    setIsAnimating(false);
  };

  const handleReset = () => {
    setSelectedId(null);
    setShowResult(false);
  };

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-amber-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl" />
        {showResult && isCorrect && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-transparent"
          />
        )}
      </div>

      <div className="relative z-10 p-6">
        {/* 标题 */}
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl">
            <Target className="w-5 h-5 text-white" />
          </div>
          <h3 className="text-xl font-bold text-white">{config.title}</h3>
        </div>

        {/* 情景描述卡片 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative mb-6"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-amber-500/20 to-orange-500/20 rounded-2xl blur-xl" />
          <div className="relative bg-gradient-to-br from-amber-500/10 to-orange-500/10 border border-amber-500/20 rounded-2xl p-5">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
              <p className="text-slate-200 leading-relaxed">{config.scenario}</p>
            </div>
          </div>
        </motion.div>

        {/* 决策问题 */}
        <div className="flex items-center gap-2 mb-4">
          <Lightbulb className="w-5 h-5 text-yellow-400" />
          <p className="text-lg font-medium text-white">{config.question}</p>
        </div>

        {/* 选项列表 */}
        <div className="space-y-3 mb-6">
          {config.options.map((option, index) => {
            const isSelected = selectedId === option.id;
            const showCorrectHighlight = showResult && option.isOptimal;
            const showWrongHighlight = showResult && isSelected && !option.isOptimal;

            return (
              <motion.button
                key={option.id}
                onClick={() => handleSelect(option.id)}
                disabled={showResult}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={!showResult ? { scale: 1.02, x: 8 } : {}}
                whileTap={!showResult ? { scale: 0.98 } : {}}
                className={cn(
                  'w-full text-left p-4 rounded-xl border-2 transition-all duration-300',
                  'backdrop-blur-sm',
                  isSelected && !showResult && 'border-blue-500 bg-blue-500/10',
                  !isSelected && !showResult && 'border-slate-700 bg-slate-800/50 hover:border-slate-600',
                  showCorrectHighlight && 'border-emerald-500 bg-emerald-500/10',
                  showWrongHighlight && 'border-red-500 bg-red-500/10',
                  showResult && !showCorrectHighlight && !showWrongHighlight && 'border-slate-700 bg-slate-800/30 opacity-50'
                )}
              >
                <div className="flex items-start gap-4">
                  {/* 选项指示器 */}
                  <div className={cn(
                    'w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-300',
                    isSelected && !showResult && 'bg-blue-500 text-white',
                    !isSelected && !showResult && 'bg-slate-700 text-slate-400',
                    showCorrectHighlight && 'bg-emerald-500 text-white',
                    showWrongHighlight && 'bg-red-500 text-white'
                  )}>
                    {showResult ? (
                      showCorrectHighlight ? (
                        <CheckCircle2 className="w-5 h-5" />
                      ) : showWrongHighlight ? (
                        <XCircle className="w-5 h-5" />
                      ) : (
                        <span className="text-sm font-bold">{String.fromCharCode(65 + index)}</span>
                      )
                    ) : (
                      <span className="text-sm font-bold">{String.fromCharCode(65 + index)}</span>
                    )}
                  </div>

                  {/* 选项内容 */}
                  <div className="flex-1 min-w-0">
                    <div className={cn(
                      'font-medium transition-colors duration-300',
                      isSelected && !showResult && 'text-blue-300',
                      !isSelected && !showResult && 'text-slate-200',
                      showCorrectHighlight && 'text-emerald-300',
                      showWrongHighlight && 'text-red-300'
                    )}>
                      {option.label}
                    </div>

                    {/* 结果反馈 */}
                    <AnimatePresence>
                      {showResult && (isSelected || option.isOptimal) && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          className="mt-3 pt-3 border-t border-slate-700/50"
                        >
                          <p className="text-sm text-slate-400 leading-relaxed">
                            {option.result}
                          </p>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>

                  {/* 最佳选择标记 */}
                  {showResult && option.isOptimal && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="flex items-center gap-1 px-2 py-1 bg-emerald-500/20 rounded-full"
                    >
                      <Sparkles className="w-3 h-3 text-emerald-400" />
                      <span className="text-xs font-medium text-emerald-400">最佳</span>
                    </motion.div>
                  )}
                </div>
              </motion.button>
            );
          })}
        </div>

        {/* 操作按钮 */}
        <div className="flex gap-3">
          {!showResult ? (
            <motion.button
              onClick={handleConfirm}
              disabled={!selectedId || isAnimating}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={cn(
                'flex-1 py-3 rounded-xl font-medium transition-all duration-300',
                'flex items-center justify-center gap-2',
                selectedId && !isAnimating
                  ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/25'
                  : 'bg-slate-700 text-slate-400 cursor-not-allowed'
              )}
            >
              {isAnimating ? (
                <>
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
                  />
                  分析中...
                </>
              ) : (
                '确认选择'
              )}
            </motion.button>
          ) : (
            <motion.button
              onClick={handleReset}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="flex-1 py-3 rounded-xl font-medium bg-slate-700 text-white hover:bg-slate-600 flex items-center justify-center gap-2"
            >
              <RotateCcw className="w-4 h-4" />
              重新选择
            </motion.button>
          )}
        </div>

        {/* 综合分析 */}
        <AnimatePresence>
          {showResult && config.analysis && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mt-6"
            >
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-indigo-500/20 rounded-2xl blur-xl" />
                <div className="relative bg-gradient-to-br from-blue-500/10 to-indigo-500/10 border border-blue-500/20 rounded-2xl p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <Lightbulb className="w-5 h-5 text-blue-400" />
                    <h4 className="font-semibold text-blue-300">综合分析</h4>
                  </div>
                  <p className="text-slate-300 leading-relaxed">{config.analysis}</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default DecisionRenderer;
