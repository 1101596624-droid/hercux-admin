"""
Create admin user for HERCU admin panel
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_admin():
    """Create admin user"""
    async with AsyncSessionLocal() as session:
        # Check if admin already exists
        result = await session.execute(
            select(User).where(User.email == "admin@hercu.com")
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update to admin
            existing.is_admin = True
            existing.hashed_password = pwd_context.hash("admin123")
            await session.commit()
            print("✅ Admin user updated!")
        else:
            # Create new admin
            admin = User(
                email="admin@hercu.com",
                username="admin",
                hashed_password=pwd_context.hash("admin123"),
                full_name="System Admin",
                is_active=True,
                is_admin=True,
                is_premium=True
            )
            session.add(admin)
            await session.commit()
            print("✅ Admin user created!")

        print("\n📋 Admin credentials:")
        print("   Email: admin@hercu.com")
        print("   Password: admin123")


if __name__ == "__main__":
    asyncio.run(create_admin())
