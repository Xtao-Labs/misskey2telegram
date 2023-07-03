import pyrogram
from pyrogram.types import Update, Message, CallbackQuery

from misskey_init import get_misskey_bot


def private_filter(filter_type: str = "timeline"):
    async def func(_, __, update: Update):
        if isinstance(update, Message):
            user_id = update.from_user.id if update.from_user else None
            topic_id = update.reply_to_top_message_id
        elif isinstance(update, CallbackQuery):
            user_id = update.from_user.id if update.from_user else None
            topic_id = update.message.reply_to_top_message_id
        else:
            return False
        if not user_id:
            return False
        misskey_bot = get_misskey_bot(user_id)
        if not misskey_bot:
            return False
        if not misskey_bot.tg_user:
            return False
        if filter_type == "timeline" and misskey_bot.tg_user.timeline_topic == topic_id:
            return True
        elif filter_type == "notice" and misskey_bot.tg_user.notice_topic == topic_id:
            return True
        else:
            return False

    return pyrogram.filters.create(func)


timeline_filter = private_filter("timeline")
notice_filter = private_filter("notice")
