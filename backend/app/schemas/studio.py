"""
Studio Schemas - Pydantic models for Studio API
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime
import json
from enum import Enum


# ============================================
# Processor Schemas
# ============================================

class ProcessorBase(BaseModel):
    """Base processor schema"""
    id: str
    name: str
    description: str
    version: str = "1.0.0"
    author: Optional[str] = None
    tags: List[str] = []
    color: str = "#3B82F6"
    icon: str = "Sparkles"

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


class ProcessorWithConfig(ProcessorBase):
    """Processor with configuration"""
    enabled: bool = True
    display_order: int = 0
    is_official: bool = False
    is_custom: bool = False
    system_prompt: Optional[str] = None


class ProcessorConfigUpdate(BaseModel):
    """Update processor config"""
    enabled: Optional[bool] = None
    display_order: Optional[int] = None


class CreateProcessorRequest(BaseModel):
    """Create custom processor"""
    name: str
    description: str
    color: Optional[str] = "#3B82F6"
    icon: Optional[str] = "Sparkles"
    system_prompt: str


# ============================================
# Lesson & Step Schemas
# ============================================

class TextContent(BaseModel):
    """Text content for steps"""
    body: str
    key_points: Optional[List[str]] = None


class IllustratedContent(BaseModel):
    """Illustrated content"""
    text: str


class DiagramSpec(BaseModel):
    """Diagram specification"""
    diagram_id: str
    type: str  # static_diagram, flowchart, line_chart, etc.
    description: str
    annotations: Optional[List[Dict[str, str]]] = None
    design_notes: Optional[str] = None


class VideoSpec(BaseModel):
    """Video specification"""
    video_id: str
    duration: str
    script: Optional[Dict[str, Any]] = None
    production_notes: Optional[str] = None


class EmbeddedInteraction(BaseModel):
    """Embedded interaction in video"""
    timestamp: str
    type: str
    question: str
    options: List[str]
    correct: str


class SimulatorSpec(BaseModel):
    """HTML Simulator specification (统一使用HTML模拟器)"""
    mode: str = "html"  # 固定为 "html"
    name: str
    description: str
    html_content: Optional[str] = None  # HTML/CSS/JS 代码
    # 保留旧字段以兼容数据库已有数据
    custom_code: Optional[str] = None  # 兼容字段，映射到 html_content
    simulator_id: Optional[str] = None
    type: Optional[str] = None
    variables: Optional[List[Dict[str, Any]]] = None
    inputs: Optional[List[Dict[str, Any]]] = None
    outputs: Optional[List[Dict[str, Any]]] = None
    instructions: Optional[List[str]] = None


class AITutorSpec(BaseModel):
    """AI Tutor specification"""
    opening_message: str
    conversation_goals: List[Dict[str, Any]]
    max_turns: int = 10


class AssessmentQuestion(BaseModel):
    """Assessment question"""
    question: str
    scenario: Optional[str] = None
    options: List[str]
    correct: str
    explanation: Optional[str] = None


class AssessmentSpec(BaseModel):
    """Assessment specification"""
    type: str  # quick_check, scenario_quiz, etc.
    questions: List[AssessmentQuestion]
    pass_required: bool = True


class PracticeContent(BaseModel):
    """Practice content"""
    instructions: str
    tasks: List[str]


class LessonStep(BaseModel):
    """Lesson step"""
    step_id: str
    type: str  # text_content, illustrated_content, video, simulator, ai_tutor, assessment, etc.
    title: str
    content: Optional[Dict[str, Any]] = None
    diagram_spec: Optional[DiagramSpec] = None
    video_spec: Optional[VideoSpec] = None
    embedded_interactions: Optional[List[EmbeddedInteraction]] = None
    simulator_spec: Optional[SimulatorSpec] = None
    trigger: Optional[str] = None
    ai_spec: Optional[AITutorSpec] = None
    assessment_spec: Optional[AssessmentSpec] = None


class Lesson(BaseModel):
    """Lesson"""
    lesson_id: str
    title: str
    order: Optional[int] = None
    total_steps: int
    rationale: str
    script: List[LessonStep]
    estimated_minutes: int
    prerequisites: List[str] = []
    learning_objectives: List[str] = []
    complexity_level: str = "standard"  # simple, standard, rich, comprehensive


class LessonOutline(BaseModel):
    """Lesson outline for generation progress"""
    title: str
    index: Optional[int] = None
    recommended_forms: Optional[List[str]] = None
    complexity_level: Optional[str] = None


# ============================================
# Package Schemas
# ============================================

class PackageMetaV2(BaseModel):
    """Package metadata V2"""
    title: str
    description: str
    source_info: str
    total_lessons: int
    estimated_hours: float
    style: str
    created_at: str


class Edge(BaseModel):
    """Edge between lessons"""
    id: str
    from_: str = Field(alias="from")
    to: str
    type: str

    class Config:
        populate_by_name = True


class GlobalAIConfig(BaseModel):
    """Global AI configuration"""
    tutor_persona: str
    fallback_responses: List[str] = []


class CoursePackageV2(BaseModel):
    """Course package V2 format"""
    id: str
    version: str = "2.0.0"
    meta: PackageMetaV2
    lessons: List[Lesson]
    edges: List[Edge]
    global_ai_config: GlobalAIConfig


class PackageListItem(BaseModel):
    """Package list item"""
    id: str
    title: str
    description: str
    style: str
    status: str
    total_nodes: int
    estimated_hours: float
    created_at: str
    updated_at: str


# ============================================
# Generation Schemas
# ============================================

class GenerateRequestV2(BaseModel):
    """V2 generation request"""
    source_material: str = ""
    source_upload_ids: Optional[List[str]] = None
    course_title: str
    processor_id: str
    source_info: str = ""
    # Resume support
    resume_from_lesson: Optional[int] = None
    completed_lessons: Optional[List[Any]] = None
    lessons_outline: Optional[List[Any]] = None
    meta: Optional[Any] = None


# ============================================
# Upload Schemas
# ============================================

class UploadResponse(BaseModel):
    """Upload response"""
    success: bool
    filename: str
    file_type: Optional[str] = None
    char_count: int
    word_count: Optional[int] = None
    reading_time_minutes: Optional[int] = None
    text: str


class UploadFileResponse(BaseModel):
    """Pure upload response (no extraction)"""
    success: bool = True
    upload_id: str
    filename: str
    file_type: Optional[str] = None
    file_size: int
    content_type: Optional[str] = None
    created_at: str
    expires_at: Optional[str] = None


class UploadTaskState(str, Enum):
    """Upload task state"""
    queued = "queued"
    extracting = "extracting"
    succeeded = "succeeded"
    failed = "failed"


class UploadTaskResult(BaseModel):
    """Upload task result payload"""
    success: bool = True
    filename: str
    file_type: Optional[str] = None
    char_count: int
    word_count: Optional[int] = None
    reading_time_minutes: Optional[int] = None
    text: str


class UploadTaskCreateResponse(BaseModel):
    """Upload task creation response"""
    task_id: str
    status: UploadTaskState
    filename: str
    file_size: int
    created_at: str


class UploadTaskStatusResponse(BaseModel):
    """Upload task status response"""
    task_id: str
    status: UploadTaskState
    filename: str
    file_size: int
    created_at: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    current_phase: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    result: Optional[UploadTaskResult] = None


# ============================================
# API Response Schemas
# ============================================

class ProcessorListResponse(BaseModel):
    """Processor list response"""
    processors: List[ProcessorWithConfig]


class PackageListResponse(BaseModel):
    """Package list response"""
    packages: List[PackageListItem]
    total: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
