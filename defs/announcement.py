from typing import TYPE_CHECKING

from mipac import Route

from init import bot
from misskey_init import MisskeyBot

if TYPE_CHECKING:
    from mipac.models.announcement import Announcement

announcement_template = """<b>Misskey Announcement</b>

<b>{0}</b>

{1}"""


class UnreadAnnouncement:
    def __init__(self, data: "Announcement", misskey_bot: MisskeyBot):
        self.misskey_bot = misskey_bot
        self.id = data.id
        self.title = data.title
        self.text = data.text
        self.is_read = data.is_read
        self.image_url = data.image_url
        self.created_at = data.created_at
        self.updated_at = data.updated_at

    async def send_notice(self):
        if not self.image_url:
            await bot.send_message(
                self.misskey_bot.tg_user.chat_id,
                announcement_template.format(
                    self.title,
                    self.text[:1000],
                ),
                reply_to_message_id=self.misskey_bot.tg_user.notice_topic,
            )
        else:
            await bot.send_photo(
                self.misskey_bot.tg_user.chat_id,
                self.image_url,
                caption=announcement_template.format(
                    self.title,
                    self.text[:1000],
                ),
                reply_to_message_id=self.misskey_bot.tg_user.notice_topic,
            )

    async def mark_as_read(self):
        data = {
            "announcementId": self.id,
        }
        await self.misskey_bot.core.http.request(
            Route("POST", "/api/i/read-announcement"),
            json=data,
            auth=True,
            lower=True,
        )
