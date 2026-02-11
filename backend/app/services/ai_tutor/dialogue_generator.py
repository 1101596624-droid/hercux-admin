"""
AI Tutor Dialogue Generator with Learning Integration

Generates high-quality AI tutor dialogues by learning from past examples.
Automatically evaluates quality and saves high-scoring dialogues as templates.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.services.learning.template_service import UnifiedTemplateService
from app.services.learning.quality_scorers import TutorDialogueScorer


class DialogueGenerator:
    """AI Tutor dialogue generator with learning capabilities"""

    def __init__(self, db: Session):
        self.db = db
        self.template_service = UnifiedTemplateService(db)
        self.scorer = TutorDialogueScorer()

    async def enhance_system_prompt(
        self,
        base_prompt: str,
        subject: str,
        topic: str,
        min_quality: float = 85.0,
    ) -> str:
        """
        Enhance system prompt with learning context from high-quality templates

        Args:
            base_prompt: Original system prompt
            subject: Subject area (e.g., "physics", "biomechanics")
            topic: Specific topic (e.g., "projectile_motion", "joint_mechanics")
            min_quality: Minimum quality score for templates (default 85)

        Returns:
            Enhanced system prompt with learning context
        """
        # Retrieve similar high-quality dialogue templates
        templates = await self.template_service.get_similar_templates(
            template_type="tutor_dialogue",
            subject=subject,
            topic=topic,
            min_quality=min_quality,
            limit=3,
        )

        if not templates:
            # No high-quality templates yet, return base prompt
            return base_prompt

        # Analyze patterns across templates
        patterns = self.template_service.analyze_patterns(templates)

        # Format learning context
        learning_context = self.template_service.format_learning_context(
            patterns=patterns,
            templates=templates,
            template_type="tutor_dialogue",
        )

        # Combine base prompt with learning context
        enhanced_prompt = f"""{base_prompt}

{learning_context}

# QUALITY STANDARDS
Aim to achieve or exceed the following quality benchmarks:
- Coherence: {patterns.get('avg_quality_score', 85):.1f}/100
- Ask {patterns['metadata_insights'].get('question_count', 3)} or more guiding questions
- Use proven teaching strategies: {', '.join(patterns['metadata_insights'].get('teaching_strategies', []))}
- Maintain conversational engagement with appropriate tone markers
"""

        return enhanced_prompt

    async def evaluate_and_save_dialogue(
        self,
        dialogue: List[Dict[str, str]],
        subject: str,
        topic: str,
        node_id: int,
        save_threshold: float = 85.0,
    ) -> Dict[str, Any]:
        """
        Evaluate dialogue quality and save as template if it meets the threshold

        Args:
            dialogue: List of message dicts with 'role' and 'content'
            subject: Subject area
            topic: Specific topic
            node_id: Course node ID (for tracking)
            save_threshold: Minimum score to save as template (default 85)

        Returns:
            Dictionary with evaluation results:
            {
                "quality_score": float,
                "score_breakdown": dict,
                "saved_as_template": bool,
                "issues": list,
                "report": str
            }
        """
        # Evaluate dialogue quality
        score = self.scorer.evaluate(dialogue)

        # Record evaluation
        await self.template_service.record_quality_evaluation(
            content_type="tutor_dialogue",
            content_id=f"node_{node_id}",
            quality_score=score.total_score,
            score_breakdown=score.details,
            saved_as_template=(score.total_score >= save_threshold),
        )

        saved_as_template = False

        # Save as template if score is high enough
        if score.total_score >= save_threshold:
            # Extract metadata
            metadata = self.scorer.extract_metadata(dialogue)

            # Prepare content for storage
            content = {
                "dialogue": dialogue,
                "node_id": node_id,
                "turn_count": len(dialogue),
            }

            # Save template
            template = await self.template_service.save_as_template(
                template_type="tutor_dialogue",
                subject=subject,
                topic=topic,
                content=content,
                quality_score=score.total_score,
                score_breakdown={
                    "coherence": score.coherence_score,
                    "guidance": score.guidance_score,
                    "knowledge": score.knowledge_score,
                    "diagnosis": score.diagnosis_score,
                    "teaching": score.teaching_score,
                },
                metadata=metadata,
            )

            saved_as_template = (template is not None)

        return {
            "quality_score": score.total_score,
            "score_breakdown": {
                "coherence": score.coherence_score,
                "guidance": score.guidance_score,
                "knowledge": score.knowledge_score,
                "diagnosis": score.diagnosis_score,
                "teaching": score.teaching_score,
            },
            "saved_as_template": saved_as_template,
            "issues": score.issues,
            "report": score.format_report(),
        }

    async def get_dialogue_insights(
        self,
        subject: str,
        topic: str,
    ) -> Dict[str, Any]:
        """
        Get insights from past high-quality dialogues for a specific topic

        Args:
            subject: Subject area
            topic: Specific topic

        Returns:
            Dictionary containing:
            - template_count: Number of high-quality templates available
            - avg_quality: Average quality score
            - common_patterns: List of common patterns
            - best_practices: List of best practices
        """
        templates = await self.template_service.get_similar_templates(
            template_type="tutor_dialogue",
            subject=subject,
            topic=topic,
            min_quality=85.0,
            limit=10,
        )

        if not templates:
            return {
                "template_count": 0,
                "avg_quality": 0.0,
                "common_patterns": [],
                "best_practices": [],
            }

        patterns = self.template_service.analyze_patterns(templates)

        return {
            "template_count": patterns["template_count"],
            "avg_quality": patterns["avg_quality_score"],
            "common_patterns": patterns["common_structures"],
            "best_practices": patterns["best_practices"],
            "quality_indicators": patterns["quality_indicators"],
        }
