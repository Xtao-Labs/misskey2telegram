import contextlib
from os import remove

from pyrogram import Client, filters, ContinuePropagation
from pyrogram.types import Message, CallbackQuery

from defs.confirm import ReadySend, ready_send
from misskey_init import get_misskey_bot
from models.filters import timeline_filter


@Client.on_message(filters.incoming & timeline_filter & filters.text)
async def post_command(_: Client, message: Message):
    """
    发送新贴或者回复
    """
    note_id = None
    if message.reply_to_message and message.reply_to_message.reply_markup:
        with contextlib.suppress(IndexError, AttributeError):
            url = message.reply_to_message.reply_markup.inline_keyboard[0][0].url
            note_id = url.split("/")[-1]
    text = message.text.strip()
    if text.startswith("@"):
        raise ContinuePropagation
    need_send = ReadySend(text, note_id)
    await need_send.confirm(message)


@Client.on_message(filters.incoming & timeline_filter & filters.photo)
async def post_photo_command(_: Client, message: Message):
    """
    发送新贴或者回复
    """
    note_id = None
    if message.reply_to_message and message.reply_to_message.reply_markup:
        with contextlib.suppress(IndexError, AttributeError):
            url = message.reply_to_message.reply_markup.inline_keyboard[0][0].url
            note_id = url.split("/")[-1]
    text = message.caption.strip() if message.caption else ""
    photo = await message.download()
    try:
        misskey_bot = get_misskey_bot(message.from_user.id)
        file_ = await misskey_bot.core.api.drive.file.action.upload_file(photo)
    except Exception as e:
        return await message.reply(f"上传文件失败：{e}", quote=True)
    need_send = ReadySend(text, note_id, [file_])
    remove(photo)
    await need_send.confirm(message)


@Client.on_callback_query(filters.regex("^send$") & timeline_filter)
async def send_callback(_: Client, callback_query: CallbackQuery):
    """
    发送
    """
    msg = callback_query.message
    if need_send := ready_send.get((msg.chat.id, msg.id), None):
        await need_send.send(msg, callback_query.from_user.id)
        return await callback_query.answer("发送成功")
    else:
        return await callback_query.answer("按钮已过期", show_alert=True)


@Client.on_callback_query(filters.regex("^delete$") & timeline_filter)
async def delete_callback(_: Client, callback_query: CallbackQuery):
    """
    删除
    """
    if not (need_send := callback_query.message):
        return await callback_query.answer("按钮已过期", show_alert=True)
    await need_send.delete()
    msg = callback_query.message
    if ready_send.get((msg.chat.id, msg.id), None):
        del ready_send[(msg.chat.id, msg.id)]
    return await callback_query.answer("已删除")
