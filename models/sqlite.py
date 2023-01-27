from sqlmodel import SQLModel

from models.models.user import User
from pathlib import Path

__all__ = ["User", "Sqlite"]

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

DataPath = Path("data")
DataPath.mkdir(exist_ok=True, parents=True)


class Sqlite:
    def __init__(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///data/data.db")
        self.session = sessionmaker(bind=self.engine, class_=AsyncSession)

    async def create_db_and_tables(self):
        async with self.engine.begin() as session:
            await session.run_sync(SQLModel.metadata.create_all)

    async def get_session(self):
        async with self.session() as session:
            yield session

    def stop(self):
        self.session.close_all()
