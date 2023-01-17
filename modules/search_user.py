from mipac.errors import InternalErrorError, AlreadyFollowingError, FolloweeIsYourselfError
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery

from glover import admin

from defs.search_user import search_user, gen_text, gen_button
from init import notice_filter
from misskey_init import misskey_bot


# @xxx
@Client.on_message(filters.incoming & notice_filter & filters.regex(r"^@(.*)$") & filters.user(admin))
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


# follow:xxx
@Client.on_callback_query(filters.regex(r"^follow:(.*)$"))
async def follow_user_callback(_: Client, callback_query: CallbackQuery):
    """
        关注/取消关注用户
    """
    user_id = callback_query.matches[0].group(1)
    try:
        await misskey_bot.core.api.follow.action.add(user_id)
        await callback_query.answer("关注成功", show_alert=True)
    except InternalErrorError:
        await callback_query.answer("关注申请未批准，请等待对方同意", show_alert=True)
    except AlreadyFollowingError:
        try:
            await misskey_bot.core.api.follow.action.remove(user_id)
            await callback_query.answer("取消关注成功", show_alert=True)
        except Exception as e:
            await callback_query.answer("取消关注失败", show_alert=True)
            await callback_query.message.reply(f"取消关注失败：{e}", quote=True)
        return
    except FolloweeIsYourselfError:
        await callback_query.answer("不能关注自己", show_alert=True)
    except Exception as e:
        await callback_query.answer("关注失败", show_alert=True)
        await callback_query.message.reply(f"关注失败：{e}", quote=True)
