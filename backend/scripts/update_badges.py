"""
Update badge icons to emoji
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update
from app.db.session import AsyncSessionLocal
from app.models.models import BadgeConfig

# Icon mapping: Lucide name -> emoji
ICON_MAPPING = {
    "footprints": "👣",
    "book-open": "📖",
    "flame": "🔥",
    "clock": "⏰",
    "graduation-cap": "🎓",
}

# Also update names to Chinese
NAME_MAPPING = {
    "first_step": {"name": "初学者", "name_en": "First Step", "description": "完成第一个学习节点"},
    "knowledge_seeker": {"name": "求知者", "name_en": "Knowledge Seeker", "description": "完成10个学习节点"},
    "dedicated_learner": {"name": "坚持学习", "name_en": "Dedicated Learner", "description": "连续学习7天"},
    "time_investor": {"name": "时间投资者", "name_en": "Time Investor", "description": "累计学习10小时"},
    "course_master": {"name": "课程大师", "name_en": "Course Master", "description": "完成3门课程"},
}


async def update_badges():
    print("Updating badge icons and names...")

    async with AsyncSessionLocal() as db:
        # Get all badges
        result = await db.execute(select(BadgeConfig))
        badges = result.scalars().all()

        count = 0
        for badge in badges:
            # Update icon if it's a Lucide name
            if badge.icon in ICON_MAPPING:
                badge.icon = ICON_MAPPING[badge.icon]
                count += 1

            # Update name if mapping exists
            if badge.id in NAME_MAPPING:
                mapping = NAME_MAPPING[badge.id]
                badge.name = mapping["name"]
                badge.name_en = mapping["name_en"]
                badge.description = mapping["description"]

        await db.commit()
        print(f"Done! Updated {count} badges.")


if __name__ == "__main__":
    asyncio.run(update_badges())
