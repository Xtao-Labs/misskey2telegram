from subprocess import run, PIPE
from time import time

import sentry_sdk
from pyrogram import Client
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from glover import sentry_dsn

sentry_sdk_report_time = time()
sentry_sdk_git_hash = (
    run("git rev-parse HEAD", stdout=PIPE, shell=True, check=True)
    .stdout.decode()
    .strip()
)
sentry_sdk.init(
    sentry_dsn,
    send_default_pii=True,
    traces_sample_rate=1.0,
    release=sentry_sdk_git_hash,
    environment="production",
    integrations=[
        AioHttpIntegration(),
        HttpxIntegration(),
        LoggingIntegration(),
        RedisIntegration(),
        SqlalchemyIntegration(),
    ],
    _experiments={
        "enable_logs": True,
    },
)


async def sentry_init_id(bot: Client):
    if not bot.me:
        bot.me = await bot.get_me()
    data = {
        "id": bot.me.id,
        "username": bot.me.username,
        "name": bot.me.first_name,
        "ip_address": "{{auto}}",
    }
    sentry_sdk.set_user(data)
