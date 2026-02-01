/**
 * 场景描述语言 (SDL) - 动画类型定义
 */

import type { EasingType, Vector2D, Color } from './base';

// ==================== 可动画属性 ====================

/** 可动画属性路径 */
export type AnimatableProperty =
  // 变换属性
  | 'position'
  | 'position.x'
  | 'position.y'
  | 'rotation'
  | 'scale'
  | 'scale.x'
  | 'scale.y'
  | 'anchor'
  | 'anchor.x'
  | 'anchor.y'
  // 显示属性
  | 'opacity'
  | 'visible'
  | 'zIndex'
  // 精灵属性
  | 'sprite.tint'
  | 'sprite.frame'
  // 形状属性
  | 'shape.fill.color'
  | 'shape.stroke.color'
  | 'shape.stroke.width'
  | 'shape.width'
  | 'shape.height'
  | 'shape.radius'
  | 'shape.points'
  // 文本属性
  | 'text.content'
  | 'text.color'
  | 'text.fontSize'
  // 粒子属性
  | 'emitter.emissionRate'
  | 'emitter.startColor'
  | 'emitter.endColor'
  // 物理属性
  | 'physics.linearVelocity'
  | 'physics.angularVelocity'
  // 骨骼属性
  | 'skeleton.animation'
  // 自定义属性
  | `custom.${string}`;

/** 属性值类型映射 */
export interface PropertyValueMap {
  'position': Vector2D;
  'position.x': number;
  'position.y': number;
  'rotation': number;
  'scale': Vector2D;
  'scale.x': number;
  'scale.y': number;
  'opacity': number;
  'visible': boolean;
  'zIndex': number;
  'sprite.tint': Color;
  'shape.fill.color': Color;
  'shape.stroke.color': Color;
  'text.content': string;
  'text.color': Color;
  [key: string]: unknown;
}

// ==================== 关键帧 ====================

/** 关键帧 */
export interface Keyframe<T = unknown> {
  time: number;                // 毫秒
  value: T;
  easing?: EasingType;
}

/** 数值关键帧 */
export type NumberKeyframe = Keyframe<number>;

/** 向量关键帧 */
export type Vector2DKeyframe = Keyframe<Vector2D>;

/** 颜色关键帧 */
export type ColorKeyframe = Keyframe<Color>;

/** 布尔关键帧 */
export type BooleanKeyframe = Keyframe<boolean>;

/** 字符串关键帧 */
export type StringKeyframe = Keyframe<string>;

// ==================== 动画轨道 ====================

/** 动画轨道 */
export interface AnimationTrack<T = unknown> {
  id: string;
  targetId: string;            // 目标元素 ID
  property: AnimatableProperty;
  keyframes: Keyframe<T>[];
  enabled?: boolean;
}

/** 数值轨道 */
export type NumberTrack = AnimationTrack<number>;

/** 向量轨道 */
export type Vector2DTrack = AnimationTrack<Vector2D>;

/** 颜色轨道 */
export type ColorTrack = AnimationTrack<Color>;

// ==================== 动画时间线 ====================

/** 时间线标记 */
export interface TimelineMarker {
  id: string;
  name: string;
  time: number;                // 毫秒
}

/** 动画时间线 */
export interface AnimationTimeline {
  id: string;
  name: string;
  duration: number;            // 毫秒
  loop: boolean;
  loopCount?: number;          // 循环次数，undefined 为无限
  autoPlay: boolean;
  playbackRate?: number;       // 播放速率，默认 1
  tracks: AnimationTrack[];
  markers?: TimelineMarker[];
}

// ==================== 动画状态 ====================

/** 动画播放状态 */
export type AnimationPlayState = 'idle' | 'playing' | 'paused' | 'finished';

/** 动画播放方向 */
export type AnimationDirection = 'normal' | 'reverse' | 'alternate' | 'alternate-reverse';

/** 动画运行时状态 */
export interface AnimationRuntimeState {
  timelineId: string;
  currentTime: number;
  playState: AnimationPlayState;
  direction: AnimationDirection;
  loopCount: number;
  playbackRate: number;
}

// ==================== 动画事件 ====================

/** 动画事件类型 */
export type AnimationEventType =
  | 'start'
  | 'end'
  | 'loop'
  | 'pause'
  | 'resume'
  | 'seek'
  | 'marker';

/** 动画事件 */
export interface AnimationEvent {
  type: AnimationEventType;
  timelineId: string;
  currentTime: number;
  marker?: TimelineMarker;
}

/** 动画事件监听器 */
export type AnimationEventListener = (event: AnimationEvent) => void;

// ==================== 动画控制器接口 ====================

/** 动画控制器接口 */
export interface IAnimationController {
  // 时间线管理
  addTimeline(timeline: AnimationTimeline): void;
  removeTimeline(timelineId: string): void;
  getTimeline(timelineId: string): AnimationTimeline | undefined;

  // 播放控制
  play(timelineId: string): void;
  pause(timelineId: string): void;
  stop(timelineId: string): void;
  seek(timelineId: string, time: number): void;
  setPlaybackRate(timelineId: string, rate: number): void;
  setDirection(timelineId: string, direction: AnimationDirection): void;

  // 状态查询
  getState(timelineId: string): AnimationRuntimeState | undefined;
  isPlaying(timelineId: string): boolean;

  // 事件
  on(event: AnimationEventType, listener: AnimationEventListener): void;
  off(event: AnimationEventType, listener: AnimationEventListener): void;

  // 更新
  update(deltaTime: number): void;

  // 销毁
  destroy(): void;
}

// ==================== 补间动画 ====================

/** 补间动画配置 */
export interface TweenConfig<T = unknown> {
  target: string;              // 目标元素 ID
  property: AnimatableProperty;
  from?: T;
  to: T;
  duration: number;            // 毫秒
  delay?: number;
  easing?: EasingType;
  repeat?: number;             // 重复次数，-1 为无限
  yoyo?: boolean;              // 往返动画
  onStart?: () => void;
  onUpdate?: (value: T) => void;
  onComplete?: () => void;
}

/** 补间动画序列 */
export interface TweenSequence {
  id: string;
  tweens: TweenConfig[];
  parallel?: boolean;          // 是否并行执行
}
