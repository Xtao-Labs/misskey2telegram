from mipa.ext import commands
from mipa.router import Router
from mipac import Note, NotificationFollow, NotificationFollowRequest

from defs.misskey import send_update
from defs.notice import send_user_followed, send_follow_request, send_follow_request_accept
from glover import admin


class MisskeyBot(commands.Bot):
    def __init__(self):
        super().__init__()

    async def on_ready(self, ws):
        await Router(ws).connect_channel(["main", "home"])

    async def on_reconnect(self, ws):
        await Router(ws).connect_channel(["main", "home"])

    async def on_note(self, note: Note):
        await send_update(admin, note)

    async def on_user_followed(self, notice: NotificationFollow):
        await send_user_followed(notice)

    async def on_follow_request(self, notice: NotificationFollowRequest):
        await send_follow_request(notice)

    async def on_follow_request_accept(self, notice: NotificationFollowRequest):
        await send_follow_request_accept(notice)


misskey_bot = MisskeyBot()
