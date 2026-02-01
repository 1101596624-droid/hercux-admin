/**
 * 动画控制器 - 基于 GSAP 的时间线动画管理
 */

import gsap from 'gsap';
import type {
  AnimationTimeline,
  AnimationTrack,
  Keyframe,
  EasingType,
  PresetEasing,
  BezierEasing,
  SpringEasing,
  Vector2D,
  Color,
} from '@/types/simulator-engine';
import { getEasingFunction } from '../utils/EasingFunctions';
import { lerpColor, lerpVector2D } from '@/types/simulator-engine/base';

// ==================== 类型定义 ====================

/** 动画状态 */
export type AnimationState = 'idle' | 'playing' | 'paused' | 'completed';

/** 动画事件类型 */
export type AnimationEventType =
  | 'start'
  | 'update'
  | 'complete'
  | 'loop'
  | 'pause'
  | 'resume'
  | 'seek';

/** 动画事件监听器 */
export type AnimationEventListener = (event: {
  type: AnimationEventType;
  timelineId: string;
  currentTime: number;
  progress: number;
}) => void;

/** 属性更新回调 */
export type PropertyUpdateCallback = (
  targetId: string,
  property: string,
  value: unknown
) => void;

/** 时间线实例 */
interface TimelineInstance {
  id: string;
  timeline: AnimationTimeline;
  gsapTimeline: gsap.core.Timeline;
  state: AnimationState;
  currentTime: number;
  loopCount: number;
}

// ==================== 动画控制器类 ====================

export class AnimationController {
  private timelines: Map<string, TimelineInstance> = new Map();
  private eventListeners: Map<AnimationEventType, Set<AnimationEventListener>> = new Map();
  private propertyUpdateCallback: PropertyUpdateCallback | null = null;
  private globalTimeScale: number = 1;

  constructor() {
    // 初始化事件监听器集合
    const eventTypes: AnimationEventType[] = [
      'start', 'update', 'complete', 'loop', 'pause', 'resume', 'seek'
    ];
    eventTypes.forEach(type => {
      this.eventListeners.set(type, new Set());
    });
  }

  // ==================== 公共方法 ====================

  /**
   * 设置属性更新回调
   */
  setPropertyUpdateCallback(callback: PropertyUpdateCallback): void {
    this.propertyUpdateCallback = callback;
  }

  /**
   * 加载时间线
   */
  loadTimeline(timeline: AnimationTimeline): void {
    // 如果已存在，先销毁
    if (this.timelines.has(timeline.id)) {
      this.destroyTimeline(timeline.id);
    }

    // 创建 GSAP 时间线
    const gsapTimeline = this.createGsapTimeline(timeline);

    const instance: TimelineInstance = {
      id: timeline.id,
      timeline,
      gsapTimeline,
      state: 'idle',
      currentTime: 0,
      loopCount: 0,
    };

    this.timelines.set(timeline.id, instance);
  }

  /**
   * 加载多个时间线
   */
  loadTimelines(timelines: AnimationTimeline[]): void {
    timelines.forEach(timeline => this.loadTimeline(timeline));
  }

  /**
   * 播放时间线
   */
  play(timelineId: string, fromStart: boolean = false): void {
    const instance = this.timelines.get(timelineId);
    if (!instance) {
      console.warn(`时间线不存在: ${timelineId}`);
      return;
    }

    if (fromStart) {
      instance.gsapTimeline.restart();
      instance.loopCount = 0;
    } else {
      instance.gsapTimeline.play();
    }

    instance.state = 'playing';
    this.emitEvent('start', instance);
  }

  /**
   * 暂停时间线
   */
  pause(timelineId: string): void {
    const instance = this.timelines.get(timelineId);
    if (!instance) return;

    instance.gsapTimeline.pause();
    instance.state = 'paused';
    this.emitEvent('pause', instance);
  }

  /**
   * 恢复时间线
   */
  resume(timelineId: string): void {
    const instance = this.timelines.get(timelineId);
    if (!instance || instance.state !== 'paused') return;

    instance.gsapTimeline.resume();
    instance.state = 'playing';
    this.emitEvent('resume', instance);
  }

  /**
   * 停止时间线
   */
  stop(timelineId: string): void {
    const instance = this.timelines.get(timelineId);
    if (!instance) return;

    instance.gsapTimeline.pause();
    instance.gsapTimeline.seek(0);
    instance.state = 'idle';
    instance.currentTime = 0;
    instance.loopCount = 0;
  }

  /**
   * 跳转到指定时间
   */
  seek(timelineId: string, time: number): void {
    const instance = this.timelines.get(timelineId);
    if (!instance) return;

    const clampedTime = Math.max(0, Math.min(time, instance.timeline.duration));
    instance.gsapTimeline.seek(clampedTime / 1000); // GSAP 使用秒
    instance.currentTime = clampedTime;
    this.emitEvent('seek', instance);
  }

  /**
   * 设置时间线进度 (0-1)
   */
  setProgress(timelineId: string, progress: number): void {
    const instance = this.timelines.get(timelineId);
    if (!instance) return;

    const clampedProgress = Math.max(0, Math.min(1, progress));
    instance.gsapTimeline.progress(clampedProgress);
    instance.currentTime = clampedProgress * instance.timeline.duration;
    this.emitEvent('seek', instance);
  }

  /**
   * 获取时间线状态
   */
  getState(timelineId: string): AnimationState | null {
    return this.timelines.get(timelineId)?.state || null;
  }

  /**
   * 获取当前时间
   */
  getCurrentTime(timelineId: string): number {
    return this.timelines.get(timelineId)?.currentTime || 0;
  }

  /**
   * 获取进度 (0-1)
   */
  getProgress(timelineId: string): number {
    const instance = this.timelines.get(timelineId);
    if (!instance) return 0;
    return instance.currentTime / instance.timeline.duration;
  }

  /**
   * 设置全局时间缩放
   */
  setGlobalTimeScale(scale: number): void {
    this.globalTimeScale = scale;
    this.timelines.forEach(instance => {
      instance.gsapTimeline.timeScale(scale);
    });
  }

  /**
   * 播放所有时间线
   */
  playAll(fromStart: boolean = false): void {
    this.timelines.forEach((_, id) => this.play(id, fromStart));
  }

  /**
   * 暂停所有时间线
   */
  pauseAll(): void {
    this.timelines.forEach((_, id) => this.pause(id));
  }

  /**
   * 停止所有时间线
   */
  stopAll(): void {
    this.timelines.forEach((_, id) => this.stop(id));
  }

  /**
   * 销毁时间线
   */
  destroyTimeline(timelineId: string): void {
    const instance = this.timelines.get(timelineId);
    if (!instance) return;

    instance.gsapTimeline.kill();
    this.timelines.delete(timelineId);
  }

  /**
   * 销毁所有时间线
   */
  destroyAll(): void {
    this.timelines.forEach(instance => {
      instance.gsapTimeline.kill();
    });
    this.timelines.clear();
  }

  /**
   * 添加事件监听器
   */
  on(event: AnimationEventType, listener: AnimationEventListener): void {
    this.eventListeners.get(event)?.add(listener);
  }

  /**
   * 移除事件监听器
   */
  off(event: AnimationEventType, listener: AnimationEventListener): void {
    this.eventListeners.get(event)?.delete(listener);
  }

  // ==================== 私有方法 ====================

  /**
   * 创建 GSAP 时间线
   */
  private createGsapTimeline(timeline: AnimationTimeline): gsap.core.Timeline {
    const gsapTl = gsap.timeline({
      paused: true,
      repeat: timeline.loop ? -1 : 0,
      onUpdate: () => this.handleTimelineUpdate(timeline.id),
      onComplete: () => this.handleTimelineComplete(timeline.id),
      onRepeat: () => this.handleTimelineLoop(timeline.id),
    });

    // 支持两种结构：tracks 或扁平 keyframes
    if (timeline.tracks && timeline.tracks.length > 0) {
      // 标准 tracks 结构
      timeline.tracks.forEach(track => {
        this.addTrackToTimeline(gsapTl, track, timeline.duration);
      });
    } else {
      // 扁平 keyframes 结构（模板使用的格式）
      const flatKeyframes = (timeline as unknown as { keyframes?: Array<{ time: number; targetId: string; property: string; value: unknown; easing?: EasingType }> }).keyframes;
      if (flatKeyframes && flatKeyframes.length > 0) {
        // 按 targetId + property 分组转换为 tracks
        const trackMap = new Map<string, AnimationTrack>();

        flatKeyframes.forEach((kf, index) => {
          const key = `${kf.targetId}:${kf.property}`;
          if (!trackMap.has(key)) {
            trackMap.set(key, {
              id: `track_${index}`,
              targetId: kf.targetId,
              property: kf.property,
              keyframes: [],
            });
          }
          trackMap.get(key)!.keyframes.push({
            time: kf.time,
            value: kf.value,
            easing: kf.easing,
          });
        });

        // 添加转换后的 tracks
        trackMap.forEach(track => {
          // 按时间排序关键帧
          track.keyframes.sort((a, b) => a.time - b.time);
          this.addTrackToTimeline(gsapTl, track, timeline.duration);
        });
      }
    }

    gsapTl.timeScale(this.globalTimeScale);

    return gsapTl;
  }

  /**
   * 将轨道添加到 GSAP 时间线
   */
  private addTrackToTimeline(
    gsapTl: gsap.core.Timeline,
    track: AnimationTrack,
    totalDuration: number
  ): void {
    if (track.keyframes.length < 2) return;

    // 对关键帧按时间排序
    const sortedKeyframes = [...track.keyframes].sort((a, b) => a.time - b.time);

    // 创建动画对象来存储当前值
    const animationTarget = { value: sortedKeyframes[0].value };

    // 为每对相邻关键帧创建补间动画
    for (let i = 0; i < sortedKeyframes.length - 1; i++) {
      const fromKf = sortedKeyframes[i];
      const toKf = sortedKeyframes[i + 1];
      const duration = (toKf.time - fromKf.time) / 1000; // 转换为秒

      if (duration <= 0) continue;

      const easing = this.getGsapEasing(toKf.easing || 'linear');

      gsapTl.to(
        animationTarget,
        {
          value: toKf.value,
          duration,
          ease: easing,
          onUpdate: () => {
            this.updateProperty(track.targetId, track.property, animationTarget.value);
          },
        },
        fromKf.time / 1000 // 开始时间（秒）
      );
    }
  }

  /**
   * 检查是否为贝塞尔缓动
   */
  private isBezierEasing(easing: EasingType): easing is BezierEasing {
    return typeof easing === 'object' && easing !== null && (easing as BezierEasing).type === 'bezier';
  }

  /**
   * 检查是否为弹簧缓动
   */
  private isSpringEasing(easing: EasingType): easing is SpringEasing {
    return typeof easing === 'object' && easing !== null && (easing as SpringEasing).type === 'spring';
  }

  /**
   * 获取 GSAP 缓动字符串
   */
  private getGsapEasing(easing: EasingType): string {
    // 处理贝塞尔缓动
    if (this.isBezierEasing(easing)) {
      const [x1, y1, x2, y2] = easing.controlPoints;
      return `cubic-bezier(${x1}, ${y1}, ${x2}, ${y2})`;
    }

    // 处理弹簧缓动
    if (this.isSpringEasing(easing)) {
      // GSAP 的 elastic 近似弹簧效果
      const amplitude = 1;
      const period = 0.3 + (1 - easing.damping / 100) * 0.7;
      return `elastic.out(${amplitude}, ${period})`;
    }

    // 预设缓动映射
    const gsapEasingMap: Record<PresetEasing, string> = {
      linear: 'none',
      easeIn: 'power1.in',
      easeOut: 'power1.out',
      easeInOut: 'power1.inOut',
      easeInQuad: 'power2.in',
      easeOutQuad: 'power2.out',
      easeInOutQuad: 'power2.inOut',
      easeInCubic: 'power3.in',
      easeOutCubic: 'power3.out',
      easeInOutCubic: 'power3.inOut',
      easeInQuart: 'power4.in',
      easeOutQuart: 'power4.out',
      easeInOutQuart: 'power4.inOut',
      easeInQuint: 'power4.in',
      easeOutQuint: 'power4.out',
      easeInOutQuint: 'power4.inOut',
      easeInSine: 'sine.in',
      easeOutSine: 'sine.out',
      easeInOutSine: 'sine.inOut',
      easeInExpo: 'expo.in',
      easeOutExpo: 'expo.out',
      easeInOutExpo: 'expo.inOut',
      easeInCirc: 'circ.in',
      easeOutCirc: 'circ.out',
      easeInOutCirc: 'circ.inOut',
      easeInElastic: 'elastic.in(1, 0.3)',
      easeOutElastic: 'elastic.out(1, 0.3)',
      easeInOutElastic: 'elastic.inOut(1, 0.3)',
      easeInBack: 'back.in(1.7)',
      easeOutBack: 'back.out(1.7)',
      easeInOutBack: 'back.inOut(1.7)',
      easeInBounce: 'bounce.in',
      easeOutBounce: 'bounce.out',
      easeInOutBounce: 'bounce.inOut',
    };

    return gsapEasingMap[easing as PresetEasing] || 'none';
  }

  /**
   * 更新属性值
   */
  private updateProperty(targetId: string, property: string, value: unknown): void {
    if (this.propertyUpdateCallback) {
      this.propertyUpdateCallback(targetId, property, value);
    }
  }

  /**
   * 处理时间线更新
   */
  private handleTimelineUpdate(timelineId: string): void {
    const instance = this.timelines.get(timelineId);
    if (!instance) return;

    instance.currentTime = instance.gsapTimeline.time() * 1000; // 转换为毫秒
    this.emitEvent('update', instance);
  }

  /**
   * 处理时间线完成
   */
  private handleTimelineComplete(timelineId: string): void {
    const instance = this.timelines.get(timelineId);
    if (!instance) return;

    instance.state = 'completed';
    this.emitEvent('complete', instance);
  }

  /**
   * 处理时间线循环
   */
  private handleTimelineLoop(timelineId: string): void {
    const instance = this.timelines.get(timelineId);
    if (!instance) return;

    instance.loopCount++;
    this.emitEvent('loop', instance);
  }

  /**
   * 触发事件
   */
  private emitEvent(type: AnimationEventType, instance: TimelineInstance): void {
    const listeners = this.eventListeners.get(type);
    if (!listeners) return;

    const event = {
      type,
      timelineId: instance.id,
      currentTime: instance.currentTime,
      progress: instance.currentTime / instance.timeline.duration,
    };

    listeners.forEach(listener => {
      try {
        listener(event);
      } catch (e) {
        console.error('动画事件监听器错误:', e);
      }
    });
  }
}

// ==================== 手动插值动画控制器 ====================

/**
 * 手动插值动画控制器 - 不依赖 GSAP，用于自定义渲染循环
 */
export class ManualAnimationController {
  private timelines: Map<string, AnimationTimeline> = new Map();
  private timelineStates: Map<string, {
    currentTime: number;
    playing: boolean;
    loopCount: number;
  }> = new Map();
  private propertyUpdateCallback: PropertyUpdateCallback | null = null;

  /**
   * 设置属性更新回调
   */
  setPropertyUpdateCallback(callback: PropertyUpdateCallback): void {
    this.propertyUpdateCallback = callback;
  }

  /**
   * 加载时间线
   */
  loadTimeline(timeline: AnimationTimeline): void {
    this.timelines.set(timeline.id, timeline);
    this.timelineStates.set(timeline.id, {
      currentTime: 0,
      playing: false,
      loopCount: 0,
    });
  }

  /**
   * 播放时间线
   */
  play(timelineId: string): void {
    const state = this.timelineStates.get(timelineId);
    console.log('ManualAnimationController: play', timelineId, 'state exists:', !!state, 'timelines:', Array.from(this.timelines.keys()));
    if (state) {
      // 从头开始播放
      state.currentTime = 0;
      state.playing = true;
    } else {
      console.warn('ManualAnimationController: timeline not found:', timelineId);
    }
  }

  /**
   * 暂停时间线
   */
  pause(timelineId: string): void {
    const state = this.timelineStates.get(timelineId);
    if (state) {
      state.playing = false;
    }
  }

  /**
   * 停止时间线
   */
  stop(timelineId: string): void {
    const state = this.timelineStates.get(timelineId);
    if (state) {
      state.playing = false;
      state.currentTime = 0;
      state.loopCount = 0;
    }
  }

  /**
   * 更新动画 (每帧调用)
   * @param deltaTime 时间增量 (毫秒)
   */
  update(deltaTime: number): void {
    this.timelines.forEach((timeline, id) => {
      const state = this.timelineStates.get(id);
      if (!state || !state.playing) return;

      // 更新时间
      state.currentTime += deltaTime;
      console.log('ManualAnimationController: update', id, 'currentTime:', state.currentTime, 'duration:', timeline.duration);

      // 处理循环
      if (state.currentTime >= timeline.duration) {
        if (timeline.loop) {
          state.currentTime = state.currentTime % timeline.duration;
          state.loopCount++;
        } else {
          state.currentTime = timeline.duration;
          state.playing = false;
        }
      }

      // 更新所有轨道
      this.updateTracks(timeline, state.currentTime);
    });
  }

  /**
   * 更新轨道
   */
  private updateTracks(timeline: AnimationTimeline, currentTime: number): void {
    // 支持标准 tracks 结构
    if (timeline.tracks && timeline.tracks.length > 0) {
      console.log('ManualAnimationController: updateTracks', timeline.id, 'tracks count:', timeline.tracks.length, 'callback exists:', !!this.propertyUpdateCallback);
      timeline.tracks.forEach(track => {
        const value = this.interpolateTrack(track, currentTime);
        console.log('ManualAnimationController: track', track.targetId, track.property, 'value:', value);
        if (value !== undefined && this.propertyUpdateCallback) {
          this.propertyUpdateCallback(track.targetId, track.property, value);
        }
      });
    } else {
      // 支持扁平 keyframes 结构
      const flatKeyframes = (timeline as unknown as { keyframes?: Array<{ time: number; targetId: string; property: string; value: unknown; easing?: EasingType }> }).keyframes;
      if (flatKeyframes && flatKeyframes.length > 0) {
        // 按 targetId + property 分组
        const trackMap = new Map<string, AnimationTrack>();

        flatKeyframes.forEach((kf, index) => {
          const key = `${kf.targetId}:${kf.property}`;
          if (!trackMap.has(key)) {
            trackMap.set(key, {
              id: `track_${index}`,
              targetId: kf.targetId,
              property: kf.property,
              keyframes: [],
            });
          }
          trackMap.get(key)!.keyframes.push({
            time: kf.time,
            value: kf.value,
            easing: kf.easing,
          });
        });

        trackMap.forEach(track => {
          track.keyframes.sort((a, b) => a.time - b.time);
          const value = this.interpolateTrack(track, currentTime);
          if (value !== undefined && this.propertyUpdateCallback) {
            this.propertyUpdateCallback(track.targetId, track.property, value);
          }
        });
      }
    }
  }

  /**
   * 插值轨道值
   */
  private interpolateTrack(track: AnimationTrack, currentTime: number): unknown {
    const keyframes = track.keyframes;
    if (keyframes.length === 0) return undefined;
    if (keyframes.length === 1) return keyframes[0].value;

    // 找到当前时间所在的关键帧区间
    let fromKf = keyframes[0];
    let toKf = keyframes[keyframes.length - 1];

    for (let i = 0; i < keyframes.length - 1; i++) {
      if (currentTime >= keyframes[i].time && currentTime <= keyframes[i + 1].time) {
        fromKf = keyframes[i];
        toKf = keyframes[i + 1];
        break;
      }
    }

    // 如果在第一个关键帧之前
    if (currentTime < fromKf.time) {
      return fromKf.value;
    }

    // 如果在最后一个关键帧之后
    if (currentTime > toKf.time) {
      return toKf.value;
    }

    // 计算进度
    const duration = toKf.time - fromKf.time;
    if (duration === 0) return toKf.value;

    const progress = (currentTime - fromKf.time) / duration;

    // 应用缓动并插值
    return this.interpolateValue(fromKf.value, toKf.value, progress, toKf.easing || 'linear');
  }

  /**
   * 插值任意类型的值
   */
  private interpolateValue(
    from: unknown,
    to: unknown,
    progress: number,
    easing: EasingType
  ): unknown {
    const easingFn = getEasingFunction(easing);
    const easedProgress = easingFn(progress);

    // 数字插值
    if (typeof from === 'number' && typeof to === 'number') {
      return from + (to - from) * easedProgress;
    }

    // Vector2D 插值
    if (this.isVector2D(from) && this.isVector2D(to)) {
      return lerpVector2D(from, to, easedProgress);
    }

    // 颜色插值
    if (this.isColor(from) && this.isColor(to)) {
      return lerpColor(from, to, easedProgress);
    }

    // 字符串颜色插值 (十六进制)
    if (typeof from === 'string' && typeof to === 'string') {
      if (from.startsWith('#') && to.startsWith('#')) {
        return this.interpolateHexColor(from, to, easedProgress);
      }
    }

    // 无法插值，返回目标值
    return progress >= 0.5 ? to : from;
  }

  /**
   * 检查是否为 Vector2D
   */
  private isVector2D(value: unknown): value is Vector2D {
    return (
      typeof value === 'object' &&
      value !== null &&
      'x' in value &&
      'y' in value &&
      typeof (value as Vector2D).x === 'number' &&
      typeof (value as Vector2D).y === 'number'
    );
  }

  /**
   * 检查是否为 Color
   */
  private isColor(value: unknown): value is Color {
    return (
      typeof value === 'object' &&
      value !== null &&
      'r' in value &&
      'g' in value &&
      'b' in value
    );
  }

  /**
   * 插值十六进制颜色
   */
  private interpolateHexColor(from: string, to: string, progress: number): string {
    const fromRgb = this.hexToRgb(from);
    const toRgb = this.hexToRgb(to);

    const r = Math.round(fromRgb.r + (toRgb.r - fromRgb.r) * progress);
    const g = Math.round(fromRgb.g + (toRgb.g - fromRgb.g) * progress);
    const b = Math.round(fromRgb.b + (toRgb.b - fromRgb.b) * progress);

    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
  }

  /**
   * 十六进制转 RGB
   */
  private hexToRgb(hex: string): { r: number; g: number; b: number } {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result
      ? {
          r: parseInt(result[1], 16),
          g: parseInt(result[2], 16),
          b: parseInt(result[3], 16),
        }
      : { r: 0, g: 0, b: 0 };
  }

  /**
   * 销毁
   */
  destroy(): void {
    this.timelines.clear();
    this.timelineStates.clear();
    this.propertyUpdateCallback = null;
  }
}

// ==================== 导出单例 ====================

export const animationController = new AnimationController();
