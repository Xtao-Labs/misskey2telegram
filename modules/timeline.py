from asyncio import sleep

from aiohttp import ClientConnectorError

from glover import misskey_url, misskey_token
from init import bot
from misskey_init import misskey_bot


async def run():
    try:
        await misskey_bot.start(misskey_url, misskey_token)
    except ClientConnectorError:
        await sleep(3)
        await run()


bot.loop.create_task(run())
