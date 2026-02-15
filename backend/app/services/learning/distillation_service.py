"""
Distillation Service for Agent Learning

Provides experience distillation functionality:
- Automatic pattern extraction from successful/failed generations
- Claude API integration for pattern analysis
- Pattern persistence to database
- Success/failure pattern detection
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, select
from anthropic import Anthropic
from sentence_transformers import SentenceTransformer

from app.models.models import (
    GenerationPattern,
    PatternApplication,
    QualityEvaluation,
    ContentTemplate,
)


class DistillationService:
    """Service for distilling experience patterns from content generation history"""

    def __init__(self, db: Session, anthropic_api_key: str):
        self.db = db
        self.anthropic_client = Anthropic(api_key=anthropic_api_key)
        self._embedding_model = None

    @property
    def embedding_model(self):
        """Lazy-load the embedding model"""
        if self._embedding_model is None:
            self._embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        return self._embedding_model

    async def distill_patterns(
        self,
        step_type: str,
        subject: str,
        lookback_days: int = 7,
        min_quality_threshold: float = 75.0,
        max_quality_threshold: float = 60.0,
    ) -> Dict[str, List[GenerationPattern]]:
        """
        Automatically distill strategy patterns from recent generation history

        Args:
            step_type: Generation step type ('text_content', 'illustrated_content', 'assessment', 'ai_tutor')
            subject: Subject area to analyze
            lookback_days: Number of days to look back in history
            min_quality_threshold: Quality threshold for success patterns (>= this is success)
            max_quality_threshold: Quality threshold for failure patterns (<= this is failure)

        Returns:
            Dictionary with 'success_patterns' and 'anti_patterns' lists
        """
        # Get recent trajectories
        recent_trajectories = await self._get_recent_trajectories(
            step_type, subject, lookback_days
        )

        if not recent_trajectories:
            return {"success_patterns": [], "anti_patterns": []}

        # Separate success and failure cases
        success_cases = [
            t for t in recent_trajectories if t["quality_score"] >= min_quality_threshold
        ]
        failure_cases = [
            t for t in recent_trajectories if t["quality_score"] <= max_quality_threshold
        ]

        # Extract patterns using Claude
        success_patterns = []
        if success_cases:
            success_patterns = await self._extract_success_patterns(
                step_type, subject, success_cases
            )

        anti_patterns = []
        if failure_cases:
            anti_patterns = await self._extract_anti_patterns(
                step_type, subject, failure_cases
            )

        # Save patterns to database
        saved_success = []
        for pattern_data in success_patterns:
            saved = await self._save_pattern(pattern_data, "best_practice")
            if saved:
                saved_success.append(saved)

        saved_anti = []
        for pattern_data in anti_patterns:
            saved = await self._save_pattern(pattern_data, "failure_recovery")
            if saved:
                saved_anti.append(saved)

        return {
            "success_patterns": saved_success,
            "anti_patterns": saved_anti,
        }

    async def _extract_success_patterns(
        self,
        step_type: str,
        subject: str,
        success_cases: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Extract success patterns using Claude API

        Args:
            step_type: Generation step type
            subject: Subject area
            success_cases: List of successful generation cases

        Returns:
            List of extracted pattern data dictionaries
        """
        # Prepare context for Claude
        context = self._prepare_distillation_context(success_cases, is_success=True)

        # Call Claude to analyze patterns
        prompt = f"""Analyze the following successful content generation cases for {step_type} in {subject}.

Extract common success patterns that can be reused in future generations.

{context}

For each pattern you identify, provide:
1. pattern_name: A concise, descriptive name
2. pattern_description: Detailed description of what makes this pattern successful
3. trigger_conditions: JSON object describing when this pattern should be applied (e.g., {{"difficulty": "advanced", "topic_type": "theoretical"}})
4. solution_strategy: Specific strategy to apply (be concrete and actionable)

Respond in JSON format as an array of patterns:
[
  {{
    "pattern_name": "Clear Progressive Structure",
    "pattern_description": "Content follows a clear progression from simple to complex...",
    "trigger_conditions": {{"complexity": "high", "audience": "beginner"}},
    "solution_strategy": "Start with a concrete example, then gradually introduce abstract concepts..."
  }}
]

Extract 2-4 most impactful patterns. Focus on actionable strategies, not generic advice."""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse response
            response_text = response.content[0].text.strip()

            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                json_start = response_text.index("```json") + 7
                json_end = response_text.rindex("```")
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.index("```") + 3
                json_end = response_text.rindex("```")
                response_text = response_text[json_start:json_end].strip()

            patterns = json.loads(response_text)

            # Add metadata to each pattern
            for pattern in patterns:
                pattern["step_type"] = step_type
                pattern["subject"] = subject
                pattern["source_count"] = len(success_cases)

            return patterns

        except Exception as e:
            print(f"Error extracting success patterns: {e}")
            return []

    async def _extract_anti_patterns(
        self,
        step_type: str,
        subject: str,
        failure_cases: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Extract failure patterns (anti-patterns) using Claude API

        Args:
            step_type: Generation step type
            subject: Subject area
            failure_cases: List of failed generation cases

        Returns:
            List of extracted anti-pattern data dictionaries
        """
        # Prepare context for Claude
        context = self._prepare_distillation_context(failure_cases, is_success=False)

        # Call Claude to analyze anti-patterns
        prompt = f"""Analyze the following failed or low-quality content generation cases for {step_type} in {subject}.

Extract common failure patterns (anti-patterns) and their solutions.

{context}

For each anti-pattern you identify, provide:
1. pattern_name: A concise name describing the problem
2. pattern_description: Detailed description of why this pattern fails
3. trigger_conditions: JSON object describing when this problem occurs (e.g., {{"error_type": "incomplete_content", "quality_dimension": "clarity"}})
4. solution_strategy: Specific recovery strategy to avoid or fix this problem

Respond in JSON format as an array of patterns:
[
  {{
    "pattern_name": "Overly Abstract Explanation",
    "pattern_description": "Content is too abstract without concrete examples, causing low comprehension...",
    "trigger_conditions": {{"clarity_score": "<70", "topic_complexity": "high"}},
    "solution_strategy": "Add 2-3 concrete examples before introducing abstract concepts. Use analogies..."
  }}
]

Extract 2-4 most critical anti-patterns. Focus on specific, actionable recovery strategies."""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse response
            response_text = response.content[0].text.strip()

            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                json_start = response_text.index("```json") + 7
                json_end = response_text.rindex("```")
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.index("```") + 3
                json_end = response_text.rindex("```")
                response_text = response_text[json_start:json_end].strip()

            patterns = json.loads(response_text)

            # Add metadata to each pattern
            for pattern in patterns:
                pattern["step_type"] = step_type
                pattern["subject"] = subject
                pattern["source_count"] = len(failure_cases)

            return patterns

        except Exception as e:
            print(f"Error extracting anti-patterns: {e}")
            return []

    async def _get_recent_trajectories(
        self,
        step_type: str,
        subject: str,
        lookback_days: int,
    ) -> List[Dict[str, Any]]:
        """
        Get recent generation trajectories for pattern extraction

        Args:
            step_type: Generation step type
            subject: Subject area
            lookback_days: Number of days to look back

        Returns:
            List of trajectory dictionaries with quality scores and content
        """
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)

        # Query quality evaluations
        stmt = (
            select(QualityEvaluation)
            .filter(
                and_(
                    QualityEvaluation.content_type == step_type,
                    QualityEvaluation.evaluated_at >= cutoff_date,
                )
            )
            .order_by(desc(QualityEvaluation.evaluated_at))
            .limit(100)  # Limit to recent 100 evaluations
        )
        result = await self.db.execute(stmt)
        evaluations = result.scalars().all()

        # Get corresponding templates for high-quality content
        trajectories = []
        for eval_record in evaluations:
            # Try to find corresponding template
            template_stmt = (
                select(ContentTemplate)
                .filter(
                    and_(
                        ContentTemplate.template_type == step_type,
                        ContentTemplate.subject == subject,
                    )
                )
                .order_by(desc(ContentTemplate.id))
            )
            template_result = await self.db.execute(template_stmt)
            template = template_result.scalar_one_or_none()

            trajectory = {
                "content_id": eval_record.content_id,
                "quality_score": eval_record.quality_score,
                "score_breakdown": eval_record.score_breakdown,
                "evaluated_at": eval_record.evaluated_at,
            }

            # Add template data if available
            if template:
                trajectory["content"] = json.loads(template.content)
                trajectory["metadata"] = template.template_metadata

            trajectories.append(trajectory)

        return trajectories

    async def _save_pattern(
        self,
        pattern_data: Dict[str, Any],
        pattern_type: str,
    ) -> Optional[GenerationPattern]:
        """
        Save extracted pattern to database

        Args:
            pattern_data: Pattern data from Claude extraction
            pattern_type: Type of pattern ('best_practice', 'failure_recovery', 'optimization')

        Returns:
            Created GenerationPattern or None if duplicate
        """
        # Generate embedding for pattern description
        embedding_text = f"{pattern_data['pattern_name']} {pattern_data['pattern_description']}"
        embedding = self.embedding_model.encode(embedding_text, convert_to_numpy=True).tolist()

        # Check for duplicate patterns using name similarity
        stmt = select(GenerationPattern).filter(
            and_(
                GenerationPattern.pattern_type == pattern_type,
                GenerationPattern.step_type == pattern_data["step_type"],
                GenerationPattern.subject == pattern_data["subject"],
                GenerationPattern.pattern_name == pattern_data["pattern_name"],
            )
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing pattern
            existing.pattern_description = pattern_data["pattern_description"]
            existing.trigger_conditions = pattern_data["trigger_conditions"]
            existing.solution_strategy = pattern_data["solution_strategy"]
            existing.embedding = embedding
            existing.created_from_count += pattern_data.get("source_count", 1)
            await self.db.commit()
            return None

        # Create new pattern
        pattern = GenerationPattern(
            pattern_type=pattern_type,
            step_type=pattern_data["step_type"],
            subject=pattern_data["subject"],
            pattern_name=pattern_data["pattern_name"],
            pattern_description=pattern_data["pattern_description"],
            trigger_conditions=pattern_data["trigger_conditions"],
            solution_strategy=pattern_data["solution_strategy"],
            confidence=0.8,  # Initial confidence
            use_count=0,
            success_count=0,
            embedding=embedding,
            source_templates=[],
            created_from_count=pattern_data.get("source_count", 1),
        )

        self.db.add(pattern)
        await self.db.commit()
        await self.db.refresh(pattern)

        return pattern

    def _prepare_distillation_context(
        self,
        cases: List[Dict[str, Any]],
        is_success: bool,
    ) -> str:
        """
        Prepare context string for Claude pattern extraction

        Args:
            cases: List of generation cases
            is_success: Whether these are success or failure cases

        Returns:
            Formatted context string
        """
        context_parts = []
        case_type = "Success" if is_success else "Failure"

        for i, case in enumerate(cases[:10], 1):  # Limit to 10 cases for context length
            context_parts.append(f"\n## {case_type} Case {i}")
            context_parts.append(f"Quality Score: {case['quality_score']:.1f}/100")

            if case.get("score_breakdown"):
                context_parts.append("Score Breakdown:")
                for dimension, score in case["score_breakdown"].items():
                    context_parts.append(f"  - {dimension}: {score:.1f}")

            if case.get("metadata"):
                context_parts.append(f"Metadata: {json.dumps(case['metadata'], indent=2)}")

            # Include content sample if available (truncated)
            if case.get("content"):
                content_str = json.dumps(case["content"], ensure_ascii=False)
                if len(content_str) > 500:
                    content_str = content_str[:500] + "..."
                context_parts.append(f"Content Sample: {content_str}")

        return "\n".join(context_parts)
