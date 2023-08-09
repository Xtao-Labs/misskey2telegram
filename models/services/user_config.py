from typing import cast, Optional

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from init import sqlite
from models.models.user_config import UserConfig


class UserConfigAction:
    @staticmethod
    async def add_user_config(user_config: UserConfig):
        async with sqlite.session() as session:
            session = cast(AsyncSession, session)
            session.add(user_config)
            await session.commit()

    @staticmethod
    async def get_user_config_by_id(user_id: int) -> Optional[UserConfig]:
        async with sqlite.session() as session:
            session = cast(AsyncSession, session)
            statement = select(UserConfig).where(UserConfig.user_id == user_id)
            results = await session.exec(statement)
            return user[0] if (user := results.first()) else None

    @staticmethod
    async def update_user_config(user_config: UserConfig):
        async with sqlite.session() as session:
            session = cast(AsyncSession, session)
            session.add(user_config)
            await session.commit()
            await session.refresh(user_config)

    @staticmethod
    def create_user_config(user_id: int) -> UserConfig:
        return UserConfig(user_id=user_id)
