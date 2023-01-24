from scheduler import scheduler
from defs.announcement import get_unread_announcements


@scheduler.scheduled_job("interval", minutes=15, id="check_announcement")
async def announcement():
    data = await get_unread_announcements()
    for an in data:
        try:
            await an.send_notice()
        finally:
            await an.mark_as_read()
