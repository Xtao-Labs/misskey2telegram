from init import bot
from misskey_init import init_misskey_bot

bot.loop.create_task(init_misskey_bot())
