"""
Test CRUD API for Course Management
测试课程管理的增删改查API
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
from app.schemas.schemas import (
    CourseManifest,
    CourseUpdate,
    NodeUpdate,
    PackageNodeConfig,
    TimelineConfig,
    TimelineStep,
    UnlockCondition
)


# Create SQLite async engine
DATABASE_URL = "sqlite+aiosqlite:///./test_crud.db"
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


async def test_create_course():
    """Test: Create a course"""
    print("\n" + "="*60)
    print("TEST 1: Create Course")
    print("="*60)

    async with AsyncSessionLocal() as session:
        service = CourseIngestionService(session)
        manifest = await load_example_package("course_package_example.json")

        result = await service.ingest_course(manifest, publish_immediately=False)

        if result.success:
            print(f"✅ Course created: ID={result.courseId}, Nodes={result.nodesCreated}")
            return result.courseId
        else:
            print(f"❌ Failed: {result.message}")
            return None


async def test_read_course(course_id: int):
    """Test: Read course details"""
    print("\n" + "="*60)
    print("TEST 2: Read Course")
    print("="*60)

    async with AsyncSessionLocal() as session:
        service = CourseIngestionService(session)
        course = await service.get_course_by_id(course_id)

        if course:
            print(f"✅ Course found:")
            print(f"   ID: {course.id}")
            print(f"   Name: {course.name}")
            print(f"   Difficulty: {course.difficulty.value}")
            print(f"   Published: {course.is_published}")
            return True
        else:
            print(f"❌ Course {course_id} not found")
            return False


async def test_update_course(course_id: int):
    """Test: Update course metadata"""
    print("\n" + "="*60)
    print("TEST 3: Update Course")
    print("="*60)

    async with AsyncSessionLocal() as session:
        service = CourseIngestionService(session)

        # Update course
        update_data = CourseUpdate(
            courseName="运动生物力学进阶 (已更新)",
            instructor="Prof. Zhang Wei",
            tags=["biomechanics", "physics", "sports-science", "updated"],
            isPublished=True
        )

        course = await service.update_course(course_id, update_data)

        if course:
            print(f"✅ Course updated:")
            print(f"   New Name: {course.name}")
            print(f"   New Instructor: {course.instructor}")
            print(f"   New Tags: {course.tags}")
            print(f"   Published: {course.is_published}")
            return True
        else:
            print(f"❌ Failed to update course {course_id}")
            return False


async def test_read_node(node_id: str):
    """Test: Read node details"""
    print("\n" + "="*60)
    print("TEST 4: Read Node")
    print("="*60)

    async with AsyncSessionLocal() as session:
        service = CourseIngestionService(session)
        node = await service.get_node_by_node_id(node_id)

        if node:
            print(f"✅ Node found:")
            print(f"   Node ID: {node.node_id}")
            print(f"   Title: {node.title}")
            print(f"   Type: {node.type.value}")
            print(f"   Sequence: {node.sequence}")
            if node.timeline_config:
                steps = node.timeline_config.get('steps', [])
                print(f"   Timeline Steps: {len(steps)}")
            return True
        else:
            print(f"❌ Node '{node_id}' not found")
            return False


async def test_update_node(node_id: str):
    """Test: Update node"""
    print("\n" + "="*60)
    print("TEST 5: Update Node")
    print("="*60)

    async with AsyncSessionLocal() as session:
        service = CourseIngestionService(session)

        # Update node
        update_data = NodeUpdate(
            title="1.1 力的基本概念 (已更新)",
            description="理解力的定义、单位和表示方法 - 更新版",
            sequence=10
        )

        node = await service.update_node(node_id, update_data)

        if node:
            print(f"✅ Node updated:")
            print(f"   New Title: {node.title}")
            print(f"   New Description: {node.description}")
            print(f"   New Sequence: {node.sequence}")
            return True
        else:
            print(f"❌ Failed to update node '{node_id}'")
            return False


async def test_add_node(course_id: int):
    """Test: Add new node to course"""
    print("\n" + "="*60)
    print("TEST 6: Add New Node")
    print("="*60)

    async with AsyncSessionLocal() as session:
        service = CourseIngestionService(session)

        # Create new node config
        new_node = PackageNodeConfig(
            nodeId="new_node_test",
            type="reading",
            componentId="text-reader",
            title="新增节点：测试内容",
            description="这是一个通过API新增的节点",
            sequence=999,
            parentId=None,
            timelineConfig=TimelineConfig(
                steps=[
                    TimelineStep(
                        stepId="step-1",
                        type="text",
                        content="# 新增节点测试\n\n这是通过API动态添加的节点内容。"
                    )
                ]
            ),
            unlockCondition=UnlockCondition(type="none"),
            estimatedMinutes=5,
            tags=["test", "new"]
        )

        node = await service.add_node_to_course(course_id, new_node)

        if node:
            print(f"✅ Node added:")
            print(f"   Node ID: {node.node_id}")
            print(f"   Title: {node.title}")
            print(f"   Course ID: {node.course_id}")
            return node.node_id
        else:
            print(f"❌ Failed to add node to course {course_id}")
            return None


async def test_delete_node(node_id: str):
    """Test: Delete node"""
    print("\n" + "="*60)
    print("TEST 7: Delete Node")
    print("="*60)

    async with AsyncSessionLocal() as session:
        service = CourseIngestionService(session)
        success = await service.delete_node(node_id)

        if success:
            print(f"✅ Node '{node_id}' deleted successfully")
            return True
        else:
            print(f"❌ Failed to delete node '{node_id}'")
            return False


async def test_delete_course(course_id: int):
    """Test: Delete course"""
    print("\n" + "="*60)
    print("TEST 8: Delete Course")
    print("="*60)

    async with AsyncSessionLocal() as session:
        service = CourseIngestionService(session)
        success = await service.delete_course(course_id)

        if success:
            print(f"✅ Course {course_id} deleted successfully")
            return True
        else:
            print(f"❌ Failed to delete course {course_id}")
            return False


async def main():
    """Run all CRUD tests"""
    print("\n" + "="*60)
    print("HERCU Course CRUD API Tests")
    print("="*60)

    try:
        # Initialize database
        await init_db()

        # Test 1: Create
        course_id = await test_create_course()
        if not course_id:
            print("\n❌ Create test failed, stopping")
            return

        # Test 2: Read course
        await test_read_course(course_id)

        # Test 3: Update course
        await test_update_course(course_id)

        # Test 4: Read node
        await test_read_node("lesson_1_1")

        # Test 5: Update node
        await test_update_node("lesson_1_1")

        # Test 6: Add new node
        new_node_id = await test_add_node(course_id)

        # Test 7: Delete the new node
        if new_node_id:
            await test_delete_node(new_node_id)

        # Test 8: Delete course (cleanup)
        # await test_delete_course(course_id)

        print("\n" + "="*60)
        print("✅ All CRUD Tests Completed!")
        print("="*60)

        print("\n💡 API Endpoints Available:")
        print("   GET    /api/v1/internal/ingestion/course/{course_id}")
        print("   PUT    /api/v1/internal/ingestion/course/{course_id}")
        print("   DELETE /api/v1/internal/ingestion/course/{course_id}")
        print("   PATCH  /api/v1/internal/ingestion/course/{course_id}/publish")
        print("   GET    /api/v1/internal/ingestion/node/{node_id}")
        print("   PUT    /api/v1/internal/ingestion/node/{node_id}")
        print("   DELETE /api/v1/internal/ingestion/node/{node_id}")
        print("   POST   /api/v1/internal/ingestion/course/{course_id}/node")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
