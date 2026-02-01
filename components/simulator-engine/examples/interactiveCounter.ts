/**
 * 示例场景 - 交互式计数器
 * 展示点击、拖拽等交互功能
 */

import type { SceneDefinition } from '@/types/simulator-engine';

export const interactiveCounterScene: SceneDefinition = {
  version: '1.0.0',
  id: 'interactive_counter_demo',
  name: '交互式计数器',
  description: '点击按钮增加或减少计数，拖拽滑块调整数值',

  canvas: {
    width: 500,
    height: 400,
    backgroundColor: '#0f172a',
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
    // 标题
    {
      id: 'title',
      name: '标题',
      type: 'text',
      transform: {
        position: { x: 250, y: 40 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: false,
      text: {
        content: '交互式计数器',
        fontFamily: 'Arial',
        fontSize: 28,
        fontWeight: 'bold',
        color: '#f8fafc',
        align: 'center',
      },
    },

    // 计数显示背景
    {
      id: 'counter_bg',
      name: '计数背景',
      type: 'shape',
      transform: {
        position: { x: 250, y: 150 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 1,
      interactive: false,
      shape: {
        shapeType: 'rectangle',
        width: 200,
        height: 80,
        fill: { type: 'solid', color: '#1e293b' },
        stroke: { color: '#3b82f6', width: 2 },
        cornerRadius: 12,
      },
    },

    // 计数显示
    {
      id: 'counter_display',
      name: '计数显示',
      type: 'text',
      transform: {
        position: { x: 250, y: 150 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 2,
      interactive: false,
      text: {
        content: '0',
        fontFamily: 'Arial',
        fontSize: 48,
        fontWeight: 'bold',
        color: '#3b82f6',
        align: 'center',
      },
    },

    // 减少按钮
    {
      id: 'btn_decrease',
      name: '减少按钮',
      type: 'shape',
      transform: {
        position: { x: 120, y: 260 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 5,
      interactive: true,
      shape: {
        shapeType: 'circle',
        radius: 35,
        fill: { type: 'solid', color: '#ef4444' },
      },
    },

    // 减少按钮文字
    {
      id: 'btn_decrease_text',
      name: '减少按钮文字',
      type: 'text',
      transform: {
        position: { x: 120, y: 260 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 6,
      interactive: false,
      text: {
        content: '-',
        fontFamily: 'Arial',
        fontSize: 40,
        fontWeight: 'bold',
        color: '#ffffff',
        align: 'center',
      },
    },

    // 增加按钮
    {
      id: 'btn_increase',
      name: '增加按钮',
      type: 'shape',
      transform: {
        position: { x: 380, y: 260 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 5,
      interactive: true,
      shape: {
        shapeType: 'circle',
        radius: 35,
        fill: { type: 'solid', color: '#22c55e' },
      },
    },

    // 增加按钮文字
    {
      id: 'btn_increase_text',
      name: '增加按钮文字',
      type: 'text',
      transform: {
        position: { x: 380, y: 260 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 6,
      interactive: false,
      text: {
        content: '+',
        fontFamily: 'Arial',
        fontSize: 40,
        fontWeight: 'bold',
        color: '#ffffff',
        align: 'center',
      },
    },

    // 重置按钮
    {
      id: 'btn_reset',
      name: '重置按钮',
      type: 'shape',
      transform: {
        position: { x: 250, y: 260 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 5,
      interactive: true,
      shape: {
        shapeType: 'rectangle',
        width: 80,
        height: 50,
        fill: { type: 'solid', color: '#6366f1' },
        cornerRadius: 8,
      },
    },

    // 重置按钮文字
    {
      id: 'btn_reset_text',
      name: '重置按钮文字',
      type: 'text',
      transform: {
        position: { x: 250, y: 260 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 6,
      interactive: false,
      text: {
        content: '重置',
        fontFamily: 'Arial',
        fontSize: 16,
        fontWeight: 'bold',
        color: '#ffffff',
        align: 'center',
      },
    },

    // 可拖拽的球
    {
      id: 'draggable_ball',
      name: '可拖拽球',
      type: 'shape',
      transform: {
        position: { x: 250, y: 350 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: true,
      shape: {
        shapeType: 'circle',
        radius: 25,
        fill: { type: 'solid', color: '#f59e0b' },
        stroke: { color: '#ffffff', width: 3 },
      },
    },

    // 拖拽提示
    {
      id: 'drag_hint',
      name: '拖拽提示',
      type: 'text',
      transform: {
        position: { x: 250, y: 385 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 0.6,
      zIndex: 5,
      interactive: false,
      text: {
        content: '拖拽上方的球',
        fontFamily: 'Arial',
        fontSize: 12,
        color: '#94a3b8',
        align: 'center',
      },
    },
  ],

  timelines: [],

  interactions: [
    // 点击增加按钮
    {
      id: 'click_increase',
      name: '点击增加',
      enabled: true,
      trigger: {
        type: 'click',
        targetId: 'btn_increase',
      },
      actions: [
        {
          type: 'incrementVariable',
          params: { name: 'counter', amount: 1 },
        },
        {
          type: 'log',
          params: { message: '计数增加' },
        },
      ],
    },

    // 点击减少按钮
    {
      id: 'click_decrease',
      name: '点击减少',
      enabled: true,
      trigger: {
        type: 'click',
        targetId: 'btn_decrease',
      },
      actions: [
        {
          type: 'incrementVariable',
          params: { name: 'counter', amount: -1 },
        },
        {
          type: 'log',
          params: { message: '计数减少' },
        },
      ],
    },

    // 点击重置按钮
    {
      id: 'click_reset',
      name: '点击重置',
      enabled: true,
      trigger: {
        type: 'click',
        targetId: 'btn_reset',
      },
      actions: [
        {
          type: 'setVariable',
          params: { name: 'counter', value: 0 },
        },
        {
          type: 'log',
          params: { message: '计数重置' },
        },
      ],
    },

    // 拖拽球
    {
      id: 'drag_ball',
      name: '拖拽球',
      enabled: true,
      trigger: {
        type: 'drag',
        targetId: 'draggable_ball',
      },
      actions: [
        {
          type: 'moveElement',
          params: { targetId: 'draggable_ball' },
        },
      ],
    },

    // 悬停增加按钮
    {
      id: 'hover_increase',
      name: '悬停增加按钮',
      enabled: true,
      trigger: {
        type: 'hover',
        targetId: 'btn_increase',
      },
      actions: [
        {
          type: 'setProperty',
          params: { targetId: 'btn_increase', property: 'scale', value: { x: 1.1, y: 1.1 } },
        },
      ],
    },

    // 离开增加按钮
    {
      id: 'hover_end_increase',
      name: '离开增加按钮',
      enabled: true,
      trigger: {
        type: 'hoverEnd',
        targetId: 'btn_increase',
      },
      actions: [
        {
          type: 'setProperty',
          params: { targetId: 'btn_increase', property: 'scale', value: { x: 1, y: 1 } },
        },
      ],
    },

    // 悬停减少按钮
    {
      id: 'hover_decrease',
      name: '悬停减少按钮',
      enabled: true,
      trigger: {
        type: 'hover',
        targetId: 'btn_decrease',
      },
      actions: [
        {
          type: 'setProperty',
          params: { targetId: 'btn_decrease', property: 'scale', value: { x: 1.1, y: 1.1 } },
        },
      ],
    },

    // 离开减少按钮
    {
      id: 'hover_end_decrease',
      name: '离开减少按钮',
      enabled: true,
      trigger: {
        type: 'hoverEnd',
        targetId: 'btn_decrease',
      },
      actions: [
        {
          type: 'setProperty',
          params: { targetId: 'btn_decrease', property: 'scale', value: { x: 1, y: 1 } },
        },
      ],
    },
  ],

  variables: [
    { id: 'counter', name: '计数器', type: 'number', defaultValue: 0 },
    { id: 'drag_count', name: '拖拽次数', type: 'number', defaultValue: 0 },
  ],

  evaluation: {
    criteria: [
      {
        id: 'reach_10',
        name: '达到10',
        description: '将计数器增加到10',
        weight: 50,
        rule: {
          type: 'variable',
          expression: 'variables.counter >= 10',
        },
      },
      {
        id: 'use_reset',
        name: '使用重置',
        description: '使用重置按钮',
        weight: 50,
        rule: {
          type: 'variable',
          expression: 'variables.counter === 0',
        },
      },
    ],
    passThreshold: 50,
  },

  metadata: {
    author: 'HERCU',
    version: '1.0.0',
    tags: ['交互', '演示', '计数器'],
  },
};

export default interactiveCounterScene;
