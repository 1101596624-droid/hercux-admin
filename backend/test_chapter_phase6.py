"""
Phase 6: Chapter Learning Functionality Tests (Simplified for Windows Console)
"""
import sys
import asyncio
from app.services.learning import ChapterScorer, UnifiedTemplateService

def test_chapter_scorer_basic():
    """Test 1: ChapterScorer scoring accuracy"""
    print("\n" + "="*60)
    print("Test 1: ChapterScorer Basic Functionality")
    print("="*60)

    scorer = ChapterScorer()

    # High-quality chapter
    high_quality_chapter = {
        "lesson_id": "test_001",
        "title": "Newton's Second Law",
        "sections": [
            {
                "title": "Concept Explanation",
                "content": "Newton's second law states that F=ma...",
                "steps": [
                    {"step_number": 1, "body": "Understanding force and mass relationship"},
                    {"step_number": 2, "body": "Deriving the equation F=ma"}
                ]
            }
        ],
        "diagrams": [
            {"diagram_id": "d1", "description": "Force diagram showing acceleration"}
        ],
        "questions": [
            {
                "question": "What is the relationship between force and acceleration?",
                "explanation": "According to F=ma, force is directly proportional to acceleration"
            }
        ],
        "simulator": {
            "simulator_id": "sim_001",
            "description": "Interactive simulator showing force-acceleration relationship"
        }
    }

    score = scorer.evaluate(high_quality_chapter)

    print(f"\nChapter: {high_quality_chapter['title']}")
    print(f"Total Score: {score.total_score}/100")
    print(f"  - Depth Score: {score.depth_score}/30")
    print(f"  - Structure Score: {score.structure_score}/25")
    print(f"  - Visual Score: {score.visual_score}/20")
    print(f"  - Teaching Score: {score.teaching_score}/15")
    print(f"  - Simulator Score: {score.simulator_score}/10")
    print(f"Pass Status: {'PASSED' if score.passed else 'FAILED'} (threshold: {score.threshold})")
    print(f"Save as Template: {'YES' if score.total_score >= 90.0 else 'NO'} (requires 90+)")

    # Low-quality chapter
    low_quality_chapter = {
        "lesson_id": "test_002",
        "title": "Simple Chapter",
        "sections": []
    }

    score2 = scorer.evaluate(low_quality_chapter)

    print(f"\nChapter: {low_quality_chapter['title']}")
    print(f"Total Score: {score2.total_score}/100")
    print(f"Pass Status: {'PASSED' if score2.passed else 'FAILED'}")

    return score.total_score >= score.threshold


def test_metadata_extraction():
    """Test 2: Metadata extraction for learning"""
    print("\n" + "="*60)
    print("Test 2: Metadata Extraction")
    print("="*60)

    scorer = ChapterScorer()

    chapter = {
        "lesson_id": "test_003",
        "title": "Test Chapter",
        "sections": [{"title": "Section 1"}],
        "diagrams": [{"diagram_id": "d1"}],
        "questions": [{"question": "Q1"}],
        "simulator": {"simulator_id": "sim_001"}
    }

    metadata = scorer.extract_metadata(chapter)

    print(f"\nExtracted Metadata: {metadata}")
    print(f"Metadata type: {type(metadata)}")
    print(f"Metadata is dict: {isinstance(metadata, dict)}")

    return isinstance(metadata, dict)


def test_threshold_validation():
    """Test 3: Threshold validation (80 pass, 90+ save)"""
    print("\n" + "="*60)
    print("Test 3: Threshold Validation")
    print("="*60)

    scorer = ChapterScorer()

    # Test 80-point threshold
    chapter_80 = {"lesson_id": "test_004", "title": "80-Point Chapter"}
    score_80 = scorer.evaluate(chapter_80)
    score_80.total_score = 80.0
    score_80.calculate_total()

    print(f"\n80-Point Chapter:")
    print(f"  Total Score: {score_80.total_score}")
    print(f"  Passed: {score_80.passed} (expected: True)")
    print(f"  Save as Template: {score_80.total_score >= 90.0} (expected: False)")

    # Test 90-point threshold
    score_90 = scorer.evaluate(chapter_80)
    score_90.total_score = 90.0
    score_90.calculate_total()

    print(f"\n90-Point Chapter:")
    print(f"  Total Score: {score_90.total_score}")
    print(f"  Passed: {score_90.passed} (expected: True)")
    print(f"  Save as Template: {score_90.total_score >= 90.0} (expected: True)")

    # Test 75-point threshold
    score_75 = scorer.evaluate(chapter_80)
    score_75.total_score = 75.0
    score_75.calculate_total()

    print(f"\n75-Point Chapter:")
    print(f"  Total Score: {score_75.total_score}")
    print(f"  Passed: {score_75.passed} (expected: False)")
    print(f"  Save as Template: {score_75.total_score >= 90.0} (expected: False)")

    return (score_80.passed and
            score_90.passed and score_90.total_score >= 90.0 and
            not score_75.passed)


def run_all_tests():
    """Run all Phase 6 tests"""
    print("\n" + "="*60)
    print("Phase 6: Chapter Learning Tests")
    print("="*60)

    results = {}

    try:
        results['test_1'] = test_chapter_scorer_basic()
        results['test_2'] = test_metadata_extraction()
        results['test_3'] = test_threshold_validation()

        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)
        for test_name, passed in results.items():
            status = "PASSED" if passed else "FAILED"
            print(f"{test_name}: {status}")

        all_passed = all(results.values())
        print(f"\nOverall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")

        return all_passed

    except Exception as e:
        print(f"\nTest execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
