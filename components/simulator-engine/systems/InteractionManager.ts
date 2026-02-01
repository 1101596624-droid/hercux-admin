/**
 * 交互管理器 - 处理场景中的用户交互
 */

import type {
  InteractionRule,
  InteractionTrigger,
  InteractionAction,
  InteractionCondition,
  ConditionGroup,
  TriggerType,
  ActionType,
  ConditionOperator,
  PointerEventData,
  DragEventData,
  InteractionEventData,
  Vector2D,
} from '@/types/simulator-engine';

// ==================== 类型定义 ====================

/** 交互上下文 - 提供变量和元素访问 */
export interface InteractionContext {
  // 变量操作
  getVariable: (name: string) => unknown;
  setVariable: (name: string, value: unknown) => void;
  incrementVariable: (name: string, amount: number) => void;
  toggleVariable: (name: string) => void;

  // 元素操作
  getElementProperty: (elementId: string, property: string) => unknown;
  setElementProperty: (elementId: string, property: string, value: unknown) => void;
  setElementPosition: (elementId: string, position: Vector2D) => void;
  setElementVisible: (elementId: string, visible: boolean) => void;
  setElementOpacity: (elementId: string, opacity: number) => void;

  // 动画操作
  playTimeline: (timelineId: string) => void;
  pauseTimeline: (timelineId: string) => void;
  stopTimeline: (timelineId: string) => void;

  // 场景操作
  resetScene: () => void;

  // 事件发射
  emit: (event: { type: string; data?: unknown }) => void;
}

/** 拖拽状态 */
interface DragState {
  isDragging: boolean;
  targetId: string | null;
  startPosition: Vector2D;
  currentPosition: Vector2D;
}

/** 规则执行状态 */
interface RuleExecutionState {
  executedOnce: boolean;
  lastExecutionTime: number;
}

// ==================== 交互管理器类 ====================

export class InteractionManager {
  private rules: Map<string, InteractionRule> = new Map();
  private ruleStates: Map<string, RuleExecutionState> = new Map();
  private context: InteractionContext | null = null;
  private dragState: DragState = {
    isDragging: false,
    targetId: null,
    startPosition: { x: 0, y: 0 },
    currentPosition: { x: 0, y: 0 },
  };
  private hoverTargets: Set<string> = new Set();
  private timers: Map<string, NodeJS.Timeout> = new Map();
  private intervals: Map<string, NodeJS.Timeout> = new Map();

  constructor() {}

  // ==================== 初始化 ====================

  /**
   * 设置交互上下文
   */
  setContext(context: InteractionContext): void {
    this.context = context;
  }

  /**
   * 加载交互规则
   */
  loadRules(rules: InteractionRule[]): void {
    console.log('InteractionManager: loadRules called with', rules.length, 'rules');
    rules.forEach(rule => {
      console.log('InteractionManager: adding rule', rule.id, 'trigger:', rule.trigger.type, 'targetId:', rule.trigger.targetId);
      this.addRule(rule);
    });
    console.log('InteractionManager: total rules loaded:', this.rules.size);
  }

  // ==================== 规则管理 ====================

  /**
   * 添加规则
   */
  addRule(rule: InteractionRule): void {
    this.rules.set(rule.id, rule);
    this.ruleStates.set(rule.id, {
      executedOnce: false,
      lastExecutionTime: 0,
    });

    // 处理定时器触发器
    if (rule.enabled) {
      this.setupTimerTrigger(rule);
    }
  }

  /**
   * 移除规则
   */
  removeRule(ruleId: string): void {
    this.rules.delete(ruleId);
    this.ruleStates.delete(ruleId);
    this.clearTimerTrigger(ruleId);
  }

  /**
   * 启用规则
   */
  enableRule(ruleId: string): void {
    const rule = this.rules.get(ruleId);
    if (rule) {
      rule.enabled = true;
      this.setupTimerTrigger(rule);
    }
  }

  /**
   * 禁用规则
   */
  disableRule(ruleId: string): void {
    const rule = this.rules.get(ruleId);
    if (rule) {
      rule.enabled = false;
      this.clearTimerTrigger(ruleId);
    }
  }

  /**
   * 获取规则
   */
  getRule(ruleId: string): InteractionRule | undefined {
    return this.rules.get(ruleId);
  }

  // ==================== 事件处理 ====================

  /**
   * 处理指针按下事件
   */
  handlePointerDown(targetId: string | null, position: Vector2D, globalPosition: Vector2D): void {
    const eventData: PointerEventData = {
      position,
      globalPosition,
      button: 0,
      buttons: 1,
      pressure: 1,
      targetId: targetId || undefined,
    };

    this.handleEvent('pointerDown', eventData);

    // 开始拖拽
    if (targetId) {
      this.dragState = {
        isDragging: true,
        targetId,
        startPosition: { ...globalPosition },
        currentPosition: { ...globalPosition },
      };
      this.handleEvent('dragStart', {
        ...eventData,
        startPosition: this.dragState.startPosition,
        delta: { x: 0, y: 0 },
        distance: 0,
      } as DragEventData);
    }
  }

  /**
   * 处理指针移动事件
   */
  handlePointerMove(targetId: string | null, position: Vector2D, globalPosition: Vector2D): void {
    const eventData: PointerEventData = {
      position,
      globalPosition,
      button: 0,
      buttons: this.dragState.isDragging ? 1 : 0,
      pressure: this.dragState.isDragging ? 1 : 0,
      targetId: targetId || undefined,
    };

    this.handleEvent('pointerMove', eventData);

    // 处理拖拽
    if (this.dragState.isDragging && this.dragState.targetId) {
      const delta = {
        x: globalPosition.x - this.dragState.currentPosition.x,
        y: globalPosition.y - this.dragState.currentPosition.y,
      };
      const distance = Math.sqrt(
        Math.pow(globalPosition.x - this.dragState.startPosition.x, 2) +
        Math.pow(globalPosition.y - this.dragState.startPosition.y, 2)
      );

      this.dragState.currentPosition = { ...globalPosition };

      this.handleEvent('drag', {
        ...eventData,
        targetId: this.dragState.targetId,
        startPosition: this.dragState.startPosition,
        delta,
        distance,
      } as DragEventData);
    }

    // 处理悬停
    if (targetId && !this.hoverTargets.has(targetId)) {
      this.hoverTargets.add(targetId);
      this.handleEvent('hover', eventData);
    }
  }

  /**
   * 处理指针抬起事件
   */
  handlePointerUp(targetId: string | null, position: Vector2D, globalPosition: Vector2D): void {
    const eventData: PointerEventData = {
      position,
      globalPosition,
      button: 0,
      buttons: 0,
      pressure: 0,
      targetId: targetId || undefined,
    };

    this.handleEvent('pointerUp', eventData);

    // 结束拖拽
    if (this.dragState.isDragging && this.dragState.targetId) {
      const distance = Math.sqrt(
        Math.pow(globalPosition.x - this.dragState.startPosition.x, 2) +
        Math.pow(globalPosition.y - this.dragState.startPosition.y, 2)
      );

      this.handleEvent('dragEnd', {
        ...eventData,
        targetId: this.dragState.targetId,
        startPosition: this.dragState.startPosition,
        delta: { x: 0, y: 0 },
        distance,
      } as DragEventData);

      // 检查是否放置在目标上
      if (targetId && targetId !== this.dragState.targetId) {
        this.handleEvent('drop', {
          ...eventData,
          targetId,
        });
      }

      this.dragState = {
        isDragging: false,
        targetId: null,
        startPosition: { x: 0, y: 0 },
        currentPosition: { x: 0, y: 0 },
      };
    }

    // 处理点击
    this.handleEvent('click', eventData);
  }

  /**
   * 处理指针离开事件
   */
  handlePointerOut(targetId: string | null, position: Vector2D, globalPosition: Vector2D): void {
    if (targetId && this.hoverTargets.has(targetId)) {
      this.hoverTargets.delete(targetId);
      this.handleEvent('hoverEnd', {
        position,
        globalPosition,
        button: 0,
        buttons: 0,
        pressure: 0,
        targetId,
      });
    }
  }

  /**
   * 处理通用事件
   */
  handleEvent(type: TriggerType, data: InteractionEventData): void {
    const now = Date.now();

    console.log('InteractionManager: handleEvent', type, 'targetId:', (data as PointerEventData).targetId, 'rules count:', this.rules.size);

    this.rules.forEach((rule, ruleId) => {
      if (!rule.enabled) {
        console.log('  Rule', ruleId, 'is disabled');
        return;
      }
      if (rule.trigger.type !== type) {
        return; // 不打印，太多了
      }

      // 检查目标匹配
      if (rule.trigger.targetId) {
        const eventTargetId = (data as PointerEventData).targetId;
        if (eventTargetId !== rule.trigger.targetId) {
          console.log('  Rule', ruleId, 'targetId mismatch:', eventTargetId, '!==', rule.trigger.targetId);
          return;
        }
      }

      console.log('  Rule', ruleId, 'matched! Executing actions...');

      // 检查执行状态
      const state = this.ruleStates.get(ruleId);
      if (!state) {
        console.log('  Rule', ruleId, 'has no state');
        return;
      }

      // 检查 once
      if (rule.once && state.executedOnce) return;

      // 检查 debounce
      if (rule.debounce && now - state.lastExecutionTime < rule.debounce) return;

      // 检查 throttle
      if (rule.throttle && now - state.lastExecutionTime < rule.throttle) return;

      // 检查条件
      if (rule.conditions && rule.conditions.length > 0) {
        const conditionsMet = rule.conditions.every(condition =>
          this.evaluateCondition(condition)
        );
        if (!conditionsMet) return;
      }

      // 执行动作
      state.lastExecutionTime = now;
      state.executedOnce = true;

      this.executeActions(rule.actions, data);
    });
  }

  // ==================== 条件评估 ====================

  /**
   * 评估条件
   */
  evaluateCondition(condition: InteractionCondition | ConditionGroup): boolean {
    if ('logic' in condition) {
      return this.evaluateConditionGroup(condition);
    }
    return this.evaluateSingleCondition(condition);
  }

  /**
   * 评估条件组
   */
  private evaluateConditionGroup(group: ConditionGroup): boolean {
    if (group.logic === 'and') {
      return group.conditions.every(c => this.evaluateCondition(c));
    } else {
      return group.conditions.some(c => this.evaluateCondition(c));
    }
  }

  /**
   * 评估单个条件
   */
  private evaluateSingleCondition(condition: InteractionCondition): boolean {
    if (!this.context) return false;

    let leftValue: unknown;

    // 获取左值
    switch (condition.type) {
      case 'variable':
        leftValue = this.context.getVariable(condition.left);
        break;
      case 'element':
        const [elementId, ...propertyPath] = condition.left.split('.');
        leftValue = this.context.getElementProperty(elementId, propertyPath.join('.'));
        break;
      default:
        leftValue = condition.left;
    }

    // 评估操作符
    let result = this.evaluateOperator(condition.operator, leftValue, condition.right);

    // 取反
    if (condition.negate) {
      result = !result;
    }

    return result;
  }

  /**
   * 评估操作符
   */
  private evaluateOperator(operator: ConditionOperator, left: unknown, right: unknown): boolean {
    switch (operator) {
      case 'eq':
        return left === right;
      case 'ne':
        return left !== right;
      case 'gt':
        return typeof left === 'number' && typeof right === 'number' && left > right;
      case 'gte':
        return typeof left === 'number' && typeof right === 'number' && left >= right;
      case 'lt':
        return typeof left === 'number' && typeof right === 'number' && left < right;
      case 'lte':
        return typeof left === 'number' && typeof right === 'number' && left <= right;
      case 'contains':
        if (typeof left === 'string' && typeof right === 'string') {
          return left.includes(right);
        }
        if (Array.isArray(left)) {
          return left.includes(right);
        }
        return false;
      case 'in':
        return Array.isArray(right) && right.includes(left);
      case 'between':
        if (typeof left === 'number' && Array.isArray(right) && right.length === 2) {
          return left >= right[0] && left <= right[1];
        }
        return false;
      case 'matches':
        if (typeof left === 'string' && typeof right === 'string') {
          return new RegExp(right).test(left);
        }
        return false;
      case 'exists':
        return left !== undefined && left !== null;
      case 'truthy':
        return Boolean(left);
      case 'falsy':
        return !left;
      default:
        return false;
    }
  }

  // ==================== 动作执行 ====================

  /**
   * 执行动作列表
   */
  async executeActions(actions: InteractionAction[], eventData?: InteractionEventData): Promise<void> {
    for (const action of actions) {
      // 检查动作条件
      if (action.condition && !this.evaluateCondition(action.condition)) {
        continue;
      }

      // 处理延迟
      if (action.delay && action.delay > 0) {
        await this.delay(action.delay);
      }

      await this.executeAction(action, eventData);
    }
  }

  /**
   * 执行单个动作
   */
  async executeAction(action: InteractionAction, eventData?: InteractionEventData): Promise<void> {
    if (!this.context) return;

    const params = action.params;

    switch (action.type) {
      // 变量操作
      case 'setVariable':
        this.context.setVariable(params.name as string, params.value);
        break;

      case 'incrementVariable':
        this.context.incrementVariable(params.name as string, params.amount as number || 1);
        break;

      case 'toggleVariable':
        this.context.toggleVariable(params.name as string);
        break;

      // 元素操作
      case 'setProperty':
        this.context.setElementProperty(
          params.targetId as string,
          params.property as string,
          params.value
        );
        break;

      case 'showElement':
        this.context.setElementVisible(params.targetId as string, true);
        break;

      case 'hideElement':
        this.context.setElementVisible(params.targetId as string, false);
        break;

      case 'toggleElement':
        const currentVisible = this.context.getElementProperty(
          params.targetId as string,
          'visible'
        );
        this.context.setElementVisible(params.targetId as string, !currentVisible);
        break;

      case 'moveElement':
        if (params.position) {
          this.context.setElementPosition(
            params.targetId as string,
            params.position as Vector2D
          );
        } else if (eventData && 'globalPosition' in eventData) {
          // 使用事件位置
          this.context.setElementPosition(
            params.targetId as string,
            (eventData as PointerEventData).globalPosition
          );
        }
        break;

      // 动画操作
      case 'playTimeline':
        this.context.playTimeline(params.timelineId as string);
        break;

      case 'pauseTimeline':
        this.context.pauseTimeline(params.timelineId as string);
        break;

      case 'stopTimeline':
        this.context.stopTimeline(params.timelineId as string);
        break;

      // 场景操作
      case 'resetScene':
        this.context.resetScene();
        break;

      // 事件操作
      case 'triggerEvent':
        this.context.emit({
          type: params.eventName as string,
          data: params.data,
        });
        break;

      // 延迟操作
      case 'delay':
        await this.delay(params.duration as number || 0);
        break;

      case 'sequence':
        if (Array.isArray(params.actions)) {
          await this.executeActions(params.actions as InteractionAction[], eventData);
        }
        break;

      case 'parallel':
        if (Array.isArray(params.actions)) {
          await Promise.all(
            (params.actions as InteractionAction[]).map(a =>
              this.executeAction(a, eventData)
            )
          );
        }
        break;

      // 条件操作
      case 'if':
        if (params.condition && this.evaluateCondition(params.condition as InteractionCondition)) {
          if (Array.isArray(params.then)) {
            await this.executeActions(params.then as InteractionAction[], eventData);
          }
        } else if (Array.isArray(params.else)) {
          await this.executeActions(params.else as InteractionAction[], eventData);
        }
        break;

      // 日志
      case 'log':
        console.log('[InteractionManager]', params.message, params.data || '');
        break;

      // 自定义
      case 'custom':
        if (typeof params.handler === 'function') {
          await params.handler(this.context, eventData);
        }
        break;

      default:
        console.warn(`未知的动作类型: ${action.type}`);
    }
  }

  // ==================== 定时器 ====================

  /**
   * 设置定时器触发器
   */
  private setupTimerTrigger(rule: InteractionRule): void {
    if (rule.trigger.type === 'timer') {
      const delay = (rule.trigger.params?.delay as number) || 1000;
      const timer = setTimeout(() => {
        this.handleEvent('timer', { ruleId: rule.id });
      }, delay);
      this.timers.set(rule.id, timer);
    } else if (rule.trigger.type === 'interval') {
      const interval = (rule.trigger.params?.interval as number) || 1000;
      const timer = setInterval(() => {
        this.handleEvent('interval', { ruleId: rule.id });
      }, interval);
      this.intervals.set(rule.id, timer);
    }
  }

  /**
   * 清除定时器触发器
   */
  private clearTimerTrigger(ruleId: string): void {
    const timer = this.timers.get(ruleId);
    if (timer) {
      clearTimeout(timer);
      this.timers.delete(ruleId);
    }

    const interval = this.intervals.get(ruleId);
    if (interval) {
      clearInterval(interval);
      this.intervals.delete(ruleId);
    }
  }

  // ==================== 工具方法 ====================

  /**
   * 延迟
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 获取当前拖拽状态
   */
  getDragState(): DragState {
    return { ...this.dragState };
  }

  /**
   * 检查元素是否正在被拖拽
   */
  isDragging(elementId?: string): boolean {
    if (elementId) {
      return this.dragState.isDragging && this.dragState.targetId === elementId;
    }
    return this.dragState.isDragging;
  }

  // ==================== 销毁 ====================

  /**
   * 销毁
   */
  destroy(): void {
    // 清除所有定时器
    this.timers.forEach(timer => clearTimeout(timer));
    this.timers.clear();

    this.intervals.forEach(interval => clearInterval(interval));
    this.intervals.clear();

    // 清除状态
    this.rules.clear();
    this.ruleStates.clear();
    this.hoverTargets.clear();
    this.context = null;

    this.dragState = {
      isDragging: false,
      targetId: null,
      startPosition: { x: 0, y: 0 },
      currentPosition: { x: 0, y: 0 },
    };
  }
}

// ==================== 导出单例 ====================

export const interactionManager = new InteractionManager();
