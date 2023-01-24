from mipa.ext import commands
from mipa.router import Router
from mipac import Note, NotificationFollow, NotificationFollowRequest, ChatMessage, NotificationAchievement

from defs.chat import send_chat_message
from defs.misskey import send_update
from defs.notice import send_user_followed, send_follow_request, send_follow_request_accept, send_achievement_earned
from glover import admin, topic_group_id, timeline_topic_id, notice_topic_id


class MisskeyBot(commands.Bot):
    def __init__(self):
        super().__init__()

    async def on_ready(self, ws):
        await Router(ws).connect_channel(["main", "home"])

    async def on_reconnect(self, ws):
        await Router(ws).connect_channel(["main", "home"])

    async def on_note(self, note: Note):
        await send_update(topic_group_id or admin, note, timeline_topic_id)

    async def on_user_followed(self, notice: NotificationFollow):
        await send_user_followed(notice)

    async def on_follow_request(self, notice: NotificationFollowRequest):
        await send_follow_request(notice)

    async def on_follow_request_accept(self, notice: NotificationFollowRequest):
        await send_follow_request_accept(notice)

    async def on_chat(self, message: ChatMessage):
        await send_chat_message(topic_group_id or admin, message, notice_topic_id)

    async def on_chat_unread_message(self, message: ChatMessage):
        await message.api.read()

    async def on_achievement_earned(self, notice: NotificationAchievement):
        await send_achievement_earned(notice)


misskey_bot = MisskeyBot()
