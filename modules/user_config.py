import base64
import json

from pydantic import ValidationError
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
    ReplyKeyboardRemove,
)

from defs.web_app import WebAppData, WebAppUserConfig, filter_web_data
from glover import web_domain
from misskey_init import rerun_misskey_bot
from models.services.user_config import UserConfigAction


@Client.on_message(filters.incoming & filters.private & filter_web_data)
async def process_user_config(_, message: Message):
    try:
        data = WebAppData(**json.loads(message.web_app_data.data)).user_config
    except (json.JSONDecodeError, ValidationError):
        await message.reply("数据解析失败，请重试。", quote=True)
        return
    if user_config := await UserConfigAction.get_user_config_by_id(
        message.from_user.id
    ):
        user_config.timeline_spoiler = data.timeline_spoiler
        user_config.push_spoiler = data.push_spoiler
        await UserConfigAction.update_user_config(user_config)
    else:
        user_config = UserConfigAction.create_user_config(message.from_user.id)
        user_config.timeline_spoiler = data.timeline_spoiler
        user_config.push_spoiler = data.push_spoiler
        await UserConfigAction.add_user_config(user_config)
    await message.reply("更新设置成功。", quote=True, reply_markup=ReplyKeyboardRemove())
    await rerun_misskey_bot(message.from_user.id)


async def get_user_config(user_id: int) -> str:
    if user_config := await UserConfigAction.get_user_config_by_id(user_id):
        data = WebAppUserConfig(
            timeline_spoiler=user_config.timeline_spoiler,
            push_spoiler=user_config.push_spoiler,
        ).json()
    else:
        data = "{}"
    return base64.b64encode(data.encode()).decode()


@Client.on_message(filters.incoming & filters.private & filters.command(["config"]))
async def notice_user_config(_, message: Message):
    data = await get_user_config(message.from_user.id)
    url = f"https://{web_domain}/config?bot_data={data}"
    await message.reply(
        "请点击下方按钮，开始设置。",
        quote=True,
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(text="web config", web_app=WebAppInfo(url=url))]]
        ),
    )
