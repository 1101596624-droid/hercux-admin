/**
 * 场景状态管理 Store
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type {
  SceneDefinition,
  SceneState,
  SceneElement,
  AnimationTimeline,
  InteractionRule,
  SceneVariable,
  Vector2D,
  SceneEvent,
  SceneEventType,
  SceneEventListener,
  EvaluationCriterion,
} from '@/types/simulator-engine';
import { validateScene } from '@/components/simulator-engine/utils/SDLValidator';

// ==================== Store 状态类型 ====================

interface SceneStoreState {
  // 场景定义
  scene: SceneDefinition | null;

  // 运行时状态
  loaded: boolean;
  running: boolean;
  paused: boolean;
  currentTime: number;

  // 变量值
  variables: Record<string, unknown>;

  // 元素状态 (运行时修改)
  elementStates: Record<string, ElementRuntimeState>;

  // 评估状态
  evaluationState: EvaluationState | null;

  // 错误
  error: string | null;

  // 事件监听器
  eventListeners: Map<SceneEventType, Set<SceneEventListener>>;
}

/** 元素运行时状态 */
interface ElementRuntimeState {
  visible: boolean;
  position: Vector2D;
  rotation: number;
  scale: Vector2D;
  opacity: number;
  customProps: Record<string, unknown>;
}

/** 评估状态 */
interface EvaluationState {
  score: number;
  passed: boolean;
  criteriaResults: Record<string, boolean>;
  attempts: number;
  timeSpent: number;
  startTime: number | null;
}

// ==================== Store Actions ====================

interface SceneStoreActions {
  // 场景管理
  loadScene: (scene: SceneDefinition) => Promise<boolean>;
  unloadScene: () => void;
  resetScene: () => void;

  // 运行控制
  start: () => void;
  pause: () => void;
  resume: () => void;
  stop: () => void;

  // 时间控制
  setCurrentTime: (time: number) => void;
  tick: (deltaTime: number) => void;

  // 变量操作
  getVariable: (name: string) => unknown;
  setVariable: (name: string, value: unknown) => void;
  incrementVariable: (name: string, amount: number) => void;
  toggleVariable: (name: string) => void;

  // 元素操作
  getElement: (id: string) => SceneElement | undefined;
  getElementState: (id: string) => ElementRuntimeState | undefined;
  setElementProperty: (id: string, property: string, value: unknown) => void;
  setElementPosition: (id: string, position: Vector2D) => void;
  setElementRotation: (id: string, rotation: number) => void;
  setElementScale: (id: string, scale: Vector2D) => void;
  setElementOpacity: (id: string, opacity: number) => void;
  setElementVisible: (id: string, visible: boolean) => void;

  // 评估
  checkEvaluation: () => void;
  submitResult: () => EvaluationState | null;

  // 事件
  on: (event: SceneEventType, listener: SceneEventListener) => void;
  off: (event: SceneEventType, listener: SceneEventListener) => void;
  emit: (event: SceneEvent) => void;

  // 获取完整状态
  getSceneState: () => SceneState | null;
}

// ==================== Store 实现 ====================

export const useSceneStore = create<SceneStoreState & SceneStoreActions>()(
  devtools(
    (set, get) => ({
      // 初始状态
      scene: null,
      loaded: false,
      running: false,
      paused: false,
      currentTime: 0,
      variables: {},
      elementStates: {},
      evaluationState: null,
      error: null,
      eventListeners: new Map(),

      // ==================== 场景管理 ====================

      loadScene: async (scene: SceneDefinition) => {
        // 验证场景
        const validation = validateScene(scene);
        if (!validation.valid) {
          set({
            error: `场景验证失败: ${validation.errors.map(e => e.message).join(', ')}`,
            loaded: false,
          });
          return false;
        }

        // 初始化变量
        const variables: Record<string, unknown> = {};
        scene.variables?.forEach((v: SceneVariable) => {
          variables[v.id] = v.defaultValue;
        });

        // 初始化元素状态
        const elementStates: Record<string, ElementRuntimeState> = {};
        scene.elements?.forEach((element: SceneElement) => {
          const transform = element.transform;
          elementStates[element.id] = {
            visible: element.visible,
            position: { ...transform.position },
            rotation: transform.rotation,
            scale: { ...transform.scale },
            opacity: element.opacity,
            customProps: {},
          };
        });

        // 初始化评估状态
        let evaluationState: EvaluationState | null = null;
        if (scene.evaluation) {
          const criteriaResults: Record<string, boolean> = {};
          scene.evaluation.criteria.forEach((c: EvaluationCriterion) => {
            criteriaResults[c.id] = false;
          });
          evaluationState = {
            score: 0,
            passed: false,
            criteriaResults,
            attempts: 0,
            timeSpent: 0,
            startTime: null,
          };
        }

        set({
          scene,
          loaded: true,
          running: false,
          paused: false,
          currentTime: 0,
          variables,
          elementStates,
          evaluationState,
          error: null,
        });

        // 触发加载事件
        get().emit({
          type: 'load',
          sceneId: scene.id,
          timestamp: Date.now(),
        });

        return true;
      },

      unloadScene: () => {
        const { scene } = get();
        if (scene) {
          get().emit({
            type: 'stop',
            sceneId: scene.id,
            timestamp: Date.now(),
          });
        }

        set({
          scene: null,
          loaded: false,
          running: false,
          paused: false,
          currentTime: 0,
          variables: {},
          elementStates: {},
          evaluationState: null,
          error: null,
        });
      },

      resetScene: () => {
        const { scene } = get();
        if (!scene) return;

        // 重新初始化变量
        const variables: Record<string, unknown> = {};
        scene.variables?.forEach((v: SceneVariable) => {
          variables[v.id] = v.defaultValue;
        });

        // 重新初始化元素状态
        const elementStates: Record<string, ElementRuntimeState> = {};
        scene.elements?.forEach((element: SceneElement) => {
          const transform = element.transform;
          elementStates[element.id] = {
            visible: element.visible,
            position: { ...transform.position },
            rotation: transform.rotation,
            scale: { ...transform.scale },
            opacity: element.opacity,
            customProps: {},
          };
        });

        // 重置评估状态
        let evaluationState: EvaluationState | null = null;
        if (scene.evaluation) {
          const criteriaResults: Record<string, boolean> = {};
          scene.evaluation.criteria.forEach((c: EvaluationCriterion) => {
            criteriaResults[c.id] = false;
          });
          evaluationState = {
            score: 0,
            passed: false,
            criteriaResults,
            attempts: get().evaluationState?.attempts || 0,
            timeSpent: 0,
            startTime: null,
          };
        }

        set({
          running: false,
          paused: false,
          currentTime: 0,
          variables,
          elementStates,
          evaluationState,
        });

        get().emit({
          type: 'reset',
          sceneId: scene.id,
          timestamp: Date.now(),
        });
      },

      // ==================== 运行控制 ====================

      start: () => {
        const { scene, loaded, running } = get();
        if (!scene || !loaded || running) return;

        set({
          running: true,
          paused: false,
          currentTime: 0,
        });

        // 更新评估开始时间
        if (get().evaluationState) {
          set({
            evaluationState: {
              ...get().evaluationState!,
              startTime: Date.now(),
            },
          });
        }

        get().emit({
          type: 'start',
          sceneId: scene.id,
          timestamp: Date.now(),
        });
      },

      pause: () => {
        const { scene, running, paused } = get();
        if (!scene || !running || paused) return;

        set({ paused: true });

        get().emit({
          type: 'pause',
          sceneId: scene.id,
          timestamp: Date.now(),
        });
      },

      resume: () => {
        const { scene, running, paused } = get();
        if (!scene || !running || !paused) return;

        set({ paused: false });

        get().emit({
          type: 'resume',
          sceneId: scene.id,
          timestamp: Date.now(),
        });
      },

      stop: () => {
        const { scene, running } = get();
        if (!scene || !running) return;

        set({
          running: false,
          paused: false,
        });

        get().emit({
          type: 'stop',
          sceneId: scene.id,
          timestamp: Date.now(),
        });
      },

      // ==================== 时间控制 ====================

      setCurrentTime: (time: number) => {
        set({ currentTime: Math.max(0, time) });
      },

      tick: (deltaTime: number) => {
        const { running, paused, currentTime, evaluationState } = get();
        if (!running || paused) return;

        set({ currentTime: currentTime + deltaTime });

        // 更新评估时间
        if (evaluationState && evaluationState.startTime) {
          set({
            evaluationState: {
              ...evaluationState,
              timeSpent: (Date.now() - evaluationState.startTime) / 1000,
            },
          });
        }
      },

      // ==================== 变量操作 ====================

      getVariable: (name: string) => {
        return get().variables[name];
      },

      setVariable: (name: string, value: unknown) => {
        const { scene, variables } = get();
        const oldValue = variables[name];

        set({
          variables: {
            ...variables,
            [name]: value,
          },
        });

        // 触发变量变化事件
        if (scene) {
          get().emit({
            type: 'variableChange',
            sceneId: scene.id,
            timestamp: Date.now(),
            data: { name, oldValue, newValue: value },
          });
        }
      },

      incrementVariable: (name: string, amount: number) => {
        const { variables } = get();
        const currentValue = variables[name];
        if (typeof currentValue === 'number') {
          get().setVariable(name, currentValue + amount);
        }
      },

      toggleVariable: (name: string) => {
        const { variables } = get();
        const currentValue = variables[name];
        if (typeof currentValue === 'boolean') {
          get().setVariable(name, !currentValue);
        }
      },

      // ==================== 元素操作 ====================

      getElement: (id: string) => {
        return get().scene?.elements?.find((e: SceneElement) => e.id === id);
      },

      getElementState: (id: string) => {
        return get().elementStates[id];
      },

      setElementProperty: (id: string, property: string, value: unknown) => {
        const { elementStates } = get();
        const state = elementStates[id];
        if (!state) return;

        // 处理核心属性
        const parts = property.split('.');
        const rootProp = parts[0];

        let newState = { ...state };

        switch (rootProp) {
          case 'opacity':
            newState.opacity = typeof value === 'number' ? Math.max(0, Math.min(1, value)) : state.opacity;
            break;
          case 'visible':
            newState.visible = typeof value === 'boolean' ? value : state.visible;
            break;
          case 'position':
            if (parts.length === 1 && typeof value === 'object' && value !== null) {
              newState.position = value as Vector2D;
            } else if (parts[1] === 'x' && typeof value === 'number') {
              newState.position = { ...state.position, x: value };
            } else if (parts[1] === 'y' && typeof value === 'number') {
              newState.position = { ...state.position, y: value };
            }
            break;
          case 'scale':
            if (parts.length === 1 && typeof value === 'object' && value !== null) {
              newState.scale = value as Vector2D;
            } else if (parts[1] === 'x' && typeof value === 'number') {
              newState.scale = { ...state.scale, x: value };
            } else if (parts[1] === 'y' && typeof value === 'number') {
              newState.scale = { ...state.scale, y: value };
            }
            break;
          case 'rotation':
            newState.rotation = typeof value === 'number' ? value : state.rotation;
            break;
          default:
            // 其他属性存到 customProps
            newState.customProps = {
              ...state.customProps,
              [property]: value,
            };
        }

        set({
          elementStates: {
            ...elementStates,
            [id]: newState,
          },
        });
      },

      setElementPosition: (id: string, position: Vector2D) => {
        const { elementStates } = get();
        const state = elementStates[id];
        if (!state) return;

        set({
          elementStates: {
            ...elementStates,
            [id]: { ...state, position },
          },
        });
      },

      setElementRotation: (id: string, rotation: number) => {
        const { elementStates } = get();
        const state = elementStates[id];
        if (!state) return;

        set({
          elementStates: {
            ...elementStates,
            [id]: { ...state, rotation },
          },
        });
      },

      setElementScale: (id: string, scale: Vector2D) => {
        const { elementStates } = get();
        const state = elementStates[id];
        if (!state) return;

        set({
          elementStates: {
            ...elementStates,
            [id]: { ...state, scale },
          },
        });
      },

      setElementOpacity: (id: string, opacity: number) => {
        const { elementStates } = get();
        const state = elementStates[id];
        if (!state) return;

        set({
          elementStates: {
            ...elementStates,
            [id]: { ...state, opacity: Math.max(0, Math.min(1, opacity)) },
          },
        });
      },

      setElementVisible: (id: string, visible: boolean) => {
        const { elementStates } = get();
        const state = elementStates[id];
        if (!state) return;

        set({
          elementStates: {
            ...elementStates,
            [id]: { ...state, visible },
          },
        });
      },

      // ==================== 评估 ====================

      checkEvaluation: () => {
        const { scene, evaluationState, variables, elementStates } = get();
        if (!scene?.evaluation || !evaluationState) return;

        const criteriaResults: Record<string, boolean> = {};
        let totalScore = 0;
        let totalWeight = 0;

        scene.evaluation.criteria.forEach((criterion: EvaluationCriterion) => {
          // 简单的表达式评估 (实际应用中可能需要更复杂的评估器)
          let passed = false;
          try {
            // 创建评估上下文
            const context = {
              variables,
              elements: elementStates,
              // 可以添加更多上下文
            };
            // 这里简化处理，实际应该使用安全的表达式评估器
            passed = evaluateExpression(criterion.rule.expression, context);
          } catch (e) {
            console.error(`评估标准 ${criterion.id} 失败:`, e);
          }

          criteriaResults[criterion.id] = passed;
          if (passed) {
            totalScore += criterion.weight;
          }
          totalWeight += criterion.weight;
        });

        const score = totalWeight > 0 ? (totalScore / totalWeight) * 100 : 0;
        const passed = score >= scene.evaluation.passThreshold;

        set({
          evaluationState: {
            ...evaluationState,
            score,
            passed,
            criteriaResults,
          },
        });

        get().emit({
          type: 'evaluationUpdate',
          sceneId: scene.id,
          timestamp: Date.now(),
          data: { score, passed, criteriaResults },
        });
      },

      submitResult: () => {
        const { scene, evaluationState } = get();
        if (!scene || !evaluationState) return null;

        // 增加尝试次数
        const newState = {
          ...evaluationState,
          attempts: evaluationState.attempts + 1,
        };

        set({ evaluationState: newState });

        get().emit({
          type: 'complete',
          sceneId: scene.id,
          timestamp: Date.now(),
          data: newState,
        });

        return newState;
      },

      // ==================== 事件 ====================

      on: (event: SceneEventType, listener: SceneEventListener) => {
        const { eventListeners } = get();
        if (!eventListeners.has(event)) {
          eventListeners.set(event, new Set());
        }
        eventListeners.get(event)!.add(listener);
      },

      off: (event: SceneEventType, listener: SceneEventListener) => {
        const { eventListeners } = get();
        eventListeners.get(event)?.delete(listener);
      },

      emit: (event: SceneEvent) => {
        const { eventListeners } = get();
        eventListeners.get(event.type)?.forEach(listener => {
          try {
            listener(event);
          } catch (e) {
            console.error('事件监听器错误:', e);
          }
        });
      },

      // ==================== 获取完整状态 ====================

      getSceneState: () => {
        const { scene, loaded, running, paused, currentTime, variables, elementStates, evaluationState } = get();
        if (!scene) return null;

        return {
          sceneId: scene.id,
          loaded,
          running,
          paused,
          currentTime,
          variables,
          elements: Object.fromEntries(
            Object.entries(elementStates).map(([id, state]) => [
              id,
              {
                visible: state.visible,
                position: state.position,
                rotation: state.rotation,
                scale: state.scale,
                opacity: state.opacity,
              },
            ])
          ),
          evaluation: evaluationState
            ? {
                score: evaluationState.score,
                passed: evaluationState.passed,
                criteriaResults: evaluationState.criteriaResults,
                attempts: evaluationState.attempts,
                timeSpent: evaluationState.timeSpent,
              }
            : undefined,
        };
      },
    }),
    { name: 'scene-store' }
  )
);

// ==================== 辅助函数 ====================

/**
 * 简单的表达式评估器
 * 注意：这是一个简化版本，生产环境应使用更安全的方案
 */
function evaluateExpression(expression: string, context: Record<string, unknown>): boolean {
  // 简单的变量检查
  if (expression.startsWith('variables.')) {
    const varName = expression.replace('variables.', '').split(/[<>=!]/)[0].trim();
    const variables = context.variables as Record<string, unknown>;

    if (expression.includes('>=')) {
      const [, value] = expression.split('>=');
      return Number(variables[varName]) >= Number(value.trim());
    }
    if (expression.includes('<=')) {
      const [, value] = expression.split('<=');
      return Number(variables[varName]) <= Number(value.trim());
    }
    if (expression.includes('===')) {
      const [, value] = expression.split('===');
      return variables[varName] === JSON.parse(value.trim());
    }
    if (expression.includes('==')) {
      const [, value] = expression.split('==');
      return variables[varName] == value.trim();
    }
    if (expression.includes('>')) {
      const [, value] = expression.split('>');
      return Number(variables[varName]) > Number(value.trim());
    }
    if (expression.includes('<')) {
      const [, value] = expression.split('<');
      return Number(variables[varName]) < Number(value.trim());
    }

    return Boolean(variables[varName]);
  }

  // 默认返回 false
  return false;
}
