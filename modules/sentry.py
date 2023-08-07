from init import bot
from defs.sentry import sentry_init_id

bot.loop.create_task(sentry_init_id(bot))
