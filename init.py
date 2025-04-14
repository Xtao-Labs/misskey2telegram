from logging import getLogger, INFO, StreamHandler, basicConfig, CRITICAL, Formatter

import httpx
import pyrogram

from cashews import cache

from glover import api_id, api_hash, ipv6, cache_uri
from models.sqlite import Sqlite

# Set Cache
cache.setup(cache_uri)
# Enable logging
logs = getLogger(__name__)
logging_handler = StreamHandler()
dt_fmt = "%Y-%m-%d %H:%M:%S"
formatter = Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
)
logging_handler.setFormatter(formatter)
root_logger = getLogger()
root_logger.setLevel(CRITICAL)
root_logger.addHandler(logging_handler)
pyro_logger = getLogger("pyrogram")
pyro_logger.setLevel(CRITICAL)
pyro_logger.addHandler(logging_handler)
basicConfig(level=INFO)
logs.setLevel(INFO)

# Init client
bot = pyrogram.Client(
    "bot", api_id=api_id, api_hash=api_hash, ipv6=ipv6, plugins=dict(root="modules")
)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.72 Safari/537.36"
}
request = httpx.AsyncClient(timeout=60.0, headers=headers)
sqlite = Sqlite()
