/**
 * 骨骼动画系统 - 支持 Spine 格式和自定义骨骼动画
 */

import * as PIXI from 'pixi.js';
import type {
  Bone,
  SkeletonSlot,
  SkeletonSkin,
  SkeletonAnimation,
  BoneTimeline,
  SlotTimeline,
  BoneKeyframe,
  SlotKeyframe,
  SkeletonConfig,
} from '@/types/simulator-engine';
import type { Vector2D, Color } from '@/types/simulator-engine';

// ==================== 类型定义 ====================

/** 骨骼运行时状态 */
interface BoneState {
  id: string;
  name: string;
  parentId?: string;
  length: number;
  localRotation: number;
  localPosition: Vector2D;
  worldRotation: number;
  worldPosition: Vector2D;
  worldScale: Vector2D;
}

/** 插槽运行时状态 */
interface SlotState {
  id: string;
  boneId: string;
  attachment?: string;
  color: Color;
  zIndex: number;
  sprite?: PIXI.Sprite | PIXI.Graphics;
}

/** 骨骼实例状态 */
interface SkeletonState {
  id: string;
  config: SkeletonConfig;
  container: PIXI.Container;
  bones: Map<string, BoneState>;
  slots: Map<string, SlotState>;
  activeSkin: string;
  activeAnimation?: string;
  animationTime: number;
  animationSpeed: number;
  isPlaying: boolean;
  loop: boolean;
}

/** 动画事件回调 */
export type SkeletonEventCallback = (event: SkeletonEvent) => void;

/** 骨骼事件 */
export interface SkeletonEvent {
  type: 'animationStart' | 'animationEnd' | 'animationLoop' | 'event';
  skeletonId: string;
  animationName?: string;
  eventName?: string;
  time?: number;
}

// ==================== 工具函数 ====================

/** 线性插值 */
function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

/** 向量插值 */
function lerpVector(a: Vector2D, b: Vector2D, t: number): Vector2D {
  return {
    x: lerp(a.x, b.x, t),
    y: lerp(a.y, b.y, t),
  };
}

/** 颜色插值 */
function lerpColor(a: Color, b: Color, t: number): Color {
  return {
    r: Math.round(lerp(a.r, b.r, t)),
    g: Math.round(lerp(a.g, b.g, t)),
    b: Math.round(lerp(a.b, b.b, t)),
    a: lerp(a.a, b.a, t),
  };
}

/** 角度插值 (处理环绕) */
function lerpAngle(a: number, b: number, t: number): number {
  let diff = b - a;
  while (diff > 180) diff -= 360;
  while (diff < -180) diff += 360;
  return a + diff * t;
}

/** 角度转弧度 */
function degToRad(deg: number): number {
  return deg * (Math.PI / 180);
}

/** 弧度转角度 */
function radToDeg(rad: number): number {
  return rad * (180 / Math.PI);
}

/** 颜色转十六进制 */
function colorToHex(color: Color): number {
  return (color.r << 16) + (color.g << 8) + color.b;
}

// ==================== 骨骼系统类 ====================

export class SkeletonSystem {
  private skeletons: Map<string, SkeletonState> = new Map();
  private eventCallbacks: Set<SkeletonEventCallback> = new Set();
  private textureCache: Map<string, PIXI.Texture> = new Map();

  constructor() {}

  // ==================== 骨骼管理 ====================

  /**
   * 创建骨骼实例
   */
  createSkeleton(
    id: string,
    config: SkeletonConfig,
    parentContainer: PIXI.Container
  ): void {
    if (this.skeletons.has(id)) {
      console.warn(`骨骼实例已存在: ${id}`);
      return;
    }

    const container = new PIXI.Container();
    container.sortableChildren = true;
    parentContainer.addChild(container);

    // 初始化骨骼状态
    const bones = new Map<string, BoneState>();
    for (const bone of config.bones) {
      bones.set(bone.id, {
        id: bone.id,
        name: bone.name,
        parentId: bone.parentId,
        length: bone.length,
        localRotation: bone.rotation,
        localPosition: { ...bone.position },
        worldRotation: 0,
        worldPosition: { x: 0, y: 0 },
        worldScale: { x: 1, y: 1 },
      });
    }

    // 初始化插槽状态
    const slots = new Map<string, SlotState>();
    for (const slot of config.slots) {
      slots.set(slot.id, {
        id: slot.id,
        boneId: slot.boneId,
        attachment: slot.attachment,
        color: slot.color || { r: 255, g: 255, b: 255, a: 1 },
        zIndex: slot.zIndex || 0,
      });
    }

    const state: SkeletonState = {
      id,
      config,
      container,
      bones,
      slots,
      activeSkin: config.activeSkin,
      activeAnimation: config.activeAnimation,
      animationTime: 0,
      animationSpeed: 1,
      isPlaying: false,
      loop: true,
    };

    this.skeletons.set(id, state);

    // 计算初始骨骼变换
    this.updateBoneTransforms(state);

    // 创建插槽精灵
    this.updateSlotAttachments(state);

    // 如果有默认动画，开始播放
    if (config.activeAnimation) {
      this.playAnimation(id, config.activeAnimation);
    }
  }

  /**
   * 移除骨骼实例
   */
  removeSkeleton(id: string): void {
    const state = this.skeletons.get(id);
    if (!state) return;

    // 清理插槽精灵
    state.slots.forEach(slot => {
      if (slot.sprite) {
        state.container.removeChild(slot.sprite);
        slot.sprite.destroy();
      }
    });

    // 移除容器
    if (state.container.parent) {
      state.container.parent.removeChild(state.container);
    }
    state.container.destroy();

    this.skeletons.delete(id);
  }

  // ==================== 骨骼变换 ====================

  /**
   * 更新骨骼世界变换
   */
  private updateBoneTransforms(state: SkeletonState): void {
    // 按层级顺序更新骨骼
    const rootBones = Array.from(state.bones.values()).filter(b => !b.parentId);

    for (const bone of rootBones) {
      this.updateBoneWorldTransform(state, bone);
    }
  }

  /**
   * 递归更新单个骨骼的世界变换
   */
  private updateBoneWorldTransform(state: SkeletonState, bone: BoneState): void {
    if (bone.parentId) {
      const parent = state.bones.get(bone.parentId);
      if (parent) {
        // 计算世界旋转
        bone.worldRotation = parent.worldRotation + bone.localRotation;

        // 计算世界位置
        const parentAngleRad = degToRad(parent.worldRotation);
        const cos = Math.cos(parentAngleRad);
        const sin = Math.sin(parentAngleRad);

        bone.worldPosition = {
          x: parent.worldPosition.x + (bone.localPosition.x * cos - bone.localPosition.y * sin) * parent.worldScale.x,
          y: parent.worldPosition.y + (bone.localPosition.x * sin + bone.localPosition.y * cos) * parent.worldScale.y,
        };

        // 继承缩放
        bone.worldScale = {
          x: parent.worldScale.x,
          y: parent.worldScale.y,
        };
      }
    } else {
      // 根骨骼
      bone.worldRotation = bone.localRotation;
      bone.worldPosition = { ...bone.localPosition };
      bone.worldScale = { x: 1, y: 1 };
    }

    // 递归更新子骨骼
    const children = Array.from(state.bones.values()).filter(b => b.parentId === bone.id);
    for (const child of children) {
      this.updateBoneWorldTransform(state, child);
    }
  }

  // ==================== 插槽和附件 ====================

  /**
   * 更新插槽附件
   */
  private updateSlotAttachments(state: SkeletonState): void {
    const skin = state.config.skins.find(s => s.id === state.activeSkin);
    if (!skin) return;

    state.slots.forEach(slot => {
      // 清理旧精灵
      if (slot.sprite) {
        state.container.removeChild(slot.sprite);
        slot.sprite.destroy();
        slot.sprite = undefined;
      }

      // 创建新附件
      if (slot.attachment) {
        const attachment = skin.attachments[slot.attachment];
        if (attachment && attachment.type === 'sprite') {
          const sprite = this.createAttachmentSprite(attachment.source);
          if (sprite) {
            if (sprite instanceof PIXI.Sprite) {
              sprite.anchor.set(0.5, 0.5);
            }
            sprite.zIndex = slot.zIndex;
            sprite.tint = colorToHex(slot.color);
            sprite.alpha = slot.color.a;
            state.container.addChild(sprite);
            slot.sprite = sprite;
          }
        }
      }
    });
  }

  /**
   * 创建附件精灵
   */
  private createAttachmentSprite(source: string): PIXI.Sprite | PIXI.Graphics | null {
    // 检查缓存
    let texture = this.textureCache.get(source);

    if (!texture) {
      // 尝试从 URL 加载
      try {
        texture = PIXI.Texture.from(source);
        this.textureCache.set(source, texture);
      } catch {
        // 创建占位符图形
        const graphics = new PIXI.Graphics();
        graphics.fill({ color: 0xcccccc });
        graphics.rect(-20, -20, 40, 40);
        graphics.fill();
        return graphics;
      }
    }

    return new PIXI.Sprite(texture);
  }

  /**
   * 更新插槽精灵位置
   */
  private updateSlotSprites(state: SkeletonState): void {
    const skin = state.config.skins.find(s => s.id === state.activeSkin);
    if (!skin) return;

    state.slots.forEach(slot => {
      if (!slot.sprite) return;

      const bone = state.bones.get(slot.boneId);
      if (!bone) return;

      const attachment = slot.attachment ? skin.attachments[slot.attachment] : null;

      // 计算精灵位置
      const boneAngleRad = degToRad(bone.worldRotation);
      const cos = Math.cos(boneAngleRad);
      const sin = Math.sin(boneAngleRad);

      let offsetX = 0;
      let offsetY = 0;
      let attachRotation = 0;
      let attachScaleX = 1;
      let attachScaleY = 1;

      if (attachment) {
        offsetX = attachment.offset.x;
        offsetY = attachment.offset.y;
        attachRotation = attachment.rotation;
        attachScaleX = attachment.scale.x;
        attachScaleY = attachment.scale.y;
      }

      slot.sprite.position.set(
        bone.worldPosition.x + (offsetX * cos - offsetY * sin) * bone.worldScale.x,
        bone.worldPosition.y + (offsetX * sin + offsetY * cos) * bone.worldScale.y
      );

      slot.sprite.rotation = degToRad(bone.worldRotation + attachRotation);
      slot.sprite.scale.set(
        bone.worldScale.x * attachScaleX,
        bone.worldScale.y * attachScaleY
      );

      slot.sprite.tint = colorToHex(slot.color);
      slot.sprite.alpha = slot.color.a;
    });
  }

  // ==================== 动画控制 ====================

  /**
   * 播放动画
   */
  playAnimation(id: string, animationName: string, loop: boolean = true): void {
    const state = this.skeletons.get(id);
    if (!state) return;

    const animation = state.config.animations.find(a => a.name === animationName || a.id === animationName);
    if (!animation) {
      console.warn(`动画不存在: ${animationName}`);
      return;
    }

    state.activeAnimation = animation.id;
    state.animationTime = 0;
    state.isPlaying = true;
    state.loop = loop;

    this.emitEvent({
      type: 'animationStart',
      skeletonId: id,
      animationName: animation.name,
    });
  }

  /**
   * 停止动画
   */
  stopAnimation(id: string): void {
    const state = this.skeletons.get(id);
    if (!state) return;

    state.isPlaying = false;
  }

  /**
   * 暂停动画
   */
  pauseAnimation(id: string): void {
    const state = this.skeletons.get(id);
    if (state) {
      state.isPlaying = false;
    }
  }

  /**
   * 恢复动画
   */
  resumeAnimation(id: string): void {
    const state = this.skeletons.get(id);
    if (state && state.activeAnimation) {
      state.isPlaying = true;
    }
  }

  /**
   * 设置动画速度
   */
  setAnimationSpeed(id: string, speed: number): void {
    const state = this.skeletons.get(id);
    if (state) {
      state.animationSpeed = speed;
    }
  }

  /**
   * 设置动画时间
   */
  setAnimationTime(id: string, time: number): void {
    const state = this.skeletons.get(id);
    if (state) {
      state.animationTime = time;
    }
  }

  // ==================== 皮肤管理 ====================

  /**
   * 设置皮肤
   */
  setSkin(id: string, skinName: string): void {
    const state = this.skeletons.get(id);
    if (!state) return;

    const skin = state.config.skins.find(s => s.name === skinName || s.id === skinName);
    if (!skin) {
      console.warn(`皮肤不存在: ${skinName}`);
      return;
    }

    state.activeSkin = skin.id;
    this.updateSlotAttachments(state);
  }

  // ==================== 更新 ====================

  /**
   * 更新所有骨骼动画
   */
  update(deltaTime: number): void {
    const dt = deltaTime / 1000; // 转换为秒

    this.skeletons.forEach(state => {
      if (!state.isPlaying || !state.activeAnimation) return;

      const animation = state.config.animations.find(a => a.id === state.activeAnimation);
      if (!animation) return;

      // 更新动画时间
      state.animationTime += dt * state.animationSpeed * 1000;

      // 检查动画结束
      if (state.animationTime >= animation.duration) {
        if (state.loop) {
          state.animationTime = state.animationTime % animation.duration;
          this.emitEvent({
            type: 'animationLoop',
            skeletonId: state.id,
            animationName: animation.name,
          });
        } else {
          state.animationTime = animation.duration;
          state.isPlaying = false;
          this.emitEvent({
            type: 'animationEnd',
            skeletonId: state.id,
            animationName: animation.name,
          });
        }
      }

      // 应用动画
      this.applyAnimation(state, animation, state.animationTime);

      // 更新骨骼变换
      this.updateBoneTransforms(state);

      // 更新插槽精灵
      this.updateSlotSprites(state);
    });
  }

  /**
   * 应用动画到骨骼
   */
  private applyAnimation(state: SkeletonState, animation: SkeletonAnimation, time: number): void {
    // 应用骨骼时间线
    for (const timeline of animation.boneTimelines) {
      const bone = state.bones.get(timeline.boneId);
      if (!bone) continue;

      const { rotation, position, scale } = this.interpolateBoneKeyframes(timeline.keyframes, time);

      if (rotation !== undefined) {
        bone.localRotation = rotation;
      }
      if (position) {
        bone.localPosition = position;
      }
      // scale 暂不处理，可扩展
    }

    // 应用插槽时间线
    for (const timeline of animation.slotTimelines) {
      const slot = state.slots.get(timeline.slotId);
      if (!slot) continue;

      const { attachment, color } = this.interpolateSlotKeyframes(timeline.keyframes, time);

      if (attachment !== undefined) {
        if (slot.attachment !== attachment) {
          slot.attachment = attachment;
          // 需要重新创建精灵
          this.updateSingleSlotAttachment(state, slot);
        }
      }
      if (color) {
        slot.color = color;
      }
    }
  }

  /**
   * 插值骨骼关键帧
   */
  private interpolateBoneKeyframes(
    keyframes: BoneKeyframe[],
    time: number
  ): { rotation?: number; position?: Vector2D; scale?: Vector2D } {
    if (keyframes.length === 0) return {};

    // 找到当前时间的前后关键帧
    let fromKf = keyframes[0];
    let toKf = keyframes[0];

    for (let i = 0; i < keyframes.length; i++) {
      if (keyframes[i].time <= time) {
        fromKf = keyframes[i];
        toKf = keyframes[i + 1] || keyframes[i];
      }
    }

    // 计算插值因子
    const duration = toKf.time - fromKf.time;
    const t = duration > 0 ? (time - fromKf.time) / duration : 0;

    const result: { rotation?: number; position?: Vector2D; scale?: Vector2D } = {};

    // 插值旋转
    if (fromKf.rotation !== undefined && toKf.rotation !== undefined) {
      result.rotation = lerpAngle(fromKf.rotation, toKf.rotation, t);
    } else if (fromKf.rotation !== undefined) {
      result.rotation = fromKf.rotation;
    }

    // 插值位置
    if (fromKf.position && toKf.position) {
      result.position = lerpVector(fromKf.position, toKf.position, t);
    } else if (fromKf.position) {
      result.position = { ...fromKf.position };
    }

    // 插值缩放
    if (fromKf.scale && toKf.scale) {
      result.scale = lerpVector(fromKf.scale, toKf.scale, t);
    } else if (fromKf.scale) {
      result.scale = { ...fromKf.scale };
    }

    return result;
  }

  /**
   * 插值插槽关键帧
   */
  private interpolateSlotKeyframes(
    keyframes: SlotKeyframe[],
    time: number
  ): { attachment?: string; color?: Color } {
    if (keyframes.length === 0) return {};

    // 找到当前时间的前后关键帧
    let fromKf = keyframes[0];
    let toKf = keyframes[0];

    for (let i = 0; i < keyframes.length; i++) {
      if (keyframes[i].time <= time) {
        fromKf = keyframes[i];
        toKf = keyframes[i + 1] || keyframes[i];
      }
    }

    const result: { attachment?: string; color?: Color } = {};

    // 附件不插值，直接使用 fromKf
    if (fromKf.attachment !== undefined) {
      result.attachment = fromKf.attachment;
    }

    // 插值颜色
    if (fromKf.color && toKf.color) {
      const duration = toKf.time - fromKf.time;
      const t = duration > 0 ? (time - fromKf.time) / duration : 0;
      result.color = lerpColor(fromKf.color, toKf.color, t);
    } else if (fromKf.color) {
      result.color = { ...fromKf.color };
    }

    return result;
  }

  /**
   * 更新单个插槽附件
   */
  private updateSingleSlotAttachment(state: SkeletonState, slot: SlotState): void {
    const skin = state.config.skins.find(s => s.id === state.activeSkin);
    if (!skin) return;

    // 清理旧精灵
    if (slot.sprite) {
      state.container.removeChild(slot.sprite);
      slot.sprite.destroy();
      slot.sprite = undefined;
    }

    // 创建新附件
    if (slot.attachment) {
      const attachment = skin.attachments[slot.attachment];
      if (attachment && attachment.type === 'sprite') {
        const sprite = this.createAttachmentSprite(attachment.source);
        if (sprite) {
          if (sprite instanceof PIXI.Sprite) {
            sprite.anchor.set(0.5, 0.5);
          }
          sprite.zIndex = slot.zIndex;
          state.container.addChild(sprite);
          slot.sprite = sprite;
        }
      }
    }
  }

  // ==================== 事件 ====================

  /**
   * 添加事件监听
   */
  onEvent(callback: SkeletonEventCallback): void {
    this.eventCallbacks.add(callback);
  }

  /**
   * 移除事件监听
   */
  offEvent(callback: SkeletonEventCallback): void {
    this.eventCallbacks.delete(callback);
  }

  /**
   * 发射事件
   */
  private emitEvent(event: SkeletonEvent): void {
    this.eventCallbacks.forEach(callback => {
      try {
        callback(event);
      } catch (e) {
        console.error('骨骼事件回调错误:', e);
      }
    });
  }

  // ==================== 查询 ====================

  /**
   * 获取骨骼世界位置
   */
  getBoneWorldPosition(skeletonId: string, boneName: string): Vector2D | undefined {
    const state = this.skeletons.get(skeletonId);
    if (!state) return undefined;

    const bone = Array.from(state.bones.values()).find(b => b.name === boneName || b.id === boneName);
    return bone ? { ...bone.worldPosition } : undefined;
  }

  /**
   * 获取骨骼世界旋转
   */
  getBoneWorldRotation(skeletonId: string, boneName: string): number | undefined {
    const state = this.skeletons.get(skeletonId);
    if (!state) return undefined;

    const bone = Array.from(state.bones.values()).find(b => b.name === boneName || b.id === boneName);
    return bone?.worldRotation;
  }

  /**
   * 获取当前动画名称
   */
  getCurrentAnimation(skeletonId: string): string | undefined {
    const state = this.skeletons.get(skeletonId);
    if (!state || !state.activeAnimation) return undefined;

    const animation = state.config.animations.find(a => a.id === state.activeAnimation);
    return animation?.name;
  }

  /**
   * 获取动画时间
   */
  getAnimationTime(skeletonId: string): number {
    const state = this.skeletons.get(skeletonId);
    return state?.animationTime ?? 0;
  }

  /**
   * 检查动画是否正在播放
   */
  isPlaying(skeletonId: string): boolean {
    const state = this.skeletons.get(skeletonId);
    return state?.isPlaying ?? false;
  }

  // ==================== 位置控制 ====================

  /**
   * 设置骨骼实例位置
   */
  setPosition(id: string, position: Vector2D): void {
    const state = this.skeletons.get(id);
    if (state) {
      state.container.position.set(position.x, position.y);
    }
  }

  /**
   * 设置骨骼实例缩放
   */
  setScale(id: string, scale: Vector2D): void {
    const state = this.skeletons.get(id);
    if (state) {
      state.container.scale.set(scale.x, scale.y);
    }
  }

  /**
   * 设置骨骼实例旋转
   */
  setRotation(id: string, rotation: number): void {
    const state = this.skeletons.get(id);
    if (state) {
      state.container.rotation = degToRad(rotation);
    }
  }

  // ==================== 销毁 ====================

  /**
   * 销毁骨骼系统
   */
  destroy(): void {
    this.skeletons.forEach((_, id) => {
      this.removeSkeleton(id);
    });
    this.skeletons.clear();
    this.eventCallbacks.clear();
    this.textureCache.clear();
  }
}

// ==================== 导出单例 ====================

export const skeletonSystem = new SkeletonSystem();
