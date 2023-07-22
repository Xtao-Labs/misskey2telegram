import contextlib
import re
from datetime import datetime, timedelta, timezone
from typing import Optional, List

import aiofiles as aiofiles
from mipac import Note, File
from mipac.models.lite import LiteUser
from pyrogram.enums import ParseMode
from pyrogram.errors import MediaEmpty
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaDocument,
    InputMediaAudio,
    Message,
)

from defs.image import webp_to_png
from init import bot, request
from models.services.scheduler import add_delete_file_job, delete_file

at_parse = re.compile(r"(?<!\S)@(\S+)\s")


def get_note_url(host: str, note: Note) -> str:
    return f"https://{host}/notes/{note.id}"


def gen_button(host: str, note: Note, author: str, show_second: bool):
    source = get_note_url(host, note)
    reply_source = get_note_url(host, note.reply) if note.reply else None
    renote_id = note.renote_id or note.id
    if reply_source:
        first_line = [
            InlineKeyboardButton(text="Source", url=source),
            InlineKeyboardButton(text="RSource", url=reply_source),
            InlineKeyboardButton(text="Author", url=author),
        ]
    else:
        first_line = [
            InlineKeyboardButton(text="Source", url=source),
            InlineKeyboardButton(text="Author", url=author),
        ]
    second_line = [
        InlineKeyboardButton(text="🔁", callback_data=f"renote:{renote_id}"),
        InlineKeyboardButton(text="❤️", callback_data=f"react:{renote_id}:love"),
        InlineKeyboardButton(text="🌐", callback_data=f"translate:{renote_id}"),
    ]
    return (
        InlineKeyboardMarkup([first_line, second_line])
        if show_second
        else InlineKeyboardMarkup([first_line])
    )


def get_user_link(host: str, user: LiteUser) -> str:
    if user.host:
        return f"https://{host}/@{user.username}@{user.host}"
    return f"https://{host}/@{user.username}"


def get_user_alink(host: str, user: LiteUser) -> str:
    return '<a href="{}">{}</a>'.format(
        get_user_link(host, user), user.nickname or f"@{user.username}"
    )


def get_post_time(date: datetime) -> str:
    try:
        date = date + timedelta(hours=8)
        return date.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def format_at(host: str, content: str) -> str:
    replaced = rf'<a href="https://{host}/@\1">@\1</a> '
    return at_parse.sub(replaced, content)


def get_content(host: str, note: Note) -> str:
    content = note.content or ""
    action = "发表"
    origin = ""
    show_note = note
    if note.renote:
        show_note = note.renote
        action = "转推"
        content = note.renote.content or content
        origin = (
            f"\n{get_user_alink(host, note.renote.author)} "
            f"发表于 {get_post_time(note.renote.created_at)}"
        )
    if note.reply:
        show_note = note.reply
        action = "回复"
        if note.reply.content:
            content = f"> {note.reply.content}\n\n{content}"
        origin = (
            f"\n{get_user_alink(host, note.reply.author)} "
            f"发表于 {get_post_time(note.reply.created_at)}"
        )
    content = format_at(host, content[:768])
    return f"""<b>Misskey Timeline Update</b>

{content}

{get_user_alink(host, note.author)} {action}于 {get_post_time(note.created_at)}{origin}
点赞: {sum(show_note.reactions.values())} | 回复: {show_note.replies_count} | 转发: {show_note.renote_count}"""


async def send_text(
    host: str, cid: int, note: Note, reply_to_message_id: int, show_second: bool
) -> Message:
    return await bot.send_message(
        cid,
        get_content(host, note),
        reply_to_message_id=reply_to_message_id,
        reply_markup=gen_button(
            host, note, get_user_link(host, note.author), show_second
        ),
        disable_web_page_preview=True,
    )


def deprecated_to_text(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except MediaEmpty:
            return await send_text(args[0], args[1], args[3], args[4], args[5])

    return wrapper


async def fetch_document(file: File) -> Optional[str]:
    file_name = "downloads/" + file.name
    file_url = file.url
    if file.size > 10 * 1024 * 1024:
        return file_url
    if not file_url:
        return file_url
    req = await request.get(file_url)
    if req.status_code != 200:
        return file_url
    if file_name.lower().endswith(".webp"):
        file_name = file_name[:-5] + ".jpg"
        io = webp_to_png(req.content).getvalue()
    else:
        io = req.content
    async with aiofiles.open(file_name, "wb") as f:
        await f.write(io)
    add_delete_file_job(file_name)
    return file_name


@deprecated_to_text
async def send_photo(
    host: str,
    cid: int,
    url: str,
    note: Note,
    reply_to_message_id: int,
    show_second: bool,
) -> Message:
    if not url:
        return await send_text(host, cid, note, reply_to_message_id, show_second)
    return await bot.send_photo(
        cid,
        url,
        reply_to_message_id=reply_to_message_id,
        caption=get_content(host, note),
        reply_markup=gen_button(
            host, note, get_user_link(host, note.author), show_second
        ),
    )


@deprecated_to_text
async def send_video(
    host: str,
    cid: int,
    url: str,
    note: Note,
    reply_to_message_id: int,
    show_second: bool,
) -> Message:
    if not url:
        return await send_text(host, cid, note, reply_to_message_id, show_second)
    return await bot.send_video(
        cid,
        url,
        reply_to_message_id=reply_to_message_id,
        caption=get_content(host, note),
        reply_markup=gen_button(
            host, note, get_user_link(host, note.author), show_second
        ),
    )


@deprecated_to_text
async def send_audio(
    host: str,
    cid: int,
    url: str,
    note: Note,
    reply_to_message_id: int,
    show_second: bool,
) -> Message:
    if not url:
        return await send_text(host, cid, note, reply_to_message_id, show_second)
    return await bot.send_audio(
        cid,
        url,
        reply_to_message_id=reply_to_message_id,
        caption=get_content(host, note),
        reply_markup=gen_button(
            host, note, get_user_link(host, note.author), show_second
        ),
    )


@deprecated_to_text
async def send_document(
    host: str,
    cid: int,
    url: str,
    note: Note,
    reply_to_message_id: int,
    show_second: bool,
) -> Message:
    if not url:
        return await send_text(host, cid, note, reply_to_message_id, show_second)
    msg = await bot.send_document(
        cid,
        url,
        reply_to_message_id=reply_to_message_id,
        caption=get_content(host, note),
        reply_markup=gen_button(
            host, note, get_user_link(host, note.author), show_second
        ),
    )
    with contextlib.suppress(Exception):
        await delete_file(url)
    return msg


async def get_media_group(files: list[File]) -> list:
    media_lists = []
    for file_ in files:
        file_url = file_.url
        if not file_url:
            continue
        file_type = file_.type
        if file_type.startswith("image"):
            media_lists.append(
                InputMediaPhoto(
                    file_url,
                    parse_mode=ParseMode.HTML,
                )
            )
        elif file_type.startswith("video"):
            media_lists.append(
                InputMediaVideo(
                    file_url,
                    parse_mode=ParseMode.HTML,
                )
            )
        elif file_type.startswith("audio"):
            media_lists.append(
                InputMediaAudio(
                    file_url,
                    parse_mode=ParseMode.HTML,
                )
            )
        elif file := await fetch_document(file_):
            media_lists.append(
                InputMediaDocument(
                    file,
                    parse_mode=ParseMode.HTML,
                )
            )
    return media_lists


async def send_group(
    host: str,
    cid: int,
    files: list[File],
    note: Note,
    reply_to_message_id: int,
    show_second: bool,
) -> List[Message]:
    groups = await get_media_group(files)
    if len(groups) == 0:
        return [await send_text(host, cid, note, reply_to_message_id, show_second)]
    photo, video, audio, document, msg = [], [], [], [], None
    for i in groups:
        if isinstance(i, InputMediaPhoto):
            photo.append(i)
        elif isinstance(i, InputMediaVideo):
            video.append(i)
        elif isinstance(i, InputMediaAudio):
            audio.append(i)
        elif isinstance(i, InputMediaDocument):
            document.append(i)
    if video and (audio or document):
        msg = await bot.send_media_group(
            cid,
            video,
            reply_to_message_id=reply_to_message_id,
        )
        if audio:
            msg = await bot.send_media_group(
                cid,
                audio,
                reply_to_message_id=reply_to_message_id,
            )
        elif document:
            msg = await bot.send_media_group(
                cid,
                document,
                reply_to_message_id=reply_to_message_id,
            )
    elif audio and (photo or document):
        msg = await bot.send_media_group(
            cid,
            audio,
            reply_to_message_id=reply_to_message_id,
        )
        if photo:
            msg = await bot.send_media_group(
                cid,
                photo,
                reply_to_message_id=reply_to_message_id,
            )
        elif document:
            msg = await bot.send_media_group(
                cid,
                document,
                reply_to_message_id=reply_to_message_id,
            )
    else:
        msg = await bot.send_media_group(
            cid,
            groups,
            reply_to_message_id=reply_to_message_id,
        )
    if msg and isinstance(msg, list):
        msg_ids = msg
    elif msg:
        msg_ids = [msg]
    else:
        msg_ids = []
    tmsg = await send_text(
        host, cid, note, msg_ids[0].id if msg_ids else None, show_second
    )
    if tmsg:
        msg_ids.append(tmsg)
    return msg_ids


async def send_update(
    host: str, cid: int, note: Note, topic_id: Optional[int], show_second: bool
) -> List[Message]:
    files = list(note.files)
    if note.reply:
        files.extend(iter(note.reply.files))
    if note.renote:
        files.extend(iter(note.renote.files))
    match len(files):
        case 0:
            return [await send_text(host, cid, note, topic_id, show_second)]
        case 1:
            file = files[0]
            file_type = file.type
            url = await fetch_document(file)
            if file_type.startswith("image"):
                return [await send_photo(host, cid, url, note, topic_id, show_second)]
            elif file_type.startswith("video"):
                return [await send_video(host, cid, url, note, topic_id, show_second)]
            elif file_type.startswith("audio"):
                return [await send_audio(host, cid, url, note, topic_id, show_second)]
            else:
                return [await send_document(host, cid, url, note, topic_id, show_second)]
        case _:
            return await send_group(host, cid, files, note, topic_id, show_second)
