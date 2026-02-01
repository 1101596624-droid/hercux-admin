"""
数据库初始化脚本
- 创建管理员账户
- 创建测试用户账户
- 清空课程数据
"""
import asyncio
import sys
sys.path.insert(0, '/www/wwwroot/hercu-backend')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete, text
from passlib.context import CryptContext

from app.models.models import User, Course, CourseNode

DATABASE_URL = "sqlite+aiosqlite:////www/wwwroot/hercu-backend/hercu.db"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def init_database():
    print("=" * 50)
    print("HERCU 数据库初始化")
    print("=" * 50)

    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 1. 清空课程数据
        print("\n[1] 清空课程数据...")
        try:
            await session.execute(delete(CourseNode))
            await session.execute(delete(Course))
            await session.commit()
            print("    ✓ 课程数据已清空")
        except Exception as e:
            print(f"    ✗ 清空课程失败: {e}")
            await session.rollback()

        # 2. 创建/更新管理员账户
        print("\n[2] 创建管理员账户...")
        result = await session.execute(select(User).where(User.email == "admin@hercu.com"))
        admin = result.scalar_one_or_none()
        if admin:
            admin.hashed_password = pwd_context.hash("admin123")
            admin.is_admin = 1
            admin.is_active = 1
            print("    ✓ 管理员账户已更新")
        else:
            admin = User(
                email="admin@hercu.com",
                username="admin",
                hashed_password=pwd_context.hash("admin123"),
                full_name="管理员",
                is_active=1,
                is_premium=1,
                is_admin=1
            )
            session.add(admin)
            print("    ✓ 管理员账户已创建")

        # 3. 创建/更新测试用户账户
        print("\n[3] 创建测试用户账户...")
        result = await session.execute(select(User).where(User.email == "test@hercu.com"))
        test_user = result.scalar_one_or_none()
        if test_user:
            test_user.hashed_password = pwd_context.hash("test123")
            test_user.is_active = 1
            print("    ✓ 测试用户账户已更新")
        else:
            test_user = User(
                email="test@hercu.com",
                username="test",
                hashed_password=pwd_context.hash("test123"),
                full_name="测试用户",
                is_active=1,
                is_premium=1,
                is_admin=0
            )
            session.add(test_user)
            print("    ✓ 测试用户账户已创建")

        await session.commit()

    await engine.dispose()

    print("\n" + "=" * 50)
    print("初始化完成!")
    print("=" * 50)
    print("\n账户信息:")
    print("-" * 40)
    print("管理员账户（后台应用）:")
    print("  邮箱: admin@hercu.com")
    print("  密码: admin123")
    print("-" * 40)
    print("测试用户账户（主应用）:")
    print("  邮箱: test@hercu.com")
    print("  密码: test123")
    print("-" * 40)
    print("\n后端服务端口: 8001")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(init_database())
