/**
 * 粒子系统 - 基于 PixiJS 的粒子效果
 */

import * as PIXI from 'pixi.js';
import type {
  ParticleEmitterConfig,
  Vector2D,
  Color,
  ColorRange,
  NumberRange,
  BlendMode,
} from '@/types/simulator-engine';

// ==================== 类型定义 ====================

/** 单个粒子 */
interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  maxLife: number;
  size: number;
  startSize: number;
  endSize: number;
  rotation: number;
  rotationSpeed: number;
  color: Color;
  startColor: Color;
  endColor: Color;
  alpha: number;
  sprite: PIXI.Sprite | PIXI.Graphics;
}

/** 发射器状态 */
interface EmitterState {
  id: string;
  config: ParticleEmitterConfig;
  container: PIXI.Container;
  particles: Particle[];
  emissionAccumulator: number;
  elapsedTime: number;
  isEmitting: boolean;
  isPaused: boolean;
}

// ==================== 工具函数 ====================

/** 在范围内随机取值 */
function randomInRange(range: NumberRange): number {
  return range.min + Math.random() * (range.max - range.min);
}

/** 线性插值 */
function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
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

/** 从 ColorRange 获取随机颜色 */
function getColorFromRange(colorOrRange: Color | ColorRange): Color {
  if ('start' in colorOrRange && 'end' in colorOrRange) {
    return lerpColor(colorOrRange.start, colorOrRange.end, Math.random());
  }
  return colorOrRange as Color;
}

/** 颜色转换为十六进制 */
function colorToHex(color: Color): number {
  return (color.r << 16) + (color.g << 8) + color.b;
}

/** 角度转弧度 */
function degToRad(deg: number): number {
  return deg * (Math.PI / 180);
}

// ==================== 粒子系统类 ====================

export class ParticleSystem {
  private emitters: Map<string, EmitterState> = new Map();
  private defaultTexture: PIXI.Texture | null = null;

  constructor() {
    // 创建默认粒子纹理 (白色圆形)
    this.createDefaultTexture();
  }

  /**
   * 创建默认粒子纹理
   */
  private createDefaultTexture(): void {
    const graphics = new PIXI.Graphics();
    graphics.fill({ color: 0xffffff });
    graphics.circle(16, 16, 16);
    graphics.fill();

    // 注意：在实际使用中，需要在 PixiJS 应用初始化后创建纹理
    // 这里先设置为 null，在添加发射器时检查
  }

  /**
   * 创建发射器
   */
  createEmitter(
    id: string,
    config: ParticleEmitterConfig,
    parentContainer: PIXI.Container
  ): void {
    if (this.emitters.has(id)) {
      console.warn(`粒子发射器已存在: ${id}`);
      return;
    }

    const container = new PIXI.Container();
    container.sortableChildren = true;
    parentContainer.addChild(container);

    const state: EmitterState = {
      id,
      config,
      container,
      particles: [],
      emissionAccumulator: 0,
      elapsedTime: 0,
      isEmitting: config.autoStart ?? true,
      isPaused: false,
    };

    this.emitters.set(id, state);
  }

  /**
   * 移除发射器
   */
  removeEmitter(id: string): void {
    const state = this.emitters.get(id);
    if (!state) return;

    // 清理所有粒子
    state.particles.forEach(p => {
      state.container.removeChild(p.sprite);
      p.sprite.destroy();
    });

    // 移除容器
    if (state.container.parent) {
      state.container.parent.removeChild(state.container);
    }
    state.container.destroy();

    this.emitters.delete(id);
  }

  /**
   * 开始发射
   */
  startEmitter(id: string): void {
    const state = this.emitters.get(id);
    if (state) {
      state.isEmitting = true;
      state.elapsedTime = 0;
    }
  }

  /**
   * 停止发射
   */
  stopEmitter(id: string): void {
    const state = this.emitters.get(id);
    if (state) {
      state.isEmitting = false;
    }
  }

  /**
   * 暂停发射器
   */
  pauseEmitter(id: string): void {
    const state = this.emitters.get(id);
    if (state) {
      state.isPaused = true;
    }
  }

  /**
   * 恢复发射器
   */
  resumeEmitter(id: string): void {
    const state = this.emitters.get(id);
    if (state) {
      state.isPaused = false;
    }
  }

  /**
   * 设置发射器位置
   */
  setEmitterPosition(id: string, position: Vector2D): void {
    const state = this.emitters.get(id);
    if (state) {
      state.container.position.set(position.x, position.y);
    }
  }

  /**
   * 立即发射一批粒子
   */
  emit(id: string, count: number): void {
    const state = this.emitters.get(id);
    if (!state) return;

    for (let i = 0; i < count; i++) {
      this.spawnParticle(state);
    }
  }

  /**
   * 更新所有发射器
   */
  update(deltaTime: number): void {
    const dt = deltaTime / 1000; // 转换为秒

    this.emitters.forEach(state => {
      if (state.isPaused) return;

      // 更新发射
      if (state.isEmitting) {
        state.elapsedTime += deltaTime;

        // 检查持续时间
        if (state.config.duration !== undefined && state.elapsedTime >= state.config.duration) {
          state.isEmitting = false;
        } else {
          // 发射新粒子
          state.emissionAccumulator += state.config.emissionRate * dt;
          while (state.emissionAccumulator >= 1 && state.particles.length < state.config.maxParticles) {
            this.spawnParticle(state);
            state.emissionAccumulator -= 1;
          }
        }
      }

      // 更新现有粒子
      this.updateParticles(state, dt);
    });
  }

  /**
   * 生成单个粒子
   */
  private spawnParticle(state: EmitterState): void {
    const config = state.config;

    // 计算发射位置
    let spawnX = 0;
    let spawnY = 0;

    switch (config.emitterShape) {
      case 'point':
        spawnX = 0;
        spawnY = 0;
        break;
      case 'rectangle':
        spawnX = (Math.random() - 0.5) * config.emitterSize.x;
        spawnY = (Math.random() - 0.5) * config.emitterSize.y;
        break;
      case 'circle':
        const angle = Math.random() * Math.PI * 2;
        const radius = Math.random() * config.emitterSize.x / 2;
        spawnX = Math.cos(angle) * radius;
        spawnY = Math.sin(angle) * radius;
        break;
      case 'ring':
        const ringAngle = Math.random() * Math.PI * 2;
        spawnX = Math.cos(ringAngle) * config.emitterSize.x / 2;
        spawnY = Math.sin(ringAngle) * config.emitterSize.y / 2;
        break;
    }

    // 计算发射角度和速度
    const emitAngle = config.emitterAngle
      ? degToRad(randomInRange(config.emitterAngle))
      : -Math.PI / 2; // 默认向上
    const speed = randomInRange(config.startSpeed);

    // 获取颜色
    const startColor = getColorFromRange(config.startColor);
    const endColor = config.endColor
      ? getColorFromRange(config.endColor)
      : startColor;

    // 获取大小
    const startSize = randomInRange(config.startSize);
    const endSize = config.endSize
      ? randomInRange(config.endSize)
      : startSize;

    // 创建粒子精灵
    const sprite = new PIXI.Graphics();
    sprite.fill({ color: colorToHex(startColor) });
    sprite.circle(0, 0, startSize / 2);
    sprite.fill();

    sprite.position.set(spawnX, spawnY);
    sprite.alpha = startColor.a;

    state.container.addChild(sprite);

    // 创建粒子对象
    const particle: Particle = {
      x: spawnX,
      y: spawnY,
      vx: Math.cos(emitAngle) * speed,
      vy: Math.sin(emitAngle) * speed,
      life: randomInRange(config.lifetime),
      maxLife: 0,
      size: startSize,
      startSize,
      endSize,
      rotation: randomInRange(config.startRotation),
      rotationSpeed: randomInRange(config.rotationSpeed),
      color: { ...startColor },
      startColor,
      endColor,
      alpha: startColor.a,
      sprite,
    };
    particle.maxLife = particle.life;

    state.particles.push(particle);
  }

  /**
   * 更新粒子
   */
  private updateParticles(state: EmitterState, dt: number): void {
    const config = state.config;
    const gravity = config.gravity;

    for (let i = state.particles.length - 1; i >= 0; i--) {
      const p = state.particles[i];

      // 更新生命周期
      p.life -= dt * 1000;

      if (p.life <= 0) {
        // 移除死亡粒子
        state.container.removeChild(p.sprite);
        p.sprite.destroy();
        state.particles.splice(i, 1);
        continue;
      }

      // 计算生命周期进度 (0 = 刚出生, 1 = 即将死亡)
      const lifeProgress = 1 - (p.life / p.maxLife);

      // 应用重力
      p.vx += gravity.x * dt;
      p.vy += gravity.y * dt;

      // 应用径向加速度
      if (config.radialAcceleration) {
        const dist = Math.sqrt(p.x * p.x + p.y * p.y);
        if (dist > 0) {
          const radialAcc = randomInRange(config.radialAcceleration);
          p.vx += (p.x / dist) * radialAcc * dt;
          p.vy += (p.y / dist) * radialAcc * dt;
        }
      }

      // 应用切向加速度
      if (config.tangentialAcceleration) {
        const dist = Math.sqrt(p.x * p.x + p.y * p.y);
        if (dist > 0) {
          const tangAcc = randomInRange(config.tangentialAcceleration);
          p.vx += (-p.y / dist) * tangAcc * dt;
          p.vy += (p.x / dist) * tangAcc * dt;
        }
      }

      // 更新位置
      p.x += p.vx * dt;
      p.y += p.vy * dt;

      // 更新旋转
      p.rotation += p.rotationSpeed * dt;

      // 插值大小
      p.size = lerp(p.startSize, p.endSize, lifeProgress);

      // 插值颜色
      p.color = lerpColor(p.startColor, p.endColor, lifeProgress);
      p.alpha = p.color.a * (1 - lifeProgress * 0.5); // 逐渐淡出

      // 更新精灵
      p.sprite.position.set(p.x, p.y);
      p.sprite.rotation = degToRad(p.rotation);
      p.sprite.scale.set(p.size / p.startSize);
      p.sprite.alpha = p.alpha;

      // 更新颜色 (重绘)
      if (p.sprite instanceof PIXI.Graphics) {
        p.sprite.clear();
        p.sprite.fill({ color: colorToHex(p.color) });
        p.sprite.circle(0, 0, p.startSize / 2);
        p.sprite.fill();
      }
    }
  }

  /**
   * 获取发射器粒子数量
   */
  getParticleCount(id: string): number {
    const state = this.emitters.get(id);
    return state ? state.particles.length : 0;
  }

  /**
   * 获取所有发射器的总粒子数
   */
  getTotalParticleCount(): number {
    let total = 0;
    this.emitters.forEach(state => {
      total += state.particles.length;
    });
    return total;
  }

  /**
   * 清除所有粒子
   */
  clearParticles(id?: string): void {
    if (id) {
      const state = this.emitters.get(id);
      if (state) {
        state.particles.forEach(p => {
          state.container.removeChild(p.sprite);
          p.sprite.destroy();
        });
        state.particles = [];
      }
    } else {
      this.emitters.forEach(state => {
        state.particles.forEach(p => {
          state.container.removeChild(p.sprite);
          p.sprite.destroy();
        });
        state.particles = [];
      });
    }
  }

  /**
   * 销毁粒子系统
   */
  destroy(): void {
    this.emitters.forEach((_, id) => {
      this.removeEmitter(id);
    });
    this.emitters.clear();
  }
}

// ==================== 预设粒子配置 ====================

/** 火焰效果配置 */
export const FIRE_EMITTER_CONFIG: Partial<ParticleEmitterConfig> = {
  emissionRate: 50,
  maxParticles: 200,
  emitterShape: 'rectangle',
  emitterSize: { x: 30, y: 5 },
  emitterAngle: { min: -100, max: -80 },
  lifetime: { min: 500, max: 1000 },
  startColor: { r: 255, g: 200, b: 50, a: 1 },
  endColor: { r: 255, g: 50, b: 0, a: 0 },
  startSize: { min: 20, max: 40 },
  endSize: { min: 5, max: 10 },
  startRotation: { min: 0, max: 360 },
  rotationSpeed: { min: -50, max: 50 },
  startSpeed: { min: 50, max: 100 },
  gravity: { x: 0, y: -50 },
  blendMode: 'add',
  autoStart: true,
};

/** 烟雾效果配置 */
export const SMOKE_EMITTER_CONFIG: Partial<ParticleEmitterConfig> = {
  emissionRate: 20,
  maxParticles: 100,
  emitterShape: 'circle',
  emitterSize: { x: 20, y: 20 },
  emitterAngle: { min: -110, max: -70 },
  lifetime: { min: 1500, max: 3000 },
  startColor: { r: 100, g: 100, b: 100, a: 0.5 },
  endColor: { r: 150, g: 150, b: 150, a: 0 },
  startSize: { min: 30, max: 50 },
  endSize: { min: 80, max: 120 },
  startRotation: { min: 0, max: 360 },
  rotationSpeed: { min: -20, max: 20 },
  startSpeed: { min: 20, max: 40 },
  gravity: { x: 0, y: -20 },
  blendMode: 'normal',
  autoStart: true,
};

/** 星星/闪光效果配置 */
export const SPARKLE_EMITTER_CONFIG: Partial<ParticleEmitterConfig> = {
  emissionRate: 30,
  maxParticles: 150,
  emitterShape: 'circle',
  emitterSize: { x: 100, y: 100 },
  lifetime: { min: 300, max: 800 },
  startColor: { r: 255, g: 255, b: 200, a: 1 },
  endColor: { r: 255, g: 255, b: 255, a: 0 },
  startSize: { min: 5, max: 15 },
  endSize: { min: 0, max: 2 },
  startRotation: { min: 0, max: 360 },
  rotationSpeed: { min: -100, max: 100 },
  startSpeed: { min: 10, max: 30 },
  gravity: { x: 0, y: 20 },
  blendMode: 'add',
  autoStart: true,
};

/** 爆炸效果配置 */
export const EXPLOSION_EMITTER_CONFIG: Partial<ParticleEmitterConfig> = {
  emissionRate: 0, // 使用 emit() 手动触发
  maxParticles: 100,
  emitterShape: 'point',
  emitterSize: { x: 0, y: 0 },
  emitterAngle: { min: 0, max: 360 },
  lifetime: { min: 500, max: 1000 },
  startColor: { r: 255, g: 200, b: 100, a: 1 },
  endColor: { r: 255, g: 100, b: 50, a: 0 },
  startSize: { min: 10, max: 30 },
  endSize: { min: 2, max: 5 },
  startRotation: { min: 0, max: 360 },
  rotationSpeed: { min: -200, max: 200 },
  startSpeed: { min: 100, max: 300 },
  gravity: { x: 0, y: 200 },
  blendMode: 'add',
  autoStart: false,
};

/** 蓝紫色氛围粒子效果配置 - HERCU 统一风格 */
export const BLUE_PURPLE_AMBIENT_CONFIG: Partial<ParticleEmitterConfig> = {
  emissionRate: 15,
  maxParticles: 80,
  emitterShape: 'rectangle',
  emitterSize: { x: 800, y: 500 },
  emitterAngle: { min: -120, max: -60 },
  lifetime: { min: 2000, max: 4000 },
  startColor: { r: 99, g: 102, b: 241, a: 0.6 },  // 蓝紫色 #6366f1
  endColor: { r: 168, g: 85, b: 247, a: 0 },      // 紫色 #a855f7
  startSize: { min: 3, max: 8 },
  endSize: { min: 1, max: 3 },
  startRotation: { min: 0, max: 360 },
  rotationSpeed: { min: -30, max: 30 },
  startSpeed: { min: 15, max: 35 },
  gravity: { x: 0, y: -10 },
  blendMode: 'add',
  autoStart: true,
};

/** 蓝紫色闪烁粒子效果配置 - 用于交互反馈 */
export const BLUE_PURPLE_SPARKLE_CONFIG: Partial<ParticleEmitterConfig> = {
  emissionRate: 25,
  maxParticles: 100,
  emitterShape: 'circle',
  emitterSize: { x: 60, y: 60 },
  emitterAngle: { min: 0, max: 360 },
  lifetime: { min: 400, max: 800 },
  startColor: { r: 139, g: 92, b: 246, a: 1 },   // 紫色 #8b5cf6
  endColor: { r: 59, g: 130, b: 246, a: 0 },     // 蓝色 #3b82f6
  startSize: { min: 4, max: 10 },
  endSize: { min: 0, max: 2 },
  startRotation: { min: 0, max: 360 },
  rotationSpeed: { min: -100, max: 100 },
  startSpeed: { min: 30, max: 80 },
  gravity: { x: 0, y: 30 },
  blendMode: 'add',
  autoStart: true,
};

/** 蓝紫色上升粒子效果配置 - 用于内容切换 */
export const BLUE_PURPLE_RISING_CONFIG: Partial<ParticleEmitterConfig> = {
  emissionRate: 20,
  maxParticles: 60,
  emitterShape: 'rectangle',
  emitterSize: { x: 400, y: 10 },
  emitterAngle: { min: -100, max: -80 },
  lifetime: { min: 1500, max: 2500 },
  startColor: { r: 79, g: 70, b: 229, a: 0.8 },  // 靛蓝色 #4f46e5
  endColor: { r: 192, g: 132, b: 252, a: 0 },    // 浅紫色 #c084fc
  startSize: { min: 5, max: 12 },
  endSize: { min: 2, max: 4 },
  startRotation: { min: 0, max: 360 },
  rotationSpeed: { min: -50, max: 50 },
  startSpeed: { min: 40, max: 70 },
  gravity: { x: 0, y: -30 },
  blendMode: 'add',
  autoStart: false,
};

// ==================== 导出单例 ====================

export const particleSystem = new ParticleSystem();
