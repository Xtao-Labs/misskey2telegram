import contextlib
from asyncio import sleep, Lock
from typing import Optional, Union

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
    NoteDeleted,
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
from models.services.revoke import RevokeAction
from models.services.user import UserAction

from init import bot, logs, sqlite


class MisskeyBot(commands.Bot):
    def __init__(self, user: User):
        super().__init__()
        self.user_id: int = user.user_id
        self.instance_user_id: str = user.instance_user_id
        self.tg_user: User = user
        self.lock = Lock()

    async def when_start(self, ws):
        await Router(ws).connect_channel(["main", "home"])
        subs = await RevokeAction.get_all_subs(self.tg_user.user_id)
        for sub in subs:
            await Router(ws).capture_message(sub)

    async def on_ready(self, ws):
        await self.when_start(ws)
        logs.info(f"成功启动 Misskey Bot WS 任务 {self.user_id}")

    async def on_reconnect(self, ws):
        await self.when_start(ws)
        logs.info(f"成功重连 Misskey Bot WS 任务 {self.user_id}")

    def check_push(self, note: Note):
        if note.user_id != self.instance_user_id:
            return False
        if self.tg_user.push_chat_id == 0:
            return False
        if note.visibility in ["specified"]:
            return False
        if "nofwd" in note.tags:
            return False
        return True

    async def on_note(self, note: Note):
        logs.info(f"{self.tg_user.user_id} 收到新 note {note.id}")
        async with self.lock:
            if self.tg_user.chat_id != 0 and self.tg_user.timeline_topic != 0:
                msgs = await send_update(
                    self.tg_user.host,
                    self.tg_user.chat_id,
                    note,
                    self.tg_user.timeline_topic,
                    True,
                )
                await RevokeAction.push(self.tg_user.user_id, note.id, msgs)
            if self.check_push(note):
                msgs = await send_update(
                    self.tg_user.host, self.tg_user.push_chat_id, note, None, False
                )
                await RevokeAction.push(self.tg_user.user_id, note.id, msgs)
        logs.info(f"{self.tg_user.user_id} 处理 note {note.id} 完成")

    async def on_note_deleted(self, note: NoteDeleted):
        logs.info(f"{self.tg_user.user_id} 收到 note 删除 {note.note_id}")
        async with self.lock:
            await RevokeAction.process_delete_note(self.tg_user.user_id, note.note_id)
        logs.info(f"{self.tg_user.user_id} 处理 note 删除 {note.note_id} 完成")

    async def on_user_followed(self, notice: NotificationFollow):
        if self.tg_user.chat_id == 0 or self.tg_user.notice_topic == 0:
            return
        await send_user_followed(
            self.tg_user.chat_id, notice, self.tg_user.notice_topic
        )

    async def on_follow_request(self, notice: NotificationFollowRequest):
        if self.tg_user.chat_id == 0 or self.tg_user.notice_topic == 0:
            return
        await send_follow_request(
            self.tg_user.chat_id, notice, self.tg_user.notice_topic
        )

    async def on_follow_request_accept(self, notice: NotificationFollowRequest):
        if self.tg_user.chat_id == 0 or self.tg_user.notice_topic == 0:
            return
        await send_follow_request_accept(
            self.tg_user.chat_id, notice, self.tg_user.notice_topic
        )

    async def on_chat(self, message: ChatMessage):
        if self.tg_user.chat_id == 0 or self.tg_user.notice_topic == 0:
            return
        await send_chat_message(
            self.tg_user.host, self.tg_user.chat_id, message, self.tg_user.notice_topic
        )

    async def on_chat_unread_message(self, message: ChatMessage):
        if self.tg_user.chat_id == 0 or self.tg_user.notice_topic == 0:
            return
        await message.api.read()

    async def on_achievement_earned(self, notice: NotificationAchievement):
        if self.tg_user.chat_id == 0 or self.tg_user.notice_topic == 0:
            return
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
        await misskey.start(f"wss://{user.host}/streaming", user.token, log_level=None)
    except ClientConnectorError:
        logs.warning(f"Misskey Bot WS 任务 {user.user_id} 掉线重连")
        await sleep(3)
        bot.loop.create_task(run(user))


async def test_token(host: str, token: str) -> Union[str, bool]:
    try:
        logs.info(f"验证 Token {host} {token}")
        client = MisskeyClient(f"https://{host}", token, log_level=None)
        await client.http.login()
        me = await client.api.user.action.get_me()
        await client.http.close_session()
        return me.id
    except Exception:
        logs.warning(f"Token {host} {token} 验证失败")
        return False


async def rerun_misskey_bot(user_id: int) -> bool:
    if misskey := get_misskey_bot(user_id):
        with contextlib.suppress(WebSocketNotConnected):
            await misskey.disconnect()
        misskey_bot_map.pop(user_id)
    user = await UserAction.get_user_if_ok(user_id)
    if not user:
        return False
    mid = await test_token(user.host, user.token)
    if not mid:
        await UserAction.set_user_status(user_id, TokenStatusEnum.INVALID_TOKEN)
        return False
    user.instance_user_id = mid
    await UserAction.change_instance_user_id(user_id, mid)
    bot.loop.create_task(run(user))
    return True


async def init_misskey_bot():
    await sqlite.create_db_and_tables()
    count = 0
    for user in await UserAction.get_all_have_token_users():
        mid = await test_token(user.host, user.token)
        if not mid:
            logs.warning(f"{user.user_id} Token 失效")
            user.status = TokenStatusEnum.INVALID_TOKEN
            await UserAction.update_user(user)
            continue
        user.instance_user_id = mid
        count += 1
        bot.loop.create_task(run(user))
    logs.info(f"初始化 Misskey Bot 完成，共启动 {count} 个 WS 任务")
