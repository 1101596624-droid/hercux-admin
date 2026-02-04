"""
Database Schema Consistency Tests
Ensures production database matches expected schema
"""
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.integration
class TestDatabaseSchema:
    """Test database schema consistency"""

    async def test_required_enum_types_exist(self, db: AsyncSession):
        """Check all required enum types exist in database"""
        required_enums = [
            'nodestatus',
            'difficultylevel', 
            'studiopackagestatus'
        ]
        
        result = await db.execute(text("""
            SELECT typname FROM pg_type 
            WHERE typtype = 'e' AND typname = ANY(:enums)
        """), {"enums": required_enums})
        
        existing_enums = [row[0] for row in result.fetchall()]
        
        for enum_name in required_enums:
            assert enum_name in existing_enums, f"Enum type '{enum_name}' does not exist in database"

    async def test_nodestatus_enum_values(self, db: AsyncSession):
        """Check nodestatus enum has correct values"""
        result = await db.execute(text("""
            SELECT enumlabel FROM pg_enum e
            JOIN pg_type t ON e.enumtypid = t.oid
            WHERE t.typname = 'nodestatus'
            ORDER BY enumsortorder
        """))
        
        values = [row[0] for row in result.fetchall()]
        expected = ['locked', 'available', 'in_progress', 'completed']
        
        # Check all expected values exist (order may vary)
        for val in expected:
            assert val in values, f"nodestatus missing value: {val}"

    async def test_difficultylevel_enum_values(self, db: AsyncSession):
        """Check difficultylevel enum has correct values"""
        result = await db.execute(text("""
            SELECT enumlabel FROM pg_enum e
            JOIN pg_type t ON e.enumtypid = t.oid
            WHERE t.typname = 'difficultylevel'
            ORDER BY enumsortorder
        """))
        
        values = [row[0] for row in result.fetchall()]
        expected = ['beginner', 'intermediate', 'advanced']
        
        for val in expected:
            assert val in values, f"difficultylevel missing value: {val}"

    async def test_studiopackagestatus_enum_values(self, db: AsyncSession):
        """Check studiopackagestatus enum has correct values"""
        result = await db.execute(text("""
            SELECT enumlabel FROM pg_enum e
            JOIN pg_type t ON e.enumtypid = t.oid
            WHERE t.typname = 'studiopackagestatus'
            ORDER BY enumsortorder
        """))
        
        values = [row[0] for row in result.fetchall()]
        expected = ['draft', 'published', 'archived']
        
        for val in expected:
            assert val in values, f"studiopackagestatus missing value: {val}"

    async def test_learning_progress_table_exists(self, db: AsyncSession):
        """Check learning_progress table exists with required columns"""
        result = await db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'learning_progress'
        """))
        
        columns = {row[0]: row[1] for row in result.fetchall()}
        
        required_columns = ['id', 'user_id', 'node_id', 'status', 'completion_percentage']
        for col in required_columns:
            assert col in columns, f"learning_progress missing column: {col}"

    async def test_courses_table_exists(self, db: AsyncSession):
        """Check courses table exists with required columns"""
        result = await db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'courses'
        """))
        
        columns = {row[0]: row[1] for row in result.fetchall()}
        
        required_columns = ['id', 'name', 'description', 'difficulty', 'is_published']
        for col in required_columns:
            assert col in columns, f"courses missing column: {col}"
