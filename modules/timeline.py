from glover import misskey_url, misskey_token
from init import bot
from misskey_init import misskey_bot

bot.loop.create_task(misskey_bot.start(misskey_url, misskey_token))
