# Course Generation Service with Supervisor-Generator Architecture
from .supervisor import CourseSupervisor
from .generator import ChapterGenerator, GeneratorPromptBuilder
from .models import (
    GenerationState, CourseOutline, ChapterOutline, ChapterResult,
    ReviewResult, ReviewStatus, ChapterType, ChapterQualityStandards,
    ChapterStep, CodeSyntaxError, SyntaxErrorType,
    HTMLSimulatorSpec, HTMLSimulatorQualityStandards, HTMLSimulatorQualityScore
)
from .service import CourseGenerationService
from .subject_classifier import SubjectClassifier
from .template_manager import TemplateManager

__all__ = [
    # Main service
    'CourseGenerationService',

    # Core components
    'CourseSupervisor',
    'ChapterGenerator',
    'GeneratorPromptBuilder',
    'SubjectClassifier',
    'TemplateManager',

    # Models
    'GenerationState',
    'CourseOutline',
    'ChapterOutline',
    'ChapterResult',
    'ReviewResult',
    'ReviewStatus',
    'ChapterType',
    'ChapterQualityStandards',
    'ChapterStep',

    # Error handling
    'CodeSyntaxError',
    'SyntaxErrorType',

    # HTML Simulator (new format only)
    'HTMLSimulatorSpec',
    'HTMLSimulatorQualityStandards',
    'HTMLSimulatorQualityScore'
]
