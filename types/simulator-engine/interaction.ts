/**
 * 场景描述语言 (SDL) - 交互类型定义
 */

import type { Vector2D } from './base';

// ==================== 触发器类型 ====================

/** 触发器类型 */
export type TriggerType =
  // 指针事件
  | 'click'
  | 'doubleClick'
  | 'rightClick'
  | 'pointerDown'
  | 'pointerUp'
  | 'pointerMove'
  // 拖拽事件
  | 'dragStart'
  | 'drag'
  | 'dragEnd'
  | 'drop'
  // 悬停事件
  | 'hover'
  | 'hoverEnd'
  // 物理事件
  | 'collision'
  | 'collisionEnd'
  | 'collisionActive'
  // 动画事件
  | 'animationStart'
  | 'animationEnd'
  | 'animationLoop'
  | 'timelineMarker'
  // 变量事件
  | 'variableChange'
  // 场景事件
  | 'sceneLoad'
  | 'sceneReady'
  // 定时器
  | 'timer'
  | 'interval'
  // 自定义
  | 'custom';

/** 交互触发器 */
export interface InteractionTrigger {
  type: TriggerType;
  targetId?: string;           // 目标元素 ID，undefined 为全局
  params?: Record<string, unknown>;
}

// ==================== 条件类型 ====================

/** 条件操作符 */
export type ConditionOperator =
  | 'eq'       // 等于
  | 'ne'       // 不等于
  | 'gt'       // 大于
  | 'gte'      // 大于等于
  | 'lt'       // 小于
  | 'lte'      // 小于等于
  | 'contains' // 包含
  | 'in'       // 在数组中
  | 'between'  // 在范围内
  | 'matches'  // 正则匹配
  | 'exists'   // 存在
  | 'truthy'   // 真值
  | 'falsy';   // 假值

/** 条件类型 */
export type ConditionType =
  | 'variable'   // 变量条件
  | 'element'    // 元素属性条件
  | 'physics'    // 物理状态条件
  | 'animation'  // 动画状态条件
  | 'input'      // 输入状态条件
  | 'custom';    // 自定义条件

/** 交互条件 */
export interface InteractionCondition {
  type: ConditionType;
  operator: ConditionOperator;
  left: string;                // 变量名、属性路径或表达式
  right?: unknown;             // 比较值
  negate?: boolean;            // 取反
}

/** 条件组 (AND/OR) */
export interface ConditionGroup {
  logic: 'and' | 'or';
  conditions: (InteractionCondition | ConditionGroup)[];
}

// ==================== 动作类型 ====================

/** 动作类型 */
export type ActionType =
  // 变量操作
  | 'setVariable'
  | 'incrementVariable'
  | 'toggleVariable'
  // 元素操作
  | 'setProperty'
  | 'showElement'
  | 'hideElement'
  | 'toggleElement'
  | 'destroyElement'
  | 'createElement'
  | 'moveElement'
  // 动画操作
  | 'playAnimation'
  | 'stopAnimation'
  | 'pauseAnimation'
  | 'resumeAnimation'
  | 'playTimeline'
  | 'pauseTimeline'
  | 'stopTimeline'
  | 'seekTimeline'
  // 补间动画
  | 'tween'
  // 物理操作
  | 'applyForce'
  | 'applyImpulse'
  | 'setVelocity'
  | 'setAngularVelocity'
  // 粒子操作
  | 'emitParticles'
  | 'startEmitter'
  | 'stopEmitter'
  // 流体操作
  | 'addFluidSource'
  | 'removeFluidSource'
  // 音频操作
  | 'playSound'
  | 'stopSound'
  | 'setVolume'
  // 场景操作
  | 'loadScene'
  | 'resetScene'
  // 事件操作
  | 'triggerEvent'
  | 'dispatchCustom'
  // 评估操作
  | 'evaluateResult'
  | 'checkCheckpoint'
  // 延迟操作
  | 'delay'
  | 'sequence'
  | 'parallel'
  // 条件操作
  | 'if'
  | 'switch'
  // 日志
  | 'log'
  // 自定义
  | 'custom';

/** 交互动作 */
export interface InteractionAction {
  type: ActionType;
  params: Record<string, unknown>;
  delay?: number;              // 延迟执行（毫秒）
  condition?: InteractionCondition | ConditionGroup;
}

// ==================== 具体动作参数 ====================

/** 设置变量参数 */
export interface SetVariableParams {
  name: string;
  value: unknown;
  // 或使用表达式
  expression?: string;
}

/** 设置属性参数 */
export interface SetPropertyParams {
  targetId: string;
  property: string;
  value: unknown;
  animate?: boolean;
  duration?: number;
  easing?: string;
}

/** 播放动画参数 */
export interface PlayAnimationParams {
  targetId: string;
  animationName: string;
  loop?: boolean;
  speed?: number;
}

/** 播放时间线参数 */
export interface PlayTimelineParams {
  timelineId: string;
  from?: number;
  to?: number;
  speed?: number;
}

/** 补间动画参数 */
export interface TweenParams {
  targetId: string;
  property: string;
  from?: unknown;
  to: unknown;
  duration: number;
  easing?: string;
  delay?: number;
}

/** 施加力参数 */
export interface ApplyForceParams {
  targetId: string;
  force: Vector2D;
  point?: Vector2D;
}

/** 发射粒子参数 */
export interface EmitParticlesParams {
  emitterId: string;
  count?: number;
  position?: Vector2D;
}

/** 播放音效参数 */
export interface PlaySoundParams {
  soundId: string;
  volume?: number;
  loop?: boolean;
}

/** 触发事件参数 */
export interface TriggerEventParams {
  eventName: string;
  data?: Record<string, unknown>;
}

/** 条件动作参数 */
export interface IfActionParams {
  condition: InteractionCondition | ConditionGroup;
  then: InteractionAction[];
  else?: InteractionAction[];
}

/** 序列动作参数 */
export interface SequenceParams {
  actions: InteractionAction[];
}

/** 并行动作参数 */
export interface ParallelParams {
  actions: InteractionAction[];
}

// ==================== 交互规则 ====================

/** 交互规则 */
export interface InteractionRule {
  id: string;
  name: string;
  description?: string;
  enabled: boolean;
  trigger: InteractionTrigger;
  conditions?: (InteractionCondition | ConditionGroup)[];
  actions: InteractionAction[];
  // 执行选项
  once?: boolean;              // 只执行一次
  debounce?: number;           // 防抖（毫秒）
  throttle?: number;           // 节流（毫秒）
  priority?: number;           // 优先级
}

// ==================== 交互事件数据 ====================

/** 指针事件数据 */
export interface PointerEventData {
  position: Vector2D;
  globalPosition: Vector2D;
  button: number;
  buttons: number;
  pressure: number;
  targetId?: string;
}

/** 拖拽事件数据 */
export interface DragEventData extends PointerEventData {
  startPosition: Vector2D;
  delta: Vector2D;
  distance: number;
}

/** 碰撞事件数据 */
export interface CollisionEventData {
  bodyA: string;
  bodyB: string;
  contactPoints: Vector2D[];
  normal: Vector2D;
  depth: number;
}

/** 变量变化事件数据 */
export interface VariableChangeEventData {
  name: string;
  oldValue: unknown;
  newValue: unknown;
}

/** 交互事件数据联合类型 */
export type InteractionEventData =
  | PointerEventData
  | DragEventData
  | CollisionEventData
  | VariableChangeEventData
  | Record<string, unknown>;

// ==================== 交互管理器接口 ====================

/** 交互管理器接口 */
export interface IInteractionManager {
  // 规则管理
  addRule(rule: InteractionRule): void;
  removeRule(ruleId: string): void;
  enableRule(ruleId: string): void;
  disableRule(ruleId: string): void;
  getRule(ruleId: string): InteractionRule | undefined;

  // 事件处理
  handleEvent(type: TriggerType, data: InteractionEventData): void;

  // 条件评估
  evaluateCondition(condition: InteractionCondition | ConditionGroup): boolean;

  // 动作执行
  executeAction(action: InteractionAction): Promise<void>;
  executeActions(actions: InteractionAction[]): Promise<void>;

  // 销毁
  destroy(): void;
}
