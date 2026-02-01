"""
Add video content and module structure to test courses
"""
import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update
from app.db.session import AsyncSessionLocal
from app.models.models import CourseNode, Course

# Placeholder video URLs (using public domain videos)
PLACEHOLDER_VIDEOS = {
    "force-basics": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    "force-composition": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
    "newton-laws": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    "biomechanics-intro": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
    "muscle-mechanics": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
}

async def update_video_nodes():
    """Update video nodes with placeholder video URLs"""
    async with AsyncSessionLocal() as db:
        # Get all VIDEO type nodes
        result = await db.execute(
            select(CourseNode).where(CourseNode.type == 'VIDEO')
        )
        video_nodes = result.scalars().all()

        print(f"Found {len(video_nodes)} video nodes")

        video_keys = list(PLACEHOLDER_VIDEOS.keys())

        for i, node in enumerate(video_nodes):
            # Parse existing config
            config = node.timeline_config or {}

            # Use a different video for each node (cycle through available videos)
            video_key = video_keys[i % len(video_keys)]
            video_url = PLACEHOLDER_VIDEOS[video_key]

            # Update video URL in config
            if 'steps' in config:
                for step in config['steps']:
                    if step.get('type') == 'video':
                        step['videoUrl'] = video_url
                        # Add some reasonable defaults
                        if 'duration' not in step:
                            step['duration'] = 300  # 5 minutes
                        if 'pauseAt' not in step:
                            step['pauseAt'] = [120, 240]  # Pause at 2min and 4min
                        if 'aiPromptAtPause' not in step:
                            step['aiPromptAtPause'] = f"视频暂停了。你理解{node.title}的内容了吗？有什么问题吗？"

            # Update the node
            node.timeline_config = config

            print(f"Updated node: {node.node_id} - {node.title}")
            print(f"  Video URL: {video_url}")

        await db.commit()
        print("\n✅ All video nodes updated!")

async def add_course_modules():
    """Add module structure to courses"""
    async with AsyncSessionLocal() as db:
        # Get course 1
        result = await db.execute(
            select(Course).where(Course.id == 1)
        )
        course = result.scalar_one_or_none()

        if course:
            # Get all nodes for this course
            result = await db.execute(
                select(CourseNode)
                .where(CourseNode.course_id == 1)
                .order_by(CourseNode.sequence)
            )
            nodes = result.scalars().all()

            # Group nodes into modules (every 3-4 nodes)
            modules = []
            current_module = None
            module_num = 1

            for i, node in enumerate(nodes):
                if i % 3 == 0:  # Start new module every 3 nodes
                    if current_module:
                        modules.append(current_module)
                    current_module = {
                        "id": f"module-{module_num}",
                        "name": f"模块 {module_num}",
                        "nodes": 0,
                        "completed": 0
                    }
                    module_num += 1

                current_module["nodes"] += 1

            if current_module:
                modules.append(current_module)

            # Update course description with module info
            course.description = f"{course.description}\n\n本课程包含 {len(modules)} 个学习模块，共 {len(nodes)} 个学习节点。"

            await db.commit()

            print(f"\n✅ Added {len(modules)} modules to course: {course.name}")
            for module in modules:
                print(f"  - {module['name']}: {module['nodes']} nodes")

async def main():
    print("🎬 Adding video content to test courses...\n")

    await update_video_nodes()
    await add_course_modules()

    print("\n✅ Done! Video content and modules added successfully!")
    print("\n📝 Test credentials:")
    print("   Email: test@hercu.com")
    print("   Password: test123456")
    print("\n🎓 You can now:")
    print("   1. Login at http://localhost:3001/login")
    print("   2. Browse courses at http://localhost:3001/courses")
    print("   3. Enroll and start learning!")
    print("   4. Test AI teacher dialogue in video nodes")

if __name__ == "__main__":
    asyncio.run(main())
