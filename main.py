from pyrogram import idle

from init import logs, bot


if __name__ == "__main__":
    logs.info("Bot 开始运行")
    bot.start()
    logs.info("Bot 启动成功！")
    idle()
    bot.stop()
