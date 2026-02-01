/**
 * 混合模拟器渲染器
 * 根据模式选择使用SDL渲染器或自定义代码渲染器
 */

'use client';

import { useState, useCallback } from 'react';
import { PixiRenderer } from './renderers/PixiRenderer';
import { CustomRenderer } from './CustomRenderer';
import type { SceneDefinition } from '@/types/simulator-engine';

// ==================== 类型定义 ====================

/** 模拟器模式 */
export type SimulatorMode = 'sdl' | 'custom';

/** SDL模式数据 */
interface SDLModeData {
  mode: 'sdl';
  scene: SceneDefinition;
}

/** 自定义代码模式数据 */
interface CustomModeData {
  mode: 'custom';
  code: string;
  variables?: VariableConfig[];
}

/** 变量配置 */
export interface VariableConfig {
  name: string;
  label: string;
  min: number;
  max: number;
  default: number;
  step?: number;
  unit?: string;
}

/** 模拟器数据 */
export type SimulatorData = SDLModeData | CustomModeData;

/** 组件属性 */
interface HybridRendererProps {
  data: SimulatorData;
  onReady?: () => void;
  onError?: (error: Error) => void;
  className?: string;
  showControls?: boolean;
}

// ==================== 组件 ====================

export function HybridRenderer({
  data,
  onReady,
  onError,
  className,
  showControls = true,
}: HybridRendererProps) {
  // 变量状态（用于自定义代码模式）
  const [variables, setVariables] = useState<Record<string, number>>(() => {
    if (data.mode === 'custom' && data.variables) {
      const initial: Record<string, number> = {};
      data.variables.forEach(v => {
        initial[v.name] = v.default;
      });
      return initial;
    }
    return {};
  });

  // 变量变化处理
  const handleVariableChange = useCallback((name: string, value: number) => {
    setVariables(prev => ({ ...prev, [name]: value }));
  }, []);

  // 滑块变化处理
  const handleSliderChange = useCallback((name: string, value: number) => {
    setVariables(prev => ({ ...prev, [name]: value }));
  }, []);

  return (
    <div className={className}>
      {/* 渲染器 */}
      {data.mode === 'sdl' ? (
        <PixiRenderer
          scene={data.scene}
          onReady={onReady}
          onError={onError}
        />
      ) : (
        <CustomRenderer
          code={data.code}
          variables={variables}
          onVariableChange={handleVariableChange}
          onReady={onReady}
          onError={onError}
        />
      )}

      {/* 控制面板（仅自定义代码模式） */}
      {showControls && data.mode === 'custom' && data.variables && data.variables.length > 0 && (
        <div style={{
          marginTop: '16px',
          padding: '16px',
          backgroundColor: '#1e293b',
          borderRadius: '8px',
        }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '16px',
          }}>
            {data.variables.map(variable => (
              <div key={variable.name}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  marginBottom: '4px',
                  fontSize: '14px',
                  color: '#94a3b8',
                }}>
                  <span>{variable.label}</span>
                  <span>
                    {variables[variable.name]?.toFixed(1) ?? variable.default}
                    {variable.unit && ` ${variable.unit}`}
                  </span>
                </div>
                <input
                  type="range"
                  min={variable.min}
                  max={variable.max}
                  step={variable.step ?? 0.1}
                  value={variables[variable.name] ?? variable.default}
                  onChange={(e) => handleSliderChange(variable.name, parseFloat(e.target.value))}
                  style={{
                    width: '100%',
                    height: '8px',
                    borderRadius: '4px',
                    appearance: 'none',
                    backgroundColor: '#374151',
                    cursor: 'pointer',
                  }}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default HybridRenderer;
