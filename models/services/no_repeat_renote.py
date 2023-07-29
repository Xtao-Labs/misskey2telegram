from cashews import cache
from mipac import Note


class NoRepeatRenoteAction:
    @staticmethod
    async def push(uid: int, note_id: str) -> None:
        await cache.set(f"pushed:{uid}:{note_id}", "true")

    @staticmethod
    async def get(uid: int, note_id: str) -> bool:
        text = await cache.get(f"pushed:{uid}:{note_id}")
        if text is None:
            return False
        return True

    @staticmethod
    async def check(uid: int, note: Note):
        if note.renote and (not note.content):
            if NoRepeatRenoteAction.get(uid, note.renote.id):
                return False
        return True

    @staticmethod
    async def set(uid: int, note: Note):
        await NoRepeatRenoteAction.push(uid, note.id)
        if note.renote and (not note.content):
            await NoRepeatRenoteAction.push(uid, note.renote.id)
