from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from misskey_init import misskey_bot


# renote:note_id
@Client.on_callback_query(filters.regex(r"^renote:(\w+)$"))
async def renote_callback(_: Client, callback_query: CallbackQuery):
    note_id = callback_query.matches[0].group(1)
    try:
        await misskey_bot.core.api.note.action.create_renote(
            note_id=note_id,
        )
    except Exception as e:
        if callback_query.message:
            await callback_query.message.reply(f"转发失败：{e}", quote=True)
        await callback_query.answer("转发失败", show_alert=True)
    else:
        await callback_query.answer("转发成功", show_alert=True)
