from sqlalchemy.ext.asyncio import AsyncEngine

from core.infrastructure.orm import Base

async def create_database(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def delete_database(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)