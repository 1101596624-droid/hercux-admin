"""
Test configuration and fixtures
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient

from app.main import app
from app.db.session import get_db
from app.models.models import Base, User, Course, CourseNode, LearningProgress, NodeStatus, DifficultyLevel, NodeType
from app.core.security import get_password_hash, create_access_token


# Test database URL (SQLite for testing)
# Use StaticPool for in-memory SQLite to share the same connection across all operations
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine with StaticPool to ensure all connections share the same in-memory database
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
    echo=False
)

# Create test session maker
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with TestSessionLocal() as session:
        yield session

    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with database session override."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_user_token(test_user: User) -> str:
    """Create an access token for the test user."""
    return create_access_token(data={"sub": str(test_user.id)})


@pytest.fixture
async def auth_headers(test_user_token: str) -> dict:
    """Create authorization headers with test user token."""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
async def test_course(db_session: AsyncSession) -> Course:
    """Create a test course."""
    course = Course(
        name="Test Course",
        description="A test course for unit testing",
        difficulty=DifficultyLevel.BEGINNER,
        duration_hours=10,
        tags=["test", "python"],
        is_published=1
    )
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)
    return course


@pytest.fixture
async def test_nodes(db_session: AsyncSession, test_course: Course) -> list[CourseNode]:
    """Create test course nodes."""
    nodes = [
        CourseNode(
            course_id=test_course.id,
            node_id="node_1",
            title="Introduction",
            description="Introduction content",
            type=NodeType.READING,
            component_id="intro-component",
            sequence=1,
            unlock_condition={}
        ),
        CourseNode(
            course_id=test_course.id,
            node_id="node_2",
            title="Chapter 1",
            description="Chapter 1 content",
            type=NodeType.VIDEO,
            component_id="chapter1-component",
            sequence=2,
            unlock_condition={"type": "previous_complete"}
        ),
        CourseNode(
            course_id=test_course.id,
            node_id="node_3",
            title="Quiz 1",
            description="Quiz content",
            type=NodeType.QUIZ,
            component_id="quiz1-component",
            sequence=3,
            unlock_condition={"type": "previous_complete"}
        )
    ]

    for node in nodes:
        db_session.add(node)

    await db_session.commit()

    for node in nodes:
        await db_session.refresh(node)

    return nodes


@pytest.fixture
async def test_progress(
    db_session: AsyncSession,
    test_user: User,
    test_nodes: list[CourseNode]
) -> list[LearningProgress]:
    """Create test learning progress records."""
    progress_records = [
        LearningProgress(
            user_id=test_user.id,
            node_id=test_nodes[0].id,
            status=NodeStatus.COMPLETED,
            completion_percentage=100,
            time_spent_seconds=1800
        ),
        LearningProgress(
            user_id=test_user.id,
            node_id=test_nodes[1].id,
            status=NodeStatus.IN_PROGRESS,
            completion_percentage=50,
            time_spent_seconds=900
        )
    ]

    for progress in progress_records:
        db_session.add(progress)

    await db_session.commit()

    for progress in progress_records:
        await db_session.refresh(progress)

    return progress_records
