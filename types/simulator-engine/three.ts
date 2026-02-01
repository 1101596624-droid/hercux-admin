/**
 * 场景描述语言 (SDL) - 3D 类型定义
 */

import type { Vector3D, ColorValue } from './base';

// ==================== 3D 几何体类型 ====================

/** 3D 几何体类型 */
export type Geometry3DType =
  | 'box'
  | 'sphere'
  | 'cylinder'
  | 'cone'
  | 'torus'
  | 'plane'
  | 'circle'
  | 'ring'
  | 'dodecahedron'
  | 'icosahedron'
  | 'octahedron'
  | 'tetrahedron'
  | 'custom';

/** 盒子几何体参数 */
export interface BoxGeometryParams {
  type: 'box';
  width: number;
  height: number;
  depth: number;
  widthSegments?: number;
  heightSegments?: number;
  depthSegments?: number;
}

/** 球体几何体参数 */
export interface SphereGeometryParams {
  type: 'sphere';
  radius: number;
  widthSegments?: number;
  heightSegments?: number;
  phiStart?: number;
  phiLength?: number;
  thetaStart?: number;
  thetaLength?: number;
}

/** 圆柱体几何体参数 */
export interface CylinderGeometryParams {
  type: 'cylinder';
  radiusTop: number;
  radiusBottom: number;
  height: number;
  radialSegments?: number;
  heightSegments?: number;
  openEnded?: boolean;
}

/** 圆锥体几何体参数 */
export interface ConeGeometryParams {
  type: 'cone';
  radius: number;
  height: number;
  radialSegments?: number;
  heightSegments?: number;
  openEnded?: boolean;
}

/** 圆环几何体参数 */
export interface TorusGeometryParams {
  type: 'torus';
  radius: number;
  tube: number;
  radialSegments?: number;
  tubularSegments?: number;
  arc?: number;
}

/** 平面几何体参数 */
export interface PlaneGeometryParams {
  type: 'plane';
  width: number;
  height: number;
  widthSegments?: number;
  heightSegments?: number;
}

/** 圆形几何体参数 */
export interface CircleGeometryParams {
  type: 'circle';
  radius: number;
  segments?: number;
  thetaStart?: number;
  thetaLength?: number;
}

/** 环形几何体参数 */
export interface RingGeometryParams {
  type: 'ring';
  innerRadius: number;
  outerRadius: number;
  thetaSegments?: number;
  phiSegments?: number;
}

/** 多面体几何体参数 */
export interface PolyhedronGeometryParams {
  type: 'dodecahedron' | 'icosahedron' | 'octahedron' | 'tetrahedron';
  radius: number;
  detail?: number;
}

/** 自定义几何体参数 */
export interface CustomGeometryParams {
  type: 'custom';
  vertices: number[];
  indices?: number[];
  normals?: number[];
  uvs?: number[];
}

/** 几何体参数联合类型 */
export type GeometryParams =
  | BoxGeometryParams
  | SphereGeometryParams
  | CylinderGeometryParams
  | ConeGeometryParams
  | TorusGeometryParams
  | PlaneGeometryParams
  | CircleGeometryParams
  | RingGeometryParams
  | PolyhedronGeometryParams
  | CustomGeometryParams;

// ==================== 3D 材质类型 ====================

/** 材质类型 */
export type Material3DType =
  | 'basic'
  | 'lambert'
  | 'phong'
  | 'standard'
  | 'physical'
  | 'toon'
  | 'normal'
  | 'depth';

/** 基础材质参数 */
export interface BasicMaterialParams {
  type: 'basic';
  color: ColorValue;
  wireframe?: boolean;
  transparent?: boolean;
  opacity?: number;
  map?: string; // 纹理 URL
  side?: 'front' | 'back' | 'double';
}

/** Lambert 材质参数 */
export interface LambertMaterialParams {
  type: 'lambert';
  color: ColorValue;
  emissive?: ColorValue;
  emissiveIntensity?: number;
  wireframe?: boolean;
  transparent?: boolean;
  opacity?: number;
  map?: string;
  side?: 'front' | 'back' | 'double';
}

/** Phong 材质参数 */
export interface PhongMaterialParams {
  type: 'phong';
  color: ColorValue;
  emissive?: ColorValue;
  specular?: ColorValue;
  shininess?: number;
  wireframe?: boolean;
  transparent?: boolean;
  opacity?: number;
  map?: string;
  normalMap?: string;
  side?: 'front' | 'back' | 'double';
}

/** Standard PBR 材质参数 */
export interface StandardMaterialParams {
  type: 'standard';
  color: ColorValue;
  emissive?: ColorValue;
  emissiveIntensity?: number;
  roughness?: number;
  metalness?: number;
  wireframe?: boolean;
  transparent?: boolean;
  opacity?: number;
  map?: string;
  normalMap?: string;
  roughnessMap?: string;
  metalnessMap?: string;
  aoMap?: string;
  side?: 'front' | 'back' | 'double';
}

/** Physical PBR 材质参数 */
export interface PhysicalMaterialParams extends Omit<StandardMaterialParams, 'type'> {
  type: 'physical';
  clearcoat?: number;
  clearcoatRoughness?: number;
  transmission?: number;
  thickness?: number;
  ior?: number;
}

/** Toon 材质参数 */
export interface ToonMaterialParams {
  type: 'toon';
  color: ColorValue;
  wireframe?: boolean;
  transparent?: boolean;
  opacity?: number;
  map?: string;
  gradientMap?: string;
  side?: 'front' | 'back' | 'double';
}

/** 材质参数联合类型 */
export type MaterialParams =
  | BasicMaterialParams
  | LambertMaterialParams
  | PhongMaterialParams
  | StandardMaterialParams
  | PhysicalMaterialParams
  | ToonMaterialParams;

// ==================== 3D 光源类型 ====================

/** 光源类型 */
export type Light3DType =
  | 'ambient'
  | 'directional'
  | 'point'
  | 'spot'
  | 'hemisphere';

/** 环境光参数 */
export interface AmbientLightParams {
  type: 'ambient';
  color: ColorValue;
  intensity: number;
}

/** 平行光参数 */
export interface DirectionalLightParams {
  type: 'directional';
  color: ColorValue;
  intensity: number;
  position: Vector3D;
  target?: Vector3D;
  castShadow?: boolean;
  shadowMapSize?: number;
}

/** 点光源参数 */
export interface PointLightParams {
  type: 'point';
  color: ColorValue;
  intensity: number;
  position: Vector3D;
  distance?: number;
  decay?: number;
  castShadow?: boolean;
}

/** 聚光灯参数 */
export interface SpotLightParams {
  type: 'spot';
  color: ColorValue;
  intensity: number;
  position: Vector3D;
  target?: Vector3D;
  distance?: number;
  angle?: number;
  penumbra?: number;
  decay?: number;
  castShadow?: boolean;
}

/** 半球光参数 */
export interface HemisphereLightParams {
  type: 'hemisphere';
  skyColor: ColorValue;
  groundColor: ColorValue;
  intensity: number;
}

/** 光源参数联合类型 */
export type LightParams =
  | AmbientLightParams
  | DirectionalLightParams
  | PointLightParams
  | SpotLightParams
  | HemisphereLightParams;

// ==================== 3D 相机类型 ====================

/** 相机类型 */
export type Camera3DType = 'perspective' | 'orthographic';

/** 透视相机参数 */
export interface PerspectiveCameraParams {
  type: 'perspective';
  fov: number;
  near: number;
  far: number;
  position: Vector3D;
  lookAt?: Vector3D;
}

/** 正交相机参数 */
export interface OrthographicCameraParams {
  type: 'orthographic';
  left: number;
  right: number;
  top: number;
  bottom: number;
  near: number;
  far: number;
  position: Vector3D;
  lookAt?: Vector3D;
}

/** 相机参数联合类型 */
export type CameraParams = PerspectiveCameraParams | OrthographicCameraParams;

// ==================== 3D 场景配置 ====================

/** 3D 场景配置 */
export interface Scene3DConfig {
  camera: CameraParams;
  lights: LightConfig[];
  background?: ColorValue | string; // 颜色或天空盒 URL
  fog?: FogConfig;
  shadows?: boolean;
  antialias?: boolean;
  controls?: CameraControlsConfig;
}

/** 光源配置 */
export interface LightConfig {
  id: string;
  name: string;
  params: LightParams;
  enabled?: boolean;
}

/** 雾效配置 */
export interface FogConfig {
  type: 'linear' | 'exponential';
  color: ColorValue;
  near?: number;  // linear
  far?: number;   // linear
  density?: number; // exponential
}

/** 相机控制配置 */
export interface CameraControlsConfig {
  type: 'orbit' | 'fly' | 'firstPerson' | 'none';
  enableDamping?: boolean;
  dampingFactor?: number;
  enableZoom?: boolean;
  enablePan?: boolean;
  enableRotate?: boolean;
  minDistance?: number;
  maxDistance?: number;
  minPolarAngle?: number;
  maxPolarAngle?: number;
  autoRotate?: boolean;
  autoRotateSpeed?: number;
}

// ==================== 3D 元素配置 ====================

/** 3D 网格元素配置 */
export interface Mesh3DConfig {
  geometry: GeometryParams;
  material: MaterialParams;
  castShadow?: boolean;
  receiveShadow?: boolean;
}

/** 3D 模型配置 */
export interface Model3DConfig {
  url: string;
  format: 'gltf' | 'glb' | 'obj' | 'fbx';
  scale?: Vector3D;
  castShadow?: boolean;
  receiveShadow?: boolean;
}

/** 3D 组配置 */
export interface Group3DConfig {
  children: string[];
}

// ==================== 默认配置 ====================

/** 默认 3D 场景配置 */
export const DEFAULT_SCENE_3D_CONFIG: Scene3DConfig = {
  camera: {
    type: 'perspective',
    fov: 75,
    near: 0.1,
    far: 1000,
    position: { x: 0, y: 5, z: 10 },
    lookAt: { x: 0, y: 0, z: 0 },
  },
  lights: [
    {
      id: 'ambient',
      name: '环境光',
      params: {
        type: 'ambient',
        color: '#ffffff',
        intensity: 0.5,
      },
    },
    {
      id: 'directional',
      name: '主光源',
      params: {
        type: 'directional',
        color: '#ffffff',
        intensity: 1,
        position: { x: 5, y: 10, z: 5 },
        castShadow: true,
      },
    },
  ],
  background: '#1a1a2e',
  shadows: true,
  antialias: true,
  controls: {
    type: 'orbit',
    enableDamping: true,
    dampingFactor: 0.05,
    enableZoom: true,
    enablePan: true,
    enableRotate: true,
  },
};

/** 默认材质 */
export const DEFAULT_MATERIAL: StandardMaterialParams = {
  type: 'standard',
  color: '#888888',
  roughness: 0.5,
  metalness: 0.5,
};
