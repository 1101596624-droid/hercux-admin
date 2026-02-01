"""
Studio Schemas - Pydantic models for Studio API
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime


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
    """Simulator specification"""
    simulator_id: Optional[str] = None
    type: Optional[str] = None
    scenario: Optional[Dict[str, Any]] = None
    interface_spec: Optional[Dict[str, Any]] = None
    evaluation_logic: Optional[Dict[str, Any]] = None
    # 自定义代码模式字段
    mode: Optional[str] = None  # "custom" for custom code mode
    name: Optional[str] = None
    description: Optional[str] = None
    custom_code: Optional[str] = None
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
    source_material: str
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
