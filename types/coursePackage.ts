/**
 * HERCU 课程包标准规范 v2.0 - TypeScript 类型定义
 *
 * 本文件定义了课程包的完整数据结构，供管理端使用。
 */

// ============================================
// 枚举类型
// ============================================

/** 教学形式类型 */
export type StepType =
  | 'text_content'        // 纯文字内容
  | 'illustrated_content' // 图文内容
  | 'video'               // 视频
  | 'simulator'           // 交互式模拟器
  | 'ai_tutor'            // AI 导师
  | 'assessment'          // 测验
  | 'quick_check'         // 快速检测
  | 'practice';           // 简单练习

/** 复杂度等级 */
export type ComplexityLevel = 'simple' | 'standard' | 'rich' | 'comprehensive';

/** 图表类型 */
export type DiagramType =
  | 'static_diagram'
  | 'flowchart'
  | 'line_chart'
  | 'analysis_diagram'
  | 'pyramid'
  | 'comparison';

/** 测验类型 */
export type AssessmentType =
  | 'quick_check'
  | 'scenario_quiz'
  | 'multiple_choice'
  | 'open_ended';

/** AI 导师模式 */
export type AITutorMode =
  | 'proactive_assessment'  // 主动评估（苏格拉底式）
  | 'reactive_qa'           // 被动问答
  | 'guided_practice';      // 引导练习

/** Step 触发条件 */
export type StepTrigger =
  | ''                      // 默认
  | 'required'              // 必须完成
  | 'optional_user_request'; // 用户可选请求

// ============================================
// 内容规格类型
// ============================================

/** 文字内容规格 */
export interface TextContentSpec {
  body: string;
  key_points?: string[];
}

/** 图表标注 */
export interface DiagramAnnotation {
  position: 'top' | 'bottom' | 'left' | 'right' | 'center';
  text: string;
}

/** 图表规格 */
export interface DiagramSpec {
  diagram_id: string;
  type: DiagramType;
  description: string;
  annotations?: DiagramAnnotation[];
  design_notes?: string;
  data_series?: Array<{
    name: string;
    trend?: string;
    [key: string]: any;
  }>;
}

/** 图文内容规格 */
export interface IllustratedContentSpec {
  text: string;
}

/** 视频场景 */
export interface VideoScene {
  timecode: string;
  scene: string;
  narration: string;
}

/** 视频脚本 */
export interface VideoScript {
  scenes: VideoScene[];
}

/** 嵌入式互动 */
export interface EmbeddedInteraction {
  timestamp: string;
  type: 'pause_and_ask' | 'highlight' | 'checkpoint';
  question?: string;
  options?: string[];
  correct?: string;
}

/** 视频规格 */
export interface VideoSpec {
  video_id: string;
  duration: string;
  script?: VideoScript;
  production_notes?: string;
  video_url?: string;  // 实际视频URL（如果已上传）
}

/** 探测问题 */
export interface ProbingQuestion {
  question: string;
  intent: string;
  expected_elements?: string[];
  follow_ups?: {
    if_superficial?: string;
    if_misconception?: string;
    if_correct?: string;
  };
}

/** 诊断焦点 */
export interface DiagnosticFocus {
  key_concepts?: string[];
  common_misconceptions?: string[];
  transfer_scenarios?: string[];
}

/** AI 导师规格 */
export interface AITutorSpec {
  mode?: AITutorMode;
  opening_message: string;
  probing_questions?: ProbingQuestion[];
  conversation_goals?: Array<{
    goal: string;
    examples?: string[];
  }>;
  diagnostic_focus?: DiagnosticFocus;
  mastery_criteria?: string;
  max_turns: number;
}

/** 测验问题 */
export interface AssessmentQuestion {
  question: string;
  scenario?: string;
  options?: string[];
  correct?: string;
  explanation?: string;
}

/** 测验规格 */
export interface AssessmentSpec {
  type: AssessmentType;
  questions: AssessmentQuestion[];
  pass_required?: boolean;
  rubric?: string[];       // 开放题评分标准
  min_words?: number;      // 开放题最少字数
  ai_grading?: boolean;    // 是否使用 AI 评分
}

// ============================================
// 模拟器类型
// ============================================

/** 模拟器类型 */
export type SimulatorType = 'preset' | 'custom' | 'iframe' | 'timeline' | 'decision' | 'comparison' | 'concept-map';

/** 模拟器输入参数 */
export interface SimulatorInput {
  id: string;
  name: string;
  label: string;
  type: 'number' | 'slider' | 'boolean' | 'select';
  defaultValue: number | string | boolean;
  min?: number;
  max?: number;
  step?: number;
  unit?: string;
  options?: Array<{ label: string; value: string | number }>;
}

/** 模拟器输出 */
export interface SimulatorOutput {
  id: string;
  name: string;
  label: string;
  type: 'number' | 'text' | 'chart' | 'animation';
  unit?: string;
  formula?: string;  // 计算公式，如 "input.force / input.mass"
}

/** 评估标准 */
export interface EvaluationCriterion {
  id: string;
  name: string;
  description?: string;
  targetValue?: number;
  tolerance?: number;
}

// ============================================
// 文科模拟器数据类型
// ============================================

/** 时间线事件 */
export interface TimelineEvent {
  id: string;
  year: string;
  title: string;
  description: string;
  category?: string;
  highlight?: boolean;
}

/** 时间线数据 */
export interface TimelineData {
  title: string;
  events: TimelineEvent[];
}

/** 决策选项 */
export interface DecisionOption {
  id: string;
  label: string;
  result: string;
  isOptimal?: boolean;
}

/** 决策情景数据 */
export interface DecisionData {
  title: string;
  scenario: string;
  question: string;
  options: DecisionOption[];
  analysis?: string;
}

/** 对比项 */
export interface ComparisonItem {
  id: string;
  name: string;
  attributes: Record<string, string>;
}

/** 对比分析数据 */
export interface ComparisonData {
  title: string;
  dimensions: string[];
  items: ComparisonItem[];
  conclusion?: string;
}

/** 概念节点 */
export interface ConceptNode {
  id: string;
  label: string;
  description?: string;
  category?: string;
}

/** 概念关系 */
export interface ConceptRelation {
  from: string;
  to: string;
  label?: string;
}

/** 概念关系图数据 */
export interface ConceptMapData {
  title: string;
  nodes: ConceptNode[];
  relations: ConceptRelation[];
}

/** 模拟器规格 */
export interface SimulatorSpec {
  simulator_id: string;
  name: string;
  description: string;
  type: SimulatorType;

  // 模式：sdl（默认）或 custom（自定义代码）
  mode?: 'sdl' | 'custom';

  // 自定义代码模式
  custom_code?: string;
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

  // 预设模拟器 ID
  preset_id?: string;

  // SDL 模板 ID (用于从模板库加载)
  template_id?: string;

  // 理科模拟器配置
  inputs?: SimulatorInput[];
  outputs?: SimulatorOutput[];

  // 文科模拟器数据
  timeline?: TimelineData;
  decision?: DecisionData;
  comparison?: ComparisonData;
  concept_map?: ConceptMapData;

  // iframe 嵌入
  iframe_url?: string;
  iframe_width?: number;
  iframe_height?: number;

  // 场景说明
  instructions?: string[];

  // 评估配置
  evaluation?: {
    criteria: EvaluationCriterion[];
    pass_threshold?: number;
  };
}

// ============================================
// Step 类型
// ============================================

/** 课时步骤基础接口 */
export interface LessonStepBase {
  step_id: string;
  type: StepType;
  title: string;
  trigger?: StepTrigger;
  embedded_interactions?: EmbeddedInteraction[];
}

/** 文字内容步骤 */
export interface TextContentStep extends LessonStepBase {
  type: 'text_content';
  content: TextContentSpec;
}

/** 图文内容步骤 */
export interface IllustratedContentStep extends LessonStepBase {
  type: 'illustrated_content';
  content: IllustratedContentSpec;
  diagram_spec?: DiagramSpec;
}

/** 视频步骤 */
export interface VideoStep extends LessonStepBase {
  type: 'video';
  video_spec: VideoSpec;
}

/** 模拟器步骤 */
export interface SimulatorStep extends LessonStepBase {
  type: 'simulator';
  simulator_spec: SimulatorSpec;
}

/** AI 导师步骤 */
export interface AITutorStep extends LessonStepBase {
  type: 'ai_tutor';
  ai_spec: AITutorSpec;
}

/** 测验步骤 */
export interface AssessmentStep extends LessonStepBase {
  type: 'assessment' | 'quick_check';
  assessment_spec: AssessmentSpec;
}

/** 练习步骤 */
export interface PracticeStep extends LessonStepBase {
  type: 'practice';
  content: TextContentSpec;
}

/** 课时步骤联合类型 */
export type LessonStep =
  | TextContentStep
  | IllustratedContentStep
  | VideoStep
  | SimulatorStep
  | AITutorStep
  | AssessmentStep
  | PracticeStep;

// ============================================
// 课时类型
// ============================================

/** 课时 */
export interface Lesson {
  lesson_id: string;
  title: string;
  order: number;
  total_steps: number;
  rationale: string;
  estimated_minutes: number;
  learning_objectives: string[];
  complexity_level: ComplexityLevel;
  prerequisites?: string[];
  script: LessonStep[];
}

// ============================================
// 课程包类型
// ============================================

/** 课程包元数据 */
export interface PackageMeta {
  title: string;
  description: string;
  cover_url?: string;
  source_info?: string;
  total_lessons: number;
  estimated_hours: number;
  style: string;
  created_at: string;
  statistics?: PackageStatistics;
}

/** 课程包统计 */
export interface PackageStatistics {
  total_steps: number;
  form_distribution: Record<StepType, number>;
  complexity_distribution: Record<ComplexityLevel, number>;
  resources_needed?: {
    videos: number;
    video_minutes: number;
    diagrams: number;
  };
}

/** 课时依赖边 */
export interface PackageEdge {
  id: string;
  from: string;
  to: string;
  type: 'prerequisite';
}

/** 全局 AI 配置 */
export interface GlobalAIConfig {
  tutor_persona?: string;
  fallback_responses?: string[];
}

/** 完整课程包 */
export interface CoursePackage {
  id: string;
  version: '2.0.0';
  meta: PackageMeta;
  lessons: Lesson[];
  edges?: PackageEdge[];
  global_ai_config?: GlobalAIConfig;
}

// ============================================
// 辅助类型
// ============================================

/** 课程包导入请求 */
export interface CoursePackageImportRequest {
  package_data: CoursePackage;
  course_id?: number;
}

/** 课程包导入响应 */
export interface CoursePackageImportResponse {
  success: boolean;
  course_id: number;
  package_id: string;
  lessons_imported: number;
  message?: string;
}

/** Step 类型守卫 */
export function isTextContentStep(step: LessonStep): step is TextContentStep {
  return step.type === 'text_content';
}

export function isIllustratedContentStep(step: LessonStep): step is IllustratedContentStep {
  return step.type === 'illustrated_content';
}

export function isVideoStep(step: LessonStep): step is VideoStep {
  return step.type === 'video';
}

export function isAITutorStep(step: LessonStep): step is AITutorStep {
  return step.type === 'ai_tutor';
}

export function isAssessmentStep(step: LessonStep): step is AssessmentStep {
  return step.type === 'assessment' || step.type === 'quick_check';
}

export function isPracticeStep(step: LessonStep): step is PracticeStep {
  return step.type === 'practice';
}

export function isSimulatorStep(step: LessonStep): step is SimulatorStep {
  return step.type === 'simulator';
}
