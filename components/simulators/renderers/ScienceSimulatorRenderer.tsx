'use client';

/**
 * 理科模拟器渲染器 - 增强版
 * 精美的滑块控件和实时计算结果展示
 */

import React, { useState, useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Calculator, Sliders, Info, Zap, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { SimulatorConfig, SimulatorInputConfig, SimulatorOutputConfig } from '@/types/editor';

interface ScienceSimulatorRendererProps {
  config: SimulatorConfig;
  readOnly?: boolean;
  compact?: boolean;
}

export function ScienceSimulatorRenderer({ config, readOnly = false, compact = false }: ScienceSimulatorRendererProps) {
  // 输入值状态
  const [inputValues, setInputValues] = useState<Record<string, number>>(() => {
    const initial: Record<string, number> = {};
    config.inputs.forEach(input => {
      initial[input.name] = input.defaultValue;
    });
    return initial;
  });

  // 上一次的输出值（用于显示趋势）
  const [prevOutputs, setPrevOutputs] = useState<Record<string, number>>({});

  // 计算输出值
  const outputValues = useMemo(() => {
    const results: Record<string, number | string> = {};

    config.outputs.forEach(output => {
      if (output.formula) {
        try {
          const input = inputValues;
          // eslint-disable-next-line no-new-func
          const calculate = new Function('input', `return ${output.formula}`);
          const value = calculate(input);
          results[output.name] = typeof value === 'number' ? Math.round(value * 100) / 100 : value;
        } catch {
          results[output.name] = 'Error';
        }
      }
    });

    return results;
  }, [inputValues, config.outputs]);

  // 更新输入值
  const handleInputChange = useCallback((name: string, value: number) => {
    setPrevOutputs({ ...outputValues } as Record<string, number>);
    setInputValues(prev => ({ ...prev, [name]: value }));
  }, [outputValues]);

  // 获取趋势
  const getTrend = (name: string, currentValue: number | string) => {
    if (typeof currentValue !== 'number') return 'stable';
    const prev = prevOutputs[name];
    if (prev === undefined) return 'stable';
    if (currentValue > prev) return 'up';
    if (currentValue < prev) return 'down';
    return 'stable';
  };

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
        {/* 网格背景 */}
        <div
          className="absolute inset-0 opacity-5"
          style={{
            backgroundImage: `linear-gradient(to right, white 1px, transparent 1px), linear-gradient(to bottom, white 1px, transparent 1px)`,
            backgroundSize: '40px 40px',
          }}
        />
      </div>

      <div className={cn('relative z-10', compact ? 'p-4' : 'p-6')}>
        {/* 标题 */}
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-xl">
            <Calculator className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-white">{config.name}</h3>
            {config.description && (
              <p className="text-sm text-slate-400 mt-0.5">{config.description}</p>
            )}
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* 输入控件区 */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-400 mb-2">
              <Sliders className="w-4 h-4" />
              参数调节
            </div>

            {config.inputs.map((input, index) => (
              <motion.div
                key={input.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <InputControl
                  config={input}
                  value={inputValues[input.name]}
                  onChange={(value) => handleInputChange(input.name, value)}
                  disabled={readOnly}
                />
              </motion.div>
            ))}
          </div>

          {/* 输出显示区 */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-400 mb-2">
              <Zap className="w-4 h-4" />
              计算结果
            </div>

            <div className="space-y-3">
              {config.outputs.map((output, index) => {
                const value = outputValues[output.name];
                const trend = getTrend(output.name, value);

                return (
                  <motion.div
                    key={output.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <OutputDisplay
                      config={output}
                      value={value}
                      trend={trend}
                    />
                  </motion.div>
                );
              })}
            </div>
          </div>
        </div>

        {/* 操作说明 */}
        {config.instructions && config.instructions.length > 0 && !compact && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mt-6"
          >
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
              <div className="flex items-center gap-2 text-sm font-medium text-slate-400 mb-3">
                <Info className="w-4 h-4" />
                操作说明
              </div>
              <ul className="space-y-2">
                {config.instructions.map((instruction, index) => (
                  <li key={index} className="flex items-start gap-3 text-sm text-slate-300">
                    <span className="flex-shrink-0 w-5 h-5 rounded-full bg-slate-700 flex items-center justify-center text-xs text-slate-400">
                      {index + 1}
                    </span>
                    {instruction}
                  </li>
                ))}
              </ul>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}

/** 输入控件 */
interface InputControlProps {
  config: SimulatorInputConfig;
  value: number;
  onChange: (value: number) => void;
  disabled?: boolean;
}

function InputControl({ config, value, onChange, disabled }: InputControlProps) {
  const percentage = config.min !== undefined && config.max !== undefined
    ? ((value - config.min) / (config.max - config.min)) * 100
    : 50;

  if (config.type === 'select' && config.options) {
    return (
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
        <div className="flex justify-between items-center mb-2">
          <label className="text-sm font-medium text-slate-300">{config.label}</label>
        </div>
        <select
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          disabled={disabled}
          className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {config.options.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </div>
    );
  }

  if (config.type === 'slider') {
    return (
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
        <div className="flex justify-between items-center mb-3">
          <label className="text-sm font-medium text-slate-300">{config.label}</label>
          <div className="flex items-baseline gap-1">
            <motion.span
              key={value}
              initial={{ scale: 1.2, color: '#60a5fa' }}
              animate={{ scale: 1, color: '#ffffff' }}
              className="text-2xl font-bold"
            >
              {value}
            </motion.span>
            {config.unit && (
              <span className="text-sm text-slate-400">{config.unit}</span>
            )}
          </div>
        </div>

        {/* 自定义滑块 */}
        <div className="relative h-3 bg-slate-700 rounded-full overflow-hidden">
          <motion.div
            className="absolute inset-y-0 left-0 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full"
            initial={false}
            animate={{ width: `${percentage}%` }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          />
          <input
            type="range"
            min={config.min}
            max={config.max}
            step={config.step}
            value={value}
            onChange={(e) => onChange(Number(e.target.value))}
            disabled={disabled}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          {/* 滑块手柄 */}
          <motion.div
            className="absolute top-1/2 -translate-y-1/2 w-5 h-5 bg-white rounded-full shadow-lg shadow-blue-500/50 pointer-events-none"
            initial={false}
            animate={{ left: `calc(${percentage}% - 10px)` }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          />
        </div>

        {/* 范围标签 */}
        <div className="flex justify-between mt-2 text-xs text-slate-500">
          <span>{config.min}{config.unit}</span>
          <span>{config.max}{config.unit}</span>
        </div>

        {config.hint && (
          <p className="text-xs text-slate-500 mt-2">{config.hint}</p>
        )}
      </div>
    );
  }

  // number 类型
  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
      <div className="flex justify-between items-center mb-2">
        <label className="text-sm font-medium text-slate-300">{config.label}</label>
      </div>
      <div className="flex items-center gap-2">
        <input
          type="number"
          min={config.min}
          max={config.max}
          step={config.step}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          disabled={disabled}
          className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {config.unit && (
          <span className="text-sm text-slate-400">{config.unit}</span>
        )}
      </div>
      {config.hint && (
        <p className="text-xs text-slate-500 mt-2">{config.hint}</p>
      )}
    </div>
  );
}

/** 输出显示 */
interface OutputDisplayProps {
  config: SimulatorOutputConfig;
  value: string | number | undefined;
  trend: 'up' | 'down' | 'stable';
}

function OutputDisplay({ config, value, trend }: OutputDisplayProps) {
  const numValue = typeof value === 'number' ? value : 0;

  if (config.type === 'progress') {
    return (
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm text-slate-300">{config.label}</span>
          <span className="text-sm font-medium text-white">{numValue}%</span>
        </div>
        <div className="h-3 bg-slate-700 rounded-full overflow-hidden">
          <motion.div
            className="h-full rounded-full"
            initial={false}
            animate={{ width: `${Math.min(100, Math.max(0, numValue))}%` }}
            transition={{ type: 'spring', stiffness: 100, damping: 20 }}
            style={{
              background: config.color
                ? `linear-gradient(to right, ${config.color}, ${config.color}dd)`
                : 'linear-gradient(to right, #3b82f6, #06b6d4)',
            }}
          />
        </div>
      </div>
    );
  }

  // number 类型 - 大数字显示
  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
      <div className="flex justify-between items-start">
        <span className="text-sm text-slate-400">{config.label}</span>
        {trend !== 'stable' && (
          <div className={cn(
            'flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium',
            trend === 'up' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
          )}>
            {trend === 'up' ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            {trend === 'up' ? '上升' : '下降'}
          </div>
        )}
      </div>
      <div className="flex items-baseline gap-2 mt-2">
        <motion.span
          key={value}
          initial={{ scale: 1.1, color: trend === 'up' ? '#34d399' : trend === 'down' ? '#f87171' : '#ffffff' }}
          animate={{ scale: 1, color: '#ffffff' }}
          transition={{ duration: 0.3 }}
          className="text-3xl font-bold text-white"
        >
          {value}
        </motion.span>
        {config.unit && (
          <span className="text-sm text-slate-400">{config.unit}</span>
        )}
      </div>
    </div>
  );
}

export default ScienceSimulatorRenderer;
