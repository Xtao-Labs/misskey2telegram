from datetime import datetime, timedelta, timezone
from typing import Optional

from mipac import Note
from mipac.models.lite import LiteUser
from mipac.types import IDriveFile
from pyrogram.enums import ParseMode
from pyrogram.errors import MediaEmpty

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InputMediaVideo, \
    InputMediaDocument, InputMediaAudio

from glover import misskey_host
from init import bot, request
from scheduler import add_delete_file_job, delete_file


def get_note_url(note: Note) -> str:
    return note.url or f"https://{misskey_host}/notes/{note.id}"


def gen_button(note: Note, author: str):
    source = get_note_url(note)
    reply_source = get_note_url(note.reply) if note.reply else None
    if reply_source:
        return InlineKeyboardMarkup([[
            InlineKeyboardButton(text="Source", url=source),
            InlineKeyboardButton(text="RSource", url=reply_source),
            InlineKeyboardButton(text="Author", url=author)]])
    else:
        return InlineKeyboardMarkup([[
            InlineKeyboardButton(text="Source", url=source),
            InlineKeyboardButton(text="Author", url=author)]])


def get_user_link(user: LiteUser) -> str:
    if user.host:
        return f"https://{user.host}/@{user.username}"
    return f"https://{misskey_host}/@{user.username}"


def get_post_time(date: datetime) -> str:
    try:
        date = date + timedelta(hours=8)
        return date.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def get_content(note: Note) -> str:
    return f"""<b>Misskey Timeline Update</b>

<code>{note.content or ''}</code>

<a href=\"{get_user_link(note.author)}\">{note.author.nickname}</a> 发表于 {get_post_time(note.created_at)}
点赞: {len(note.emojis)} | 回复: {note.replies_count} | 转发: {note.renote_count}"""


async def send_text(cid: int, note: Note):
    await bot.send_message(
        cid,
        get_content(note),
        reply_markup=gen_button(note, get_user_link(note.author)),
        disable_web_page_preview=True,
    )


def deprecated_to_text(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except MediaEmpty:
            return await send_text(args[0], args[2])

    return wrapper


@deprecated_to_text
async def send_photo(cid: int, url: str, note: Note):
    if not url:
        return await send_text(cid, note)
    await bot.send_photo(
        cid,
        url,
        caption=get_content(note),
        reply_markup=gen_button(note, get_user_link(note.author)),
    )


@deprecated_to_text
async def send_video(cid: int, url: str, note: Note):
    if not url:
        return await send_text(cid, note)
    await bot.send_video(
        cid,
        url,
        caption=get_content(note),
        reply_markup=gen_button(note, get_user_link(note.author)),
    )


@deprecated_to_text
async def send_audio(cid: int, url: str, note: Note):
    if not url:
        return await send_text(cid, note)
    await bot.send_audio(
        cid,
        url,
        caption=get_content(note),
        reply_markup=gen_button(note, get_user_link(note.author)),
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
async def send_document(cid: int, file: IDriveFile, note: Note):
    file = await fetch_document(file)
    if not file:
        return await send_text(cid, note)
    await bot.send_document(
        cid,
        file,
        caption=get_content(note),
        reply_markup=gen_button(note, get_user_link(note.author)),
    )
    await delete_file(file)


async def get_media_group(files: list[IDriveFile], note: Note) -> list:
    media_lists = []
    for ff in range(len(files)):
        file_url = files[ff].get("url", None)
        if not file_url:
            continue
        file_type = files[ff].get("type", "")
        if file_type.startswith("image"):
            media_lists.append(
                InputMediaPhoto(
                    file_url,
                    caption=get_content(note) if ff == 0 else None,
                    parse_mode=ParseMode.HTML,
                )
            )
        elif file_type.startswith("video"):
            media_lists.append(
                InputMediaVideo(
                    file_url,
                    caption=get_content(note) if ff == 0 else None,
                    parse_mode=ParseMode.HTML,
                )
            )
        elif file_type.startswith("audio"):
            media_lists.append(
                InputMediaAudio(
                    file_url,
                    caption=get_content(note) if ff == 0 else None,
                    parse_mode=ParseMode.HTML,
                )
            )
        elif file := await fetch_document(files[ff]):
            media_lists.append(
                InputMediaDocument(
                    file,
                    caption=get_content(note) if ff == 0 else None,
                    parse_mode=ParseMode.HTML,
                )
            )
    return media_lists


async def send_group(cid: int, files: list[IDriveFile], note: Note):
    groups = await get_media_group(files, note)
    if len(groups) == 0:
        return await send_text(cid, note)
    photo, video, audio, document = [], [], [], []
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
        await bot.send_media_group(
            cid,
            video,
        )
        if audio:
            await bot.send_media_group(
                cid,
                audio,
            )
        elif document:
            await bot.send_media_group(
                cid,
                document,
            )
    elif audio and (photo or document):
        await bot.send_media_group(
            cid,
            audio,
        )
        if photo:
            await bot.send_media_group(
                cid,
                photo,
            )
        elif document:
            await bot.send_media_group(
                cid,
                document,
            )
    else:
        await bot.send_media_group(
            cid,
            groups,
        )


async def send_update(cid: int, note: Note):
    files = list(note.files)
    if note.reply:
        files.extend(iter(note.reply.files))
    match len(files):
        case 0:
            await send_text(cid, note)
        case 1:
            file = files[0]
            file_url = file.get("url", None)
            file_type = file.get("type", "")
            if file_type.startswith("image"):
                await send_photo(cid, file_url, note)
            elif file_type.startswith("video"):
                await send_video(cid, file_url, note)
            elif file_type.startswith("audio"):
                await send_audio(cid, file_url, note)
            else:
                await send_document(cid, file, note)
        case _:
            await send_group(cid, files, note)
