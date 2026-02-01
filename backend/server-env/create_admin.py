"""
创建测试账户脚本
"""
import asyncio
import sys
sys.path.insert(0, '/www/wwwroot/hercu-backend')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from passlib.context import CryptContext

from app.models.models import User

DATABASE_URL = "sqlite+aiosqlite:////www/wwwroot/hercu-backend/hercu.db"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_test_user():
    print("正在创建测试账户...")

    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 检查是否已存在
        result = await session.execute(select(User).where(User.email == "test@hercu.com"))
        if result.scalar_one_or_none():
            print("测试账户已存在")
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
            await session.commit()
            print("测试账户创建成功!")

        print("-" * 40)
        print("测试账户（主应用）:")
        print("  邮箱: test@hercu.com")
        print("  密码: test123")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_test_user())
