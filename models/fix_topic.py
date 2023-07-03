import pyrogram


async def fix_topic(
    client: "pyrogram.Client",
    message: pyrogram.raw.base.Message,
    users: dict,
    chats: dict,
    is_scheduled: bool = False,
    replies: int = 1,
):
    parsed = await pyrogram.types.Message.old_parse(
        client, message, users, chats, is_scheduled, replies
    )  # noqa
    if isinstance(message, pyrogram.raw.types.Message):
        parsed.forum_topic = getattr(message.reply_to, "forum_topic", None)
        if (
            message.reply_to
            and parsed.forum_topic
            and not message.reply_to.reply_to_top_id
        ):
            parsed.reply_to_top_message_id = parsed.reply_to_message_id
            parsed.reply_to_message_id = None
            parsed.reply_to_message = None
    return parsed
