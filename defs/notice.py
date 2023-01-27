from mipac.models.notification import NotificationFollow, NotificationFollowRequest, NotificationAchievement
from mipac.models.lite.user import LiteUser
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from init import bot

user_followed_template = """<b>有人关注了你！</b> <a href="{0}">{1}</a>"""
follow_request_template = """<b>有人申请关注你！</b> <a href="{0}">{1}</a>"""
follow_request_accept_template = """<b>有人同意了你的关注申请！</b> <a href="{0}">{1}</a>"""
achievement_template = """<b>你获得了新成就！</b> <b>{0}</b>：{1} {2}"""
achievement_map = {
    'notes1': ('初来乍到', '第一次发帖', '祝您在Misskey玩的愉快～'),
    'notes10': ('一些帖子', '发布了10篇帖子', ''),
    'notes100': ('很多帖子', '发布了100篇帖子', ''),
    'notes500': ('满是帖子', '发布了500篇帖子', ''),
    'notes1000': ('积帖成山', '发布了1,000篇帖子', ''),
    'notes5000': ('帖如泉涌', '发布了5,000篇帖子', ''),
    'notes10000': ('超级帖', '发布了10,000篇帖子', ''),
    'notes20000': ('还想要更多帖子', '发布了20,000篇帖子', ''),
    'notes30000': ('帖子帖子帖子', '发布了30,000篇帖子', ''),
    'notes40000': ('帖子工厂', '发布了40,000篇帖子', ''),
    'notes50000': ('帖子星球', '发布了50,000篇帖子', ''),
    'notes60000': ('帖子类星体', '发布了60,000篇帖子', ''),
    'notes70000': ('帖子黑洞', '发布了70,000篇帖子', ''),
    'notes80000': ('帖子星系', '发布了80,000篇帖子', ''),
    'notes90000': ('帖子起源', '发布了90,000篇帖子', ''),
    'notes100000': ('ALL YOUR NOTE ARE BELONG TO US', '发布了100,000篇帖子', '真的有那么多可以写的东西吗？'),
    'login3': ('初学者 I', '连续登录3天', ''),
    'login7': ('初学者 II', '连续登录7天', ''),
    'login15': ('初学者 III', '连续登录15天', ''),
    'login30': ('', '连续登录30天', ''),
    'login60': ('', '连续登录60天', ''),
    'login1000': ('', '', '感谢您使用Misskey！'),
    'noteFavorited1': ('观星者', '', ''),
    'profileFilled': ('整装待发', '设置了个人资料', ''),
    'markedAsCat': ('我是猫', '将账户设定为一只猫', ''),
    'following10': ('关注，跟随', '关注数超过10', ''),
    'following50': ('我的朋友很多', '关注数超过50', ''),
    'following300': ('', '关注数超过300', ''),
    'followers100': ('胜友如云', '被关注数超过100', ''),
    'collectAchievements30': ('', '获得超过30个成就', ''),
    'viewAchievements3min': ('', '盯着成就看三分钟', ''),
    'iLoveMisskey': ('I Love Misskey', '发布"I ❤ #Misskey"帖子', '感谢您使用 Misskey ！ by 开发团队'),
    'noteDeletedWithin1min': ('', '发帖后一分钟内就将其删除', ''),
    'postedAtLateNight': ('夜行者', '深夜发布帖子', ''),
    'outputHelloWorldOnScratchpad': ('Hello, world!', '', ''),
    'passedSinceAccountCreated1': ('', '账户创建时间超过1年', ''),
    'passedSinceAccountCreated2': ('', '账户创建时间超过2年', ''),
    'passedSinceAccountCreated3': ('', '账户创建时间超过3年', ''),
    'loggedInOnBirthday': ('生日快乐', '在生日当天登录', ''),
    'loggedInOnNewYearsDay': ('恭贺新禧', '在元旦登入', '')
}


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


async def send_follow_request(chat_id: int, notice: NotificationFollowRequest, topic_id: int):
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
                ]
            ],
        ),
    )


async def send_follow_request_accept(chat_id: int, notice: NotificationFollowRequest, topic_id: int):
    await bot.send_message(
        chat_id,
        follow_request_accept_template.format(
            notice.user.api.action.get_profile_link(),
            notice.user.username,
        ),
        reply_to_message_id=topic_id,
        reply_markup=InlineKeyboardMarkup([gen_user_link_button(notice.user)]),
    )


async def send_achievement_earned(chat_id: int, notice: NotificationAchievement, topic_id: int):
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
