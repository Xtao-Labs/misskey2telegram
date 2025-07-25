import contextlib
from asyncio import sleep, Lock
from typing import Optional, Union

from aiohttp import ClientConnectorError
from mipa.exception import WebSocketNotConnected
from mipa.ext import commands
from mipac import (
    Note,
    NotificationFollow,
    NotificationFollowRequest,
    NotificationAchievement,
    NoteDeleted,
    NotificationNote,
    Route,
)
from mipac.client import Client as MisskeyClient
from pyrogram.errors import ChatWriteForbidden
from pyrogram.types import Message

from defs.misskey import send_update, send_notice
from defs.notice import (
    send_user_followed,
    send_follow_request,
    send_follow_request_accept,
    send_achievement_earned,
    send_note_mention,
)

from models.models.user import User, TokenStatusEnum
from models.models.user_config import UserConfig
from models.services.no_repeat_renote import NoRepeatRenoteAction
from models.services.revoke import RevokeAction
from models.services.user import UserAction

from init import bot, logs, sqlite
from models.services.user_config import UserConfigAction


class MisskeyBot(commands.Bot):
    def __init__(self, user: User, user_config: UserConfig):
        super().__init__()
        self._BotBase__on_error = self.__on_error
        self.user_id: int = user.user_id
        self.instance_user_id: str = user.instance_user_id
        self.tg_user: User = user
        self.user_config: UserConfig = user_config
        self.lock = Lock()

    async def fetch_offline_notes(self):
        logs.info(f"{self.tg_user.user_id} 开始获取最近十条时间线")
        data = {"withReplies": False, "limit": 10}
        data = await self.core.http.request(
            Route("POST", "/api/notes/timeline"), auth=True, json=data
        )
        for note in (Note(raw_note=note, client=self.client) for note in data):
            await self.process_note(note, notice=False)
        logs.info(f"{self.tg_user.user_id} 处理完成最近十条时间线")

    async def when_start(self, _):
        await self.router.connect_channel(["main", "home"])
        await self.fetch_offline_notes()
        subs = await RevokeAction.get_all_subs(self.tg_user.user_id)
        for sub in subs:
            await self.router.capture_message(sub)

    async def on_ready(self, ws):
        try:
            await self.when_start(ws)
            logs.info(f"成功启动 Misskey Bot WS 任务 {self.user_id}")
        except ConnectionResetError:
            """在预启动时，WS 已被关闭"""

    async def on_reconnect(self, ws):
        try:
            await self.when_start(ws)
            logs.info(f"成功重连 Misskey Bot WS 任务 {self.user_id}")
        except ConnectionResetError:
            """在预启动时，WS 已被关闭"""

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

    async def send_update(
        self, note: Note, send_type: str
    ) -> Message | list[Message] | None:
        cid = (
            self.tg_user.chat_id
            if send_type == "timeline"
            else self.tg_user.push_chat_id
        )
        try:
            if send_type == "timeline":
                return await send_update(
                    self.tg_user.host,
                    self.tg_user.chat_id,
                    note,
                    self.tg_user.timeline_topic,
                    True,
                    spoiler=self.user_config and self.user_config.timeline_spoiler,
                )
            else:
                return await send_update(
                    self.tg_user.host,
                    self.tg_user.push_chat_id,
                    note,
                    None,
                    False,
                    spoiler=self.user_config and self.user_config.push_spoiler,
                )
        except ChatWriteForbidden:
            logs.warning(f"{self.tg_user.user_id} 无法向 {send_type} {cid} 发送消息")
            if send_type == "timeline":
                await UserAction.change_user_group_id(self.tg_user.user_id, 0)
            else:
                await UserAction.change_user_push(self.tg_user.user_id, 0)
            await send_notice(
                self.tg_user.user_id, f"无法向 {cid} 发送消息，已停止推送"
            )
            await rerun_misskey_bot(self.tg_user.user_id)

    async def process_note(self, note: Note, notice: bool = True):
        async with self.lock:
            try:
                if await NoRepeatRenoteAction.check(self.tg_user.user_id, note):
                    if self.tg_user.chat_id != 0 and self.tg_user.timeline_topic != 0:
                        msgs = await self.send_update(note, "timeline")
                        await RevokeAction.push(self.tg_user.user_id, note.id, msgs)
                    if self.check_push(note):
                        msgs = await self.send_update(note, "push")
                        await RevokeAction.push(self.tg_user.user_id, note.id, msgs)
                elif notice:
                    logs.info(f"{self.tg_user.user_id} 跳过重复转发 note {note.id}")
                await NoRepeatRenoteAction.set(self.tg_user.user_id, note)
            except Exception:
                logs.exception(
                    f"{self.tg_user.user_id} 处理 note {self.tg_user.host}/notes/{note.id} 发生异常"
                )

    async def on_note(self, note: Note):
        logs.info(f"{self.tg_user.user_id} 收到新 note {note.id}")
        await self.process_note(note)
        logs.info(f"{self.tg_user.user_id} 处理 note {note.id} 完成")

    async def on_note_deleted(self, note: NoteDeleted):
        logs.info(f"{self.tg_user.user_id} 收到 note 删除 {note.note_id}")
        async with self.lock:
            await RevokeAction.process_delete_note(self.tg_user.user_id, note.note_id)
        logs.info(f"{self.tg_user.user_id} 处理 note 删除 {note.note_id} 完成")

    async def on_user_followed(self, notice: NotificationFollow):
        if self.tg_user.chat_id != 0 and self.tg_user.notice_topic != 0:
            await send_user_followed(
                self.tg_user.host,
                self.tg_user.chat_id,
                notice,
                self.tg_user.notice_topic,
            )

    async def on_follow_request(self, notice: NotificationFollowRequest):
        if self.tg_user.chat_id != 0 and self.tg_user.notice_topic != 0:
            await send_follow_request(
                self.tg_user.host,
                self.tg_user.chat_id,
                notice,
                self.tg_user.notice_topic,
            )

    async def on_follow_request_accept(self, notice: NotificationFollowRequest):
        if self.tg_user.chat_id != 0 and self.tg_user.notice_topic != 0:
            await send_follow_request_accept(
                self.tg_user.host,
                self.tg_user.chat_id,
                notice,
                self.tg_user.notice_topic,
            )

    async def on_achievement_earned(self, notice: NotificationAchievement):
        if self.tg_user.chat_id != 0 and self.tg_user.notice_topic != 0:
            await send_achievement_earned(
                self.tg_user.host,
                self.tg_user.chat_id,
                notice,
                self.tg_user.notice_topic,
            )

    @staticmethod
    def ignore_mention(note: NotificationNote) -> bool:
        new_note = note.note
        if (
            len(new_note.mentions) >= 3
            and new_note.user.username
            and len(new_note.user.username) == 10
        ):
            return True
        return False

    async def on_mention(self, notice: NotificationNote):
        if self.tg_user.chat_id != 0 and self.tg_user.notice_topic != 0:
            if self.ignore_mention(notice):
                logs.warning(f"{self.tg_user.user_id} 遇到 spam 轰炸 {notice.note.id}")
                return
            msg = await send_note_mention(
                self.tg_user.host,
                self.tg_user.chat_id,
                notice,
                self.tg_user.notice_topic,
            )
            await RevokeAction.push_extend(self.tg_user.user_id, notice.note.id, msg)
            await self.router.capture_message(notice.note.id)

    @staticmethod
    async def __on_error(event_method: str) -> None:
        logs.exception(f"MisskeyBot 执行 {event_method} 出错", exc_info=True)


misskey_bot_map: dict[int, MisskeyBot] = {}


def get_misskey_bot(user_id: int) -> Optional[MisskeyBot]:
    return None if user_id not in misskey_bot_map else misskey_bot_map[user_id]


async def create_or_get_misskey_bot(user: User, user_config: UserConfig) -> MisskeyBot:
    if user.user_id not in misskey_bot_map:
        misskey_bot_map[user.user_id] = MisskeyBot(user, user_config)
    return misskey_bot_map[user.user_id]


async def run(user: User):
    user_config = await UserConfigAction.get_user_config_by_id(user.user_id)
    misskey = await create_or_get_misskey_bot(user, user_config)
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
