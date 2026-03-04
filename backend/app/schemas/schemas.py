from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import json
from app.models.models import DifficultyLevel, NodeType, NodeStatus


# ============ Authentication Schemas ============

class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str
    expires_in: Optional[int] = None  # Token 有效期（秒）


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[int] = None


# ============ User Schemas ============

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    id: int
    avatar_url: Optional[str] = None
    is_active: bool
    is_premium: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============ Course Schemas ============

class CourseBase(BaseModel):
    name: str
    description: Optional[str] = None
    difficulty: DifficultyLevel
    tags: List[str] = []
    instructor: Optional[str] = None
    duration_hours: Optional[float] = None

    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        """Parse tags from JSON string if needed"""
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else []
            except (json.JSONDecodeError, TypeError):
                return []
        return []


class CourseCreate(CourseBase):
    pass


class CourseResponse(CourseBase):
    id: int
    thumbnail_url: Optional[str] = None
    is_published: bool
    created_at: datetime
    node_count: Optional[int] = None
    progress_percentage: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class CourseDetail(CourseResponse):
    """Detailed course info with progress"""
    total_nodes: int = 0
    completed_nodes: int = 0
    progress_percentage: float = 0.0


# ============ Course Node Schemas ============

class CourseNodeBase(BaseModel):
    node_id: str
    type: NodeType
    component_id: str
    title: str
    description: Optional[str] = None
    timeline_config: Optional[Dict[str, Any]] = None
    sequence: int = 0
    parent_id: Optional[int] = None
    unlock_condition: Optional[Dict[str, Any]] = None


class CourseNodeCreate(CourseNodeBase):
    course_id: int


class CourseNodeResponse(CourseNodeBase):
    id: int
    course_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseNodeWithProgress(CourseNodeResponse):
    """Node with user progress"""
    status: NodeStatus = NodeStatus.LOCKED
    completion_percentage: float = 0.0
    time_spent_seconds: int = 0


# ============ Learning Progress Schemas ============

class ProgressUpdate(BaseModel):
    status: Optional[NodeStatus] = None
    completion_percentage: Optional[float] = Field(None, ge=0, le=100)
    time_spent_seconds: Optional[int] = Field(None, ge=0)
    current_step_index: Optional[int] = None


class ProgressResponse(BaseModel):
    id: int
    user_id: int
    node_id: int
    status: NodeStatus
    completion_percentage: float
    time_spent_seconds: int
    current_step_index: int = 0
    last_accessed: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============ Training Plan Schemas ============

class TrainingPlanCreate(BaseModel):
    title: str
    plan_data: Dict[str, Any]
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class TrainingPlanResponse(BaseModel):
    id: int
    user_id: int
    title: str
    plan_data: Dict[str, Any]
    status: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============ AI Schemas ============

class AIGuideChatRequest(BaseModel):
    node_id: Union[int, str]
    user_message: str
    context: Optional[Dict[str, Any]] = None


class AIGuideChatResponse(BaseModel):
    response: str
    suggestions: Optional[List[str]] = None


class AIGeneratePlanRequest(BaseModel):
    role: str  # e.g., "athlete", "coach"
    goal: str  # e.g., "strength", "endurance"
    duration_weeks: int = 12
    sessions_per_week: int = 4
    experience_level: str = "intermediate"  # beginner, intermediate, advanced
    available_equipment: List[str] = []
    constraints: Optional[str] = None
    sport: Optional[str] = None
    current_phase: Optional[str] = None


class AIGeneratePlanResponse(BaseModel):
    plan_data: Dict[str, Any]
    plan_id: Optional[int] = None


class AIAdjustPlanRequest(BaseModel):
    plan_id: int
    instruction: str  # Natural language instruction


# ============ Dashboard Schemas ============

class UserSummary(BaseModel):
    total_learning_hours: float
    consecutive_days: int
    weekly_progress: float
    weekly_intensity: float
    active_courses: int
    completed_courses: int


class RecommendedCourse(BaseModel):
    course: CourseResponse
    reason: str


# ============ Achievement Schemas ============

class AchievementResponse(BaseModel):
    badge_id: str
    badge_name: str
    badge_description: Optional[str] = None
    rarity: str
    icon_url: Optional[str] = None
    unlocked_at: Optional[datetime] = None
    is_unlocked: bool = False
    unlock_animation: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SkillTreeNode(BaseModel):
    skill_id: str
    skill_name: str
    category: str
    level: int  # 0-3
    progress: float  # 0-100
    dependencies: List[str] = []


# ============ Course Package Ingestion Schemas ============

class TimelineStep(BaseModel):
    """Single step in a timeline configuration"""
    stepId: str
    type: str  # "video", "simulator", "quiz", "text"

    # Video specific
    videoUrl: Optional[str] = None
    duration: Optional[int] = None
    pauseAt: Optional[List[int]] = None
    aiPromptAtPause: Optional[str] = None

    # Simulator specific
    simulatorId: Optional[str] = None
    props: Optional[Dict[str, Any]] = None
    completionCriteria: Optional[Dict[str, Any]] = None

    # Quiz specific
    question: Optional[str] = None
    options: Optional[List[str]] = None
    correctAnswer: Optional[int] = None

    # Text specific
    content: Optional[str] = None

    # Common
    guidePrompt: Optional[str] = None


class TimelineConfig(BaseModel):
    """Timeline configuration for a course node"""
    steps: List[TimelineStep]


class UnlockCondition(BaseModel):
    """Unlock condition for a course node"""
    type: str  # "none", "previous_complete", "manual", "all_complete"
    nodeIds: Optional[List[str]] = None  # For "all_complete" type


class PackageNodeConfig(BaseModel):
    """Configuration for a single node in the course package"""
    nodeId: str = Field(..., description="Unique node identifier")
    type: str = Field(..., description="Node type: video, simulator, quiz, reading, practice")
    componentId: str = Field(..., description="Frontend component ID")
    title: str = Field(..., description="Node title")
    description: Optional[str] = Field(None, description="Node description")
    sequence: int = Field(0, description="Order within parent")
    parentId: Optional[str] = Field(None, description="Parent node ID for tree structure")

    # Timeline configuration
    timelineConfig: Optional[TimelineConfig] = Field(None, description="Multi-step learning flow")

    # Unlock logic
    unlockCondition: Optional[UnlockCondition] = Field(
        default_factory=lambda: UnlockCondition(type="previous_complete"),
        description="Unlock condition"
    )

    # AI guidance
    guidePrompt: Optional[str] = Field(None, description="AI guide prompt for this node")

    # Metadata
    estimatedMinutes: Optional[int] = Field(None, description="Estimated completion time")
    tags: Optional[List[str]] = Field(default_factory=list, description="Node tags")


class CourseManifest(BaseModel):
    """Course package manifest - the main configuration file"""
    # Course metadata
    courseName: str = Field(..., description="Course name")
    courseDescription: Optional[str] = Field(None, description="Course description")
    difficulty: str = Field(..., description="beginner, intermediate, advanced, expert")
    instructor: Optional[str] = Field(None, description="Instructor name")
    tags: List[str] = Field(default_factory=list, description="Course tags")
    durationHours: Optional[float] = Field(None, description="Total course duration")
    thumbnailUrl: Optional[str] = Field(None, description="Course thumbnail URL")

    # Course structure
    nodes: List[PackageNodeConfig] = Field(..., description="List of all course nodes")

    # Package metadata
    packageVersion: str = Field("1.0", description="Package format version")


class CourseUpdate(BaseModel):
    """Schema for updating course metadata"""
    name: Optional[str] = Field(None, description="Course name")
    description: Optional[str] = Field(None, description="Course description")
    difficulty: Optional[str] = Field(None, description="beginner, intermediate, advanced, expert")
    instructor: Optional[str] = Field(None, description="Instructor name")
    tags: Optional[List[str]] = Field(None, description="Course tags")
    duration_hours: Optional[float] = Field(None, description="Total course duration")
    thumbnail_url: Optional[str] = Field(None, description="Course thumbnail URL")
    is_published: Optional[bool] = Field(None, description="Publication status")


class NodeUpdate(BaseModel):
    """Schema for updating a single node"""
    title: Optional[str] = Field(None, description="Node title")
    description: Optional[str] = Field(None, description="Node description")
    sequence: Optional[int] = Field(None, description="Order within parent")
    parentId: Optional[str] = Field(None, description="Parent node ID")
    timelineConfig: Optional[TimelineConfig] = Field(None, description="Timeline configuration")
    unlockCondition: Optional[UnlockCondition] = Field(None, description="Unlock condition")
    guidePrompt: Optional[str] = Field(None, description="AI guide prompt")
    estimatedMinutes: Optional[int] = Field(None, description="Estimated completion time")
    tags: Optional[List[str]] = Field(None, description="Node tags")
    createdAt: Optional[str] = Field(None, description="Package creation timestamp")
    author: Optional[str] = Field(None, description="Package author")


class CoursePackageUpload(BaseModel):
    """Request for uploading a course package"""
    manifest: CourseManifest
    publishImmediately: bool = Field(False, description="Publish course immediately after ingestion")
    generateQuiz: bool = Field(False, description="Generate quiz bank for each node using AI")


class CourseIngestionResponse(BaseModel):
    """Response after course ingestion"""
    success: bool
    courseId: int
    nodesCreated: int
    message: str
    errors: Optional[List[str]] = None


class CoursePackageValidation(BaseModel):
    """Validation result for a course package"""
    isValid: bool
    errors: List[str] = []
    warnings: List[str] = []
    nodeCount: int = 0


# ============ BKT Knowledge Tracking Schemas ============

class SubjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class SubjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class KnowledgeNodeCreate(BaseModel):
    subject_id: int
    course_node_id: Optional[int] = None
    code: str
    name: str
    description: Optional[str] = None
    difficulty: float = Field(0.5, ge=0, le=1)
    parent_code: Optional[str] = None
    prerequisites: Optional[List[int]] = []

class KnowledgeNodeResponse(BaseModel):
    id: int
    subject_id: int
    course_node_id: Optional[int] = None
    code: str
    name: str
    description: Optional[str] = None
    difficulty: float
    parent_code: Optional[str] = None
    prerequisites: Optional[List[int]] = []
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class StudentEventCreate(BaseModel):
    knowledge_node_id: int
    event_type: str = Field(..., pattern="^(answer|hint|skip|review)$")
    is_correct: Optional[int] = None
    response_time_ms: Optional[int] = None
    event_data: Optional[Dict[str, Any]] = {}

class StudentEventResponse(BaseModel):
    id: int
    user_id: int
    knowledge_node_id: int
    event_type: str
    is_correct: Optional[int] = None
    response_time_ms: Optional[int] = None
    event_data: Optional[Dict[str, Any]] = {}
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class StudentMisconceptionResponse(BaseModel):
    id: int
    user_id: int
    knowledge_node_id: int
    misconception: str
    frequency: int
    last_seen_at: Optional[datetime] = None
    resolved: int
    created_at: datetime
    node_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# ============ Emotion Schemas (Phase 2) ============

class StudentEmotionResponse(BaseModel):
    id: int
    user_id: int
    emotion_type: str
    intensity: float
    confidence: float
    trigger_type: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ============ Learning Path Schemas (Phase 2) ============

class LearningPathRequest(BaseModel):
    subject_id: int
    session_duration: int = Field(30, ge=5, le=120, description="计划学习时长（分钟）")

class LearningPathItemResponse(BaseModel):
    knowledge_node_id: int
    node_code: str
    node_name: str
    activity_type: str
    estimated_minutes: int
    target_difficulty: float
    mastery_before: float
    reason: str
    completed: Optional[bool] = False
    completed_at: Optional[str] = None

class LearningPathResponse(BaseModel):
    id: int
    user_id: int
    subject_id: int
    status: str
    session_duration: int
    emotion_snapshot: Optional[str] = None
    total_nodes: int
    completed_nodes: int
    path_items: List[LearningPathItemResponse] = []
    created_at: datetime
    completed_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class CompleteNodeRequest(BaseModel):
    knowledge_node_id: int


# ============ Spaced Repetition Schemas (Phase 4) ============

class RecordReviewRequest(BaseModel):
    knowledge_node_id: int
    rating: int = Field(..., ge=1, le=4, description="1=Again, 2=Hard, 3=Good, 4=Easy")
    review_type: str = Field("mini_quiz", pattern="^(flashcard|mini_quiz|simulator_replay|explain_to_ai)$")

class DueReviewsRequest(BaseModel):
    max_count: int = Field(20, ge=1, le=50)
    max_minutes: int = Field(30, ge=5, le=120)
    subject_id: Optional[int] = None


# ============ Learning Report & Metacognitive Schemas (Phase 5) ============

class MetacognitivePromptRequest(BaseModel):
    trigger: str = Field(..., pattern="^(after_practice_set|after_hard_correct|after_error_recovery|session_start|session_end)$")
    knowledge_node_id: Optional[int] = None

class MetacognitiveResponseRequest(BaseModel):
    log_id: int
    response_text: str = Field(..., min_length=1, max_length=2000)


# ============ Diagnostic Tutor Schemas (Phase 3) ============

class StartConversationRequest(BaseModel):
    knowledge_node_id: int
    mode: str = Field("adaptive", pattern="^(adaptive|diagnostic|remedial|challenge)$")
    initial_message: Optional[str] = Field(None, max_length=1000)

class SendMessageRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=64)
    message: str = Field(..., min_length=1, max_length=2000)


# ============ Recommendation Schemas (Phase 6) ============

class CourseRecommendationCreate(BaseModel):
    source_course_id: int
    target_course_id: int
    relation_type: str = Field(..., pattern="^(prerequisite|complementary|advanced|cross_discipline)$")
    weight: float = Field(1.0, ge=0.0, le=1.0)
    reason: Optional[str] = Field(None, max_length=500)


# ============ Assessment Schemas (Phase 7) ============

class LearningAssessmentRequest(BaseModel):
    knowledge_node_id: Optional[int] = None
    assessment_type: str = Field("auto", pattern="^(auto|manual|session_end)$")

class AdaptiveFeedbackRequest(BaseModel):
    knowledge_node_id: Optional[int] = None


# ============ Multi-Task & Multi-Objective Schemas (Phase 8) ============

class ObjectiveWeights(BaseModel):
    mastery: float = Field(0.35, ge=0, le=1, description="掌握度提升权重")
    retention: float = Field(0.25, ge=0, le=1, description="记忆保持权重")
    emotion: float = Field(0.2, ge=0, le=1, description="情感稳定权重")
    efficiency: float = Field(0.2, ge=0, le=1, description="时间效率权重")

class MultiTaskRequest(BaseModel):
    session_minutes: int = Field(30, ge=5, le=120, description="计划学习时长（分钟）")
    subject_id: Optional[int] = None
    objective_weights: Optional[ObjectiveWeights] = None

class MultiObjectiveFeedbackRequest(BaseModel):
    plan_id: Optional[int] = None
    subject_id: Optional[int] = None


# ============ Subject Knowledge Graph Schemas (Phase 9) ============

class SubjectRelationCreate(BaseModel):
    source_subject_id: int
    target_subject_id: int
    relation_type: str = Field(..., pattern="^(prerequisite|extension|cross_discipline|complementary)$")
    weight: float = Field(1.0, ge=0, le=1)
    description: Optional[str] = None
    shared_concepts: Optional[list] = []


# ============ Cross-Disciplinary & Knowledge Inference Schemas (Phase 10) ============

class ConceptBridgeCreate(BaseModel):
    source_node_id: int
    target_node_id: int
    concept_name: str = Field(..., min_length=1, max_length=200)
    transfer_weight: float = Field(0.5, ge=0, le=1)
    description: Optional[str] = None

class TransferPredictionRequest(BaseModel):
    source_subject_id: int
    target_subject_id: int

class CrossDisciplinaryPathRequest(BaseModel):
    target_subject_id: int
    session_minutes: int = Field(30, ge=5, le=120)


# ============ Course Recommendation Schemas (Phase 11) ============

class CourseRelationCreate(BaseModel):
    source_course_id: int
    target_course_id: int
    relation_type: str = Field(..., pattern="^(prerequisite|advanced|parallel|supplementary)$")
    weight: float = Field(1.0, ge=0, le=1)
    description: Optional[str] = None

class RecommendedCoursesRequest(BaseModel):
    limit: int = Field(10, ge=1, le=30)
    subject_id: Optional[int] = None

class CourseLearningPathRequest(BaseModel):
    course_id: Optional[int] = None
    session_minutes: int = Field(30, ge=5, le=120)


# ============ Phase 12: Learning Feedback & Smart Report ============

class ProgressFeedbackRequest(BaseModel):
    subject_id: Optional[int] = None
    include_suggestions: bool = True

class EmotionFeedbackRequest(BaseModel):
    subject_id: Optional[int] = None

class SmartReportRequest(BaseModel):
    period: str = Field("weekly", description="daily/weekly/monthly")
    subject_id: Optional[int] = None


# ============ Phase 13: Agent RL & Adaptive Task Generation ============

class AdaptiveTaskRequest(BaseModel):
    subject_id: Optional[int] = None
    session_minutes: int = Field(30, ge=5, le=120)

class RewardSignalRequest(BaseModel):
    strategy_type: str = Field(..., description="task_generation/difficulty_selection/content_type")
    action_taken: Dict[str, Any] = {}
    student_state_before: Dict[str, Any] = {}
    student_state_after: Dict[str, Any] = {}

class AdaptivePathRequest(BaseModel):
    subject_id: Optional[int] = None
    session_minutes: int = Field(30, ge=5, le=120)
    include_cross_discipline: bool = False


# ============ Phase 15: Predictive Analytics & Goal Management ============

class GoalCreateRequest(BaseModel):
    goal_type: str = Field(..., pattern="^(mastery|streak|completion|custom)$")
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    subject_id: Optional[int] = None
    node_id: Optional[int] = None
    target_value: float = Field(..., gt=0)
    deadline: Optional[datetime] = None

class GoalUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    target_value: Optional[float] = Field(None, gt=0)
    deadline: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(active|completed|abandoned)$")

class PredictiveRequest(BaseModel):
    subject_id: Optional[int] = None
    target_mastery: float = Field(0.8, ge=0.1, le=1.0)

class ComparativeRequest(BaseModel):
    period: str = Field("weekly", pattern="^(weekly|monthly)$")
    subject_id: Optional[int] = None

class HabitCalendarRequest(BaseModel):
    days: int = Field(30, ge=7, le=90)

# ============ Phase 16: 推荐精准化与跨学科深度集成 ============

class TransferUpdateRequest(BaseModel):
    source_subject_id: int
    target_subject_id: int

class TemporalPatternRequest(BaseModel):
    days: int = Field(30, ge=7, le=90)