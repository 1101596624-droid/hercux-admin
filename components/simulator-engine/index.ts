/**
 * 模拟引擎 - 导出
 */

// 渲染器
export { default as HTMLSimulatorRenderer } from './HTMLSimulatorRenderer';
export { ThreeRenderer } from './renderers/ThreeRenderer';

// 系统
export {
  PhysicsEngine,
  physicsEngine,
} from './systems/PhysicsEngine';
export type {
  CollisionCallback,
} from './systems/PhysicsEngine';

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
