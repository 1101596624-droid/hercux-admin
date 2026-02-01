/**
 * 示例场景 - 带动画的弹跳球
 */

import type { SceneDefinition } from '@/types/simulator-engine';

export const bouncingBallScene: SceneDefinition = {
  version: '1.0.0',
  id: 'bouncing_ball_demo',
  name: '弹跳球动画演示',
  description: '展示动画系统的弹跳球效果',

  canvas: {
    width: 600,
    height: 400,
    backgroundColor: '#1e293b',
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
    // 地面
    {
      id: 'ground',
      name: '地面',
      type: 'shape',
      transform: {
        position: { x: 300, y: 380 },
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
        width: 580,
        height: 20,
        fill: { type: 'solid', color: '#475569' },
        cornerRadius: 4,
      },
    },

    // 弹跳球
    {
      id: 'ball',
      name: '弹跳球',
      type: 'shape',
      transform: {
        position: { x: 300, y: 100 },
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
        radius: 30,
        fill: { type: 'solid', color: '#f97316' },
      },
    },

    // 球的阴影
    {
      id: 'ball_shadow',
      name: '球阴影',
      type: 'shape',
      transform: {
        position: { x: 300, y: 365 },
        rotation: 0,
        scale: { x: 1, y: 0.3 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 0.3,
      zIndex: 5,
      interactive: false,
      shape: {
        shapeType: 'ellipse',
        radiusX: 30,
        radiusY: 30,
        fill: { type: 'solid', color: '#000000' },
      },
    },

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
      zIndex: 20,
      interactive: false,
      text: {
        content: '弹跳球动画演示',
        fontFamily: 'Arial',
        fontSize: 24,
        fontWeight: 'bold',
        color: '#f8fafc',
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
      zIndex: 20,
      interactive: false,
      text: {
        content: '点击播放按钮观看弹跳动画',
        fontFamily: 'Arial',
        fontSize: 14,
        color: '#94a3b8',
        align: 'center',
      },
    },
  ],

  timelines: [
    {
      id: 'bounce_animation',
      name: '弹跳动画',
      duration: 2000,
      loop: true,
      autoPlay: false,
      tracks: [
        // 球的垂直位置
        {
          id: 'ball_y',
          targetId: 'ball',
          property: 'position.y',
          keyframes: [
            { time: 0, value: 100, easing: 'easeInQuad' },
            { time: 500, value: 340, easing: 'easeOutQuad' },
            { time: 1000, value: 100, easing: 'easeInQuad' },
            { time: 1500, value: 340, easing: 'easeOutQuad' },
            { time: 2000, value: 100 },
          ],
        },
        // 球的挤压效果 (Y 缩放)
        {
          id: 'ball_scale_y',
          targetId: 'ball',
          property: 'scale.y',
          keyframes: [
            { time: 0, value: 1, easing: 'linear' },
            { time: 450, value: 1, easing: 'easeOutQuad' },
            { time: 500, value: 0.7, easing: 'easeOutQuad' },
            { time: 600, value: 1.1, easing: 'easeOutElastic' },
            { time: 800, value: 1, easing: 'linear' },
            { time: 1450, value: 1, easing: 'easeOutQuad' },
            { time: 1500, value: 0.7, easing: 'easeOutQuad' },
            { time: 1600, value: 1.1, easing: 'easeOutElastic' },
            { time: 1800, value: 1 },
          ],
        },
        // 球的挤压效果 (X 缩放)
        {
          id: 'ball_scale_x',
          targetId: 'ball',
          property: 'scale.x',
          keyframes: [
            { time: 0, value: 1, easing: 'linear' },
            { time: 450, value: 1, easing: 'easeOutQuad' },
            { time: 500, value: 1.3, easing: 'easeOutQuad' },
            { time: 600, value: 0.9, easing: 'easeOutElastic' },
            { time: 800, value: 1, easing: 'linear' },
            { time: 1450, value: 1, easing: 'easeOutQuad' },
            { time: 1500, value: 1.3, easing: 'easeOutQuad' },
            { time: 1600, value: 0.9, easing: 'easeOutElastic' },
            { time: 1800, value: 1 },
          ],
        },
        // 阴影缩放
        {
          id: 'shadow_scale',
          targetId: 'ball_shadow',
          property: 'scale.x',
          keyframes: [
            { time: 0, value: 0.5, easing: 'easeInQuad' },
            { time: 500, value: 1.2, easing: 'easeOutQuad' },
            { time: 1000, value: 0.5, easing: 'easeInQuad' },
            { time: 1500, value: 1.2, easing: 'easeOutQuad' },
            { time: 2000, value: 0.5 },
          ],
        },
        // 阴影透明度
        {
          id: 'shadow_opacity',
          targetId: 'ball_shadow',
          property: 'opacity',
          keyframes: [
            { time: 0, value: 0.1, easing: 'easeInQuad' },
            { time: 500, value: 0.4, easing: 'easeOutQuad' },
            { time: 1000, value: 0.1, easing: 'easeInQuad' },
            { time: 1500, value: 0.4, easing: 'easeOutQuad' },
            { time: 2000, value: 0.1 },
          ],
        },
      ],
    },
  ],

  interactions: [],

  variables: [
    { id: 'bounce_count', name: '弹跳次数', type: 'number', defaultValue: 0 },
  ],

  metadata: {
    author: 'HERCU',
    version: '1.0.0',
    tags: ['动画', '演示', '弹跳'],
  },
};

export default bouncingBallScene;
