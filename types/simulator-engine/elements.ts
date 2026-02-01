/**
 * 场景描述语言 (SDL) - 元素类型定义
 */

import type {
  Vector2D,
  Transform2D,
  Transform3D,
  ColorValue,
  FillStyle,
  StrokeStyle,
  MarkerStyle,
  BlendMode,
  NumberRange,
  ColorRange,
  Color,
} from './base';

// ==================== 元素基类 ====================

/** 元素类型枚举 */
export type ElementType =
  | 'sprite'           // 精灵/图标
  | 'shape'            // 基础形状
  | 'text'             // 文本
  | 'connector'        // 连接器/线条
  | 'group'            // 组合
  | 'skeleton'         // 骨骼动画
  | 'particle_emitter' // 粒子发射器
  | 'fluid'            // 流体
  | 'physics_body'     // 物理刚体
  | 'container';       // 容器

/** 拖动约束 */
export interface DragConstraint {
  axis?: 'x' | 'y' | 'both';  // 拖动轴向限制
  min?: number;               // 最小值
  max?: number;               // 最大值
}

/** 元素基类 */
export interface BaseElement {
  id: string;
  name: string;
  type: ElementType;
  transform: Transform2D | Transform3D;
  visible: boolean;
  opacity: number;
  zIndex: number;
  interactive: boolean;
  draggable?: boolean;              // 是否可拖动
  dragConstraint?: DragConstraint;  // 拖动约束
  metadata?: Record<string, unknown>;
}

/** 默认元素属性 */
export const DEFAULT_ELEMENT: Omit<BaseElement, 'id' | 'name' | 'type' | 'transform'> = {
  visible: true,
  opacity: 1,
  zIndex: 0,
  interactive: false,
  draggable: false,
};

// ==================== 精灵元素 ====================

/** 精灵源类型 */
export type SpriteSourceType = 'icon' | 'url' | 'base64' | 'spritesheet';

/** 精灵配置 */
export interface SpriteConfig {
  source: string;              // 图标ID、URL 或 base64
  sourceType: SpriteSourceType;
  frame?: string;              // 精灵表帧名
  tint?: ColorValue;           // 着色
  blendMode?: BlendMode;
  flipX?: boolean;
  flipY?: boolean;
}

/** 精灵元素 */
export interface SpriteElement extends BaseElement {
  type: 'sprite';
  sprite: SpriteConfig;
}

// ==================== 形状元素 ====================

/** 形状类型 */
export type ShapeType =
  | 'rectangle'
  | 'circle'
  | 'ellipse'
  | 'polygon'
  | 'line'
  | 'polyline'
  | 'arc'
  | 'bezier'
  | 'quadratic'
  | 'smooth_curve';  // 平滑曲线（自动计算控制点）

/** 形状配置 */
export interface ShapeConfig {
  shapeType: ShapeType;
  fill?: FillStyle;
  stroke?: StrokeStyle;
  // 矩形
  width?: number;
  height?: number;
  cornerRadius?: number;
  // 圆形
  radius?: number;
  // 椭圆
  radiusX?: number;
  radiusY?: number;
  // 多边形/折线
  points?: Vector2D[];
  closed?: boolean;
  // 弧形
  startAngle?: number;
  endAngle?: number;
  anticlockwise?: boolean;
  // 贝塞尔曲线
  controlPoints?: Vector2D[];
}

/** 形状元素 */
export interface ShapeElement extends BaseElement {
  type: 'shape';
  shape: ShapeConfig;
}

// ==================== 文本元素 ====================

/** 文本对齐 */
export type TextAlign = 'left' | 'center' | 'right';
export type TextVerticalAlign = 'top' | 'middle' | 'bottom';

/** 文本配置 */
export interface TextConfig {
  content: string;
  fontFamily: string;
  fontSize: number;
  fontWeight?: number | 'normal' | 'bold';
  fontStyle?: 'normal' | 'italic';
  color: ColorValue;
  align?: TextAlign;
  verticalAlign?: TextVerticalAlign;
  lineHeight?: number;
  letterSpacing?: number;
  maxWidth?: number;
  wordWrap?: boolean;
  // 描边
  stroke?: ColorValue;
  strokeWidth?: number;
  // 阴影
  shadow?: {
    color: ColorValue;
    blur: number;
    offsetX: number;
    offsetY: number;
  };
}

/** 文本元素 */
export interface TextElement extends BaseElement {
  type: 'text';
  text: TextConfig;
}

// ==================== 连接器元素 ====================

/** 连接器样式 */
export type ConnectorStyle = 'straight' | 'curved' | 'orthogonal' | 'bezier';

/** 连接器配置 */
export interface ConnectorConfig {
  fromElementId: string;
  toElementId: string;
  fromAnchor: Vector2D;        // 起点锚点 (0-1)
  toAnchor: Vector2D;          // 终点锚点 (0-1)
  style: ConnectorStyle;
  stroke: StrokeStyle;
  startMarker?: MarkerStyle;
  endMarker?: MarkerStyle;
  label?: string;
  labelPosition?: number;      // 0-1，标签在线上的位置
  curvature?: number;          // 曲线弯曲程度
}

/** 连接器元素 */
export interface ConnectorElement extends BaseElement {
  type: 'connector';
  connector: ConnectorConfig;
}

// ==================== 组合元素 ====================

/** 组合配置 */
export interface GroupConfig {
  children: string[];          // 子元素 ID 列表
  clipChildren?: boolean;      // 是否裁剪子元素
}

/** 组合元素 */
export interface GroupElement extends BaseElement {
  type: 'group';
  group: GroupConfig;
}

// ==================== 容器元素 ====================

/** 容器配置 */
export interface ContainerConfig {
  children: string[];
  scrollable?: boolean;
  scrollDirection?: 'horizontal' | 'vertical' | 'both';
  padding?: number | { top: number; right: number; bottom: number; left: number };
  background?: FillStyle;
  border?: StrokeStyle;
  borderRadius?: number;
}

/** 容器元素 */
export interface ContainerElement extends BaseElement {
  type: 'container';
  container: ContainerConfig;
}

// ==================== 骨骼动画元素 ====================

/** 骨骼定义 */
export interface Bone {
  id: string;
  name: string;
  parentId?: string;
  length: number;
  rotation: number;
  position: Vector2D;
}

/** 骨骼插槽 */
export interface SkeletonSlot {
  id: string;
  boneId: string;
  attachment?: string;
  color?: Color;
  zIndex?: number;
}

/** 精灵附件 */
export interface SpriteAttachment {
  id: string;
  type: 'sprite';
  source: string;
  offset: Vector2D;
  rotation: number;
  scale: Vector2D;
}

/** 骨骼皮肤 */
export interface SkeletonSkin {
  id: string;
  name: string;
  attachments: Record<string, SpriteAttachment>;
}

/** 骨骼关键帧 */
export interface BoneKeyframe {
  time: number;
  rotation?: number;
  position?: Vector2D;
  scale?: Vector2D;
  easing?: string;
}

/** 骨骼时间线 */
export interface BoneTimeline {
  boneId: string;
  keyframes: BoneKeyframe[];
}

/** 插槽关键帧 */
export interface SlotKeyframe {
  time: number;
  attachment?: string;
  color?: Color;
}

/** 插槽时间线 */
export interface SlotTimeline {
  slotId: string;
  keyframes: SlotKeyframe[];
}

/** 骨骼动画 */
export interface SkeletonAnimation {
  id: string;
  name: string;
  duration: number;
  loop: boolean;
  boneTimelines: BoneTimeline[];
  slotTimelines: SlotTimeline[];
}

/** 骨骼配置 */
export interface SkeletonConfig {
  bones: Bone[];
  slots: SkeletonSlot[];
  skins: SkeletonSkin[];
  activeSkin: string;
  animations: SkeletonAnimation[];
  activeAnimation?: string;
}

/** 骨骼元素 */
export interface SkeletonElement extends BaseElement {
  type: 'skeleton';
  skeleton: SkeletonConfig;
}

// ==================== 粒子发射器元素 ====================

/** 发射器形状 */
export type EmitterShape = 'point' | 'circle' | 'rectangle' | 'line' | 'ring';

/** 粒子发射器配置 */
export interface ParticleEmitterConfig {
  // 发射属性
  emissionRate: number;        // 每秒发射数量
  maxParticles: number;
  emitterShape: EmitterShape;
  emitterSize: Vector2D;
  emitterAngle?: NumberRange;  // 发射角度范围

  // 粒子生命周期
  lifetime: NumberRange;

  // 粒子外观
  texture?: string;
  startColor: Color | ColorRange;
  endColor?: Color | ColorRange;
  startSize: NumberRange;
  endSize?: NumberRange;
  startRotation: NumberRange;
  rotationSpeed: NumberRange;

  // 粒子运动
  startSpeed: NumberRange;
  gravity: Vector2D;
  radialAcceleration?: NumberRange;
  tangentialAcceleration?: NumberRange;

  // 混合模式
  blendMode: BlendMode;

  // 控制
  autoStart?: boolean;
  duration?: number;           // 发射持续时间，undefined 为无限
}

/** 粒子发射器元素 */
export interface ParticleEmitterElement extends BaseElement {
  type: 'particle_emitter';
  emitter: ParticleEmitterConfig;
}

// ==================== 流体元素 ====================

/** 流体类型 */
export type FluidType = 'water' | 'smoke' | 'fire' | 'custom';

/** 流体源 */
export interface FluidSource {
  id: string;
  position: Vector2D;
  velocity: Vector2D;
  density: number;
  radius: number;
  continuous: boolean;
}

/** 流体配置 */
export interface FluidConfig {
  type: FluidType;
  resolution: number;          // 模拟分辨率
  viscosity: number;           // 粘度
  diffusion: number;           // 扩散率
  density: number;             // 密度
  color: Color | Color[];      // 颜色或渐变
  velocityDissipation: number;
  pressureIterations: number;

  // 边界
  bounds: {
    width: number;
    height: number;
  };

  // 源
  sources: FluidSource[];

  // 障碍物元素 ID
  obstacles?: string[];
}

/** 流体元素 */
export interface FluidElement extends BaseElement {
  type: 'fluid';
  fluid: FluidConfig;
}

// ==================== 物理刚体元素 ====================

/** 物理体类型 */
export type PhysicsBodyType = 'static' | 'dynamic' | 'kinematic';

/** 物理形状类型 */
export type PhysicsShapeType = 'circle' | 'rectangle' | 'polygon' | 'chain';

/** 物理形状 */
export interface PhysicsShape {
  type: PhysicsShapeType;
  radius?: number;
  width?: number;
  height?: number;
  vertices?: Vector2D[];
  offset?: Vector2D;
}

/** 物理约束类型 */
export type PhysicsConstraintType =
  | 'distance'
  | 'revolute'
  | 'prismatic'
  | 'weld'
  | 'rope'
  | 'spring'
  | 'mouse';

/** 物理约束 */
export interface PhysicsConstraint {
  id: string;
  type: PhysicsConstraintType;
  targetBodyId?: string;
  anchorA: Vector2D;
  anchorB?: Vector2D;
  // 约束参数
  length?: number;
  stiffness?: number;
  damping?: number;
  lowerLimit?: number;
  upperLimit?: number;
  motorEnabled?: boolean;
  motorSpeed?: number;
  maxMotorTorque?: number;
}

/** 物理刚体配置 */
export interface PhysicsBodyConfig {
  bodyType: PhysicsBodyType;
  shape: PhysicsShape;

  // 物理属性
  mass?: number;
  friction?: number;
  restitution?: number;        // 弹性
  linearDamping?: number;
  angularDamping?: number;

  // 初始状态
  linearVelocity?: Vector2D;
  angularVelocity?: number;

  // 碰撞
  collisionGroup?: number;
  collisionMask?: number;
  isSensor?: boolean;          // 是否为传感器

  // 约束
  constraints?: PhysicsConstraint[];

  // 渲染的元素 ID (可选)
  renderElementId?: string;
}

/** 物理刚体元素 */
export interface PhysicsBodyElement extends BaseElement {
  type: 'physics_body';
  physics: PhysicsBodyConfig;
}

// ==================== 联合类型 ====================

/** 场景元素联合类型 */
export type SceneElement =
  | SpriteElement
  | ShapeElement
  | TextElement
  | ConnectorElement
  | GroupElement
  | ContainerElement
  | SkeletonElement
  | ParticleEmitterElement
  | FluidElement
  | PhysicsBodyElement;

/** 根据类型获取元素 */
export type ElementByType<T extends ElementType> =
  T extends 'sprite' ? SpriteElement :
  T extends 'shape' ? ShapeElement :
  T extends 'text' ? TextElement :
  T extends 'connector' ? ConnectorElement :
  T extends 'group' ? GroupElement :
  T extends 'container' ? ContainerElement :
  T extends 'skeleton' ? SkeletonElement :
  T extends 'particle_emitter' ? ParticleEmitterElement :
  T extends 'fluid' ? FluidElement :
  T extends 'physics_body' ? PhysicsBodyElement :
  never;
