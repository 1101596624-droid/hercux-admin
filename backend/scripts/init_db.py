"""
Database initialization script
Creates all tables and initial data
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db.session import engine, Base
from app.models.models import *
from app.core.config import settings


async def init_db():
    """Initialize database with all tables"""
    print("🔧 Initializing database...")

    try:
        # Create all tables
        async with engine.begin() as conn:
            print("📋 Creating tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Tables created successfully!")

        print("✅ Database initialization complete!")

    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise
    finally:
        await engine.dispose()


async def drop_all_tables():
    """Drop all tables (use with caution!)"""
    print("⚠️  Dropping all tables...")

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            print("✅ All tables dropped!")

    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        raise
    finally:
        await engine.dispose()


async def reset_db():
    """Reset database - drop and recreate all tables"""
    print("🔄 Resetting database...")
    await drop_all_tables()
    await init_db()
    print("✅ Database reset complete!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "init":
            asyncio.run(init_db())
        elif command == "drop":
            confirm = input("⚠️  Are you sure you want to drop all tables? (yes/no): ")
            if confirm.lower() == "yes":
                asyncio.run(drop_all_tables())
            else:
                print("❌ Operation cancelled")
        elif command == "reset":
            confirm = input("⚠️  Are you sure you want to reset the database? (yes/no): ")
            if confirm.lower() == "yes":
                asyncio.run(reset_db())
            else:
                print("❌ Operation cancelled")
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: init, drop, reset")
    else:
        # Default: just initialize
        asyncio.run(init_db())
