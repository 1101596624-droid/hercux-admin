"""
Initialize default badges in badge_configs table
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.models import BadgeConfig

# Default badges data
DEFAULT_BADGES = [
    {
        "id": "first_step",
        "name": "First Step",
        "name_en": "First Step",
        "icon": "footprints",
        "description": "Complete your first learning node",
        "category": "learning",
        "rarity": "common",
        "points": 10,
        "condition": {"type": "counter", "metric": "completed_nodes", "target": 1},
        "is_active": 1,
        "sort_order": 1
    },
    {
        "id": "knowledge_seeker",
        "name": "Knowledge Seeker",
        "name_en": "Knowledge Seeker",
        "icon": "book-open",
        "description": "Complete 10 learning nodes",
        "category": "learning",
        "rarity": "rare",
        "points": 50,
        "condition": {"type": "counter", "metric": "completed_nodes", "target": 10},
        "is_active": 1,
        "sort_order": 2
    },
    {
        "id": "dedicated_learner",
        "name": "Dedicated Learner",
        "name_en": "Dedicated Learner",
        "icon": "flame",
        "description": "Maintain a 7-day learning streak",
        "category": "persistence",
        "rarity": "rare",
        "points": 100,
        "condition": {"type": "streak", "target": 7},
        "is_active": 1,
        "sort_order": 3
    },
    {
        "id": "time_investor",
        "name": "Time Investor",
        "name_en": "Time Investor",
        "icon": "clock",
        "description": "Spend 10 hours learning",
        "category": "persistence",
        "rarity": "epic",
        "points": 150,
        "condition": {"type": "time_based", "target": 10},
        "is_active": 1,
        "sort_order": 4
    },
    {
        "id": "course_master",
        "name": "Course Master",
        "name_en": "Course Master",
        "icon": "graduation-cap",
        "description": "Complete 3 courses",
        "category": "learning",
        "rarity": "legendary",
        "points": 200,
        "condition": {"type": "courses", "target": 3},
        "is_active": 1,
        "sort_order": 5
    }
]


async def init_badges():
    print("Initializing default badges...")

    async with AsyncSessionLocal() as db:
        for badge_data in DEFAULT_BADGES:
            # Check if badge already exists
            result = await db.execute(
                select(BadgeConfig).where(BadgeConfig.id == badge_data["id"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"  Badge '{badge_data['id']}' already exists, skipping...")
                continue

            # Create new badge
            badge = BadgeConfig(**badge_data)
            db.add(badge)
            print(f"  Created badge: {badge_data['id']} - {badge_data['name']}")

        await db.commit()
        print("Done! Default badges initialized.")


if __name__ == "__main__":
    asyncio.run(init_badges())
