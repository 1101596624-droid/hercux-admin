"""
Reset test user password
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update
from app.db.session import AsyncSessionLocal
from app.models.models import User
from app.core.security import get_password_hash

async def reset_password():
    """Reset test user password"""
    async with AsyncSessionLocal() as db:
        # Get test user
        result = await db.execute(
            select(User).where(User.email == 'test@hercu.com')
        )
        user = result.scalar_one_or_none()

        if user:
            # Update password
            new_hash = get_password_hash('test123456')
            user.hashed_password = new_hash
            await db.commit()
            print(f"✅ Password reset for user: {user.email}")
            print(f"   New hash: {new_hash}")
        else:
            print("❌ User not found")

if __name__ == "__main__":
    asyncio.run(reset_password())
