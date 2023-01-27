from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from glover import misskey_host, web_domain, misskey_domain
from init import bot
from misskey_init import test_token, rerun_misskey_bot
from models.services.user import UserAction

des = f"""欢迎使用 {bot.me.first_name}，这是一个用于在 Telegram 上使用 Misskey 的机器人。

1. 请先点击下方按钮绑定 Misskey 账号

2. 在论坛群组中使用 /bind_timeline 绑定 Timeline 话题，接收时间线更新

3. 在论坛群组中使用 /bind_notice 绑定 Notice 话题，接收通知

4. 使用 /status 查看运行状态

此实例支持绑定 {misskey_host} 的 Misskey 账号。"""


async def finish_check(message: Message):
    if await rerun_misskey_bot(message.from_user.id):
        await message.reply("Token 设置完成，开始链接。", quote=True)
    else:
        await message.reply("Token 设置完成，请绑定群组。", quote=True)


def gen_url():
    return f"https://{web_domain}/gen?host={misskey_domain}&back_host={web_domain}&username={bot.me.username}"


@Client.on_message(filters.incoming & filters.private &
                   filters.command(["start"]))
async def start_command(_: Client, message: Message):
    """
        回应 start
    """
    if len(message.command) == 2:
        token = message.command[1]
        if not token:
            await message.reply(des, quote=True)
            return
        if await test_token(token):
            await UserAction.change_user_token(message.from_user.id, token)
            await message.reply("Token 验证成功，绑定账号完成。", quote=True)
            await finish_check(message)
        else:
            await message.reply("Token 验证失败，请检查 Token 是否正确", quote=True)
        return
    await message.reply(
        des,
        quote=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="绑定 Misskey 账号", url=gen_url()),
                ]
            ]
        )
    )
