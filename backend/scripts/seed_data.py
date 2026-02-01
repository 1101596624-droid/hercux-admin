"""
Seed database with sample data
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.models import (
    User, Course, CourseNode, LearningProgress, TrainingPlan,
    Achievement, UserCourse, DifficultyLevel, NodeType, NodeStatus
)
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed_users():
    """Create sample users"""
    async with AsyncSessionLocal() as session:
        # Check if users already exist
        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("⏭️  Users already exist, skipping...")
            return

        users = [
            User(
                email="demo@hercu.com",
                username="demo_user",
                hashed_password=pwd_context.hash("demo123"),
                full_name="Demo User",
                is_active=1,
                is_premium=1
            ),
            User(
                email="student@hercu.com",
                username="student",
                hashed_password=pwd_context.hash("student123"),
                full_name="Student User",
                is_active=1,
                is_premium=0
            ),
            User(
                email="test@hercu.com",
                username="test",
                hashed_password=pwd_context.hash("test123"),
                full_name="Test User",
                is_active=1,
                is_premium=0
            )
        ]

        session.add_all(users)
        await session.commit()
        print(f"✅ Created {len(users)} users")


async def seed_courses():
    """Create sample courses"""
    async with AsyncSessionLocal() as session:
        # Check if courses already exist
        result = await session.execute(select(Course).limit(1))
        if result.scalar_one_or_none():
            print("⏭️  Courses already exist, skipping...")
            return

        courses = [
            Course(
                name="运动生物力学基础",
                description="深入理解人体运动的力学原理，从基础概念到实际应用",
                difficulty=DifficultyLevel.BEGINNER,
                tags=["biomechanics", "fundamentals", "strength"],
                instructor="Dr. Zhang Wei",
                duration_hours=12.5,
                thumbnail_url="https://example.com/biomechanics.jpg",
                is_published=1
            ),
            Course(
                name="力量训练科学",
                description="基于科学的力量训练方法和编程原理",
                difficulty=DifficultyLevel.INTERMEDIATE,
                tags=["strength", "training", "programming"],
                instructor="Coach Li Ming",
                duration_hours=15.0,
                thumbnail_url="https://example.com/strength.jpg",
                is_published=1
            ),
            Course(
                name="运动营养学",
                description="运动员和健身爱好者的营养策略",
                difficulty=DifficultyLevel.BEGINNER,
                tags=["nutrition", "recovery", "performance"],
                instructor="Dr. Wang Fang",
                duration_hours=10.0,
                thumbnail_url="https://example.com/nutrition.jpg",
                is_published=1
            )
        ]

        session.add_all(courses)
        await session.commit()
        print(f"✅ Created {len(courses)} courses")


async def seed_course_nodes():
    """Create sample course nodes with timeline configs"""
    async with AsyncSessionLocal() as session:
        # Check if nodes already exist
        result = await session.execute(select(CourseNode).limit(1))
        if result.scalar_one_or_none():
            print("⏭️  Course nodes already exist, skipping...")
            return

        # Get first course
        result = await session.execute(select(Course).limit(1))
        course = result.scalar_one()

        if not course:
            print("❌ No courses found, please seed courses first")
            return

        nodes = [
            # Chapter 1: Introduction
            CourseNode(
                course_id=course.id,
                parent_id=None,
                node_id="biomech_ch1",
                type=NodeType.READING,
                component_id="chapter-intro",
                title="第一章：力学基础",
                description="力学基本概念介绍",
                sequence=1,
                timeline_config={
                    "steps": [
                        {
                            "stepId": "step-1",
                            "type": "text",
                            "content": "# 欢迎来到运动生物力学\n\n在这一章中，我们将学习力学的基本概念..."
                        }
                    ]
                },
                unlock_condition={"type": "none"}
            ),
            # Lesson 1.1: Force Basics
            CourseNode(
                course_id=course.id,
                parent_id=None,  # Will be updated after parent is created
                node_id="biomech_1_1",
                type=NodeType.VIDEO,
                component_id="video-player",
                title="1.1 力的基本概念",
                description="理解力的定义、单位和表示方法",
                sequence=1,
                timeline_config={
                    "steps": [
                        {
                            "stepId": "step-1",
                            "type": "video",
                            "videoUrl": "https://example.com/videos/force-basics.mp4",
                            "duration": 300,
                            "pauseAt": [120, 240],
                            "aiPromptAtPause": "你理解力的三要素了吗？"
                        },
                        {
                            "stepId": "step-2",
                            "type": "quiz",
                            "question": "力的三要素不包括以下哪一项？",
                            "options": ["大小", "方向", "作用点", "颜色"],
                            "correctAnswer": 3
                        }
                    ]
                },
                unlock_condition={"type": "previous_complete"}
            ),
            # Lesson 1.2: Force Simulator
            CourseNode(
                course_id=course.id,
                parent_id=None,
                node_id="biomech_1_2",
                type=NodeType.SIMULATOR,
                component_id="force-vector-sim",
                title="1.2 力的合成与分解",
                description="通过模拟器理解力的矢量运算",
                sequence=2,
                timeline_config={
                    "steps": [
                        {
                            "stepId": "step-1",
                            "type": "video",
                            "videoUrl": "https://example.com/videos/force-composition.mp4",
                            "duration": 180
                        },
                        {
                            "stepId": "step-2",
                            "type": "simulator",
                            "simulatorId": "force-vector-sim",
                            "props": {
                                "force1": {"magnitude": 10, "angle": 0},
                                "force2": {"magnitude": 10, "angle": 90}
                            },
                            "completionCriteria": {
                                "type": "attempts",
                                "minAttempts": 3
                            }
                        },
                        {
                            "stepId": "step-3",
                            "type": "quiz",
                            "question": "两个大小相等、方向相反的力合成后结果是？",
                            "options": ["零", "两倍", "不变", "无法确定"],
                            "correctAnswer": 0
                        }
                    ]
                },
                unlock_condition={"type": "previous_complete"}
            ),
            # Lesson 1.3: Practice
            CourseNode(
                course_id=course.id,
                parent_id=None,
                node_id="biomech_1_3",
                type=NodeType.PRACTICE,
                component_id="practice-quiz",
                title="1.3 章节练习",
                description="测试你对本章内容的掌握程度",
                sequence=3,
                timeline_config={
                    "steps": [
                        {
                            "stepId": "step-1",
                            "type": "quiz",
                            "question": "牛顿第一定律又称为？",
                            "options": ["惯性定律", "加速度定律", "作用力定律", "万有引力定律"],
                            "correctAnswer": 0
                        },
                        {
                            "stepId": "step-2",
                            "type": "quiz",
                            "question": "F=ma 中，a 代表什么？",
                            "options": ["速度", "加速度", "位移", "时间"],
                            "correctAnswer": 1
                        }
                    ]
                },
                unlock_condition={"type": "previous_complete"}
            )
        ]

        session.add_all(nodes)
        await session.commit()
        print(f"✅ Created {len(nodes)} course nodes")


async def seed_user_enrollments():
    """Enroll demo user in courses"""
    async with AsyncSessionLocal() as session:
        # Check if enrollments exist
        result = await session.execute(select(UserCourse).limit(1))
        if result.scalar_one_or_none():
            print("⏭️  User enrollments already exist, skipping...")
            return

        # Get demo user and first course
        user_result = await session.execute(
            select(User).where(User.email == "demo@hercu.com")
        )
        user = user_result.scalar_one_or_none()

        course_result = await session.execute(select(Course).limit(1))
        course = course_result.scalar_one_or_none()

        if not user or not course:
            print("❌ User or course not found")
            return

        enrollment = UserCourse(
            user_id=user.id,
            course_id=course.id,
            enrolled_at=datetime.now(timezone.utc),
            last_accessed=datetime.now(timezone.utc)
        )

        session.add(enrollment)
        await session.commit()
        print("✅ Created user enrollment")


async def seed_learning_progress():
    """Create initial learning progress for demo user"""
    async with AsyncSessionLocal() as session:
        # Check if progress exists
        result = await session.execute(select(LearningProgress).limit(1))
        if result.scalar_one_or_none():
            print("⏭️  Learning progress already exists, skipping...")
            return

        # Get demo user
        user_result = await session.execute(
            select(User).where(User.email == "demo@hercu.com")
        )
        user = user_result.scalar_one_or_none()

        # Get first few nodes
        nodes_result = await session.execute(
            select(CourseNode).order_by(CourseNode.sequence).limit(3)
        )
        nodes = nodes_result.scalars().all()

        if not user or not nodes:
            print("❌ User or nodes not found")
            return

        progress_records = [
            LearningProgress(
                user_id=user.id,
                node_id=nodes[0].id,
                status=NodeStatus.COMPLETED,
                completion_percentage=100.0,
                time_spent_seconds=300,
                last_accessed=datetime.now(timezone.utc) - timedelta(days=2),
                completed_at=datetime.now(timezone.utc) - timedelta(days=2)
            ),
            LearningProgress(
                user_id=user.id,
                node_id=nodes[1].id,
                status=NodeStatus.IN_PROGRESS,
                completion_percentage=60.0,
                time_spent_seconds=180,
                last_accessed=datetime.now(timezone.utc) - timedelta(hours=3)
            ),
            LearningProgress(
                user_id=user.id,
                node_id=nodes[2].id,
                status=NodeStatus.UNLOCKED,
                completion_percentage=0.0,
                time_spent_seconds=0
            )
        ]

        session.add_all(progress_records)
        await session.commit()
        print(f"✅ Created {len(progress_records)} progress records")


async def seed_all():
    """Seed all data"""
    print("🌱 Starting database seeding...\n")

    await seed_users()
    await seed_courses()
    await seed_course_nodes()
    await seed_user_enrollments()
    await seed_learning_progress()

    print("\n✅ Database seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_all())
