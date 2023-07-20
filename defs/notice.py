from json import load

from mipac.models.lite.user import LiteUser
from mipac.models.notification import (
    NotificationFollow,
    NotificationFollowRequest,
    NotificationAchievement,
)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from init import bot

user_followed_template = """<b>有人关注了你！</b> <a href="{0}">{1}</a>"""
follow_request_template = """<b>有人申请关注你！</b> <a href="{0}">{1}</a>"""
follow_request_accept_template = """<b>有人同意了你的关注申请！</b> <a href="{0}">{1}</a>"""
achievement_template = """<b>你获得了新成就！</b> <b>{0}</b>：{1} {2}"""
with open("gen/achievement.json", "r", encoding="utf-8") as f:
    achievement_map = load(f)


def gen_user_link_button(user: LiteUser):
    return [
        InlineKeyboardButton(
            text="Link",
            url=user.api.action.get_profile_link(),
        ),
    ]


async def send_user_followed(chat_id: int, notice: NotificationFollow, topic_id: int):
    await bot.send_message(
        chat_id,
        user_followed_template.format(
            notice.user.api.action.get_profile_link(),
            notice.user.username,
        ),
        reply_to_message_id=topic_id,
        reply_markup=InlineKeyboardMarkup([gen_user_link_button(notice.user)]),
    )


async def send_follow_request(
    chat_id: int, notice: NotificationFollowRequest, topic_id: int
):
    await bot.send_message(
        chat_id,
        follow_request_template.format(
            notice.user.api.action.get_profile_link(),
            notice.user.username,
        ),
        reply_to_message_id=topic_id,
        reply_markup=InlineKeyboardMarkup(
            [
                gen_user_link_button(notice.user),
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
    chat_id: int, notice: NotificationFollowRequest, topic_id: int
):
    await bot.send_message(
        chat_id,
        follow_request_accept_template.format(
            notice.user.api.action.get_profile_link(),
            notice.user.username,
        ),
        reply_to_message_id=topic_id,
        reply_markup=InlineKeyboardMarkup([gen_user_link_button(notice.user)]),
    )


async def send_achievement_earned(
    chat_id: int, notice: NotificationAchievement, topic_id: int
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
