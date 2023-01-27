import re
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
misskey_domain: str = ""
web_domain: str = ""
admin: int = 0

config = RawConfigParser()
config.read("config.ini")
api_id = config.getint("pyrogram", "api_id", fallback=api_id)
api_hash = config.get("pyrogram", "api_hash", fallback=api_hash)
ipv6 = config.get("basic", "ipv6", fallback=ipv6)
misskey_url = config.get("misskey", "url", fallback=misskey_url)
if origin_url := re.search(r'wss?://(.*)/streaming', misskey_url):
    misskey_host = (
        origin_url[0]
        .replace('wss', 'https')
        .replace('ws', 'http')
        .replace('/streaming', '')
    )
else:
    misskey_host = misskey_url
misskey_domain = re.search(r'https?://(.*)', misskey_host)[1]
web_domain = config.get("misskey", "web_domain", fallback=web_domain)
admin = config.getint("misskey", "admin", fallback=admin)
try:
    ipv6 = strtobool(ipv6)
except ValueError:
    ipv6 = False
