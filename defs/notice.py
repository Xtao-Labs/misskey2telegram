from json import load

from mipac import Note
from mipac.models.lite.user import PartialUser
from mipac.models.notification import (
    NotificationFollow,
    NotificationFollowRequest,
    NotificationAchievement,
    NotificationNote,
)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from init import bot

user_followed_template = """<b>有人关注了你！</b> {0}"""
follow_request_template = """<b>有人申请关注你！</b> {0}"""
follow_request_accept_template = """<b>有人同意了你的关注申请！</b> {0}"""
achievement_template = """<b>你获得了新成就！</b> <b>{0}</b>：{1} {2}"""
mention_template = """<b>有人在帖子中提到了你！</b> {0} {1}"""
with open("gen/achievement.json", "r", encoding="utf-8") as f:
    achievement_map = load(f)


def get_user_link(host: str, user: PartialUser) -> str:
    if user.host:
        return f"https://{host}/@{user.username}@{user.host}"
    return f"https://{host}/@{user.username}"


def get_user_alink(host: str, user: PartialUser) -> str:
    return '<a href="{}">{}</a>'.format(
        get_user_link(host, user), user.name or f"@{user.username}"
    )


def get_note_link(host: str, note: Note) -> str:
    return f"https://{host}/notes/{note.id}"


def gen_link_button(host: str, user: PartialUser = None, note: Note = None):
    return [
        InlineKeyboardButton(
            text="Link",
            url=get_user_link(host, user) if user else get_note_link(host, note),
        ),
    ]


async def send_user_followed(
    host: str, chat_id: int, notice: NotificationFollow, topic_id: int
):
    await bot.send_message(
        chat_id,
        user_followed_template.format(
            get_user_alink(host, notice.user),
        ),
        reply_to_message_id=topic_id,
        reply_markup=InlineKeyboardMarkup([gen_link_button(host, notice.user)]),
    )


async def send_follow_request(
    host: str, chat_id: int, notice: NotificationFollowRequest, topic_id: int
):
    await bot.send_message(
        chat_id,
        follow_request_template.format(
            get_user_alink(host, notice.user),
        ),
        reply_to_message_id=topic_id,
        reply_markup=InlineKeyboardMarkup(
            [
                gen_link_button(host, notice.user),
                [
                    InlineKeyboardButton(
                        text="Accept",
                        callback_data=f"request_accept:{notice.user.id}",
                    ),
                    InlineKeyboardButton(
                        text="Reject",
                        callback_data=f"request_reject:{notice.user.id}",
                    ),
                ],
            ],
        ),
    )


async def send_follow_request_accept(
    host: str, chat_id: int, notice: NotificationFollowRequest, topic_id: int
):
    await bot.send_message(
        chat_id,
        follow_request_accept_template.format(
            get_user_alink(host, notice.user),
        ),
        reply_to_message_id=topic_id,
        reply_markup=InlineKeyboardMarkup([gen_link_button(host, notice.user)]),
    )


async def send_achievement_earned(
    _: str, chat_id: int, notice: NotificationAchievement, topic_id: int
):
    name, desc, note = achievement_map.get(notice.achievement, ("", "", ""))
    await bot.send_message(
        chat_id,
        achievement_template.format(
            name,
            desc,
            f"- {note}" if note else "",
        ),
        reply_to_message_id=topic_id,
    )


async def send_note_mention(
    host: str,
    chat_id: int,
    notice: NotificationNote,
    topic_id: int,
):
    await bot.send_message(
        chat_id,
        mention_template.format(
            get_note_link(host, notice.note),
            get_user_alink(host, notice.user),
        ),
        reply_to_message_id=topic_id,
        reply_markup=InlineKeyboardMarkup([gen_link_button(host, note=notice.note)]),
    )
