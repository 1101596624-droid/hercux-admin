"""
Re-import courses with quiz generation
重新导入课程并生成题库
"""
import asyncio
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.services.ingestion import CourseIngestionService
from app.schemas.schemas import CourseManifest
from app.models.models import Course, CourseNode


async def load_manifest(filename: str) -> CourseManifest:
    """Load course manifest from JSON file"""
    file_path = Path(__file__).parent.parent / "examples" / filename

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return CourseManifest(**data)


async def reimport_course(filename: str, generate_quiz: bool = True):
    """Re-import a course with quiz generation"""
    print(f"\n{'='*60}")
    print(f"Re-importing: {filename}")
    print(f"Generate Quiz: {generate_quiz}")
    print(f"{'='*60}")

    async with AsyncSessionLocal() as session:
        service = CourseIngestionService(session)

        # Load manifest
        manifest = await load_manifest(filename)
        print(f"\nCourse: {manifest.courseName}")
        print(f"Nodes: {len(manifest.nodes)}")

        # Check if course exists
        existing = await service.get_course_by_name(manifest.courseName)
        if existing:
            print(f"\nDeleting existing course (ID: {existing.id})...")
            await service.delete_course(existing.id)
            print("Deleted.")

        # Re-import with quiz generation
        print(f"\nIngesting course...")
        result = await service.ingest_course(
            manifest,
            publish_immediately=True,
            generate_quiz=generate_quiz
        )

        if result.success:
            print(f"\n✅ Success!")
            print(f"   Course ID: {result.courseId}")
            print(f"   Nodes Created: {result.nodesCreated}")
            print(f"   Message: {result.message}")
            return result.courseId
        else:
            print(f"\n❌ Failed!")
            print(f"   Message: {result.message}")
            if result.errors:
                for error in result.errors:
                    print(f"   - {error}")
            return None


async def main():
    """Re-import all example courses with quiz generation"""
    print("\n" + "="*60)
    print("HERCU Course Re-import with Quiz Generation")
    print("="*60)

    # List of example packages to import
    packages = [
        "course_package_example.json",
        "course_package_20_nodes.json",
    ]

    results = []

    for package in packages:
        try:
            course_id = await reimport_course(package, generate_quiz=True)
            results.append({
                "package": package,
                "success": course_id is not None,
                "course_id": course_id
            })
        except FileNotFoundError as e:
            print(f"\n⚠️ Skipping {package}: {e}")
            results.append({
                "package": package,
                "success": False,
                "course_id": None
            })
        except Exception as e:
            print(f"\n❌ Error processing {package}: {e}")
            results.append({
                "package": package,
                "success": False,
                "course_id": None
            })

    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)

    success_count = sum(1 for r in results if r["success"])
    print(f"\nTotal: {len(results)}")
    print(f"Success: {success_count}")
    print(f"Failed: {len(results) - success_count}")

    for r in results:
        status = "✅" if r["success"] else "❌"
        course_info = f"(ID: {r['course_id']})" if r["course_id"] else ""
        print(f"  {status} {r['package']} {course_info}")


if __name__ == "__main__":
    asyncio.run(main())
