from mipac.errors import NoSuchNoteError, AlreadyReactedError
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from misskey_init import misskey_bot


# react:note_id:reaction
@Client.on_callback_query(filters.regex(r"^react:(\w+):(\w+)$"))
async def renote_callback(_: Client, callback_query: CallbackQuery):
    note_id = callback_query.matches[0].group(1)
    match callback_query.matches[0].group(2):
        case "love":
            reaction = "❤️"
        case _:
            reaction = "❤️"
    try:
        await misskey_bot.core.api.reaction.add(
            reaction=reaction,
            note_id=note_id,
        )
    except NoSuchNoteError:
        await callback_query.answer("该嘟文不存在", show_alert=True)
    except AlreadyReactedError:
        try:
            await misskey_bot.core.api.reaction.remove(
                note_id=note_id,
            )
            await callback_query.answer("取消表态成功", show_alert=True)
        except Exception as e:
            if callback_query.message:
                await callback_query.message.reply(f"取消表态失败：{e}", quote=True)
            await callback_query.answer("取消表态失败", show_alert=True)
        return
    except Exception as e:
        if callback_query.message:
            await callback_query.message.reply(f"表态失败：{e}", quote=True)
        await callback_query.answer("表态失败", show_alert=True)
    else:
        await callback_query.answer("表态成功", show_alert=True)
