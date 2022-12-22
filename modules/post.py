from pyrogram import Client, filters
from pyrogram.types import Message

from misskey_init import misskey_bot


@Client.on_message(filters.incoming & filters.private & filters.text &
                   filters.command(["post"]))
async def post_command(_: Client, message: Message):
    """
        发送新贴
    """
    if text := message.text[6:].strip():
        await misskey_bot.core.api.note.action.send(text)
        await message.reply("发送成功", quote=True)
    else:
        return
