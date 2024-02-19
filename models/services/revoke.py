import base64
import contextlib

from cashews import cache
from pyrogram.types import Message

from init import bot


class RevokeAction:
    HOURS: int = 2

    @staticmethod
    def encode_messages(cid: int, ids: list[str]) -> str:
        text = f"{cid}:{','.join(ids)}"
        return base64.b64encode(text.encode()).decode()

    @staticmethod
    def decode_messages(text: str) -> tuple[int, list[int]]:
        text = base64.b64decode(text.encode()).decode()
        cid, ids = text.split(":")
        return int(cid), [int(mid) for mid in ids.split(",")]

    @staticmethod
    async def _push(uid: int, note_id: str, cid: int, messages: list[int]):
        ids = [str(message) for message in messages]
        await cache.set(
            f"sub:{uid}:{note_id}",
            RevokeAction.encode_messages(cid, ids),
            expire=60 * 60 * RevokeAction.HOURS,
        )

    @staticmethod
    async def push(uid: int, note_id: str, messages: Message | list[Message]):
        if not messages:
            return
        messages = [messages] if isinstance(messages, Message) else messages
        cid = messages[0].chat.id
        mids = [message.id for message in messages]
        await RevokeAction._push(uid, note_id, cid, mids)

    @staticmethod
    async def push_extend(uid: int, note_id: str, messages: Message | list[Message]):
        if not messages:
            return
        messages = [messages] if isinstance(messages, Message) else messages
        try:
            cid, mids = await RevokeAction.get(uid, note_id)
        except ValueError:
            cid, mids = messages[0].chat.id, []
        mids.extend([message.id for message in messages])
        await RevokeAction._push(uid, note_id, cid, mids)

    @staticmethod
    async def get(uid: int, note_id: str) -> tuple[int, list[int]]:
        text = await cache.get(f"sub:{uid}:{note_id}")
        if text is None:
            raise ValueError("No such sub note: {}".format(note_id))
        return RevokeAction.decode_messages(text)

    @staticmethod
    async def get_all_subs(uid: int) -> list[str]:
        keys = []
        async for key in cache.scan(f"sub:{uid}:*"):
            key: str
            keys.append(key.split(":")[-1])
        return keys

    @staticmethod
    async def process_delete_note(uid: int, note_id: str):
        try:
            cid, msgs = await RevokeAction.get(uid, note_id)
        except ValueError:
            return
        with contextlib.suppress(Exception):
            await RevokeAction._delete_message(cid, msgs)
        await cache.delete(f"sub:{uid}:{note_id}")

    @staticmethod
    async def _delete_message(cid: int, msgs: list[int]):
        await bot.delete_messages(cid, msgs)
