/**
 * 预设模拟器注册表
 */

import type { SimulatorConfig } from '@/types/editor';

export interface PresetSimulator {
  id: string;
  name: string;
  description: string;
  thumbnail: string;
  category: 'physics' | 'math' | 'biology' | 'other';
  defaultConfig: Omit<SimulatorConfig, 'type' | 'presetId'>;
}

/** 起跑生物力学模拟器 */
export const sprintStartSimulator: PresetSimulator = {
  id: 'sprint-start',
  name: '起跑生物力学',
  description: '调整角度参数，观察对起跑效能的影响',
  thumbnail: '🏃',
  category: 'physics',
  defaultConfig: {
    name: '起跑生物力学交互模拟器',
    description: '调整角度参数，观察对起跑效能的影响',
    inputs: [
      {
        id: 'front-knee',
        name: 'frontKnee',
        label: '前脚膝关节角度',
        type: 'slider',
        defaultValue: 90,
        min: 70,
        max: 110,
        step: 1,
        unit: '°',
        hint: '推荐：90°左右以平衡力量与时间',
      },
      {
        id: 'rear-knee',
        name: 'rearKnee',
        label: '后脚膝关节角度',
        type: 'slider',
        defaultValue: 120,
        min: 100,
        max: 140,
        step: 1,
        unit: '°',
        hint: '推荐：120°-130°提供爆发性初动',
      },
      {
        id: 'com-height',
        name: 'comHeight',
        label: '重心（COM）离地高度',
        type: 'slider',
        defaultValue: 45,
        min: 30,
        max: 60,
        step: 1,
        unit: 'cm',
        hint: '抬高臀部可增加重力势能转化的优势',
      },
    ],
    outputs: [
      {
        id: 'horizontal-power',
        name: 'horizontalPower',
        label: '水平爆发力',
        type: 'progress',
        formula: 'Math.min(100, (100 - Math.abs(input.frontKnee - 90) * 2) * (input.comHeight / 45))',
        color: '#22c55e',
      },
      {
        id: 'coordination',
        name: 'coordination',
        label: '动作协调性',
        type: 'progress',
        formula: 'Math.min(100, 100 - Math.abs(input.rearKnee - 125) - Math.abs(input.frontKnee - 90))',
        color: '#3b82f6',
      },
    ],
    instructions: [
      '调整前脚膝关节角度，观察水平爆发力变化',
      '调整后脚膝关节角度，观察动作协调性变化',
      '尝试找到最佳参数组合',
    ],
  },
};

/** 力学计算器 */
export const forceCalculatorSimulator: PresetSimulator = {
  id: 'force-calculator',
  name: '力学计算器',
  description: 'F = ma 牛顿第二定律演示',
  thumbnail: '⚡',
  category: 'physics',
  defaultConfig: {
    name: '力学计算器',
    description: '通过调整质量和加速度，观察力的变化',
    inputs: [
      {
        id: 'mass',
        name: 'mass',
        label: '质量 (m)',
        type: 'slider',
        defaultValue: 10,
        min: 1,
        max: 100,
        step: 1,
        unit: 'kg',
      },
      {
        id: 'acceleration',
        name: 'acceleration',
        label: '加速度 (a)',
        type: 'slider',
        defaultValue: 5,
        min: 0,
        max: 20,
        step: 0.5,
        unit: 'm/s²',
      },
    ],
    outputs: [
      {
        id: 'force',
        name: 'force',
        label: '力 (F)',
        type: 'number',
        unit: 'N',
        formula: 'input.mass * input.acceleration',
      },
    ],
    instructions: [
      '调整质量和加速度的值',
      '观察力的计算结果',
      '理解 F = ma 的关系',
    ],
  },
};

/** 杠杆平衡模拟器 */
export const leverBalanceSimulator: PresetSimulator = {
  id: 'lever-balance',
  name: '杠杆平衡',
  description: '力矩平衡原理演示',
  thumbnail: '⚖️',
  category: 'physics',
  defaultConfig: {
    name: '杠杆平衡模拟器',
    description: '调整力和力臂，观察杠杆平衡状态',
    inputs: [
      {
        id: 'force1',
        name: 'force1',
        label: '左侧力',
        type: 'slider',
        defaultValue: 10,
        min: 1,
        max: 50,
        step: 1,
        unit: 'N',
      },
      {
        id: 'arm1',
        name: 'arm1',
        label: '左侧力臂',
        type: 'slider',
        defaultValue: 2,
        min: 0.5,
        max: 5,
        step: 0.5,
        unit: 'm',
      },
      {
        id: 'force2',
        name: 'force2',
        label: '右侧力',
        type: 'slider',
        defaultValue: 20,
        min: 1,
        max: 50,
        step: 1,
        unit: 'N',
      },
      {
        id: 'arm2',
        name: 'arm2',
        label: '右侧力臂',
        type: 'slider',
        defaultValue: 1,
        min: 0.5,
        max: 5,
        step: 0.5,
        unit: 'm',
      },
    ],
    outputs: [
      {
        id: 'torque1',
        name: 'torque1',
        label: '左侧力矩',
        type: 'number',
        unit: 'N·m',
        formula: 'input.force1 * input.arm1',
      },
      {
        id: 'torque2',
        name: 'torque2',
        label: '右侧力矩',
        type: 'number',
        unit: 'N·m',
        formula: 'input.force2 * input.arm2',
      },
      {
        id: 'balance',
        name: 'balance',
        label: '平衡状态',
        type: 'text',
        formula: 'Math.abs(input.force1 * input.arm1 - input.force2 * input.arm2) < 0.1 ? "平衡" : (input.force1 * input.arm1 > input.force2 * input.arm2 ? "左倾" : "右倾")',
      },
    ],
    instructions: [
      '调整两侧的力和力臂',
      '观察力矩的变化',
      '尝试使杠杆达到平衡状态',
    ],
  },
};

/** 单位换算器 */
export const unitConverterSimulator: PresetSimulator = {
  id: 'unit-converter',
  name: '单位换算',
  description: '常用物理单位转换',
  thumbnail: '🔄',
  category: 'physics',
  defaultConfig: {
    name: '单位换算器',
    description: '输入数值，自动转换单位',
    inputs: [
      {
        id: 'value',
        name: 'value',
        label: '输入值',
        type: 'number',
        defaultValue: 100,
        min: 0,
        max: 10000,
        step: 1,
      },
      {
        id: 'unit-type',
        name: 'unitType',
        label: '单位类型',
        type: 'select',
        defaultValue: 0,
        options: [
          { label: '米 → 厘米', value: 0 },
          { label: '千克 → 克', value: 1 },
          { label: '秒 → 毫秒', value: 2 },
        ],
      },
    ],
    outputs: [
      {
        id: 'result',
        name: 'result',
        label: '转换结果',
        type: 'number',
        formula: 'input.unitType === 0 ? input.value * 100 : input.unitType === 1 ? input.value * 1000 : input.value * 1000',
      },
    ],
    instructions: [
      '输入要转换的数值',
      '选择单位类型',
      '查看转换结果',
    ],
  },
};

/** 所有预设模拟器 */
export const PRESET_SIMULATORS: PresetSimulator[] = [
  sprintStartSimulator,
  forceCalculatorSimulator,
  leverBalanceSimulator,
  unitConverterSimulator,
];

/** 根据 ID 获取预设模拟器 */
export function getPresetSimulator(id: string): PresetSimulator | undefined {
  return PRESET_SIMULATORS.find(s => s.id === id);
}

/** 获取所有预设模拟器 */
export function getAllPresetSimulators(): PresetSimulator[] {
  return PRESET_SIMULATORS;
}
