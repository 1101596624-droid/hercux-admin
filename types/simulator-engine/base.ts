/**
 * 场景描述语言 (SDL) - 基础类型定义
 */

// ==================== 基础类型 ====================

/** 2D 向量 */
export interface Vector2D {
  x: number;
  y: number;
}

/** 3D 向量 */
export interface Vector3D {
  x: number;
  y: number;
  z: number;
}

/** RGBA 颜色 */
export interface Color {
  r: number;  // 0-255
  g: number;
  b: number;
  a: number;  // 0-1
}

/** 颜色字符串 (hex 或 rgba) */
export type ColorString = string;

/** 颜色值 (对象或字符串) */
export type ColorValue = Color | ColorString;

/** 数值范围 */
export interface NumberRange {
  min: number;
  max: number;
}

/** 颜色范围 */
export interface ColorRange {
  start: Color;
  end: Color;
}

// ==================== 变换类型 ====================

/** 2D 变换属性 */
export interface Transform2D {
  position: Vector2D;
  rotation: number;      // 角度 (度)
  scale: Vector2D;
  anchor: Vector2D;      // 锚点 0-1
}

/** 3D 变换属性 */
export interface Transform3D extends Transform2D {
  position3D: Vector3D;
  rotation3D: Vector3D;  // 欧拉角 (度)
  perspective?: number;  // 透视距离
}

/** 默认 2D 变换 */
export const DEFAULT_TRANSFORM_2D: Transform2D = {
  position: { x: 0, y: 0 },
  rotation: 0,
  scale: { x: 1, y: 1 },
  anchor: { x: 0.5, y: 0.5 },
};

// ==================== 样式类型 ====================

/** 填充样式 */
export interface FillStyle {
  type: 'solid' | 'gradient' | 'pattern';
  color?: ColorValue;
  gradient?: GradientStyle;
  pattern?: PatternStyle;
}

/** 渐变样式 */
export interface GradientStyle {
  type: 'linear' | 'radial';
  stops: GradientStop[];
  angle?: number;        // 线性渐变角度
  center?: Vector2D;     // 径向渐变中心
  radius?: number;       // 径向渐变半径
}

/** 渐变停止点 */
export interface GradientStop {
  offset: number;        // 0-1
  color: ColorValue;
}

/** 图案样式 */
export interface PatternStyle {
  source: string;        // 图片 URL 或资源 ID
  repeat: 'repeat' | 'repeat-x' | 'repeat-y' | 'no-repeat';
  scale?: Vector2D;
}

/** 描边样式 */
export interface StrokeStyle {
  color: ColorValue;
  width: number;
  lineCap?: 'butt' | 'round' | 'square';
  lineJoin?: 'miter' | 'round' | 'bevel';
  dashArray?: number[];
  dashOffset?: number;
}

/** 标记样式 (箭头等) */
export interface MarkerStyle {
  type: 'arrow' | 'circle' | 'square' | 'diamond' | 'none';
  size: number;
  fill?: ColorValue;
}

/** 混合模式 */
export type BlendMode =
  | 'normal'
  | 'add'
  | 'multiply'
  | 'screen'
  | 'overlay'
  | 'darken'
  | 'lighten'
  | 'color-dodge'
  | 'color-burn';

// ==================== 缓动类型 ====================

/** 预设缓动类型 */
export type PresetEasing =
  | 'linear'
  | 'easeIn' | 'easeOut' | 'easeInOut'
  | 'easeInQuad' | 'easeOutQuad' | 'easeInOutQuad'
  | 'easeInCubic' | 'easeOutCubic' | 'easeInOutCubic'
  | 'easeInQuart' | 'easeOutQuart' | 'easeInOutQuart'
  | 'easeInQuint' | 'easeOutQuint' | 'easeInOutQuint'
  | 'easeInSine' | 'easeOutSine' | 'easeInOutSine'
  | 'easeInExpo' | 'easeOutExpo' | 'easeInOutExpo'
  | 'easeInCirc' | 'easeOutCirc' | 'easeInOutCirc'
  | 'easeInElastic' | 'easeOutElastic' | 'easeInOutElastic'
  | 'easeInBack' | 'easeOutBack' | 'easeInOutBack'
  | 'easeInBounce' | 'easeOutBounce' | 'easeInOutBounce';

/** 贝塞尔缓动 */
export interface BezierEasing {
  type: 'bezier';
  controlPoints: [number, number, number, number];
}

/** 弹簧缓动 */
export interface SpringEasing {
  type: 'spring';
  stiffness: number;
  damping: number;
  mass?: number;
}

/** 缓动类型 */
export type EasingType = PresetEasing | BezierEasing | SpringEasing;

// ==================== 工具函数 ====================

/** 将 Color 对象转换为 CSS 字符串 */
export function colorToString(color: ColorValue): string {
  if (typeof color === 'string') return color;
  return `rgba(${color.r}, ${color.g}, ${color.b}, ${color.a})`;
}

/** 将 CSS 字符串转换为 Color 对象 */
export function stringToColor(str: string): Color {
  // 处理 hex
  if (str.startsWith('#')) {
    const hex = str.slice(1);
    if (hex.length === 3) {
      return {
        r: parseInt(hex[0] + hex[0], 16),
        g: parseInt(hex[1] + hex[1], 16),
        b: parseInt(hex[2] + hex[2], 16),
        a: 1,
      };
    }
    if (hex.length === 6) {
      return {
        r: parseInt(hex.slice(0, 2), 16),
        g: parseInt(hex.slice(2, 4), 16),
        b: parseInt(hex.slice(4, 6), 16),
        a: 1,
      };
    }
    if (hex.length === 8) {
      return {
        r: parseInt(hex.slice(0, 2), 16),
        g: parseInt(hex.slice(2, 4), 16),
        b: parseInt(hex.slice(4, 6), 16),
        a: parseInt(hex.slice(6, 8), 16) / 255,
      };
    }
  }
  // 处理 rgba
  const rgbaMatch = str.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
  if (rgbaMatch) {
    return {
      r: parseInt(rgbaMatch[1]),
      g: parseInt(rgbaMatch[2]),
      b: parseInt(rgbaMatch[3]),
      a: rgbaMatch[4] ? parseFloat(rgbaMatch[4]) : 1,
    };
  }
  // 默认黑色
  return { r: 0, g: 0, b: 0, a: 1 };
}

/** 将 Color 转换为 PixiJS 数值格式 */
export function colorToPixi(color: ColorValue): number {
  const c = typeof color === 'string' ? stringToColor(color) : color;
  return (c.r << 16) + (c.g << 8) + c.b;
}

/** 插值两个颜色 */
export function lerpColor(a: Color, b: Color, t: number): Color {
  return {
    r: Math.round(a.r + (b.r - a.r) * t),
    g: Math.round(a.g + (b.g - a.g) * t),
    b: Math.round(a.b + (b.b - a.b) * t),
    a: a.a + (b.a - a.a) * t,
  };
}

/** 插值两个向量 */
export function lerpVector2D(a: Vector2D, b: Vector2D, t: number): Vector2D {
  return {
    x: a.x + (b.x - a.x) * t,
    y: a.y + (b.y - a.y) * t,
  };
}

/** 计算两点距离 */
export function distance(a: Vector2D, b: Vector2D): number {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  return Math.sqrt(dx * dx + dy * dy);
}

/** 计算两点角度 (度) */
export function angle(from: Vector2D, to: Vector2D): number {
  return Math.atan2(to.y - from.y, to.x - from.x) * (180 / Math.PI);
}

/** 角度转弧度 */
export function degToRad(deg: number): number {
  return deg * (Math.PI / 180);
}

/** 弧度转角度 */
export function radToDeg(rad: number): number {
  return rad * (180 / Math.PI);
}
