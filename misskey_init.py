import contextlib
from asyncio import sleep
from typing import Optional

from aiohttp import ClientConnectorError
from mipa.exception import WebSocketNotConnected
from mipa.ext import commands
from mipa.router import Router
from mipac import (
    Note,
    NotificationFollow,
    NotificationFollowRequest,
    ChatMessage,
    NotificationAchievement,
)
from mipac.client import Client as MisskeyClient

from defs.chat import send_chat_message
from defs.misskey import send_update
from defs.notice import (
    send_user_followed,
    send_follow_request,
    send_follow_request_accept,
    send_achievement_earned,
)

from models.models.user import User, TokenStatusEnum
from models.services.user import UserAction

from init import bot, logs, sqlite


class MisskeyBot(commands.Bot):
    def __init__(self, user: User):
        super().__init__()
        self.user_id: int = user.user_id
        self.tg_user: User = user

    async def on_ready(self, ws):
        await Router(ws).connect_channel(["main", "home"])
        logs.info(f"成功启动 Misskey Bot WS 任务 {self.user_id}")

    async def on_reconnect(self, ws):
        await Router(ws).connect_channel(["main", "home"])

    async def on_note(self, note: Note):
        await send_update(
            self.tg_user.host, self.tg_user.chat_id, note, self.tg_user.timeline_topic
        )

    async def on_user_followed(self, notice: NotificationFollow):
        await send_user_followed(
            self.tg_user.chat_id, notice, self.tg_user.notice_topic
        )

    async def on_follow_request(self, notice: NotificationFollowRequest):
        await send_follow_request(
            self.tg_user.chat_id, notice, self.tg_user.notice_topic
        )

    async def on_follow_request_accept(self, notice: NotificationFollowRequest):
        await send_follow_request_accept(
            self.tg_user.chat_id, notice, self.tg_user.notice_topic
        )

    async def on_chat(self, message: ChatMessage):
        await send_chat_message(
            self.tg_user.host, self.tg_user.chat_id, message, self.tg_user.notice_topic
        )

    async def on_chat_unread_message(self, message: ChatMessage):
        await message.api.read()

    async def on_achievement_earned(self, notice: NotificationAchievement):
        await send_achievement_earned(
            self.tg_user.chat_id, notice, self.tg_user.notice_topic
        )


misskey_bot_map: dict[int, MisskeyBot] = {}


def get_misskey_bot(user_id: int) -> Optional[MisskeyBot]:
    return None if user_id not in misskey_bot_map else misskey_bot_map[user_id]


async def create_or_get_misskey_bot(user: User) -> MisskeyBot:
    if user.user_id not in misskey_bot_map:
        misskey_bot_map[user.user_id] = MisskeyBot(user)
    return misskey_bot_map[user.user_id]


async def run(user: User):
    misskey = await create_or_get_misskey_bot(user)
    try:
        logs.info(f"尝试启动 Misskey Bot WS 任务 {user.user_id}")
        await misskey.start(f"wss://{user.host}/streaming", user.token)
    except ClientConnectorError:
        await sleep(3)
        await run(user)


async def test_token(host: str, token: str) -> bool:
    try:
        logs.info(f"验证 Token {host} {token}")
        client = MisskeyClient(f"https://{host}", token)
        await client.http.login()
        await client.http.close_session()
        return True
    except Exception:
        return False


async def rerun_misskey_bot(user_id: int) -> bool:
    if misskey := get_misskey_bot(user_id):
        with contextlib.suppress(WebSocketNotConnected):
            await misskey.disconnect()
        misskey_bot_map.pop(user_id)
    user = await UserAction.get_user_if_ok(user_id)
    if not user:
        return False
    if not await test_token(user.host, user.token):
        await UserAction.set_user_status(user_id, TokenStatusEnum.INVALID_TOKEN)
        return False
    bot.loop.create_task(run(user))
    return True


async def init_misskey_bot():
    await sqlite.create_db_and_tables()
    count = 0
    for user in await UserAction.get_all_token_ok_users():
        if not await test_token(user.host, user.token):
            user.status = TokenStatusEnum.INVALID_TOKEN
            await UserAction.update_user(user)
            continue
        count += 1
        bot.loop.create_task(run(user))
    logs.info(f"初始化 Misskey Bot 完成，共启动 {count} 个 WS 任务")
