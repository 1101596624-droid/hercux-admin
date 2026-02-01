/**
 * Zustand Stores Index
 * Central export point for all stores
 */

export { useWorkstationStore } from './useWorkstationStore';
export type { CanvasMode, AIModeType } from './useWorkstationStore';

export { useCourseStore } from './useCourseStore';

export { useUserStore } from './useUserStore';

export { useTrainingStore } from './useTrainingStore';

// Studio Store
export { useStudioStore } from './studio/useStudioStore';
export type { } from './studio/useStudioStore';

// Editor Store
export { useEditorStore } from './editor/useEditorStore';
