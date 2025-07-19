from pyrogram import filters, Client
from pyrogram.types import Message

from glover import admin
from misskey_init import get_misskey_bot, rerun_misskey_bot, misskey_bot_map
from models.models.user import TokenStatusEnum
from models.services.user import UserAction


@Client.on_message(filters.incoming & filters.private & filters.command(["status"]))
async def status_command(_: Client, message: Message):
    """
    回应 status
    """
    user = await UserAction.get_user_by_id(message.from_user.id)
    if not user:
        await message.reply("请先私聊发送 /start ，然后点击按钮绑定账号", quote=True)
        return
    if user.status == TokenStatusEnum.INVALID_TOKEN:
        await message.reply(
            "Token 无效，请私聊发送 /start ，然后点击按钮重新绑定", quote=True
        )
        return
    misskey = get_misskey_bot(user.user_id)
    if not misskey and not await rerun_misskey_bot(user.user_id):
        await message.reply("无法启动 Misskey Bot，可能是未绑定群组。", quote=True)
        return
    text = "Bot 运行正常"
    if user.user_id == admin:
        text += f"\nBot 目前有 {len(misskey_bot_map.values())} 个 ws 任务"
    await message.reply(text, quote=True)
