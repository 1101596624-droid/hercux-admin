"""
Test Quiz Learning Integration

Simple test to verify the quiz learning system is working correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.quiz.quiz_generator import EnhancedQuizGenerator


async def test_basic_generation():
    """Test basic quiz generation"""
    print("=" * 60)
    print("Testing Quiz Learning Integration")
    print("=" * 60)

    # Setup database
    db_path = Path(__file__).parent.parent.parent.parent / "hercu_dev.db"
    engine = create_engine(f'sqlite:///{db_path}')
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        generator = EnhancedQuizGenerator(db)

        print("\nGenerating sample quiz questions...")
        questions = await generator.generate_quiz_with_learning(
            node_title="Python Variables and Data Types",
            learning_objectives=[
                "Understand variable naming conventions",
                "Learn basic data types in Python"
            ],
            content="""
            Variables are containers for storing data values. In Python, you don't
            need to declare the type of a variable. Python has several data types
            including integers, floats, strings, and booleans.
            """,
            difficulty="easy",
            subject="programming",
            topic="python_basics",
            num_questions=3
        )

        print(f"\n✓ Generated {len(questions)} questions")

        for q in questions:
            print(f"\n--- Question {q['id']} ---")
            print(f"Q: {q['question']}")
            print(f"Quality Score: {q.get('quality_score', 0):.1f}/100")
            print(f"Passed: {'✓' if q.get('quality_passed') else '✗'}")

        print("\n" + "=" * 60)
        print("Test completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_basic_generation())
