/**
 * 示例场景 - AI 控制演示
 * 展示 AI 如何控制场景变量、触发动作、观察状态
 */

import type { SceneDefinition } from '@/types/simulator-engine';

export const aiControlDemoScene: SceneDefinition = {
  version: '1.0.0',
  id: 'ai_control_demo',
  name: 'AI 控制演示',
  description: '展示 AI 如何实时控制场景元素和变量',

  canvas: {
    width: 700,
    height: 500,
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
        position: { x: 350, y: 30 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 100,
      interactive: false,
      text: {
        content: 'AI 场景控制演示',
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
        position: { x: 350, y: 60 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 0.7,
      zIndex: 100,
      interactive: false,
      text: {
        content: 'AI 可以控制下方的变量和元素',
        fontFamily: 'Arial',
        fontSize: 14,
        color: '#94a3b8',
        align: 'center',
      },
    },

    // ==================== 变量显示区域 ====================
    {
      id: 'var_panel_bg',
      name: '变量面板背景',
      type: 'shape',
      transform: {
        position: { x: 175, y: 200 },
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
        width: 280,
        height: 220,
        fill: { type: 'solid', color: '#1e293b' },
        stroke: { color: '#334155', width: 2 },
        cornerRadius: 12,
      },
    },

    {
      id: 'var_panel_title',
      name: '变量面板标题',
      type: 'text',
      transform: {
        position: { x: 175, y: 105 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: false,
      text: {
        content: '可控变量',
        fontFamily: 'Arial',
        fontSize: 16,
        fontWeight: 'bold',
        color: '#3b82f6',
        align: 'center',
      },
    },

    // 分数变量
    {
      id: 'score_label',
      name: '分数标签',
      type: 'text',
      transform: {
        position: { x: 80, y: 150 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0, y: 0.5 },
      },
      visible: true,
      opacity: 0.8,
      zIndex: 10,
      interactive: false,
      text: {
        content: '分数:',
        fontFamily: 'Arial',
        fontSize: 14,
        color: '#94a3b8',
        align: 'left',
      },
    },

    {
      id: 'score_value',
      name: '分数值',
      type: 'text',
      transform: {
        position: { x: 250, y: 150 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 1, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: false,
      text: {
        content: '0',
        fontFamily: 'Arial',
        fontSize: 24,
        fontWeight: 'bold',
        color: '#22c55e',
        align: 'right',
      },
    },

    // 等级变量
    {
      id: 'level_label',
      name: '等级标签',
      type: 'text',
      transform: {
        position: { x: 80, y: 190 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0, y: 0.5 },
      },
      visible: true,
      opacity: 0.8,
      zIndex: 10,
      interactive: false,
      text: {
        content: '等级:',
        fontFamily: 'Arial',
        fontSize: 14,
        color: '#94a3b8',
        align: 'left',
      },
    },

    {
      id: 'level_value',
      name: '等级值',
      type: 'text',
      transform: {
        position: { x: 250, y: 190 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 1, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: false,
      text: {
        content: '1',
        fontFamily: 'Arial',
        fontSize: 24,
        fontWeight: 'bold',
        color: '#f59e0b',
        align: 'right',
      },
    },

    // 状态变量
    {
      id: 'status_label',
      name: '状态标签',
      type: 'text',
      transform: {
        position: { x: 80, y: 230 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0, y: 0.5 },
      },
      visible: true,
      opacity: 0.8,
      zIndex: 10,
      interactive: false,
      text: {
        content: '状态:',
        fontFamily: 'Arial',
        fontSize: 14,
        color: '#94a3b8',
        align: 'left',
      },
    },

    {
      id: 'status_value',
      name: '状态值',
      type: 'text',
      transform: {
        position: { x: 250, y: 230 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 1, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: false,
      text: {
        content: '等待中',
        fontFamily: 'Arial',
        fontSize: 18,
        fontWeight: 'bold',
        color: '#6366f1',
        align: 'right',
      },
    },

    // 消息变量
    {
      id: 'message_label',
      name: '消息标签',
      type: 'text',
      transform: {
        position: { x: 80, y: 270 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0, y: 0.5 },
      },
      visible: true,
      opacity: 0.8,
      zIndex: 10,
      interactive: false,
      text: {
        content: '消息:',
        fontFamily: 'Arial',
        fontSize: 14,
        color: '#94a3b8',
        align: 'left',
      },
    },

    {
      id: 'message_value',
      name: '消息值',
      type: 'text',
      transform: {
        position: { x: 175, y: 295 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: false,
      text: {
        content: '欢迎使用 AI 控制',
        fontFamily: 'Arial',
        fontSize: 12,
        color: '#e2e8f0',
        align: 'center',
      },
    },

    // ==================== 可控元素区域 ====================
    {
      id: 'element_panel_bg',
      name: '元素面板背景',
      type: 'shape',
      transform: {
        position: { x: 525, y: 200 },
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
        width: 280,
        height: 220,
        fill: { type: 'solid', color: '#1e293b' },
        stroke: { color: '#334155', width: 2 },
        cornerRadius: 12,
      },
    },

    {
      id: 'element_panel_title',
      name: '元素面板标题',
      type: 'text',
      transform: {
        position: { x: 525, y: 105 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: false,
      text: {
        content: '可控元素',
        fontFamily: 'Arial',
        fontSize: 16,
        fontWeight: 'bold',
        color: '#ec4899',
        align: 'center',
      },
    },

    // 可控球体
    {
      id: 'controllable_ball',
      name: '可控球体',
      type: 'shape',
      transform: {
        position: { x: 525, y: 200 },
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
        radius: 40,
        fill: { type: 'solid', color: '#ec4899' },
        stroke: { color: '#f9a8d4', width: 3 },
      },
    },

    {
      id: 'ball_label',
      name: '球体标签',
      type: 'text',
      transform: {
        position: { x: 525, y: 200 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 21,
      interactive: false,
      text: {
        content: 'AI',
        fontFamily: 'Arial',
        fontSize: 20,
        fontWeight: 'bold',
        color: '#ffffff',
        align: 'center',
      },
    },

    // 位置指示
    {
      id: 'position_indicator',
      name: '位置指示',
      type: 'text',
      transform: {
        position: { x: 525, y: 280 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 0.7,
      zIndex: 10,
      interactive: false,
      text: {
        content: 'X: 525, Y: 200',
        fontFamily: 'Arial',
        fontSize: 12,
        color: '#94a3b8',
        align: 'center',
      },
    },

    // ==================== 动作按钮区域 ====================
    {
      id: 'action_panel_bg',
      name: '动作面板背景',
      type: 'shape',
      transform: {
        position: { x: 350, y: 420 },
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
        width: 630,
        height: 120,
        fill: { type: 'solid', color: '#1e293b' },
        stroke: { color: '#334155', width: 2 },
        cornerRadius: 12,
      },
    },

    {
      id: 'action_panel_title',
      name: '动作面板标题',
      type: 'text',
      transform: {
        position: { x: 350, y: 370 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: false,
      text: {
        content: '可触发动作',
        fontFamily: 'Arial',
        fontSize: 16,
        fontWeight: 'bold',
        color: '#22c55e',
        align: 'center',
      },
    },

    // 增加分数按钮
    {
      id: 'btn_add_score',
      name: '增加分数按钮',
      type: 'shape',
      transform: {
        position: { x: 120, y: 430 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: true,
      shape: {
        shapeType: 'rectangle',
        width: 100,
        height: 40,
        fill: { type: 'solid', color: '#22c55e' },
        cornerRadius: 8,
      },
    },

    {
      id: 'btn_add_score_text',
      name: '增加分数文字',
      type: 'text',
      transform: {
        position: { x: 120, y: 430 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 11,
      interactive: false,
      text: {
        content: '+10 分',
        fontFamily: 'Arial',
        fontSize: 14,
        fontWeight: 'bold',
        color: '#ffffff',
        align: 'center',
      },
    },

    // 升级按钮
    {
      id: 'btn_level_up',
      name: '升级按钮',
      type: 'shape',
      transform: {
        position: { x: 250, y: 430 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: true,
      shape: {
        shapeType: 'rectangle',
        width: 100,
        height: 40,
        fill: { type: 'solid', color: '#f59e0b' },
        cornerRadius: 8,
      },
    },

    {
      id: 'btn_level_up_text',
      name: '升级文字',
      type: 'text',
      transform: {
        position: { x: 250, y: 430 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 11,
      interactive: false,
      text: {
        content: '升级',
        fontFamily: 'Arial',
        fontSize: 14,
        fontWeight: 'bold',
        color: '#ffffff',
        align: 'center',
      },
    },

    // 切换状态按钮
    {
      id: 'btn_toggle_status',
      name: '切换状态按钮',
      type: 'shape',
      transform: {
        position: { x: 380, y: 430 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: true,
      shape: {
        shapeType: 'rectangle',
        width: 100,
        height: 40,
        fill: { type: 'solid', color: '#6366f1' },
        cornerRadius: 8,
      },
    },

    {
      id: 'btn_toggle_status_text',
      name: '切换状态文字',
      type: 'text',
      transform: {
        position: { x: 380, y: 430 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 11,
      interactive: false,
      text: {
        content: '切换状态',
        fontFamily: 'Arial',
        fontSize: 14,
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
        position: { x: 510, y: 430 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 10,
      interactive: true,
      shape: {
        shapeType: 'rectangle',
        width: 100,
        height: 40,
        fill: { type: 'solid', color: '#ef4444' },
        cornerRadius: 8,
      },
    },

    {
      id: 'btn_reset_text',
      name: '重置文字',
      type: 'text',
      transform: {
        position: { x: 510, y: 430 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 11,
      interactive: false,
      text: {
        content: '重置',
        fontFamily: 'Arial',
        fontSize: 14,
        fontWeight: 'bold',
        color: '#ffffff',
        align: 'center',
      },
    },
  ],

  timelines: [
    // 球体脉冲动画
    {
      id: 'ball_pulse',
      name: '球体脉冲',
      duration: 1000,
      loop: true,
      autoPlay: true,
      tracks: [
        {
          id: 'ball_pulse_scale',
          targetId: 'controllable_ball',
          property: 'scale' as const,
          keyframes: [
            { time: 0, value: { x: 1, y: 1 }, easing: 'easeInOutSine' as const },
            { time: 500, value: { x: 1.1, y: 1.1 }, easing: 'easeInOutSine' as const },
            { time: 1000, value: { x: 1, y: 1 }, easing: 'easeInOutSine' as const },
          ],
        },
      ],
    },
  ],

  interactions: [
    // 增加分数
    {
      id: 'action_add_score',
      name: '增加分数',
      enabled: true,
      trigger: {
        type: 'click',
        targetId: 'btn_add_score',
      },
      actions: [
        {
          type: 'incrementVariable',
          params: { name: 'score', amount: 10 },
        },
        {
          type: 'setVariable',
          params: { name: 'message', value: '分数 +10!' },
        },
      ],
    },

    // 升级
    {
      id: 'action_level_up',
      name: '升级',
      enabled: true,
      trigger: {
        type: 'click',
        targetId: 'btn_level_up',
      },
      actions: [
        {
          type: 'incrementVariable',
          params: { name: 'level', amount: 1 },
        },
        {
          type: 'setVariable',
          params: { name: 'message', value: '等级提升!' },
        },
      ],
    },

    // 切换状态
    {
      id: 'action_toggle_status',
      name: '切换状态',
      enabled: true,
      trigger: {
        type: 'click',
        targetId: 'btn_toggle_status',
      },
      actions: [
        {
          type: 'custom',
          params: { handler: 'toggleStatus' },
        },
      ],
    },

    // 重置
    {
      id: 'action_reset',
      name: '重置',
      enabled: true,
      trigger: {
        type: 'click',
        targetId: 'btn_reset',
      },
      actions: [
        {
          type: 'setVariable',
          params: { name: 'score', value: 0 },
        },
        {
          type: 'setVariable',
          params: { name: 'level', value: 1 },
        },
        {
          type: 'setVariable',
          params: { name: 'status', value: '等待中' },
        },
        {
          type: 'setVariable',
          params: { name: 'message', value: '已重置' },
        },
      ],
    },

    // 拖拽球体
    {
      id: 'drag_ball',
      name: '拖拽球体',
      enabled: true,
      trigger: {
        type: 'drag',
        targetId: 'controllable_ball',
      },
      actions: [
        {
          type: 'moveElement',
          params: { targetId: 'controllable_ball' },
        },
      ],
    },

    // 按钮悬停效果
    ...['btn_add_score', 'btn_level_up', 'btn_toggle_status', 'btn_reset'].flatMap(btnId => [
      {
        id: `hover_${btnId}`,
        name: `悬停 ${btnId}`,
        enabled: true,
        trigger: { type: 'hover' as const, targetId: btnId },
        actions: [
          {
            type: 'setProperty' as const,
            params: { targetId: btnId, property: 'scale', value: { x: 1.05, y: 1.05 } },
          },
        ],
      },
      {
        id: `hover_end_${btnId}`,
        name: `离开 ${btnId}`,
        enabled: true,
        trigger: { type: 'hoverEnd' as const, targetId: btnId },
        actions: [
          {
            type: 'setProperty' as const,
            params: { targetId: btnId, property: 'scale', value: { x: 1, y: 1 } },
          },
        ],
      },
    ]),
  ],

  variables: [
    { id: 'score', name: '分数', type: 'number', defaultValue: 0 },
    { id: 'level', name: '等级', type: 'number', defaultValue: 1 },
    { id: 'status', name: '状态', type: 'string', defaultValue: '等待中' },
    { id: 'message', name: '消息', type: 'string', defaultValue: '欢迎使用 AI 控制' },
    { id: 'ball_x', name: '球体X', type: 'number', defaultValue: 525 },
    { id: 'ball_y', name: '球体Y', type: 'number', defaultValue: 200 },
  ],

  evaluation: {
    criteria: [
      {
        id: 'score_50',
        name: '达到50分',
        description: '将分数增加到50',
        weight: 30,
        rule: {
          type: 'variable',
          expression: 'variables.score >= 50',
        },
      },
      {
        id: 'level_3',
        name: '达到3级',
        description: '将等级提升到3',
        weight: 30,
        rule: {
          type: 'variable',
          expression: 'variables.level >= 3',
        },
      },
      {
        id: 'status_running',
        name: '运行状态',
        description: '将状态切换为运行中',
        weight: 40,
        rule: {
          type: 'variable',
          expression: 'variables.status === "运行中"',
        },
      },
    ],
    passThreshold: 60,
  },

  // AI 控制接口
  aiInterface: {
    controllableVariables: ['score', 'level', 'status', 'message', 'ball_x', 'ball_y'],
    availableActions: [
      'action_add_score',
      'action_level_up',
      'action_toggle_status',
      'action_reset',
    ],
    observableState: ['score', 'level', 'status', 'message', 'ball_x', 'ball_y'],
    commandTemplates: [
      {
        id: 'set_score',
        name: '设置分数',
        description: '直接设置分数值',
        parameters: [
          {
            name: 'value',
            type: 'number',
            description: '新的分数值',
            required: true,
          },
        ],
        action: {
          type: 'setVariable',
          params: { name: 'score', value: 0 },
        },
      },
      {
        id: 'set_level',
        name: '设置等级',
        description: '直接设置等级值',
        parameters: [
          {
            name: 'value',
            type: 'number',
            description: '新的等级值',
            required: true,
          },
        ],
        action: {
          type: 'setVariable',
          params: { name: 'level', value: 1 },
        },
      },
      {
        id: 'set_status',
        name: '设置状态',
        description: '设置状态文本',
        parameters: [
          {
            name: 'value',
            type: 'string',
            description: '状态文本 (等待中/运行中/已完成)',
            required: true,
          },
        ],
        action: {
          type: 'setVariable',
          params: { name: 'status', value: '等待中' },
        },
      },
      {
        id: 'move_ball',
        name: '移动球体',
        description: '移动可控球体到指定位置',
        parameters: [
          {
            name: 'x',
            type: 'number',
            description: 'X 坐标',
            required: true,
          },
          {
            name: 'y',
            type: 'number',
            description: 'Y 坐标',
            required: true,
          },
        ],
        action: {
          type: 'setProperty',
          params: {
            targetId: 'controllable_ball',
            property: 'position',
            value: { x: 525, y: 200 },
          },
        },
      },
    ],
  },

  metadata: {
    author: 'HERCU',
    version: '1.0.0',
    tags: ['AI', '控制', '演示'],
  },
};

export default aiControlDemoScene;
