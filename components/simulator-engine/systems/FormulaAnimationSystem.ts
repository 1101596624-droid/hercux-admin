/**
 * 公式动画系统 - 支持实时计算的动画
 * 每帧根据公式计算元素属性值
 */

import { evaluateFormula, compileFormula } from './FormulaParser';
import type { Vector2D } from '@/types/simulator-engine';

// ==================== 类型定义 ====================

/** 公式动画定义 */
export interface FormulaAnimation {
  id: string;
  target: string;  // 元素ID 或 "dynamic" 表示动态生成
  enabled: boolean;
  properties: {
    [property: string]: string;  // 属性名 -> 公式字符串
  };
}

/** 动态元素组定义 */
export interface DynamicElementGroup {
  id: string;
  countVariable: string;  // 控制数量的变量名
  template: {
    type: string;
    [key: string]: unknown;
  };
  layout: {
    [property: string]: string;  // 属性名 -> 公式字符串（支持 index 变量）
  };
}

/** 计算变量定义 */
export interface ComputedVariable {
  id: string;
  formula: string;
  dependencies?: string[];  // 依赖的变量
}

/** 动画上下文 */
export interface FormulaAnimationContext {
  // 变量操作
  getVariable: (name: string) => number;
  setVariable: (name: string, value: number) => void;

  // 元素操作
  getElementProperty: (elementId: string, property: string) => unknown;
  setElementProperty: (elementId: string, property: string, value: unknown) => void;

  // 动态元素操作
  createDynamicElement?: (groupId: string, index: number, template: Record<string, unknown>) => void;
  removeDynamicElement?: (groupId: string, index: number) => void;
  getDynamicElementCount?: (groupId: string) => number;
}

/** 编译后的公式 */
interface CompiledFormula {
  property: string;
  execute: (variables: Record<string, number>) => number;
}

/** 编译后的动画 */
interface CompiledAnimation {
  id: string;
  target: string;
  enabled: boolean;
  formulas: CompiledFormula[];
}

// ==================== 公式动画系统类 ====================

export class FormulaAnimationSystem {
  private animations: Map<string, CompiledAnimation> = new Map();
  private dynamicGroups: Map<string, DynamicElementGroup> = new Map();
  private computedVariables: Map<string, ComputedVariable> = new Map();
  private context: FormulaAnimationContext | null = null;

  // 内置变量
  private time: number = 0;
  private deltaTime: number = 16;
  private frameCount: number = 0;

  // 性能优化：缓存变量快照
  private variableSnapshot: Record<string, number> = {};

  constructor() {}

  // ==================== 初始化 ====================

  /**
   * 设置动画上下文
   */
  setContext(context: FormulaAnimationContext): void {
    this.context = context;
  }

  /**
   * 加载公式动画
   */
  loadAnimations(animations: FormulaAnimation[]): void {
    this.animations.clear();

    for (const anim of animations) {
      const compiled = this.compileAnimation(anim);
      this.animations.set(anim.id, compiled);
    }
  }

  /**
   * 加载动态元素组
   */
  loadDynamicGroups(groups: DynamicElementGroup[]): void {
    this.dynamicGroups.clear();

    for (const group of groups) {
      this.dynamicGroups.set(group.id, group);
    }
  }

  /**
   * 加载计算变量
   */
  loadComputedVariables(variables: ComputedVariable[]): void {
    this.computedVariables.clear();

    for (const v of variables) {
      this.computedVariables.set(v.id, v);
    }
  }

  /**
   * 编译动画
   */
  private compileAnimation(anim: FormulaAnimation): CompiledAnimation {
    const formulas: CompiledFormula[] = [];

    for (const [property, formula] of Object.entries(anim.properties)) {
      formulas.push({
        property,
        execute: compileFormula(formula),
      });
    }

    return {
      id: anim.id,
      target: anim.target,
      enabled: anim.enabled,
      formulas,
    };
  }

  // ==================== 更新循环 ====================

  /**
   * 更新动画（每帧调用）
   */
  update(deltaTime: number): void {
    if (!this.context) return;

    this.deltaTime = deltaTime;
    this.time += deltaTime / 1000;  // 转换为秒
    this.frameCount++;

    // 更新变量快照
    this.updateVariableSnapshot();

    // 更新计算变量
    this.updateComputedVariables();

    // 更新动态元素组
    this.updateDynamicGroups();

    // 执行公式动画
    this.executeAnimations();
  }

  /**
   * 更新变量快照
   */
  private updateVariableSnapshot(): void {
    if (!this.context) return;

    // 添加内置变量
    this.variableSnapshot = {
      time: this.time,
      deltaTime: this.deltaTime,
      frameCount: this.frameCount,
    };

    // 这里可以从 context 获取用户定义的变量
    // 由于我们不知道所有变量名，需要在使用时动态获取
  }

  /**
   * 获取变量值（带缓存）
   */
  private getVariableValue(name: string): number {
    // 先检查快照
    if (name in this.variableSnapshot) {
      return this.variableSnapshot[name];
    }

    // 从 context 获取
    if (this.context) {
      const value = this.context.getVariable(name);
      this.variableSnapshot[name] = value;
      return value;
    }

    return 0;
  }

  /**
   * 构建变量对象（用于公式执行）
   */
  private buildVariables(extraVars: Record<string, number> = {}): Record<string, number> {
    return {
      ...this.variableSnapshot,
      ...extraVars,
    };
  }

  /**
   * 更新计算变量
   */
  private updateComputedVariables(): void {
    if (!this.context) return;

    for (const [id, computed] of this.computedVariables) {
      try {
        const value = evaluateFormula(computed.formula, this.buildVariables());
        this.context.setVariable(id, value);
        this.variableSnapshot[id] = value;
      } catch (error) {
        console.error(`FormulaAnimationSystem: Error computing variable ${id}:`, error);
      }
    }
  }

  /**
   * 更新动态元素组
   */
  private updateDynamicGroups(): void {
    if (!this.context) return;

    for (const [groupId, group] of this.dynamicGroups) {
      const countVar = this.getVariableValue(group.countVariable);
      const targetCount = Math.floor(countVar);
      const currentCount = this.context.getDynamicElementCount?.(groupId) || 0;

      // 创建或删除元素以匹配目标数量
      if (targetCount > currentCount) {
        for (let i = currentCount; i < targetCount; i++) {
          this.context.createDynamicElement?.(groupId, i, group.template);
        }
      } else if (targetCount < currentCount) {
        for (let i = currentCount - 1; i >= targetCount; i--) {
          this.context.removeDynamicElement?.(groupId, i);
        }
      }

      // 更新每个元素的属性
      for (let i = 0; i < targetCount; i++) {
        const elementId = `${groupId}_${i}`;
        const vars = this.buildVariables({
          index: i,
          count: targetCount,
        });

        for (const [property, formula] of Object.entries(group.layout)) {
          try {
            const value = evaluateFormula(formula, vars);
            this.context.setElementProperty(elementId, property, value);
          } catch (error) {
            console.error(`FormulaAnimationSystem: Error updating dynamic element ${elementId}.${property}:`, error);
          }
        }
      }
    }
  }

  /**
   * 执行公式动画
   */
  private executeAnimations(): void {
    if (!this.context) return;

    for (const [animId, anim] of this.animations) {
      if (!anim.enabled) continue;

      const vars = this.buildVariables();

      for (const formula of anim.formulas) {
        try {
          const value = formula.execute(vars);

          // 解析属性路径（支持 position.x 这样的嵌套属性）
          this.setNestedProperty(anim.target, formula.property, value);
        } catch (error) {
          console.error(`FormulaAnimationSystem: Error executing animation ${animId}.${formula.property}:`, error);
        }
      }
    }
  }

  /**
   * 设置嵌套属性
   */
  private setNestedProperty(elementId: string, propertyPath: string, value: number): void {
    if (!this.context) return;

    const parts = propertyPath.split('.');

    if (parts.length === 1) {
      // 简单属性
      this.context.setElementProperty(elementId, propertyPath, value);
    } else if (parts.length === 2) {
      // 嵌套属性（如 position.x）
      const [parent, child] = parts;
      const current = this.context.getElementProperty(elementId, parent);

      if (typeof current === 'object' && current !== null) {
        const updated = { ...current, [child]: value };
        this.context.setElementProperty(elementId, parent, updated);
      } else {
        // 创建新对象
        this.context.setElementProperty(elementId, parent, { [child]: value });
      }
    }
  }

  // ==================== 控制方法 ====================

  /**
   * 重置时间
   */
  reset(): void {
    this.time = 0;
    this.frameCount = 0;
    this.variableSnapshot = {};
  }

  /**
   * 设置时间
   */
  setTime(time: number): void {
    this.time = time;
  }

  /**
   * 获取当前时间
   */
  getTime(): number {
    return this.time;
  }

  /**
   * 启用/禁用动画
   */
  setAnimationEnabled(animId: string, enabled: boolean): void {
    const anim = this.animations.get(animId);
    if (anim) {
      anim.enabled = enabled;
    }
  }

  /**
   * 添加动画
   */
  addAnimation(animation: FormulaAnimation): void {
    const compiled = this.compileAnimation(animation);
    this.animations.set(animation.id, compiled);
  }

  /**
   * 移除动画
   */
  removeAnimation(animId: string): void {
    this.animations.delete(animId);
  }

  /**
   * 清除所有
   */
  clear(): void {
    this.animations.clear();
    this.dynamicGroups.clear();
    this.computedVariables.clear();
    this.reset();
  }
}
