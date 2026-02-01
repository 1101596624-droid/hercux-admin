// ============================================
// HERCU Studio Types
// ============================================

// 从课程包标准导入类型
import type {
  StepType as TeachingFormType,
  ComplexityLevel,
  TextContentSpec as TextContent,
  IllustratedContentSpec as IllustratedContent,
  DiagramSpec,
  VideoSpec,
  EmbeddedInteraction,
  SimulatorSpec,
  AITutorSpec,
  AssessmentQuestion,
  AssessmentSpec,
  LessonStep,
  Lesson,
  PackageMeta as PackageMetaV2,
  PackageEdge as Edge,
  CoursePackage as CoursePackageV2,
} from './coursePackage';

// 重新导出供本模块使用
export type { TeachingFormType, ComplexityLevel, TextContent, IllustratedContent };
export type { DiagramSpec, VideoSpec, EmbeddedInteraction, SimulatorSpec };
export type { AITutorSpec, AssessmentQuestion, AssessmentSpec };
export type { LessonStep, Lesson, PackageMetaV2, Edge, CoursePackageV2 };

// Processor (Plugin) Types
export interface Processor {
  id: string;
  name: string;
  description: string;
  version: string;
  author?: string;
  tags: string[];
  color: string;
  icon: string;
}

export interface ProcessorWithConfig extends Processor {
  enabled: boolean;
  display_order: number;
  is_official: boolean;
  is_custom: boolean;
  system_prompt?: string;
}

// Practice Content (Studio 特有)
export interface PracticeContent {
  instructions: string;
  tasks: string[];
}

// Package List Item
export interface PackageListItem {
  id: string;
  title: string;
  description: string;
  style: string;
  status: string;
  total_nodes: number;
  estimated_hours: number;
  created_at: string;
  updated_at: string;
}

// Uploaded Source
export interface UploadedSource {
  id: string;
  name: string;
  charCount: number;
  text: string;
  type: 'file' | 'text' | 'paste';
}

// Generated Lesson (for result view)
export interface GeneratedLesson {
  lesson_id: string;
  title: string;
  description?: string;
  duration_minutes?: number;
  steps: LessonStep[];
}

// Generated Package (for result view)
export interface GeneratedPackage {
  meta: PackageMetaV2;
  lessons: GeneratedLesson[];
}

// View Mode
export type ViewMode = 'input' | 'generating' | 'result';

// Lesson Outline
export interface LessonOutline {
  title: string;
  index?: number;
  recommended_forms?: string[];
  complexity_level?: ComplexityLevel;
}

// Generation Progress
export interface GenerationProgress {
  phase: number;
  message: string;
  processor?: Processor;
  lessonsOutline?: LessonOutline[];
  currentLessonIndex?: number;
  totalLessons?: number;
  completedLessons: number;
}

// Generate Request
export interface GenerateRequestV2 {
  source_material: string;
  course_title: string;
  processor_id: string;
  source_info: string;
  // 断点续传支持
  resume_from_lesson?: number;  // 从第几个课时继续（0-indexed）
  completed_lessons?: any[];    // 已完成的课时数据
  lessons_outline?: any[];      // 课程大纲（续传时使用）
  meta?: any;                   // 课程元数据（续传时使用）
}

// Stream Callbacks
export interface V2StreamCallbacks {
  onPhase: (phase: number, message: string, processor?: Processor) => void;
  onStructure: (
    meta: PackageMetaV2,
    lessonsCount: number,
    lessonsOutline: LessonOutline[],
    processor?: Processor
  ) => void;
  onLessonStart: (
    index: number,
    total: number,
    title: string,
    recommendedForms?: string[],
    complexityLevel?: ComplexityLevel
  ) => void;
  onChunk: (content: string, phase: number, lessonIndex?: number) => void;
  onStepComplete?: (lessonIndex: number, stepIndex: number, step: Step, totalSteps: number) => void;
  onLessonComplete: (index: number, total: number, lesson: Lesson, warning?: string) => void;
  onComplete: (pkg: CoursePackageV2) => void;
  onError: (error: string) => void;
}

// Upload Response
export interface UploadResponse {
  success: boolean;
  filename: string;
  text: string;
  char_count: number;
  file_type?: string;
  word_count?: number;
  reading_time_minutes?: number;
}

// Processor Config Update
export interface ProcessorConfigUpdate {
  enabled?: boolean;
  display_order?: number;
}

// Create Processor Request
export interface CreateProcessorRequest {
  name: string;
  description: string;
  color?: string;
  icon?: string;
  system_prompt: string;
}
