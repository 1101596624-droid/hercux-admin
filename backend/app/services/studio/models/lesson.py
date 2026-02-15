# ============================================
# lesson.py - HERCU Studio 课时模型
# 基于 HERCU 课程包标准规范 v2.0
# ============================================

from dataclasses import dataclass, field
from typing import Optional, List
from .content_specs import (
    TextContentSpec,
    DiagramSpec,
    VideoSpec,
    SimulatorSpec,
    AITutorSpec,
    AssessmentSpec,
    EmbeddedInteraction
)


@dataclass
class LessonStep:
    """课时步骤"""
    step_id: str
    type: str  # TeachingFormType
    title: str

    # 根据 type 使用不同的内容规格
    content: Optional[TextContentSpec] = None
    diagram_spec: Optional[DiagramSpec] = None
    video_spec: Optional[VideoSpec] = None
    simulator_spec: Optional[SimulatorSpec] = None
    ai_spec: Optional[AITutorSpec] = None
    assessment_spec: Optional[AssessmentSpec] = None

    # 可选配置
    trigger: str = ""  # required, optional_user_request, auto_after_simulator
    embedded_interactions: List[EmbeddedInteraction] = field(default_factory=list)


@dataclass
class Lesson:
    """课时（v2.0 标准结构）"""
    lesson_id: str
    title: str
    order: int = 0
    total_steps: int = 0
    rationale: str = ""  # 为什么选择这些教学形式
    steps: List[LessonStep] = field(default_factory=list)  # 统一使用steps字段

    # 元数据
    estimated_minutes: int = 30
    prerequisites: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    complexity_level: str = "standard"  # simple, standard, rich, comprehensive
