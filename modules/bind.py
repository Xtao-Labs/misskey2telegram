from pyrogram import Client, filters
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.types import Message

from misskey_init import rerun_misskey_bot
from models.services.user import UserAction


async def pre_check(message: Message):
    if not message.from_user:
        await message.reply("请用普通用户身份执行命令。", quote=True)
        return False
    if not message.topic_message or not message.message_thread_id:
        await message.reply("请在论坛群组或者子话题中运行此命令。", quote=True)
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
        message.from_user.id,
        message.message_thread_id,
    ):
        await message.reply("Timeline 绑定成功。", quote=True)
    else:
        await message.reply("Timeline 绑定失败，不能和 Notice 话题相同。", quote=True)
        return
    await finish_check(message)


@Client.on_message(filters.incoming & filters.group & filters.command(["bind_notice"]))
async def bind_notice_command(_: Client, message: Message):
    if not await pre_check(message):
        return
    await UserAction.change_user_group_id(message.from_user.id, message.chat.id)
    if await UserAction.change_user_notice(
        message.from_user.id,
        message.message_thread_id,
    ):
        await message.reply("Notice 话题绑定成功。", quote=True)
    else:
        await message.reply(
            "Notice 话题绑定失败，不能和 Timeline 话题相同。", quote=True
        )
        return
    await finish_check(message)


@Client.on_message(filters.incoming & filters.private & filters.command(["bind_push"]))
async def bind_push_command(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply(
            "请使用 /bind_push <对话 ID> 的格式，绑定 Self Timeline Push。", quote=True
        )
        return
    try:
        push_chat_id = int(message.command[1])
    except ValueError:
        await message.reply("对话 ID 必须是数字。", quote=True)
        return
    try:
        chat = await client.get_chat(push_chat_id)
        if chat.type in [ChatType.SUPERGROUP, ChatType.CHANNEL, ChatType.GROUP]:
            me = await client.get_chat_member(push_chat_id, "me")
            if me.status not in [
                ChatMemberStatus.OWNER,
                ChatMemberStatus.ADMINISTRATOR,
            ]:
                raise FileExistsError
            you = await client.get_chat_member(push_chat_id, message.from_user.id)
            if you.status not in [
                ChatMemberStatus.OWNER,
                ChatMemberStatus.ADMINISTRATOR,
            ]:
                raise FileNotFoundError
    except FileExistsError:
        await message.reply("对话 ID 无效，我不是该对话的管理员。", quote=True)
        return
    except FileNotFoundError:
        await message.reply("对话 ID 无效，你不是该对话的管理员。", quote=True)
        return
    except Exception:
        await message.reply("对话 ID 无效。", quote=True)
        return
    if await UserAction.change_user_push(message.from_user.id, push_chat_id):
        await message.reply("Self Timeline Push 对话绑定成功。", quote=True)
    else:
        await message.reply(
            "Self Timeline Push 对话绑定失败，可能已经绑定过了。", quote=True
        )
    await finish_check(message)


@Client.on_message(
    filters.incoming & filters.private & filters.command(["unbind_push"])
)
async def unbind_push_command(_: Client, message: Message):
    if await UserAction.get_user_by_id(message.from_user.id):
        if await UserAction.change_user_push(message.from_user.id, 0):
            await message.reply("Self Timeline Push 对话解绑成功。", quote=True)
        else:
            await message.reply(
                "Self Timeline Push 对话解绑失败，可能没有绑定。", quote=True
            )
