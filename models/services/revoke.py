import base64
from cashews import cache
from pyrogram.types import Message

from init import bot


class RevokeAction:
    HOURS: int = 2

    @staticmethod
    def encode_messages(messages: list[Message]) -> str:
        ids = [str(message.id) for message in messages]
        cid = messages[0].chat.id
        text = f"{cid}:{','.join(ids)}"
        return base64.b64encode(text.encode()).decode()

    @staticmethod
    def decode_messages(text: str) -> tuple[int, list[int]]:
        text = base64.b64decode(text.encode()).decode()
        cid, ids = text.split(":")
        return int(cid), [int(mid) for mid in ids.split(",")]

    @staticmethod
    async def push(uid: int, note_id: str, messages: list[Message]):
        await cache.set(
            f"sub:{uid}:{note_id}",
            RevokeAction.encode_messages(messages),
            expire=60 * 60 * RevokeAction.HOURS,
        )

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
            keys.append(key[4:])
        return keys

    @staticmethod
    async def process_delete_note(uid: int, note_id: str):
        try:
            cid, msgs = await RevokeAction.get(uid, note_id)
        except ValueError:
            return
        await RevokeAction._delete_message(cid, msgs)
        await cache.delete(f"sub:{uid}:{note_id}")

    @staticmethod
    async def _delete_message(cid: int, msgs: list[int]):
        await bot.delete_messages(cid, msgs)
