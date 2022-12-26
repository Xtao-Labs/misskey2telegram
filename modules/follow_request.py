from mipac.errors import NoSuchUserError, NoFollowRequestError
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from misskey_init import misskey_bot


# request_accept:user_id
@Client.on_callback_query(filters.regex(r"^request_accept:(\w+)$"))
async def request_accept_callback(_: Client, callback_query: CallbackQuery):
    user_id = callback_query.matches[0].group(1)
    try:
        await misskey_bot.core.api.follow_request.action.accept(
            user_id=user_id,
        )
        await callback_query.answer("已接受关注请求", show_alert=True)
    except NoSuchUserError:
        await callback_query.answer("该用户不存在", show_alert=True)
    except NoFollowRequestError:
        await callback_query.answer("该用户没有向你发起关注请求", show_alert=True)
    except Exception as e:
        if callback_query.message:
            await callback_query.message.reply(f"接受关注请求失败：{e}", quote=True)
        await callback_query.answer("接受关注请求失败", show_alert=True)


# request_reject:user_id
@Client.on_callback_query(filters.regex(r"^request_reject:(\w+)$"))
async def request_reject_callback(_: Client, callback_query: CallbackQuery):
    user_id = callback_query.matches[0].group(1)
    try:
        await misskey_bot.core.api.follow_request.action.reject(
            user_id=user_id,
        )
        await callback_query.answer("已拒绝关注请求", show_alert=True)
    except NoSuchUserError:
        await callback_query.answer("该用户不存在", show_alert=True)
    except NoFollowRequestError:
        await callback_query.answer("该用户没有向你发起关注请求", show_alert=True)
    except Exception as e:
        if callback_query.message:
            await callback_query.message.reply(f"拒绝关注请求失败：{e}", quote=True)
        await callback_query.answer("拒绝关注请求失败", show_alert=True)
