from datetime import datetime, timedelta
from typing import Optional

from mipac import UserDetailedNotMe
from mipac.errors import FailedToResolveRemoteUserError
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from defs.misskey import get_user_link
from misskey_init import MisskeyBot

template = """<b>Misskey User Info</b>

Name: %s
Username: <a href="%s">@%s</a>
Bio: <code>%s</code>
Joined: <code>%s</code>
Updated: <code>%s</code>

📤 %s 粉丝 %s 关注 %s"""


def gen_text(host: str, user: UserDetailedNotMe):
    def parse_time(time: datetime) -> str:
        if not time:
            return "Unknown"
        time = time + timedelta(hours=8)
        return time.strftime("%Y-%m-%d %H:%M:%S")

    create_at = parse_time(user.created_at)
    update_at = parse_time(user.updated_at)
    return template % (
        user.name,
        get_user_link(host, user),
        user.username,
        user.description or "",
        create_at,
        update_at,
        user.notes_count,
        user.followers_count,
        user.following_count,
    )


def gen_button(host: str, user: UserDetailedNotMe):
    first_line = [
        InlineKeyboardButton(text="Link", url=get_user_link(host, user)),
    ]
    second_line = [
        InlineKeyboardButton(
            text="➖" if user.is_followed else "➕",
            callback_data=f"follow:{user.id}",
        ),
    ]
    return InlineKeyboardMarkup([first_line, second_line])


async def search_user(
    misskey_bot: MisskeyBot, username: str, host: str = None
) -> Optional[UserDetailedNotMe]:
    """
    搜索用户
    """
    if host:
        users = await misskey_bot.core.api.user.action.search_by_username_and_host(
            username, host, limit=1
        )
        if not users:
            try:
                users = [
                    await misskey_bot.core.api.user.action.get(
                        username=username, host=host
                    )
                ]
            except FailedToResolveRemoteUserError:
                pass
    else:
        users = []
        async for user in misskey_bot.core.api.user.action.search(username, limit=1):
            users.append(user)
    return users[0] if users else None
