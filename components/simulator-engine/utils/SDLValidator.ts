import type { SceneDefinition } from '@/types/simulator-engine';

export interface SceneValidationError {
  code: string;
  message: string;
  path?: string;
}

export interface SceneValidationResult {
  valid: boolean;
  errors: SceneValidationError[];
}

/**
 * Lightweight runtime validator used by scene store before loading scenes.
 * It keeps validation strict on required structure and cheap at runtime.
 */
export function validateScene(scene: SceneDefinition): SceneValidationResult {
  const errors: SceneValidationError[] = [];

  if (!scene || typeof scene !== 'object') {
    errors.push({ code: 'SCENE_INVALID', message: '场景对象无效' });
    return { valid: false, errors };
  }

  if (!scene.id?.trim()) {
    errors.push({ code: 'SCENE_ID_REQUIRED', message: '场景缺少 id', path: 'id' });
  }

  if (!scene.name?.trim()) {
    errors.push({ code: 'SCENE_NAME_REQUIRED', message: '场景缺少 name', path: 'name' });
  }

  if (!scene.version) {
    errors.push({ code: 'SCENE_VERSION_REQUIRED', message: '场景缺少 version', path: 'version' });
  }

  if (!scene.canvas) {
    errors.push({ code: 'SCENE_CANVAS_REQUIRED', message: '场景缺少 canvas', path: 'canvas' });
  } else {
    if (!(scene.canvas.width > 0)) {
      errors.push({ code: 'SCENE_CANVAS_WIDTH', message: 'canvas.width 必须大于 0', path: 'canvas.width' });
    }
    if (!(scene.canvas.height > 0)) {
      errors.push({ code: 'SCENE_CANVAS_HEIGHT', message: 'canvas.height 必须大于 0', path: 'canvas.height' });
    }
  }

  if (!Array.isArray(scene.elements)) {
    errors.push({ code: 'SCENE_ELEMENTS_REQUIRED', message: 'scene.elements 必须是数组', path: 'elements' });
  }

  if (!Array.isArray(scene.interactions)) {
    errors.push({ code: 'SCENE_INTERACTIONS_REQUIRED', message: 'scene.interactions 必须是数组', path: 'interactions' });
  }

  if (!Array.isArray(scene.timelines)) {
    errors.push({ code: 'SCENE_TIMELINES_REQUIRED', message: 'scene.timelines 必须是数组', path: 'timelines' });
  }

  if (!Array.isArray(scene.variables)) {
    errors.push({ code: 'SCENE_VARIABLES_REQUIRED', message: 'scene.variables 必须是数组', path: 'variables' });
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

