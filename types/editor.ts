/**
 * Course Editor Type Definitions
 * 课程编辑器类型定义
 * 基于 HERCU 课程包标准规范 v2.0
 */

import type {
  StepType,
  ComplexityLevel,
  TimelineData,
  DecisionData,
  ComparisonData,
  ConceptMapData,
} from './coursePackage';
import type { SceneDefinition } from './simulator-engine';

// ============================================
// Component Types
// ============================================

// 编辑器组件类型（扩展自课程包标准）
export type ComponentType = StepType | 'exam' | 'model_3d' | 'reading';

export const COMPONENT_TYPE_LABELS: Record<string, string> = {
  text_content: '文本内容',
  illustrated_content: '图文内容',
  video: '视频',
  simulator: '交互模拟器',
  assessment: '测验',
  quick_check: '快速检测',
};

// ============================================
// AI Provider Types
// ============================================

export type AIProvider = 'claude' | 'gpt' | 'deepseek' | 'qwen';

export const AI_PROVIDER_LABELS: Record<AIProvider, string> = {
  claude: 'Claude (Anthropic)',
  gpt: 'GPT (OpenAI)',
  deepseek: 'DeepSeek',
  qwen: 'Qwen (阿里)',
};

// ============================================
// Config Types
// ============================================

export interface VideoConfig {
  videoUrl: string;
  subtitleUrl?: string;
  duration?: number;
  autoPlay?: boolean;
}

export interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correctIndex: number;
  explanation?: string;
}

export interface QuizConfig {
  questions: QuizQuestion[];
  passingScore: number;
  shuffleQuestions?: boolean;
  showExplanation?: boolean;
}

export interface DiagramConfig {
  type: 'flowchart' | 'mindmap' | 'sequence' | 'static';
  data: Record<string, unknown>;
  title?: string;
  description?: string;
}

export interface IllustratedConfig {
  imageUrl?: string;
  imageAlt?: string;
  imageCaption?: string;
  layout?: 'text_left_image_right' | 'text_top_image_bottom' | 'image_left_text_right';
}

export interface TextConfig {
  content: string;
  format: 'markdown' | 'html' | 'plain';
  keyPoints?: string[];
}

export interface AITutorConfig {
  openingMessage: string;
  conversationGoals: string[];
  maxTurns: number;
}

export interface ExamConfig {
  questions: QuizQuestion[];
  timeLimit?: number; // 考试时间限制（分钟）
  passingScore: number;
  allowRetry?: boolean;
  showResults?: boolean;
}

export interface Model3DConfig {
  modelUrl: string;
  format: 'gltf' | 'glb' | 'obj' | 'fbx';
  annotations?: Array<{
    id: string;
    position: [number, number, number];
    label: string;
    description?: string;
  }>;
  initialCamera?: {
    position: [number, number, number];
    target: [number, number, number];
  };
}

export interface ReadingConfig {
  content: string;
  format: 'markdown' | 'html';
  estimatedReadTime?: number; // 预计阅读时间（分钟）
  keyPoints?: string[];
  references?: Array<{
    title: string;
    url?: string;
  }>;
}

/** 模拟器输入参数配置 */
export interface SimulatorInputConfig {
  id: string;
  name: string;
  label: string;
  type: 'slider' | 'number' | 'select';
  defaultValue: number;
  min?: number;
  max?: number;
  step?: number;
  unit?: string;
  hint?: string;  // 推荐值提示
  options?: Array<{ label: string; value: number }>;
}

/** 模拟器输出配置 */
export interface SimulatorOutputConfig {
  id: string;
  name: string;
  label: string;
  type: 'number' | 'progress' | 'text';
  unit?: string;
  formula?: string;  // 计算公式
  color?: string;    // 进度条颜色
}

// 文科模拟器配置兼容类型（供旧编辑器 API 与页面复用）
export type TimelineConfig = TimelineData;
export type DecisionScenarioConfig = DecisionData;
export type ComparisonConfig = ComparisonData;
export type ConceptMapConfig = ConceptMapData;

// SDL 场景类型别名（供模板系统使用）
export type SDLScene = SceneDefinition;

/** 模拟器配置（新版本：仅支持 custom 和 iframe） */
export interface SimulatorConfig {
  id?: string;
  type: 'custom' | 'iframe' | 'preset' | 'interactive' | 'timeline' | 'decision' | 'comparison' | 'concept-map';
  name: string;
  description: string;
  thumbnail?: string;
  // 模式：sdl（默认）或 custom/html（自定义代码）
  mode?: 'sdl' | 'custom' | 'html';
  // 自定义代码模式
  custom_code?: string;
  html_content?: string;
  // 输入输出（保留向后兼容）
  inputs: SimulatorInputConfig[];
  outputs: SimulatorOutputConfig[];
  // 通用
  iframeUrl?: string;
  presetId?: string;
  parameters?: Record<string, unknown>[];
  initialState?: Record<string, unknown>;
  interfaceSpec?: Record<string, unknown>;
  evaluationLogic?: Record<string, unknown>;
  pixi_config?: Record<string, unknown>;
  instructions?: string[];
  // 变量配置（用于自定义代码模式）
  variables?: Array<{
    id?: string;
    name: string;
    label?: string;
    min?: number;
    max?: number;
    default?: number;
    step?: number;
    unit?: string;
  }>;
  // SDL 场景配置（保留向后兼容）
  scenario?: Record<string, unknown> & {
    description?: string;
  };
  sdl?: SDLScene | Record<string, unknown>;
}

// ============================================
// Node Configuration
// ============================================

export interface NodeConfig {
  type: ComponentType;
  videoConfig?: VideoConfig;
  quizConfig?: QuizConfig;
  diagramConfig?: DiagramConfig;
  illustratedConfig?: IllustratedConfig;
  textConfig?: TextConfig;
  aiTutorConfig?: AITutorConfig;
  examConfig?: ExamConfig;
  model3DConfig?: Model3DConfig;
  readingConfig?: ReadingConfig;
  simulatorConfig?: SimulatorConfig;
}

// ============================================
// Chapter & Section Structure
// ============================================

export interface EditorSection {
  id: string;
  chapterId: string;
  title: string;
  order: number;
  componentType: ComponentType;
  config: NodeConfig;
}

export interface EditorChapter {
  id: string;
  title: string;
  order: number;
  sections: EditorSection[];
  expanded?: boolean;
}

// ============================================
// AI Trigger Types
// ============================================

export type TriggerConditionType = 'on_enter' | 'on_complete' | 'on_error' | 'on_idle' | 'custom';

export interface TriggerCondition {
  type: TriggerConditionType;
  errorType?: string;
  seconds?: number;
  expression?: string;
}

export interface AITrigger {
  id: string;
  name: string;
  condition: TriggerCondition;
  prompt: string;
  enabled: boolean;
}

// ============================================
// AI Guidance Configuration
// ============================================

export interface AIGuidanceConfig {
  provider: AIProvider;
  apiKey?: string;
  persona: string;
  triggers: AITrigger[];
  knowledgeGraphId?: string;
  maxTurns: number;
  temperature: number;
}

// ============================================
// Editor State
// ============================================

// 课程难度等级
export type CourseDifficulty = 'entry' | 'beginner' | 'intermediate' | 'advanced' | 'expert';

export const DIFFICULTY_LABELS: Record<CourseDifficulty, string> = {
  entry: '入门',
  beginner: '基础',
  intermediate: '进阶',
  advanced: '高级',
  expert: '专家',
};

export const DIFFICULTY_COLORS: Record<CourseDifficulty, string> = {
  entry: 'bg-green-100 text-green-700',
  beginner: 'bg-blue-100 text-blue-700',
  intermediate: 'bg-yellow-100 text-yellow-700',
  advanced: 'bg-orange-100 text-orange-700',
  expert: 'bg-red-100 text-red-700',
};

export interface EditorState {
  courseId: string | null;
  courseTitle: string;
  courseCoverImage: string | null;
  courseDifficulty: CourseDifficulty;
  courseTags: string[];  // 课程标签，最多3个
  chapters: EditorChapter[];
  selectedChapterId: string | null;
  selectedSectionId: string | null;
  aiGuidance: AIGuidanceConfig;
  isDirty: boolean;
  isSaving: boolean;
  isLoading: boolean;
}

// ============================================
// API Types
// ============================================

export interface EditorCourseData {
  id: string;
  title: string;
  description?: string;
  difficulty?: CourseDifficulty;
  tags?: string[];
  coverImage?: string;
  chapters: EditorChapter[];
  aiGuidance: AIGuidanceConfig;
  createdAt: string;
  updatedAt: string;
}

export interface SaveCourseRequest {
  title: string;
  coverImage?: string | null;
  difficulty?: CourseDifficulty;
  tags?: string[];  // 课程标签
  chapters: EditorChapter[];
  aiGuidance: AIGuidanceConfig;
}

export interface SaveCourseResponse {
  success: boolean;
  courseId: string;
  updatedAt: string;
}

export interface PublishCourseResponse {
  success: boolean;
  publishedAt: string;
  publishedVersion: string;
}

// ============================================
// Default Values
// ============================================

export const DEFAULT_AI_GUIDANCE: AIGuidanceConfig = {
  provider: 'claude',
  persona: '你是一位友好、耐心的AI教学助手，帮助学生理解课程内容。',
  triggers: [],
  maxTurns: 10,
  temperature: 0.7,
};

export const DEFAULT_NODE_CONFIG: NodeConfig = {
  type: 'text_content',
  textConfig: {
    content: '',
    format: 'markdown',
  },
};

export const createDefaultSection = (chapterId: string, order: number): EditorSection => ({
  id: `section-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
  chapterId,
  title: '新小节',
  order,
  componentType: 'text_content',
  config: { ...DEFAULT_NODE_CONFIG },
});

export const createDefaultChapter = (order: number): EditorChapter => ({
  id: `chapter-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
  title: '新章节',
  order,
  sections: [],
  expanded: true,
});

export const createDefaultTrigger = (): AITrigger => ({
  id: `trigger-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
  name: '新触发器',
  condition: { type: 'on_enter' },
  prompt: '',
  enabled: true,
});
