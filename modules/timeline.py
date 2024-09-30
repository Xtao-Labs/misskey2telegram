import contextlib
from datetime import datetime, timedelta

from typing import TYPE_CHECKING

from pyrogram import Client, filters

from defs.announcement import UnreadAnnouncement
from init import bot
from misskey_init import init_misskey_bot, misskey_bot_map
from models.services.scheduler import scheduler

if TYPE_CHECKING:
    from mipac import MeDetailed
    from misskey_init import MisskeyBot

bot.loop.create_task(init_misskey_bot())


async def get_unread_announcements(me: "MeDetailed", m_bot: "MisskeyBot"):
    if not me:
        return
    un = [UnreadAnnouncement(an, m_bot) for an in me.unread_announcements]
    for an in un:
        try:
            await an.send_notice()
        finally:
            await an.mark_as_read()


@scheduler.scheduled_job("cron", minute="*/30", id="daily_status")
@scheduler.scheduled_job("date", run_date=datetime.now() + timedelta(minutes=1), id="daily_status_start")
async def daily_status():
    for m_bot in misskey_bot_map.values():
        with contextlib.suppress(Exception):
            me = await m_bot.core.api.get_me()
            me._MeDetailedOnly__client = me._client
            await get_unread_announcements(me, m_bot)


@Client.on_message(filters.incoming & filters.private & filters.command(["daily_status"]))
async def daily_status_command(_: Client, __):
    await daily_status()
