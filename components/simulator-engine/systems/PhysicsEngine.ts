/**
 * 物理引擎 - 基于 Matter.js 的 2D 物理模拟
 */

import Matter from 'matter-js';
import type {
  PhysicsWorldConfig,
  PhysicsBodyConfig,
  PhysicsBodyState,
  PhysicsCollisionEvent,
  CollisionPair,
  CollisionFilter,
  Ray,
  RaycastResult,
  QueryRegion,
  QueryResult,
  Vector2D,
  PhysicsConstraint,
} from '@/types/simulator-engine';
import { DEFAULT_PHYSICS_CONFIG, PHYSICS_MATERIALS } from '@/types/simulator-engine/physics';

// ==================== 类型定义 ====================

/** 碰撞事件回调 */
export type CollisionCallback = (event: PhysicsCollisionEvent) => void;

/** 物理体映射 */
interface BodyMapping {
  id: string;
  body: Matter.Body;
  config: PhysicsBodyConfig;
}

/** 约束映射 */
interface ConstraintMapping {
  id: string;
  constraint: Matter.Constraint;
  config: PhysicsConstraint;
}

// ==================== 物理引擎类 ====================

export class PhysicsEngine {
  private engine: Matter.Engine | null = null;
  private world: Matter.World | null = null;
  private bodies: Map<string, BodyMapping> = new Map();
  private constraints: Map<string, ConstraintMapping> = new Map();
  private collisionCallbacks: Set<CollisionCallback> = new Set();
  private config: PhysicsWorldConfig = DEFAULT_PHYSICS_CONFIG;
  private paused: boolean = false;
  private accumulator: number = 0;

  constructor() {}

  // ==================== 初始化 ====================

  /**
   * 初始化物理引擎
   */
  init(config: Partial<PhysicsWorldConfig> = {}): void {
    this.config = { ...DEFAULT_PHYSICS_CONFIG, ...config };

    // 创建引擎
    this.engine = Matter.Engine.create({
      enableSleeping: this.config.enableSleeping,
    });

    this.world = this.engine.world;

    // 设置重力
    this.world.gravity.x = this.config.gravity.x / 1000; // 转换为 Matter.js 单位
    this.world.gravity.y = this.config.gravity.y / 1000;

    // 设置边界
    if (this.config.bounds) {
      this.createBounds(this.config.bounds.min, this.config.bounds.max);
    }

    // 设置碰撞事件监听
    this.setupCollisionEvents();
  }

  /**
   * 创建边界墙
   */
  private createBounds(min: Vector2D, max: Vector2D): void {
    if (!this.world) return;

    const thickness = 50;
    const width = max.x - min.x;
    const height = max.y - min.y;

    const walls = [
      // 底部
      Matter.Bodies.rectangle(
        min.x + width / 2,
        max.y + thickness / 2,
        width + thickness * 2,
        thickness,
        { isStatic: true, label: 'wall_bottom' }
      ),
      // 顶部
      Matter.Bodies.rectangle(
        min.x + width / 2,
        min.y - thickness / 2,
        width + thickness * 2,
        thickness,
        { isStatic: true, label: 'wall_top' }
      ),
      // 左侧
      Matter.Bodies.rectangle(
        min.x - thickness / 2,
        min.y + height / 2,
        thickness,
        height,
        { isStatic: true, label: 'wall_left' }
      ),
      // 右侧
      Matter.Bodies.rectangle(
        max.x + thickness / 2,
        min.y + height / 2,
        thickness,
        height,
        { isStatic: true, label: 'wall_right' }
      ),
    ];

    Matter.Composite.add(this.world, walls);
  }

  /**
   * 设置碰撞事件监听
   */
  private setupCollisionEvents(): void {
    if (!this.engine) return;

    Matter.Events.on(this.engine, 'collisionStart', (event) => {
      this.emitCollisionEvent('collisionStart', event.pairs);
    });

    Matter.Events.on(this.engine, 'collisionActive', (event) => {
      this.emitCollisionEvent('collisionActive', event.pairs);
    });

    Matter.Events.on(this.engine, 'collisionEnd', (event) => {
      this.emitCollisionEvent('collisionEnd', event.pairs);
    });
  }

  /**
   * 发射碰撞事件
   */
  private emitCollisionEvent(type: 'collisionStart' | 'collisionActive' | 'collisionEnd', pairs: Matter.Pair[]): void {
    const collisionPairs: CollisionPair[] = pairs.map(pair => ({
      bodyA: this.getBodyId(pair.bodyA) || pair.bodyA.label,
      bodyB: this.getBodyId(pair.bodyB) || pair.bodyB.label,
      contacts: pair.contacts?.map((contact: Matter.Contact) => ({
        vertex: { x: contact.vertex.x, y: contact.vertex.y },
        normal: { x: pair.collision.normal.x, y: pair.collision.normal.y },
        depth: pair.collision.depth,
      })) || [],
      separation: pair.separation,
      isActive: pair.isActive,
    }));

    const event: PhysicsCollisionEvent = {
      type,
      pairs: collisionPairs,
      timestamp: Date.now(),
    };

    this.collisionCallbacks.forEach(callback => {
      try {
        callback(event);
      } catch (e) {
        console.error('碰撞回调错误:', e);
      }
    });
  }

  /**
   * 根据 Matter.Body 获取自定义 ID
   */
  private getBodyId(body: Matter.Body): string | undefined {
    for (const [id, mapping] of this.bodies) {
      if (mapping.body === body) {
        return id;
      }
    }
    return undefined;
  }

  // ==================== 物理体管理 ====================

  /**
   * 添加物理体
   */
  addBody(id: string, config: PhysicsBodyConfig): void {
    if (!this.world) {
      console.warn('物理引擎未初始化');
      return;
    }

    if (this.bodies.has(id)) {
      console.warn(`物理体已存在: ${id}`);
      return;
    }

    const body = this.createMatterBody(id, config);
    Matter.Composite.add(this.world, body);

    this.bodies.set(id, { id, body, config });

    // 添加约束
    if (config.constraints) {
      config.constraints.forEach(constraint => {
        this.addConstraint(constraint.id, constraint, id);
      });
    }
  }

  /**
   * 创建 Matter.js 物理体
   */
  private createMatterBody(id: string, config: PhysicsBodyConfig): Matter.Body {
    const { shape, bodyType } = config;
    const isStatic = bodyType === 'static';

    // 获取材质属性
    const friction = config.friction ?? PHYSICS_MATERIALS.default.friction;
    const restitution = config.restitution ?? PHYSICS_MATERIALS.default.restitution;

    const bodyOptions = {
      label: id,
      isStatic,
      friction,
      restitution,
      frictionAir: config.linearDamping ?? 0.01,
      angle: 0,
      collisionFilter: {
        category: config.collisionGroup ?? 0x0001,
        mask: config.collisionMask ?? 0xFFFFFFFF,
      },
      isSensor: config.isSensor ?? false,
      mass: config.mass,
    };

    let body: Matter.Body;

    switch (shape.type) {
      case 'circle':
        body = Matter.Bodies.circle(
          shape.offset?.x ?? 0,
          shape.offset?.y ?? 0,
          shape.radius ?? 25,
          bodyOptions
        );
        break;

      case 'rectangle':
        body = Matter.Bodies.rectangle(
          shape.offset?.x ?? 0,
          shape.offset?.y ?? 0,
          shape.width ?? 50,
          shape.height ?? 50,
          bodyOptions
        );
        break;

      case 'polygon':
        if (shape.vertices && shape.vertices.length >= 3) {
          const vertices = shape.vertices.map(v => ({ x: v.x, y: v.y }));
          body = Matter.Bodies.fromVertices(
            shape.offset?.x ?? 0,
            shape.offset?.y ?? 0,
            [vertices],
            bodyOptions
          );
        } else {
          // 默认创建六边形
          body = Matter.Bodies.polygon(
            shape.offset?.x ?? 0,
            shape.offset?.y ?? 0,
            6,
            shape.radius ?? 25,
            bodyOptions
          );
        }
        break;

      default:
        body = Matter.Bodies.circle(
          shape.offset?.x ?? 0,
          shape.offset?.y ?? 0,
          25,
          bodyOptions
        );
    }

    // 设置初始速度
    if (config.linearVelocity) {
      Matter.Body.setVelocity(body, {
        x: config.linearVelocity.x / 60, // 转换为每帧速度
        y: config.linearVelocity.y / 60,
      });
    }

    if (config.angularVelocity !== undefined) {
      Matter.Body.setAngularVelocity(body, config.angularVelocity);
    }

    return body;
  }

  /**
   * 移除物理体
   */
  removeBody(id: string): void {
    const mapping = this.bodies.get(id);
    if (!mapping || !this.world) return;

    Matter.Composite.remove(this.world, mapping.body);
    this.bodies.delete(id);
  }

  /**
   * 获取物理体状态
   */
  getBody(id: string): PhysicsBodyState | undefined {
    const mapping = this.bodies.get(id);
    if (!mapping) return undefined;

    const { body, config } = mapping;
    return {
      id,
      position: { x: body.position.x, y: body.position.y },
      angle: body.angle,
      velocity: { x: body.velocity.x * 60, y: body.velocity.y * 60 }, // 转换为每秒速度
      angularVelocity: body.angularVelocity,
      isSleeping: body.isSleeping,
      isStatic: body.isStatic,
    };
  }

  /**
   * 获取所有物理体状态
   */
  getAllBodies(): PhysicsBodyState[] {
    const states: PhysicsBodyState[] = [];
    this.bodies.forEach((_, id) => {
      const state = this.getBody(id);
      if (state) states.push(state);
    });
    return states;
  }

  // ==================== 物理体操作 ====================

  /**
   * 设置位置
   */
  setPosition(id: string, position: Vector2D): void {
    const mapping = this.bodies.get(id);
    if (!mapping) return;

    Matter.Body.setPosition(mapping.body, position);
  }

  /**
   * 设置角度
   */
  setAngle(id: string, angle: number): void {
    const mapping = this.bodies.get(id);
    if (!mapping) return;

    Matter.Body.setAngle(mapping.body, angle);
  }

  /**
   * 设置速度
   */
  setVelocity(id: string, velocity: Vector2D): void {
    const mapping = this.bodies.get(id);
    if (!mapping) return;

    Matter.Body.setVelocity(mapping.body, {
      x: velocity.x / 60,
      y: velocity.y / 60,
    });
  }

  /**
   * 设置角速度
   */
  setAngularVelocity(id: string, angularVelocity: number): void {
    const mapping = this.bodies.get(id);
    if (!mapping) return;

    Matter.Body.setAngularVelocity(mapping.body, angularVelocity);
  }

  /**
   * 施加力
   */
  applyForce(id: string, force: Vector2D, point?: Vector2D): void {
    const mapping = this.bodies.get(id);
    if (!mapping) return;

    const applyPoint = point ?? mapping.body.position;
    Matter.Body.applyForce(mapping.body, applyPoint, {
      x: force.x / 1000000, // 转换为 Matter.js 单位
      y: force.y / 1000000,
    });
  }

  /**
   * 施加冲量
   */
  applyImpulse(id: string, impulse: Vector2D, point?: Vector2D): void {
    const mapping = this.bodies.get(id);
    if (!mapping) return;

    // Matter.js 没有直接的冲量方法，使用速度变化模拟
    const mass = mapping.body.mass;
    const velocityChange = {
      x: impulse.x / mass / 60,
      y: impulse.y / mass / 60,
    };

    Matter.Body.setVelocity(mapping.body, {
      x: mapping.body.velocity.x + velocityChange.x,
      y: mapping.body.velocity.y + velocityChange.y,
    });
  }

  // ==================== 约束管理 ====================

  /**
   * 添加约束
   * @param id 约束 ID
   * @param config 约束配置
   * @param sourceBodyId 源物理体 ID (约束的 bodyA)
   */
  addConstraint(id: string, config: PhysicsConstraint, sourceBodyId?: string): void {
    if (!this.world) return;

    if (this.constraints.has(id)) {
      console.warn(`约束已存在: ${id}`);
      return;
    }

    const constraint = this.createMatterConstraint(config, sourceBodyId);
    if (!constraint) return;

    Matter.Composite.add(this.world, constraint);
    this.constraints.set(id, { id, constraint, config });
  }

  /**
   * 创建 Matter.js 约束
   */
  private createMatterConstraint(config: PhysicsConstraint, sourceBodyId?: string): Matter.Constraint | null {
    // sourceBodyId 是约束所属的物理体 (bodyA)
    // config.targetBodyId 是约束连接的目标物理体 (bodyB)
    const bodyAMapping = sourceBodyId ? this.bodies.get(sourceBodyId) : null;
    const bodyBMapping = config.targetBodyId ? this.bodies.get(config.targetBodyId) : null;

    const options: Matter.IConstraintDefinition = {
      label: config.id,
      stiffness: config.stiffness ?? 1,
      damping: config.damping ?? 0,
      length: config.length,
    };

    if (bodyAMapping) {
      options.bodyA = bodyAMapping.body;
      if (config.anchorA) {
        options.pointA = config.anchorA;
      }
    } else if (config.anchorA) {
      // 如果没有 bodyA，anchorA 作为世界坐标点
      options.pointA = config.anchorA;
    }

    if (bodyBMapping) {
      options.bodyB = bodyBMapping.body;
      if (config.anchorB) {
        options.pointB = config.anchorB;
      }
    } else if (config.anchorB) {
      options.pointB = config.anchorB;
    }

    return Matter.Constraint.create(options);
  }

  /**
   * 移除约束
   */
  removeConstraint(id: string): void {
    const mapping = this.constraints.get(id);
    if (!mapping || !this.world) return;

    Matter.Composite.remove(this.world, mapping.constraint);
    this.constraints.delete(id);
  }

  // ==================== 查询 ====================

  /**
   * 射线检测
   */
  raycast(ray: Ray, filter?: CollisionFilter): RaycastResult[] {
    if (!this.engine) return [];

    const allBodies = Matter.Composite.allBodies(this.engine.world);
    const results: RaycastResult[] = [];

    // 简单的射线检测实现
    const rayVector = {
      x: ray.end.x - ray.start.x,
      y: ray.end.y - ray.start.y,
    };
    const rayLength = Math.sqrt(rayVector.x * rayVector.x + rayVector.y * rayVector.y);

    allBodies.forEach(body => {
      // 检查碰撞过滤
      if (filter) {
        const bodyCategory = body.collisionFilter?.category ?? 0x0001;
        const bodyMask = body.collisionFilter?.mask ?? 0xFFFFFFFF;
        if ((bodyCategory & filter.mask) === 0) return;
        if ((filter.category & bodyMask) === 0) return;
      }

      // 简单的边界框检测
      const bounds = body.bounds;
      if (this.lineIntersectsRect(ray.start, ray.end, bounds.min, bounds.max)) {
        const bodyId = this.getBodyId(body) || body.label;
        results.push({
          body: bodyId,
          point: body.position, // 简化：使用物体中心
          normal: { x: 0, y: -1 },
          fraction: 0.5,
        });
      }
    });

    return results;
  }

  /**
   * 线段与矩形相交检测
   */
  private lineIntersectsRect(
    start: Vector2D,
    end: Vector2D,
    min: Matter.Vector,
    max: Matter.Vector
  ): boolean {
    // 简化的 AABB 检测
    const lineMinX = Math.min(start.x, end.x);
    const lineMaxX = Math.max(start.x, end.x);
    const lineMinY = Math.min(start.y, end.y);
    const lineMaxY = Math.max(start.y, end.y);

    return !(lineMaxX < min.x || lineMinX > max.x || lineMaxY < min.y || lineMinY > max.y);
  }

  /**
   * 区域查询
   */
  query(region: QueryRegion, filter?: CollisionFilter): QueryResult {
    if (!this.engine) return { bodies: [] };

    const allBodies = Matter.Composite.allBodies(this.engine.world);
    const results: string[] = [];

    allBodies.forEach(body => {
      // 检查碰撞过滤
      if (filter) {
        const bodyCategory = body.collisionFilter?.category ?? 0x0001;
        const bodyMask = body.collisionFilter?.mask ?? 0xFFFFFFFF;
        if ((bodyCategory & filter.mask) === 0) return;
        if ((filter.category & bodyMask) === 0) return;
      }

      let inRegion = false;

      switch (region.type) {
        case 'point':
          if (region.point) {
            inRegion = Matter.Bounds.contains(body.bounds, region.point);
          }
          break;

        case 'rectangle':
          if (region.min && region.max) {
            inRegion = Matter.Bounds.overlaps(body.bounds, {
              min: region.min,
              max: region.max,
            });
          }
          break;

        case 'circle':
          if (region.center && region.radius) {
            const dx = body.position.x - region.center.x;
            const dy = body.position.y - region.center.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            inRegion = distance <= region.radius;
          }
          break;
      }

      if (inRegion) {
        const bodyId = this.getBodyId(body) || body.label;
        results.push(bodyId);
      }
    });

    return { bodies: results };
  }

  // ==================== 事件 ====================

  /**
   * 添加碰撞事件监听
   */
  onCollision(callback: CollisionCallback): void {
    this.collisionCallbacks.add(callback);
  }

  /**
   * 移除碰撞事件监听
   */
  offCollision(callback: CollisionCallback): void {
    this.collisionCallbacks.delete(callback);
  }

  // ==================== 更新 ====================

  /**
   * 更新物理模拟
   */
  update(deltaTime: number): void {
    if (!this.engine || this.paused) return;

    const timeStep = this.config.timeStep ?? 1000 / 60;
    const substeps = this.config.substeps ?? 1;

    // 使用固定时间步长
    this.accumulator += deltaTime;

    while (this.accumulator >= timeStep) {
      for (let i = 0; i < substeps; i++) {
        Matter.Engine.update(this.engine, timeStep / substeps);
      }
      this.accumulator -= timeStep;
    }
  }

  // ==================== 控制 ====================

  /**
   * 暂停物理模拟
   */
  pause(): void {
    this.paused = true;
  }

  /**
   * 恢复物理模拟
   */
  resume(): void {
    this.paused = false;
  }

  /**
   * 检查是否暂停
   */
  isPaused(): boolean {
    return this.paused;
  }

  // ==================== 销毁 ====================

  /**
   * 销毁物理引擎
   */
  destroy(): void {
    if (this.engine) {
      Matter.Events.off(this.engine, 'collisionStart', () => {});
      Matter.Events.off(this.engine, 'collisionActive', () => {});
      Matter.Events.off(this.engine, 'collisionEnd', () => {});
      Matter.Engine.clear(this.engine);
      this.engine = null;
    }

    this.world = null;
    this.bodies.clear();
    this.constraints.clear();
    this.collisionCallbacks.clear();
    this.accumulator = 0;
    this.paused = false;
  }
}

// ==================== 导出单例 ====================

export const physicsEngine = new PhysicsEngine();
