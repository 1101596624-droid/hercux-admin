'use client';

/**
 * 时间线渲染器 - 增强版
 * 精美的时间线可视化，支持动画和交互
 */

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, Calendar, Star, Circle } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { TimelineConfig } from '@/types/editor';

interface TimelineRendererProps {
  config: TimelineConfig;
}

export function TimelineRenderer({ config }: TimelineRendererProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [direction, setDirection] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);
  const events = config.events;

  if (!events || events.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gradient-to-br from-slate-50 to-slate-100 rounded-2xl">
        <p className="text-slate-400">暂无时间线数据</p>
      </div>
    );
  }

  const currentEvent = events[currentIndex];

  const goTo = (index: number) => {
    setDirection(index > currentIndex ? 1 : -1);
    setCurrentIndex(index);
  };

  const goPrev = () => {
    if (currentIndex > 0) goTo(currentIndex - 1);
  };

  const goNext = () => {
    if (currentIndex < events.length - 1) goTo(currentIndex + 1);
  };

  // 自动滚动到当前选中的时间点
  useEffect(() => {
    if (scrollRef.current) {
      const activeBtn = scrollRef.current.querySelector(`[data-index="${currentIndex}"]`);
      if (activeBtn) {
        activeBtn.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      }
    }
  }, [currentIndex]);

  // 获取分类颜���
  const getCategoryColor = (category?: string) => {
    const colors: Record<string, string> = {
      '政治': 'from-red-500 to-rose-600',
      '经济': 'from-emerald-500 to-green-600',
      '文化': 'from-purple-500 to-violet-600',
      '科技': 'from-blue-500 to-cyan-600',
      '军事': 'from-orange-500 to-amber-600',
      '社会': 'from-pink-500 to-fuchsia-600',
    };
    return colors[category || ''] || 'from-indigo-500 to-blue-600';
  };

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10">
        {/* 标题 */}
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl">
            <Calendar className="w-5 h-5 text-white" />
          </div>
          <h3 className="text-xl font-bold text-white">{config.title}</h3>
        </div>

        {/* 时间轴 */}
        <div className="relative mb-6">
          {/* 时间线背景 */}
          <div className="absolute top-1/2 left-0 right-0 h-1 bg-slate-700 rounded-full -translate-y-1/2" />
          <div
            className="absolute top-1/2 left-0 h-1 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full -translate-y-1/2 transition-all duration-500"
            style={{ width: `${(currentIndex / (events.length - 1)) * 100}%` }}
          />

          {/* 时间点 */}
          <div
            ref={scrollRef}
            className="flex items-center gap-4 overflow-x-auto py-4 px-2 scrollbar-hide"
            style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
          >
            {events.map((event, index) => (
              <motion.button
                key={event.id}
                data-index={index}
                onClick={() => goTo(index)}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                className={cn(
                  'relative flex-shrink-0 flex flex-col items-center gap-2 transition-all duration-300',
                  index === currentIndex ? 'z-10' : 'z-0'
                )}
              >
                {/* 时间点圆圈 */}
                <div className={cn(
                  'relative w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300',
                  index === currentIndex
                    ? 'bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg shadow-blue-500/50'
                    : index < currentIndex
                    ? 'bg-slate-600'
                    : 'bg-slate-700 border-2 border-slate-600'
                )}>
                  {event.highlight && (
                    <Star className={cn(
                      'w-5 h-5',
                      index === currentIndex ? 'text-yellow-300' : 'text-slate-400'
                    )} />
                  )}
                  {!event.highlight && (
                    <Circle className={cn(
                      'w-3 h-3',
                      index === currentIndex ? 'text-white fill-white' : 'text-slate-400'
                    )} />
                  )}

                  {/* 脉冲动画 */}
                  {index === currentIndex && (
                    <motion.div
                      className="absolute inset-0 rounded-full bg-blue-500"
                      initial={{ scale: 1, opacity: 0.5 }}
                      animate={{ scale: 1.5, opacity: 0 }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    />
                  )}
                </div>

                {/* 年份标签 */}
                <span className={cn(
                  'text-sm font-medium whitespace-nowrap transition-colors duration-300',
                  index === currentIndex ? 'text-white' : 'text-slate-400'
                )}>
                  {event.year}
                </span>
              </motion.button>
            ))}
          </div>
        </div>

        {/* 事件详情卡片 */}
        <AnimatePresence mode="wait">
          <motion.div
            key={currentIndex}
            initial={{ opacity: 0, x: direction * 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -direction * 50 }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
            className="relative"
          >
            <div className={cn(
              'relative overflow-hidden rounded-2xl p-6',
              'bg-gradient-to-br from-slate-800/80 to-slate-900/80',
              'border border-slate-700/50 backdrop-blur-sm'
            )}>
              {/* 分类色带 */}
              <div className={cn(
                'absolute top-0 left-0 right-0 h-1 bg-gradient-to-r',
                getCategoryColor(currentEvent.category)
              )} />

              {/* 头部信息 */}
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <span className={cn(
                      'text-3xl font-bold bg-gradient-to-r bg-clip-text text-transparent',
                      getCategoryColor(currentEvent.category)
                    )}>
                      {currentEvent.year}
                    </span>
                    {currentEvent.highlight && (
                      <span className="px-2 py-0.5 bg-yellow-500/20 text-yellow-400 text-xs font-medium rounded-full flex items-center gap-1">
                        <Star className="w-3 h-3" /> 重要
                      </span>
                    )}
                  </div>
                  {currentEvent.category && (
                    <span className={cn(
                      'inline-block px-3 py-1 text-xs font-medium rounded-full',
                      'bg-gradient-to-r text-white',
                      getCategoryColor(currentEvent.category)
                    )}>
                      {currentEvent.category}
                    </span>
                  )}
                </div>
                <div className="text-sm text-slate-400">
                  {currentIndex + 1} / {events.length}
                </div>
              </div>

              {/* 事件标题 */}
              <h4 className="text-xl font-bold text-white mb-3">
                {currentEvent.title}
              </h4>

              {/* 事件描述 */}
              <p className="text-slate-300 leading-relaxed">
                {currentEvent.description}
              </p>
            </div>
          </motion.div>
        </AnimatePresence>

        {/* 导航按钮 */}
        <div className="flex justify-between items-center mt-4">
          <motion.button
            onClick={goPrev}
            disabled={currentIndex === 0}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all',
              currentIndex === 0
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                : 'bg-slate-700 text-white hover:bg-slate-600'
            )}
          >
            <ChevronLeft className="w-4 h-4" />
            上一个
          </motion.button>

          {/* 进度指示器 */}
          <div className="flex gap-1.5">
            {events.map((_, index) => (
              <button
                key={index}
                onClick={() => goTo(index)}
                className={cn(
                  'w-2 h-2 rounded-full transition-all duration-300',
                  index === currentIndex
                    ? 'w-6 bg-blue-500'
                    : 'bg-slate-600 hover:bg-slate-500'
                )}
              />
            ))}
          </div>

          <motion.button
            onClick={goNext}
            disabled={currentIndex === events.length - 1}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all',
              currentIndex === events.length - 1
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white hover:shadow-lg hover:shadow-blue-500/25'
            )}
          >
            下一个
            <ChevronRight className="w-4 h-4" />
          </motion.button>
        </div>
      </div>
    </div>
  );
}

export default TimelineRenderer;
