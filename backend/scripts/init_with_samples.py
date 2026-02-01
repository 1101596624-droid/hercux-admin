"""
Initialize database and load sample courses
初始化数据库并加载示例课程
"""
import asyncio
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.models import Base
from app.services.ingestion import CourseIngestionService
from app.schemas.schemas import CourseManifest
from app.core.config import settings


async def init_database():
    """Initialize database with sample courses"""
    print("\n" + "="*60)
    print("HERCU Database Initialization")
    print("="*60)

    # Create engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create tables
    print("\n📦 Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created")

    # Load sample courses
    examples_dir = Path(__file__).parent.parent / "examples"
    sample_files = [
        "course_package_example.json",
        "course_package_20_nodes.json"
    ]

    async with AsyncSessionLocal() as session:
        service = CourseIngestionService(session)

        for filename in sample_files:
            file_path = examples_dir / filename
            if not file_path.exists():
                print(f"⚠️  File not found: {filename}")
                continue

            print(f"\n📚 Loading: {filename}")
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            manifest = CourseManifest(**data)
            result = await service.ingest_course(manifest, publish_immediately=True)

            if result.success:
                print(f"✅ Loaded: {manifest.courseName}")
                print(f"   Course ID: {result.courseId}")
                print(f"   Nodes: {result.nodesCreated}")
            else:
                print(f"❌ Failed: {result.message}")

    print("\n" + "="*60)
    print("✅ Database initialization complete!")
    print("="*60)
    print("\n💡 Next steps:")
    print("   1. Start backend: python run.py")
    print("   2. Visit API docs: http://localhost:8000/api/v1/docs")
    print("   3. Test endpoints with sample data")


if __name__ == "__main__":
    asyncio.run(init_database())
