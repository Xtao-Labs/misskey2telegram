from mipac.models.notification import NotificationFollow, NotificationFollowRequest
from mipac.models.lite.user import LiteUser
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from glover import admin, topic_group_id, notice_topic_id
from init import bot

user_followed_template = """<b>有人关注了你！</b> <a href="{0}">{1}</a>"""
follow_request_template = """<b>有人申请关注你！</b> <a href="{0}">{1}</a>"""
follow_request_accept_template = """<b>有人同意了你的关注申请！</b> <a href="{0}">{1}</a>"""


def gen_user_link_button(user: LiteUser):
    return [
        InlineKeyboardButton(
            text="Link",
            url=user.api.action.get_profile_link(),
        ),
    ]


async def send_user_followed(notice: NotificationFollow):
    await bot.send_message(
        topic_group_id or admin,
        user_followed_template.format(
            notice.user.api.action.get_profile_link(),
            notice.user.username,
        ),
        reply_to_message_id=notice_topic_id,
        reply_markup=InlineKeyboardMarkup([gen_user_link_button(notice.user)]),
    )


async def send_follow_request(notice: NotificationFollowRequest):
    await bot.send_message(
        topic_group_id or admin,
        follow_request_template.format(
            notice.user.api.action.get_profile_link(),
            notice.user.username,
        ),
        reply_to_message_id=notice_topic_id,
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
                ]
            ],
        ),
    )


async def send_follow_request_accept(notice: NotificationFollowRequest):
    await bot.send_message(
        topic_group_id or admin,
        follow_request_accept_template.format(
            notice.user.api.action.get_profile_link(),
            notice.user.username,
        ),
        reply_to_message_id=notice_topic_id,
        reply_markup=InlineKeyboardMarkup([gen_user_link_button(notice.user)]),
    )
