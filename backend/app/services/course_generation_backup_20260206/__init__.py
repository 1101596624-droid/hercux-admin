# Course Generation Service with Supervisor-Generator Architecture
from .supervisor import CourseSupervisor
from .generator import ChapterGenerator, GeneratorPromptBuilder
from .models import (
    GenerationState, CourseOutline, ChapterOutline, ChapterResult,
    ReviewResult, ReviewStatus, ChapterType, ChapterQualityStandards,
    SimulatorQualityStandards, SimulatorSpec, ChapterStep
)
from .service import CourseGenerationService

__all__ = [
    # Main service
    'CourseGenerationService',

    # Core components
    'CourseSupervisor',
    'ChapterGenerator',
    'GeneratorPromptBuilder',

    # Models
    'GenerationState',
    'CourseOutline',
    'ChapterOutline',
    'ChapterResult',
    'ReviewResult',
    'ReviewStatus',
    'ChapterType',
    'ChapterQualityStandards',
    'SimulatorQualityStandards',
    'SimulatorSpec',
    'ChapterStep'
]
