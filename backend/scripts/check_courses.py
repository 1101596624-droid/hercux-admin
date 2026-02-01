import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.models import Course

async def check_courses():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Course))
        courses = result.scalars().all()

        print(f'Found {len(courses)} courses in database:')
        for course in courses:
            print(f'  - ID: {course.id}, Name: {course.name}, Published: {course.is_published}')

if __name__ == "__main__":
    asyncio.run(check_courses())
