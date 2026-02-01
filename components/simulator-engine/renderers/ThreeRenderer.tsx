/**
 * Three.js 3D 渲染器
 * 支持 3D 场景渲染、相机控制、光照系统
 */

'use client';

import React, { useRef, useEffect, useCallback, useMemo } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import type {
  SceneDefinition,
  SceneElement,
  Vector3D,
  Scene3DConfig,
  GeometryParams,
  MaterialParams,
  LightParams,
  CameraParams,
  ColorValue,
} from '@/types/simulator-engine';
import { stringToColor, colorToPixi } from '@/types/simulator-engine';
import { DEFAULT_SCENE_3D_CONFIG } from '@/types/simulator-engine/three';

// ==================== 类型定义 ====================

interface ThreeRendererProps {
  scene: SceneDefinition;
  width?: number;
  height?: number;
  onReady?: () => void;
  onError?: (error: Error) => void;
}

interface ThreeState {
  scene: THREE.Scene;
  camera: THREE.Camera;
  renderer: THREE.WebGLRenderer;
  controls: OrbitControls | null;
  meshes: Map<string, THREE.Object3D>;
  lights: Map<string, THREE.Light>;
  animationId: number | null;
}

// ==================== 工具函数 ====================

/** 颜色值转 Three.js 颜色 */
function colorToThree(color: ColorValue): THREE.Color {
  if (typeof color === 'string') {
    return new THREE.Color(color);
  }
  return new THREE.Color(color.r / 255, color.g / 255, color.b / 255);
}

/** 获取材质透明度 */
function getOpacity(color: ColorValue): number {
  if (typeof color === 'string') {
    const c = stringToColor(color);
    return c.a;
  }
  return color.a;
}

/** 角度转弧度 */
function degToRad(deg: number): number {
  return deg * (Math.PI / 180);
}

// ==================== 几何体创建 ====================

function createGeometry(params: GeometryParams): THREE.BufferGeometry {
  switch (params.type) {
    case 'box':
      return new THREE.BoxGeometry(
        params.width,
        params.height,
        params.depth,
        params.widthSegments,
        params.heightSegments,
        params.depthSegments
      );

    case 'sphere':
      return new THREE.SphereGeometry(
        params.radius,
        params.widthSegments ?? 32,
        params.heightSegments ?? 16,
        params.phiStart,
        params.phiLength,
        params.thetaStart,
        params.thetaLength
      );

    case 'cylinder':
      return new THREE.CylinderGeometry(
        params.radiusTop,
        params.radiusBottom,
        params.height,
        params.radialSegments ?? 32,
        params.heightSegments ?? 1,
        params.openEnded ?? false
      );

    case 'cone':
      return new THREE.ConeGeometry(
        params.radius,
        params.height,
        params.radialSegments ?? 32,
        params.heightSegments ?? 1,
        params.openEnded ?? false
      );

    case 'torus':
      return new THREE.TorusGeometry(
        params.radius,
        params.tube,
        params.radialSegments ?? 16,
        params.tubularSegments ?? 100,
        params.arc
      );

    case 'plane':
      return new THREE.PlaneGeometry(
        params.width,
        params.height,
        params.widthSegments,
        params.heightSegments
      );

    case 'circle':
      return new THREE.CircleGeometry(
        params.radius,
        params.segments ?? 32,
        params.thetaStart,
        params.thetaLength
      );

    case 'ring':
      return new THREE.RingGeometry(
        params.innerRadius,
        params.outerRadius,
        params.thetaSegments ?? 32,
        params.phiSegments ?? 1
      );

    case 'dodecahedron':
      return new THREE.DodecahedronGeometry(params.radius, params.detail);

    case 'icosahedron':
      return new THREE.IcosahedronGeometry(params.radius, params.detail);

    case 'octahedron':
      return new THREE.OctahedronGeometry(params.radius, params.detail);

    case 'tetrahedron':
      return new THREE.TetrahedronGeometry(params.radius, params.detail);

    case 'custom':
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position', new THREE.Float32BufferAttribute(params.vertices, 3));
      if (params.indices) {
        geometry.setIndex(params.indices);
      }
      if (params.normals) {
        geometry.setAttribute('normal', new THREE.Float32BufferAttribute(params.normals, 3));
      }
      if (params.uvs) {
        geometry.setAttribute('uv', new THREE.Float32BufferAttribute(params.uvs, 2));
      }
      geometry.computeVertexNormals();
      return geometry;

    default:
      return new THREE.BoxGeometry(1, 1, 1);
  }
}

// ==================== 材质创建 ====================

function createMaterial(params: MaterialParams): THREE.Material {
  const side = params.side === 'back' ? THREE.BackSide :
               params.side === 'double' ? THREE.DoubleSide : THREE.FrontSide;

  switch (params.type) {
    case 'basic':
      return new THREE.MeshBasicMaterial({
        color: colorToThree(params.color),
        wireframe: params.wireframe ?? false,
        transparent: params.transparent ?? false,
        opacity: params.opacity ?? 1,
        side,
      });

    case 'lambert':
      return new THREE.MeshLambertMaterial({
        color: colorToThree(params.color),
        emissive: params.emissive ? colorToThree(params.emissive) : undefined,
        emissiveIntensity: params.emissiveIntensity,
        wireframe: params.wireframe ?? false,
        transparent: params.transparent ?? false,
        opacity: params.opacity ?? 1,
        side,
      });

    case 'phong':
      return new THREE.MeshPhongMaterial({
        color: colorToThree(params.color),
        emissive: params.emissive ? colorToThree(params.emissive) : undefined,
        specular: params.specular ? colorToThree(params.specular) : undefined,
        shininess: params.shininess ?? 30,
        wireframe: params.wireframe ?? false,
        transparent: params.transparent ?? false,
        opacity: params.opacity ?? 1,
        side,
      });

    case 'standard':
      return new THREE.MeshStandardMaterial({
        color: colorToThree(params.color),
        emissive: params.emissive ? colorToThree(params.emissive) : undefined,
        emissiveIntensity: params.emissiveIntensity,
        roughness: params.roughness ?? 0.5,
        metalness: params.metalness ?? 0.5,
        wireframe: params.wireframe ?? false,
        transparent: params.transparent ?? false,
        opacity: params.opacity ?? 1,
        side,
      });

    case 'physical':
      return new THREE.MeshPhysicalMaterial({
        color: colorToThree(params.color),
        emissive: params.emissive ? colorToThree(params.emissive) : undefined,
        emissiveIntensity: params.emissiveIntensity,
        roughness: params.roughness ?? 0.5,
        metalness: params.metalness ?? 0.5,
        clearcoat: params.clearcoat ?? 0,
        clearcoatRoughness: params.clearcoatRoughness ?? 0,
        transmission: params.transmission ?? 0,
        thickness: params.thickness ?? 0,
        ior: params.ior ?? 1.5,
        wireframe: params.wireframe ?? false,
        transparent: params.transparent ?? (params.transmission ?? 0) > 0,
        opacity: params.opacity ?? 1,
        side,
      });

    case 'toon':
      return new THREE.MeshToonMaterial({
        color: colorToThree(params.color),
        wireframe: params.wireframe ?? false,
        transparent: params.transparent ?? false,
        opacity: params.opacity ?? 1,
        side,
      });

    default:
      return new THREE.MeshStandardMaterial({
        color: 0x888888,
        roughness: 0.5,
        metalness: 0.5,
      });
  }
}

// ==================== 光源创建 ====================

function createLight(params: LightParams): THREE.Light {
  switch (params.type) {
    case 'ambient':
      return new THREE.AmbientLight(
        colorToThree(params.color),
        params.intensity
      );

    case 'directional': {
      const light = new THREE.DirectionalLight(
        colorToThree(params.color),
        params.intensity
      );
      light.position.set(params.position.x, params.position.y, params.position.z);
      if (params.target) {
        light.target.position.set(params.target.x, params.target.y, params.target.z);
      }
      if (params.castShadow) {
        light.castShadow = true;
        light.shadow.mapSize.width = params.shadowMapSize ?? 1024;
        light.shadow.mapSize.height = params.shadowMapSize ?? 1024;
        light.shadow.camera.near = 0.5;
        light.shadow.camera.far = 500;
      }
      return light;
    }

    case 'point': {
      const light = new THREE.PointLight(
        colorToThree(params.color),
        params.intensity,
        params.distance ?? 0,
        params.decay ?? 2
      );
      light.position.set(params.position.x, params.position.y, params.position.z);
      if (params.castShadow) {
        light.castShadow = true;
      }
      return light;
    }

    case 'spot': {
      const light = new THREE.SpotLight(
        colorToThree(params.color),
        params.intensity,
        params.distance ?? 0,
        params.angle ?? Math.PI / 3,
        params.penumbra ?? 0,
        params.decay ?? 2
      );
      light.position.set(params.position.x, params.position.y, params.position.z);
      if (params.target) {
        light.target.position.set(params.target.x, params.target.y, params.target.z);
      }
      if (params.castShadow) {
        light.castShadow = true;
      }
      return light;
    }

    case 'hemisphere':
      return new THREE.HemisphereLight(
        colorToThree(params.skyColor),
        colorToThree(params.groundColor),
        params.intensity
      );

    default:
      return new THREE.AmbientLight(0xffffff, 0.5);
  }
}

// ==================== 相机创建 ====================

function createCamera(params: CameraParams, aspect: number): THREE.Camera {
  let camera: THREE.Camera;

  if (params.type === 'perspective') {
    camera = new THREE.PerspectiveCamera(
      params.fov,
      aspect,
      params.near,
      params.far
    );
  } else {
    camera = new THREE.OrthographicCamera(
      params.left,
      params.right,
      params.top,
      params.bottom,
      params.near,
      params.far
    );
  }

  camera.position.set(params.position.x, params.position.y, params.position.z);

  if (params.lookAt) {
    camera.lookAt(params.lookAt.x, params.lookAt.y, params.lookAt.z);
  }

  return camera;
}

// ==================== 主组件 ====================

export const ThreeRenderer: React.FC<ThreeRendererProps> = ({
  scene: sceneDefinition,
  width,
  height,
  onReady,
  onError,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const stateRef = useRef<ThreeState | null>(null);

  // 获取 3D 配置
  const scene3DConfig = useMemo<Scene3DConfig>(() => {
    return sceneDefinition.scene3D || DEFAULT_SCENE_3D_CONFIG;
  }, [sceneDefinition.scene3D]);

  // 计算尺寸
  const canvasWidth = width ?? sceneDefinition.canvas.width;
  const canvasHeight = height ?? sceneDefinition.canvas.height;

  // 初始化 Three.js
  const initThree = useCallback(() => {
    if (!containerRef.current) return;

    try {
      // 创建场景
      const scene = new THREE.Scene();

      // 设置背景
      if (scene3DConfig.background) {
        if (typeof scene3DConfig.background === 'string' && scene3DConfig.background.startsWith('#')) {
          scene.background = colorToThree(scene3DConfig.background);
        } else if (typeof scene3DConfig.background === 'object') {
          scene.background = colorToThree(scene3DConfig.background);
        }
      }

      // 设置雾效
      if (scene3DConfig.fog) {
        if (scene3DConfig.fog.type === 'linear') {
          scene.fog = new THREE.Fog(
            colorToThree(scene3DConfig.fog.color),
            scene3DConfig.fog.near ?? 1,
            scene3DConfig.fog.far ?? 1000
          );
        } else {
          scene.fog = new THREE.FogExp2(
            colorToThree(scene3DConfig.fog.color),
            scene3DConfig.fog.density ?? 0.00025
          );
        }
      }

      // 创建渲染器
      const renderer = new THREE.WebGLRenderer({
        antialias: scene3DConfig.antialias ?? true,
        alpha: true,
      });
      renderer.setSize(canvasWidth, canvasHeight);
      renderer.setPixelRatio(window.devicePixelRatio);

      if (scene3DConfig.shadows) {
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      }

      containerRef.current.appendChild(renderer.domElement);

      // 创建相机
      const aspect = canvasWidth / canvasHeight;
      const camera = createCamera(scene3DConfig.camera, aspect);

      // 创建控制器
      let controls: OrbitControls | null = null;
      if (scene3DConfig.controls && scene3DConfig.controls.type === 'orbit') {
        controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = scene3DConfig.controls.enableDamping ?? true;
        controls.dampingFactor = scene3DConfig.controls.dampingFactor ?? 0.05;
        controls.enableZoom = scene3DConfig.controls.enableZoom ?? true;
        controls.enablePan = scene3DConfig.controls.enablePan ?? true;
        controls.enableRotate = scene3DConfig.controls.enableRotate ?? true;
        if (scene3DConfig.controls.minDistance !== undefined) {
          controls.minDistance = scene3DConfig.controls.minDistance;
        }
        if (scene3DConfig.controls.maxDistance !== undefined) {
          controls.maxDistance = scene3DConfig.controls.maxDistance;
        }
        if (scene3DConfig.controls.autoRotate) {
          controls.autoRotate = true;
          controls.autoRotateSpeed = scene3DConfig.controls.autoRotateSpeed ?? 2;
        }
      }

      // 创建光源
      const lights = new Map<string, THREE.Light>();
      for (const lightConfig of scene3DConfig.lights) {
        if (lightConfig.enabled === false) continue;
        const light = createLight(lightConfig.params);
        lights.set(lightConfig.id, light);
        scene.add(light);
      }

      // 存储状态
      stateRef.current = {
        scene,
        camera,
        renderer,
        controls,
        meshes: new Map(),
        lights,
        animationId: null,
      };

      // 创建场景元素
      createElements(sceneDefinition.elements);

      // 开始渲染循环
      startRenderLoop();

      onReady?.();
    } catch (error) {
      onError?.(error as Error);
    }
  }, [sceneDefinition, scene3DConfig, canvasWidth, canvasHeight, onReady, onError]);

  // 创建场景元素
  const createElements = useCallback((elements: SceneElement[]) => {
    if (!stateRef.current) return;

    const { scene, meshes } = stateRef.current;

    for (const element of elements) {
      // 检查是否是 3D 元素 (通过 metadata 或特定属性判断)
      const mesh3D = element.metadata?.mesh3D as {
        geometry: GeometryParams;
        material: MaterialParams;
        castShadow?: boolean;
        receiveShadow?: boolean;
      } | undefined;

      if (mesh3D) {
        const geometry = createGeometry(mesh3D.geometry);
        const material = createMaterial(mesh3D.material);
        const mesh = new THREE.Mesh(geometry, material);

        // 设置变换
        if ('position3D' in element.transform) {
          const t = element.transform;
          mesh.position.set(t.position3D.x, t.position3D.y, t.position3D.z);
          mesh.rotation.set(
            degToRad(t.rotation3D.x),
            degToRad(t.rotation3D.y),
            degToRad(t.rotation3D.z)
          );
        } else {
          mesh.position.set(element.transform.position.x, 0, element.transform.position.y);
          mesh.rotation.y = degToRad(element.transform.rotation);
        }

        mesh.scale.set(
          element.transform.scale.x,
          element.transform.scale.y,
          element.transform.scale.x
        );

        // 阴影设置
        mesh.castShadow = mesh3D.castShadow ?? true;
        mesh.receiveShadow = mesh3D.receiveShadow ?? true;

        mesh.visible = element.visible;
        mesh.name = element.id;

        meshes.set(element.id, mesh);
        scene.add(mesh);
      }
    }
  }, []);

  // 渲染循环
  const startRenderLoop = useCallback(() => {
    if (!stateRef.current) return;

    const { scene, camera, renderer, controls } = stateRef.current;

    const animate = () => {
      stateRef.current!.animationId = requestAnimationFrame(animate);

      // 更新控制器
      if (controls) {
        controls.update();
      }

      // 渲染
      renderer.render(scene, camera);
    };

    animate();
  }, []);

  // 清理
  const cleanup = useCallback(() => {
    if (!stateRef.current) return;

    const { scene, renderer, controls, meshes, lights, animationId } = stateRef.current;

    // 停止动画
    if (animationId !== null) {
      cancelAnimationFrame(animationId);
    }

    // 清理控制器
    if (controls) {
      controls.dispose();
    }

    // 清理网格
    meshes.forEach((mesh) => {
      scene.remove(mesh);
      if (mesh instanceof THREE.Mesh) {
        mesh.geometry.dispose();
        if (Array.isArray(mesh.material)) {
          mesh.material.forEach(m => m.dispose());
        } else {
          mesh.material.dispose();
        }
      }
    });

    // 清理光源
    lights.forEach((light) => {
      scene.remove(light);
    });

    // 清理渲染器
    renderer.dispose();
    if (containerRef.current && renderer.domElement.parentNode === containerRef.current) {
      containerRef.current.removeChild(renderer.domElement);
    }

    stateRef.current = null;
  }, []);

  // 初始化和清理
  useEffect(() => {
    initThree();
    return cleanup;
  }, [initThree, cleanup]);

  // 窗口大小变化处理
  useEffect(() => {
    const handleResize = () => {
      if (!stateRef.current) return;

      const { camera, renderer } = stateRef.current;

      renderer.setSize(canvasWidth, canvasHeight);

      if (camera instanceof THREE.PerspectiveCamera) {
        camera.aspect = canvasWidth / canvasHeight;
        camera.updateProjectionMatrix();
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [canvasWidth, canvasHeight]);

  return (
    <div
      ref={containerRef}
      style={{
        width: canvasWidth,
        height: canvasHeight,
        overflow: 'hidden',
      }}
    />
  );
};

export default ThreeRenderer;
