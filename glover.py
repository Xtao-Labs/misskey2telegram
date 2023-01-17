from configparser import RawConfigParser
from typing import Union
from distutils.util import strtobool

# [pyrogram]
api_id: int = 0
api_hash: str = ""
# [Basic]
ipv6: Union[bool, str] = "False"
# [misskey]
misskey_url: str = ""
misskey_host: str = ""
misskey_token: str = ""
admin: int = 0
topic_group_id: int = 0
timeline_topic_id: int = 0
notice_topic_id: int = 0

config = RawConfigParser()
config.read("config.ini")
api_id = config.getint("pyrogram", "api_id", fallback=api_id)
api_hash = config.get("pyrogram", "api_hash", fallback=api_hash)
ipv6 = config.get("basic", "ipv6", fallback=ipv6)
misskey_url = config.get("misskey", "url", fallback=misskey_url)
misskey_host = config.get("misskey", "host", fallback=misskey_host)
misskey_token = config.get("misskey", "token", fallback=misskey_token)
admin = config.getint("misskey", "admin", fallback=admin)
topic_group_id = config.getint("misskey", "topic_group_id", fallback=topic_group_id)
timeline_topic_id = config.getint("misskey", "timeline_topic_id", fallback=timeline_topic_id)
notice_topic_id = config.getint("misskey", "notice_topic_id", fallback=notice_topic_id)
try:
    ipv6 = strtobool(ipv6)
except ValueError:
    ipv6 = False
