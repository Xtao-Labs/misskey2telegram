from pyrogram import Client, filters
from pyrogram.types import Message


des = """running"""


@Client.on_message(filters.incoming & filters.private &
                   filters.command(["start"]))
async def start_command(_: Client, message: Message):
    """
        回应机器人信息
    """
    await message.reply(des, quote=True)
