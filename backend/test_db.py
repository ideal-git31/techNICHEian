import asyncio
from database import engine
from models import Base

async def test_connection():
    async with engine.begin() as conn:
        print("✅ Connected to PostgreSQL successfully")
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created successfully")

asyncio.run(test_connection())