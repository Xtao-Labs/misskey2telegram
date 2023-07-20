from httpx import URL, InvalidURL

from init import request


def get_host(url: str) -> str:
    try:
        url = URL(url)
    except InvalidURL:
        return ""
    return url.host


async def check_host(host: str) -> bool:
    if not host:
        return False
    try:
        req = await request.get(f"https://{host}/.well-known/nodeinfo")
        req.raise_for_status()
        node_url = req.json()["links"][0]["href"]
        req = await request.get(node_url)
        req.raise_for_status()
        data = req.json()
        if data["software"]["name"] != "misskey":
            raise ValueError
        if not data["software"]["version"].startswith("13."):
            raise ValueError
        return True
    except Exception:
        return False
