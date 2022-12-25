import contextlib
from os import remove

from pyrogram import Client, filters, ContinuePropagation
from pyrogram.types import Message, CallbackQuery

from defs.confirm import ReadySend, ready_send
from glover import admin
from misskey_init import misskey_bot


@Client.on_message(filters.incoming & filters.private & filters.text & filters.user(admin))
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


@Client.on_message(filters.incoming & filters.private & filters.photo & filters.user(admin))
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
        file_ = await misskey_bot.core.api.drive.file.action.upload_file(photo)
    except Exception as e:
        return await message.reply(f"上传文件失败：{e}", quote=True)
    need_send = ReadySend(text, note_id, [file_])
    remove(photo)
    await need_send.confirm(message)


@Client.on_callback_query(filters.regex("^send$"))
async def send_callback(_: Client, callback_query: CallbackQuery):
    """
        发送
    """
    if need_send := ready_send.get(callback_query.message.id, None):
        await need_send.send(callback_query.message)
        return await callback_query.answer("发送成功")
    else:
        return await callback_query.answer("按钮已过期", show_alert=True)


@Client.on_callback_query(filters.regex("^delete$"))
async def delete_callback(_: Client, callback_query: CallbackQuery):
    """
        删除
    """
    if not (need_send := callback_query.message):
        return await callback_query.answer("按钮已过期", show_alert=True)
    await need_send.delete()
    if ready_send.get(callback_query.message.id, None):
        del ready_send[callback_query.message.id]
    return await callback_query.answer("已删除")
