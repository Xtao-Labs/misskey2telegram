from pyrogram import Client, filters
from pyrogram.types import Message

help_msg = f"""这里是 Bot 帮助

1. 你可以直接在 Timeline Topic 中发送消息，目前支持文本和单张图片

2. 同样你可以在 Timeline Topic 中回复某条时间线推送，进行评论操作

3. 每个时间线推送最下方都有三个按钮，分别是：转发、喜欢、翻译

4. 你可以回复时间线推送 /delete 命令来删除这条推文

5. 你可以在 Notice Topic 中回复私聊消息，目前支持文本和单张图片

6. 你可以在 Notice Topic 中发送 @username@hostname 或者 @username 来查找用户，对用户进行关注、取消关注操作

7. 请注意：BOT 会持续监听帖子 2 小时，如果 2 小时内删帖则会同步删除 Telegram 推送

更多功能正在开发中，敬请期待！"""


@Client.on_message(filters.incoming & filters.private & filters.command(["help"]))
async def help_command(_: Client, message: Message):
    """
    回应 help
    """
    await message.reply(
        help_msg,
        quote=True,
    )
