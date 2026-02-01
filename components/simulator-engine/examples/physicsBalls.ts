/**
 * 示例场景 - 物理弹球
 * 展示物理引擎的碰撞、重力、弹性效果
 */

import type { SceneDefinition } from '@/types/simulator-engine';

export const physicsBallsScene: SceneDefinition = {
  version: '1.0.0',
  id: 'physics_balls_demo',
  name: '物理弹球',
  description: '点击添加弹球，观察物理碰撞效果',

  canvas: {
    width: 600,
    height: 500,
    backgroundColor: '#1a1a2e',
    renderer: 'pixi',
    antialias: true,
  },

  assets: {
    icons: [],
    images: [],
    sounds: [],
    fonts: [],
  },

  // 物理世界配置
  physics: {
    gravity: { x: 0, y: 500 },
    enableSleeping: true,
    bounds: {
      min: { x: 0, y: 0 },
      max: { x: 600, y: 500 },
    },
  },

  elements: [
    // 标题
    {
      id: 'title',
      name: '标题',
      type: 'text',
      transform: {
        position: { x: 300, y: 30 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 100,
      interactive: false,
      text: {
        content: '物理弹球演示',
        fontFamily: 'Arial',
        fontSize: 24,
        fontWeight: 'bold',
        color: '#ffffff',
        align: 'center',
      },
    },

    // 说明
    {
      id: 'instructions',
      name: '说明',
      type: 'text',
      transform: {
        position: { x: 300, y: 60 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 0.7,
      zIndex: 100,
      interactive: false,
      text: {
        content: '点击播放按钮开始物理模拟',
        fontFamily: 'Arial',
        fontSize: 14,
        color: '#94a3b8',
        align: 'center',
      },
    },

    // 地面
    {
      id: 'ground',
      name: '地面',
      type: 'physics_body',
      transform: {
        position: { x: 300, y: 480 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 1,
      interactive: false,
      physics: {
        bodyType: 'static',
        shape: {
          type: 'rectangle',
          width: 600,
          height: 40,
        },
        friction: 0.3,
        restitution: 0.5,
      },
    },

    // 左墙
    {
      id: 'wall_left',
      name: '左墙',
      type: 'physics_body',
      transform: {
        position: { x: 10, y: 250 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 1,
      interactive: false,
      physics: {
        bodyType: 'static',
        shape: {
          type: 'rectangle',
          width: 20,
          height: 500,
        },
        friction: 0.1,
        restitution: 0.8,
      },
    },

    // 右墙
    {
      id: 'wall_right',
      name: '右墙',
      type: 'physics_body',
      transform: {
        position: { x: 590, y: 250 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 1,
      interactive: false,
      physics: {
        bodyType: 'static',
        shape: {
          type: 'rectangle',
          width: 20,
          height: 500,
        },
        friction: 0.1,
        restitution: 0.8,
      },
    },

    // 斜坡平台 1
    {
      id: 'platform_1',
      name: '斜坡平台1',
      type: 'physics_body',
      transform: {
        position: { x: 150, y: 200 },
        rotation: 15,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 2,
      interactive: false,
      physics: {
        bodyType: 'static',
        shape: {
          type: 'rectangle',
          width: 200,
          height: 15,
        },
        friction: 0.2,
        restitution: 0.6,
      },
    },

    // 斜坡平台 2
    {
      id: 'platform_2',
      name: '斜坡平台2',
      type: 'physics_body',
      transform: {
        position: { x: 450, y: 300 },
        rotation: -15,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 2,
      interactive: false,
      physics: {
        bodyType: 'static',
        shape: {
          type: 'rectangle',
          width: 200,
          height: 15,
        },
        friction: 0.2,
        restitution: 0.6,
      },
    },

    // 弹球 1 (红色)
    {
      id: 'ball_1',
      name: '弹球1',
      type: 'physics_body',
      transform: {
        position: { x: 100, y: 100 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: true,
      physics: {
        bodyType: 'dynamic',
        shape: {
          type: 'circle',
          radius: 25,
        },
        mass: 1,
        friction: 0.1,
        restitution: 0.9,
        linearVelocity: { x: 100, y: 0 },
      },
    },

    // 弹球 2 (蓝色)
    {
      id: 'ball_2',
      name: '弹球2',
      type: 'physics_body',
      transform: {
        position: { x: 300, y: 80 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: true,
      physics: {
        bodyType: 'dynamic',
        shape: {
          type: 'circle',
          radius: 30,
        },
        mass: 1.5,
        friction: 0.1,
        restitution: 0.85,
      },
    },

    // 弹球 3 (绿色)
    {
      id: 'ball_3',
      name: '弹球3',
      type: 'physics_body',
      transform: {
        position: { x: 500, y: 100 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: true,
      physics: {
        bodyType: 'dynamic',
        shape: {
          type: 'circle',
          radius: 20,
        },
        mass: 0.8,
        friction: 0.05,
        restitution: 0.95,
        linearVelocity: { x: -80, y: 50 },
      },
    },

    // 方块
    {
      id: 'box_1',
      name: '方块',
      type: 'physics_body',
      transform: {
        position: { x: 300, y: 380 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: true,
      physics: {
        bodyType: 'dynamic',
        shape: {
          type: 'rectangle',
          width: 50,
          height: 50,
        },
        mass: 2,
        friction: 0.3,
        restitution: 0.4,
      },
    },

    // 渲染用的形状元素 - 地面
    {
      id: 'ground_render',
      name: '地面渲染',
      type: 'shape',
      transform: {
        position: { x: 300, y: 480 },
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
        width: 600,
        height: 40,
        fill: { type: 'solid', color: '#4a5568' },
      },
    },

    // 渲染用的形状元素 - 左墙
    {
      id: 'wall_left_render',
      name: '左墙渲染',
      type: 'shape',
      transform: {
        position: { x: 10, y: 250 },
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
        width: 20,
        height: 500,
        fill: { type: 'solid', color: '#4a5568' },
      },
    },

    // 渲染用的形状元素 - 右墙
    {
      id: 'wall_right_render',
      name: '右墙渲染',
      type: 'shape',
      transform: {
        position: { x: 590, y: 250 },
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
        width: 20,
        height: 500,
        fill: { type: 'solid', color: '#4a5568' },
      },
    },

    // 渲染用的形状元素 - 平台1
    {
      id: 'platform_1_render',
      name: '平台1渲染',
      type: 'shape',
      transform: {
        position: { x: 150, y: 200 },
        rotation: 15,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 2,
      interactive: false,
      shape: {
        shapeType: 'rectangle',
        width: 200,
        height: 15,
        fill: { type: 'solid', color: '#6366f1' },
        cornerRadius: 4,
      },
    },

    // 渲染用的形状元素 - 平台2
    {
      id: 'platform_2_render',
      name: '平台2渲染',
      type: 'shape',
      transform: {
        position: { x: 450, y: 300 },
        rotation: -15,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 2,
      interactive: false,
      shape: {
        shapeType: 'rectangle',
        width: 200,
        height: 15,
        fill: { type: 'solid', color: '#6366f1' },
        cornerRadius: 4,
      },
    },

    // 渲染用的形状元素 - 弹球1
    {
      id: 'ball_1_render',
      name: '弹球1渲染',
      type: 'shape',
      transform: {
        position: { x: 100, y: 100 },
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
        radius: 25,
        fill: { type: 'solid', color: '#ef4444' },
      },
    },

    // 渲染用的形状元素 - 弹球2
    {
      id: 'ball_2_render',
      name: '弹球2渲染',
      type: 'shape',
      transform: {
        position: { x: 300, y: 80 },
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
        radius: 30,
        fill: { type: 'solid', color: '#3b82f6' },
      },
    },

    // 渲染用的形状元素 - 弹球3
    {
      id: 'ball_3_render',
      name: '弹球3渲染',
      type: 'shape',
      transform: {
        position: { x: 500, y: 100 },
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
        radius: 20,
        fill: { type: 'solid', color: '#22c55e' },
      },
    },

    // 渲染用的形状元素 - 方块
    {
      id: 'box_1_render',
      name: '方块渲染',
      type: 'shape',
      transform: {
        position: { x: 300, y: 380 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: false,
      shape: {
        shapeType: 'rectangle',
        width: 50,
        height: 50,
        fill: { type: 'solid', color: '#f59e0b' },
        cornerRadius: 4,
      },
    },
  ],

  timelines: [],

  interactions: [],

  variables: [
    { id: 'collision_count', name: '碰撞次数', type: 'number', defaultValue: 0 },
  ],

  metadata: {
    author: 'HERCU',
    version: '1.0.0',
    tags: ['物理', '演示', '碰撞'],
  },
};

export default physicsBallsScene;
