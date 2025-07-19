from httpx import URL, InvalidURL, AsyncClient

from init import headers


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
        async with AsyncClient(timeout=60, headers=headers) as request:
            req = await request.get(f"https://{host}/.well-known/nodeinfo")
            req.raise_for_status()
            node_url = req.json()["links"][0]["href"]
            req = await request.get(node_url)
        req.raise_for_status()
        data = req.json()
        if data["software"]["name"] != "misskey":
            raise ValueError
        year = int(data["software"]["version"].split(".")[0])
        if year < 2023:
            return False
        return True
    except Exception:
        return False
