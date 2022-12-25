from pyrogram import Client, filters
from pyrogram.types import Message

from glover import admin

from defs.search_user import search_user, gen_text, gen_button


# @xxx
@Client.on_message(filters.incoming & filters.private & filters.regex(r"^@(.*)$") & filters.user(admin))
async def search_user_command(_: Client, message: Message):
    """
        搜索用户
    """
    username = message.matches[0].group(1)
    path = username.strip().split("@")
    username = path[0]
    host = path[1] if len(path) > 1 else None
    try:
        user = await search_user(username, host)
        if not user:
            return await message.reply("没有找到用户", quote=True)
        text, button = gen_text(user), gen_button(user)
        if user.avatar_url:
            try:
                await message.reply_photo(user.avatar_url, caption=text, reply_markup=button, quote=True)
            except Exception:
                await message.reply(text, reply_markup=button, quote=True, disable_web_page_preview=True)
        else:
            await message.reply(text, reply_markup=button, quote=True, disable_web_page_preview=True)
    except Exception as e:
        return await message.reply(f"搜索用户失败：{e}", quote=True)
