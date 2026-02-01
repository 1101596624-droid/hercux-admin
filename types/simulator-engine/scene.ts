/**
 * 场景描述语言 (SDL) - 场景定义类型
 */

import type { Vector2D, Vector3D, Color, ColorValue } from './base';
import type { SceneElement } from './elements';
import type { AnimationTimeline } from './animation';
import type { InteractionRule, InteractionAction } from './interaction';
import type { PhysicsWorldConfig } from './physics';
import type { Scene3DConfig } from './three';
import type {
  FormulaAnimation,
  ComputedVariable,
} from '../../components/simulator-engine/systems/FormulaAnimationSystem';
import type { DynamicCurveConfig } from '../../components/simulator-engine/systems/DynamicCurve';
import type { StageIndicatorConfig } from '../../components/simulator-engine/systems/StageIndicator';

// ==================== 画布配置 ====================

/** 渲染器类型 */
export type RendererType = 'svg' | 'pixi' | 'three';

/** 相机类型 */
export type CameraType = 'orthographic' | 'perspective';

/** 相机配置 */
export interface CameraConfig {
  type: CameraType;
  fov?: number;                // 透视相机视野角度
  near?: number;
  far?: number;
  position?: Vector3D;
  lookAt?: Vector3D;
  zoom?: number;
}

/** 画布配置 */
export interface CanvasConfig {
  width: number;
  height: number;
  backgroundColor: ColorValue;
  renderer: RendererType;
  pixelRatio?: number;
  antialias?: boolean;
  transparent?: boolean;
  // 3D 相机
  camera?: CameraConfig;
  // 视口
  viewport?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

/** 默认画布配置 */
export const DEFAULT_CANVAS_CONFIG: CanvasConfig = {
  width: 800,
  height: 600,
  backgroundColor: '#f8fafc',
  renderer: 'pixi',
  pixelRatio: window?.devicePixelRatio || 1,
  antialias: true,
  transparent: false,
};

// ==================== 资源清单 ====================

/** 资源引用 */
export interface AssetReference {
  id: string;
  url: string;
  preload: boolean;
}

/** 精灵表资源 */
export interface SpritesheetAsset extends AssetReference {
  frames: Record<string, {
    x: number;
    y: number;
    width: number;
    height: number;
  }>;
  animations?: Record<string, string[]>;
}

/** 骨骼资源 */
export interface SkeletonAsset extends AssetReference {
  atlasUrl: string;
  scale?: number;
}

/** 资源清单 */
export interface AssetManifest {
  icons?: AssetReference[];
  images?: AssetReference[];
  sounds?: AssetReference[];
  fonts?: AssetReference[];
  spritesheets?: SpritesheetAsset[];
  skeletons?: SkeletonAsset[];
}

// ==================== 场景变量 ====================

/** 变量类型 */
export type VariableType =
  | 'number'
  | 'string'
  | 'boolean'
  | 'vector2'
  | 'vector3'
  | 'color'
  | 'array'
  | 'object';

/** 场景变量 */
export interface SceneVariable {
  id: string;
  name: string;
  type: VariableType;
  defaultValue: unknown;
  persistent?: boolean;        // 是否持久化
  readonly?: boolean;          // 是否只读
  description?: string;
}

// ==================== 评估配置 ====================

/** 评估规则类型 */
export type EvaluationRuleType =
  | 'variable'     // 变量值检查
  | 'element'      // 元素状态检查
  | 'physics'      // 物理状态检查
  | 'interaction'  // 交互完成检查
  | 'time'         // 时间检查
  | 'custom';      // 自定义表达式

/** 评估规则 */
export interface EvaluationRule {
  type: EvaluationRuleType;
  expression: string;          // 表达式或函数名
  expectedValue?: unknown;
  tolerance?: number;          // 数值容差
}

/** 评估标准 */
export interface EvaluationCriterion {
  id: string;
  name: string;
  description?: string;
  weight: number;              // 权重 (0-100)
  rule: EvaluationRule;
  feedback?: {
    success: string;
    failure: string;
  };
}

/** 评估提示 */
export interface EvaluationHint {
  id: string;
  condition: string;           // 触发条件表达式
  message: string;
  level: 'info' | 'warning' | 'error';
  showOnce?: boolean;
}

/** 评估配置 */
export interface EvaluationConfig {
  criteria: EvaluationCriterion[];
  passThreshold: number;       // 通过阈值 (0-100)
  maxAttempts?: number;
  timeLimit?: number;          // 秒
  hints?: EvaluationHint[];
  // 回调
  onPass?: InteractionAction[];
  onFail?: InteractionAction[];
}

// ==================== AI 控制接口 ====================

/** AI 命令参数 */
export interface AICommandParameter {
  name: string;
  type: string;
  description: string;
  required: boolean;
  default?: unknown;
  enum?: unknown[];
}

/** AI 命令模板 */
export interface AICommandTemplate {
  id: string;
  name: string;
  description: string;
  parameters: AICommandParameter[];
  action: InteractionAction;
}

/** AI 控制接口 */
export interface AIControlInterface {
  // 可由 AI 控制的变量
  controllableVariables: string[];
  // 可由 AI 触发的动作
  availableActions: string[];
  // AI 可观察的状态
  observableState: string[];
  // 命令模板
  commandTemplates: AICommandTemplate[];
}

// ==================== 场景定义 ====================

/** SDL 版本 */
export type SDLVersion = '1.0.0';

/** 场景定义 */
export interface SceneDefinition {
  /** SDL 版本 */
  version: SDLVersion;

  /** 场景 ID */
  id: string;

  /** 场景名称 */
  name: string;

  /** 场景描述 */
  description: string;

  /** 画布配置 */
  canvas: CanvasConfig;

  /** 资源清单 */
  assets: AssetManifest;

  /** 场景元素 */
  elements: SceneElement[];

  /** 动画时间线 */
  timelines: AnimationTimeline[];

  /** 交互规则 */
  interactions: InteractionRule[];

  /** 物理世界配置 */
  physics?: PhysicsWorldConfig;

  /** 3D 场景配置 */
  scene3D?: Scene3DConfig;

  /** 场景变量 */
  variables: SceneVariable[];

  /** 评估配置 */
  evaluation?: EvaluationConfig;

  /** AI 控制接口 */
  aiInterface?: AIControlInterface;

  /** 公式动画 */
  formulaAnimations?: FormulaAnimation[];

  /** 计算变量 */
  computedVariables?: ComputedVariable[];

  /** 动态曲线 */
  dynamicCurves?: DynamicCurveConfig[];

  /** 阶段指示器 */
  stageIndicators?: StageIndicatorConfig[];

  /** 元数据 */
  metadata?: {
    author?: string;
    version?: string;
    tags?: string[];
    thumbnail?: string;
    createdAt?: string;
    updatedAt?: string;
  };
}

// ==================== 场景状态 ====================

/** 场景运行时状态 */
export interface SceneState {
  /** 场景 ID */
  sceneId: string;

  /** 是否已加载 */
  loaded: boolean;

  /** 是否正在运行 */
  running: boolean;

  /** 是否暂停 */
  paused: boolean;

  /** 当前时间 (毫秒) */
  currentTime: number;

  /** 变量值 */
  variables: Record<string, unknown>;

  /** 元素状态 */
  elements: Record<string, {
    visible: boolean;
    position: Vector2D;
    rotation: number;
    scale: Vector2D;
    opacity: number;
  }>;

  /** 评估结果 */
  evaluation?: {
    score: number;
    passed: boolean;
    criteriaResults: Record<string, boolean>;
    attempts: number;
    timeSpent: number;
  };
}

// ==================== 场景事件 ====================

/** 场景事件类型 */
export type SceneEventType =
  | 'load'
  | 'ready'
  | 'start'
  | 'pause'
  | 'resume'
  | 'stop'
  | 'reset'
  | 'complete'
  | 'error'
  | 'variableChange'
  | 'evaluationUpdate';

/** 场景事件 */
export interface SceneEvent {
  type: SceneEventType;
  sceneId: string;
  timestamp: number;
  data?: unknown;
}

/** 场景事件监听器 */
export type SceneEventListener = (event: SceneEvent) => void;
