/**
 * 模拟引擎 - 导出
 */

// 主渲染器
export { SceneRenderer } from './SceneRenderer';
export { default as SceneRendererDefault } from './SceneRenderer';

// 渲染器
export { PixiRenderer } from './renderers/PixiRenderer';
export { ThreeRenderer } from './renderers/ThreeRenderer';
export { CustomRenderer } from './CustomRenderer';
export { HybridRenderer } from './HybridRenderer';
export type { SimulatorMode, SimulatorData, VariableConfig } from './HybridRenderer';

// 系统
export {
  AnimationController,
  ManualAnimationController,
  animationController,
} from './systems/AnimationController';
export type {
  AnimationState,
  AnimationEventType,
  AnimationEventListener,
  PropertyUpdateCallback,
} from './systems/AnimationController';

export {
  InteractionManager,
  interactionManager,
} from './systems/InteractionManager';
export type {
  InteractionContext,
} from './systems/InteractionManager';

export {
  PhysicsEngine,
  physicsEngine,
} from './systems/PhysicsEngine';
export type {
  CollisionCallback,
} from './systems/PhysicsEngine';

export {
  ParticleSystem,
  particleSystem,
  FIRE_EMITTER_CONFIG,
  SMOKE_EMITTER_CONFIG,
  SPARKLE_EMITTER_CONFIG,
  EXPLOSION_EMITTER_CONFIG,
} from './systems/ParticleSystem';

export {
  SkeletonSystem,
  skeletonSystem,
} from './systems/SkeletonSystem';
export type {
  SkeletonEvent,
  SkeletonEventCallback,
} from './systems/SkeletonSystem';

// 公式动画系统
export {
  evaluateFormula,
  compileFormula,
  clearFormulaCache,
  getFormulaVariables,
  BUILT_IN_FUNCTIONS,
  BUILT_IN_CONSTANTS,
} from './systems/FormulaParser';

export {
  FormulaAnimationSystem,
} from './systems/FormulaAnimationSystem';
export type {
  FormulaAnimation,
  DynamicElementGroup,
  ComputedVariable,
  FormulaAnimationContext,
} from './systems/FormulaAnimationSystem';

// 动态曲线
export {
  DynamicCurve,
  createWaveCurve,
} from './systems/DynamicCurve';
export type {
  DynamicCurveConfig,
} from './systems/DynamicCurve';

// 阶段指示器
export {
  StageIndicator,
  createStageIndicator,
} from './systems/StageIndicator';
export type {
  Stage,
  StageIndicatorConfig,
} from './systems/StageIndicator';

// 工具
export { SDLValidator, validateScene, isValidScene } from './utils/SDLValidator';
export type { ValidationResult, ValidationError } from './utils/SDLValidator';
export {
  getEasingFunction,
  interpolate,
  createBezierEasing,
  createSpringEasing,
  easingFunctions,
} from './utils/EasingFunctions';
export type { EasingFunction } from './utils/EasingFunctions';

// 重新导出类型
export type {
  // 场景
  SceneDefinition,
  SceneState,
  CanvasConfig,
  AssetManifest,
  SceneVariable,
  EvaluationConfig,
  AIControlInterface,
  // 元素
  SceneElement,
  ElementType,
  SpriteElement,
  ShapeElement,
  TextElement,
  ConnectorElement,
  GroupElement,
  ParticleEmitterElement,
  PhysicsBodyElement,
  DragConstraint,
  // 动画
  AnimationTimeline,
  AnimationTrack,
  Keyframe,
  EasingType,
  // 交互
  InteractionRule,
  InteractionAction,
  InteractionTrigger,
  TriggerType,
  // 物理
  PhysicsWorldConfig,
  PhysicsBodyConfig,
  // 3D
  Scene3DConfig,
  GeometryParams,
  MaterialParams,
  LightParams,
  CameraParams,
  // 基础
  Vector2D,
  Vector3D,
  Color,
  Transform2D,
} from '@/types/simulator-engine';
