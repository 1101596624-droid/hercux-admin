/**
 * 动态曲线系统 - 用于渲染实时计算的曲线（如波浪、脊柱等）
 */

import * as PIXI from 'pixi.js';
import { evaluateFormula } from './FormulaParser';
import type { Vector2D } from '@/types/simulator-engine';

// ==================== 类型定义 ====================

/** 动态曲线配置 */
export interface DynamicCurveConfig {
  id: string;
  segments: number;           // 节点数量
  startY: number;             // 起始Y坐标
  endY: number;               // 结束Y坐标
  baseX: number;              // 基准X坐标
  lineColor: string;          // 线条颜色
  lineWidth: number;          // 线条宽度
  nodeColor: string;          // 节点颜色
  nodeSize: number;           // 节点大小
  glowColor?: string;         // 发光颜色
  glowStrength?: number;      // 发光强度
  smooth?: boolean;           // 是否平滑
  // 公式
  xFormula?: string;          // X坐标公式（支持 index, time, amplitude 等变量）
  sizeFormula?: string;       // 节点大小公式
  glowFormula?: string;       // 发光强度公式
}

/** 曲线节点 */
interface CurveNode {
  x: number;
  y: number;
  size: number;
  glow: number;
}

// ==================== 动态曲线类 ====================

export class DynamicCurve {
  private config: DynamicCurveConfig;
  private container: PIXI.Container;
  private lineGraphics: PIXI.Graphics;
  private nodeGraphics: PIXI.Graphics[];
  private nodes: CurveNode[] = [];

  // 变量
  private variables: Record<string, number> = {};

  constructor(config: DynamicCurveConfig) {
    this.config = config;
    this.container = new PIXI.Container();
    this.lineGraphics = new PIXI.Graphics();
    this.nodeGraphics = [];

    this.container.addChild(this.lineGraphics);
    this.initNodes();
  }

  /**
   * 初始化节点
   */
  private initNodes(): void {
    const { segments, startY, endY, baseX, nodeSize } = this.config;
    const segmentHeight = (endY - startY) / Math.max(segments - 1, 1);

    this.nodes = [];
    this.nodeGraphics = [];

    for (let i = 0; i < segments; i++) {
      const y = startY + i * segmentHeight;

      this.nodes.push({
        x: baseX,
        y: y,
        size: nodeSize,
        glow: 0,
      });

      // 创建节点图形
      const nodeGfx = new PIXI.Graphics();
      this.container.addChild(nodeGfx);
      this.nodeGraphics.push(nodeGfx);
    }
  }

  /**
   * 设置变量
   */
  setVariables(vars: Record<string, number>): void {
    this.variables = { ...vars };
  }

  /**
   * 设置单个变量
   */
  setVariable(name: string, value: number): void {
    this.variables[name] = value;
  }

  /**
   * 更新曲线
   */
  update(): void {
    this.updateNodes();
    this.drawLine();
    this.drawNodes();
  }

  /**
   * 更新节点位置和属性
   */
  private updateNodes(): void {
    const { segments, startY, endY, baseX, nodeSize, xFormula, sizeFormula, glowFormula } = this.config;
    const segmentHeight = (endY - startY) / Math.max(segments - 1, 1);

    for (let i = 0; i < segments; i++) {
      const node = this.nodes[i];
      const vars = {
        ...this.variables,
        index: i,
        count: segments,
        segmentHeight: segmentHeight,
        baseX: baseX,
        startY: startY,
        endY: endY,
      };

      // 计算X坐标
      if (xFormula) {
        node.x = evaluateFormula(xFormula, vars);
      } else {
        node.x = baseX;
      }

      // Y坐标固定
      node.y = startY + i * segmentHeight;

      // 计算节点大小
      if (sizeFormula) {
        node.size = evaluateFormula(sizeFormula, vars);
      } else {
        node.size = nodeSize;
      }

      // 计算发光强度
      if (glowFormula) {
        node.glow = evaluateFormula(glowFormula, vars);
      } else {
        node.glow = 0;
      }
    }
  }

  /**
   * 绘制曲线
   */
  private drawLine(): void {
    const { lineColor, lineWidth, smooth } = this.config;
    const gfx = this.lineGraphics;

    gfx.clear();

    if (this.nodes.length < 2) return;

    const color = this.parseColor(lineColor);

    gfx.moveTo(this.nodes[0].x, this.nodes[0].y);

    if (smooth && this.nodes.length > 2) {
      // 平滑曲线
      for (let i = 1; i < this.nodes.length; i++) {
        const prev = this.nodes[i - 1];
        const curr = this.nodes[i];
        const xc = (prev.x + curr.x) / 2;
        const yc = (prev.y + curr.y) / 2;
        gfx.quadraticCurveTo(prev.x, prev.y, xc, yc);
      }
      // 连接到最后一个点
      const last = this.nodes[this.nodes.length - 1];
      gfx.lineTo(last.x, last.y);
    } else {
      // 直线连接
      for (let i = 1; i < this.nodes.length; i++) {
        gfx.lineTo(this.nodes[i].x, this.nodes[i].y);
      }
    }

    gfx.stroke({ color, width: lineWidth });
  }

  /**
   * 绘制节点
   */
  private drawNodes(): void {
    const { nodeColor, glowColor, glowStrength } = this.config;
    const baseColor = this.parseColor(nodeColor);
    const glow = glowColor ? this.parseColor(glowColor) : baseColor;

    for (let i = 0; i < this.nodes.length; i++) {
      const node = this.nodes[i];
      const gfx = this.nodeGraphics[i];

      gfx.clear();

      // 发光效果
      if (node.glow > 0 && glowStrength) {
        const glowSize = node.size + node.glow * glowStrength / 10;
        gfx.circle(node.x, node.y, glowSize);
        gfx.fill({ color: glow, alpha: 0.3 * (node.glow / 20) });
      }

      // 节点
      gfx.circle(node.x, node.y, node.size);
      gfx.fill({ color: node.glow > 10 ? 0xffffff : baseColor });
    }
  }

  /**
   * 解析颜色
   */
  private parseColor(color: string): number {
    if (color.startsWith('#')) {
      return parseInt(color.slice(1), 16);
    }
    return parseInt(color, 16) || 0xffffff;
  }

  /**
   * 获取容器
   */
  getContainer(): PIXI.Container {
    return this.container;
  }

  /**
   * 获取节点数据
   */
  getNodes(): CurveNode[] {
    return [...this.nodes];
  }

  /**
   * 获取当前波峰索引
   */
  getPeakIndex(): number {
    let peakIndex = 0;
    let maxOffset = -Infinity;

    for (let i = 0; i < this.nodes.length; i++) {
      const offset = this.nodes[i].x - this.config.baseX;
      if (offset > maxOffset) {
        maxOffset = offset;
        peakIndex = i;
      }
    }

    return peakIndex;
  }

  /**
   * 获取进度（0-1）
   */
  getProgress(): number {
    const peakIndex = this.getPeakIndex();
    return this.nodes.length > 1 ? peakIndex / (this.nodes.length - 1) : 0;
  }

  /**
   * 更新配置
   */
  updateConfig(config: Partial<DynamicCurveConfig>): void {
    const segmentsChanged = config.segments !== undefined && config.segments !== this.config.segments;

    this.config = { ...this.config, ...config };

    if (segmentsChanged) {
      // 重新初始化节点
      this.nodeGraphics.forEach(gfx => {
        this.container.removeChild(gfx);
        gfx.destroy();
      });
      this.initNodes();
    }
  }

  /**
   * 销毁
   */
  destroy(): void {
    if (this.lineGraphics) {
      this.lineGraphics.destroy();
    }
    if (this.nodeGraphics) {
      this.nodeGraphics.forEach(gfx => gfx.destroy());
    }
    if (this.container) {
      this.container.destroy();
    }
    this.nodes = [];
  }
}

// ==================== 工厂函数 ====================

/**
 * 创建波浪曲线
 */
export function createWaveCurve(options: {
  id: string;
  x: number;
  startY: number;
  endY: number;
  segments?: number;
  color?: string;
  nodeColor?: string;
}): DynamicCurve {
  return new DynamicCurve({
    id: options.id,
    segments: options.segments || 30,
    startY: options.startY,
    endY: options.endY,
    baseX: options.x,
    lineColor: options.color || '#fbbf24',
    lineWidth: 4,
    nodeColor: options.nodeColor || '#d97706',
    nodeSize: 6,
    glowColor: '#fbbf24',
    glowStrength: 20,
    smooth: true,
    xFormula: 'baseX + sin(time * speed + index * 0.4) * amplitude',
    sizeFormula: '6 + (index < count * 0.3 ? index / count * 10 : (index < count * 0.6 ? 12 - (index / count - 0.3) * 10 : 10 - (index / count - 0.6) * 15))',
    glowFormula: 'abs(sin(time * speed + index * 0.4)) > 0.85 ? 20 : 0',
  });
}
