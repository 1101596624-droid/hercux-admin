"""
Course Package Upload Test Script (SQLite Version)
测试课程打包上传功能 - SQLite 版本
"""
import asyncio
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.models import Base, Course, CourseNode
from app.services.ingestion import CourseIngestionService
from app.schemas.schemas import CourseManifest


# Create SQLite async engine
DATABASE_URL = "sqlite+aiosqlite:///./test_hercu.db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Initialize database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database initialized")


async def load_example_package(filename: str) -> CourseManifest:
    """Load example course package from JSON file"""
    file_path = Path(__file__).parent.parent / "examples" / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Example file not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return CourseManifest(**data)


async def test_validation():
    """Test package validation"""
    print("\n" + "="*60)
    print("TEST 1: Package Validation")
    print("="*60)

    async with AsyncSessionLocal() as session:
        service = CourseIngestionService(session)

        # Load example package
        manifest = await load_example_package("course_package_example.json")

        # Validate
        validation = await service.validate_package(manifest)

        print(f"\n✅ Validation Result:")
        print(f"   Valid: {validation.isValid}")
        print(f"   Node Count: {validation.nodeCount}")
        print(f"   Estimated Duration: {validation.estimatedDuration:.1f} hours")

        if validation.errors:
            print(f"\n❌ Errors:")
            for error in validation.errors:
                print(f"   - {error}")

        if validation.warnings:
            print(f"\n⚠️  Warnings:")
            for warning in validation.warnings:
                print(f"   - {warning}")

        return validation.isValid


async def test_ingestion():
    """Test course ingestion"""
    print("\n" + "="*60)
    print("TEST 2: Course Ingestion")
    print("="*60)

    async with AsyncSessionLocal() as session:
        service = CourseIngestionService(session)

        # Load example package
        manifest = await load_example_package("course_package_example.json")

        # Check if course already exists
        existing = await service.get_course_by_name(manifest.courseName)
        if existing:
            print(f"\n⚠️  Course '{manifest.courseName}' already exists (ID: {existing.id})")
            print("   Deleting existing course...")
            await service.delete_course(existing.id)
            print("   ✅ Deleted")

        # Ingest
        print(f"\n📦 Ingesting course: {manifest.courseName}")
        result = await service.ingest_course(manifest, publish_immediately=False)

        if result.success:
            print(f"\n✅ Ingestion Successful!")
            print(f"   Course ID: {result.courseId}")
            print(f"   Nodes Created: {result.nodesCreated}")
            print(f"   Message: {result.message}")
            return result.courseId
        else:
            print(f"\n❌ Ingestion Failed!")
            print(f"   Message: {result.message}")
            if result.errors:
                for error in result.errors:
                    print(f"   - {error}")
            return None


async def test_query_course(course_id: int):
    """Test querying the ingested course"""
    print("\n" + "="*60)
    print("TEST 3: Query Ingested Course")
    print("="*60)

    async with AsyncSessionLocal() as session:
        # Get course
        result = await session.execute(
            select(Course).where(Course.id == course_id)
        )
        course = result.scalar_one_or_none()

        if not course:
            print(f"\n❌ Course {course_id} not found")
            return

        print(f"\n📚 Course Details:")
        print(f"   ID: {course.id}")
        print(f"   Name: {course.name}")
        print(f"   Difficulty: {course.difficulty.value}")
        print(f"   Instructor: {course.instructor}")
        print(f"   Duration: {course.duration_hours} hours")
        print(f"   Tags: {', '.join(course.tags)}")
        print(f"   Published: {'Yes' if course.is_published else 'No'}")

        # Get nodes
        result = await session.execute(
            select(CourseNode)
            .where(CourseNode.course_id == course_id)
            .order_by(CourseNode.sequence)
        )
        nodes = result.scalars().all()

        print(f"\n📋 Course Nodes ({len(nodes)} total):")
        for node in nodes:
            indent = "  " if node.parent_id else ""
            icon = "📖" if node.type.value == "reading" else \
                   "🎥" if node.type.value == "video" else \
                   "🎮" if node.type.value == "simulator" else \
                   "❓" if node.type.value == "quiz" else \
                   "✏️"

            print(f"   {indent}{icon} {node.title}")

            # Show timeline steps if present
            if node.timeline_config and 'steps' in node.timeline_config:
                steps = node.timeline_config['steps']
                print(f"      └─ {len(steps)} steps: {', '.join([s['type'] for s in steps])}")


async def test_20_node_course():
    """Test ingesting the 20-node course"""
    print("\n" + "="*60)
    print("TEST 4: Ingest 20-Node Course")
    print("="*60)

    async with AsyncSessionLocal() as session:
        service = CourseIngestionService(session)

        # Load 20-node package
        manifest = await load_example_package("course_package_20_nodes.json")

        # Check if exists
        existing = await service.get_course_by_name(manifest.courseName)
        if existing:
            print(f"\n⚠️  Course '{manifest.courseName}' already exists")
            print("   Deleting...")
            await service.delete_course(existing.id)

        # Ingest
        print(f"\n📦 Ingesting: {manifest.courseName}")
        print(f"   Nodes: {len(manifest.nodes)}")

        result = await service.ingest_course(manifest, publish_immediately=True)

        if result.success:
            print(f"\n✅ Success!")
            print(f"   Course ID: {result.courseId}")
            print(f"   Nodes Created: {result.nodesCreated}")

            # Show node breakdown
            node_types = {}
            for node in manifest.nodes:
                node_types[node.type] = node_types.get(node.type, 0) + 1

            print(f"\n📊 Node Type Breakdown:")
            for node_type, count in node_types.items():
                print(f"   {node_type}: {count}")

            return result.courseId
        else:
            print(f"\n❌ Failed: {result.message}")
            return None


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("HERCU Course Package Ingestion Tests (SQLite)")
    print("="*60)

    try:
        # Initialize database
        await init_db()

        # Test 1: Validation
        is_valid = await test_validation()
        if not is_valid:
            print("\n❌ Validation failed, stopping tests")
            return

        # Test 2: Ingestion
        course_id = await test_ingestion()
        if not course_id:
            print("\n❌ Ingestion failed, stopping tests")
            return

        # Test 3: Query
        await test_query_course(course_id)

        # Test 4: 20-node course
        course_id_20 = await test_20_node_course()
        if course_id_20:
            await test_query_course(course_id_20)

        print("\n" + "="*60)
        print("✅ All Tests Completed Successfully!")
        print("="*60)

        print("\n💡 Next Steps:")
        print("   1. Set up PostgreSQL database")
        print("   2. Start the backend: python run.py")
        print("   3. Visit API docs: http://localhost:8000/docs")
        print("   4. Try the ingestion endpoints")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
