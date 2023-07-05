import contextlib

from init import bot
from misskey_init import init_misskey_bot, misskey_bot_map
from models.services.scheduler import scheduler

bot.loop.create_task(init_misskey_bot())


@scheduler.scheduled_job("cron", hour=1, id="daily_status")
async def daily_status():
    for m_bot in misskey_bot_map.values():
        with contextlib.suppress(Exception):
            await m_bot.core.api.get_me()
