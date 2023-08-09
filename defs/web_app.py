from pydantic import BaseModel
from pyrogram import filters
from pyrogram.types import Message


class WebAppUserConfig(BaseModel):
    timeline_spoiler: bool
    push_spoiler: bool


class WebAppData(BaseModel):
    path: str
    data: dict
    code: int
    message: str

    @property
    def user_config(self) -> WebAppUserConfig:
        return WebAppUserConfig(**self.data)


async def web_data_filter(_, __, m: Message):
    return bool(m.web_app_data)


filter_web_data = filters.create(web_data_filter)
