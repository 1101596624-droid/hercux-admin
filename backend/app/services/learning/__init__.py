"""
Unified Learning System for Agent Quality Improvement

This module provides a framework for the AI agent to learn from high-quality
content templates across 4 core features:
- HTML Simulator generation
- AI Tutor dialogues
- Course chapter content
- Quiz questions

The system enables continuous quality improvement through:
1. Template storage (high-quality examples)
2. Pattern analysis (extracting insights)
3. Learning context injection (guiding future generations)
4. Quality feedback loops (scoring and filtering)
"""

from .template_service import UnifiedTemplateService
from .quality_scorers import (
    BaseQualityScorer,
    BaseQualityScore,
    TutorDialogueQualityScore,
    TutorDialogueScorer,
    ChapterQualityScore,
    ChapterScorer,
    QuizQualityScore,
    QuizScorer,
)

__all__ = [
    "UnifiedTemplateService",
    "BaseQualityScorer",
    "BaseQualityScore",
    "TutorDialogueQualityScore",
    "TutorDialogueScorer",
    "ChapterQualityScore",
    "ChapterScorer",
    "QuizQualityScore",
    "QuizScorer",
]
