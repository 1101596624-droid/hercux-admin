"""
Template Learning Service for HTML Simulator Generation (2026-02-11)

Provides template retrieval and pattern analysis capabilities for the AI agent
to learn from high-quality HTML simulator examples.

**Dynamic Quality Standards (2026-02-11)**:
- Initial phase (<10 templates): 74 point pass threshold (lenient for rapid accumulation)
- Growth phase (10-50 templates): Dynamic threshold based on template library average
- Mature phase (>50 templates): Strict standards (85-90 point threshold)
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from app.models.models import SimulatorTemplate
import json
import re
import statistics


class TemplateService:
    """Service for retrieving and analyzing simulator templates for agent learning"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_similar_templates(
        self,
        subject: str,
        topic: Optional[str] = None,
        min_quality_score: float = 75.0,
        limit: int = 2
    ) -> List[SimulatorTemplate]:
        """
        Retrieve similar high-quality templates for learning.

        Args:
            subject: Subject area (e.g., "physics", "mathematics")
            topic: Optional specific topic for more targeted results
            min_quality_score: Minimum quality threshold (default 75)
            limit: Maximum number of templates to return (default 2 to avoid prompt bloat)

        Returns:
            List of SimulatorTemplate objects ordered by quality score descending
        """
        query = select(SimulatorTemplate).where(
            and_(
                SimulatorTemplate.subject == subject,
                SimulatorTemplate.quality_score >= min_quality_score
            )
        ).order_by(desc(SimulatorTemplate.quality_score)).limit(limit)

        if topic:
            # If topic specified, try to find exact or similar topic matches
            query = query.where(SimulatorTemplate.topic.ilike(f"%{topic}%"))

        result = await self.db.execute(query)
        templates = result.scalars().all()

        # If no topic-specific templates found and topic was specified, retry without topic filter
        if not templates and topic:
            query = select(SimulatorTemplate).where(
                and_(
                    SimulatorTemplate.subject == subject,
                    SimulatorTemplate.quality_score >= min_quality_score
                )
            ).order_by(desc(SimulatorTemplate.quality_score)).limit(limit)
            result = await self.db.execute(query)
            templates = result.scalars().all()

        return list(templates)

    async def analyze_template_patterns(
        self,
        templates: List[SimulatorTemplate]
    ) -> Dict[str, Any]:
        """
        Analyze templates to extract common patterns and best practices.

        Args:
            templates: List of SimulatorTemplate objects

        Returns:
            Dictionary containing:
            - common_apis: Most frequently used Canvas 2D APIs
            - color_schemes: Common color palettes
            - animation_patterns: Animation techniques
            - structure_insights: Code organization patterns
            - interaction_types: User interaction patterns
        """
        if not templates:
            return self._get_default_patterns()

        all_common_apis = []
        all_colors = []
        all_animation_patterns = []
        all_interaction_types = []
        structure_insights = []

        for template in templates:
            metadata = template.metadata or {}

            # Collect common APIs
            if "common_apis" in metadata:
                all_common_apis.extend(metadata["common_apis"])

            # Collect color schemes
            if "color_scheme" in metadata:
                all_colors.extend(metadata["color_scheme"])

            # Collect animation patterns
            if "animation_patterns" in metadata:
                all_animation_patterns.extend(metadata["animation_patterns"])

            # Collect interaction types
            if "interaction_types" in metadata:
                all_interaction_types.extend(metadata["interaction_types"])

            # Collect structure insights
            if "structure_insights" in metadata:
                structure_insights.append(metadata["structure_insights"])

        # Extract most common patterns
        common_apis = self._extract_common_apis(templates)
        color_schemes = self._extract_color_schemes(all_colors)

        return {
            "common_apis": common_apis[:15],  # Top 15 most used APIs
            "color_schemes": color_schemes[:8],  # Top 8 colors
            "animation_patterns": list(set(all_animation_patterns))[:5],
            "interaction_types": list(set(all_interaction_types))[:5],
            "structure_insights": structure_insights[:2],  # Top 2 insights
            "avg_line_count": sum(t.line_count for t in templates) // len(templates) if templates else 0,
            "avg_quality_score": sum(t.quality_score for t in templates) / len(templates) if templates else 75.0
        }

    def _extract_common_apis(self, templates: List[SimulatorTemplate]) -> List[str]:
        """Extract most frequently used Canvas 2D APIs from template code"""
        api_counts = {}
        canvas_apis = [
            "fillRect", "strokeRect", "clearRect", "fillText", "strokeText",
            "arc", "beginPath", "closePath", "moveTo", "lineTo",
            "stroke", "fill", "save", "restore", "translate",
            "rotate", "scale", "setTransform", "drawImage", "createLinearGradient",
            "createRadialGradient", "rect", "quadraticCurveTo", "bezierCurveTo"
        ]

        for template in templates:
            code = template.code
            for api in canvas_apis:
                # Count occurrences of each API
                count = len(re.findall(rf'\b{api}\b', code))
                if count > 0:
                    api_counts[api] = api_counts.get(api, 0) + count

        # Sort by frequency and return top APIs
        sorted_apis = sorted(api_counts.items(), key=lambda x: x[1], reverse=True)
        return [api for api, _ in sorted_apis]

    def _extract_color_schemes(self, all_colors: List[str]) -> List[str]:
        """Extract most common color values"""
        color_counts = {}
        for color in all_colors:
            color_counts[color] = color_counts.get(color, 0) + 1

        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
        return [color for color, _ in sorted_colors]

    def _get_default_patterns(self) -> Dict[str, Any]:
        """Return default patterns when no templates are available"""
        return {
            "common_apis": [
                "fillRect", "arc", "beginPath", "stroke", "fill",
                "clearRect", "fillText", "moveTo", "lineTo", "save", "restore"
            ],
            "color_schemes": [
                "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DFE6E9"
            ],
            "animation_patterns": ["requestAnimationFrame", "physics_update"],
            "interaction_types": ["mouse_click", "slider_control"],
            "structure_insights": ["Use clear state management", "Separate setup and update logic"],
            "avg_line_count": 400,
            "avg_quality_score": 75.0
        }

    def format_learning_context(
        self,
        patterns: Dict[str, Any],
        templates: List[SimulatorTemplate]
    ) -> str:
        """
        Format template analysis into a concise learning context string for the AI prompt.

        Args:
            patterns: Pattern analysis from analyze_template_patterns()
            templates: Original template objects

        Returns:
            Formatted string with key insights (NOT full code to avoid prompt bloat)
        """
        context_parts = []

        # Quality benchmark
        context_parts.append(
            f"📊 Quality Benchmark: Average template score {patterns['avg_quality_score']:.1f}/100, "
            f"Average length {patterns['avg_line_count']} lines"
        )

        # Common APIs
        if patterns["common_apis"]:
            api_list = ", ".join(patterns["common_apis"][:10])
            context_parts.append(f"🎨 Most Used Canvas APIs: {api_list}")

        # Color schemes
        if patterns["color_schemes"]:
            color_list = ", ".join(patterns["color_schemes"])
            context_parts.append(f"🌈 Recommended Colors: {color_list}")

        # Animation patterns
        if patterns["animation_patterns"]:
            anim_list = ", ".join(patterns["animation_patterns"])
            context_parts.append(f"⚡ Animation Patterns: {anim_list}")

        # Interaction types
        if patterns["interaction_types"]:
            interact_list = ", ".join(patterns["interaction_types"])
            context_parts.append(f"🖱️ Interaction Types: {interact_list}")

        # Structure insights
        if patterns["structure_insights"]:
            for i, insight in enumerate(patterns["structure_insights"], 1):
                context_parts.append(f"💡 Insight {i}: {insight}")

        # Template references (topic + score only, not full code)
        if templates:
            context_parts.append("\n📚 Reference Templates:")
            for template in templates:
                context_parts.append(
                    f"  - {template.subject}/{template.topic} "
                    f"(Score: {template.quality_score:.1f}, Lines: {template.line_count})"
                )

        return "\n".join(context_parts)

    async def calculate_dynamic_thresholds(
        self,
        subject: str = None
    ) -> Dict[str, Any]:
        """
        Calculate dynamic quality thresholds based on template library progress.

        As the agent learns and accumulates high-quality templates, standards are raised.

        Args:
            subject: Optional subject filter (e.g., "physics"). If None, uses all subjects.

        Returns:
            {
                'pass_threshold': float,      # Minimum score to pass (74-90)
                'save_threshold': float,      # Minimum score to save as template (85-95)
                'template_count': int,        # Number of templates in library
                'avg_quality': float,         # Average quality of templates
                'median_quality': float,      # Median quality
                'phase': str,                 # 'initial', 'growth', 'mature'
                'recommendation': str         # Guidance for agent
            }
        """
        # Query template statistics
        query = select(
            func.count(SimulatorTemplate.id),
            func.avg(SimulatorTemplate.quality_score),
            func.percentile_cont(0.5).within_group(SimulatorTemplate.quality_score)
        )

        if subject:
            query = query.where(SimulatorTemplate.subject == subject)

        result = await self.db.execute(query)
        row = result.one()

        template_count = row[0] or 0
        avg_quality = float(row[1]) if row[1] else 74.0

        # Get all scores for median calculation
        score_query = select(SimulatorTemplate.quality_score)
        if subject:
            score_query = score_query.where(SimulatorTemplate.subject == subject)

        score_result = await self.db.execute(score_query)
        scores = [s for (s,) in score_result.fetchall()]
        median_quality = statistics.median(scores) if scores else 74.0

        # === Dynamic Threshold Logic ===

        if template_count < 10:
            # Phase 1: Initial - Lenient standards to rapidly accumulate examples
            phase = "initial"
            pass_threshold = 74.0
            save_threshold = 85.0
            recommendation = "初始阶段：快速积累高质量模板，标准相对宽松"

        elif template_count < 50:
            # Phase 2: Growth - Standards rise with library quality
            phase = "growth"

            # Pass threshold rises based on library average
            # If avg is 88, pass threshold becomes 80 (avg - 8)
            pass_threshold = max(74.0, min(85.0, avg_quality - 8))

            # Save threshold rises to maintain high-quality bar
            # If median is 90, save threshold becomes 88 (median - 2)
            save_threshold = max(85.0, min(92.0, median_quality - 2))

            recommendation = f"成长阶段：模板库平均质量{avg_quality:.1f}分，通过标准提升至{pass_threshold:.1f}分"

        else:
            # Phase 3: Mature - Strict standards, only excellent simulators pass
            phase = "mature"

            # Pass threshold approaches library median
            # If median is 90, pass threshold is 85 (median - 5)
            pass_threshold = max(80.0, min(90.0, median_quality - 5))

            # Save threshold is very high
            # Only top 30% quality simulators are saved
            percentile_70 = statistics.quantiles(scores, n=10)[6] if len(scores) >= 10 else 90.0
            save_threshold = max(88.0, min(95.0, percentile_70))

            recommendation = f"成熟阶段：已积累{template_count}个模板，高标准要求{pass_threshold:.1f}+分通过"

        return {
            'pass_threshold': pass_threshold,
            'save_threshold': save_threshold,
            'template_count': template_count,
            'avg_quality': avg_quality,
            'median_quality': median_quality,
            'phase': phase,
            'recommendation': recommendation,
            'quality_distribution': {
                'excellent': len([s for s in scores if s >= 90]),
                'good': len([s for s in scores if 80 <= s < 90]),
                'acceptable': len([s for s in scores if 74 <= s < 80]),
                'poor': len([s for s in scores if s < 74])
            }
        }
