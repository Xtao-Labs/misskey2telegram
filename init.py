from logging import getLogger, INFO, ERROR, StreamHandler, basicConfig

import httpx
import pyrogram

from fix_topic import fix_topic
from glover import api_id, api_hash, ipv6, timeline_topic_id, notice_topic_id
from scheduler import scheduler

# Enable logging
logs = getLogger("misskey2telegram")
logging_handler = StreamHandler()
root_logger = getLogger("pyrogram")
root_logger.setLevel(ERROR)
root_logger.addHandler(logging_handler)
basicConfig(level=INFO)
logs.setLevel(INFO)

if not scheduler.running:
    scheduler.start()
# Init client
bot = pyrogram.Client("bot", api_id=api_id, api_hash=api_hash, ipv6=ipv6, plugins=dict(root="modules"))
# fix topic group
setattr(pyrogram.types.Message, "old_parse", getattr(pyrogram.types.Message, "_parse"))
setattr(pyrogram.types.Message, "_parse", fix_topic)


def private_filter(topic_id: int = 0):
    if not topic_id:
        return pyrogram.filters.private

    async def func(_, __, m: pyrogram.types.Message):
        if m.chat.type == pyrogram.enums.ChatType.PRIVATE:
            return True
        elif m.reply_to_top_message_id == topic_id:
            return True
        else:
            return False

    return pyrogram.filters.create(func)


timeline_filter = private_filter(timeline_topic_id)
notice_filter = private_filter(notice_topic_id)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.72 Safari/537.36"
}
request = httpx.AsyncClient(timeout=60.0, headers=headers)
