from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
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


class ProgressResponse(BaseModel):
    id: int
    user_id: int
    node_id: int
    status: NodeStatus
    completion_percentage: float
    time_spent_seconds: int
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
    id: int
    badge_id: str
    badge_name: str
    badge_description: Optional[str] = None
    rarity: str
    icon_url: Optional[str] = None
    unlocked_at: datetime
    is_unlocked: bool = True

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


