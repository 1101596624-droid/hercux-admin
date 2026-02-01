/**
 * 示例场景 - 3D 几何体展示
 * 展示 Three.js 3D 渲染能力
 */

import type { SceneDefinition } from '@/types/simulator-engine';

export const geometry3DScene: SceneDefinition = {
  version: '1.0.0',
  id: '3d_geometry_demo',
  name: '3D 几何体展示',
  description: '展示各种 3D 几何体和材质效果',

  canvas: {
    width: 800,
    height: 600,
    backgroundColor: '#1a1a2e',
    renderer: 'three',
    antialias: true,
  },

  assets: {
    icons: [],
    images: [],
    sounds: [],
    fonts: [],
  },

  // 3D 场景配置
  scene3D: {
    camera: {
      type: 'perspective',
      fov: 60,
      near: 0.1,
      far: 1000,
      position: { x: 8, y: 6, z: 12 },
      lookAt: { x: 0, y: 0, z: 0 },
    },
    lights: [
      {
        id: 'ambient',
        name: '环境光',
        params: {
          type: 'ambient',
          color: '#404060',
          intensity: 0.6,
        },
      },
      {
        id: 'main_light',
        name: '主光源',
        params: {
          type: 'directional',
          color: '#ffffff',
          intensity: 1.2,
          position: { x: 10, y: 15, z: 10 },
          castShadow: true,
          shadowMapSize: 2048,
        },
      },
      {
        id: 'fill_light',
        name: '补光',
        params: {
          type: 'directional',
          color: '#6080ff',
          intensity: 0.4,
          position: { x: -5, y: 5, z: -5 },
        },
      },
      {
        id: 'point_light',
        name: '点光源',
        params: {
          type: 'point',
          color: '#ff8040',
          intensity: 0.8,
          position: { x: 0, y: 3, z: 0 },
          distance: 15,
          decay: 2,
        },
      },
    ],
    background: '#0a0a1a',
    shadows: true,
    antialias: true,
    controls: {
      type: 'orbit',
      enableDamping: true,
      dampingFactor: 0.05,
      enableZoom: true,
      enablePan: true,
      enableRotate: true,
      minDistance: 5,
      maxDistance: 30,
      autoRotate: true,
      autoRotateSpeed: 0.5,
    },
  },

  elements: [
    // 地面
    {
      id: 'ground',
      name: '地面',
      type: 'shape',
      transform: {
        position: { x: 0, y: 0 },
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
        width: 20,
        height: 20,
        fill: { type: 'solid', color: '#2a2a4a' },
      },
      metadata: {
        mesh3D: {
          geometry: {
            type: 'plane',
            width: 20,
            height: 20,
          },
          material: {
            type: 'standard',
            color: '#2a2a4a',
            roughness: 0.8,
            metalness: 0.2,
          },
          receiveShadow: true,
          castShadow: false,
        },
        transform3D: {
          position: { x: 0, y: -0.5, z: 0 },
          rotation: { x: -90, y: 0, z: 0 },
        },
      },
    },

    // 立方体
    {
      id: 'cube',
      name: '立方体',
      type: 'shape',
      transform: {
        position: { x: -4, y: 0 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 1,
      interactive: true,
      shape: {
        shapeType: 'rectangle',
        width: 2,
        height: 2,
        fill: { type: 'solid', color: '#ef4444' },
      },
      metadata: {
        mesh3D: {
          geometry: {
            type: 'box',
            width: 2,
            height: 2,
            depth: 2,
          },
          material: {
            type: 'standard',
            color: '#ef4444',
            roughness: 0.3,
            metalness: 0.7,
          },
          castShadow: true,
          receiveShadow: true,
        },
        transform3D: {
          position: { x: -4, y: 1, z: 0 },
          rotation: { x: 0, y: 45, z: 0 },
        },
      },
    },

    // 球体
    {
      id: 'sphere',
      name: '球体',
      type: 'shape',
      transform: {
        position: { x: 0, y: 0 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 1,
      interactive: true,
      shape: {
        shapeType: 'circle',
        radius: 1.2,
        fill: { type: 'solid', color: '#3b82f6' },
      },
      metadata: {
        mesh3D: {
          geometry: {
            type: 'sphere',
            radius: 1.2,
            widthSegments: 32,
            heightSegments: 24,
          },
          material: {
            type: 'standard',
            color: '#3b82f6',
            roughness: 0.1,
            metalness: 0.9,
          },
          castShadow: true,
          receiveShadow: true,
        },
        transform3D: {
          position: { x: 0, y: 1.2, z: 0 },
          rotation: { x: 0, y: 0, z: 0 },
        },
      },
    },

    // 圆柱体
    {
      id: 'cylinder',
      name: '圆柱体',
      type: 'shape',
      transform: {
        position: { x: 4, y: 0 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 1,
      interactive: true,
      shape: {
        shapeType: 'circle',
        radius: 0.8,
        fill: { type: 'solid', color: '#22c55e' },
      },
      metadata: {
        mesh3D: {
          geometry: {
            type: 'cylinder',
            radiusTop: 0.8,
            radiusBottom: 0.8,
            height: 2.5,
            radialSegments: 32,
          },
          material: {
            type: 'standard',
            color: '#22c55e',
            roughness: 0.4,
            metalness: 0.6,
          },
          castShadow: true,
          receiveShadow: true,
        },
        transform3D: {
          position: { x: 4, y: 1.25, z: 0 },
          rotation: { x: 0, y: 0, z: 0 },
        },
      },
    },

    // 圆环
    {
      id: 'torus',
      name: '圆环',
      type: 'shape',
      transform: {
        position: { x: -4, y: 4 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 1,
      interactive: true,
      shape: {
        shapeType: 'circle',
        radius: 1,
        fill: { type: 'solid', color: '#f59e0b' },
      },
      metadata: {
        mesh3D: {
          geometry: {
            type: 'torus',
            radius: 1,
            tube: 0.3,
            radialSegments: 16,
            tubularSegments: 48,
          },
          material: {
            type: 'standard',
            color: '#f59e0b',
            roughness: 0.2,
            metalness: 0.8,
          },
          castShadow: true,
          receiveShadow: true,
        },
        transform3D: {
          position: { x: -4, y: 3, z: 4 },
          rotation: { x: 45, y: 0, z: 0 },
        },
      },
    },

    // 圆锥
    {
      id: 'cone',
      name: '圆锥',
      type: 'shape',
      transform: {
        position: { x: 0, y: 4 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 1,
      interactive: true,
      shape: {
        shapeType: 'circle',
        radius: 0.8,
        fill: { type: 'solid', color: '#a855f7' },
      },
      metadata: {
        mesh3D: {
          geometry: {
            type: 'cone',
            radius: 0.8,
            height: 2,
            radialSegments: 32,
          },
          material: {
            type: 'standard',
            color: '#a855f7',
            roughness: 0.3,
            metalness: 0.5,
          },
          castShadow: true,
          receiveShadow: true,
        },
        transform3D: {
          position: { x: 0, y: 1, z: 4 },
          rotation: { x: 0, y: 0, z: 0 },
        },
      },
    },

    // 二十面体
    {
      id: 'icosahedron',
      name: '二十面体',
      type: 'shape',
      transform: {
        position: { x: 4, y: 4 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 1,
      zIndex: 1,
      interactive: true,
      shape: {
        shapeType: 'circle',
        radius: 1,
        fill: { type: 'solid', color: '#ec4899' },
      },
      metadata: {
        mesh3D: {
          geometry: {
            type: 'icosahedron',
            radius: 1,
            detail: 0,
          },
          material: {
            type: 'standard',
            color: '#ec4899',
            roughness: 0.2,
            metalness: 0.8,
          },
          castShadow: true,
          receiveShadow: true,
        },
        transform3D: {
          position: { x: 4, y: 2, z: 4 },
          rotation: { x: 0, y: 30, z: 0 },
        },
      },
    },

    // 玻璃球 (Physical 材质)
    {
      id: 'glass_sphere',
      name: '玻璃球',
      type: 'shape',
      transform: {
        position: { x: 0, y: 0 },
        rotation: 0,
        scale: { x: 1, y: 1 },
        anchor: { x: 0.5, y: 0.5 },
      },
      visible: true,
      opacity: 0.5,
      zIndex: 2,
      interactive: true,
      shape: {
        shapeType: 'circle',
        radius: 0.8,
        fill: { type: 'solid', color: '#88ccff' },
      },
      metadata: {
        mesh3D: {
          geometry: {
            type: 'sphere',
            radius: 0.8,
            widthSegments: 32,
            heightSegments: 24,
          },
          material: {
            type: 'physical',
            color: '#ffffff',
            roughness: 0,
            metalness: 0,
            transmission: 0.9,
            thickness: 0.5,
            ior: 1.5,
            transparent: true,
          },
          castShadow: true,
          receiveShadow: false,
        },
        transform3D: {
          position: { x: 0, y: 0.8, z: -3 },
          rotation: { x: 0, y: 0, z: 0 },
        },
      },
    },
  ],

  timelines: [],

  interactions: [],

  variables: [],

  metadata: {
    author: 'HERCU',
    version: '1.0.0',
    tags: ['3D', '几何体', '演示'],
  },
};

export default geometry3DScene;
