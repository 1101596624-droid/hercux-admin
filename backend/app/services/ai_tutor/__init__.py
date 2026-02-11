"""
AI Tutor Service Package

Provides AI tutor functionality with learning integration.
"""

from app.services.ai_tutor.service import AITutorService
from app.services.ai_tutor.dialogue_generator import DialogueGenerator

__all__ = ["AITutorService", "DialogueGenerator"]
