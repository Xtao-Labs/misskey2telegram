from datetime import datetime, timedelta, timezone
from typing import Optional

from mipac import Note
from mipac.models.lite import LiteUser
from mipac.types import IDriveFile
from pyrogram.enums import ParseMode
from pyrogram.errors import MediaEmpty

from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaDocument,
    InputMediaAudio,
)

from init import bot, request
from models.services.scheduler import add_delete_file_job, delete_file


def get_note_url(host: str, note: Note) -> str:
    return f"https://{host}/notes/{note.id}"


def gen_button(host: str, note: Note, author: str):
    source = get_note_url(host, note)
    reply_source = get_note_url(host, note.reply) if note.reply else None
    renote_id = note.renote_id if note.reply else note.id
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
    return InlineKeyboardMarkup([first_line, second_line])


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
    content = content[:768]
    return f"""<b>Misskey Timeline Update</b>

<code>{content}</code>

{get_user_alink(host, note.author)} {action}于 {get_post_time(note.created_at)}{origin}
点赞: {sum(show_note.reactions.values())} | 回复: {show_note.replies_count} | 转发: {show_note.renote_count}"""


async def send_text(host: str, cid: int, note: Note, reply_to_message_id: int):
    await bot.send_message(
        cid,
        get_content(host, note),
        reply_to_message_id=reply_to_message_id,
        reply_markup=gen_button(host, note, get_user_link(host, note.author)),
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
    host: str, cid: int, url: str, note: Note, reply_to_message_id: int
):
    if not url:
        return await send_text(host, cid, note, reply_to_message_id)
    await bot.send_photo(
        cid,
        url,
        reply_to_message_id=reply_to_message_id,
        caption=get_content(host, note),
        reply_markup=gen_button(host, note, get_user_link(host, note.author)),
    )


@deprecated_to_text
async def send_video(
    host: str, cid: int, url: str, note: Note, reply_to_message_id: int
):
    if not url:
        return await send_text(host, cid, note, reply_to_message_id)
    await bot.send_video(
        cid,
        url,
        reply_to_message_id=reply_to_message_id,
        caption=get_content(host, note),
        reply_markup=gen_button(host, note, get_user_link(host, note.author)),
    )


@deprecated_to_text
async def send_audio(
    host: str, cid: int, url: str, note: Note, reply_to_message_id: int
):
    if not url:
        return await send_text(host, cid, note, reply_to_message_id)
    await bot.send_audio(
        cid,
        url,
        reply_to_message_id=reply_to_message_id,
        caption=get_content(host, note),
        reply_markup=gen_button(host, note, get_user_link(host, note.author)),
    )


async def fetch_document(file: IDriveFile) -> Optional[str]:
    file_name = "downloads/" + file.get("name", "file")
    file_url = file.get("url", None)
    if file.get("size", 0) > 10 * 1024 * 1024:
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
    host: str, cid: int, file: IDriveFile, note: Note, reply_to_message_id: int
):
    file = await fetch_document(file)
    if not file:
        return await send_text(host, cid, note, reply_to_message_id)
    await bot.send_document(
        cid,
        file,
        reply_to_message_id=reply_to_message_id,
        caption=get_content(host, note),
        reply_markup=gen_button(host, note, get_user_link(host, note.author)),
    )
    await delete_file(file)


async def get_media_group(files: list[IDriveFile]) -> list:
    media_lists = []
    for file_ in files:
        file_url = file_.get("url", None)
        if not file_url:
            continue
        file_type = file_.get("type", "")
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
    host: str, cid: int, files: list[IDriveFile], note: Note, reply_to_message_id: int
):
    groups = await get_media_group(files)
    if len(groups) == 0:
        return await send_text(host, cid, note, reply_to_message_id)
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
        msg = msg[0]
    await send_text(host, cid, note, msg.id if msg else None)


async def send_update(host: str, cid: int, note: Note, topic_id: int):
    files = list(note.files)
    if note.reply:
        files.extend(iter(note.reply.files))
    if note.renote:
        files.extend(iter(note.renote.files))
    files = list({f.get("id"): f for f in files}.values())
    match len(files):
        case 0:
            await send_text(host, cid, note, topic_id)
        case 1:
            file = files[0]
            file_url = file.get("url", None)
            file_type = file.get("type", "")
            if file_type.startswith("image"):
                await send_photo(host, cid, file_url, note, topic_id)
            elif file_type.startswith("video"):
                await send_video(host, cid, file_url, note, topic_id)
            elif file_type.startswith("audio"):
                await send_audio(host, cid, file_url, note, topic_id)
            else:
                await send_document(host, cid, file, note, topic_id)
        case _:
            await send_group(host, cid, files, note, topic_id)
