from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from defs.check_node import get_host, check_host
from glover import web_domain
from init import bot
from misskey_init import test_token, rerun_misskey_bot
from models.services.user import UserAction

des = f"""欢迎使用 {bot.me.first_name}，这是一个用于在 Telegram 上使用 Misskey 的机器人。按下方教程开始使用：

1. 使用 `/start https://[misskey_domain]` 设置账号所在 Misskey 实例地址（仅支持 https 链接）

2. 点击 start 之后回复你的按钮绑定所在 Misskey 实例的账号

3. 在论坛群组中使用 /bind_timeline 绑定 Timeline 话题，接收时间线更新

4. 在论坛群组中使用 /bind_notice 绑定 Notice 话题，接收通知

5. [可选] 在私聊中使用 `/bind_push [对话id]` 绑定本人发帖时推送 /unbind_push 解除绑定

6. [可选] 在私聊中使用 `/config` 设置敏感媒体是否自动设置 Spoiler

7. 使用 `/fix` 可尝试自助修复机器人运行问题，若无法修复请联系实例管理员

至此，你便可以在 Telegram 接收 Misskey 消息，同时你可以私聊我使用 /status 查看 Bot 运行状态

此 Bot 仅支持 Misskey 2023+ 实例的账号！"""


async def finish_check(message: Message):
    if await rerun_misskey_bot(message.from_user.id):
        await message.reply("Token 设置完成，开始链接。", quote=True)
    else:
        await message.reply("Token 设置完成，请绑定群组。", quote=True)


def gen_url(domain: str):
    return f"https://{web_domain}/gen?host={domain}&back_host={web_domain}&username={bot.me.username}"


async def change_host(message: Message, token_or_host: str):
    host = get_host(token_or_host)
    if await check_host(host):
        await UserAction.change_user_host(message.from_user.id, host)
        await message.reply(
            "Host 验证成功，请点击下方按钮绑定账号。",
            quote=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="绑定 Misskey 账号", url=gen_url(host)
                        ),
                    ]
                ]
            ),
        )
    else:
        await message.reply(
            "Host 验证失败，请检查 Host 是否正在运行 Misskey 2023+", quote=True
        )


async def change_token(message: Message, token_or_host: str):
    if user := await UserAction.get_user_by_id(message.from_user.id):
        if user.host:
            me = await test_token(user.host, token_or_host)
            if me:
                await UserAction.change_user_token(message.from_user.id, token_or_host)
                await UserAction.change_instance_user_id(message.from_user.id, me)
                await message.reply(
                    "Token 验证成功，绑定账号完成。\n当你撤销此登录时，你可以重新点击按钮授权。",
                    quote=True,
                )
                await finish_check(message)
            else:
                await message.reply("Token 验证失败，请检查 Token 是否正确", quote=True)


@Client.on_message(filters.incoming & filters.private & filters.command(["start"]))
async def start_command(_: Client, message: Message):
    """
    回应 start
    """
    if len(message.command) == 2:
        token_or_host = message.command[1]
        if not token_or_host:
            await message.reply(des, quote=True)
            return
        if token_or_host.startswith("https://"):
            await change_host(message, token_or_host)
            return
        await change_token(message, token_or_host)
        return
    await message.reply(des, quote=True)
