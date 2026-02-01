"""
为现有课程生成题库
Generate quiz bank for existing courses
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.quiz_generator import generate_quiz_for_course


async def main():
    """Generate quiz for existing psychology course"""
    print("\n" + "="*60)
    print("HERCU Quiz Generation for Existing Course")
    print("="*60)

    course_id = 4  # 稀缺心理学课程

    print(f"\nGenerating quiz bank for course ID: {course_id}")
    print("This will generate 39 questions per node (13 easy, 13 medium, 13 hard)")
    print("-"*60)

    try:
        result = await generate_quiz_for_course(course_id)

        print("\n" + "="*60)
        print("Generation Complete!")
        print("="*60)
        print(f"Total nodes processed: {result.get('total_nodes', 0)}")
        print(f"Successful: {result.get('successful', 0)}")
        print(f"Failed: {result.get('failed', 0)}")
        print(f"Total questions generated: {result.get('total_questions', 0)}")

        if result.get('errors'):
            print("\nErrors:")
            for error in result['errors']:
                print(f"  - {error}")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
