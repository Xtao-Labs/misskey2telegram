from typing import Optional

from mipac import ChatMessage, File
from mipac.models.lite import LiteUser
from pyrogram.errors import MediaEmpty
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from init import bot, request
from models.services.scheduler import add_delete_file_job, delete_file


def get_user_link(host: str, user: LiteUser) -> str:
    if user.host:
        return f"https://{host}/@{user.username}@{user.host}"
    return f"https://{host}/@{user.username}"


def get_source_link(host: str, message: ChatMessage) -> str:
    return (
        f"https://{host}/my/messaging/{message.user.username}?cid={message.user.id}"
        if not message.group and message.user
        else f"https://{host}/my/messaging/group/{message.group.id}"
    )


def gen_button(host: str, message: ChatMessage):
    author = get_user_link(host, message.user)
    source = get_source_link(host, message)
    first_line = [
        InlineKeyboardButton(text="Chat", url=source),
        InlineKeyboardButton(text="Author", url=author),
    ]
    return InlineKeyboardMarkup([first_line])


def get_content(host: str, message: ChatMessage) -> str:
    content = message.text or ""
    content = content[:768]
    user = f'<a href="{get_user_link(host, message.user)}">{message.user.nickname}</a>'
    if message.group:
        group = f'<a href="{get_source_link(host, message)}">{message.group.name}</a>'
        user += f" ( {group} )"
    return f"""<b>Misskey Message</b>

{user}： <code>{content}</code>"""


async def send_text(
    host: str, cid: int, message: ChatMessage, reply_to_message_id: int
):
    await bot.send_message(
        cid,
        get_content(host, message),
        reply_to_message_id=reply_to_message_id,
        reply_markup=gen_button(host, message),
        disable_web_page_preview=True,
    )


def deprecated_to_text(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except MediaEmpty:
            return await send_text(args[0], args[1], args[3], args[4])

    return wrapper


@deprecated_to_text
async def send_photo(
    host: str, cid: int, url: str, message: ChatMessage, reply_to_message_id: int
):
    if not url:
        return await send_text(host, cid, message, reply_to_message_id)
    await bot.send_photo(
        cid,
        url,
        reply_to_message_id=reply_to_message_id,
        caption=get_content(host, message),
        reply_markup=gen_button(host, message),
    )


@deprecated_to_text
async def send_video(
    host: str, cid: int, url: str, message: ChatMessage, reply_to_message_id: int
):
    if not url:
        return await send_text(host, cid, message, reply_to_message_id)
    await bot.send_video(
        cid,
        url,
        reply_to_message_id=reply_to_message_id,
        caption=get_content(host, message),
        reply_markup=gen_button(host, message),
    )


@deprecated_to_text
async def send_audio(
    host: str, cid: int, url: str, message: ChatMessage, reply_to_message_id: int
):
    if not url:
        return await send_text(host, cid, message, reply_to_message_id)
    await bot.send_audio(
        cid,
        url,
        reply_to_message_id=reply_to_message_id,
        caption=get_content(host, message),
        reply_markup=gen_button(host, message),
    )


async def fetch_document(file: File) -> Optional[str]:
    file_name = f"downloads/{file.name}"
    file_url = file.url
    if file.size > 10 * 1024 * 1024:
        return file_url
    if not file_url:
        return file_url
    req = await request.get(file_url)
    if req.status_code != 200:
        return file_url
    with open(file_name, "wb") as f:
        f.write(req.content)
    add_delete_file_job(file_name)
    return file_name


@deprecated_to_text
async def send_document(
    host: str, cid: int, file: File, message: ChatMessage, reply_to_message_id: int
):
    file = await fetch_document(file)
    if not file:
        return await send_text(host, cid, message, reply_to_message_id)
    await bot.send_document(
        cid,
        file,
        reply_to_message_id=reply_to_message_id,
        caption=get_content(host, message),
        reply_markup=gen_button(host, message),
    )
    await delete_file(file)


async def send_chat_message(host: str, cid: int, message: ChatMessage, topic_id: int):
    if not message.file:
        return await send_text(host, cid, message, topic_id)
    file_url = message.file.url
    file_type = message.file.type
    if file_type.startswith("image"):
        await send_photo(host, cid, file_url, message, topic_id)
    elif file_type.startswith("video"):
        await send_video(host, cid, file_url, message, topic_id)
    elif file_type.startswith("audio"):
        await send_audio(host, cid, file_url, message, topic_id)
    else:
        await send_document(host, cid, message.file, message, topic_id)
