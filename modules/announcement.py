from models.services.scheduler import scheduler
from defs.announcement import get_unread_announcements

from misskey_init import misskey_bot_map


@scheduler.scheduled_job("interval", minutes=15, id="check_announcement")
async def announcement():
    for bot in misskey_bot_map.values():
        if not bot.tg_user:
            continue
        data = await get_unread_announcements(bot)
        for an in data:
            try:
                await an.send_notice()
            finally:
                await an.mark_as_read()
