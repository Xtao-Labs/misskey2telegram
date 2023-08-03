import asyncio
from concurrent.futures import ThreadPoolExecutor

from pyrogram import Client, filters
from pyrogram.types import Message

from defs.fcm_notice import check_fcm_token
from misskey_init import rerun_misskey_bot
from models.services.user import UserAction


async def finish_check(message: Message):
    if await rerun_misskey_bot(message.from_user.id):
        await message.reply("设置完成，开始链接。", quote=True)


@Client.on_message(filters.incoming & filters.private & filters.command(["fcm"]))
async def bind_fcm_token_command(_: Client, message: Message):
    user = await UserAction.get_user_if_ok(message.from_user.id)
    if not user:
        await message.reply("请先私聊我绑定 Misskey 账号。", quote=True)
        return
    if len(message.command) == 2:
        fcm_token = message.command[1]
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            success = await loop.run_in_executor(executor, check_fcm_token, fcm_token)
        if success:
            await UserAction.change_user_fcm_token(message.from_user.id, fcm_token)
            await message.reply("FCM Token 绑定成功。", quote=True)
            await finish_check(message)
        else:
            await message.reply("FCM Token 无效，请尝试重新获取。", quote=True)
    else:
        await message.reply("请提供 FCM Token，APP 请联系实例管理员索要。", quote=True)
