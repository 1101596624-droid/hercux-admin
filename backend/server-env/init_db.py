"""
数据库初始化脚本
上传到服务器后运行: python init_db.py
"""
import asyncio
import sys
sys.path.insert(0, '/www/wwwroot/hercu-backend')

from sqlalchemy.ext.asyncio import create_async_engine
from app.db.session import Base
from app.models.models import *  # 导入所有模型以注册表

DATABASE_URL = "sqlite+aiosqlite:////www/wwwroot/hercu-backend/hercu.db"

async def init_database():
    print("正在初始化数据库...")
    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()
    print("数据库表创建完成!")

if __name__ == "__main__":
    asyncio.run(init_database())
