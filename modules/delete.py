from mipac.errors import APIError, NoSuchNoteError
from pyrogram import Client, filters
from pyrogram.types import Message

from misskey_init import get_misskey_bot
from models.filters import timeline_filter


@Client.on_message(filters.incoming & filters.text & filters.reply & timeline_filter)
async def delete_command(_: Client, message: Message):
    """
        删除
    """
    if not message.reply_to_message:
        return
    if not message.reply_to_message.reply_markup:
        return
    try:
        url = message.reply_to_message.reply_markup.inline_keyboard[0][0].url
        note_id = url.split("/")[-1]
    except (IndexError, AttributeError):
        return
    try:
        misskey_bot = get_misskey_bot(message.from_user.id)
        await misskey_bot.core.api.note.action.delete(note_id)
        await message.reply("删除成功", quote=True)
    except NoSuchNoteError:
        await message.reply("该嘟文不存在", quote=True)
    except APIError as e:
        await message.reply(f"删除失败 {e}", quote=True)
