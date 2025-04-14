from pyrogram.methods.utilities.idle import idle

from init import logs, bot
from models.services.scheduler import scheduler


async def main():
    logs.info("Bot 开始运行")
    await bot.start()
    if not scheduler.running:
        scheduler.start()
    logs.info(f"Bot 启动成功！@{bot.me.username}")
    try:
        await idle()
    finally:
        if scheduler.running:
            scheduler.shutdown()
        await bot.stop()


if __name__ == "__main__":
    bot.run(main())
