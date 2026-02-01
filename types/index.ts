/**
 * TypeScript Type Definitions Index
 * Central export point for all type definitions
 */

// Course types
export type {
  CourseCategory,
  CourseDifficulty,
  Instructor,
  CourseModule,
  Course,
  CourseProgress,
  CourseEnrollment,
} from './course';

// Timeline types
export type {
  NodeType,
  NodeStatus,
  UnlockCondition,
  TimelineNode,
  NodeState,
  TimelineState,
  LearningPath,
} from './timeline';

// AI types
export type {
  AIMessageRole,
  AIContextType,
  Reference,
  AIMessage,
  AIContext,
  AIChatSession,
  AIMode,
  AITrainingPlan,
} from './ai';

// User types
export type {
  UserRole,
  SubscriptionPlan,
  SubscriptionStatus,
  User,
  UserSettings,
  UserStats,
  Activity,
  Badge,
  Subscription,
  StorageInfo,
  Invoice,
} from './user';

// Admin types
export type {
  AdminRole,
  AdminLevel,
  AdminPermission,
  AdminUser,
  AdminAuthState,
  AdminLoginRequest,
  AdminLoginResponse,
  LogLevel,
  LogType,
  SystemLog,
  SystemSettings,
  Role,
  PermissionDefinition,
  SystemStatus,
  QuickAction,
  RecentActivity,
} from './admin';

export {
  ADMIN_LEVEL_PERMISSIONS,
  ADMIN_LEVEL_NAMES,
  ADMIN_LEVEL_DESCRIPTIONS,
} from './admin';

// Management types
export type {
  UserManagementFilters,
  UserManagementSort,
  UserListItem,
  UserDetailStats,
  BulkUserAction,
  CourseManagementFilters,
  CourseManagementSort,
  CourseListItem,
  CourseDetailStats,
  CourseFormData,
  ContentFilters,
  ResourceFile,
  ResourceUploadProgress,
  ContentLibraryStats,
  PaginationConfig,
  PaginatedResponse,
  BulkOperationResult,
  ExportConfig,
} from './management';

// Analytics types
export type {
  TimeRange,
  CustomTimeRange,
  DashboardStats,
  UserAnalytics,
  TrendData,
  RetentionData,
  DistributionData,
  TopUserData,
  EngagementData,
  CourseAnalytics,
  TopCourseData,
  CoursePerformanceData,
  LearningAnalytics,
  HeatmapData,
  FunnelData,
  StrugglingTopicData,
  SystemAnalytics,
  EndpointData,
  Report,
  ReportSchedule,
  ReportData,
  ChartData,
  TableData,
  TableColumn,
  RealtimeMetrics,
  ComparisonData,
} from './analytics';

// Editor types
export type {
  ComponentType,
  AIProvider,
  VideoConfig,
  QuizQuestion,
  QuizConfig,
  DiagramConfig,
  TextConfig,
  AITutorConfig,
  SimulatorInputConfig,
  SimulatorOutputConfig,
  TimelineConfig,
  DecisionScenarioConfig,
  ComparisonConfig,
  ConceptMapConfig,
  SimulatorConfig,
  NodeConfig,
  EditorSection,
  EditorChapter,
  TriggerConditionType,
  TriggerCondition,
  AITrigger,
  AIGuidanceConfig,
  EditorState,
  EditorCourseData,
  SaveCourseRequest,
  SaveCourseResponse,
  PublishCourseResponse,
} from './editor';

export {
  COMPONENT_TYPE_LABELS,
  AI_PROVIDER_LABELS,
  DEFAULT_AI_GUIDANCE,
  DEFAULT_NODE_CONFIG,
  createDefaultSection,
  createDefaultChapter,
  createDefaultTrigger,
} from './editor';

// Course Package types (v2.0 标准)
// Note: TimelineEvent, DecisionOption, ComparisonItem, ConceptNode, ConceptRelation
// are also defined in editor.ts for editor config. Import from coursePackage directly if needed.
export type {
  StepType,
  ComplexityLevel,
  DiagramType,
  AssessmentType,
  AITutorMode,
  StepTrigger,
  TextContentSpec,
  DiagramAnnotation,
  DiagramSpec,
  IllustratedContentSpec,
  VideoScene,
  VideoScript,
  EmbeddedInteraction,
  VideoSpec,
  SimulatorType,
  SimulatorInput,
  SimulatorOutput,
  EvaluationCriterion,
  TimelineData,
  DecisionData,
  ConceptMapData,
  SimulatorSpec,
  ProbingQuestion,
  DiagnosticFocus,
  AITutorSpec,
  AssessmentQuestion,
  AssessmentSpec,
  LessonStepBase,
  TextContentStep,
  IllustratedContentStep,
  VideoStep,
  SimulatorStep,
  AITutorStep,
  AssessmentStep,
  PracticeStep,
  LessonStep,
  Lesson,
  PackageMeta,
  PackageStatistics,
  PackageEdge,
  GlobalAIConfig,
  CoursePackage,
  CoursePackageImportRequest,
  CoursePackageImportResponse,
} from './coursePackage';

export {
  isTextContentStep,
  isIllustratedContentStep,
  isVideoStep,
  isSimulatorStep,
  isAITutorStep,
  isAssessmentStep,
  isPracticeStep,
} from './coursePackage';
