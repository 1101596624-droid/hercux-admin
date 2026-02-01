"""
Simple database table initialization script
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import engine, Base
from app.models.models import *

async def init_tables():
    print("Initializing database tables...")
    try:
        async with engine.begin() as conn:
            print("Creating tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("Tables created successfully!")
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_tables())
