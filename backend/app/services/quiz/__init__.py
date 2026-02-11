"""
Quiz Generation Service with Learning Integration

This module provides quiz generation capabilities enhanced with
the unified learning framework. Quizzes learn from high-quality
examples to continuously improve question quality.
"""

from .quiz_generator import EnhancedQuizGenerator
from .service import QuizService

__all__ = ['EnhancedQuizGenerator', 'QuizService']
