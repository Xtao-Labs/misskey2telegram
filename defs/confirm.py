from typing import Optional

from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from misskey_init import misskey_bot


class ReadySend:
    def __init__(
            self,
            content: str,
            reply_id: Optional[str] = None,
            files: Optional[list[str]] = None,
    ):
        self.content = content
        self.reply_id = reply_id
        self.files = files

    async def confirm(self, msg: Message):
        msg = await msg.reply(
            "确认发送？",
            quote=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="发送", callback_data="send"),
                        InlineKeyboardButton(text="拒绝", callback_data="delete")
                    ]
                ]
            ),
        )
        ready_send[msg.id] = self

    async def send(self, msg: Message):
        try:
            await misskey_bot.core.api.note.action.send(
                content=self.content,
                reply_id=self.reply_id,
                files=self.files,
            )
        except Exception as e:
            await msg.edit(f"发送失败：{e}")
        else:
            await msg.delete()
        finally:
            del ready_send[msg.id]


class ReadySendMessage:
    def __init__(
            self,
            text: str,
            group: bool = False,
            uid: Optional[str] = None,
            file_id: Optional[str] = None,
    ):
        self.text = text
        self.user_id = None if group else uid
        self.group_id = uid if group else None
        self.file_id = file_id

    async def confirm(self, msg: Message):
        msg = await msg.reply(
            "确认发送？",
            quote=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="发送", callback_data="chat_send"),
                        InlineKeyboardButton(text="拒绝", callback_data="delete")
                    ]
                ]
            ),
        )
        ready_send[msg.id] = self

    async def send(self, msg: Message):
        try:
            await misskey_bot.core.api.chat.action.send(
                text=self.text,
                user_id=self.user_id,
                group_id=self.group_id,
                file_id=self.file_id,
            )
        except Exception as e:
            await msg.edit(f"发送失败：{e}")
        else:
            await msg.delete()
        finally:
            del ready_send[msg.id]


ready_send = {}
