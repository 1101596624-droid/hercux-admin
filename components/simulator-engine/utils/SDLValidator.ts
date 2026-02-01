/**
 * SDL 验证器 - 验证场景定义 JSON 的结构和内容
 */

import type {
  SceneDefinition,
  SceneElement,
  AnimationTimeline,
  AnimationTrack,
  InteractionRule,
  CanvasConfig,
  SceneVariable,
  EvaluationConfig,
  ConnectorElement,
} from '@/types/simulator-engine';

// ==================== 验证结果 ====================

/** 验证错误 */
export interface ValidationError {
  path: string;
  message: string;
  severity: 'error' | 'warning';
}

/** 验证结果 */
export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
}

// ==================== 验证器类 ====================

export class SDLValidator {
  private errors: ValidationError[] = [];
  private warnings: ValidationError[] = [];

  /**
   * 验证场景定义
   */
  validate(scene: unknown): ValidationResult {
    this.errors = [];
    this.warnings = [];

    if (!scene || typeof scene !== 'object') {
      this.addError('', '场景定义必须是一个对象');
      return this.getResult();
    }

    const s = scene as Record<string, unknown>;

    // 验证必需字段
    this.validateRequired(s, '', ['version', 'id', 'name', 'canvas', 'elements']);

    // 验证版本
    if (s.version && s.version !== '1.0.0') {
      this.addWarning('version', `不支持的版本: ${s.version}，当前支持 1.0.0`);
    }

    // 验证 ID
    if (s.id && typeof s.id !== 'string') {
      this.addError('id', 'id 必须是字符串');
    }

    // 验证名称
    if (s.name && typeof s.name !== 'string') {
      this.addError('name', 'name 必须是字符串');
    }

    // 验证画布配置
    if (s.canvas) {
      this.validateCanvas(s.canvas, 'canvas');
    }

    // 验证元素
    if (s.elements) {
      this.validateElements(s.elements, 'elements');
    }

    // 验证时间线
    if (s.timelines) {
      this.validateTimelines(s.timelines, 'timelines');
    }

    // 验证交互规则
    if (s.interactions) {
      this.validateInteractions(s.interactions, 'interactions');
    }

    // 验证变量
    if (s.variables) {
      this.validateVariables(s.variables, 'variables');
    }

    // 验证评估配置
    if (s.evaluation) {
      this.validateEvaluation(s.evaluation, 'evaluation');
    }

    // 验证引用完整性
    this.validateReferences(s as unknown as SceneDefinition);

    return this.getResult();
  }

  /**
   * 快速验证 - 只检查基本结构
   */
  quickValidate(scene: unknown): boolean {
    if (!scene || typeof scene !== 'object') return false;
    const s = scene as Record<string, unknown>;
    return (
      typeof s.version === 'string' &&
      typeof s.id === 'string' &&
      typeof s.name === 'string' &&
      typeof s.canvas === 'object' &&
      Array.isArray(s.elements)
    );
  }

  // ==================== 私有方法 ====================

  private validateRequired(obj: Record<string, unknown>, path: string, fields: string[]): void {
    for (const field of fields) {
      if (obj[field] === undefined || obj[field] === null) {
        this.addError(path ? `${path}.${field}` : field, `缺少必需字段: ${field}`);
      }
    }
  }

  private validateCanvas(canvas: unknown, path: string): void {
    if (typeof canvas !== 'object' || canvas === null) {
      this.addError(path, '画布配置必须是一个对象');
      return;
    }

    const c = canvas as Record<string, unknown>;

    // 验证必需字段
    this.validateRequired(c, path, ['width', 'height', 'renderer']);

    // 验证尺寸
    if (typeof c.width !== 'number' || c.width <= 0) {
      this.addError(`${path}.width`, 'width 必须是正数');
    }
    if (typeof c.height !== 'number' || c.height <= 0) {
      this.addError(`${path}.height`, 'height 必须是正数');
    }

    // 验证渲染器类型
    const validRenderers = ['svg', 'pixi', 'three'];
    if (c.renderer && !validRenderers.includes(c.renderer as string)) {
      this.addError(`${path}.renderer`, `无效的渲染器类型: ${c.renderer}，支持: ${validRenderers.join(', ')}`);
    }
  }

  private validateElements(elements: unknown, path: string): void {
    if (!Array.isArray(elements)) {
      this.addError(path, '元素列表必须是数组');
      return;
    }

    const ids = new Set<string>();

    elements.forEach((element, index) => {
      const elementPath = `${path}[${index}]`;
      this.validateElement(element, elementPath, ids);
    });
  }

  private validateElement(element: unknown, path: string, ids: Set<string>): void {
    if (typeof element !== 'object' || element === null) {
      this.addError(path, '元素必须是一个对象');
      return;
    }

    const e = element as Record<string, unknown>;

    // 验证必需字段
    this.validateRequired(e, path, ['id', 'name', 'type', 'transform']);

    // 验证 ID 唯一性
    if (typeof e.id === 'string') {
      if (ids.has(e.id)) {
        this.addError(`${path}.id`, `重复的元素 ID: ${e.id}`);
      } else {
        ids.add(e.id);
      }
    }

    // 验证类型
    const validTypes = [
      'sprite', 'shape', 'text', 'connector', 'group', 'container',
      'skeleton', 'particle_emitter', 'fluid', 'physics_body'
    ];
    if (e.type && !validTypes.includes(e.type as string)) {
      this.addError(`${path}.type`, `无效的元素类型: ${e.type}`);
    }

    // 验证变换
    if (e.transform) {
      this.validateTransform(e.transform, `${path}.transform`);
    }

    // 根据类型验证特定配置
    if (e.type === 'shape' && e.shape) {
      this.validateShapeConfig(e.shape, `${path}.shape`);
    }
    if (e.type === 'text' && e.text) {
      this.validateTextConfig(e.text, `${path}.text`);
    }
    if (e.type === 'sprite' && e.sprite) {
      this.validateSpriteConfig(e.sprite, `${path}.sprite`);
    }
  }

  private validateTransform(transform: unknown, path: string): void {
    if (typeof transform !== 'object' || transform === null) {
      this.addError(path, '变换必须是一个对象');
      return;
    }

    const t = transform as Record<string, unknown>;

    // 验证位置
    if (t.position) {
      this.validateVector2D(t.position, `${path}.position`);
    }

    // 验证缩放
    if (t.scale) {
      this.validateVector2D(t.scale, `${path}.scale`);
    }

    // 验证锚点
    if (t.anchor) {
      this.validateVector2D(t.anchor, `${path}.anchor`);
    }

    // 验证旋转
    if (t.rotation !== undefined && typeof t.rotation !== 'number') {
      this.addError(`${path}.rotation`, 'rotation 必须是数字');
    }
  }

  private validateVector2D(vec: unknown, path: string): void {
    if (typeof vec !== 'object' || vec === null) {
      this.addError(path, '向量必须是一个对象');
      return;
    }

    const v = vec as Record<string, unknown>;
    if (typeof v.x !== 'number') {
      this.addError(`${path}.x`, 'x 必须是数字');
    }
    if (typeof v.y !== 'number') {
      this.addError(`${path}.y`, 'y 必须是数字');
    }
  }

  private validateShapeConfig(shape: unknown, path: string): void {
    if (typeof shape !== 'object' || shape === null) {
      this.addError(path, '形状配置必须是一个对象');
      return;
    }

    const s = shape as Record<string, unknown>;

    const validShapeTypes = [
      'rectangle', 'circle', 'ellipse', 'polygon', 'line', 'polyline', 'arc', 'bezier', 'quadratic'
    ];
    if (s.shapeType && !validShapeTypes.includes(s.shapeType as string)) {
      this.addError(`${path}.shapeType`, `无效的形状类型: ${s.shapeType}`);
    }
  }

  private validateTextConfig(text: unknown, path: string): void {
    if (typeof text !== 'object' || text === null) {
      this.addError(path, '文本配置必须是一个对象');
      return;
    }

    const t = text as Record<string, unknown>;

    if (typeof t.content !== 'string') {
      this.addError(`${path}.content`, 'content 必须是字符串');
    }
    if (typeof t.fontSize !== 'number' || t.fontSize <= 0) {
      this.addError(`${path}.fontSize`, 'fontSize 必须是正数');
    }
  }

  private validateSpriteConfig(sprite: unknown, path: string): void {
    if (typeof sprite !== 'object' || sprite === null) {
      this.addError(path, '精灵配置必须是一个对象');
      return;
    }

    const s = sprite as Record<string, unknown>;

    if (typeof s.source !== 'string') {
      this.addError(`${path}.source`, 'source 必须是字符串');
    }

    const validSourceTypes = ['icon', 'url', 'base64', 'spritesheet'];
    if (s.sourceType && !validSourceTypes.includes(s.sourceType as string)) {
      this.addError(`${path}.sourceType`, `无效的源类型: ${s.sourceType}`);
    }
  }

  private validateTimelines(timelines: unknown, path: string): void {
    if (!Array.isArray(timelines)) {
      this.addError(path, '时间线列表必须是数组');
      return;
    }

    const ids = new Set<string>();

    timelines.forEach((timeline, index) => {
      const timelinePath = `${path}[${index}]`;
      this.validateTimeline(timeline, timelinePath, ids);
    });
  }

  private validateTimeline(timeline: unknown, path: string, ids: Set<string>): void {
    if (typeof timeline !== 'object' || timeline === null) {
      this.addError(path, '时间线必须是一个对象');
      return;
    }

    const t = timeline as Record<string, unknown>;

    // 支持两种结构：tracks 结构或 keyframes 结构
    const hasTracks = Array.isArray(t.tracks);
    const hasKeyframes = Array.isArray(t.keyframes);

    this.validateRequired(t, path, ['id', 'name', 'duration']);

    // 至少需要 tracks 或 keyframes 之一
    if (!hasTracks && !hasKeyframes) {
      this.addWarning(path, '时间线缺少 tracks 或 keyframes');
    }

    // 验证 ID 唯一性
    if (typeof t.id === 'string') {
      if (ids.has(t.id)) {
        this.addError(`${path}.id`, `重复的时间线 ID: ${t.id}`);
      } else {
        ids.add(t.id);
      }
    }

    // 验证持续时间
    if (typeof t.duration !== 'number' || t.duration <= 0) {
      this.addError(`${path}.duration`, 'duration 必须是正数');
    }

    // 验证轨道结构
    if (hasTracks) {
      (t.tracks as unknown[]).forEach((track, index) => {
        this.validateTrack(track, `${path}.tracks[${index}]`);
      });
    }

    // 验证扁平关键帧结构（模板使用的格式）
    if (hasKeyframes) {
      (t.keyframes as unknown[]).forEach((kf, index) => {
        this.validateFlatKeyframe(kf, `${path}.keyframes[${index}]`);
      });
    }
  }

  private validateFlatKeyframe(keyframe: unknown, path: string): void {
    if (typeof keyframe !== 'object' || keyframe === null) {
      this.addError(path, '关键帧必须是一个对象');
      return;
    }

    const kf = keyframe as Record<string, unknown>;

    // 扁平关键帧需要 time, targetId, property, value
    if (typeof kf.time !== 'number') {
      this.addError(`${path}.time`, 'time 必须是数字');
    }
    if (typeof kf.targetId !== 'string') {
      this.addError(`${path}.targetId`, 'targetId 必须是字符串');
    }
    if (typeof kf.property !== 'string') {
      this.addError(`${path}.property`, 'property 必须是字符串');
    }
    if (kf.value === undefined) {
      this.addError(`${path}.value`, '缺少 value 字段');
    }
  }

  private validateTrack(track: unknown, path: string): void {
    if (typeof track !== 'object' || track === null) {
      this.addError(path, '轨道必须是一个对象');
      return;
    }

    const t = track as Record<string, unknown>;

    this.validateRequired(t, path, ['id', 'targetId', 'property', 'keyframes']);

    if (!Array.isArray(t.keyframes)) {
      this.addError(`${path}.keyframes`, 'keyframes 必须是数组');
    } else if (t.keyframes.length < 2) {
      this.addWarning(`${path}.keyframes`, '轨道至少需要 2 个关键帧');
    }
  }

  private validateInteractions(interactions: unknown, path: string): void {
    if (!Array.isArray(interactions)) {
      this.addError(path, '交互规则列表必须是数组');
      return;
    }

    const ids = new Set<string>();

    interactions.forEach((rule, index) => {
      const rulePath = `${path}[${index}]`;
      this.validateInteractionRule(rule, rulePath, ids);
    });
  }

  private validateInteractionRule(rule: unknown, path: string, ids: Set<string>): void {
    if (typeof rule !== 'object' || rule === null) {
      this.addError(path, '交互规则必须是一个对象');
      return;
    }

    const r = rule as Record<string, unknown>;

    this.validateRequired(r, path, ['id', 'name', 'trigger', 'actions']);

    // 验证 ID 唯一性
    if (typeof r.id === 'string') {
      if (ids.has(r.id)) {
        this.addError(`${path}.id`, `重复的交互规则 ID: ${r.id}`);
      } else {
        ids.add(r.id);
      }
    }

    // 验证触发器
    if (r.trigger && typeof r.trigger === 'object') {
      const trigger = r.trigger as Record<string, unknown>;
      const validTriggerTypes = [
        'click', 'doubleClick', 'rightClick', 'pointerDown', 'pointerUp', 'pointerMove',
        'dragStart', 'drag', 'dragEnd', 'drop', 'hover', 'hoverEnd',
        'collision', 'collisionEnd', 'collisionActive',
        'animationStart', 'animationEnd', 'animationLoop', 'timelineMarker',
        'variableChange', 'sceneLoad', 'sceneReady', 'timer', 'interval', 'custom'
      ];
      if (trigger.type && !validTriggerTypes.includes(trigger.type as string)) {
        this.addError(`${path}.trigger.type`, `无效的触发器类型: ${trigger.type}`);
      }
    }

    // 验证动作
    if (!Array.isArray(r.actions)) {
      this.addError(`${path}.actions`, 'actions 必须是数组');
    }
  }

  private validateVariables(variables: unknown, path: string): void {
    if (!Array.isArray(variables)) {
      this.addError(path, '变量列表必须是数组');
      return;
    }

    const ids = new Set<string>();

    variables.forEach((variable, index) => {
      const varPath = `${path}[${index}]`;
      if (typeof variable !== 'object' || variable === null) {
        this.addError(varPath, '变量必须是一个对象');
        return;
      }

      const v = variable as Record<string, unknown>;
      this.validateRequired(v, varPath, ['id', 'name', 'type', 'defaultValue']);

      // 验证 ID 唯一性
      if (typeof v.id === 'string') {
        if (ids.has(v.id)) {
          this.addError(`${varPath}.id`, `重复的变量 ID: ${v.id}`);
        } else {
          ids.add(v.id);
        }
      }

      // 验证类型
      const validTypes = ['number', 'string', 'boolean', 'vector2', 'vector3', 'color', 'array', 'object'];
      if (v.type && !validTypes.includes(v.type as string)) {
        this.addError(`${varPath}.type`, `无效的变量类型: ${v.type}`);
      }
    });
  }

  private validateEvaluation(evaluation: unknown, path: string): void {
    if (typeof evaluation !== 'object' || evaluation === null) {
      this.addError(path, '评估配置必须是一个对象');
      return;
    }

    const e = evaluation as Record<string, unknown>;

    this.validateRequired(e, path, ['criteria', 'passThreshold']);

    if (typeof e.passThreshold !== 'number' || e.passThreshold < 0 || e.passThreshold > 100) {
      this.addError(`${path}.passThreshold`, 'passThreshold 必须是 0-100 之间的数字');
    }

    if (!Array.isArray(e.criteria)) {
      this.addError(`${path}.criteria`, 'criteria 必须是数组');
    }
  }

  private validateReferences(scene: SceneDefinition): void {
    const elementIds = new Set(scene.elements?.map((e: SceneElement) => e.id) || []);
    const timelineIds = new Set(scene.timelines?.map((t: AnimationTimeline) => t.id) || []);
    const variableIds = new Set(scene.variables?.map((v: SceneVariable) => v.id) || []);

    // 验证时间线中的元素引用
    scene.timelines?.forEach((timeline: AnimationTimeline, ti: number) => {
      // 支持 tracks 结构
      timeline.tracks?.forEach((track: AnimationTrack, tri: number) => {
        if (!elementIds.has(track.targetId)) {
          this.addWarning(
            `timelines[${ti}].tracks[${tri}].targetId`,
            `引用了不存在的元素: ${track.targetId}`
          );
        }
      });

      // 支持扁平 keyframes 结构
      const flatKeyframes = (timeline as unknown as Record<string, unknown>).keyframes;
      if (Array.isArray(flatKeyframes)) {
        flatKeyframes.forEach((kf: { targetId?: string }, ki: number) => {
          if (kf.targetId && !elementIds.has(kf.targetId)) {
            this.addWarning(
              `timelines[${ti}].keyframes[${ki}].targetId`,
              `引用了不存在的元素: ${kf.targetId}`
            );
          }
        });
      }
    });

    // 验证交互规则中的元素引用
    scene.interactions?.forEach((rule: InteractionRule, ri: number) => {
      if (rule.trigger.targetId && !elementIds.has(rule.trigger.targetId)) {
        this.addWarning(
          `interactions[${ri}].trigger.targetId`,
          `引用了不存在的元素: ${rule.trigger.targetId}`
        );
      }
    });

    // 验证连接器元素的引用
    scene.elements?.forEach((element: SceneElement, ei: number) => {
      if (element.type === 'connector') {
        const connector = (element as ConnectorElement).connector;
        if (connector) {
          if (!elementIds.has(connector.fromElementId)) {
            this.addWarning(
              `elements[${ei}].connector.fromElementId`,
              `引用了不存在的元素: ${connector.fromElementId}`
            );
          }
          if (!elementIds.has(connector.toElementId)) {
            this.addWarning(
              `elements[${ei}].connector.toElementId`,
              `引用了不存在的元素: ${connector.toElementId}`
            );
          }
        }
      }
    });
  }

  private addError(path: string, message: string): void {
    this.errors.push({ path, message, severity: 'error' });
  }

  private addWarning(path: string, message: string): void {
    this.warnings.push({ path, message, severity: 'warning' });
  }

  private getResult(): ValidationResult {
    return {
      valid: this.errors.length === 0,
      errors: this.errors,
      warnings: this.warnings,
    };
  }
}

// ==================== 导出单例 ====================

export const sdlValidator = new SDLValidator();

/**
 * 验证场景定义
 */
export function validateScene(scene: unknown): ValidationResult {
  return sdlValidator.validate(scene);
}

/**
 * 快速验证场景定义
 */
export function isValidScene(scene: unknown): scene is SceneDefinition {
  return sdlValidator.quickValidate(scene);
}
