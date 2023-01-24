from datetime import datetime
from typing import Optional

from mipac import Route

from glover import topic_group_id, admin, notice_topic_id
from init import bot
from misskey_init import misskey_bot

announcement_template = """<b>Misskey Announcement</b>

<b>{0}</b>

{1}"""


class Announcement:
    def __init__(self, data):
        self.id = data["id"]
        self.title = data["title"]
        self.text = data["text"]
        self.is_read = data["is_read"]
        self.image_url = data["image_url"]
        self._created_at = data["created_at"]
        self._updated_at = data["updated_at"]

    @property
    def created_at(self) -> datetime:
        return datetime.strptime(self._created_at, "%Y-%m-%dT%H:%M:%S.%fZ")

    @property
    def updated_at(self) -> Optional[datetime]:
        return datetime.strptime(self._updated_at, "%Y-%m-%dT%H:%M:%S.%fZ") if self._updated_at else None

    async def send_notice(self):
        if not self.image_url:
            await bot.send_message(
                topic_group_id or admin,
                announcement_template.format(
                    self.title,
                    self.text[:1000],
                ),
                reply_to_message_id=notice_topic_id,
            )
        else:
            await bot.send_photo(
                topic_group_id or admin,
                self.image_url,
                caption=announcement_template.format(
                    self.title,
                    self.text[:1000],
                ),
                reply_to_message_id=notice_topic_id,
            )

    async def mark_as_read(self):
        data = {
            "announcementId": self.id,
        }
        await misskey_bot.core.http.request(
            Route("POST", "/api/i/read-announcement"),
            json=data, auth=True, lower=True,
        )


async def get_unread_announcements():
    data = {
        "limit": 10,
        "withUnreads": True,
    }
    req = await misskey_bot.core.http.request(
        Route("POST", "/api/announcements"),
        json=data, auth=True, lower=True,
    )
    return [Announcement(i) for i in req]
