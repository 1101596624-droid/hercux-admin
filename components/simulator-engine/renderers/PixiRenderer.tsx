/**
 * PixiJS 渲染器 - 高性能 2D 渲染
 */

'use client';

import { useEffect, useRef, useCallback } from 'react';
import * as PIXI from 'pixi.js';
import { useSceneStore } from '@/stores/useSceneStore';
import type {
  SceneDefinition,
  SceneElement,
  SpriteElement,
  ShapeElement,
  TextElement,
  ParticleEmitterElement,
  Vector2D,
  AnimationTimeline,
  InteractionRule,
  DragConstraint,
} from '@/types/simulator-engine';
import { ParticleSystem, BLUE_PURPLE_AMBIENT_CONFIG } from '../systems/ParticleSystem';
import { colorToPixi, degToRad } from '@/types/simulator-engine/base';
import { ManualAnimationController } from '../systems/AnimationController';
import { InteractionManager, InteractionContext } from '../systems/InteractionManager';
import { FormulaAnimationSystem, FormulaAnimationContext } from '../systems/FormulaAnimationSystem';
import { DynamicCurve } from '../systems/DynamicCurve';
import { StageIndicator } from '../systems/StageIndicator';

// ==================== Props ====================

interface PixiRendererProps {
  scene: SceneDefinition;
  onReady?: () => void;
  onError?: (error: Error) => void;
  className?: string;
}

// ==================== 组件 ====================

export function PixiRenderer({ scene, onReady, onError, className }: PixiRendererProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const appRef = useRef<PIXI.Application | null>(null);
  const elementsRef = useRef<Map<string, PIXI.Container>>(new Map());
  const animationFrameRef = useRef<number | null>(null);
  const animationControllerRef = useRef<ManualAnimationController | null>(null);
  const interactionManagerRef = useRef<InteractionManager | null>(null);
  const particleSystemRef = useRef<ParticleSystem | null>(null);
  const formulaAnimationRef = useRef<FormulaAnimationSystem | null>(null);
  const dynamicCurvesRef = useRef<Map<string, DynamicCurve>>(new Map());
  const stageIndicatorsRef = useRef<Map<string, StageIndicator>>(new Map());
  const lastTimeRef = useRef<number>(0);

  // 全局拖动状态
  const dragStateRef = useRef<{
    isDragging: boolean;
    elementId: string | null;
    element: SceneElement | null;
    pixiElement: PIXI.Container | null;
    startPos: Vector2D;
    elementStartPos: Vector2D;
  }>({
    isDragging: false,
    elementId: null,
    element: null,
    pixiElement: null,
    startPos: { x: 0, y: 0 },
    elementStartPos: { x: 0, y: 0 },
  });

  const {
    loadScene,
    elementStates,
    running,
    paused,
    tick,
    getVariable,
    setVariable,
    incrementVariable,
    toggleVariable,
    setElementPosition,
    setElementVisible,
    setElementOpacity,
    setElementProperty,
    getElementState,
    resetScene,
    emit,
  } = useSceneStore();

  // 绑定 PixiJS 事件到交互管理器
  const bindElementEvents = useCallback((element: SceneElement, pixiElement: PIXI.Container) => {
    if (!element.interactive) return;

    console.log('PixiRenderer: binding events for element', element.id, 'draggable:', element.draggable);

    const getLocalPosition = (e: PIXI.FederatedPointerEvent): Vector2D => {
      const local = e.getLocalPosition(pixiElement);
      return { x: local.x, y: local.y };
    };

    const getGlobalPosition = (e: PIXI.FederatedPointerEvent): Vector2D => {
      return { x: e.globalX, y: e.globalY };
    };

    pixiElement.on('pointerdown', (e: PIXI.FederatedPointerEvent) => {
      console.log('PixiRenderer: pointerdown on', element.id, 'draggable:', element.draggable);
      interactionManagerRef.current?.handlePointerDown(
        element.id,
        getLocalPosition(e),
        getGlobalPosition(e)
      );

      // 如果元素可拖动，开始拖动
      if (element.draggable) {
        dragStateRef.current = {
          isDragging: true,
          elementId: element.id,
          element: element,
          pixiElement: pixiElement,
          startPos: { x: e.globalX, y: e.globalY },
          elementStartPos: { x: pixiElement.position.x, y: pixiElement.position.y },
        };
        console.log('PixiRenderer: start dragging', element.id, 'from', dragStateRef.current.elementStartPos);
      }
    });

    pixiElement.on('pointerup', (e: PIXI.FederatedPointerEvent) => {
      console.log('PixiRenderer: pointerup on', element.id);
      interactionManagerRef.current?.handlePointerUp(
        element.id,
        getLocalPosition(e),
        getGlobalPosition(e)
      );

      if (dragStateRef.current.isDragging && dragStateRef.current.elementId === element.id) {
        dragStateRef.current.isDragging = false;
      }
    });

    pixiElement.on('pointerout', (e: PIXI.FederatedPointerEvent) => {
      interactionManagerRef.current?.handlePointerOut(
        element.id,
        getLocalPosition(e),
        getGlobalPosition(e)
      );
    });
  }, []);

  // 初始化 PixiJS 应用
  const initApp = useCallback(async () => {
    if (!containerRef.current || appRef.current) return;

    try {
      const app = new PIXI.Application();

      await app.init({
        width: scene.canvas.width,
        height: scene.canvas.height,
        backgroundColor: typeof scene.canvas.backgroundColor === 'string'
          ? scene.canvas.backgroundColor
          : colorToPixi(scene.canvas.backgroundColor),
        antialias: scene.canvas.antialias ?? true,
        resolution: scene.canvas.pixelRatio || window.devicePixelRatio || 1,
        autoDensity: true,
      });

      containerRef.current.appendChild(app.canvas as HTMLCanvasElement);
      appRef.current = app;

      // PixiJS 8: 必须设置 stage 的 eventMode 才能接收事件
      app.stage.eventMode = 'static';
      app.stage.interactiveChildren = true;
      app.stage.hitArea = new PIXI.Rectangle(0, 0, scene.canvas.width, scene.canvas.height);

      // 绑定全局拖动事件到 stage
      app.stage.on('pointermove', (e: PIXI.FederatedPointerEvent) => {
        const dragState = dragStateRef.current;
        if (dragState.isDragging && dragState.pixiElement && dragState.element) {
          const deltaX = e.globalX - dragState.startPos.x;
          const deltaY = e.globalY - dragState.startPos.y;
          let newX = dragState.elementStartPos.x + deltaX;
          let newY = dragState.elementStartPos.y + deltaY;

          // 应用拖动约束
          const constraint = dragState.element.dragConstraint;
          if (constraint) {
            if (constraint.axis === 'x') {
              newY = dragState.elementStartPos.y;
            } else if (constraint.axis === 'y') {
              newX = dragState.elementStartPos.x;
            }
            if (constraint.min !== undefined && (constraint.axis === 'x' || constraint.axis === 'both')) {
              newX = Math.max(constraint.min, newX);
            }
            if (constraint.max !== undefined && (constraint.axis === 'x' || constraint.axis === 'both')) {
              newX = Math.min(constraint.max, newX);
            }
            if (constraint.min !== undefined && (constraint.axis === 'y' || constraint.axis === 'both')) {
              newY = Math.max(constraint.min, newY);
            }
            if (constraint.max !== undefined && (constraint.axis === 'y' || constraint.axis === 'both')) {
              newY = Math.min(constraint.max, newY);
            }
          }

          dragState.pixiElement.position.set(newX, newY);
          setElementProperty(dragState.elementId!, 'position', { x: newX, y: newY });
        }
      });

      app.stage.on('pointerup', () => {
        if (dragStateRef.current.isDragging) {
          console.log('PixiRenderer: global pointerup, ending drag');
          dragStateRef.current.isDragging = false;
        }
      });

      app.stage.on('pointerupoutside', () => {
        if (dragStateRef.current.isDragging) {
          console.log('PixiRenderer: global pointerupoutside, ending drag');
          dragStateRef.current.isDragging = false;
        }
      });

      // 创建元素
      createElements(app, scene.elements);

      // 加载场景到 store
      await loadScene(scene);

      onReady?.();
    } catch (error) {
      console.error('PixiJS 初始化失败:', error);
      onError?.(error as Error);
    }
  }, [scene, loadScene, onReady, onError, setElementProperty]);

  // 创建所有元素（不绑定事件，事件在交互管理器初始化后绑定）
  const createElements = useCallback((app: PIXI.Application, elements: SceneElement[]) => {
    elements.forEach(element => {
      const pixiElement = createPixiElement(element);
      if (pixiElement) {
        app.stage.addChild(pixiElement);
        elementsRef.current.set(element.id, pixiElement);
        // 注意：事件绑定移到 bindAllElementEvents() 中
      }
    });
  }, []);

  // 绑定所有元素的交互事件（在交互管理器初始化后调用）
  const bindAllElementEvents = useCallback(() => {
    if (!scene.elements) {
      console.log('PixiRenderer: bindAllElementEvents - no elements');
      return;
    }

    console.log('PixiRenderer: bindAllElementEvents called, elements count:', scene.elements.length);
    console.log('PixiRenderer: elementsRef size:', elementsRef.current.size);
    console.log('PixiRenderer: interactionManager exists:', !!interactionManagerRef.current);

    let bindCount = 0;
    scene.elements.forEach(element => {
      const pixiElement = elementsRef.current.get(element.id);
      console.log(`PixiRenderer: element ${element.id}, interactive: ${element.interactive}, pixiElement exists: ${!!pixiElement}`);
      if (pixiElement && element.interactive) {
        bindElementEvents(element, pixiElement);
        bindCount++;
      }
    });

    console.log('PixiRenderer: bindAllElementEvents completed, bindCount:', bindCount);
  }, [scene.elements, bindElementEvents]);

  // 创建单个 Pixi 元素
  const createPixiElement = useCallback((element: SceneElement): PIXI.Container | null => {
    switch (element.type) {
      case 'shape':
        return createShapeElement(element as ShapeElement);
      case 'text':
        return createTextElement(element as TextElement);
      case 'sprite':
        return createSpriteElement(element as SpriteElement);
      case 'particle_emitter':
        return createParticleEmitterElement(element as ParticleEmitterElement);
      default:
        console.warn(`不支持的元素类型: ${element.type}`);
        return null;
    }
  }, []);

  // 辅助函数：将颜色字符串转换为数字
  const parseColor = (color: string | number | object): number => {
    if (typeof color === 'number') return color;
    if (typeof color === 'string') {
      // 处理 #RRGGBB 格式
      if (color.startsWith('#')) {
        return parseInt(color.slice(1), 16);
      }
      // 处理 rgb() 格式
      if (color.startsWith('rgb')) {
        const match = color.match(/\d+/g);
        if (match && match.length >= 3) {
          return (parseInt(match[0]) << 16) + (parseInt(match[1]) << 8) + parseInt(match[2]);
        }
      }
      // 尝试直接解析为十六进制
      return parseInt(color, 16) || 0x000000;
    }
    if (typeof color === 'object' && color !== null) {
      return colorToPixi(color as any);
    }
    return 0x000000;
  };

  // 创建形状元素
  const createShapeElement = useCallback((element: ShapeElement): PIXI.Graphics => {
    const graphics = new PIXI.Graphics();
    const { shape, transform } = element;

    console.log('createShapeElement:', element.id, 'shape:', JSON.stringify(shape), 'transform:', JSON.stringify(transform));

    // 获取填充颜色 (转换为数字格式)
    const fillColor = shape.fill?.color ? parseColor(shape.fill.color) : 0x3B82F6; // 默认蓝色
    console.log('createShapeElement:', element.id, 'fillColor:', fillColor, 'shape.fill:', shape.fill);

    // 获取描边配置
    const strokeColor = shape.stroke?.color ? parseColor(shape.stroke.color) : null;
    const strokeWidth = shape.stroke?.width || 1;

    // PixiJS 8: 使用链式 API 绘制形状并填充
    switch (shape.shapeType) {
      case 'rectangle':
        const w = shape.width || 100;
        const h = shape.height || 100;
        if (shape.cornerRadius) {
          graphics.roundRect(-w / 2, -h / 2, w, h, shape.cornerRadius).fill({ color: fillColor });
        } else {
          graphics.rect(-w / 2, -h / 2, w, h).fill({ color: fillColor });
        }
        if (strokeColor !== null) {
          graphics.rect(-w / 2, -h / 2, w, h).stroke({ color: strokeColor, width: strokeWidth });
        }
        break;

      case 'circle':
        graphics.circle(0, 0, shape.radius || 50).fill({ color: fillColor });
        if (strokeColor !== null) {
          graphics.circle(0, 0, shape.radius || 50).stroke({ color: strokeColor, width: strokeWidth });
        }
        break;

      case 'ellipse':
        graphics.ellipse(0, 0, shape.radiusX || 50, shape.radiusY || 30).fill({ color: fillColor });
        if (strokeColor !== null) {
          graphics.ellipse(0, 0, shape.radiusX || 50, shape.radiusY || 30).stroke({ color: strokeColor, width: strokeWidth });
        }
        break;

      case 'polygon':
        if (shape.points && shape.points.length >= 3) {
          const flatPoints = shape.points.flatMap((p: Vector2D) => [p.x, p.y]);
          graphics.poly(flatPoints).fill({ color: fillColor });
          if (strokeColor !== null) {
            graphics.poly(flatPoints).stroke({ color: strokeColor, width: strokeWidth });
          }
        }
        break;

      case 'line':
        if (shape.points && shape.points.length >= 2) {
          graphics.moveTo(shape.points[0].x, shape.points[0].y);
          for (let i = 1; i < shape.points.length; i++) {
            graphics.lineTo(shape.points[i].x, shape.points[i].y);
          }
          if (strokeColor !== null) {
            graphics.stroke({ color: strokeColor, width: strokeWidth });
          }
        }
        break;

      case 'arc':
        graphics.arc(
          0, 0,
          shape.radius || 50,
          degToRad(shape.startAngle || 0),
          degToRad(shape.endAngle || 360),
          shape.anticlockwise
        ).fill({ color: fillColor });
        if (strokeColor !== null) {
          graphics.arc(
            0, 0,
            shape.radius || 50,
            degToRad(shape.startAngle || 0),
            degToRad(shape.endAngle || 360),
            shape.anticlockwise
          ).stroke({ color: strokeColor, width: strokeWidth });
        }
        break;

      case 'bezier':
        // 三次贝塞尔曲线
        if (shape.points && shape.points.length >= 4) {
          graphics.moveTo(shape.points[0].x, shape.points[0].y);
          for (let i = 1; i < shape.points.length - 2; i += 3) {
            graphics.bezierCurveTo(
              shape.points[i].x, shape.points[i].y,
              shape.points[i + 1].x, shape.points[i + 1].y,
              shape.points[i + 2].x, shape.points[i + 2].y
            );
          }
          if (strokeColor !== null) {
            graphics.stroke({ color: strokeColor, width: strokeWidth });
          }
        }
        break;

      case 'quadratic':
        // 二次贝塞尔曲线（平滑曲线）
        if (shape.points && shape.points.length >= 3) {
          graphics.moveTo(shape.points[0].x, shape.points[0].y);
          for (let i = 1; i < shape.points.length - 1; i += 2) {
            graphics.quadraticCurveTo(
              shape.points[i].x, shape.points[i].y,
              shape.points[i + 1].x, shape.points[i + 1].y
            );
          }
          if (strokeColor !== null) {
            graphics.stroke({ color: strokeColor, width: strokeWidth });
          }
        }
        break;

      case 'smooth_curve':
        // 平滑曲线（自动计算控制点）
        if (shape.points && shape.points.length >= 2) {
          const pts = shape.points;
          graphics.moveTo(pts[0].x, pts[0].y);

          if (pts.length === 2) {
            graphics.lineTo(pts[1].x, pts[1].y);
          } else {
            for (let i = 1; i < pts.length; i++) {
              const xc = (pts[i].x + pts[i - 1].x) / 2;
              const yc = (pts[i].y + pts[i - 1].y) / 2;
              graphics.quadraticCurveTo(pts[i - 1].x, pts[i - 1].y, xc, yc);
            }
            // 连接到最后一个点
            graphics.lineTo(pts[pts.length - 1].x, pts[pts.length - 1].y);
          }

          if (strokeColor !== null) {
            graphics.stroke({ color: strokeColor, width: strokeWidth });
          }
        }
        break;
    }

    // 应用变换
    applyTransform(graphics, transform);

    console.log('createShapeElement:', element.id, 'after transform - position:', graphics.position.x, graphics.position.y, 'scale:', graphics.scale.x, graphics.scale.y, 'visible:', element.visible, 'opacity:', element.opacity);

    // 设置交互
    if (element.interactive) {
      graphics.eventMode = 'static';
      graphics.cursor = 'pointer';
      graphics.interactive = true;

      // PixiJS 8 需要设置 hitArea 才能接收事件
      const shape = element.shape;
      if (shape) {
        switch (shape.shapeType) {
          case 'rectangle':
            const w = shape.width || 100;
            const h = shape.height || 100;
            graphics.hitArea = new PIXI.Rectangle(-w / 2, -h / 2, w, h);
            console.log(`PixiRenderer: set hitArea for ${element.id}: Rectangle(${-w/2}, ${-h/2}, ${w}, ${h})`);
            break;
          case 'circle':
            graphics.hitArea = new PIXI.Circle(0, 0, shape.radius || 50);
            console.log(`PixiRenderer: set hitArea for ${element.id}: Circle(0, 0, ${shape.radius || 50})`);
            break;
          case 'ellipse':
            graphics.hitArea = new PIXI.Ellipse(0, 0, shape.radiusX || 50, shape.radiusY || 30);
            break;
          default:
            // 使用边界框作为 hitArea
            const bounds = graphics.getLocalBounds();
            graphics.hitArea = new PIXI.Rectangle(bounds.x, bounds.y, bounds.width, bounds.height);
        }
      }
    }

    graphics.visible = element.visible !== false;
    graphics.alpha = element.opacity ?? 1;

    console.log('createShapeElement:', element.id, 'final - visible:', graphics.visible, 'alpha:', graphics.alpha, 'bounds:', graphics.getLocalBounds());

    return graphics;
  }, []);

  // 创建文本元素
  const createTextElement = useCallback((element: TextElement): PIXI.Text => {
    const { text: textConfig, transform } = element;

    const fontWeight = textConfig.fontWeight === 'bold' ? 'bold' :
                       textConfig.fontWeight === 'normal' ? 'normal' :
                       typeof textConfig.fontWeight === 'number' ? (textConfig.fontWeight >= 600 ? 'bold' : 'normal') :
                       'normal';

    // 解析文本颜色
    const textColor = textConfig.color
      ? (typeof textConfig.color === 'string' ? textConfig.color : parseColor(textConfig.color))
      : '#ffffff';

    const style = new PIXI.TextStyle({
      fontFamily: textConfig.fontFamily || 'Arial, sans-serif',
      fontSize: textConfig.fontSize || 16,
      fontWeight: fontWeight as PIXI.TextStyleFontWeight,
      fontStyle: textConfig.fontStyle || 'normal',
      fill: textColor,
      align: (textConfig.align as 'left' | 'center' | 'right') || 'center',
      wordWrap: textConfig.wordWrap ?? false,
      wordWrapWidth: textConfig.maxWidth || 400,
      letterSpacing: textConfig.letterSpacing || 0,
      lineHeight: textConfig.lineHeight ? textConfig.fontSize * textConfig.lineHeight : undefined,
    });

    if (textConfig.stroke) {
      style.stroke = {
        color: typeof textConfig.stroke === 'string'
          ? textConfig.stroke
          : parseColor(textConfig.stroke),
        width: textConfig.strokeWidth || 1,
      };
    }

    const text = new PIXI.Text({
      text: textConfig.content || '',
      style,
    });

    // 设置锚点以便居中
    text.anchor.set(transform.anchor?.x ?? 0.5, transform.anchor?.y ?? 0.5);

    // 应用变换
    text.position.set(transform.position.x, transform.position.y);
    text.rotation = degToRad(transform.rotation || 0);
    text.scale.set(transform.scale?.x ?? 1, transform.scale?.y ?? 1);

    // 设置交互
    if (element.interactive) {
      text.eventMode = 'static';
      text.cursor = 'pointer';
    }

    text.visible = element.visible !== false;
    text.alpha = element.opacity ?? 1;

    return text;
  }, []);

  // 创建精灵元素
  const createSpriteElement = useCallback((element: SpriteElement): PIXI.Sprite | PIXI.Graphics => {
    const { sprite: spriteConfig, transform } = element;

    // 如果是图标类型，创建一个占位符
    // 实际应用中应该从资源加载器获取纹理
    if (spriteConfig.sourceType === 'icon') {
      // 创建一个简单的占位符
      const graphics = new PIXI.Graphics();
      graphics.fill({ color: spriteConfig.tint ? colorToPixi(spriteConfig.tint) : 0x3B82F6 });
      graphics.circle(0, 0, 20);
      graphics.fill();

      applyTransform(graphics, transform);

      if (element.interactive) {
        graphics.eventMode = 'static';
        graphics.cursor = 'pointer';
      }

      graphics.visible = element.visible;
      graphics.alpha = element.opacity;

      return graphics;
    }

    // URL 或 base64 类型
    const sprite = PIXI.Sprite.from(spriteConfig.source);

    // 应用着色
    if (spriteConfig.tint) {
      sprite.tint = colorToPixi(spriteConfig.tint);
    }

    // 应用翻转
    if (spriteConfig.flipX) {
      sprite.scale.x *= -1;
    }
    if (spriteConfig.flipY) {
      sprite.scale.y *= -1;
    }

    // 应用变换
    applyTransform(sprite, transform);

    // 设置交互
    if (element.interactive) {
      sprite.eventMode = 'static';
      sprite.cursor = 'pointer';
    }

    sprite.visible = element.visible;
    sprite.alpha = element.opacity;

    return sprite;
  }, []);

  // 创建粒子发射器元素
  const createParticleEmitterElement = useCallback((element: ParticleEmitterElement): PIXI.Container => {
    const container = new PIXI.Container();
    const { emitter: emitterConfig, transform } = element;

    // 应用变换到容器
    container.position.set(transform.position.x, transform.position.y);
    container.rotation = degToRad(transform.rotation || 0);
    container.scale.set(transform.scale?.x ?? 1, transform.scale?.y ?? 1);
    container.visible = element.visible !== false;
    container.alpha = element.opacity ?? 1;

    // 初始化粒子系统（如果还没有）
    if (!particleSystemRef.current) {
      particleSystemRef.current = new ParticleSystem();
    }

    // 创建发射器
    const fullConfig = {
      emissionRate: emitterConfig.emissionRate ?? 20,
      maxParticles: emitterConfig.maxParticles ?? 100,
      emitterShape: emitterConfig.emitterShape ?? 'point',
      emitterSize: emitterConfig.emitterSize ?? { x: 0, y: 0 },
      emitterAngle: emitterConfig.emitterAngle ?? { min: -90, max: -90 },
      lifetime: emitterConfig.lifetime ?? { min: 1000, max: 2000 },
      startColor: emitterConfig.startColor ?? { r: 99, g: 102, b: 241, a: 0.8 },
      endColor: emitterConfig.endColor ?? { r: 168, g: 85, b: 247, a: 0 },
      startSize: emitterConfig.startSize ?? { min: 5, max: 10 },
      endSize: emitterConfig.endSize ?? { min: 1, max: 3 },
      startRotation: emitterConfig.startRotation ?? { min: 0, max: 360 },
      rotationSpeed: emitterConfig.rotationSpeed ?? { min: -30, max: 30 },
      startSpeed: emitterConfig.startSpeed ?? { min: 20, max: 50 },
      gravity: emitterConfig.gravity ?? { x: 0, y: -10 },
      blendMode: emitterConfig.blendMode ?? 'add',
      autoStart: emitterConfig.autoStart ?? true,
      duration: emitterConfig.duration,
    };

    particleSystemRef.current.createEmitter(element.id, fullConfig, container);

    return container;
  }, []);

  // 应用变换
  const applyTransform = useCallback((
    displayObject: PIXI.Container,
    transform: { position: Vector2D; rotation: number; scale: Vector2D; anchor: Vector2D }
  ) => {
    displayObject.position.set(transform.position.x, transform.position.y);
    displayObject.rotation = degToRad(transform.rotation);
    displayObject.scale.set(transform.scale.x, transform.scale.y);

    // 设置锚点 (如果支持)
    if ('anchor' in displayObject && displayObject.anchor) {
      (displayObject.anchor as PIXI.ObservablePoint).set(transform.anchor.x, transform.anchor.y);
    }
  }, []);

  // 更新元素状态
  const updateElements = useCallback(() => {
    elementsRef.current.forEach((pixiElement, id) => {
      const state = elementStates[id];
      if (!state) return;

      pixiElement.position.set(state.position.x, state.position.y);
      pixiElement.rotation = degToRad(state.rotation);
      pixiElement.scale.set(state.scale.x, state.scale.y);
      pixiElement.alpha = state.opacity;
      pixiElement.visible = state.visible;
    });
  }, [elementStates]);

  // 处理动画属性更新
  const handleAnimationPropertyUpdate = useCallback((
    targetId: string,
    property: string,
    value: unknown
  ) => {
    const pixiElement = elementsRef.current.get(targetId);
    if (!pixiElement) return;

    // 解析属性路径 (如 "position.x", "rotation", "opacity")
    const parts = property.split('.');

    if (parts[0] === 'position') {
      if (parts[1] === 'x' && typeof value === 'number') {
        pixiElement.position.x = value;
      } else if (parts[1] === 'y' && typeof value === 'number') {
        pixiElement.position.y = value;
      } else if (typeof value === 'object' && value !== null) {
        const pos = value as Vector2D;
        pixiElement.position.set(pos.x, pos.y);
      }
    } else if (parts[0] === 'scale') {
      if (parts[1] === 'x' && typeof value === 'number') {
        pixiElement.scale.x = value;
      } else if (parts[1] === 'y' && typeof value === 'number') {
        pixiElement.scale.y = value;
      } else if (typeof value === 'object' && value !== null) {
        const scale = value as Vector2D;
        pixiElement.scale.set(scale.x, scale.y);
      }
    } else if (property === 'rotation' && typeof value === 'number') {
      pixiElement.rotation = degToRad(value);
    } else if (property === 'opacity' && typeof value === 'number') {
      pixiElement.alpha = value;
    } else if (property === 'visible' && typeof value === 'boolean') {
      pixiElement.visible = value;
    }
  }, []);

  // 初始化动画控制器
  const initAnimationController = useCallback(() => {
    if (animationControllerRef.current) {
      animationControllerRef.current.destroy();
    }

    const controller = new ManualAnimationController();
    controller.setPropertyUpdateCallback(handleAnimationPropertyUpdate);

    // 加载所有时间线
    if (scene.timelines && scene.timelines.length > 0) {
      scene.timelines.forEach((timeline: AnimationTimeline) => {
        controller.loadTimeline(timeline);
      });
    }

    animationControllerRef.current = controller;
  }, [scene.timelines, handleAnimationPropertyUpdate]);

  // 初始化交互管理器
  const initInteractionManager = useCallback(() => {
    if (interactionManagerRef.current) {
      interactionManagerRef.current.destroy();
    }

    const manager = new InteractionManager();

    // 创建交互上下文
    const context: InteractionContext = {
      getVariable,
      setVariable,
      incrementVariable,
      toggleVariable,
      getElementProperty: (elementId: string, property: string) => {
        const state = getElementState(elementId);
        if (!state) return undefined;
        const parts = property.split('.');
        let value: unknown = state;
        for (const part of parts) {
          if (value && typeof value === 'object' && part in value) {
            value = (value as Record<string, unknown>)[part];
          } else {
            return undefined;
          }
        }
        return value;
      },
      setElementProperty,
      setElementPosition,
      setElementVisible,
      setElementOpacity,
      playTimeline: (timelineId: string) => {
        animationControllerRef.current?.play(timelineId);
      },
      pauseTimeline: (timelineId: string) => {
        animationControllerRef.current?.pause(timelineId);
      },
      stopTimeline: (timelineId: string) => {
        animationControllerRef.current?.stop(timelineId);
      },
      resetScene,
      emit: (event) => {
        // 只发送有效的场景事件类型
        const validTypes = ['load', 'ready', 'start', 'pause', 'resume', 'stop', 'reset', 'complete', 'error', 'variableChange', 'evaluationUpdate'];
        if (validTypes.includes(event.type)) {
          emit({
            type: event.type as 'load' | 'start' | 'pause' | 'resume' | 'stop' | 'reset' | 'complete' | 'evaluationUpdate' | 'variableChange',
            sceneId: scene.id,
            timestamp: Date.now(),
            data: event.data,
          });
        }
      },
    };

    manager.setContext(context);

    // 加载交互规则
    console.log('PixiRenderer: initInteractionManager, scene.interactions:', scene.interactions?.length || 0);
    if (scene.interactions && scene.interactions.length > 0) {
      manager.loadRules(scene.interactions);
    } else {
      console.warn('PixiRenderer: No interactions found in scene!');
    }

    interactionManagerRef.current = manager;
    console.log('PixiRenderer: interactionManagerRef.current set');
  }, [
    scene.id,
    scene.interactions,
    getVariable,
    setVariable,
    incrementVariable,
    toggleVariable,
    getElementState,
    setElementProperty,
    setElementPosition,
    setElementVisible,
    setElementOpacity,
    resetScene,
    emit,
  ]);

  // 动画循环
  const animate = useCallback((currentTime: number) => {
    if (lastTimeRef.current === 0) {
      lastTimeRef.current = currentTime;
    }

    const deltaTime = currentTime - lastTimeRef.current;
    lastTimeRef.current = currentTime;

    // 始终更新动画控制器（不依赖 running 状态）
    if (animationControllerRef.current) {
      animationControllerRef.current.update(deltaTime);
    }

    // 始终更新粒子系统
    if (particleSystemRef.current) {
      particleSystemRef.current.update(deltaTime);
    }

    // 更新公式动画系统
    if (formulaAnimationRef.current) {
      formulaAnimationRef.current.update(deltaTime);
    }

    // 更新动态曲线
    dynamicCurvesRef.current.forEach(curve => {
      // 传递当前变量值给曲线
      curve.setVariable('time', currentTime / 1000);
      curve.update();
    });

    // 更新阶段指示器（根据进度变量）
    stageIndicatorsRef.current.forEach((indicator, id) => {
      const progress = (getVariable('progress') as number) ?? 0;
      indicator.setProgress(progress);
    });

    if (running && !paused) {
      // 更新场景时间
      tick(deltaTime);

      // 注意：不再调用 updateElements()，因为动画控制器已经直接更新 PixiJS 元素
      // 如果需要同步非动画属性，可以通过 useEffect 监听 elementStates 变化
    }

    animationFrameRef.current = requestAnimationFrame(animate);
  }, [running, paused, tick]);

  // 初始化
  useEffect(() => {
    let isMounted = true;
    let app: PIXI.Application | null = null;

    const initialize = async () => {
      if (!containerRef.current) return;

      try {
        // 1. 创建 PixiJS 应用
        app = new PIXI.Application();
        await app.init({
          width: scene.canvas.width,
          height: scene.canvas.height,
          backgroundColor: typeof scene.canvas.backgroundColor === 'string'
            ? scene.canvas.backgroundColor
            : colorToPixi(scene.canvas.backgroundColor),
          antialias: scene.canvas.antialias ?? true,
          resolution: scene.canvas.pixelRatio || window.devicePixelRatio || 1,
          autoDensity: true,
        });

        if (!isMounted) return;

        containerRef.current.appendChild(app.canvas as HTMLCanvasElement);
        appRef.current = app;

        // PixiJS 8: 必须设置 stage 的 eventMode 才能接收事件
        app.stage.eventMode = 'static';
        app.stage.interactiveChildren = true;
        app.stage.hitArea = new PIXI.Rectangle(0, 0, scene.canvas.width, scene.canvas.height);

        // 绑定全局拖动事件到 stage
        app.stage.on('pointermove', (e: PIXI.FederatedPointerEvent) => {
          const dragState = dragStateRef.current;
          if (dragState.isDragging && dragState.pixiElement && dragState.element) {
            const deltaX = e.globalX - dragState.startPos.x;
            const deltaY = e.globalY - dragState.startPos.y;
            let newX = dragState.elementStartPos.x + deltaX;
            let newY = dragState.elementStartPos.y + deltaY;

            // 应用拖动约束
            const constraint = dragState.element.dragConstraint;
            if (constraint) {
              if (constraint.axis === 'x') {
                newY = dragState.elementStartPos.y;
              } else if (constraint.axis === 'y') {
                newX = dragState.elementStartPos.x;
              }
              if (constraint.min !== undefined && (constraint.axis === 'x' || constraint.axis === 'both')) {
                newX = Math.max(constraint.min, newX);
              }
              if (constraint.max !== undefined && (constraint.axis === 'x' || constraint.axis === 'both')) {
                newX = Math.min(constraint.max, newX);
              }
              if (constraint.min !== undefined && (constraint.axis === 'y' || constraint.axis === 'both')) {
                newY = Math.max(constraint.min, newY);
              }
              if (constraint.max !== undefined && (constraint.axis === 'y' || constraint.axis === 'both')) {
                newY = Math.min(constraint.max, newY);
              }
            }

            dragState.pixiElement.position.set(newX, newY);
            setElementProperty(dragState.elementId!, 'position', { x: newX, y: newY });
          }
        });

        app.stage.on('pointerup', () => {
          if (dragStateRef.current.isDragging) {
            console.log('PixiRenderer: global pointerup, ending drag');
            dragStateRef.current.isDragging = false;
          }
        });

        app.stage.on('pointerupoutside', () => {
          if (dragStateRef.current.isDragging) {
            console.log('PixiRenderer: global pointerupoutside, ending drag');
            dragStateRef.current.isDragging = false;
          }
        });

        // 2. 创建所有元素
        scene.elements.forEach(element => {
          const pixiElement = createPixiElement(element);
          if (pixiElement) {
            app!.stage.addChild(pixiElement);
            elementsRef.current.set(element.id, pixiElement);
          }
        });

        // 3. 加载场景到 store
        await loadScene(scene);
        if (!isMounted) return;

        // 直接更新 PixiJS 元素的辅助函数
        const updatePixiElementProperty = (elementId: string, property: string, value: unknown) => {
          console.log('updatePixiElementProperty called:', elementId, property, value);
          const pixiElement = elementsRef.current.get(elementId);
          if (!pixiElement) {
            console.log('updatePixiElementProperty: element not found:', elementId, 'available:', Array.from(elementsRef.current.keys()));
            return;
          }
          console.log('updatePixiElementProperty: element found, current state - visible:', pixiElement.visible, 'alpha:', pixiElement.alpha, 'position:', pixiElement.position.x, pixiElement.position.y);

          const parts = property.split('.');
          const rootProp = parts[0];

          switch (rootProp) {
            case 'opacity':
              if (typeof value === 'number') {
                pixiElement.alpha = Math.max(0, Math.min(1, value));
              }
              break;
            case 'visible':
              if (typeof value === 'boolean') {
                pixiElement.visible = value;
              }
              break;
            case 'position':
              if (parts.length === 1 && typeof value === 'object' && value !== null) {
                const pos = value as Vector2D;
                pixiElement.position.set(pos.x, pos.y);
              } else if (parts[1] === 'x' && typeof value === 'number') {
                pixiElement.position.x = value;
              } else if (parts[1] === 'y' && typeof value === 'number') {
                pixiElement.position.y = value;
              }
              break;
            case 'scale':
              if (parts.length === 1 && typeof value === 'object' && value !== null) {
                const scale = value as Vector2D;
                pixiElement.scale.set(scale.x, scale.y);
              } else if (parts[1] === 'x' && typeof value === 'number') {
                pixiElement.scale.x = value;
              } else if (parts[1] === 'y' && typeof value === 'number') {
                pixiElement.scale.y = value;
              }
              break;
            case 'rotation':
              if (typeof value === 'number') {
                pixiElement.rotation = degToRad(value);
              }
              break;
            case 'text':
              // 处理文本属性更新
              if (pixiElement instanceof PIXI.Text) {
                if (parts[1] === 'content' && typeof value === 'string') {
                  pixiElement.text = value;
                }
              }
              break;
          }
        };

        // 4. 初始化动画控制器
        const animController = new ManualAnimationController();
        // 动画控制器的回调需要同时更新 store 和 PixiJS 元素
        animController.setPropertyUpdateCallback((elementId: string, property: string, value: unknown) => {
          // 更新 PixiJS 元素
          updatePixiElementProperty(elementId, property, value);
          // 同时更新 store，避免 updateElements() 覆盖动画值
          if (property === 'opacity' && typeof value === 'number') {
            setElementOpacity(elementId, value);
          } else if (property === 'visible' && typeof value === 'boolean') {
            setElementVisible(elementId, value);
          } else if (property === 'position' || property === 'position.x' || property === 'position.y') {
            // position 更新由 setElementProperty 处理
            setElementProperty(elementId, property, value);
          } else if (property === 'scale' || property === 'scale.x' || property === 'scale.y') {
            setElementProperty(elementId, property, value);
          } else if (property === 'rotation') {
            setElementProperty(elementId, property, value);
          }
        });
        if (scene.timelines && scene.timelines.length > 0) {
          scene.timelines.forEach((timeline: AnimationTimeline) => {
            animController.loadTimeline(timeline);
          });
        }
        animationControllerRef.current = animController;

        // 5. 初始化交互管理器
        const interactionMgr = new InteractionManager();

        const context: InteractionContext = {
          getVariable,
          setVariable,
          incrementVariable,
          toggleVariable,
          getElementProperty: (elementId: string, property: string) => {
            const state = getElementState(elementId);
            if (!state) return undefined;
            const parts = property.split('.');
            let value: unknown = state;
            for (const part of parts) {
              if (value && typeof value === 'object' && part in value) {
                value = (value as Record<string, unknown>)[part];
              } else {
                return undefined;
              }
            }
            return value;
          },
          setElementProperty: (elementId: string, property: string, value: unknown) => {
            // 同时更新 store 和 PixiJS 元素
            setElementProperty(elementId, property, value);
            updatePixiElementProperty(elementId, property, value);
          },
          setElementPosition: (elementId: string, position: Vector2D) => {
            setElementPosition(elementId, position);
            const pixiElement = elementsRef.current.get(elementId);
            if (pixiElement) {
              pixiElement.position.set(position.x, position.y);
            }
          },
          setElementVisible: (elementId: string, visible: boolean) => {
            setElementVisible(elementId, visible);
            const pixiElement = elementsRef.current.get(elementId);
            if (pixiElement) {
              pixiElement.visible = visible;
            }
          },
          setElementOpacity: (elementId: string, opacity: number) => {
            setElementOpacity(elementId, opacity);
            const pixiElement = elementsRef.current.get(elementId);
            if (pixiElement) {
              pixiElement.alpha = Math.max(0, Math.min(1, opacity));
            }
          },
          playTimeline: (timelineId: string) => {
            console.log('PixiRenderer: playTimeline called', timelineId, 'animationController exists:', !!animationControllerRef.current);
            animationControllerRef.current?.play(timelineId);
          },
          pauseTimeline: (timelineId: string) => {
            animationControllerRef.current?.pause(timelineId);
          },
          stopTimeline: (timelineId: string) => {
            animationControllerRef.current?.stop(timelineId);
          },
          resetScene,
          emit: (event) => {
            const validTypes = ['load', 'ready', 'start', 'pause', 'resume', 'stop', 'reset', 'complete', 'error', 'variableChange', 'evaluationUpdate'];
            if (validTypes.includes(event.type)) {
              emit({
                type: event.type as 'load' | 'start' | 'pause' | 'resume' | 'stop' | 'reset' | 'complete' | 'evaluationUpdate' | 'variableChange',
                sceneId: scene.id,
                timestamp: Date.now(),
                data: event.data,
              });
            }
          },
        };
        interactionMgr.setContext(context);

        console.log('PixiRenderer: loading interactions, count:', scene.interactions?.length || 0);
        if (scene.interactions && scene.interactions.length > 0) {
          interactionMgr.loadRules(scene.interactions);
        }
        interactionManagerRef.current = interactionMgr;

        // 6. 绑定所有交互元素的事件
        console.log('PixiRenderer: binding events for interactive elements');
        scene.elements.forEach(element => {
          if (!element.interactive) return;
          const pixiElement = elementsRef.current.get(element.id);
          if (!pixiElement) return;

          console.log('PixiRenderer: bindEvents for', element.id, 'draggable:', element.draggable);

          const getLocalPosition = (e: PIXI.FederatedPointerEvent): Vector2D => {
            const local = e.getLocalPosition(pixiElement);
            return { x: local.x, y: local.y };
          };

          const getGlobalPosition = (e: PIXI.FederatedPointerEvent): Vector2D => {
            return { x: e.globalX, y: e.globalY };
          };

          pixiElement.on('pointerdown', (e: PIXI.FederatedPointerEvent) => {
            console.log('PixiRenderer: pointerdown on', element.id, 'draggable:', element.draggable);
            interactionManagerRef.current?.handlePointerDown(
              element.id,
              getLocalPosition(e),
              getGlobalPosition(e)
            );

            // 如果元素可拖动，开始拖动
            if (element.draggable) {
              dragStateRef.current = {
                isDragging: true,
                elementId: element.id,
                element: element,
                pixiElement: pixiElement,
                startPos: { x: e.globalX, y: e.globalY },
                elementStartPos: { x: pixiElement.position.x, y: pixiElement.position.y },
              };
              console.log('PixiRenderer: start dragging', element.id, 'from', dragStateRef.current.elementStartPos);
            }
          });

          pixiElement.on('pointerup', (e: PIXI.FederatedPointerEvent) => {
            console.log('PixiRenderer: pointerup on', element.id);
            interactionManagerRef.current?.handlePointerUp(
              element.id,
              getLocalPosition(e),
              getGlobalPosition(e)
            );

            // 结束拖动
            if (dragStateRef.current.isDragging && dragStateRef.current.elementId === element.id) {
              dragStateRef.current.isDragging = false;
            }
          });

          pixiElement.on('pointermove', (e: PIXI.FederatedPointerEvent) => {
            interactionManagerRef.current?.handlePointerMove(
              element.id,
              getLocalPosition(e),
              getGlobalPosition(e)
            );
          });

          pixiElement.on('pointerover', (e: PIXI.FederatedPointerEvent) => {
            interactionManagerRef.current?.handlePointerMove(
              element.id,
              getLocalPosition(e),
              getGlobalPosition(e)
            );
          });

          pixiElement.on('pointerout', (e: PIXI.FederatedPointerEvent) => {
            interactionManagerRef.current?.handlePointerOut(
              element.id,
              getLocalPosition(e),
              getGlobalPosition(e)
            );
          });
        });

        // 7. 初始化公式动画系统
        if (scene.formulaAnimations || scene.computedVariables) {
          const formulaSystem = new FormulaAnimationSystem();

          const formulaContext: FormulaAnimationContext = {
            getVariable: (name: string) => (getVariable(name) as number) ?? 0,
            setVariable: (name: string, value: number) => setVariable(name, value),
            getElementProperty: (elementId: string, property: string) => {
              const state = getElementState(elementId);
              if (!state) return undefined;
              const parts = property.split('.');
              let value: unknown = state;
              for (const part of parts) {
                if (value && typeof value === 'object' && part in value) {
                  value = (value as Record<string, unknown>)[part];
                } else {
                  return undefined;
                }
              }
              return value;
            },
            setElementProperty: (elementId: string, property: string, value: any) => {
              setElementProperty(elementId, property, value);
              updatePixiElementProperty(elementId, property, value);
            },
          };

          formulaSystem.setContext(formulaContext);

          if (scene.formulaAnimations) {
            formulaSystem.loadAnimations(scene.formulaAnimations);
          }
          if (scene.computedVariables) {
            formulaSystem.loadComputedVariables(scene.computedVariables);
          }

          formulaAnimationRef.current = formulaSystem;
        }

        // 8. 初始化动态曲线
        if (scene.dynamicCurves && app) {
          scene.dynamicCurves.forEach((curveConfig) => {
            const curve = new DynamicCurve(curveConfig);
            app!.stage.addChild(curve.getContainer());
            dynamicCurvesRef.current.set(curveConfig.id, curve);
          });
        }

        // 9. 初始化阶段指示器
        if (scene.stageIndicators && app) {
          scene.stageIndicators.forEach((indicatorConfig) => {
            const indicator = new StageIndicator(indicatorConfig);
            app!.stage.addChild(indicator.getContainer());
            stageIndicatorsRef.current.set(indicatorConfig.id, indicator);
          });
        }

        console.log('PixiRenderer: initialization complete');
        onReady?.();
      } catch (error) {
        console.error('PixiRenderer initialization failed:', error);
        onError?.(error as Error);
      }
    };

    initialize();

    return () => {
      isMounted = false;

      // 清理动画帧
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }

      // 清理动画控制器
      if (animationControllerRef.current) {
        try {
          animationControllerRef.current.destroy();
        } catch (e) {
          console.warn('AnimationController cleanup warning:', e);
        }
        animationControllerRef.current = null;
      }

      // 清理交互管理器
      if (interactionManagerRef.current) {
        try {
          interactionManagerRef.current.destroy();
        } catch (e) {
          console.warn('InteractionManager cleanup warning:', e);
        }
        interactionManagerRef.current = null;
      }

      // 清理粒子系统
      if (particleSystemRef.current) {
        try {
          particleSystemRef.current.destroy();
        } catch (e) {
          console.warn('ParticleSystem cleanup warning:', e);
        }
        particleSystemRef.current = null;
      }

      // 清理公式动画系统
      if (formulaAnimationRef.current) {
        try {
          formulaAnimationRef.current.clear();
        } catch (e) {
          console.warn('FormulaAnimation cleanup warning:', e);
        }
        formulaAnimationRef.current = null;
      }

      // 清理动态曲线
      dynamicCurvesRef.current.forEach(curve => {
        try {
          curve.destroy();
        } catch (e) {
          console.warn('DynamicCurve cleanup warning:', e);
        }
      });
      dynamicCurvesRef.current.clear();

      // 清理阶段指示器
      stageIndicatorsRef.current.forEach(indicator => {
        try {
          indicator.destroy();
        } catch (e) {
          console.warn('StageIndicator cleanup warning:', e);
        }
      });
      stageIndicatorsRef.current.clear();

      // 清理元素引用（不销毁，让 app.destroy 处理）
      elementsRef.current.clear();

      // 最后销毁 PixiJS 应用
      if (appRef.current) {
        const appToDestroy = appRef.current;
        appRef.current = null; // 先清空引用，防止重复销毁

        // 使用 setTimeout 延迟销毁，避免纹理竞态条件
        setTimeout(() => {
          try {
            // 先停止渲染
            if (appToDestroy.ticker) {
              appToDestroy.ticker.stop();
            }
            // 移除所有子元素
            if (appToDestroy.stage) {
              appToDestroy.stage.removeChildren();
            }
            // 使用最安全的销毁选项 - 不销毁纹理
            appToDestroy.destroy(false, {
              children: false,
              texture: false,
              textureSource: false,
              context: false
            });
          } catch (e) {
            // 忽略销毁时的错误，组件已卸载
            console.warn('PixiJS cleanup warning (deferred):', e);
          }
        }, 0);
      }
    };
  }, [scene.id]); // 只依赖 scene.id，避免重复初始化

  // 启动动画循环
  useEffect(() => {
    lastTimeRef.current = 0;
    animationFrameRef.current = requestAnimationFrame(animate);
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [animate]);

  // 当运行状态改变时，不自动播放所有时间线
  // 时间线应该由交互管理器根据用户操作来触发
  // 这里只处理暂停/恢复逻辑
  useEffect(() => {
    if (!animationControllerRef.current || !scene.timelines) return;

    // 只在暂停时暂停所有正在播放的时间线
    // 不在这里自动播放时间线，让交互管理器来控制
    if (paused) {
      scene.timelines.forEach((timeline: AnimationTimeline) => {
        animationControllerRef.current?.pause(timeline.id);
      });
    }
    // 注意：不在这里自动播放，让用户点击按钮触发
  }, [running, paused, scene.timelines]);

  // 监听元素状态变化 - 只在非动画属性变化时更新
  // 注意：动画属性（opacity, scale, position, rotation）由动画控制器直接更新
  // 这里只处理其他属性的变化，如 visible
  useEffect(() => {
    // 暂时禁用自动同步，因为动画控制器已经在更新元素
    // updateElements();
    console.log('elementStates changed, but not calling updateElements to avoid overwriting animation values');
  }, [elementStates]);

  return (
    <div
      ref={containerRef}
      className={className}
      style={{
        width: '100%',
        maxWidth: scene.canvas.width,
        height: scene.canvas.height,
        margin: '0 auto',
      }}
    />
  );
}

export default PixiRenderer;
