/**
 * 自定义代码渲染器 - 执行AI生成的PixiJS代码
 * 画布尺寸固定 800x500
 */

'use client';

import React, { useEffect, useRef, useCallback, useState, Component, ErrorInfo, ReactNode } from 'react';
import * as PIXI from 'pixi.js';

// ==================== ErrorBoundary ====================

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class CustomRendererErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('CustomRenderer Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div style={{
          width: 800,
          height: 500,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#1e293b',
          borderRadius: '8px',
          color: '#fecaca',
          flexDirection: 'column',
          gap: '8px',
        }}>
          <p style={{ fontSize: '16px', fontWeight: 'bold' }}>模拟器加载出错</p>
          <p style={{ fontSize: '12px', color: '#94a3b8' }}>{this.state.error?.message}</p>
        </div>
      );
    }
    return this.props.children;
  }
}

// ==================== 类型定义 ====================

interface CustomRendererProps {
  /** AI生成的代码字符串 */
  code: string;
  /** 变量值（与滑块绑定） */
  variables?: Record<string, number>;
  /** 变量变化回调 */
  onVariableChange?: (name: string, value: number) => void;
  /** 准备就绪回调 */
  onReady?: () => void;
  /** 错误回调 */
  onError?: (error: Error) => void;
  /** 样式类名 */
  className?: string;
}

/** 模拟器上下文 - 提供给AI代码的安全API */
interface SimulatorContext {
  // 画布信息
  width: number;
  height: number;
  time: number;
  deltaTime: number;

  // 绘图API
  createCircle: (x: number, y: number, radius: number, color: string) => string;
  createRect: (x: number, y: number, w: number, h: number, color: string, cornerRadius?: number) => string;
  createLine: (points: Array<{x: number, y: number}>, color: string, lineWidth?: number) => string;
  createText: (text: string, x: number, y: number, style?: TextStyle) => string;
  createCurve: (points: Array<{x: number, y: number}>, color: string, lineWidth?: number, smooth?: boolean) => string;
  createPolygon: (points: Array<{x: number, y: number}>, fillColor: string, strokeColor?: string) => string;

  // 元素操作
  setPosition: (id: string, x: number, y: number) => void;
  setScale: (id: string, sx: number, sy: number) => void;
  setRotation: (id: string, angle: number) => void;
  setAlpha: (id: string, alpha: number) => void;
  setColor: (id: string, color: string) => void;
  setText: (id: string, text: string) => void;
  setVisible: (id: string, visible: boolean) => void;
  remove: (id: string) => void;
  clear: () => void;

  // 变量操作
  getVar: (name: string) => number;
  setVar: (name: string, value: number) => void;

  // 数学工具
  math: MathUtils;
}

interface TextStyle {
  fontSize?: number;
  fontFamily?: string;
  color?: string;
  fontWeight?: string;
  align?: 'left' | 'center' | 'right';
}

interface MathUtils {
  sin: (x: number) => number;
  cos: (x: number) => number;
  tan: (x: number) => number;
  abs: (x: number) => number;
  floor: (x: number) => number;
  ceil: (x: number) => number;
  round: (x: number) => number;
  sqrt: (x: number) => number;
  pow: (x: number, y: number) => number;
  min: (...values: number[]) => number;
  max: (...values: number[]) => number;
  random: () => number;
  PI: number;
  lerp: (a: number, b: number, t: number) => number;
  clamp: (value: number, min: number, max: number) => number;
  smoothstep: (edge0: number, edge1: number, x: number) => number;
  wave: (t: number, frequency?: number, amplitude?: number) => number;
  degToRad: (deg: number) => number;
  radToDeg: (rad: number) => number;
}

/** 编译后的模拟器 */
interface CompiledSimulator {
  setup: (ctx: SimulatorContext) => void;
  update: (ctx: SimulatorContext) => void;
  cleanup?: () => void;
}

// ==================== 常量 ====================

const CANVAS_WIDTH = 800;
const CANVAS_HEIGHT = 500;

// ==================== 组件 ====================

function CustomRendererInner({
  code,
  variables = {},
  onVariableChange,
  onReady,
  onError,
  className,
}: CustomRendererProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const appRef = useRef<PIXI.Application | null>(null);
  const elementsRef = useRef<Map<string, PIXI.Container>>(new Map());
  const simulatorRef = useRef<CompiledSimulator | null>(null);
  const variablesRef = useRef<Record<string, number>>(variables);
  const timeRef = useRef<number>(0);
  const animationFrameRef = useRef<number | null>(null);
  const lastTimeRef = useRef<number>(0);
  const elementIdCounter = useRef<number>(0);

  const [error, setError] = useState<Error | null>(null);

  // 更新变量引用
  useEffect(() => {
    variablesRef.current = { ...variablesRef.current, ...variables };
  }, [variables]);

  // 生成唯一ID
  const generateId = useCallback(() => {
    return `elem_${++elementIdCounter.current}`;
  }, []);

  // 解析颜色
  const parseColor = useCallback((color: string): number => {
    if (color.startsWith('#')) {
      return parseInt(color.slice(1), 16);
    }
    if (color.startsWith('rgb')) {
      const match = color.match(/\d+/g);
      if (match && match.length >= 3) {
        return (parseInt(match[0]) << 16) + (parseInt(match[1]) << 8) + parseInt(match[2]);
      }
    }
    return 0xffffff;
  }, []);

  // 创建模拟器上下文
  const createContext = useCallback((deltaTime: number): SimulatorContext => {
    const app = appRef.current;
    if (!app) throw new Error('App not initialized');

    return {
      width: CANVAS_WIDTH,
      height: CANVAS_HEIGHT,
      time: timeRef.current,
      deltaTime,

      // 创建圆形
      createCircle: (x, y, radius, color) => {
        const id = generateId();
        const graphics = new PIXI.Graphics();
        graphics.circle(0, 0, radius);
        graphics.fill({ color: parseColor(color) });
        graphics.position.set(x, y);
        app.stage.addChild(graphics);
        elementsRef.current.set(id, graphics);
        return id;
      },

      // 创建矩形
      createRect: (x, y, w, h, color, cornerRadius = 0) => {
        const id = generateId();
        const graphics = new PIXI.Graphics();
        if (cornerRadius > 0) {
          graphics.roundRect(-w/2, -h/2, w, h, cornerRadius);
        } else {
          graphics.rect(-w/2, -h/2, w, h);
        }
        graphics.fill({ color: parseColor(color) });
        graphics.position.set(x, y);
        app.stage.addChild(graphics);
        elementsRef.current.set(id, graphics);
        return id;
      },

      // 创建线条
      createLine: (points, color, lineWidth = 2) => {
        const id = generateId();
        const graphics = new PIXI.Graphics();
        if (points.length > 1) {
          graphics.moveTo(points[0].x, points[0].y);
          for (let i = 1; i < points.length; i++) {
            graphics.lineTo(points[i].x, points[i].y);
          }
          graphics.stroke({ color: parseColor(color), width: lineWidth });
        }
        app.stage.addChild(graphics);
        elementsRef.current.set(id, graphics);
        return id;
      },

      // 创建文本
      createText: (text, x, y, style = {}) => {
        const id = generateId();
        const pixiText = new PIXI.Text({
          text,
          style: {
            fontFamily: style.fontFamily || 'Arial',
            fontSize: style.fontSize || 16,
            fill: style.color || '#ffffff',
            fontWeight: (style.fontWeight || 'normal') as PIXI.TextStyleFontWeight,
            align: style.align || 'left',
          },
        });
        pixiText.anchor.set(0.5, 0.5);
        pixiText.position.set(x, y);
        app.stage.addChild(pixiText);
        elementsRef.current.set(id, pixiText);
        return id;
      },

      // 创建曲线
      createCurve: (points, color, lineWidth = 2, smooth = true) => {
        const id = generateId();
        const graphics = new PIXI.Graphics();
        if (points.length > 1) {
          graphics.moveTo(points[0].x, points[0].y);
          if (smooth && points.length > 2) {
            for (let i = 1; i < points.length; i++) {
              const prev = points[i - 1];
              const curr = points[i];
              const xc = (prev.x + curr.x) / 2;
              const yc = (prev.y + curr.y) / 2;
              graphics.quadraticCurveTo(prev.x, prev.y, xc, yc);
            }
            const last = points[points.length - 1];
            graphics.lineTo(last.x, last.y);
          } else {
            for (let i = 1; i < points.length; i++) {
              graphics.lineTo(points[i].x, points[i].y);
            }
          }
          graphics.stroke({ color: parseColor(color), width: lineWidth });
        }
        app.stage.addChild(graphics);
        elementsRef.current.set(id, graphics);
        return id;
      },

      // 创建多边形
      createPolygon: (points, fillColor, strokeColor) => {
        const id = generateId();
        const graphics = new PIXI.Graphics();
        if (points.length > 2) {
          graphics.poly(points.flatMap(p => [p.x, p.y]));
          graphics.fill({ color: parseColor(fillColor) });
          if (strokeColor) {
            graphics.stroke({ color: parseColor(strokeColor), width: 2 });
          }
        }
        app.stage.addChild(graphics);
        elementsRef.current.set(id, graphics);
        return id;
      },

      // 设置位置
      setPosition: (id, x, y) => {
        const elem = elementsRef.current.get(id);
        if (elem) elem.position.set(x, y);
      },

      // 设置缩放
      setScale: (id, sx, sy) => {
        const elem = elementsRef.current.get(id);
        if (elem) elem.scale.set(sx, sy);
      },

      // 设置旋转
      setRotation: (id, angle) => {
        const elem = elementsRef.current.get(id);
        if (elem) elem.rotation = angle * Math.PI / 180;
      },

      // 设置透明度
      setAlpha: (id, alpha) => {
        const elem = elementsRef.current.get(id);
        if (elem) elem.alpha = Math.max(0, Math.min(1, alpha));
      },

      // 设置颜色（仅Graphics）
      setColor: (id, color) => {
        const elem = elementsRef.current.get(id);
        if (elem && elem instanceof PIXI.Graphics) {
          elem.tint = parseColor(color);
        }
      },

      // 设置文本
      setText: (id, text) => {
        const elem = elementsRef.current.get(id);
        if (elem && elem instanceof PIXI.Text) {
          elem.text = text;
        }
      },

      // 设置可见性
      setVisible: (id, visible) => {
        const elem = elementsRef.current.get(id);
        if (elem) elem.visible = visible;
      },

      // 移除元素
      remove: (id) => {
        const elem = elementsRef.current.get(id);
        if (elem) {
          elem.destroy();
          elementsRef.current.delete(id);
        }
      },

      // 清除所有元素
      clear: () => {
        elementsRef.current.forEach(elem => elem.destroy());
        elementsRef.current.clear();
        elementIdCounter.current = 0;
      },

      // 获取变量
      getVar: (name) => {
        return variablesRef.current[name] ?? 0;
      },

      // 设置变量
      setVar: (name, value) => {
        variablesRef.current[name] = value;
        onVariableChange?.(name, value);
      },

      // 数学工具
      math: {
        sin: Math.sin,
        cos: Math.cos,
        tan: Math.tan,
        abs: Math.abs,
        floor: Math.floor,
        ceil: Math.ceil,
        round: Math.round,
        sqrt: Math.sqrt,
        pow: Math.pow,
        min: Math.min,
        max: Math.max,
        random: Math.random,
        PI: Math.PI,
        lerp: (a, b, t) => a + (b - a) * t,
        clamp: (value, min, max) => Math.max(min, Math.min(max, value)),
        smoothstep: (edge0, edge1, x) => {
          const t = Math.max(0, Math.min(1, (x - edge0) / (edge1 - edge0)));
          return t * t * (3 - 2 * t);
        },
        wave: (t, frequency = 1, amplitude = 1) => Math.sin(t * frequency * Math.PI * 2) * amplitude,
        degToRad: (deg) => deg * Math.PI / 180,
        radToDeg: (rad) => rad * 180 / Math.PI,
      },
    };
  }, [generateId, parseColor, onVariableChange]);

  // 编译代码
  const compileCode = useCallback((codeStr: string): CompiledSimulator | null => {
    try {
      // 包装代码，提供安全的执行环境
      const wrappedCode = `
        "use strict";
        return (function() {
          ${codeStr}
          return { setup, update, cleanup: typeof cleanup !== 'undefined' ? cleanup : undefined };
        })();
      `;

      // 使用 Function 构造器执行代码
      const factory = new Function(wrappedCode);
      const simulator = factory();

      if (typeof simulator.setup !== 'function') {
        throw new Error('代码必须定义 setup(ctx) 函数');
      }
      if (typeof simulator.update !== 'function') {
        throw new Error('代码必须定义 update(ctx) 函数');
      }

      return simulator;
    } catch (err) {
      console.error('代码编译失败:', err);
      setError(err as Error);
      onError?.(err as Error);
      return null;
    }
  }, [onError]);

  // 动画循环
  const animate = useCallback((currentTime: number) => {
    if (lastTimeRef.current === 0) {
      lastTimeRef.current = currentTime;
    }

    const deltaTime = (currentTime - lastTimeRef.current) / 1000; // 转换为秒
    lastTimeRef.current = currentTime;
    timeRef.current += deltaTime;

    if (simulatorRef.current && appRef.current) {
      try {
        const ctx = createContext(deltaTime);
        simulatorRef.current.update(ctx);
      } catch (err) {
        console.error('更新循环错误:', err);
      }
    }

    animationFrameRef.current = requestAnimationFrame(animate);
  }, [createContext]);

  // 初始化
  useEffect(() => {
    let isMounted = true;

    const initialize = async () => {
      if (!containerRef.current) return;

      try {
        // 创建 PixiJS 应用
        const app = new PIXI.Application();
        await app.init({
          width: CANVAS_WIDTH,
          height: CANVAS_HEIGHT,
          backgroundColor: '#1e293b',
          antialias: true,
          resolution: window.devicePixelRatio || 1,
          autoDensity: true,
        });

        if (!isMounted) return;

        containerRef.current.appendChild(app.canvas as HTMLCanvasElement);
        appRef.current = app;

        // 编译代码
        const simulator = compileCode(code);
        if (!simulator) return;

        simulatorRef.current = simulator;

        // 执行 setup
        const ctx = createContext(0);
        simulator.setup(ctx);

        // 启动动画循环
        lastTimeRef.current = 0;
        timeRef.current = 0;
        animationFrameRef.current = requestAnimationFrame(animate);

        setError(null);
        onReady?.();
      } catch (err) {
        console.error('初始化失败:', err);
        setError(err as Error);
        onError?.(err as Error);
      }
    };

    initialize();

    return () => {
      isMounted = false;

      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }

      if (simulatorRef.current?.cleanup) {
        try {
          simulatorRef.current.cleanup();
        } catch (e) {
          console.warn('Cleanup error:', e);
        }
      }
      simulatorRef.current = null;

      // 清空元素引用（不销毁，让 app.destroy 处理）
      elementsRef.current.clear();

      if (appRef.current) {
        const appToDestroy = appRef.current;
        appRef.current = null; // 先清空引用，防止重复销毁

        // 使用 setTimeout 延迟销毁，避免纹理竞态条件
        setTimeout(() => {
          try {
            // 先停止渲染
            if (appToDestroy.ticker) {
              appToDestroy.ticker.stop();
            }
            // 移除所有子元素
            if (appToDestroy.stage) {
              appToDestroy.stage.removeChildren();
            }
            // 使用最安全的销毁选项 - 不销毁纹理
            appToDestroy.destroy(false, {
              children: false,
              texture: false,
              textureSource: false,
              context: false
            });
          } catch (e) {
            // 忽略销毁时的错误，组件已卸载
            console.warn('PixiJS cleanup warning (deferred):', e);
          }
        }, 0);
      }
    };
  }, [code, compileCode, createContext, animate, onReady, onError]);

  return (
    <div className={className}>
      <div
        ref={containerRef}
        style={{
          width: CANVAS_WIDTH,
          height: CANVAS_HEIGHT,
          borderRadius: '8px',
          overflow: 'hidden',
        }}
      />
      {error && (
        <div style={{
          marginTop: '8px',
          padding: '12px',
          backgroundColor: '#7f1d1d',
          borderRadius: '8px',
          color: '#fecaca',
          fontSize: '14px',
        }}>
          <strong>错误：</strong> {error.message}
        </div>
      )}
    </div>
  );
}

// 包装组件，添加错误边界
function CustomRendererWithErrorBoundary(props: CustomRendererProps) {
  return (
    <CustomRendererErrorBoundary>
      <CustomRendererInner {...props} />
    </CustomRendererErrorBoundary>
  );
}

export { CustomRendererWithErrorBoundary as CustomRenderer };
export default CustomRendererWithErrorBoundary;
