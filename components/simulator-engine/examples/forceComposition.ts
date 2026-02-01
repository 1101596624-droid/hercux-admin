/**
 * 示例场景 - 力的合成模拟器
 */

import type { SceneDefinition } from '@/types/simulator-engine';

export const forceCompositionScene: SceneDefinition = {
  version: '1.0.0',
  id: 'force_composition_demo',
  name: '力的合成模拟器',
  description: '通过拖拽调整两个力的大小和方向，观察合力的变化',

  canvas: {
    width: 800,
    height: 500,
    backgroundColor: '#f8fafc',
    renderer: 'pixi',
    antialias: true,
  },

  assets: {
    icons: [],
    images: [],
    sounds: [],
    fonts: [],
  },

  elements: [
    // 网格背景 (使用矩形模拟)
    {
      id: 'background',
      name: '背景',
      type: 'shape',
      transform: {
        position: { x: 400, y: 250 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 0,
      interactive: false,
      shape: {
        shapeType: 'rectangle',
        width: 780,
        height: 480,
        fill: { type: 'solid', color: '#f1f5f9' },
        stroke: { color: '#e2e8f0', width: 1 },
        cornerRadius: 8,
      },
    },

    // 原点
    {
      id: 'origin',
      name: '原点',
      type: 'shape',
      transform: {
        position: { x: 400, y: 250 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: false,
      shape: {
        shapeType: 'circle',
        radius: 8,
        fill: { type: 'solid', color: '#1e293b' },
      },
    },

    // 原点标签
    {
      id: 'origin_label',
      name: '原点标签',
      type: 'text',
      transform: {
        position: { x: 415, y: 235 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 11,
      interactive: false,
      text: {
        content: 'O',
        fontFamily: 'Arial',
        fontSize: 14,
        fontWeight: 'bold',
        color: '#1e293b',
        align: 'left',
      },
    },

    // 力 F1 (红色)
    {
      id: 'force_f1',
      name: '力 F1',
      type: 'shape',
      transform: {
        position: { x: 400, y: 250 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 5,
      interactive: false,
      shape: {
        shapeType: 'line',
        points: [
          { x: 0, y: 0 },
          { x: 120, y: 0 },
        ],
        stroke: { color: '#ef4444', width: 4, lineCap: 'round' },
      },
    },

    // F1 箭头 (可拖拽)
    {
      id: 'force_f1_handle',
      name: 'F1 控制点',
      type: 'shape',
      transform: {
        position: { x: 520, y: 250 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 20,
      interactive: true,
      shape: {
        shapeType: 'circle',
        radius: 12,
        fill: { type: 'solid', color: '#ef4444' },
        stroke: { color: '#ffffff', width: 2 },
      },
    },

    // F1 标签
    {
      id: 'force_f1_label',
      name: 'F1 标签',
      type: 'text',
      transform: {
        position: { x: 540, y: 235 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 21,
      interactive: false,
      text: {
        content: 'F₁ = 100N',
        fontFamily: 'Arial',
        fontSize: 14,
        fontWeight: 600,
        color: '#ef4444',
        align: 'left',
      },
    },

    // 力 F2 (蓝色)
    {
      id: 'force_f2',
      name: '力 F2',
      type: 'shape',
      transform: {
        position: { x: 400, y: 250 },
        rotation: -45,
        scale: { x: 1, y: 1 },
        anchor: { x: 0, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 5,
      interactive: false,
      shape: {
        shapeType: 'line',
        points: [
          { x: 0, y: 0 },
          { x: 100, y: 0 },
        ],
        stroke: { color: '#3b82f6', width: 4, lineCap: 'round' },
      },
    },

    // F2 箭头 (可拖拽)
    {
      id: 'force_f2_handle',
      name: 'F2 控制点',
      type: 'shape',
      transform: {
        position: { x: 470, y: 180 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 20,
      interactive: true,
      shape: {
        shapeType: 'circle',
        radius: 12,
        fill: { type: 'solid', color: '#3b82f6' },
        stroke: { color: '#ffffff', width: 2 },
      },
    },

    // F2 标签
    {
      id: 'force_f2_label',
      name: 'F2 标签',
      type: 'text',
      transform: {
        position: { x: 485, y: 165 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 21,
      interactive: false,
      text: {
        content: 'F₂ = 80N',
        fontFamily: 'Arial',
        fontSize: 14,
        fontWeight: 600,
        color: '#3b82f6',
        align: 'left',
      },
    },

    // 合力 (绿色虚线)
    {
      id: 'resultant',
      name: '合力',
      type: 'shape',
      transform: {
        position: { x: 400, y: 250 },
        rotation: -20,
        scale: { x: 1, y: 1 },
        anchor: { x: 0, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 6,
      interactive: false,
      shape: {
        shapeType: 'line',
        points: [
          { x: 0, y: 0 },
          { x: 180, y: 0 },
        ],
        stroke: {
          color: '#22c55e',
          width: 5,
          lineCap: 'round',
          dashArray: [10, 5],
        },
      },
    },

    // 合力标签
    {
      id: 'resultant_label',
      name: '合力标签',
      type: 'text',
      transform: {
        position: { x: 520, y: 200 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 21,
      interactive: false,
      text: {
        content: 'R = 156N',
        fontFamily: 'Arial',
        fontSize: 16,
        fontWeight: 'bold',
        color: '#22c55e',
        align: 'left',
      },
    },

    // 说明文字
    {
      id: 'instructions',
      name: '说明',
      type: 'text',
      transform: {
        position: { x: 400, y: 470 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 0.7,
      zIndex: 30,
      interactive: false,
      text: {
        content: '拖拽红色和蓝色控制点调整力的大小和方向',
        fontFamily: 'Arial',
        fontSize: 13,
        color: '#64748b',
        align: 'center',
      },
    },
  ],

  timelines: [],

  interactions: [
    {
      id: 'drag_f1',
      name: '拖拽 F1',
      enabled: true,
      trigger: {
        type: 'drag',
        targetId: 'force_f1_handle',
      },
      actions: [
        {
          type: 'log',
          params: { message: 'F1 被拖拽' },
        },
      ],
    },
    {
      id: 'drag_f2',
      name: '拖拽 F2',
      enabled: true,
      trigger: {
        type: 'drag',
        targetId: 'force_f2_handle',
      },
      actions: [
        {
          type: 'log',
          params: { message: 'F2 被拖拽' },
        },
      ],
    },
  ],

  variables: [
    { id: 'f1_magnitude', name: 'F1 大小', type: 'number', defaultValue: 100 },
    { id: 'f1_angle', name: 'F1 角度', type: 'number', defaultValue: 0 },
    { id: 'f2_magnitude', name: 'F2 大小', type: 'number', defaultValue: 80 },
    { id: 'f2_angle', name: 'F2 角度', type: 'number', defaultValue: 45 },
    { id: 'resultant_magnitude', name: '合力大小', type: 'number', defaultValue: 156 },
    { id: 'resultant_angle', name: '合力角度', type: 'number', defaultValue: 20 },
  ],

  evaluation: {
    criteria: [
      {
        id: 'understand_composition',
        name: '理解力的合成',
        description: '正确调整两个力使合力达到目标值',
        weight: 100,
        rule: {
          type: 'variable',
          expression: 'variables.resultant_magnitude >= 150',
        },
      },
    ],
    passThreshold: 60,
    hints: [
      {
        id: 'hint_drag',
        condition: 'true',
        message: '尝试拖拽控制点来改变力的大小和方向',
        level: 'info',
      },
    ],
  },

  metadata: {
    author: 'HERCU',
    version: '1.0.0',
    tags: ['物理', '力学', '力的合成'],
  },
};

export default forceCompositionScene;
