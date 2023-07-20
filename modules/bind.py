from pyrogram import Client, filters
from pyrogram.types import Message

from misskey_init import rerun_misskey_bot
from models.services.user import UserAction


async def pre_check(message: Message):
    if not message.from_user:
        await message.reply("请用普通用户身份执行命令。", quote=True)
        return False
    if not getattr(message, "forum_topic", False):
        await message.reply("请在论坛群组中运行此命令。", quote=True)
        return False
    if not message.reply_to_top_message_id:
        await message.reply("请在子话题中运行此命令。", quote=True)
        return False
    user = await UserAction.get_user_by_id(message.from_user.id)
    if not user:
        await message.reply("请先私聊我绑定 Misskey 账号。", quote=True)
        return False
    return True


async def finish_check(message: Message):
    if await rerun_misskey_bot(message.from_user.id):
        await message.reply("设置完成，开始链接。", quote=True)


@Client.on_message(
    filters.incoming & filters.group & filters.command(["bind_timeline"])
)
async def bind_timeline_command(_: Client, message: Message):
    if not await pre_check(message):
        return
    await UserAction.change_user_group_id(message.from_user.id, message.chat.id)
    if await UserAction.change_user_timeline(
        message.from_user.id, message.reply_to_top_message_id
    ):
        await message.reply("Timeline 绑定成功。", quote=True)
    else:
        await message.reply("Timeline 绑定失败，不能和 Notice 话题相同。", quote=True)
    await finish_check(message)


@Client.on_message(filters.incoming & filters.group & filters.command(["bind_notice"]))
async def bind_notice_command(_: Client, message: Message):
    if not await pre_check(message):
        return
    await UserAction.change_user_group_id(message.from_user.id, message.chat.id)
    if await UserAction.change_user_notice(
        message.from_user.id, message.reply_to_top_message_id
    ):
        await message.reply("Notice 话题绑定成功。", quote=True)
    else:
        await message.reply("Notice 话题绑定失败，不能和 Timeline 话题相同。", quote=True)
    await finish_check(message)
