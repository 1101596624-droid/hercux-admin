"""
Unified Template Service for Agent Learning

Provides core functionality for:
- Retrieving similar high-quality templates
- Analyzing patterns across templates
- Formatting learning context for LLM prompts
- Saving new high-quality content as templates
"""

import json
import hashlib
import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, select
from sentence_transformers import SentenceTransformer
from app.models.models import ContentTemplate, QualityEvaluation, GenerationPattern, PatternApplication
from app.core.constants import QUALITY_BASELINE, TEMPLATE_RETRIEVE_LIMIT_DEFAULT


class UnifiedTemplateService:
    """Service for managing learning templates across all content types"""

    def __init__(self, db: Session):
        self.db = db
        self._embedding_model = None  # Lazy initialization

    @property
    def embedding_model(self):
        """Lazy-load the embedding model"""
        if self._embedding_model is None:
            self._embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        return self._embedding_model

    async def get_similar_templates(
        self,
        template_type: str,
        subject: str,
        topic: str = None,
        min_quality: float = QUALITY_BASELINE,
        limit: int = TEMPLATE_RETRIEVE_LIMIT_DEFAULT,
        difficulty_level: str = None,
    ) -> List[ContentTemplate]:
        """
        Retrieve similar high-quality templates for learning

        Args:
            template_type: Type of content ('simulator', 'tutor_dialogue', 'chapter_content', 'quiz_question')
            subject: Subject area (e.g., 'physics', 'mathematics')
            topic: Optional specific topic for more targeted results
            min_quality: Minimum quality score threshold (default 75)
            limit: Maximum number of templates to return (default 3)
            difficulty_level: Optional difficulty filter for quiz/chapter

        Returns:
            List of ContentTemplate objects sorted by quality score
        """
        stmt = select(ContentTemplate).filter(
            and_(
                ContentTemplate.template_type == template_type,
                ContentTemplate.subject == subject,
                ContentTemplate.quality_score >= min_quality,
            )
        )

        # Add optional filters
        if topic:
            stmt = stmt.filter(ContentTemplate.topic == topic)

        if difficulty_level:
            stmt = stmt.filter(ContentTemplate.difficulty_level == difficulty_level)

        # Order by quality score (highest first) and limit results
        stmt = stmt.order_by(desc(ContentTemplate.quality_score)).limit(limit)
        result = await self.db.execute(stmt)
        templates = result.scalars().all()

        return templates

    def analyze_patterns(self, templates: List[ContentTemplate]) -> Dict[str, Any]:
        """
        Analyze patterns across multiple templates to extract insights

        Args:
            templates: List of ContentTemplate objects

        Returns:
            Dictionary containing extracted patterns and insights:
            {
                "common_structures": [...],
                "quality_indicators": [...],
                "best_practices": [...],
                "avg_quality_score": float,
                "metadata_insights": {...}
            }
        """
        if not templates:
            return {
                "common_structures": [],
                "quality_indicators": [],
                "best_practices": [],
                "avg_quality_score": 0.0,
                "metadata_insights": {},
            }

        # Calculate average quality
        avg_quality = sum(t.quality_score for t in templates) / len(templates)

        # Extract metadata patterns
        all_metadata = []
        for template in templates:
            if template.template_metadata:
                all_metadata.append(template.template_metadata)

        # Aggregate metadata insights
        metadata_insights = self._aggregate_metadata(all_metadata)

        # Extract score breakdown patterns
        quality_indicators = self._extract_quality_indicators(templates)

        return {
            "common_structures": self._extract_common_structures(templates),
            "quality_indicators": quality_indicators,
            "best_practices": self._extract_best_practices(templates),
            "avg_quality_score": avg_quality,
            "metadata_insights": metadata_insights,
            "template_count": len(templates),
        }

    def format_learning_context(
        self,
        patterns: Dict[str, Any],
        templates: List[ContentTemplate],
        template_type: str,
    ) -> str:
        """
        Format learning context as a string to inject into LLM prompts

        Args:
            patterns: Output from analyze_patterns()
            templates: List of reference templates
            template_type: Type of content being generated

        Returns:
            Formatted string to inject into system prompt
        """
        if not templates:
            return ""

        context_parts = []

        # Header
        context_parts.append(f"\n# LEARNING CONTEXT ({template_type.upper()})")
        context_parts.append(
            f"The agent has learned from {patterns['template_count']} high-quality examples "
            f"(avg quality: {patterns['avg_quality_score']:.1f}/100).\n"
        )

        # Quality indicators
        if patterns["quality_indicators"]:
            context_parts.append("## High-Quality Indicators:")
            for indicator in patterns["quality_indicators"]:
                context_parts.append(f"- {indicator}")
            context_parts.append("")

        # Best practices
        if patterns["best_practices"]:
            context_parts.append("## Best Practices from Templates:")
            for practice in patterns["best_practices"]:
                context_parts.append(f"- {practice}")
            context_parts.append("")

        # Common structures
        if patterns["common_structures"]:
            context_parts.append("## Common Structural Patterns:")
            for structure in patterns["common_structures"]:
                context_parts.append(f"- {structure}")
            context_parts.append("")

        # Metadata insights
        if patterns["metadata_insights"]:
            context_parts.append("## Pattern Insights:")
            for key, value in patterns["metadata_insights"].items():
                if isinstance(value, list):
                    context_parts.append(f"- {key}: {', '.join(str(v) for v in value[:5])}")
                else:
                    context_parts.append(f"- {key}: {value}")
            context_parts.append("")

        context_parts.append(
            "Use these insights to generate content that matches or exceeds the quality "
            "of the reference templates.\n"
        )

        return "\n".join(context_parts)

    async def save_as_template(
        self,
        template_type: str,
        subject: str,
        topic: str,
        content: Dict[str, Any],
        quality_score: float,
        score_breakdown: Dict[str, float],
        metadata: Dict[str, Any],
        difficulty_level: str = None,
    ) -> Optional[ContentTemplate]:
        """
        Save high-quality content as a template for future learning

        Args:
            template_type: Type of content
            subject: Subject area
            topic: Specific topic
            content: Content data (will be JSON serialized)
            quality_score: Overall quality score
            score_breakdown: Detailed scoring
            metadata: Extracted patterns and insights
            difficulty_level: Optional difficulty level

        Returns:
            Created ContentTemplate or None if duplicate
        """
        # Serialize content to JSON
        content_json = json.dumps(content, ensure_ascii=False, indent=2)

        # Calculate content hash for deduplication
        content_hash = hashlib.sha256(content_json.encode()).hexdigest()

        # Check for duplicate
        stmt = select(ContentTemplate).filter(
            and_(
                ContentTemplate.template_type == template_type,
                ContentTemplate.content_hash == content_hash,
            )
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # Update usage count
            existing.usage_count += 1
            await self.db.commit()
            return None

        # Create new template
        template = ContentTemplate(
            template_type=template_type,
            subject=subject,
            topic=topic,
            content=content_json,
            quality_score=quality_score,
            score_breakdown=score_breakdown,
            template_metadata=metadata,
            difficulty_level=difficulty_level,
            content_hash=content_hash,
            usage_count=0,
        )

        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)

        return template

    async def record_quality_evaluation(
        self,
        content_type: str,
        content_id: str,
        quality_score: float,
        score_breakdown: Dict[str, float],
        saved_as_template: bool = False,
    ) -> QualityEvaluation:
        """
        Record a quality evaluation for monitoring and analytics

        Args:
            content_type: Type of content evaluated
            content_id: Unique identifier for the content
            quality_score: Overall quality score
            score_breakdown: Detailed scoring
            saved_as_template: Whether this was saved as a template

        Returns:
            Created QualityEvaluation record
        """
        evaluation = QualityEvaluation(
            content_type=content_type,
            content_id=content_id,
            quality_score=quality_score,
            score_breakdown=score_breakdown,
            saved_as_template=1 if saved_as_template else 0,
        )

        self.db.add(evaluation)
        await self.db.commit()
        await self.db.refresh(evaluation)

        return evaluation

    async def get_similar_patterns_by_vector(
        self,
        query_text: str,
        step_type: str,
        subject: str,
        pattern_type: str = None,
        min_confidence: float = 0.7,
        limit: int = 5,
    ) -> List[GenerationPattern]:
        """
        Retrieve similar patterns using vector similarity search (cosine distance)

        Args:
            query_text: Text to generate embedding for similarity search
            step_type: Generation step type ('text_content', 'illustrated_content', 'assessment', 'ai_tutor')
            subject: Subject area filter
            pattern_type: Optional pattern type filter ('failure_recovery', 'optimization', 'best_practice')
            min_confidence: Minimum confidence threshold (0-1)
            limit: Maximum number of patterns to return

        Returns:
            List of GenerationPattern objects sorted by similarity
        """
        # Generate embedding for query
        query_embedding = self._generate_embedding(query_text)

        # Build base query with filters
        stmt = select(GenerationPattern).filter(
            and_(
                GenerationPattern.step_type == step_type,
                GenerationPattern.subject == subject,
                GenerationPattern.confidence >= min_confidence,
            )
        )

        # Add optional pattern type filter
        if pattern_type:
            stmt = stmt.filter(GenerationPattern.pattern_type == pattern_type)

        # Get all matching patterns (we'll sort by similarity in Python)
        result = await self.db.execute(stmt)
        patterns = result.scalars().all()

        if not patterns:
            return []

        # Calculate cosine similarity for each pattern
        pattern_similarities = []
        for pattern in patterns:
            if pattern.embedding is not None:
                # Calculate cosine distance (lower is more similar)
                # PostgreSQL pgvector uses <=> for cosine distance
                similarity = 1 - self._cosine_distance(query_embedding, pattern.embedding)
                pattern_similarities.append((pattern, similarity))

        # Sort by similarity (highest first) and limit
        pattern_similarities.sort(key=lambda x: x[1], reverse=True)
        top_patterns = [p for p, _ in pattern_similarities[:limit]]

        return top_patterns

    async def record_pattern_application(
        self,
        pattern_id: int,
        step_type: str,
        subject: str,
        topic: str,
        original_input: Dict[str, Any],
        applied_strategy: str,
        result_quality: float = None,
        success: bool = True,
    ) -> PatternApplication:
        """
        Record a pattern application and update pattern statistics

        Args:
            pattern_id: ID of the pattern that was applied
            step_type: Generation step type
            subject: Subject area
            topic: Specific topic
            original_input: Original generation request data
            applied_strategy: Strategy text that was applied
            result_quality: Quality score of the result (if evaluated)
            success: Whether the application was successful

        Returns:
            Created PatternApplication record
        """
        # Create application record
        application = PatternApplication(
            pattern_id=pattern_id,
            step_type=step_type,
            subject=subject,
            topic=topic,
            original_input=original_input,
            applied_strategy=applied_strategy,
            result_quality=result_quality,
            success=success,
        )

        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)

        # Update pattern statistics
        await self._update_pattern_stats(pattern_id, success)

        return application

    async def _update_pattern_stats(self, pattern_id: int, success: bool):
        """
        Update pattern statistics and confidence score

        Args:
            pattern_id: ID of the pattern to update
            success: Whether the latest application was successful
        """
        stmt = select(GenerationPattern).filter(GenerationPattern.id == pattern_id)
        result = await self.db.execute(stmt)
        pattern = result.scalar_one_or_none()

        if not pattern:
            return

        # Update usage count
        pattern.use_count += 1

        # Update success count if successful
        if success:
            pattern.success_count += 1

        # Recalculate confidence using Bayesian update
        # Formula: confidence = (success_count + prior) / (use_count + prior * 2)
        # prior acts as smoothing factor to prevent overconfidence from small samples
        prior = 2.0
        pattern.confidence = (pattern.success_count + prior) / (pattern.use_count + prior * 2)

        await self.db.commit()

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using sentence-transformers

        Args:
            text: Text to embed

        Returns:
            384-dimensional embedding vector as list
        """
        if not text:
            # Return zero vector for empty text
            return [0.0] * 384

        # Generate embedding using sentence-transformers
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)

        # Convert to list for JSON serialization
        return embedding.tolist()

    def _cosine_distance(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine distance between two vectors

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine distance (0 = identical, 2 = opposite)
        """
        # Convert to numpy arrays
        v1 = np.array(vec1)
        v2 = np.array(vec2)

        # Calculate cosine similarity
        dot_product = np.dot(v1, v2)
        norm_product = np.linalg.norm(v1) * np.linalg.norm(v2)

        if norm_product == 0:
            return 1.0  # Maximum distance if either vector is zero

        cosine_similarity = dot_product / norm_product

        # Convert to cosine distance (1 - similarity)
        return 1.0 - cosine_similarity

    # === Private helper methods ===

    def _aggregate_metadata(self, metadata_list: List[Dict]) -> Dict[str, Any]:
        """Aggregate metadata from multiple templates"""
        if not metadata_list:
            return {}

        aggregated = {}

        # Collect all keys
        all_keys = set()
        for meta in metadata_list:
            all_keys.update(meta.keys())

        # Aggregate values for each key
        for key in all_keys:
            values = [meta.get(key) for meta in metadata_list if key in meta]

            # Handle lists (collect unique values)
            if values and isinstance(values[0], list):
                unique_values = set()
                for v in values:
                    if isinstance(v, list):
                        unique_values.update(v)
                aggregated[key] = list(unique_values)

            # Handle strings (collect unique values)
            elif values and isinstance(values[0], str):
                aggregated[key] = list(set(values))

            # Handle numbers (calculate average)
            elif values and isinstance(values[0], (int, float)):
                aggregated[key] = sum(values) / len(values)

        return aggregated

    def _extract_quality_indicators(self, templates: List[ContentTemplate]) -> List[str]:
        """Extract quality indicators from high-scoring templates"""
        indicators = []

        if not templates:
            return indicators

        # Analyze score breakdowns
        all_breakdowns = [t.score_breakdown for t in templates if t.score_breakdown]

        if all_breakdowns:
            # Find dimensions with consistently high scores
            dimension_scores = {}
            for breakdown in all_breakdowns:
                for dimension, score in breakdown.items():
                    if dimension not in dimension_scores:
                        dimension_scores[dimension] = []
                    dimension_scores[dimension].append(score)

            # Identify high-performing dimensions
            for dimension, scores in dimension_scores.items():
                avg_score = sum(scores) / len(scores)
                if avg_score >= 80:
                    indicators.append(f"Strong {dimension.replace('_', ' ')} (avg: {avg_score:.1f})")

        return indicators

    def _extract_common_structures(self, templates: List[ContentTemplate]) -> List[str]:
        """Extract common structural patterns"""
        structures = []

        # This is template-type specific
        # For now, return generic insights based on metadata
        if templates and templates[0].template_metadata:
            meta = templates[0].template_metadata

            # Look for structural keys in metadata
            structure_keys = [
                "structure_insights",
                "common_pattern",
                "organization",
                "format",
            ]

            for key in structure_keys:
                if key in meta:
                    structures.append(str(meta[key]))

        return structures

    def _extract_best_practices(self, templates: List[ContentTemplate]) -> List[str]:
        """Extract best practices from templates"""
        practices = []

        if not templates:
            return practices

        # Look for best practices in metadata
        for template in templates:
            if template.template_metadata:
                # Check for explicit best practices
                if "best_practices" in template.template_metadata:
                    bp = template.template_metadata["best_practices"]
                    if isinstance(bp, list):
                        practices.extend(bp)
                    elif isinstance(bp, str):
                        practices.append(bp)

                # Extract from other metadata fields
                if "tips" in template.template_metadata:
                    tips = template.template_metadata["tips"]
                    if isinstance(tips, list):
                        practices.extend(tips)

        # Remove duplicates while preserving order
        seen = set()
        unique_practices = []
        for p in practices:
            if p not in seen:
                seen.add(p)
                unique_practices.append(p)

        return unique_practices[:10]  # Return top 10
