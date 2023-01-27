from typing import cast, Optional

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from init import sqlite
from models.models.user import User, TokenStatusEnum


class UserAction:
    @staticmethod
    async def add_user(user: User):
        async with sqlite.session() as session:
            session = cast(AsyncSession, session)
            session.add(user)
            await session.commit()

    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[User]:
        async with sqlite.session() as session:
            session = cast(AsyncSession, session)
            statement = select(User).where(User.user_id == user_id)
            results = await session.exec(statement)
            return user[0] if (user := results.first()) else None

    @staticmethod
    async def get_user_if_ok(user_id: int) -> Optional[User]:
        async with sqlite.session() as session:
            session = cast(AsyncSession, session)
            statement = select(User).where(
                User.user_id == user_id
            ).where(
                User.status == TokenStatusEnum.STATUS_SUCCESS
            ).where(
                User.chat_id != 0
            ).where(
                User.timeline_topic != 0
            ).where(
                User.notice_topic != 0
            ).where(
                User.token != ""
            )
            results = await session.exec(statement)
            return user[0] if (user := results.first()) else None

    @staticmethod
    async def get_all_token_ok_users() -> list[User]:
        async with sqlite.session() as session:
            session = cast(AsyncSession, session)
            statement = select(User).where(
                User.status == TokenStatusEnum.STATUS_SUCCESS
            ).where(
                User.chat_id != 0
            ).where(
                User.timeline_topic != 0
            ).where(
                User.notice_topic != 0
            ).where(
                User.token != ""
            )
            results = await session.exec(statement)
            users = results.all()
            return [user[0] for user in users]

    @staticmethod
    async def update_user(user: User):
        async with sqlite.session() as session:
            session = cast(AsyncSession, session)
            session.add(user)
            await session.commit()
            await session.refresh(user)

    @staticmethod
    async def add_or_update_user(user: User):
        if await UserAction.get_user_by_id(user.user_id):
            await UserAction.update_user(user)
        else:
            await UserAction.add_user(user)

    @staticmethod
    async def set_user_status(user_id: int, status: TokenStatusEnum) -> bool:
        user = await UserAction.get_user_by_id(user_id)
        if not user:
            return False
        user.status = status
        await UserAction.update_user(user)
        return True

    @staticmethod
    async def change_user_token(user_id: int, token: str) -> bool:
        user = await UserAction.get_user_by_id(user_id)
        if not user:
            user = User(user_id=user_id, token=token, status=TokenStatusEnum.STATUS_SUCCESS)
        user.token = token
        user.status = TokenStatusEnum.STATUS_SUCCESS
        await UserAction.update_user(user)
        return True

    @staticmethod
    async def change_user_group_id(user_id: int, chat_id: int) -> bool:
        user = await UserAction.get_user_by_id(user_id)
        if not user:
            return False
        user.chat_id = chat_id
        await UserAction.update_user(user)
        return True

    @staticmethod
    async def change_user_timeline(user_id: int, timeline: int) -> bool:
        user = await UserAction.get_user_by_id(user_id)
        if not user:
            return False
        if user.notice_topic == timeline:
            return False
        user.timeline_topic = timeline
        await UserAction.update_user(user)
        return True

    @staticmethod
    async def change_user_notice(user_id: int, notice: int) -> bool:
        user = await UserAction.get_user_by_id(user_id)
        if not user:
            return False
        if user.timeline_topic == notice:
            return False
        user.notice_topic = notice
        await UserAction.update_user(user)
        return True
