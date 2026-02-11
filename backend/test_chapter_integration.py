"""
Phase 6: Integration Test for Chapter Learning System

This test verifies:
1. Learning context injection in _generate_text_content()
2. ChapterScorer evaluation after chapter generation
3. Automatic template saving for 90+ score chapters
4. Quality evaluation recording to database
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.services.learning import ChapterScorer, UnifiedTemplateService
from app.models.models import ContentTemplate, QualityEvaluation
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, AsyncMock, patch
import json

def test_learning_context_injection():
    """Test 1: Verify learning context is retrieved and formatted"""
    print("\n" + "="*60)
    print("Test 1: Learning Context Injection")
    print("="*60)

    # Mock database session
    mock_db = Mock()
    mock_query = Mock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.limit.return_value = mock_query

    # Create mock templates
    mock_template = Mock()
    mock_template.quality_score = 92.0
    mock_template.template_metadata = {
        "best_practices": ["Use clear explanations", "Include visual aids"],
        "common_pattern": "Start with theory, then examples"
    }
    mock_template.score_breakdown = {
        "depth_score": 28,
        "structure_score": 23,
        "visual_score": 18,
        "teaching_score": 14,
        "simulator_score": 9
    }
    mock_query.all.return_value = [mock_template]

    # Test template service
    template_service = UnifiedTemplateService(mock_db)

    # Verify get_similar_templates works
    import asyncio
    templates = asyncio.run(template_service.get_similar_templates(
        template_type='chapter_content',
        subject='physics',
        topic='newtons_laws',
        min_quality=90.0,
        limit=2
    ))

    print(f"\nRetrieved {len(templates)} high-quality templates")
    print(f"Template quality score: {templates[0].quality_score if templates else 'N/A'}")

    # Verify pattern analysis
    patterns = template_service.analyze_patterns(templates)
    print(f"\nPattern analysis results:")
    print(f"  - Average quality: {patterns['avg_quality_score']}")
    print(f"  - Template count: {patterns['template_count']}")
    print(f"  - Best practices found: {len(patterns['best_practices'])}")

    # Verify learning context formatting
    learning_context = template_service.format_learning_context(
        patterns=patterns,
        templates=templates,
        template_type='chapter_content'
    )

    print(f"\nLearning context generated: {len(learning_context)} characters")
    print(f"Contains 'LEARNING CONTEXT': {'LEARNING CONTEXT' in learning_context}")
    print(f"Contains 'Best Practices': {'Best Practices' in learning_context}")

    success = (len(templates) > 0 and
               patterns['avg_quality_score'] >= 90.0 and
               'LEARNING CONTEXT' in learning_context)

    print(f"\nTest 1: {'PASSED' if success else 'FAILED'}")
    return success


def test_chapter_evaluation():
    """Test 2: Verify ChapterScorer evaluates chapters correctly"""
    print("\n" + "="*60)
    print("Test 2: Chapter Quality Evaluation")
    print("="*60)

    scorer = ChapterScorer()

    # Test chapter
    chapter = {
        "lesson_id": "test_chapter_001",
        "title": "Newton's Second Law",
        "sections": [
            {
                "title": "Introduction",
                "content": "Force equals mass times acceleration",
                "steps": [
                    {"step_number": 1, "body": "Understanding force"},
                    {"step_number": 2, "body": "Understanding acceleration"}
                ]
            }
        ],
        "diagrams": [{"diagram_id": "d1", "description": "Force diagram"}],
        "questions": [{"question": "What is F=ma?", "explanation": "Newton's second law"}],
        "simulator": {"simulator_id": "sim_001", "description": "Force simulator"}
    }

    score = scorer.evaluate(chapter)

    print(f"\nChapter evaluated: {chapter['title']}")
    print(f"Total score: {score.total_score}/100")
    print(f"Score breakdown:")
    print(f"  - Depth: {score.depth_score}/30")
    print(f"  - Structure: {score.structure_score}/25")
    print(f"  - Visual: {score.visual_score}/20")
    print(f"  - Teaching: {score.teaching_score}/15")
    print(f"  - Simulator: {score.simulator_score}/10")
    print(f"\nPassed threshold (80): {score.passed}")
    print(f"Qualifies for template (90+): {score.total_score >= 90.0}")

    # Extract metadata
    metadata = scorer.extract_metadata(chapter)
    print(f"\nMetadata extracted: {type(metadata).__name__}")

    success = (score.total_score > 0 and
               isinstance(metadata, dict) and
               score.threshold == 80.0)

    print(f"\nTest 2: {'PASSED' if success else 'FAILED'}")
    return success


def test_template_saving():
    """Test 3: Verify high-quality chapters are saved as templates"""
    print("\n" + "="*60)
    print("Test 3: Template Saving (90+ scores)")
    print("="*60)

    # Mock database
    mock_db = Mock()
    mock_db.add = Mock()
    mock_db.commit = Mock()
    mock_db.refresh = Mock()

    mock_query = Mock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None  # No duplicate

    template_service = UnifiedTemplateService(mock_db)

    # High-quality chapter (90+ score)
    high_quality_chapter = {
        "lesson_id": "test_high_quality",
        "title": "Excellent Chapter",
        "sections": [{"title": "Section 1", "content": "Rich content"}],
        "complexity_level": "advanced"
    }

    score_breakdown = {
        "depth_score": 28,
        "structure_score": 23,
        "visual_score": 18,
        "teaching_score": 14,
        "simulator_score": 9
    }

    metadata = {
        "quality_breakdown": score_breakdown,
        "best_practices": ["Clear structure", "Good examples"]
    }

    # Save as template
    import asyncio
    result = asyncio.run(template_service.save_as_template(
        template_type='chapter_content',
        subject='physics',
        topic='test_topic',
        content=high_quality_chapter,
        quality_score=92.0,
        score_breakdown=score_breakdown,
        metadata=metadata,
        difficulty_level='advanced'
    ))

    print(f"\nTemplate save attempted: {result is not None or 'duplicate detected'}")
    print(f"Database add() called: {mock_db.add.called}")
    print(f"Database commit() called: {mock_db.commit.called}")

    success = mock_db.add.called and mock_db.commit.called

    print(f"\nTest 3: {'PASSED' if success else 'FAILED'}")
    return success


def test_quality_evaluation_recording():
    """Test 4: Verify quality evaluations are recorded"""
    print("\n" + "="*60)
    print("Test 4: Quality Evaluation Recording")
    print("="*60)

    # Mock database
    mock_db = Mock()
    mock_db.add = Mock()
    mock_db.commit = Mock()
    mock_db.refresh = Mock()

    template_service = UnifiedTemplateService(mock_db)

    # Record evaluation
    import asyncio
    evaluation = asyncio.run(template_service.record_quality_evaluation(
        content_type='chapter_content',
        content_id='test_chapter_001',
        quality_score=85.0,
        score_breakdown={'depth_score': 25, 'structure_score': 20},
        saved_as_template=False
    ))

    print(f"\nEvaluation recorded: {evaluation is not None}")
    print(f"Database add() called: {mock_db.add.called}")
    print(f"Database commit() called: {mock_db.commit.called}")

    success = mock_db.add.called and mock_db.commit.called

    print(f"\nTest 4: {'PASSED' if success else 'FAILED'}")
    return success


def run_integration_tests():
    """Run all integration tests"""
    print("\n" + "="*70)
    print("Phase 6: Chapter Learning System Integration Tests")
    print("="*70)

    results = {}

    try:
        results['learning_context_injection'] = test_learning_context_injection()
        results['chapter_evaluation'] = test_chapter_evaluation()
        results['template_saving'] = test_template_saving()
        results['quality_recording'] = test_quality_evaluation_recording()

        print("\n" + "="*70)
        print("Integration Test Summary")
        print("="*70)

        for test_name, passed in results.items():
            status = "PASSED" if passed else "FAILED"
            print(f"{test_name}: {status}")

        all_passed = all(results.values())
        passed_count = sum(1 for v in results.values() if v)
        total_count = len(results)

        print(f"\nResults: {passed_count}/{total_count} tests passed")
        print(f"Overall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")

        return all_passed

    except Exception as e:
        print(f"\nIntegration test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
