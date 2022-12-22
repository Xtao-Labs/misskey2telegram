from pyrogram import Client, filters
from pyrogram.types import Message

from misskey_init import misskey_bot


@Client.on_message(filters.incoming & filters.private & filters.text & filters.reply)
async def reply_command(_: Client, message: Message):
    """
        回复
    """
    if not message.reply_to_message:
        return
    if not message.reply_to_message.reply_markup:
        return
    if not message.text:
        return
    try:
        url = message.reply_to_message.reply_markup.inline_keyboard[0][0].url
        note_id = url.split("/")[-1]
    except (IndexError, AttributeError):
        return
    await misskey_bot.core.api.note.action.reply(message.text, reply_id=note_id)
    await message.reply("回复成功", quote=True)
