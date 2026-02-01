"""
Add missing indexes to improve query performance
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db.session import engine


async def add_indexes():
    print("Adding database indexes...")

    indexes = [
        # LearningProgress indexes
        ("idx_learning_progress_user_id", "learning_progress", "user_id"),
        ("idx_learning_progress_node_id", "learning_progress", "node_id"),
        ("idx_learning_progress_status", "learning_progress", "status"),
        ("idx_learning_progress_last_accessed", "learning_progress", "last_accessed"),
        # CourseNode indexes
        ("idx_course_nodes_course_id", "course_nodes", "course_id"),
        # UserCourse indexes
        ("idx_user_courses_user_id", "user_courses", "user_id"),
        ("idx_user_courses_course_id", "user_courses", "course_id"),
    ]

    async with engine.begin() as conn:
        for idx_name, table, column in indexes:
            try:
                await conn.execute(text(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column})"))
                print(f"  Created index: {idx_name}")
            except Exception as e:
                print(f"  Index {idx_name} already exists or error: {e}")

    print("Done!")


if __name__ == "__main__":
    asyncio.run(add_indexes())
