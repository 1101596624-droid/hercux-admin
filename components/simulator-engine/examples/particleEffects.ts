/**
 * 示例场景 - 粒子效果展示
 * 展示火焰、烟雾、星光、爆炸等粒子效果
 */

import type { SceneDefinition } from '@/types/simulator-engine';

export const particleEffectsScene: SceneDefinition = {
  version: '1.0.0',
  id: 'particle_effects_demo',
  name: '粒子效果展示',
  description: '点击不同区域触发各种粒子效果',

  canvas: {
    width: 800,
    height: 600,
    backgroundColor: '#0a0a1a',
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
        position: { x: 400, y: 30 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 100,
      interactive: false,
      text: {
        content: '粒子效果展示',
        fontFamily: 'Arial',
        fontSize: 28,
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
        position: { x: 400, y: 60 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 0.7,
      zIndex: 100,
      interactive: false,
      text: {
        content: '点击下方按钮触发不同的粒子效果',
        fontFamily: 'Arial',
        fontSize: 14,
        color: '#94a3b8',
        align: 'center',
      },
    },

    // ==================== 火焰效果区域 ====================
    {
      id: 'fire_zone_bg',
      name: '火焰区域背景',
      type: 'shape',
      transform: {
        position: { x: 150, y: 200 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 0.3,
      zIndex: 1,
      interactive: false,
      shape: {
        shapeType: 'rectangle',
        width: 200,
        height: 200,
        fill: { type: 'solid', color: '#ff4400' },
        cornerRadius: 12,
      },
    },

    {
      id: 'fire_label',
      name: '火焰标签',
      type: 'text',
      transform: {
        position: { x: 150, y: 110 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: false,
      text: {
        content: '🔥 火焰',
        fontFamily: 'Arial',
        fontSize: 18,
        fontWeight: 'bold',
        color: '#ff6b35',
        align: 'center',
      },
    },

    // 火焰粒子发射器
    {
      id: 'fire_emitter',
      name: '火焰发射器',
      type: 'particle_emitter',
      transform: {
        position: { x: 150, y: 280 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 50,
      interactive: false,
      emitter: {
        emissionRate: 50,
        maxParticles: 200,
        emitterShape: 'rectangle',
        emitterSize: { x: 60, y: 10 },
        emitterAngle: { min: -100, max: -80 },
        lifetime: { min: 500, max: 1000 },
        startColor: { r: 255, g: 200, b: 50, a: 1 },
        endColor: { r: 255, g: 50, b: 0, a: 0 },
        startSize: { min: 15, max: 30 },
        endSize: { min: 3, max: 8 },
        startRotation: { min: 0, max: 360 },
        rotationSpeed: { min: -50, max: 50 },
        startSpeed: { min: 40, max: 80 },
        gravity: { x: 0, y: -40 },
        blendMode: 'add',
        autoStart: true,
      },
    },

    // ==================== 烟雾效果区域 ====================
    {
      id: 'smoke_zone_bg',
      name: '烟雾区域背景',
      type: 'shape',
      transform: {
        position: { x: 400, y: 200 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 0.3,
      zIndex: 1,
      interactive: false,
      shape: {
        shapeType: 'rectangle',
        width: 200,
        height: 200,
        fill: { type: 'solid', color: '#666666' },
        cornerRadius: 12,
      },
    },

    {
      id: 'smoke_label',
      name: '烟雾标签',
      type: 'text',
      transform: {
        position: { x: 400, y: 110 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: false,
      text: {
        content: '💨 烟雾',
        fontFamily: 'Arial',
        fontSize: 18,
        fontWeight: 'bold',
        color: '#9ca3af',
        align: 'center',
      },
    },

    // 烟雾粒子发射器
    {
      id: 'smoke_emitter',
      name: '烟雾发射器',
      type: 'particle_emitter',
      transform: {
        position: { x: 400, y: 280 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 50,
      interactive: false,
      emitter: {
        emissionRate: 15,
        maxParticles: 80,
        emitterShape: 'circle',
        emitterSize: { x: 30, y: 30 },
        emitterAngle: { min: -110, max: -70 },
        lifetime: { min: 2000, max: 4000 },
        startColor: { r: 80, g: 80, b: 80, a: 0.6 },
        endColor: { r: 120, g: 120, b: 120, a: 0 },
        startSize: { min: 25, max: 40 },
        endSize: { min: 60, max: 100 },
        startRotation: { min: 0, max: 360 },
        rotationSpeed: { min: -15, max: 15 },
        startSpeed: { min: 15, max: 30 },
        gravity: { x: 0, y: -15 },
        blendMode: 'normal',
        autoStart: true,
      },
    },

    // ==================== 星光效果区域 ====================
    {
      id: 'sparkle_zone_bg',
      name: '星光区域背景',
      type: 'shape',
      transform: {
        position: { x: 650, y: 200 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 0.3,
      zIndex: 1,
      interactive: false,
      shape: {
        shapeType: 'rectangle',
        width: 200,
        height: 200,
        fill: { type: 'solid', color: '#4444ff' },
        cornerRadius: 12,
      },
    },

    {
      id: 'sparkle_label',
      name: '星光标签',
      type: 'text',
      transform: {
        position: { x: 650, y: 110 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: false,
      text: {
        content: '✨ 星光',
        fontFamily: 'Arial',
        fontSize: 18,
        fontWeight: 'bold',
        color: '#a5b4fc',
        align: 'center',
      },
    },

    // 星光粒子发射器
    {
      id: 'sparkle_emitter',
      name: '星光发射器',
      type: 'particle_emitter',
      transform: {
        position: { x: 650, y: 200 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 50,
      interactive: false,
      emitter: {
        emissionRate: 25,
        maxParticles: 120,
        emitterShape: 'circle',
        emitterSize: { x: 150, y: 150 },
        lifetime: { min: 400, max: 1000 },
        startColor: { r: 255, g: 255, b: 220, a: 1 },
        endColor: { r: 200, g: 200, b: 255, a: 0 },
        startSize: { min: 4, max: 12 },
        endSize: { min: 0, max: 2 },
        startRotation: { min: 0, max: 360 },
        rotationSpeed: { min: -80, max: 80 },
        startSpeed: { min: 5, max: 20 },
        gravity: { x: 0, y: 15 },
        blendMode: 'add',
        autoStart: true,
      },
    },

    // ==================== 爆炸效果区域 ====================
    {
      id: 'explosion_zone_bg',
      name: '爆炸区域背景',
      type: 'shape',
      transform: {
        position: { x: 275, y: 450 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 0.3,
      zIndex: 1,
      interactive: false,
      shape: {
        shapeType: 'rectangle',
        width: 250,
        height: 180,
        fill: { type: 'solid', color: '#ff0044' },
        cornerRadius: 12,
      },
    },

    {
      id: 'explosion_label',
      name: '爆炸标签',
      type: 'text',
      transform: {
        position: { x: 275, y: 370 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: false,
      text: {
        content: '💥 爆炸 (点击触发)',
        fontFamily: 'Arial',
        fontSize: 18,
        fontWeight: 'bold',
        color: '#f87171',
        align: 'center',
      },
    },

    // 爆炸触发按钮
    {
      id: 'explosion_btn',
      name: '爆炸按钮',
      type: 'shape',
      transform: {
        position: { x: 275, y: 450 },
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
        radius: 50,
        fill: { type: 'solid', color: '#dc2626' },
        stroke: { color: '#fca5a5', width: 3 },
      },
    },

    {
      id: 'explosion_btn_text',
      name: '爆炸按钮文字',
      type: 'text',
      transform: {
        position: { x: 275, y: 450 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 21,
      interactive: false,
      text: {
        content: 'BOOM',
        fontFamily: 'Arial',
        fontSize: 20,
        fontWeight: 'bold',
        color: '#ffffff',
        align: 'center',
      },
    },

    // 爆炸粒子发射器 (手动触发)
    {
      id: 'explosion_emitter',
      name: '爆炸发射器',
      type: 'particle_emitter',
      transform: {
        position: { x: 275, y: 450 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 60,
      interactive: false,
      emitter: {
        emissionRate: 0, // 手动触发
        maxParticles: 150,
        emitterShape: 'point',
        emitterSize: { x: 0, y: 0 },
        emitterAngle: { min: 0, max: 360 },
        lifetime: { min: 600, max: 1200 },
        startColor: { r: 255, g: 200, b: 100, a: 1 },
        endColor: { r: 255, g: 80, b: 30, a: 0 },
        startSize: { min: 8, max: 25 },
        endSize: { min: 2, max: 6 },
        startRotation: { min: 0, max: 360 },
        rotationSpeed: { min: -150, max: 150 },
        startSpeed: { min: 150, max: 350 },
        gravity: { x: 0, y: 150 },
        blendMode: 'add',
        autoStart: false,
      },
    },

    // ==================== 雪花效果区域 ====================
    {
      id: 'snow_zone_bg',
      name: '雪花区域背景',
      type: 'shape',
      transform: {
        position: { x: 575, y: 450 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 0.3,
      zIndex: 1,
      interactive: false,
      shape: {
        shapeType: 'rectangle',
        width: 250,
        height: 180,
        fill: { type: 'solid', color: '#00aaff' },
        cornerRadius: 12,
      },
    },

    {
      id: 'snow_label',
      name: '雪花标签',
      type: 'text',
      transform: {
        position: { x: 575, y: 370 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: false,
      text: {
        content: '❄️ 雪花',
        fontFamily: 'Arial',
        fontSize: 18,
        fontWeight: 'bold',
        color: '#7dd3fc',
        align: 'center',
      },
    },

    // 雪花粒子发射器
    {
      id: 'snow_emitter',
      name: '雪花发射器',
      type: 'particle_emitter',
      transform: {
        position: { x: 575, y: 370 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 50,
      interactive: false,
      emitter: {
        emissionRate: 20,
        maxParticles: 100,
        emitterShape: 'rectangle',
        emitterSize: { x: 200, y: 10 },
        emitterAngle: { min: 80, max: 100 },
        lifetime: { min: 3000, max: 5000 },
        startColor: { r: 255, g: 255, b: 255, a: 0.9 },
        endColor: { r: 200, g: 220, b: 255, a: 0.3 },
        startSize: { min: 4, max: 10 },
        endSize: { min: 2, max: 6 },
        startRotation: { min: 0, max: 360 },
        rotationSpeed: { min: -30, max: 30 },
        startSpeed: { min: 20, max: 40 },
        gravity: { x: 0, y: 20 },
        tangentialAcceleration: { min: -20, max: 20 },
        blendMode: 'normal',
        autoStart: true,
      },
    },
  ],

  timelines: [],

  interactions: [
    // 点击爆炸按钮触发爆炸
    {
      id: 'trigger_explosion',
      name: '触发爆炸',
      enabled: true,
      trigger: {
        type: 'click',
        targetId: 'explosion_btn',
      },
      actions: [
        {
          type: 'emitParticles',
          params: { emitterId: 'explosion_emitter', count: 80 },
        },
        {
          type: 'log',
          params: { message: '💥 爆炸!' },
        },
      ],
    },

    // 悬停爆炸按钮
    {
      id: 'hover_explosion_btn',
      name: '悬停爆炸按钮',
      enabled: true,
      trigger: {
        type: 'hover',
        targetId: 'explosion_btn',
      },
      actions: [
        {
          type: 'setProperty',
          params: { targetId: 'explosion_btn', property: 'scale', value: { x: 1.1, y: 1.1 } },
        },
      ],
    },

    // 离开爆炸按钮
    {
      id: 'hover_end_explosion_btn',
      name: '离开爆炸按钮',
      enabled: true,
      trigger: {
        type: 'hoverEnd',
        targetId: 'explosion_btn',
      },
      actions: [
        {
          type: 'setProperty',
          params: { targetId: 'explosion_btn', property: 'scale', value: { x: 1, y: 1 } },
        },
      ],
    },
  ],

  variables: [
    { id: 'explosion_count', name: '爆炸次数', type: 'number', defaultValue: 0 },
  ],

  metadata: {
    author: 'HERCU',
    version: '1.0.0',
    tags: ['粒子', '效果', '演示'],
  },
};

export default particleEffectsScene;
