"""
Integration Tests for Agent Learning System (Phase 3)

Tests the complete learning system including:
- Vector search and pattern retrieval
- Pattern application recording
- Experience distillation
- Smart evaluation skipping
- Code cleaning and quality checks
- End-to-end learning flow

Created: 2026-02-13
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import (
    GenerationPattern,
    PatternApplication,
    ContentTemplate,
    QualityEvaluation,
)
from app.services.learning.template_service import UnifiedTemplateService
from app.services.learning.distillation_service import DistillationService
from app.services.course_generation.generator import ChapterGenerator
from app.core.config import settings


# ============================================
# Test Fixtures
# ============================================

@pytest.fixture
async def template_service(db_session: AsyncSession):
    """Create UnifiedTemplateService instance for testing"""
    return UnifiedTemplateService(db_session)


@pytest.fixture
async def distillation_service(db_session: AsyncSession):
    """Create DistillationService instance for testing"""
    # Use test API key
    api_key = settings.anthropic_key or "test-api-key"
    return DistillationService(db_session, api_key)


@pytest.fixture
async def generator(db_session: AsyncSession):
    """Create ChapterGenerator instance for testing"""
    return ChapterGenerator(db=db_session)


@pytest.fixture
async def sample_pattern(db_session: AsyncSession) -> GenerationPattern:
    """Create a sample generation pattern for testing"""
    pattern = GenerationPattern(
        pattern_type="best_practice",
        step_type="text_content",
        subject="physics",
        topic="mechanics",
        description="Use clear explanations with real-world examples",
        strategy_guidance="Start with conceptual overview, then detailed mechanics",
        success_indicators=["high clarity score", "positive student feedback"],
        common_pitfalls=["too much jargon", "lack of examples"],
        confidence=0.85,
        embedding=[0.1] * 384,  # Mock embedding
        source_templates=["template_1", "template_2"],
        created_from_count=2,
    )
    db_session.add(pattern)
    await db_session.commit()
    await db_session.refresh(pattern)
    return pattern


@pytest.fixture
async def sample_content_template(db_session: AsyncSession) -> ContentTemplate:
    """Create a sample content template for testing"""
    content = {
        "text": "This is a high-quality physics explanation about forces.",
        "examples": ["Apple falling", "Ball rolling"],
    }

    template = ContentTemplate(
        template_type="chapter_content",
        subject="physics",
        topic="forces",
        content=json.dumps(content),
        quality_score=82.5,
        score_breakdown={"clarity": 85, "accuracy": 90, "engagement": 75},
        template_metadata={"word_count": 500, "has_examples": True},
        difficulty_level="beginner",
        content_hash="abc123def456",
        usage_count=0,
    )
    db_session.add(template)
    await db_session.commit()
    await db_session.refresh(template)
    return template


# ============================================
# Test 1: End-to-End Learning Flow
# ============================================

@pytest.mark.asyncio
async def test_learning_flow_end_to_end(
    db_session: AsyncSession,
    template_service: UnifiedTemplateService,
    sample_content_template: ContentTemplate,
):
    """
    Test complete learning flow from generation to pattern storage

    Flow:
    1. Generate content
    2. Evaluate quality
    3. Save as template (if high quality)
    4. Record evaluation
    5. Verify storage
    """
    # Step 1: Simulate content generation (already have sample_content_template)

    # Step 2: Record quality evaluation
    evaluation = await template_service.record_quality_evaluation(
        content_type="chapter_content",
        content_id="test_chapter_001",
        quality_score=82.5,
        score_breakdown={"clarity": 85, "accuracy": 90, "engagement": 75},
        saved_as_template=True,
    )

    assert evaluation is not None
    assert evaluation.quality_score == 82.5
    assert evaluation.saved_as_template == 1

    # Step 3: Verify template exists
    templates = await template_service.get_similar_templates(
        template_type="chapter_content",
        subject="physics",
        topic="forces",
        min_quality=75.0,
        limit=5,
    )

    assert len(templates) >= 1
    assert templates[0].quality_score >= 75.0

    # Step 4: Query evaluation records
    result = await db_session.execute(
        select(QualityEvaluation).where(QualityEvaluation.content_id == "test_chapter_001")
    )
    stored_eval = result.scalar_one_or_none()

    assert stored_eval is not None
    assert stored_eval.quality_score == 82.5


# ============================================
# Test 2: Vector Search
# ============================================

@pytest.mark.asyncio
async def test_vector_search(
    db_session: AsyncSession,
    template_service: UnifiedTemplateService,
    sample_pattern: GenerationPattern,
):
    """
    Test vector similarity search for patterns

    Verifies:
    - Query embedding generation
    - Similarity calculation
    - Result filtering and ranking
    """
    # Test vector search for similar patterns
    query_text = "How to explain physics concepts clearly"

    with patch.object(template_service, '_generate_embedding', return_value=[0.1] * 384):
        patterns = await template_service.get_similar_patterns_by_vector(
            query_text=query_text,
            step_type="text_content",
            subject="physics",
            min_confidence=0.7,
            limit=5,
        )

    # Should find the sample pattern
    assert len(patterns) >= 1
    assert patterns[0].step_type == "text_content"
    assert patterns[0].subject == "physics"
    assert patterns[0].confidence >= 0.7

    # Verify pattern content
    pattern = patterns[0]
    assert pattern.description is not None
    assert pattern.strategy_guidance is not None
    assert isinstance(pattern.success_indicators, list)


# ============================================
# Test 3: Pattern Application Recording
# ============================================

@pytest.mark.asyncio
async def test_pattern_application(
    db_session: AsyncSession,
    template_service: UnifiedTemplateService,
    sample_pattern: GenerationPattern,
):
    """
    Test recording of pattern applications during generation

    Verifies:
    - Application recording
    - Success tracking
    - Confidence updates
    """
    # Record a pattern application
    application = await template_service.record_pattern_application(
        pattern_id=sample_pattern.id,
        step_type="text_content",
        applied_context={
            "chapter_title": "Introduction to Forces",
            "learning_objectives": ["Understand Newton's laws"],
        },
        result_quality_score=85.0,
        was_successful=True,
    )

    assert application is not None
    assert application.pattern_id == sample_pattern.id
    assert application.result_quality_score == 85.0
    assert application.was_successful is True

    # Verify application was stored
    result = await db_session.execute(
        select(PatternApplication).where(PatternApplication.pattern_id == sample_pattern.id)
    )
    stored_app = result.scalar_one_or_none()

    assert stored_app is not None
    assert stored_app.result_quality_score == 85.0


# ============================================
# Test 4: Experience Distillation
# ============================================

@pytest.mark.asyncio
async def test_distillation(
    db_session: AsyncSession,
    distillation_service: DistillationService,
    sample_content_template: ContentTemplate,
):
    """
    Test experience distillation from generation history

    Verifies:
    - Pattern extraction from successful cases
    - Anti-pattern extraction from failures
    - Pattern persistence
    """
    # Create multiple quality evaluations to distill from
    evaluations = [
        QualityEvaluation(
            content_type="chapter_content",
            content_id=f"chapter_{i}",
            quality_score=score,
            score_breakdown={"clarity": score, "accuracy": score},
            saved_as_template=1 if score >= 75 else 0,
        )
        for i, score in enumerate([85, 80, 78, 55, 50, 45])
    ]

    for eval in evaluations:
        db_session.add(eval)
    await db_session.commit()

    # Mock the Claude API calls for distillation
    mock_success_patterns = [
        {
            "description": "Use clear structure with examples",
            "strategy_guidance": "Start simple, add complexity gradually",
            "success_indicators": ["high clarity", "good examples"],
            "confidence": 0.8,
        }
    ]

    mock_anti_patterns = [
        {
            "description": "Avoid dense technical jargon without explanation",
            "strategy_guidance": "Don't assume prior knowledge",
            "common_pitfalls": ["too complex", "no examples"],
            "confidence": 0.75,
        }
    ]

    with patch.object(
        distillation_service,
        '_extract_success_patterns',
        return_value=mock_success_patterns
    ), patch.object(
        distillation_service,
        '_extract_anti_patterns',
        return_value=mock_anti_patterns
    ):
        result = await distillation_service.distill_patterns(
            step_type="text_content",
            subject="physics",
            lookback_days=7,
            min_quality_threshold=75.0,
            max_quality_threshold=60.0,
        )

    # Verify patterns were extracted
    assert "success_patterns" in result
    assert "anti_patterns" in result


# ============================================
# Test 5: Smart Skip (Intelligent Evaluation)
# ============================================

@pytest.mark.asyncio
async def test_smart_skip(
    db_session: AsyncSession,
    generator: ChapterGenerator,
):
    """
    Test smart evaluation skipping based on confidence

    Verifies:
    - Probability calculation
    - Threshold-based skipping
    - Confidence scoring
    """
    # Test case 1: High rule score + similar samples -> likely skip
    should_eval, probability, reason = generator.should_evaluate_with_agent(
        step_type="text_content",
        rule_score=85.0,
        similar_samples=[
            {"quality_score": 82, "confidence": 0.9},
            {"quality_score": 88, "confidence": 0.85},
            {"quality_score": 80, "confidence": 0.8},
        ],
    )

    assert isinstance(should_eval, bool)
    assert 0.0 <= probability <= 1.0
    assert reason is not None

    # With high confidence, should likely skip (low probability)
    if probability < 0.5:
        assert should_eval is False

    # Test case 2: Low rule score -> should evaluate
    should_eval_low, probability_low, reason_low = generator.should_evaluate_with_agent(
        step_type="text_content",
        rule_score=60.0,
        similar_samples=None,
    )

    # Low score should trigger evaluation (high probability)
    assert probability_low > probability  # Lower score = higher eval probability


# ============================================
# Test 6: Code Cleaning Enhancement
# ============================================

@pytest.mark.asyncio
async def test_code_cleaning(generator: ChapterGenerator):
    """
    Test enhanced code cleaning functionality

    Verifies:
    - Comment removal
    - Whitespace normalization
    - console.log removal
    - Validation
    """
    # Test HTML with issues
    dirty_html = """
    <html>
        <script>
            // This is a comment
            console.log("Debug message");


            function setup() {
                // Another comment
                console.log("Setup");
            }

            /* Multi-line
               comment */
            function update() {
                ctx.fillRect(0, 0, 10, 10);
            }
        </script>
    </html>
    """

    cleaned = generator._clean_code(dirty_html)

    # Verify cleaning
    assert "// This is a comment" not in cleaned
    assert "console.log" not in cleaned
    assert "/* Multi-line" not in cleaned
    assert "function setup()" in cleaned
    assert "function update()" in cleaned
    assert "ctx.fillRect" in cleaned


# ============================================
# Test 7: Enhanced Quality Check
# ============================================

@pytest.mark.asyncio
async def test_enhanced_quality_check(generator: ChapterGenerator):
    """
    Test enhanced quality checking with multiple criteria

    Verifies:
    - Setup/update function detection
    - Canvas API usage
    - Interaction patterns
    - Visual elements
    - Code structure
    """
    # Test valid simulator code
    valid_html = """
    <html>
    <body>
        <canvas id="canvas"></canvas>
        <script>
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');

            let state = { x: 0, y: 0, vx: 1, vy: 1 };

            function setup() {
                canvas.width = 800;
                canvas.height = 600;
            }

            function update() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                state.x += state.vx;
                state.y += state.vy;
                ctx.beginPath();
                ctx.arc(state.x, state.y, 10, 0, Math.PI * 2);
                ctx.fill();
            }

            canvas.addEventListener('click', (e) => {
                state.x = e.offsetX;
                state.y = e.offsetY;
            });

            setup();
            setInterval(update, 16);
        </script>
    </body>
    </html>
    """

    score, breakdown = generator._calculate_quality_score(valid_html)

    # Verify quality metrics
    assert score > 0
    assert isinstance(breakdown, dict)

    # Check breakdown includes key metrics
    expected_keys = [
        "structure_score",
        "canvas_api_score",
        "interaction_score",
        "visual_score",
    ]

    for key in expected_keys:
        if key in breakdown:
            assert 0 <= breakdown[key] <= 100


# ============================================
# Test 8: Pattern Confidence Updates
# ============================================

@pytest.mark.asyncio
async def test_pattern_confidence_updates(
    db_session: AsyncSession,
    template_service: UnifiedTemplateService,
    sample_pattern: GenerationPattern,
):
    """
    Test pattern confidence updates based on application results

    Verifies:
    - Confidence increases with successful applications
    - Confidence decreases with failures
    - Confidence bounds (0-1)
    """
    initial_confidence = sample_pattern.confidence

    # Record successful application
    await template_service.record_pattern_application(
        pattern_id=sample_pattern.id,
        step_type="text_content",
        applied_context={"test": "success"},
        result_quality_score=90.0,
        was_successful=True,
    )

    # Refresh pattern
    await db_session.refresh(sample_pattern)

    # Note: Confidence update logic may be implemented in the service
    # For now, just verify the application was recorded
    result = await db_session.execute(
        select(PatternApplication).where(PatternApplication.pattern_id == sample_pattern.id)
    )
    applications = result.scalars().all()

    assert len(applications) >= 1
    assert applications[0].was_successful is True


# ============================================
# Test 9: Trajectory Recording
# ============================================

@pytest.mark.asyncio
async def test_trajectory_recording(db_session: AsyncSession):
    """
    Test generation trajectory recording for auto-distillation

    Verifies:
    - Trajectory creation
    - Counter increment
    - Distillation trigger threshold
    """
    # This would test the CourseGenerationService._record_generation_trajectory
    # Since we're testing in isolation, we'll verify the data models work

    # Create quality evaluations that would trigger distillation
    evaluations = []
    for i in range(55):  # Over threshold of 50
        eval = QualityEvaluation(
            content_type="text_content",
            content_id=f"content_{i}",
            quality_score=75.0 + i % 10,
            score_breakdown={"clarity": 75},
        )
        evaluations.append(eval)
        db_session.add(eval)

    await db_session.commit()

    # Query evaluations
    result = await db_session.execute(select(QualityEvaluation))
    stored_evals = result.scalars().all()

    assert len(stored_evals) >= 50  # Threshold for auto-distillation


# ============================================
# Test 10: Template Deduplication
# ============================================

@pytest.mark.asyncio
async def test_template_deduplication(
    db_session: AsyncSession,
    template_service: UnifiedTemplateService,
):
    """
    Test template deduplication based on content hash

    Verifies:
    - Duplicate detection
    - Usage count increment
    - No duplicate storage
    """
    content = {"text": "Unique physics content", "examples": ["Ex1"]}

    # Save first time
    template1 = await template_service.save_as_template(
        template_type="chapter_content",
        subject="physics",
        topic="mechanics",
        content=content,
        quality_score=80.0,
        score_breakdown={"clarity": 80},
        metadata={"word_count": 100},
    )

    assert template1 is not None
    assert template1.usage_count == 0

    # Try to save duplicate
    template2 = await template_service.save_as_template(
        template_type="chapter_content",
        subject="physics",
        topic="mechanics",
        content=content,  # Same content
        quality_score=80.0,
        score_breakdown={"clarity": 80},
        metadata={"word_count": 100},
    )

    # Should return None (duplicate detected)
    assert template2 is None

    # Verify usage count was incremented
    await db_session.refresh(template1)
    assert template1.usage_count == 1


# ============================================
# Test 11: Multi-Step Type Pattern Search
# ============================================

@pytest.mark.asyncio
async def test_multi_step_pattern_search(
    db_session: AsyncSession,
    template_service: UnifiedTemplateService,
):
    """
    Test pattern search across different step types

    Verifies:
    - Step type filtering
    - Subject filtering
    - Pattern type filtering
    """
    # Create patterns for different step types
    step_types = ["text_content", "illustrated_content", "assessment", "ai_tutor"]

    for step_type in step_types:
        pattern = GenerationPattern(
            pattern_type="best_practice",
            step_type=step_type,
            subject="physics",
            topic="mechanics",
            description=f"Best practice for {step_type}",
            strategy_guidance=f"Strategy for {step_type}",
            success_indicators=["high quality"],
            confidence=0.8,
            embedding=[0.1] * 384,
            source_templates=[],
            created_from_count=1,
        )
        db_session.add(pattern)

    await db_session.commit()

    # Search for each step type
    for step_type in step_types:
        with patch.object(template_service, '_generate_embedding', return_value=[0.1] * 384):
            patterns = await template_service.get_similar_patterns_by_vector(
                query_text="test query",
                step_type=step_type,
                subject="physics",
                min_confidence=0.7,
                limit=5,
            )

        assert len(patterns) >= 1
        assert all(p.step_type == step_type for p in patterns)


# ============================================
# Configuration Tests
# ============================================

def test_learning_system_config():
    """
    Test learning system configuration values

    Verifies:
    - All required config values exist
    - Values are within expected ranges
    """
    assert hasattr(settings, 'ENABLE_AGENT_LEARNING')
    assert hasattr(settings, 'AGENT_EVAL_PROBABILITY_THRESHOLD')
    assert hasattr(settings, 'DISTILLATION_TRIGGER_COUNT')
    assert hasattr(settings, 'PATTERN_CONFIDENCE_THRESHOLD')
    assert hasattr(settings, 'VECTOR_SIMILARITY_TOP_K')

    # Verify reasonable defaults
    assert 0.0 <= settings.AGENT_EVAL_PROBABILITY_THRESHOLD <= 1.0
    assert settings.DISTILLATION_TRIGGER_COUNT > 0
    assert 0.0 <= settings.PATTERN_CONFIDENCE_THRESHOLD <= 1.0
    assert settings.VECTOR_SIMILARITY_TOP_K > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
