from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Creating Connection pool to PostgresSQL
engine = create_async_engine(
    DATABASE_URL,
    echo = True
)

# Configurinf session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()   
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()    