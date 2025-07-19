from pyrogram import Client, filters
from pyrogram.types import Message

from misskey_init import get_misskey_bot, rerun_misskey_bot, test_token
from models.services.user import UserAction

no_account = "你还没有绑定账号哦，请使用 `/start https://[misskey_domain]` 设置账号所在 Misskey 实例地址（仅支持 https 链接）。"
no_timeline = "你还没有绑定时间线话题哦，在论坛群组中使用 /bind_timeline 绑定 Timeline 话题，接收时间线更新。"
no_notice = (
    "你还没有绑定通知话题哦，在论坛群组中使用 /bind_notice 绑定 Notice 话题，接收通知。"
)
token_expired = "Token 已过期，请重新绑定账号。"
success = "bot 运行正常，无需修复！"
no_bot = "bot 似乎离线，已尝试重启..."
cannot_fix = "无法自助修复，请联系实例管理员！"


@Client.on_message(filters.incoming & filters.private & filters.command(["fix"]))
async def fix_command(_: Client, message: Message):
    if get_misskey_bot(message.from_user.id):
        await message.reply(success, quote=True)
        return
    user = await UserAction.get_user_by_id(message.from_user.id)
    if not user:
        await message.reply(no_account, quote=True)
        return
    if not user.token:
        await message.reply(no_account, quote=True)
        return
    if not (await test_token(user.host, user.token)):
        await message.reply(token_expired, quote=True)
        return
    if not user.push_chat_id:
        if not user.timeline_topic:
            await message.reply(no_timeline, quote=True)
            return
        if not user.notice_topic:
            await message.reply(no_notice, quote=True)
            return
    if await rerun_misskey_bot(message.from_user.id):
        await message.reply(no_bot, quote=True)
        return
    await message.reply(cannot_fix, quote=True)
