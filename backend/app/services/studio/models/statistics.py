# ============================================
# statistics.py - HERCU Studio 统计模型
# ============================================

from dataclasses import dataclass, field


@dataclass
class FormDistribution:
    """教学形式分布"""
    text_content: int = 0
    illustrated_content: int = 0
    video: int = 0
    simulator: int = 0
    ai_tutor: int = 0
    assessment: int = 0


@dataclass
class ComplexityDistribution:
    """复杂度分布"""
    simple: int = 0
    standard: int = 0
    rich: int = 0
    comprehensive: int = 0


@dataclass
class ResourcesNeeded:
    """所需资源"""
    videos: int = 0
    video_minutes: int = 0
    diagrams: int = 0
    simulators: int = 0


@dataclass
class PackageStatistics:
    """课程包统计"""
    total_lessons: int = 0
    total_steps: int = 0
    form_distribution: FormDistribution = field(default_factory=FormDistribution)
    complexity_distribution: ComplexityDistribution = field(default_factory=ComplexityDistribution)
    resources_needed: ResourcesNeeded = field(default_factory=ResourcesNeeded)
