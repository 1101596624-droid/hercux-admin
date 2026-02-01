/**
 * 场景描述语言 (SDL) - 物理类型定义
 */

import type { Vector2D } from './base';

// ==================== 物理世界配置 ====================

/** 物理世界配置 */
export interface PhysicsWorldConfig {
  gravity: Vector2D;
  velocityIterations?: number;
  positionIterations?: number;
  enableSleeping?: boolean;
  bounds?: {
    min: Vector2D;
    max: Vector2D;
  };
  // 时间步长
  timeStep?: number;
  // 子步数
  substeps?: number;
}

/** 默认物理世界配置 */
export const DEFAULT_PHYSICS_CONFIG: PhysicsWorldConfig = {
  gravity: { x: 0, y: 980 },   // 像素/秒²
  velocityIterations: 6,
  positionIterations: 2,
  enableSleeping: true,
  timeStep: 1000 / 60,
  substeps: 1,
};

// ==================== 碰撞过滤 ====================

/** 碰撞类别 */
export interface CollisionCategory {
  id: string;
  name: string;
  mask: number;
}

/** 碰撞过滤器 */
export interface CollisionFilter {
  category: number;
  mask: number;
  group?: number;
}

/** 预设碰撞类别 */
export const COLLISION_CATEGORIES = {
  DEFAULT: 0x0001,
  STATIC: 0x0002,
  DYNAMIC: 0x0004,
  SENSOR: 0x0008,
  PLAYER: 0x0010,
  ENEMY: 0x0020,
  PROJECTILE: 0x0040,
  PICKUP: 0x0080,
} as const;

// ==================== 物理材质 ====================

/** 物理材质 */
export interface PhysicsMaterial {
  id: string;
  name: string;
  friction: number;            // 0-1
  restitution: number;         // 0-1 (弹性)
  density?: number;
}

/** 预设物理材质 */
export const PHYSICS_MATERIALS: Record<string, PhysicsMaterial> = {
  default: { id: 'default', name: '默认', friction: 0.1, restitution: 0.5 },
  rubber: { id: 'rubber', name: '橡胶', friction: 0.9, restitution: 0.9 },
  ice: { id: 'ice', name: '冰', friction: 0.01, restitution: 0.1 },
  wood: { id: 'wood', name: '木头', friction: 0.4, restitution: 0.3 },
  metal: { id: 'metal', name: '金属', friction: 0.2, restitution: 0.6 },
  stone: { id: 'stone', name: '石头', friction: 0.5, restitution: 0.2 },
  bouncy: { id: 'bouncy', name: '弹力球', friction: 0.1, restitution: 0.95 },
};

// ==================== 物理体状态 ====================

/** 物理体运行时状态 */
export interface PhysicsBodyState {
  id: string;
  position: Vector2D;
  angle: number;
  velocity: Vector2D;
  angularVelocity: number;
  isSleeping: boolean;
  isStatic: boolean;
}

// ==================== 碰撞事件 ====================

/** 碰撞对 */
export interface CollisionPair {
  bodyA: string;
  bodyB: string;
  contacts: ContactPoint[];
  separation: number;
  isActive: boolean;
}

/** 接触点 */
export interface ContactPoint {
  vertex: Vector2D;
  normal: Vector2D;
  depth: number;
}

/** 碰撞事件 */
export interface PhysicsCollisionEvent {
  type: 'collisionStart' | 'collisionActive' | 'collisionEnd';
  pairs: CollisionPair[];
  timestamp: number;
}

// ==================== 射线检测 ====================

/** 射线 */
export interface Ray {
  start: Vector2D;
  end: Vector2D;
}

/** 射线检测结果 */
export interface RaycastResult {
  body: string;
  point: Vector2D;
  normal: Vector2D;
  fraction: number;
}

// ==================== 区域查询 ====================

/** 区域查询类型 */
export type QueryRegionType = 'rectangle' | 'circle' | 'point';

/** 区域查询 */
export interface QueryRegion {
  type: QueryRegionType;
  // 矩形
  min?: Vector2D;
  max?: Vector2D;
  // 圆形
  center?: Vector2D;
  radius?: number;
  // 点
  point?: Vector2D;
}

/** 区域查询结果 */
export interface QueryResult {
  bodies: string[];
}

// ==================== 物理引擎接口 ====================

/** 物理引擎接口 */
export interface IPhysicsEngine {
  // 初始化
  init(config: PhysicsWorldConfig): void;

  // 物理体管理
  addBody(id: string, config: PhysicsBodyConfig): void;
  removeBody(id: string): void;
  getBody(id: string): PhysicsBodyState | undefined;
  getAllBodies(): PhysicsBodyState[];

  // 物理体操作
  setPosition(id: string, position: Vector2D): void;
  setAngle(id: string, angle: number): void;
  setVelocity(id: string, velocity: Vector2D): void;
  setAngularVelocity(id: string, angularVelocity: number): void;
  applyForce(id: string, force: Vector2D, point?: Vector2D): void;
  applyImpulse(id: string, impulse: Vector2D, point?: Vector2D): void;

  // 约束管理
  addConstraint(id: string, config: PhysicsConstraintConfig): void;
  removeConstraint(id: string): void;

  // 查询
  raycast(ray: Ray, filter?: CollisionFilter): RaycastResult[];
  query(region: QueryRegion, filter?: CollisionFilter): QueryResult;

  // 事件
  onCollision(callback: (event: PhysicsCollisionEvent) => void): void;
  offCollision(callback: (event: PhysicsCollisionEvent) => void): void;

  // 更新
  update(deltaTime: number): void;

  // 暂停/恢复
  pause(): void;
  resume(): void;
  isPaused(): boolean;

  // 销毁
  destroy(): void;
}

// ==================== 物理体配置 (从 elements.ts 引用) ====================

import type { PhysicsBodyConfig, PhysicsConstraint } from './elements';

/** 物理约束配置 (别名) */
export type PhysicsConstraintConfig = PhysicsConstraint;

export type { PhysicsBodyConfig };
