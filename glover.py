from configparser import RawConfigParser
from typing import Union
from distutils.util import strtobool

# [pyrogram]
api_id: int = 0
api_hash: str = ""
# [Basic]
ipv6: Union[bool, str] = "False"
# [misskey]
web_domain: str = ""
admin: int = 0

config = RawConfigParser()
config.read("config.ini")
api_id = config.getint("pyrogram", "api_id", fallback=api_id)
api_hash = config.get("pyrogram", "api_hash", fallback=api_hash)
ipv6 = config.get("basic", "ipv6", fallback=ipv6)
web_domain = config.get("misskey", "web_domain", fallback=web_domain)
admin = config.getint("misskey", "admin", fallback=admin)
try:
    ipv6 = bool(strtobool(ipv6))
except ValueError:
    ipv6 = False
