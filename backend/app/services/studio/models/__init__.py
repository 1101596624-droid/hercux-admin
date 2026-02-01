# ============================================
# __init__.py - HERCU Studio 模型包导出
# ============================================

# 导出所有枚举
from .enums import (
    TeachingFormType,
    ComplexityLevel,
    DiagramType,
    AssessmentType
)

# 导出分析模型
from .analysis import ContentAnalysis

# 导出内容规格
from .content_specs import (
    TextContentSpec,
    DiagramAnnotation,
    DiagramSpec,
    IllustratedContentSpec,
    VideoScene,
    VideoScript,
    EmbeddedInteraction,
    VideoSpec,
    SimulatorInput,
    SimulatorOutput,
    EvaluationCriterion,
    SimulatorSpec,
    ConversationGoal,
    AITutorSpec,
    AssessmentQuestion,
    AssessmentRubric,
    AssessmentSpec
)

# 导出课时模型
from .lesson import (
    LessonStep,
    Lesson
)

# 导出统计模型
from .statistics import (
    FormDistribution,
    ComplexityDistribution,
    ResourcesNeeded,
    PackageStatistics
)

# 导出课程包模型
from .package import (
    PackageMeta,
    CoursePackage
)

# 导出转换工具
from .converters import (
    convert_old_node_to_lesson,
    calculate_statistics
)

__all__ = [
    # Enums
    "TeachingFormType",
    "ComplexityLevel",
    "DiagramType",
    "AssessmentType",
    # Analysis
    "ContentAnalysis",
    # Content Specs
    "TextContentSpec",
    "DiagramAnnotation",
    "DiagramSpec",
    "IllustratedContentSpec",
    "VideoScene",
    "VideoScript",
    "EmbeddedInteraction",
    "VideoSpec",
    "SimulatorInput",
    "SimulatorOutput",
    "EvaluationCriterion",
    "SimulatorSpec",
    "ConversationGoal",
    "AITutorSpec",
    "AssessmentQuestion",
    "AssessmentRubric",
    "AssessmentSpec",
    # Lesson
    "LessonStep",
    "Lesson",
    # Statistics
    "FormDistribution",
    "ComplexityDistribution",
    "ResourcesNeeded",
    "PackageStatistics",
    # Package
    "PackageMeta",
    "CoursePackage",
    # Converters
    "convert_old_node_to_lesson",
    "calculate_statistics",
]
