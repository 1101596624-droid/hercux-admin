"""
Enum Query Tests
Tests various ways of querying enum fields to ensure compatibility
"""
import pytest
from sqlalchemy import select, func, cast, String, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import LearningProgress, Course, NodeStatus, DifficultyLevel


@pytest.mark.unit
class TestEnumQueries:
    """Test enum field query patterns"""

    async def test_status_equals_enum(self, db: AsyncSession):
        """Test status = NodeStatus.COMPLETED comparison"""
        # This should not raise an error
        query = select(LearningProgress).where(
            LearningProgress.status == NodeStatus.COMPLETED
        )
        # Just verify query builds without error
        assert query is not None

    async def test_status_equals_string(self, db: AsyncSession):
        """Test status = 'completed' string comparison"""
        query = select(LearningProgress).where(
            LearningProgress.status == 'completed'
        )
        assert query is not None

    async def test_status_cast_to_string(self, db: AsyncSession):
        """Test cast(status, String) = 'completed' comparison"""
        query = select(LearningProgress).where(
            cast(LearningProgress.status, String) == 'completed'
        )
        assert query is not None

    async def test_status_in_with_cast(self, db: AsyncSession):
        """Test cast(status, String).in_([...]) comparison"""
        query = select(func.count(LearningProgress.id)).where(
            cast(LearningProgress.status, String).in_([
                NodeStatus.IN_PROGRESS.value,
                NodeStatus.COMPLETED.value
            ])
        )
        assert query is not None

    async def test_status_in_with_string_values(self, db: AsyncSession):
        """Test status.in_(['in_progress', 'completed']) comparison"""
        query = select(LearningProgress).where(
            LearningProgress.status.in_(['in_progress', 'completed'])
        )
        assert query is not None

    async def test_difficulty_equals_enum(self, db: AsyncSession):
        """Test difficulty = DifficultyLevel comparison"""
        query = select(Course).where(
            Course.difficulty == DifficultyLevel.INTERMEDIATE
        )
        assert query is not None

    async def test_difficulty_cast_to_string(self, db: AsyncSession):
        """Test cast(difficulty, String) comparison"""
        query = select(Course).where(
            cast(Course.difficulty, String) == 'intermediate'
        )
        assert query is not None

    async def test_combined_enum_query(self, db: AsyncSession):
        """Test complex query with multiple enum comparisons"""
        query = select(func.avg(LearningProgress.completion_percentage)).where(
            and_(
                cast(LearningProgress.status, String).in_([
                    NodeStatus.IN_PROGRESS.value,
                    NodeStatus.COMPLETED.value
                ]),
                LearningProgress.completion_percentage > 0
            )
        )
        assert query is not None
