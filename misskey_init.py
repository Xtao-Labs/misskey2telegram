from mipa.ext import commands
from mipa.router import Router
from mipac import Note

from defs.misskey import send_update
from glover import admin


class MisskeyBot(commands.Bot):
    def __init__(self):
        super().__init__()

    async def on_ready(self, ws):
        await Router(ws).connect_channel(["main", "home"])

    async def on_reconnect(self, ws):
        await Router(ws).connect_channel(["main", "home"])

    async def on_chat(self, note: Note):
        await send_update(admin, note)


misskey_bot = MisskeyBot()
