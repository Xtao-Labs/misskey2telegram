import contextlib
from os import remove
from typing import Tuple

from pyrogram import Client, filters, ContinuePropagation
from pyrogram.types import Message, CallbackQuery

from defs.confirm import ready_send, ReadySendMessage
from misskey_init import get_misskey_bot
from models.filters import notice_filter


def get_uid(message: Message) -> Tuple[bool, str]:
    group, user, uid = False, None, None
    if (
            not message.reply_to_message
            or not message.reply_to_message.reply_markup
    ):
        raise ContinuePropagation
    with contextlib.suppress(IndexError, AttributeError):
        url = message.reply_to_message.reply_markup.inline_keyboard[0][0].url
        user = url.split("/")[-1]
        if "/my/messaging/group/" in url:
            group = True
            uid = user
        else:
            uid = user.split("?cid=")[1]
    if not user:
        raise ContinuePropagation
    if not uid:
        raise ContinuePropagation
    return group, uid


@Client.on_message(filters.incoming & notice_filter & filters.text)
async def chat_command(_: Client, message: Message):
    group, uid = get_uid(message)
    text = message.text.strip()
    if text.startswith("@"):
        raise ContinuePropagation
    need_send = ReadySendMessage(text, group, uid)
    await need_send.confirm(message)


@Client.on_message(filters.incoming & notice_filter & filters.photo)
async def chat_photo_command(_: Client, message: Message):
    group, uid = get_uid(message)
    text = message.caption.strip() if message.caption else ""
    photo = await message.download()
    try:
        misskey_bot = get_misskey_bot(message.from_user.id)
        file_ = await misskey_bot.core.api.drive.file.action.upload_file(photo)
    except Exception as e:
        return await message.reply(f"上传文件失败：{e}", quote=True)
    need_send = ReadySendMessage(text, group, uid, file_.id)
    remove(photo)
    await need_send.confirm(message)


@Client.on_callback_query(filters.regex("^chat_send$") & notice_filter)
async def chat_send_callback(_: Client, callback_query: CallbackQuery):
    """
        发送
    """
    msg = callback_query.message
    if need_send := ready_send.get((msg.chat.id, msg.id), None):
        await need_send.send(msg, callback_query.from_user.id)
        return await callback_query.answer("发送成功")
    else:
        return await callback_query.answer("按钮已过期", show_alert=True)
