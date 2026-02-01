# ============================================
# package.py - HERCU Studio 课程包模型
# 基于 HERCU 课程包标准规范 v2.0
# ============================================

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from .lesson import Lesson
from .statistics import PackageStatistics


@dataclass
class PackageMeta:
    """课程包元数据"""
    title: str
    description: str
    source_info: str = ""
    total_lessons: int = 0
    estimated_hours: float = 0.0
    style: str = "intelligent"  # 使用的风格/处理器
    created_at: str = ""
    statistics: Optional[PackageStatistics] = None


@dataclass
class PackageEdge:
    """课时依赖边"""
    id: str
    from_lesson: str  # 使用 from_lesson 避免 Python 关键字冲突
    to_lesson: str
    type: str = "prerequisite"


@dataclass
class GlobalAIConfig:
    """全局 AI 配置"""
    tutor_persona: str = "专业友好的AI导师"
    fallback_responses: List[str] = field(default_factory=lambda: [
        "让我换个方式解释...",
        "我们再看一遍这个概念..."
    ])


@dataclass
class CoursePackage:
    """完整课程包（v2.0 标准）"""
    id: str
    version: str = "2.0.0"
    meta: PackageMeta = field(default_factory=PackageMeta)
    lessons: List[Lesson] = field(default_factory=list)
    edges: List[PackageEdge] = field(default_factory=list)
    global_ai_config: GlobalAIConfig = field(default_factory=GlobalAIConfig)
