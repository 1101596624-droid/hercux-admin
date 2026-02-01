/**
 * 阶段指示器 - 显示当前进度所处的阶段
 */

import * as PIXI from 'pixi.js';

// ==================== 类型定义 ====================

/** 阶段定义 */
export interface Stage {
  id: string;
  label: string;
  sublabel?: string;
  range: [number, number];  // [start, end] 范围 0-1
  color?: string;
  activeColor?: string;
}

/** 阶段指示器配置 */
export interface StageIndicatorConfig {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  stages: Stage[];
  gap?: number;
  borderRadius?: number;
  backgroundColor?: string;
  borderColor?: string;
  activeBorderColor?: string;
  textColor?: string;
  activeTextColor?: string;
  fontSize?: number;
  fontFamily?: string;
}

// ==================== 阶段指示器类 ====================

export class StageIndicator {
  private config: StageIndicatorConfig;
  private container: PIXI.Container;
  private stageContainers: Map<string, PIXI.Container> = new Map();
  private stageBackgrounds: Map<string, PIXI.Graphics> = new Map();
  private stageTexts: Map<string, PIXI.Text> = new Map();
  private stageSublabels: Map<string, PIXI.Text> = new Map();
  private currentStageId: string | null = null;

  constructor(config: StageIndicatorConfig) {
    this.config = {
      gap: 10,
      borderRadius: 8,
      backgroundColor: 'transparent',
      borderColor: '#475569',
      activeBorderColor: '#fbbf24',
      textColor: '#94a3b8',
      activeTextColor: '#fbbf24',
      fontSize: 12,
      fontFamily: 'Arial, sans-serif',
      ...config,
    };

    this.container = new PIXI.Container();
    this.container.position.set(config.x, config.y);

    this.createStages();
  }

  /**
   * 创建阶段元素
   */
  private createStages(): void {
    const { stages, width, height, gap } = this.config;
    const stageCount = stages.length;
    const stageWidth = (width - (stageCount - 1) * gap!) / stageCount;

    stages.forEach((stage, index) => {
      const x = index * (stageWidth + gap!);

      // 容器
      const stageContainer = new PIXI.Container();
      stageContainer.position.set(x, 0);
      this.container.addChild(stageContainer);
      this.stageContainers.set(stage.id, stageContainer);

      // 背景
      const bg = new PIXI.Graphics();
      this.drawStageBackground(bg, stageWidth, height, false);
      stageContainer.addChild(bg);
      this.stageBackgrounds.set(stage.id, bg);

      // 主标签
      const labelText = new PIXI.Text({
        text: stage.label,
        style: {
          fontFamily: this.config.fontFamily,
          fontSize: this.config.fontSize,
          fontWeight: 'bold',
          fill: this.config.textColor,
        },
      });
      labelText.anchor.set(0.5, 0.5);
      labelText.position.set(stageWidth / 2, height / 2 - (stage.sublabel ? 8 : 0));
      stageContainer.addChild(labelText);
      this.stageTexts.set(stage.id, labelText);

      // 副标签
      if (stage.sublabel) {
        const sublabelText = new PIXI.Text({
          text: stage.sublabel,
          style: {
            fontFamily: this.config.fontFamily,
            fontSize: this.config.fontSize! - 2,
            fill: this.config.textColor,
          },
        });
        sublabelText.anchor.set(0.5, 0.5);
        sublabelText.alpha = 0.7;
        sublabelText.position.set(stageWidth / 2, height / 2 + 10);
        stageContainer.addChild(sublabelText);
        this.stageSublabels.set(stage.id, sublabelText);
      }
    });
  }

  /**
   * 绘制阶段背景
   */
  private drawStageBackground(
    graphics: PIXI.Graphics,
    width: number,
    height: number,
    active: boolean
  ): void {
    const { borderRadius, backgroundColor, borderColor, activeBorderColor } = this.config;

    graphics.clear();

    // 背景
    if (backgroundColor && backgroundColor !== 'transparent') {
      const bgColor = this.parseColor(backgroundColor);
      graphics.roundRect(0, 0, width, height, borderRadius!);
      graphics.fill({ color: bgColor, alpha: active ? 0.1 : 0.05 });
    }

    // 边框
    const strokeColor = this.parseColor(active ? activeBorderColor! : borderColor!);
    graphics.roundRect(0, 0, width, height, borderRadius!);
    graphics.stroke({ color: strokeColor, width: active ? 2 : 1 });
  }

  /**
   * 更新进度
   */
  setProgress(progress: number): void {
    const { stages } = this.config;

    // 找到当前阶段
    let activeStage: Stage | null = null;
    for (const stage of stages) {
      if (progress >= stage.range[0] && progress < stage.range[1]) {
        activeStage = stage;
        break;
      }
    }

    // 如果进度为1，选择最后一个阶段
    if (progress >= 1 && stages.length > 0) {
      activeStage = stages[stages.length - 1];
    }

    const newStageId = activeStage?.id || null;

    // 如果阶段没变，不更新
    if (newStageId === this.currentStageId) return;

    // 更新样式
    this.updateStageStyles(newStageId);
    this.currentStageId = newStageId;
  }

  /**
   * 更新阶段样式
   */
  private updateStageStyles(activeStageId: string | null): void {
    const { stages, width, height, gap, textColor, activeTextColor } = this.config;
    const stageCount = stages.length;
    const stageWidth = (width - (stageCount - 1) * gap!) / stageCount;

    for (const stage of stages) {
      const isActive = stage.id === activeStageId;
      const bg = this.stageBackgrounds.get(stage.id);
      const text = this.stageTexts.get(stage.id);
      const sublabel = this.stageSublabels.get(stage.id);

      if (bg) {
        this.drawStageBackground(bg, stageWidth, height, isActive);
      }

      if (text) {
        text.style.fill = (isActive ? activeTextColor : textColor) as string;
      }

      if (sublabel) {
        sublabel.style.fill = (isActive ? activeTextColor : textColor) as string;
        sublabel.alpha = isActive ? 1 : 0.7;
      }
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
   * 获取当前阶段ID
   */
  getCurrentStageId(): string | null {
    return this.currentStageId;
  }

  /**
   * 更新配置
   */
  updateConfig(config: Partial<StageIndicatorConfig>): void {
    this.config = { ...this.config, ...config };

    // 重新创建
    this.stageContainers.forEach(c => c.destroy());
    this.stageContainers.clear();
    this.stageBackgrounds.clear();
    this.stageTexts.clear();
    this.stageSublabels.clear();

    this.createStages();
    if (this.currentStageId) {
      this.updateStageStyles(this.currentStageId);
    }
  }

  /**
   * 销毁
   */
  destroy(): void {
    if (this.container) {
      this.container.destroy({ children: true });
    }
    this.stageContainers.clear();
    this.stageBackgrounds.clear();
    this.stageTexts.clear();
    this.stageSublabels.clear();
  }
}

// ==================== 工厂函数 ====================

/**
 * 创建默认阶段指示器
 */
export function createStageIndicator(options: {
  id: string;
  x: number;
  y: number;
  stages: Array<{ label: string; sublabel?: string }>;
  width?: number;
}): StageIndicator {
  const stageCount = options.stages.length;
  const rangeStep = 1 / stageCount;

  const stages: Stage[] = options.stages.map((s, i) => ({
    id: `stage-${i + 1}`,
    label: s.label,
    sublabel: s.sublabel,
    range: [i * rangeStep, (i + 1) * rangeStep] as [number, number],
  }));

  return new StageIndicator({
    id: options.id,
    x: options.x,
    y: options.y,
    width: options.width || 600,
    height: 50,
    stages,
  });
}
