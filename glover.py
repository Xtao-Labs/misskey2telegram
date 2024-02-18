from configparser import RawConfigParser
from typing import Union


def strtobool(val, default=False):
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    if val is None:
        return default
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return 1
    elif val in ("n", "no", "f", "false", "off", "0"):
        return 0
    else:
        print("[Degrade] invalid truth value %r" % (val,))
        return default


# [pyrogram]
api_id: int = 0
api_hash: str = ""
# [Basic]
ipv6: Union[bool, str] = "False"
cache_uri: str = "mem://"
sentry_dsn: str = ""
# [misskey]
web_domain: str = ""
admin: int = 0

config = RawConfigParser()
config.read("config.ini")
api_id = config.getint("pyrogram", "api_id", fallback=api_id)
api_hash = config.get("pyrogram", "api_hash", fallback=api_hash)
ipv6 = config.get("basic", "ipv6", fallback=ipv6)
cache_uri = config.get("basic", "cache_uri", fallback=cache_uri)
sentry_dsn = config.get("basic", "sentry_dsn", fallback=sentry_dsn)
web_domain = config.get("misskey", "web_domain", fallback=web_domain)
admin = config.getint("misskey", "admin", fallback=admin)
try:
    ipv6 = bool(strtobool(ipv6))
except ValueError:
    ipv6 = False
