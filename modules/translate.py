from mipac.errors import NoSuchRenoteTargetError, APIError
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from misskey_init import misskey_bot


# translate:note_id
@Client.on_callback_query(filters.regex(r"^translate:(\w+)$"))
async def translate_callback(_: Client, callback_query: CallbackQuery):
    note_id = callback_query.matches[0].group(1)
    try:
        result = await misskey_bot.core.api.note.action.translate(
            note_id=note_id,
            target_lang="zh-CN",
        )
        if len(result.text) < 50:
            await callback_query.answer(result.text, show_alert=True)
        else:
            await callback_query.message.reply(
                f"翻译结果：<code>{result.text}</code>",
                quote=True,
            )
            await callback_query.answer("翻译成功", show_alert=True)
    except NoSuchRenoteTargetError:
        await callback_query.answer("该嘟文不存在", show_alert=True)
    except APIError as e:
        if e.code == 204:
            return await callback_query.answer("该嘟文无法翻译", show_alert=True)
        if callback_query.message:
            await callback_query.message.reply(f"翻译失败：{e}", quote=True)
        await callback_query.answer("翻译失败", show_alert=True)
    except Exception as e:
        if callback_query.message:
            await callback_query.message.reply(f"翻译失败：{e}", quote=True)
        await callback_query.answer("翻译失败", show_alert=True)
